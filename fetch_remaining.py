"""Fetch remaining companies' data."""
import sys
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent))

from src.graph_db.neo4j_connector import Neo4jConnector
import requests
import time

ALPHAVANTAGE_API_KEY = "JLIXY16JZYO30PNX"

conn = Neo4jConnector()

# Remaining companies that need data
companies = {
    'META': {'name': 'Meta Platforms Inc.', 'sector': 'Technology'},
    'NVDA': {'name': 'NVIDIA Corporation', 'sector': 'Technology'},
    'JPM': {'name': 'JPMorgan Chase & Co.', 'sector': 'Financial Services'},
    'V': {'name': 'Visa Inc.', 'sector': 'Financial Services'},
    'WMT': {'name': 'Walmart Inc.', 'sector': 'Consumer Defensive'}
}

print('Fetching remaining 5 companies from Alpha Vantage...\n')
print('Waiting 60 seconds to respect rate limit...')
time.sleep(60)

success_count = 0

for symbol, data in companies.items():
    try:
        print(f'\nFetching {symbol} ({data["name"]})...')

        url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={ALPHAVANTAGE_API_KEY}'
        response = requests.get(url, timeout=10)
        quote_data = response.json()

        if 'Global Quote' in quote_data and quote_data['Global Quote']:
            quote = quote_data['Global Quote']

            price = float(quote.get('05. price', 0))
            change_pct = float(quote.get('10. change percent', '0').replace('%', ''))
            volume = int(float(quote.get('06. volume', 0)))
            market_cap = int(price * 1000000000)  # Estimate

            print(f'  [OK] Price: ${price:.2f} ({change_pct:+.2f}%)')
            print(f'  [OK] Volume: {volume:,}')

            # Update in Neo4j
            query = '''
            MATCH (c:Company {symbol: $symbol})
            SET c.price = $price,
                c.price_change_pct = $change_pct,
                c.market_cap = $market_cap,
                c.sector = $sector,
                c.volume = $volume
            RETURN c.symbol as symbol
            '''

            params = {
                'symbol': symbol,
                'price': price,
                'change_pct': change_pct,
                'market_cap': market_cap,
                'sector': data['sector'],
                'volume': volume
            }

            result = conn.execute_query(query, params)
            if result:
                print(f'  [OK] Updated in database')
                success_count += 1
        else:
            print(f'  [FAIL] No data available')

        time.sleep(13)  # Wait 13 seconds between requests (5 requests per minute)

    except Exception as e:
        print(f'  [ERROR] {str(e)}')

print(f'\n{"="*60}')
print(f'Successfully fetched data for {success_count}/5 remaining companies')
print(f'{"="*60}\n')

# Verify all data in database
print('Verifying ALL companies in database...\n')
verify_query = '''
MATCH (c:Company)
RETURN c.symbol as symbol, c.name as name, c.price as price,
       c.market_cap as market_cap, c.price_change_pct as change,
       c.volume as volume
ORDER BY c.market_cap DESC
'''

results = conn.execute_query(verify_query)
print(f'Found {len(results)} companies:\n')
print(f'{"Symbol":<8} {"Name":<30} {"Price":<12} {"Change":<10} {"Volume"}')
print(f'{"-"*8} {"-"*30} {"-"*12} {"-"*10} {"-"*15}')

complete = 0
for r in results:
    price = r.get('price', 0)
    price_display = f"${price:.2f}" if price else "N/A"
    change = r.get('change', 0)
    change_display = f"{change:+.2f}%" if change else "N/A"
    volume = r.get('volume', 0)
    volume_display = f"{volume:,}" if volume else "N/A"
    print(f'{r["symbol"]:<8} {r["name"]:<30} {price_display:<12} {change_display:<10} {volume_display}')
    if price:
        complete += 1

conn.close()

print(f'\n{"="*60}')
print(f'SUMMARY: {complete}/{len(results)} companies have real-time data')
print(f'{"="*60}')
print('\nDone! Refresh your browser to see ALL updated data.')

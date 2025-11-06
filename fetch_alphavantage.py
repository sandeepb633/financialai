"""Fetch real-time data using Alpha Vantage (free tier)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.graph_db.neo4j_connector import Neo4jConnector
import requests
import time

# Free Alpha Vantage API key (demo key - get your own from https://www.alphavantage.co/support/#api-key)
API_KEY = "JLIXY16JZYO30PNX"  # Replace with your key for unlimited use

conn = Neo4jConnector()

companies = {
    'AAPL': {'name': 'Apple Inc.', 'sector': 'Technology'},
    'MSFT': {'name': 'Microsoft Corporation', 'sector': 'Technology'},
    'GOOGL': {'name': 'Alphabet Inc.', 'sector': 'Technology'},
    'AMZN': {'name': 'Amazon.com Inc.', 'sector': 'Consumer Cyclical'},
    'TSLA': {'name': 'Tesla Inc.', 'sector': 'Automotive'},
    'META': {'name': 'Meta Platforms Inc.', 'sector': 'Technology'},
    'NVDA': {'name': 'NVIDIA Corporation', 'sector': 'Technology'},
    'JPM': {'name': 'JPMorgan Chase & Co.', 'sector': 'Financial Services'},
    'V': {'name': 'Visa Inc.', 'sector': 'Financial Services'},
    'WMT': {'name': 'Walmart Inc.', 'sector': 'Consumer Defensive'}
}

print('Fetching real-time data from Alpha Vantage (free API)...\n')
print('NOTE: Free tier is limited to 5 requests per minute, 500 per day')
print('Get your free API key at: https://www.alphavantage.co/support/#api-key\n')

count = 0
for symbol, data in companies.items():
    try:
        print(f'Fetching {symbol} ({data["name"]})...')

        # Get quote data
        url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={API_KEY}'
        response = requests.get(url)
        quote_data = response.json()

        if 'Global Quote' in quote_data and quote_data['Global Quote']:
            quote = quote_data['Global Quote']

            price = float(quote.get('05. price', 0))
            change_pct = float(quote.get('10. change percent', '0').replace('%', ''))
            volume = int(float(quote.get('06. volume', 0)))

            # Estimate market cap (rough calculation: price * 1B shares)
            market_cap = int(price * 1000000000)  # Rough estimate

            print(f'  Price: ${price:.2f}')
            print(f'  Change: {change_pct:+.2f}%')
            print(f'  Volume: {volume:,}')

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
                print(f'  Updated in database!\n')
        else:
            print(f'  No data available (might need API key or hit rate limit)\n')

        count += 1
        if count >= 5:
            print('Waiting 60 seconds (free tier rate limit: 5 requests/minute)...')
            time.sleep(60)
            count = 0
        else:
            time.sleep(12)  # Wait 12 seconds between requests

    except Exception as e:
        print(f'  ERROR: {str(e)}\n')

print('\nVerifying data in database...')
verify_query = '''
MATCH (c:Company)
RETURN c.symbol as symbol, c.name as name, c.price as price,
       c.market_cap as market_cap, c.price_change_pct as change,
       c.volume as volume
ORDER BY c.symbol
'''

results = conn.execute_query(verify_query)
print(f'\nFound {len(results)} companies:')
for r in results:
    price = r.get('price', 0)
    price_display = f"${price:.2f}" if price else "N/A"
    change = r.get('change', 0)
    change_display = f"{change:+.2f}%" if change else "N/A"
    volume = r.get('volume', 0)
    volume_display = f"{volume:,}" if volume else "N/A"
    print(f"{r['symbol']:6s} {r['name']:30s} {price_display:10s} {change_display:8s} Vol: {volume_display}")

conn.close()
print('\nDone! Refresh your browser to see the updated data.')
print('\nTo get unlimited API calls, sign up for a free API key at:')
print('https://www.alphavantage.co/support/#api-key')

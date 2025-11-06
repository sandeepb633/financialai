"""Fetch real-time data using multiple free APIs with fallback."""
import sys
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent))

from src.graph_db.neo4j_connector import Neo4jConnector
from src.data_ingestion.finnhub_collector import FinnhubCollector
import requests
import time
import yfinance as yf

# API Configuration
ALPHAVANTAGE_API_KEY = "JLIXY16JZYO30PNX"  # Your Alpha Vantage API key
USE_ALPHAVANTAGE = True
USE_YFINANCE = True
USE_FINNHUB = True

conn = Neo4jConnector()
finnhub = FinnhubCollector() if USE_FINNHUB else None

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

print('Fetching real-time data from multiple sources...\n')
print('Data sources: ', end='')
sources = []
if USE_ALPHAVANTAGE:
    sources.append('Alpha Vantage')
if USE_YFINANCE:
    sources.append('Yahoo Finance')
if USE_FINNHUB:
    sources.append('Finnhub')
print(', '.join(sources))
print()

def fetch_from_alphavantage(symbol):
    """Fetch data from Alpha Vantage."""
    try:
        url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={ALPHAVANTAGE_API_KEY}'
        response = requests.get(url, timeout=10)
        data = response.json()

        if 'Global Quote' in data and data['Global Quote']:
            quote = data['Global Quote']
            return {
                'source': 'AlphaVantage',
                'price': float(quote.get('05. price', 0)),
                'change_pct': float(quote.get('10. change percent', '0').replace('%', '')),
                'volume': int(float(quote.get('06. volume', 0))),
                'market_cap': int(float(quote.get('05. price', 0)) * 1000000000)  # Estimate
            }
    except Exception as e:
        pass
    return None

def fetch_from_yfinance(symbol):
    """Fetch data from Yahoo Finance (yfinance)."""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info

        price = info.get('currentPrice') or info.get('regularMarketPrice') or info.get('previousClose', 0)
        if price and price > 0:
            return {
                'source': 'YahooFinance',
                'price': float(price),
                'change_pct': float(info.get('regularMarketChangePercent', 0)),
                'volume': int(info.get('volume', 0) or 0),
                'market_cap': int(info.get('marketCap', 0) or 0)
            }
    except Exception as e:
        pass
    return None

def fetch_from_finnhub(symbol):
    """Fetch data from Finnhub."""
    try:
        profile = finnhub.get_company_profile(symbol)
        if profile and profile.get('price', 0) > 0:
            return {
                'source': 'Finnhub',
                'price': float(profile.get('price', 0)),
                'change_pct': 0,  # Finnhub doesn't provide change percent in profile
                'volume': 0,
                'market_cap': int(profile.get('marketCapitalization', 0) * 1000000) if profile.get('marketCapitalization') else 0
            }
    except Exception as e:
        pass
    return None

# Fetch data for all companies
success_count = 0
alpha_count = 0

for symbol, data in companies.items():
    print(f'Fetching {symbol} ({data["name"]})...')

    fetched_data = None

    # Try Alpha Vantage first (if enabled and we haven't hit the limit)
    if USE_ALPHAVANTAGE and alpha_count < 5:
        fetched_data = fetch_from_alphavantage(symbol)
        if fetched_data:
            alpha_count += 1
            print(f'  [OK] {fetched_data["source"]}: ${fetched_data["price"]:.2f} ({fetched_data["change_pct"]:+.2f}%)')
        else:
            time.sleep(1)  # Brief pause before trying next source

    # Fallback to Yahoo Finance
    if not fetched_data and USE_YFINANCE:
        fetched_data = fetch_from_yfinance(symbol)
        if fetched_data:
            print(f'  [OK] {fetched_data["source"]}: ${fetched_data["price"]:.2f} ({fetched_data["change_pct"]:+.2f}%)')

    # Fallback to Finnhub
    if not fetched_data and USE_FINNHUB:
        time.sleep(0.5)
        fetched_data = fetch_from_finnhub(symbol)
        if fetched_data:
            print(f'  [OK] {fetched_data["source"]}: ${fetched_data["price"]:.2f}')

    # Update database if we got data
    if fetched_data:
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
            'price': fetched_data['price'],
            'change_pct': fetched_data['change_pct'],
            'market_cap': fetched_data['market_cap'],
            'sector': data['sector'],
            'volume': fetched_data.get('volume', 0)
        }

        result = conn.execute_query(query, params)
        if result:
            print(f'  [OK] Updated in database')
            success_count += 1
    else:
        print(f'  [FAIL] No data available from any source')

    print()

    # Rate limiting: wait between requests
    if alpha_count >= 5:
        # Hit Alpha Vantage limit, disable it
        USE_ALPHAVANTAGE = False
        print('  (Alpha Vantage rate limit reached, using other sources...)\n')

    time.sleep(3)  # 3 second delay between each company

print(f'\n{"="*60}')
print(f'Successfully fetched data for {success_count}/{len(companies)} companies')
print(f'{"="*60}\n')

# Verify data in database
print('Verifying data in database...\n')
verify_query = '''
MATCH (c:Company)
RETURN c.symbol as symbol, c.name as name, c.price as price,
       c.market_cap as market_cap, c.price_change_pct as change,
       c.volume as volume
ORDER BY c.symbol
'''

results = conn.execute_query(verify_query)
print(f'Found {len(results)} companies in database:\n')
print(f'{"Symbol":<8} {"Name":<30} {"Price":<12} {"Change":<10} {"Volume"}')
print(f'{"-"*8} {"-"*30} {"-"*12} {"-"*10} {"-"*15}')

for r in results:
    price = r.get('price', 0)
    price_display = f"${price:.2f}" if price else "N/A"
    change = r.get('change', 0)
    change_display = f"{change:+.2f}%" if change else "N/A"
    volume = r.get('volume', 0)
    volume_display = f"{volume:,}" if volume else "N/A"
    print(f'{r["symbol"]:<8} {r["name"]:<30} {price_display:<12} {change_display:<10} {volume_display}')

conn.close()

print('\n' + '='*60)
print('Done! Refresh your browser to see the updated data.')
print('='*60)

if success_count < len(companies):
    print('\nTo improve data coverage:')
    print('1. Get a free Alpha Vantage API key: https://www.alphavantage.co/support/#api-key')
    print('2. Update ALPHAVANTAGE_API_KEY in this script')
    print('3. Run this script again')

"""Fetch real-time financial data from multiple sources."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.graph_db.neo4j_connector import Neo4jConnector
import yfinance as yf
import time
import requests

conn = Neo4jConnector()

companies = {
    'AAPL': 'Apple Inc.',
    'MSFT': 'Microsoft Corporation',
    'GOOGL': 'Alphabet Inc.',
    'AMZN': 'Amazon.com Inc.',
    'TSLA': 'Tesla Inc.',
    'META': 'Meta Platforms Inc.',
    'NVDA': 'NVIDIA Corporation',
    'JPM': 'JPMorgan Chase & Co.',
    'V': 'Visa Inc.',
    'WMT': 'Walmart Inc.'
}

print('Fetching real-time financial data from Yahoo Finance...\n')

for symbol, name in companies.items():
    try:
        print(f'Fetching {symbol}...')

        # Use yfinance to get current data
        ticker = yf.Ticker(symbol)

        # Get current info
        info = ticker.info

        # Get current price and other data
        price = info.get('currentPrice') or info.get('regularMarketPrice') or info.get('previousClose', 0)
        market_cap = info.get('marketCap', 0)
        change_pct = info.get('regularMarketChangePercent', 0)
        sector = info.get('sector', 'Technology')
        industry = info.get('industry', 'Technology')

        print(f'  Price: ${price:.2f}')
        print(f'  Market Cap: ${market_cap/1e9:.2f}B')
        print(f'  Change: {change_pct:.2f}%')
        print(f'  Sector: {sector}')

        # Update in Neo4j
        query = '''
        MATCH (c:Company {symbol: $symbol})
        SET c.price = $price,
            c.market_cap = $market_cap,
            c.price_change_pct = $change_pct,
            c.sector = $sector,
            c.industry = $industry,
            c.name = $name
        RETURN c.symbol as symbol
        '''

        params = {
            'symbol': symbol,
            'name': name,
            'price': float(price) if price else 0,
            'market_cap': int(market_cap) if market_cap else 0,
            'change_pct': float(change_pct) if change_pct else 0,
            'sector': sector or 'Technology',
            'industry': industry or 'Technology'
        }

        result = conn.execute_query(query, params)
        if result:
            print(f'  Updated in database!\n')
        else:
            print(f'  WARNING: Database update failed\n')

        # Wait to avoid rate limiting
        time.sleep(2)

    except Exception as e:
        print(f'  ERROR: {str(e)}\n')
        time.sleep(2)

print('\nVerifying data in database...')
verify_query = '''
MATCH (c:Company)
RETURN c.symbol as symbol, c.name as name, c.price as price,
       c.market_cap as market_cap, c.price_change_pct as change
ORDER BY c.market_cap DESC
'''

results = conn.execute_query(verify_query)
print(f'\nFound {len(results)} companies:')
for r in results:
    mc = r.get('market_cap', 0)
    mc_display = f"${mc/1e9:.2f}B" if mc else "N/A"
    price = r.get('price', 0)
    price_display = f"${price:.2f}" if price else "N/A"
    change = r.get('change', 0)
    change_display = f"{change:+.2f}%" if change else "N/A"
    print(f"{r['symbol']:6s} {r['name']:30s} {price_display:10s} {mc_display:12s} {change_display}")

conn.close()
print('\nDone! Refresh your browser to see the updated data.')

"""Update company prices from Finnhub."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.graph_db.neo4j_connector import Neo4jConnector
from src.data_ingestion.finnhub_collector import FinnhubCollector
import time

conn = Neo4jConnector()
finnhub = FinnhubCollector()

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

print('Fetching financial data for companies...')

for symbol, name in companies.items():
    try:
        # Get company profile from Finnhub
        profile = finnhub.get_company_profile(symbol)

        if profile:
            # Update company with financial data
            query = '''
            MATCH (c:Company {symbol: $symbol})
            SET c.price = $price,
                c.market_cap = $market_cap,
                c.sector = COALESCE($sector, c.sector),
                c.industry = $industry,
                c.country = $country,
                c.currency = $currency
            RETURN c.symbol as symbol, c.name as name, c.price as price
            '''

            params = {
                'symbol': symbol,
                'price': profile.get('price', 0),
                'market_cap': profile.get('marketCapitalization', 0) * 1000000 if profile.get('marketCapitalization') else 0,
                'sector': profile.get('finnhubIndustry', 'Technology'),
                'industry': profile.get('finnhubIndustry', 'Technology'),
                'country': profile.get('country', 'US'),
                'currency': profile.get('currency', 'USD')
            }

            result = conn.execute_query(query, params)
            if result:
                print(f'{symbol}: Price=${profile.get("price", 0):.2f}, MarketCap=${profile.get("marketCapitalization", 0):.2f}B')
        else:
            print(f'{symbol}: No data from Finnhub')

        time.sleep(0.5)  # Rate limiting

    except Exception as e:
        print(f'{symbol}: Error - {str(e)}')

print('Financial data updated!')
conn.close()

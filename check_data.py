from src.graph_db.neo4j_connector import Neo4jConnector
import sys
sys.path.insert(0, '.')

conn = Neo4jConnector()
result = conn.execute_query('MATCH (c:Company) RETURN c.symbol as symbol, c.name as name, c.price as price, c.sector as sector ORDER BY c.symbol')
print('Companies in database:')
for r in result:
    print(f"{r['symbol']}: {r.get('name', 'N/A')} - Price: ${r.get('price', 'N/A')} - Sector: {r.get('sector', 'N/A')}")
conn.close()

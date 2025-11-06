"""Test and explore the Knowledge Graph."""
import sys
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent))

from src.graph_db.neo4j_connector import Neo4jConnector

conn = Neo4jConnector()

print("="*70)
print("KNOWLEDGE GRAPH TESTING SUITE")
print("="*70)
print()

# Test 1: Count all node types
print("[TEST 1] Counting all node types in the graph...")
print("-"*70)
query = """
MATCH (n)
RETURN labels(n)[0] as NodeType, count(n) as Count
ORDER BY Count DESC
"""
results = conn.execute_query(query)
for r in results:
    print(f"  {r['NodeType']:<20s} {r['Count']:>6d} nodes")
print()

# Test 2: Count all relationship types
print("[TEST 2] Counting all relationship types...")
print("-"*70)
query = """
MATCH ()-[r]->()
RETURN type(r) as RelationshipType, count(r) as Count
ORDER BY Count DESC
"""
results = conn.execute_query(query)
if results:
    for r in results:
        print(f"  {r['RelationshipType']:<30s} {r['Count']:>6d} relationships")
else:
    print("  No relationships found!")
print()

# Test 3: Company details with financial data
print("[TEST 3] Company nodes with financial data...")
print("-"*70)
query = """
MATCH (c:Company)
RETURN c.symbol as Symbol, c.name as Name, c.sector as Sector,
       c.price as Price, c.price_change_pct as Change
ORDER BY c.market_cap DESC
LIMIT 10
"""
results = conn.execute_query(query)
print(f"{'Symbol':<8} {'Name':<30} {'Sector':<20} {'Price':<12} {'Change':<10}")
print("-"*90)
for r in results:
    symbol = r['Symbol'] or 'N/A'
    name = r['Name'] or 'N/A'
    sector = r['Sector'] or 'N/A'
    price = f"${r['Price']:.2f}" if r.get('Price') else 'N/A'
    change = f"{r['Change']:+.2f}%" if r.get('Change') is not None else 'N/A'
    print(f"{symbol:<8} {name:<30} {sector:<20} {price:<12} {change:<10}")
print()

# Test 4: News articles and their connections
print("[TEST 4] News articles connected to companies...")
print("-"*70)
query = """
MATCH (n:News)-[r:MENTIONS]->(c:Company)
RETURN n.title as NewsTitle, c.symbol as Company, n.sentiment as Sentiment
ORDER BY n.published_date DESC
LIMIT 5
"""
results = conn.execute_query(query)
if results:
    for i, r in enumerate(results, 1):
        print(f"\n  News #{i}:")
        print(f"    Title: {r['NewsTitle'][:70]}...")
        print(f"    Company: {r['Company']}")
        print(f"    Sentiment: {r['Sentiment']}")
else:
    print("  No news-company relationships found!")
print()

# Test 5: Multi-hop relationship test (Companies connected through events)
print("[TEST 5] Multi-hop relationships: Companies connected through events...")
print("-"*70)
query = """
MATCH (c1:Company)-[:INVOLVED_IN]->(e:Event)<-[:INVOLVED_IN]-(c2:Company)
WHERE c1.symbol < c2.symbol
RETURN c1.symbol as Company1, e.event_type as EventType, c2.symbol as Company2
LIMIT 5
"""
results = conn.execute_query(query)
if results:
    for r in results:
        print(f"  {r['Company1']} --[{r['EventType']}]--> {r['Company2']}")
else:
    print("  No event-based connections found between companies")
print()

# Test 6: Sector analysis
print("[TEST 6] Companies grouped by sector...")
print("-"*70)
query = """
MATCH (c:Company)
WHERE c.sector IS NOT NULL
RETURN c.sector as Sector, count(c) as CompanyCount,
       avg(c.price_change_pct) as AvgChange
ORDER BY CompanyCount DESC
"""
results = conn.execute_query(query)
if results:
    print(f"{'Sector':<30} {'Companies':<12} {'Avg Change':<15}")
    print("-"*70)
    for r in results:
        sector = r['Sector'] or 'Unknown'
        count = r['CompanyCount']
        avg_change = f"{r['AvgChange']:+.2f}%" if r.get('AvgChange') is not None else 'N/A'
        print(f"{sector:<30} {count:<12} {avg_change:<15}")
else:
    print("  No sector data found")
print()

# Test 7: Graph connectivity test
print("[TEST 7] Testing graph connectivity...")
print("-"*70)
query = """
MATCH (c:Company {symbol: 'AAPL'})
OPTIONAL MATCH (c)-[r1:MENTIONS]-(n:News)
OPTIONAL MATCH (c)-[r2:INVOLVED_IN]-(e:Event)
OPTIONAL MATCH (c)-[r3:IN_SECTOR]-(s:Sector)
RETURN
    count(DISTINCT n) as NewsCount,
    count(DISTINCT e) as EventCount,
    count(DISTINCT s) as SectorCount
"""
results = conn.execute_query(query)
if results:
    r = results[0]
    print(f"  Apple (AAPL) connections:")
    print(f"    Connected to {r['NewsCount']} news articles")
    print(f"    Connected to {r['EventCount']} events")
    print(f"    Connected to {r['SectorCount']} sectors")

    total = r['NewsCount'] + r['EventCount'] + r['SectorCount']
    if total > 0:
        print(f"\n  [PASS] Apple is connected to {total} entities")
    else:
        print(f"\n  [WARN] Apple has no connections in the graph")
print()

# Test 8: Recent news test
print("[TEST 8] Most recent news in the graph...")
print("-"*70)
query = """
MATCH (n:News)
RETURN n.title as Title, n.published_date as Date, n.source as Source
ORDER BY n.published_date DESC
LIMIT 3
"""
results = conn.execute_query(query)
if results:
    for i, r in enumerate(results, 1):
        print(f"\n  News #{i}:")
        print(f"    {r['Title'][:65]}...")
        print(f"    Date: {r['Date']}")
        print(f"    Source: {r['Source']}")
else:
    print("  No news articles found")
print()

# Test 9: Path finding test (shortest path between two companies)
print("[TEST 9] Finding paths between companies...")
print("-"*70)
query = """
MATCH path = shortestPath(
    (c1:Company {symbol: 'AAPL'})-[*..3]-(c2:Company {symbol: 'MSFT'})
)
RETURN length(path) as PathLength,
       [n in nodes(path) | labels(n)[0]] as NodeTypes
LIMIT 1
"""
results = conn.execute_query(query)
if results and results[0].get('PathLength') is not None:
    r = results[0]
    print(f"  Found path from AAPL to MSFT:")
    print(f"    Path length: {r['PathLength']} hops")
    print(f"    Node types: {' -> '.join(r['NodeTypes'])}")
    print(f"  [PASS] Graph is connected")
else:
    print(f"  [WARN] No path found between AAPL and MSFT")
    print(f"  This might mean companies are not connected through events or news")
print()

# Test 10: Graph statistics summary
print("[TEST 10] Overall graph statistics...")
print("-"*70)
query = """
MATCH (n)
WITH count(n) as NodeCount
MATCH ()-[r]->()
RETURN NodeCount, count(r) as RelationshipCount
"""
results = conn.execute_query(query)
if results:
    r = results[0]
    nodes = r['NodeCount']
    rels = r['RelationshipCount']
    density = (rels / (nodes * (nodes - 1))) * 100 if nodes > 1 else 0

    print(f"  Total Nodes: {nodes}")
    print(f"  Total Relationships: {rels}")
    print(f"  Graph Density: {density:.2f}%")
    print(f"  Avg Connections per Node: {(rels*2/nodes):.2f}" if nodes > 0 else "  N/A")

    if rels > 0:
        print(f"\n  [PASS] Knowledge graph is populated and connected")
    else:
        print(f"\n  [FAIL] Knowledge graph has nodes but no relationships!")
print()

conn.close()

print("="*70)
print("TESTING COMPLETE")
print("="*70)
print()
print("Next steps to explore your knowledge graph:")
print("1. Open Neo4j Browser and run: MATCH (n) RETURN n LIMIT 50")
print("2. Use the Graph Explorer in your dashboard: http://192.168.2.29:8501")
print("3. Ask the AI Assistant questions about companies and news")

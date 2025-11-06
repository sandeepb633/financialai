from src.entity_extraction.entity_extractor import EntityExtractor
from src.graph_db.neo4j_connector import Neo4jConnector
from src.graphrag_engine.query_engine import GraphRAGQueryEngine
import sys
sys.path.insert(0, '.')

# Test entity extraction
extractor = EntityExtractor()

test_queries = [
    "what is the current stock price of apple?",
    "What's the latest news in technology sector?",
    "What's the overall market sentiment?",
    "Tell me about Microsoft",
    "How is TSLA doing?"
]

print("=" * 60)
print("TESTING ENTITY EXTRACTION")
print("=" * 60)

for query in test_queries:
    print(f"\nQuery: {query}")
    entities = extractor.extract_financial_entities(query)
    print(f"  Tickers: {entities.get('tickers', [])}")
    print(f"  Companies: {entities.get('companies', [])}")

# Test query engine
print("\n" + "=" * 60)
print("TESTING QUERY ENGINE")
print("=" * 60)

connector = Neo4jConnector()
engine = GraphRAGQueryEngine(connector)

for query in test_queries[:3]:
    print(f"\nQuery: {query}")
    result = engine.execute_query(query)
    print(f"  Intent: {result['intent']}")
    print(f"  Entities: {result['entities']}")
    print(f"  Results found: {result['num_results']}")
    if result['num_results'] > 0:
        print(f"  First result: {result['results'][0]}")

connector.close()
print("\n" + "=" * 60)
print("TEST COMPLETE!")
print("=" * 60)

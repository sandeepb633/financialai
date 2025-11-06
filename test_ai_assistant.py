"""Test script to check if AI Assistant components are working."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from config.config import settings

# Windows-compatible symbols
OK = "[OK]"
FAIL = "[FAIL]"
WARN = "[WARN]"

print("=" * 60)
print("AI Assistant Component Check")
print("=" * 60)

# 1. Check Neo4j Connection
print("\n1. Checking Neo4j Connection...")
try:
    from src.graph_db.neo4j_connector import Neo4jConnector
    connector = Neo4jConnector()
    stats = connector.get_database_stats()
    print(f"   {OK} Neo4j Connected")
    print(f"   - Companies: {stats.get('companies', 0)}")
    print(f"   - News: {stats.get('news', 0)}")
    print(f"   - Events: {stats.get('events', 0)}")
except Exception as e:
    print(f"   {FAIL} Neo4j Connection Failed: {str(e)}")
    connector = None

# 2. Check LLM Configuration
print("\n2. Checking LLM Configuration...")
print(f"   Provider: {settings.LLM_PROVIDER}")

if settings.LLM_PROVIDER == 'openai':
    if settings.OPENAI_API_KEY:
        print(f"   {OK} OpenAI API Key: {'*' * 20}{settings.OPENAI_API_KEY[-4:]}")
        print(f"   Model: {settings.OPENAI_MODEL}")
    else:
        print(f"   {FAIL} OpenAI API Key not set")
elif settings.LLM_PROVIDER == 'anthropic':
    if settings.ANTHROPIC_API_KEY:
        print(f"   {OK} Anthropic API Key: {'*' * 20}{settings.ANTHROPIC_API_KEY[-4:]}")
        print(f"   Model: {settings.ANTHROPIC_MODEL}")
    else:
        print(f"   {FAIL} Anthropic API Key not set")

# 3. Test LLM Client Initialization
print("\n3. Testing LLM Client Initialization...")
try:
    from src.llm_integration.llm_client import LLMClient
    llm_client = LLMClient()
    print(f"   {OK} LLM Client initialized successfully")
    print(f"   Provider: {llm_client.provider}")
    print(f"   Model: {llm_client.model}")
except Exception as e:
    print(f"   {FAIL} LLM Client initialization failed: {str(e)}")
    llm_client = None

# 4. Test Query Engine
print("\n4. Testing Query Engine...")
if connector:
    try:
        from src.graphrag_engine.query_engine import GraphRAGQueryEngine
        query_engine = GraphRAGQueryEngine(connector)
        print(f"   {OK} Query Engine initialized")

        # Test a simple query
        test_query = "Show me companies"
        print(f"\n   Testing query: '{test_query}'")
        result = query_engine.execute_query(test_query)
        print(f"   - Intent: {result.get('intent')}")
        print(f"   - Results: {result.get('num_results')} items")

        if result.get('num_results', 0) > 0:
            print(f"   {OK} Query executed successfully")
            print(f"\n   Sample result:")
            sample = result['results'][0] if result['results'] else {}
            for key, value in list(sample.items())[:3]:
                print(f"   - {key}: {value}")
        else:
            print(f"   {WARN} Query returned no results (database may be empty)")

    except Exception as e:
        print(f"   {FAIL} Query Engine failed: {str(e)}")
        query_engine = None
else:
    print(f"   {WARN} Skipped (Neo4j not connected)")
    query_engine = None

# 5. Test GraphRAG Generator
print("\n5. Testing GraphRAG Generator...")
if llm_client and query_engine:
    try:
        from src.llm_integration.llm_client import GraphRAGGenerator
        generator = GraphRAGGenerator(llm_client)
        print(f"   ✓ GraphRAG Generator initialized")

        # Test with mock data
        print(f"\n   Testing response generation with mock data...")
        mock_result = {
            'intent': 'company_info',
            'results': [{
                'symbol': 'AAPL',
                'name': 'Apple Inc.',
                'sector': 'Technology',
                'price': 175.00,
                'price_change_pct': 2.5
            }],
            'num_results': 1,
            'cypher_query': 'MATCH (c:Company) RETURN c'
        }

        response = generator.generate_grounded_response(
            "Tell me about Apple",
            mock_result
        )

        print(f"   {OK} Response generated")
        print(f"\n   Response preview (first 200 chars):")
        print(f"   {response['response'][:200]}...")

    except Exception as e:
        print(f"   {FAIL} GraphRAG Generator failed: {str(e)}")
else:
    print(f"   {WARN} Skipped (dependencies not available)")

# 6. Summary
print("\n" + "=" * 60)
print("Summary")
print("=" * 60)

components = {
    'Neo4j': connector is not None,
    'LLM Client': llm_client is not None,
    'Query Engine': query_engine is not None if connector else None,
    'GraphRAG Generator': 'generator' in locals() if llm_client else None
}

all_working = all(v for v in components.values() if v is not None)

for component, status in components.items():
    if status is None:
        symbol = WARN
        status_text = "SKIPPED"
    elif status:
        symbol = OK
        status_text = "WORKING"
    else:
        symbol = FAIL
        status_text = "FAILED"

    print(f"{symbol} {component}: {status_text}")

print("\n" + "=" * 60)

if all_working:
    print(f"{OK} AI Assistant is fully operational!")
    print("\nYou can now use the AI Assistant in the Streamlit app.")
else:
    print(f"{WARN} Some components are not working.")
    print("\nPlease check:")
    if not connector:
        print("  - Neo4j is running (http://localhost:7474)")
        print("  - NEO4J_PASSWORD is set in .env file")
    if not llm_client:
        print("  - LLM API key is set in .env file")
        print(f"  - For {settings.LLM_PROVIDER}: {settings.LLM_PROVIDER.upper()}_API_KEY")

print("=" * 60)

# Cleanup
if connector:
    connector.close()

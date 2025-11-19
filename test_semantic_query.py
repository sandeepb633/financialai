"""Test semantic query understanding with different wordings."""

import logging
import sys
from pathlib import Path
import os

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from src.graph_db.neo4j_connector import Neo4jConnector
from src.graphrag_engine.query_engine import GraphRAGQueryEngine
from src.llm_integration.llm_client import LLMClient, GraphRAGGenerator
from config.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_query_understanding():
    """Test query understanding with various wordings."""

    # Test queries with different wordings for the same intent
    test_cases = [
        # Sentiment Analysis
        {
            "category": "Sentiment Analysis",
            "queries": [
                "What is the market sentiment?",
                "How are investors feeling?",
                "What's the mood in the market?",
                "What's the investor perception?",
                "Show me the market outlook",
                "What's the general tone of the market?",
                "What are people's attitudes towards stocks?"
            ],
            "expected_intent": "sentiment_analysis"
        },

        # Company News
        {
            "category": "Company News",
            "queries": [
                "Latest news about Apple",
                "Show me recent articles on Tesla",
                "What are the headlines for Microsoft?",
                "Any updates on Amazon?",
                "Get me reports about Google",
                "What's in the press about Meta?"
            ],
            "expected_intent": "company_news"
        },

        # Company Info
        {
            "category": "Company Information",
            "queries": [
                "Tell me about Apple",
                "What's the price of Tesla?",
                "Show me Microsoft's value",
                "What is Amazon trading at?",
                "How much is Google worth?",
                "Give me fundamentals for Meta"
            ],
            "expected_intent": "company_info"
        },

        # Market Overview
        {
            "category": "Market Overview",
            "queries": [
                "Market overview",
                "Give me a market summary",
                "Show me a market snapshot",
                "What's the market status?",
                "Market breakdown",
                "Overall market analysis",
                "How are stocks performing?"
            ],
            "expected_intent": "market_overview"
        },

        # Sector/Industry
        {
            "category": "Sector Companies",
            "queries": [
                "Show me tech companies",
                "Companies in the technology sector",
                "What's in the healthcare industry?",
                "List financial sector stocks",
                "Tech vertical companies",
                "Energy category stocks"
            ],
            "expected_intent": "sector_companies"
        },

        # Trending News
        {
            "category": "Trending News",
            "queries": [
                "What's trending?",
                "Show me popular stocks",
                "What's hot in the market?",
                "Stocks in the spotlight",
                "What's getting attention?",
                "Focus on buzz stocks"
            ],
            "expected_intent": "trending_news"
        }
    ]

    print("=" * 80)
    print("SEMANTIC QUERY UNDERSTANDING TEST")
    print("=" * 80)

    try:
        # Initialize connections
        print("\nInitializing connections...")
        connector = Neo4jConnector()

        # Try to initialize LLM client
        try:
            llm_client = LLMClient()
            print(f"✓ LLM Client initialized ({settings.LLM_PROVIDER})")
            use_llm = True
        except Exception as e:
            print(f"⚠ LLM Client unavailable: {e}")
            print("  Testing with rule-based classification only")
            llm_client = None
            use_llm = False

        # Initialize query engine with or without LLM
        query_engine = GraphRAGQueryEngine(connector, llm_client=llm_client)
        print(f"✓ Query Engine initialized (LLM-enhanced: {use_llm})\n")

        # Test each category
        total_tests = 0
        correct_classifications = 0

        for test_case in test_cases:
            category = test_case["category"]
            expected = test_case["expected_intent"]
            queries = test_case["queries"]

            print(f"\n{'=' * 80}")
            print(f"Testing: {category} (Expected: {expected})")
            print(f"{'=' * 80}")

            category_correct = 0

            for query in queries:
                total_tests += 1

                # Understand the query
                understanding = query_engine.understand_query(query)
                detected_intent = understanding['intent']
                entities = understanding['entities']

                is_correct = detected_intent == expected
                if is_correct:
                    correct_classifications += 1
                    category_correct += 1

                # Display result
                status = "✓" if is_correct else "✗"
                print(f"\n{status} Query: \"{query}\"")
                print(f"  Intent: {detected_intent} {'(CORRECT)' if is_correct else '(EXPECTED: ' + expected + ')'}")

                if entities.get('tickers'):
                    print(f"  Tickers: {entities['tickers']}")
                if entities.get('companies'):
                    print(f"  Companies: {entities['companies']}")
                if entities.get('concepts'):
                    print(f"  Concepts: {entities['concepts']}")

            accuracy = (category_correct / len(queries)) * 100
            print(f"\nCategory Accuracy: {category_correct}/{len(queries)} ({accuracy:.1f}%)")

        # Final summary
        print(f"\n{'=' * 80}")
        print("FINAL RESULTS")
        print(f"{'=' * 80}")
        overall_accuracy = (correct_classifications / total_tests) * 100
        print(f"\nTotal Tests: {total_tests}")
        print(f"Correct Classifications: {correct_classifications}")
        print(f"Overall Accuracy: {overall_accuracy:.1f}%")
        print(f"Classification Method: {'LLM-Enhanced' if use_llm else 'Rule-Based Only'}")

        if overall_accuracy >= 80:
            print("\n✓ EXCELLENT: Query understanding is working well!")
        elif overall_accuracy >= 60:
            print("\n⚠ GOOD: Most queries are understood correctly")
        else:
            print("\n✗ NEEDS IMPROVEMENT: Consider tuning the classification logic")

        connector.close()

    except Exception as e:
        logger.error(f"Test failed: {str(e)}", exc_info=True)
        print(f"\n✗ Error: {str(e)}")
        return False

    return True


def test_live_query():
    """Test a live query with full GraphRAG pipeline."""
    print("\n" + "=" * 80)
    print("LIVE QUERY TEST")
    print("=" * 80)

    try:
        connector = Neo4jConnector()

        try:
            llm_client = LLMClient()
        except:
            llm_client = None

        query_engine = GraphRAGQueryEngine(connector, llm_client=llm_client)
        generator = GraphRAGGenerator(llm_client) if llm_client else None

        # Test with different wordings
        test_queries = [
            "What is the market sentiment?",
            "How are investors feeling about tech stocks?",
            "Show me the mood in the market"
        ]

        for query in test_queries:
            print(f"\n{'=' * 80}")
            print(f"Query: {query}")
            print(f"{'=' * 80}")

            # Execute query
            result = query_engine.execute_query(query)

            print(f"\nDetected Intent: {result['intent']}")
            print(f"Entities: {result.get('entities', {})}")
            print(f"Results Found: {result['num_results']}")

            if result['results']:
                print("\nSample Results:")
                for i, item in enumerate(result['results'][:3], 1):
                    print(f"  {i}. {item}")

            # Generate response if LLM available
            if generator and result['results']:
                print("\nAI Response:")
                response = generator.generate_grounded_response(query, result)
                print(response['response'][:500] + "..." if len(response['response']) > 500 else response['response'])

        connector.close()

    except Exception as e:
        logger.error(f"Live test failed: {str(e)}", exc_info=True)
        print(f"\n✗ Error: {str(e)}")


if __name__ == "__main__":
    print("\nStarting Semantic Query Understanding Tests...\n")

    # Run understanding tests
    test_query_understanding()

    # Run live query test
    test_live_query()

    print("\n" + "=" * 80)
    print("Tests Complete!")
    print("=" * 80)

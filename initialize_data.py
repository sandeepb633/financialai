"""Initialize the knowledge graph with financial data."""

import logging
import sys
import os
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.graph_db.neo4j_connector import Neo4jConnector
from src.graph_db.graph_populator import GraphPopulator
from config.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Initialize the knowledge graph with data."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║     Financial GraphRAG - Data Initialization                ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""")

    try:
        # Connect to Neo4j
        print("📡 Connecting to Neo4j...")
        connector = Neo4jConnector()
        print("✅ Connected to Neo4j successfully!\n")

        # Create schema
        print("🔧 Creating graph schema and constraints...")
        connector.create_constraints()
        print("✅ Schema created!\n")

        # Initialize populator
        print("🚀 Initializing data populator...")
        populator = GraphPopulator(connector)
        print("✅ Populator initialized!\n")

        # Get companies to track
        companies = settings.DEFAULT_COMPANIES
        print(f"📊 Tracking {len(companies)} companies:")
        print(f"   {', '.join(companies)}\n")

        # Populate data
        print("="*60)
        print("🔄 Starting data collection...")
        print("="*60)
        print("This may take several minutes depending on API rate limits.\n")

        stats = populator.refresh_all_data(companies)

        # Display results
        print("\n" + "="*60)
        print("📈 Data Collection Summary")
        print("="*60)
        print(f"✅ Companies Updated: {stats['companies_updated']}")
        print(f"❌ Companies Failed: {stats['companies_failed']}")
        print(f"📰 Market News Added: {stats['market_news_added']}")
        print(f"⏰ Timestamp: {stats['timestamp']}")

        # Get final statistics
        db_stats = connector.get_database_stats()
        print("\n" + "="*60)
        print("🗄️ Knowledge Graph Statistics")
        print("="*60)
        print(f"Companies: {db_stats['companies']}")
        print(f"News Articles: {db_stats['news']}")
        print(f"Events: {db_stats['events']}")
        print(f"Sectors: {db_stats['sectors']}")
        print(f"Relationships: {db_stats['relationships']}")

        print("\n" + "="*60)
        print("✅ Data initialization completed successfully!")
        print("="*60)
        print("\n🚀 You can now start the application:")
        print("   streamlit run src/ui/app.py\n")

        # Close connection
        connector.close()

    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
        print("\nPlease check:")
        print("1. Neo4j is running at http://localhost:7474")
        print("2. NEO4J_PASSWORD is set in .env file")
        print("3. API keys are configured in .env file")
        sys.exit(1)

    except Exception as e:
        logger.error(f"Error during initialization: {str(e)}", exc_info=True)
        print(f"\n❌ Error: {str(e)}")
        print("\nPlease check the logs for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()

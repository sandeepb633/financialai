"""Background service to auto-refresh financial data at regular intervals."""

import logging
import sys
import time
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.graph_db.neo4j_connector import Neo4jConnector
from src.graph_db.graph_populator import GraphPopulator
from config.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/auto_refresh.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def refresh_data(populator, companies):
    """Refresh all financial data."""
    try:
        logger.info("[REFRESH] Starting data refresh...")
        stats = populator.refresh_all_data(companies)

        logger.info("[SUCCESS] Refresh completed successfully!")
        logger.info(f"   Companies Updated: {stats['companies_updated']}")
        logger.info(f"   Companies Failed: {stats['companies_failed']}")
        logger.info(f"   Market News Added: {stats['market_news_added']}")

        return True
    except Exception as e:
        logger.error(f"[ERROR] Error during refresh: {str(e)}", exc_info=True)
        return False


def main():
    """Run the auto-refresh service."""
    print("""
================================================================
    Financial GraphRAG - Auto-Refresh Service
================================================================
""")

    # Get refresh interval from settings (default: 5 minutes = 300 seconds)
    refresh_interval = settings.DATA_REFRESH_INTERVAL
    companies = settings.DEFAULT_COMPANIES

    print(f"[INFO] Tracking {len(companies)} companies:")
    print(f"   {', '.join(companies)}")
    print(f"\n[INFO] Refresh interval: {refresh_interval} seconds ({refresh_interval//60} minutes)")
    print(f"\n[START] Starting auto-refresh service...")
    print(f"   Press Ctrl+C to stop\n")

    try:
        # Connect to Neo4j
        connector = Neo4jConnector()
        logger.info("[SUCCESS] Connected to Neo4j")

        # Initialize populator
        populator = GraphPopulator(connector)
        logger.info("[SUCCESS] Populator initialized")

        # Initial refresh
        logger.info("[REFRESH] Performing initial data refresh...")
        refresh_data(populator, companies)

        # Main loop
        refresh_count = 0
        while True:
            # Wait for next refresh
            next_refresh = datetime.now().timestamp() + refresh_interval
            logger.info(f"[WAIT] Next refresh in {refresh_interval//60} minutes...")

            time.sleep(refresh_interval)

            # Refresh data
            refresh_count += 1
            logger.info(f"\n{'='*60}")
            logger.info(f"[REFRESH] Refresh #{refresh_count} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info(f"{'='*60}")

            success = refresh_data(populator, companies)

            if success:
                logger.info(f"[SUCCESS] Refresh #{refresh_count} completed successfully")
            else:
                logger.error(f"[ERROR] Refresh #{refresh_count} failed")

    except KeyboardInterrupt:
        print("\n\n[STOP] Auto-refresh service stopped by user")
        logger.info("Auto-refresh service stopped")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        print(f"\n[ERROR] Fatal error: {str(e)}")
        sys.exit(1)
    finally:
        if 'connector' in locals():
            connector.close()
            logger.info("Neo4j connection closed")


if __name__ == "__main__":
    main()

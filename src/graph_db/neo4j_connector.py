"""Neo4j database connector and operations."""

from neo4j import GraphDatabase
from typing import Dict, List, Optional, Any
import logging
from config.config import settings

logger = logging.getLogger(__name__)


class Neo4jConnector:
    """Manages connection and operations with Neo4j database."""

    def __init__(self, uri: Optional[str] = None, user: Optional[str] = None, password: Optional[str] = None):
        """
        Initialize Neo4j connector.

        Args:
            uri: Neo4j URI (optional, uses config if not provided)
            user: Neo4j user (optional, uses config if not provided)
            password: Neo4j password (optional, uses config if not provided)
        """
        self.uri = uri or settings.NEO4J_URI
        self.user = user or settings.NEO4J_USER
        self.password = password or settings.NEO4J_PASSWORD

        if not self.password:
            raise ValueError("Neo4j password is required")

        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            self.driver.verify_connectivity()
            logger.info("Successfully connected to Neo4j")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {str(e)}")
            raise

    def close(self):
        """Close the database connection."""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j connection closed")

    def execute_query(self, query: str, parameters: Optional[Dict] = None) -> List[Dict]:
        """
        Execute a Cypher query.

        Args:
            query: Cypher query string
            parameters: Query parameters

        Returns:
            List of result dictionaries
        """
        with self.driver.session() as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]

    def execute_write(self, query: str, parameters: Optional[Dict] = None) -> Any:
        """
        Execute a write query.

        Args:
            query: Cypher query string
            parameters: Query parameters

        Returns:
            Query result
        """
        with self.driver.session() as session:
            result = session.write_transaction(lambda tx: tx.run(query, parameters or {}))
            return result

    def create_constraints(self):
        """Create necessary constraints and indexes."""
        constraints = [
            "CREATE CONSTRAINT company_symbol IF NOT EXISTS FOR (c:Company) REQUIRE c.symbol IS UNIQUE",
            "CREATE CONSTRAINT event_id IF NOT EXISTS FOR (e:Event) REQUIRE e.id IS UNIQUE",
            "CREATE CONSTRAINT news_id IF NOT EXISTS FOR (n:News) REQUIRE n.id IS UNIQUE",
            "CREATE CONSTRAINT sector_name IF NOT EXISTS FOR (s:Sector) REQUIRE s.name IS UNIQUE",
            "CREATE INDEX company_name IF NOT EXISTS FOR (c:Company) ON (c.name)",
            "CREATE INDEX event_timestamp IF NOT EXISTS FOR (e:Event) ON (e.timestamp)",
            "CREATE INDEX news_timestamp IF NOT EXISTS FOR (n:News) ON (n.published_at)"
        ]

        for constraint in constraints:
            try:
                self.execute_write(constraint)
                logger.info(f"Created constraint/index: {constraint[:50]}...")
            except Exception as e:
                # Constraint may already exist
                logger.debug(f"Constraint/index operation: {str(e)}")

    def clear_database(self):
        """Clear all nodes and relationships (use with caution!)."""
        query = "MATCH (n) DETACH DELETE n"
        self.execute_write(query)
        logger.warning("Database cleared")

    def get_database_stats(self) -> Dict:
        """Get database statistics."""
        queries = {
            'companies': "MATCH (c:Company) RETURN count(c) as count",
            'events': "MATCH (e:Event) RETURN count(e) as count",
            'news': "MATCH (n:News) RETURN count(n) as count",
            'sectors': "MATCH (s:Sector) RETURN count(s) as count",
            'relationships': "MATCH ()-[r]->() RETURN count(r) as count"
        }

        stats = {}
        for key, query in queries.items():
            result = self.execute_query(query)
            stats[key] = result[0]['count'] if result else 0

        return stats


class GraphOperations:
    """High-level graph operations for financial knowledge graph."""

    def __init__(self, connector: Neo4jConnector):
        """Initialize with Neo4j connector."""
        self.connector = connector

    def create_company(self, company_data: Dict) -> bool:
        """
        Create or update a company node.

        Args:
            company_data: Dictionary with company information

        Returns:
            True if successful
        """
        query = """
        MERGE (c:Company {symbol: $symbol})
        SET c.name = $name,
            c.sector = $sector,
            c.industry = $industry,
            c.market_cap = $market_cap,
            c.website = $website,
            c.description = $description,
            c.updated_at = datetime()
        RETURN c
        """

        try:
            self.connector.execute_write(query, company_data)
            logger.info(f"Created/updated company: {company_data.get('symbol')}")
            return True
        except Exception as e:
            logger.error(f"Error creating company: {str(e)}")
            return False

    def create_sector(self, sector_name: str) -> bool:
        """
        Create a sector node.

        Args:
            sector_name: Name of the sector

        Returns:
            True if successful
        """
        query = """
        MERGE (s:Sector {name: $name})
        SET s.updated_at = datetime()
        RETURN s
        """

        try:
            self.connector.execute_write(query, {'name': sector_name})
            return True
        except Exception as e:
            logger.error(f"Error creating sector: {str(e)}")
            return False

    def link_company_to_sector(self, symbol: str, sector: str) -> bool:
        """
        Link a company to its sector.

        Args:
            symbol: Company symbol
            sector: Sector name

        Returns:
            True if successful
        """
        query = """
        MATCH (c:Company {symbol: $symbol})
        MERGE (s:Sector {name: $sector})
        MERGE (c)-[r:BELONGS_TO]->(s)
        SET r.updated_at = datetime()
        RETURN c, s
        """

        try:
            self.connector.execute_write(query, {'symbol': symbol, 'sector': sector})
            return True
        except Exception as e:
            logger.error(f"Error linking company to sector: {str(e)}")
            return False

    def create_news(self, news_data: Dict) -> bool:
        """
        Create a news node.

        Args:
            news_data: Dictionary with news information

        Returns:
            True if successful
        """
        query = """
        CREATE (n:News {
            id: $id,
            headline: $headline,
            summary: $summary,
            source: $source,
            url: $url,
            published_at: $published_at,
            sentiment_label: $sentiment_label,
            sentiment_score: $sentiment_score,
            created_at: datetime()
        })
        RETURN n
        """

        try:
            self.connector.execute_write(query, news_data)
            return True
        except Exception as e:
            logger.error(f"Error creating news: {str(e)}")
            return False

    def link_news_to_company(self, news_id: str, symbol: str, sentiment: str) -> bool:
        """
        Link news to a company.

        Args:
            news_id: News article ID
            symbol: Company symbol
            sentiment: Sentiment label (positive, negative, neutral)

        Returns:
            True if successful
        """
        query = """
        MATCH (n:News {id: $news_id})
        MATCH (c:Company {symbol: $symbol})
        MERGE (n)-[r:MENTIONS {sentiment: $sentiment}]->(c)
        SET r.created_at = datetime()
        RETURN n, c
        """

        try:
            self.connector.execute_write(query, {
                'news_id': news_id,
                'symbol': symbol,
                'sentiment': sentiment
            })
            return True
        except Exception as e:
            logger.error(f"Error linking news to company: {str(e)}")
            return False

    def create_event(self, event_data: Dict) -> bool:
        """
        Create an event node.

        Args:
            event_data: Dictionary with event information

        Returns:
            True if successful
        """
        query = """
        CREATE (e:Event {
            id: $id,
            type: $type,
            description: $description,
            timestamp: $timestamp,
            impact: $impact,
            created_at: datetime()
        })
        RETURN e
        """

        try:
            self.connector.execute_write(query, event_data)
            return True
        except Exception as e:
            logger.error(f"Error creating event: {str(e)}")
            return False

    def link_event_to_company(self, event_id: str, symbol: str, relationship_type: str = "IMPACTS") -> bool:
        """
        Link an event to a company.

        Args:
            event_id: Event ID
            symbol: Company symbol
            relationship_type: Type of relationship (default: IMPACTS)

        Returns:
            True if successful
        """
        query = f"""
        MATCH (e:Event {{id: $event_id}})
        MATCH (c:Company {{symbol: $symbol}})
        MERGE (e)-[r:{relationship_type}]->(c)
        SET r.created_at = datetime()
        RETURN e, c
        """

        try:
            self.connector.execute_write(query, {'event_id': event_id, 'symbol': symbol})
            return True
        except Exception as e:
            logger.error(f"Error linking event to company: {str(e)}")
            return False

    def update_stock_price(self, symbol: str, price_data: Dict) -> bool:
        """
        Update stock price information for a company.

        Args:
            symbol: Company symbol
            price_data: Dictionary with price information

        Returns:
            True if successful
        """
        query = """
        MATCH (c:Company {symbol: $symbol})
        SET c.price = $price,
            c.price_change = $price_change,
            c.price_change_pct = $price_change_pct,
            c.volume = $volume,
            c.price_updated_at = datetime()
        RETURN c
        """

        try:
            price_data['symbol'] = symbol
            self.connector.execute_write(query, price_data)
            return True
        except Exception as e:
            logger.error(f"Error updating stock price: {str(e)}")
            return False


if __name__ == "__main__":
    # Test the connector
    logging.basicConfig(level=logging.INFO)

    try:
        connector = Neo4jConnector()
        print("Neo4j connection successful!")

        # Create constraints
        connector.create_constraints()

        # Get stats
        stats = connector.get_database_stats()
        print(f"\nDatabase Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")

        connector.close()

    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure:")
        print("1. Neo4j is running")
        print("2. NEO4J_PASSWORD is set in .env file")

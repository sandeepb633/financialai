"""GraphRAG query engine for translating natural language to graph queries."""

import logging
from typing import Dict, List, Optional, Tuple
from src.graph_db.neo4j_connector import Neo4jConnector
from src.entity_extraction.entity_extractor import EntityExtractor

logger = logging.getLogger(__name__)


class GraphRAGQueryEngine:
    """Translates natural language queries to Cypher and retrieves graph data."""

    def __init__(self, connector: Neo4jConnector):
        """
        Initialize query engine.

        Args:
            connector: Neo4j connector instance
        """
        self.connector = connector
        self.entity_extractor = EntityExtractor()

        # Query templates for common patterns
        self.query_templates = {
            'company_info': self._get_company_info_query,
            'company_news': self._get_company_news_query,
            'company_events': self._get_company_events_query,
            'sector_companies': self._get_sector_companies_query,
            'company_relationships': self._get_company_relationships_query,
            'sentiment_analysis': self._get_sentiment_analysis_query,
            'market_overview': self._get_market_overview_query,
            'trending_news': self._get_trending_news_query
        }

    def understand_query(self, query: str) -> Dict:
        """
        Understand user query and extract intent and entities.

        Args:
            query: Natural language query

        Returns:
            Dictionary with query intent and extracted entities
        """
        query_lower = query.lower()

        # Extract entities from query
        entities = self.entity_extractor.extract_financial_entities(query)

        # Determine query intent
        intent = 'company_info'  # default

        if any(word in query_lower for word in ['news', 'article', 'headlines']):
            intent = 'company_news'
        elif any(word in query_lower for word in ['event', 'earnings', 'merger', 'acquisition']):
            intent = 'company_events'
        elif any(word in query_lower for word in ['sector', 'industry']):
            intent = 'sector_companies'
        elif any(word in query_lower for word in ['sentiment', 'feeling', 'positive', 'negative']):
            intent = 'sentiment_analysis'
        elif any(word in query_lower for word in ['market', 'overview', 'summary']):
            intent = 'market_overview'
        elif any(word in query_lower for word in ['trending', 'popular', 'hot']):
            intent = 'trending_news'
        elif any(word in query_lower for word in ['relationship', 'connection', 'related', 'similar']):
            intent = 'company_relationships'

        return {
            'intent': intent,
            'entities': entities,
            'original_query': query
        }

    def execute_query(self, query: str) -> Dict:
        """
        Execute a natural language query.

        Args:
            query: Natural language query

        Returns:
            Dictionary with results and metadata
        """
        logger.info(f"Executing query: {query}")

        # Understand query
        understanding = self.understand_query(query)
        intent = understanding['intent']
        entities = understanding['entities']

        # Get query template
        query_func = self.query_templates.get(intent, self._get_company_info_query)

        # Execute query
        try:
            cypher_query, params = query_func(entities, query)
            results = self.connector.execute_query(cypher_query, params)

            return {
                'intent': intent,
                'entities': entities,
                'cypher_query': cypher_query,
                'results': results,
                'num_results': len(results)
            }

        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            return {
                'intent': intent,
                'entities': entities,
                'error': str(e),
                'results': []
            }

    def _get_company_info_query(self, entities: Dict, query: str) -> Tuple[str, Dict]:
        """Get company information query."""
        tickers = entities.get('tickers', [])
        companies = entities.get('companies', [])

        if not tickers:
            # Try to find company in the database by name or partial match
            if companies:
                cypher = """
                MATCH (c:Company)
                WHERE toLower(c.name) CONTAINS toLower($company_name)
                   OR toLower(c.symbol) CONTAINS toLower($company_name)
                OPTIONAL MATCH (c)-[:BELONGS_TO]->(s:Sector)
                RETURN c.symbol as symbol, c.name as name, c.sector as sector,
                       c.industry as industry, c.price as price,
                       c.price_change as price_change,
                       c.price_change_pct as price_change_pct,
                       c.volume as volume, c.market_cap as market_cap,
                       c.website as website, c.description as description,
                       s.name as sector_name
                LIMIT 10
                """
                return cypher, {'company_name': companies[0]}
            else:
                # Return all companies if no specific company mentioned
                cypher = """
                MATCH (c:Company)
                OPTIONAL MATCH (c)-[:BELONGS_TO]->(s:Sector)
                RETURN c.symbol as symbol, c.name as name, c.sector as sector,
                       c.price as price, c.price_change_pct as price_change_pct,
                       c.market_cap as market_cap
                ORDER BY c.market_cap DESC
                LIMIT 10
                """
                return cypher, {}

        symbol = tickers[0]
        cypher = """
        MATCH (c:Company {symbol: $symbol})
        OPTIONAL MATCH (c)-[:BELONGS_TO]->(s:Sector)
        RETURN c.symbol as symbol, c.name as name, c.sector as sector,
               c.industry as industry, c.price as price,
               c.price_change as price_change,
               c.price_change_pct as price_change_pct,
               c.volume as volume, c.market_cap as market_cap,
               c.website as website, c.description as description,
               s.name as sector_name
        """

        return cypher, {'symbol': symbol}

    def _get_company_news_query(self, entities: Dict, query: str) -> Tuple[str, Dict]:
        """Get company news query."""
        tickers = entities.get('tickers', [])

        if not tickers:
            cypher = """
            MATCH (n:News)
            RETURN n.headline as headline, n.summary as summary,
                   n.source as source, n.published_at as published_at,
                   n.sentiment_label as sentiment, n.url as url
            ORDER BY n.published_at DESC
            LIMIT 20
            """
            return cypher, {}

        symbol = tickers[0]
        cypher = """
        MATCH (n:News)-[r:MENTIONS]->(c:Company {symbol: $symbol})
        RETURN n.headline as headline, n.summary as summary,
               n.source as source, n.published_at as published_at,
               n.sentiment_label as sentiment, r.sentiment as mention_sentiment,
               n.url as url, c.name as company_name
        ORDER BY n.published_at DESC
        LIMIT 20
        """

        return cypher, {'symbol': symbol}

    def _get_company_events_query(self, entities: Dict, query: str) -> Tuple[str, Dict]:
        """Get company events query."""
        tickers = entities.get('tickers', [])

        if not tickers:
            return "MATCH (e:Event) RETURN e ORDER BY e.timestamp DESC LIMIT 20", {}

        symbol = tickers[0]
        cypher = """
        MATCH (e:Event)-[:IMPACTS]->(c:Company {symbol: $symbol})
        RETURN e.type as event_type, e.description as description,
               e.timestamp as timestamp, e.impact as impact,
               c.name as company_name
        ORDER BY e.timestamp DESC
        LIMIT 20
        """

        return cypher, {'symbol': symbol}

    def _get_sector_companies_query(self, entities: Dict, query: str) -> Tuple[str, Dict]:
        """Get companies in a sector query."""
        # Extract sector from query
        sectors = ['technology', 'healthcare', 'financial', 'energy', 'consumer', 'industrial']
        query_lower = query.lower()

        sector = None
        for s in sectors:
            if s in query_lower:
                sector = s.capitalize()
                break

        if not sector:
            return "MATCH (s:Sector)<-[:BELONGS_TO]-(c:Company) RETURN s.name as sector, count(c) as count", {}

        cypher = """
        MATCH (s:Sector)<-[:BELONGS_TO]-(c:Company)
        WHERE s.name CONTAINS $sector
        RETURN c.symbol as symbol, c.name as name, c.price as price,
               c.price_change_pct as price_change_pct, s.name as sector
        ORDER BY c.market_cap DESC
        LIMIT 20
        """

        return cypher, {'sector': sector}

    def _get_company_relationships_query(self, entities: Dict, query: str) -> Tuple[str, Dict]:
        """Get company relationships query."""
        tickers = entities.get('tickers', [])

        if not tickers:
            return "MATCH (c1:Company)-[r]-(c2:Company) RETURN c1, r, c2 LIMIT 20", {}

        symbol = tickers[0]
        cypher = """
        MATCH (c:Company {symbol: $symbol})<-[:BELONGS_TO]-(s:Sector)-[:BELONGS_TO]->(other:Company)
        WHERE other.symbol <> $symbol
        RETURN other.symbol as symbol, other.name as name,
               other.price as price, other.price_change_pct as price_change_pct,
               s.name as sector
        ORDER BY other.market_cap DESC
        LIMIT 10
        """

        return cypher, {'symbol': symbol}

    def _get_sentiment_analysis_query(self, entities: Dict, query: str) -> Tuple[str, Dict]:
        """Get sentiment analysis query."""
        tickers = entities.get('tickers', [])

        if not tickers:
            cypher = """
            MATCH (n:News)-[:MENTIONS]->(c:Company)
            RETURN c.symbol as symbol, c.name as name,
                   n.sentiment_label as sentiment,
                   count(n) as article_count
            GROUP BY c.symbol, c.name, n.sentiment_label
            ORDER BY article_count DESC
            LIMIT 20
            """
            return cypher, {}

        symbol = tickers[0]
        cypher = """
        MATCH (n:News)-[:MENTIONS]->(c:Company {symbol: $symbol})
        RETURN c.name as company_name,
               n.sentiment_label as sentiment,
               count(n) as count,
               avg(n.sentiment_score) as avg_score
        GROUP BY c.name, n.sentiment_label
        """

        return cypher, {'symbol': symbol}

    def _get_market_overview_query(self, entities: Dict, query: str) -> Tuple[str, Dict]:
        """Get market overview query."""
        cypher = """
        MATCH (c:Company)
        OPTIONAL MATCH (c)-[:BELONGS_TO]->(s:Sector)
        RETURN s.name as sector,
               count(c) as company_count,
               avg(c.price_change_pct) as avg_change,
               sum(c.market_cap) as total_market_cap
        GROUP BY s.name
        ORDER BY total_market_cap DESC
        """

        return cypher, {}

    def _get_trending_news_query(self, entities: Dict, query: str) -> Tuple[str, Dict]:
        """Get trending news query."""
        cypher = """
        MATCH (n:News)-[:MENTIONS]->(c:Company)
        WITH c, count(n) as mention_count, collect(n) as news_items
        ORDER BY mention_count DESC
        LIMIT 5
        UNWIND news_items as n
        RETURN c.symbol as symbol, c.name as company_name,
               n.headline as headline, n.published_at as published_at,
               n.sentiment_label as sentiment
        ORDER BY c.symbol, n.published_at DESC
        LIMIT 20
        """

        return cypher, {}


if __name__ == "__main__":
    # Test the query engine
    logging.basicConfig(level=logging.INFO)

    try:
        connector = Neo4jConnector()
        engine = GraphRAGQueryEngine(connector)

        test_queries = [
            "What's the latest news about Apple?",
            "Show me companies in the technology sector",
            "What's the sentiment for TSLA?",
            "Tell me about Microsoft's recent events"
        ]

        print("Testing GraphRAG Query Engine...\n")

        for query in test_queries:
            print(f"\nQuery: {query}")
            result = engine.execute_query(query)
            print(f"Intent: {result['intent']}")
            print(f"Results: {result['num_results']} items")

        connector.close()

    except Exception as e:
        print(f"Error: {e}")

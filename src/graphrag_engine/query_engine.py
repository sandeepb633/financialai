"""GraphRAG query engine for translating natural language to graph queries."""

import logging
from typing import Dict, List, Optional, Tuple
from src.graph_db.neo4j_connector import Neo4jConnector
from src.entity_extraction.entity_extractor import EntityExtractor
import json

logger = logging.getLogger(__name__)


class GraphRAGQueryEngine:
    """Translates natural language queries to Cypher and retrieves graph data."""

    def __init__(self, connector: Neo4jConnector, llm_client=None):
        """
        Initialize query engine.

        Args:
            connector: Neo4j connector instance
            llm_client: Optional LLM client for semantic query understanding
        """
        self.connector = connector
        self.llm_client = llm_client
        # Pass LLM client to entity extractor for enhanced extraction
        self.entity_extractor = EntityExtractor(llm_client=llm_client)

        # Financial terminology mapping for better semantic understanding
        self.financial_synonyms = {
            'sentiment': ['feeling', 'mood', 'opinion', 'perception', 'outlook', 'tone', 'attitude', 'view'],
            'news': ['article', 'headlines', 'stories', 'updates', 'reports', 'announcements', 'press'],
            'events': ['earnings', 'merger', 'acquisition', 'announcement', 'conference', 'filing', 'dividend'],
            'performance': ['returns', 'gains', 'losses', 'growth', 'decline', 'change', 'movement'],
            'market': ['stock', 'trading', 'exchange', 'securities', 'equities', 'shares'],
            'overview': ['summary', 'snapshot', 'breakdown', 'analysis', 'report', 'status'],
            'sector': ['industry', 'vertical', 'segment', 'category', 'group'],
            'price': ['value', 'quote', 'trading at', 'worth', 'valuation', 'cost'],
            'trending': ['popular', 'hot', 'buzz', 'spotlight', 'attention', 'focus']
        }

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

    def _semantic_intent_classification(self, query: str, entities: Dict) -> str:
        """
        Use LLM to classify query intent semantically.

        Args:
            query: Natural language query
            entities: Extracted entities

        Returns:
            Classified intent
        """
        if not self.llm_client:
            return self._rule_based_intent_classification(query)

        intent_prompt = f"""You are a financial query classifier. Analyze the user's query and classify it into ONE of these intents:

Available Intents:
1. company_info - General information about a company (price, market cap, description, fundamentals)
2. company_news - News articles and updates about companies
3. company_events - Corporate events (earnings, mergers, acquisitions, filings)
4. sentiment_analysis - Market sentiment, investor perception, mood, outlook, tone
5. market_overview - Overall market summary, sector performance, market trends
6. sector_companies - Companies within a specific sector/industry
7. trending_news - Popular/trending topics and companies in the news
8. company_relationships - Related companies, competitors, same sector companies

User Query: "{query}"
Extracted Entities: {json.dumps(entities)}

Respond with ONLY the intent name (e.g., "sentiment_analysis"). Consider:
- Synonyms and different phrasings (e.g., "mood" → sentiment, "feeling" → sentiment)
- Financial terminology (e.g., "outlook" → sentiment, "performance" → company_info)
- Context from extracted entities

Intent:"""

        try:
            response = self.llm_client.generate_response(
                prompt=intent_prompt,
                temperature=0.1  # Low temperature for consistent classification
            ).strip().lower()

            # Validate the response
            valid_intents = list(self.query_templates.keys())
            if response in valid_intents:
                return response

            # Try to extract intent from response if LLM was verbose
            for intent in valid_intents:
                if intent in response:
                    return intent

            logger.warning(f"LLM returned invalid intent '{response}', falling back to rule-based")
            return self._rule_based_intent_classification(query)

        except Exception as e:
            logger.warning(f"LLM intent classification failed: {e}, falling back to rule-based")
            return self._rule_based_intent_classification(query)

    def _rule_based_intent_classification(self, query: str) -> str:
        """
        Rule-based intent classification with enhanced synonym matching.

        Args:
            query: Natural language query

        Returns:
            Classified intent
        """
        query_lower = query.lower()

        # Check for sentiment-related queries with expanded synonyms
        sentiment_keywords = ['sentiment'] + self.financial_synonyms['sentiment']
        if any(word in query_lower for word in sentiment_keywords):
            return 'sentiment_analysis'

        # Check for news-related queries
        news_keywords = ['news'] + self.financial_synonyms['news']
        if any(word in query_lower for word in news_keywords):
            return 'company_news'

        # Check for events
        event_keywords = ['event'] + self.financial_synonyms['events']
        if any(word in query_lower for word in event_keywords):
            return 'company_events'

        # Check for sector/industry queries
        sector_keywords = ['sector'] + self.financial_synonyms['sector']
        if any(word in query_lower for word in sector_keywords):
            return 'sector_companies'

        # Check for market overview
        overview_keywords = ['overview'] + self.financial_synonyms['overview']
        market_keywords = ['market'] + self.financial_synonyms['market']
        if any(word in query_lower for word in overview_keywords + market_keywords):
            # Distinguish between market overview and company info
            if any(word in query_lower for word in overview_keywords):
                return 'market_overview'

        # Check for trending
        trending_keywords = ['trending'] + self.financial_synonyms['trending']
        if any(word in query_lower for word in trending_keywords):
            return 'trending_news'

        # Check for relationships
        if any(word in query_lower for word in ['relationship', 'connection', 'related', 'similar', 'competitor', 'peer']):
            return 'company_relationships'

        # Default to company info
        return 'company_info'

    def understand_query(self, query: str) -> Dict:
        """
        Understand user query and extract intent and entities.

        Args:
            query: Natural language query

        Returns:
            Dictionary with query intent and extracted entities
        """
        # Extract entities from query
        entities = self.entity_extractor.extract_financial_entities(query)

        # Determine query intent using semantic or rule-based classification
        if self.llm_client:
            intent = self._semantic_intent_classification(query, entities)
            logger.info(f"LLM classified intent: {intent}")
        else:
            intent = self._rule_based_intent_classification(query)
            logger.info(f"Rule-based classified intent: {intent}")

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
            # Get overall market sentiment breakdown by company and sentiment type
            cypher = """
            MATCH (n:News)-[:MENTIONS]->(c:Company)
            WITH c.symbol as symbol, c.name as name, n.sentiment_label as sentiment
            WITH symbol, name, sentiment, count(*) as article_count
            RETURN symbol, name, sentiment, article_count
            ORDER BY article_count DESC
            LIMIT 20
            """
            return cypher, {}

        symbol = tickers[0]
        cypher = """
        MATCH (n:News)-[:MENTIONS]->(c:Company {symbol: $symbol})
        WITH c.name as company_name, n.sentiment_label as sentiment, n.sentiment_score as score
        WITH company_name, sentiment, count(*) as count, avg(score) as avg_score
        RETURN company_name, sentiment, count, avg_score
        ORDER BY count DESC
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

"""Graph populator for building the financial knowledge graph."""

import logging
import hashlib
from datetime import datetime
from typing import Dict, List
from .neo4j_connector import Neo4jConnector, GraphOperations
from src.data_ingestion.data_aggregator import DataAggregator
from src.entity_extraction.entity_extractor import EntityExtractor

logger = logging.getLogger(__name__)


class GraphPopulator:
    """Populates Neo4j graph with financial data."""

    def __init__(self, connector: Neo4jConnector):
        """
        Initialize graph populator.

        Args:
            connector: Neo4j connector instance
        """
        self.connector = connector
        self.graph_ops = GraphOperations(connector)
        self.data_aggregator = DataAggregator()
        self.entity_extractor = EntityExtractor()

    def generate_id(self, *args) -> str:
        """Generate a unique ID from arguments."""
        combined = '_'.join(str(arg) for arg in args)
        return hashlib.md5(combined.encode()).hexdigest()

    def populate_company(self, symbol: str) -> bool:
        """
        Populate company data into the graph.

        Args:
            symbol: Stock ticker symbol

        Returns:
            True if successful
        """
        logger.info(f"Populating data for {symbol}")

        try:
            # Collect company data
            data = self.data_aggregator.collect_company_data(symbol)

            if not data:
                logger.warning(f"No data collected for {symbol}")
                return False

            # Create company node
            company_info = data.get('company_info') or data.get('stock_data')
            if company_info:
                company_data = {
                    'symbol': symbol,
                    'name': company_info.get('name', symbol),
                    'sector': company_info.get('sector', 'Unknown'),
                    'industry': company_info.get('industry', 'Unknown'),
                    'market_cap': company_info.get('market_cap', 0),
                    'website': company_info.get('website', ''),
                    'description': company_info.get('description', '')
                }

                self.graph_ops.create_company(company_data)

                # Link to sector
                if company_data['sector'] != 'Unknown':
                    self.graph_ops.create_sector(company_data['sector'])
                    self.graph_ops.link_company_to_sector(symbol, company_data['sector'])

            # Update stock price
            stock_data = data.get('stock_data')
            if stock_data:
                price_data = {
                    'price': stock_data.get('price', 0),
                    'price_change': stock_data.get('price_change', 0),
                    'price_change_pct': stock_data.get('price_change_pct', 0),
                    'volume': stock_data.get('volume', 0)
                }
                self.graph_ops.update_stock_price(symbol, price_data)

            # Process and add news articles
            news_articles = data.get('company_news', [])
            for article in news_articles[:20]:  # Limit to 20 most recent articles
                self.add_news_article(article, symbol)

            logger.info(f"Successfully populated data for {symbol}")
            return True

        except Exception as e:
            logger.error(f"Error populating company {symbol}: {str(e)}")
            return False

    def add_news_article(self, article: Dict, symbol: str = None) -> bool:
        """
        Add a news article to the graph.

        Args:
            article: News article dictionary
            symbol: Related company symbol (optional)

        Returns:
            True if successful
        """
        try:
            # Process article with entity extractor
            processed = self.entity_extractor.process_news_article(article)

            # Generate unique ID for news
            url = article.get('url', '')
            headline = article.get('headline') or article.get('title', '')
            news_id = self.generate_id(url, headline)

            # Get sentiment
            sentiment = processed.get('extracted', {}).get('sentiment', {})
            sentiment_label = sentiment.get('label', 'neutral')
            sentiment_score = sentiment.get('score', 0.0)

            # Create news node
            news_data = {
                'id': news_id,
                'headline': headline,
                'summary': article.get('summary') or article.get('description', ''),
                'source': article.get('source', ''),
                'url': url,
                'published_at': article.get('published_at', datetime.now().isoformat()),
                'sentiment_label': sentiment_label,
                'sentiment_score': sentiment_score
            }

            self.graph_ops.create_news(news_data)

            # Link to companies mentioned
            entities = processed.get('extracted', {}).get('entities', {})
            companies = entities.get('companies', [])
            tickers = entities.get('tickers', [])

            # Add the provided symbol if available
            if symbol and symbol not in tickers:
                tickers.append(symbol)

            # Link news to companies
            for ticker in tickers:
                self.graph_ops.link_news_to_company(news_id, ticker, sentiment_label)

            # Extract and create events
            events = processed.get('extracted', {}).get('events', [])
            for event in events:
                event_id = self.generate_id(news_id, event['type'])
                event_data = {
                    'id': event_id,
                    'type': event['type'],
                    'description': headline,
                    'timestamp': article.get('published_at', datetime.now().isoformat()),
                    'impact': sentiment_label
                }

                self.graph_ops.create_event(event_data)

                # Link event to companies
                for ticker in tickers:
                    self.graph_ops.link_event_to_company(event_id, ticker)

            return True

        except Exception as e:
            logger.error(f"Error adding news article: {str(e)}")
            return False

    def populate_multiple_companies(self, symbols: List[str]) -> Dict[str, bool]:
        """
        Populate data for multiple companies.

        Args:
            symbols: List of stock ticker symbols

        Returns:
            Dictionary mapping symbols to success status
        """
        results = {}
        for symbol in symbols:
            results[symbol] = self.populate_company(symbol)

        return results

    def populate_market_news(self) -> int:
        """
        Populate general market news.

        Returns:
            Number of articles added
        """
        logger.info("Populating market news")

        try:
            news_articles = self.data_aggregator.collect_market_news()
            count = 0

            for article in news_articles:
                if self.add_news_article(article):
                    count += 1

            logger.info(f"Added {count} market news articles")
            return count

        except Exception as e:
            logger.error(f"Error populating market news: {str(e)}")
            return 0

    def refresh_all_data(self, symbols: List[str]) -> Dict:
        """
        Refresh all data in the graph.

        Args:
            symbols: List of stock ticker symbols

        Returns:
            Dictionary with refresh statistics
        """
        logger.info(f"Refreshing data for {len(symbols)} companies")

        stats = {
            'companies_updated': 0,
            'companies_failed': 0,
            'market_news_added': 0,
            'timestamp': datetime.now().isoformat()
        }

        # Populate companies
        results = self.populate_multiple_companies(symbols)
        stats['companies_updated'] = sum(1 for success in results.values() if success)
        stats['companies_failed'] = sum(1 for success in results.values() if not success)

        # Populate market news
        stats['market_news_added'] = self.populate_market_news()

        logger.info(f"Refresh complete: {stats}")
        return stats


if __name__ == "__main__":
    # Test the graph populator
    logging.basicConfig(level=logging.INFO)

    try:
        connector = Neo4jConnector()
        populator = GraphPopulator(connector)

        print("Testing Graph Populator...")
        print("\n1. Populating data for AAPL:")
        success = populator.populate_company("AAPL")
        print(f"   Success: {success}")

        print("\n2. Getting database stats:")
        stats = connector.get_database_stats()
        for key, value in stats.items():
            print(f"   {key}: {value}")

        connector.close()

    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure Neo4j is running and configured properly")

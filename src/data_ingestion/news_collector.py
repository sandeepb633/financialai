"""NewsAPI collector for financial news."""

import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
from config.config import settings

logger = logging.getLogger(__name__)


class NewsAPICollector:
    """Collects financial news from NewsAPI."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize NewsAPI collector.

        Args:
            api_key: NewsAPI key (optional, uses config if not provided)
        """
        self.api_key = api_key or settings.NEWSAPI_KEY
        if not self.api_key:
            raise ValueError("NewsAPI key is required")

        self.base_url = "https://newsapi.org/v2"

    def search_news(self, query: str, days: int = 7, language: str = 'en') -> List[Dict]:
        """
        Search for news articles by query.

        Args:
            query: Search query
            days: Number of days to look back
            language: Language code (default: 'en')

        Returns:
            List of news articles
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            params = {
                'q': query,
                'from': start_date.strftime('%Y-%m-%d'),
                'to': end_date.strftime('%Y-%m-%d'),
                'language': language,
                'sortBy': 'publishedAt',
                'apiKey': self.api_key
            }

            response = requests.get(f"{self.base_url}/everything", params=params)
            response.raise_for_status()

            data = response.json()
            articles = []

            for article in data.get('articles', [])[:50]:  # Limit to 50 articles
                articles.append({
                    'query': query,
                    'title': article.get('title', ''),
                    'description': article.get('description', ''),
                    'content': article.get('content', ''),
                    'author': article.get('author', ''),
                    'source': article.get('source', {}).get('name', ''),
                    'url': article.get('url', ''),
                    'image_url': article.get('urlToImage', ''),
                    'published_at': article.get('publishedAt', ''),
                    'timestamp': datetime.now().isoformat()
                })

            return articles

        except Exception as e:
            logger.error(f"Error searching news for '{query}': {str(e)}")
            return []

    def get_top_headlines(self, category: str = 'business', country: str = 'us') -> List[Dict]:
        """
        Get top headlines.

        Args:
            category: News category (business, technology, etc.)
            country: Country code (default: 'us')

        Returns:
            List of news articles
        """
        try:
            params = {
                'category': category,
                'country': country,
                'apiKey': self.api_key
            }

            response = requests.get(f"{self.base_url}/top-headlines", params=params)
            response.raise_for_status()

            data = response.json()
            articles = []

            for article in data.get('articles', [])[:30]:  # Limit to 30 articles
                articles.append({
                    'category': category,
                    'title': article.get('title', ''),
                    'description': article.get('description', ''),
                    'content': article.get('content', ''),
                    'author': article.get('author', ''),
                    'source': article.get('source', {}).get('name', ''),
                    'url': article.get('url', ''),
                    'image_url': article.get('urlToImage', ''),
                    'published_at': article.get('publishedAt', ''),
                    'timestamp': datetime.now().isoformat()
                })

            return articles

        except Exception as e:
            logger.error(f"Error fetching top headlines: {str(e)}")
            return []

    def get_company_news(self, company_name: str, days: int = 7) -> List[Dict]:
        """
        Get news about a specific company.

        Args:
            company_name: Company name or ticker
            days: Number of days to look back

        Returns:
            List of news articles
        """
        return self.search_news(company_name, days=days)


if __name__ == "__main__":
    # Test the collector
    logging.basicConfig(level=logging.INFO)

    try:
        collector = NewsAPICollector()
        print("Testing NewsAPI Collector...")

        print("\n1. Top Business Headlines:")
        headlines = collector.get_top_headlines(category='business')
        for article in headlines[:5]:
            print(f"  - {article['title']}")

        print("\n2. Apple News:")
        apple_news = collector.get_company_news("Apple Inc", days=3)
        for article in apple_news[:3]:
            print(f"  - {article['title']}")

    except ValueError as e:
        print(f"Error: {e}")
        print("Please set NEWSAPI_KEY in your .env file")

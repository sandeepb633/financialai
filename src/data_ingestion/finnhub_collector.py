"""Finnhub API collector for financial news and events."""

import finnhub
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
from config.config import settings

logger = logging.getLogger(__name__)


class FinnhubCollector:
    """Collects financial news and data from Finnhub API."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Finnhub collector.

        Args:
            api_key: Finnhub API key (optional, uses config if not provided)
        """
        api_key = api_key or settings.FINNHUB_API_KEY
        if not api_key:
            raise ValueError("Finnhub API key is required")

        self.client = finnhub.Client(api_key=api_key)

    def get_company_news(self, symbol: str, days: int = 7) -> List[Dict]:
        """
        Get company news for a symbol.

        Args:
            symbol: Stock ticker symbol
            days: Number of days to look back

        Returns:
            List of news articles
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            news = self.client.company_news(
                symbol,
                _from=start_date.strftime('%Y-%m-%d'),
                to=end_date.strftime('%Y-%m-%d')
            )

            articles = []
            for article in news:
                articles.append({
                    'symbol': symbol,
                    'headline': article.get('headline', ''),
                    'summary': article.get('summary', ''),
                    'source': article.get('source', ''),
                    'url': article.get('url', ''),
                    'published_at': datetime.fromtimestamp(article.get('datetime', 0)).isoformat(),
                    'category': article.get('category', 'general'),
                    'image': article.get('image', ''),
                    'timestamp': datetime.now().isoformat()
                })

            return articles

        except Exception as e:
            logger.error(f"Error fetching company news for {symbol}: {str(e)}")
            return []

    def get_market_news(self, category: str = 'general') -> List[Dict]:
        """
        Get general market news.

        Args:
            category: News category (general, forex, crypto, merger)

        Returns:
            List of news articles
        """
        try:
            news = self.client.general_news(category)

            articles = []
            for article in news[:20]:  # Limit to 20 articles
                articles.append({
                    'headline': article.get('headline', ''),
                    'summary': article.get('summary', ''),
                    'source': article.get('source', ''),
                    'url': article.get('url', ''),
                    'published_at': datetime.fromtimestamp(article.get('datetime', 0)).isoformat(),
                    'category': category,
                    'image': article.get('image', ''),
                    'timestamp': datetime.now().isoformat()
                })

            return articles

        except Exception as e:
            logger.error(f"Error fetching market news: {str(e)}")
            return []

    def get_company_profile(self, symbol: str) -> Optional[Dict]:
        """
        Get company profile information.

        Args:
            symbol: Stock ticker symbol

        Returns:
            Company profile dictionary or None if error
        """
        try:
            profile = self.client.company_profile2(symbol=symbol)

            if not profile:
                return None

            return {
                'symbol': symbol,
                'name': profile.get('name', ''),
                'ticker': profile.get('ticker', symbol),
                'exchange': profile.get('exchange', ''),
                'industry': profile.get('finnhubIndustry', ''),
                'website': profile.get('weburl', ''),
                'logo': profile.get('logo', ''),
                'market_cap': profile.get('marketCapitalization', 0),
                'ipo_date': profile.get('ipo', ''),
                'phone': profile.get('phone', ''),
                'outstanding_shares': profile.get('shareOutstanding', 0),
                'currency': profile.get('currency', 'USD'),
                'country': profile.get('country', ''),
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error fetching company profile for {symbol}: {str(e)}")
            return None

    def get_basic_financials(self, symbol: str) -> Optional[Dict]:
        """
        Get basic financial metrics.

        Args:
            symbol: Stock ticker symbol

        Returns:
            Financial metrics dictionary or None if error
        """
        try:
            financials = self.client.company_basic_financials(symbol, 'all')

            if not financials or 'metric' not in financials:
                return None

            metrics = financials['metric']

            return {
                'symbol': symbol,
                'pe_ratio': metrics.get('peBasicExclExtraTTM', None),
                'ps_ratio': metrics.get('psAnnual', None),
                'pb_ratio': metrics.get('pbAnnual', None),
                'dividend_yield': metrics.get('dividendYieldIndicatedAnnual', None),
                'eps': metrics.get('epsBasicExclExtraItemsTTM', None),
                'revenue': metrics.get('revenueTTM', None),
                'profit_margin': metrics.get('netProfitMarginTTM', None),
                'roe': metrics.get('roeTTM', None),
                'roa': metrics.get('roaTTM', None),
                'beta': metrics.get('beta', None),
                'week_52_high': metrics.get('52WeekHigh', None),
                'week_52_low': metrics.get('52WeekLow', None),
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error fetching financials for {symbol}: {str(e)}")
            return None

    def get_earnings_calendar(self, symbol: str) -> List[Dict]:
        """
        Get earnings calendar for a company.

        Args:
            symbol: Stock ticker symbol

        Returns:
            List of earnings events
        """
        try:
            # Get earnings for the next 30 days
            end_date = datetime.now() + timedelta(days=30)
            start_date = datetime.now() - timedelta(days=30)

            earnings = self.client.earnings_calendar(
                _from=start_date.strftime('%Y-%m-%d'),
                to=end_date.strftime('%Y-%m-%d'),
                symbol=symbol
            )

            events = []
            for event in earnings.get('earningsCalendar', []):
                if event.get('symbol') == symbol:
                    events.append({
                        'symbol': symbol,
                        'date': event.get('date', ''),
                        'eps_estimate': event.get('epsEstimate', None),
                        'eps_actual': event.get('epsActual', None),
                        'revenue_estimate': event.get('revenueEstimate', None),
                        'revenue_actual': event.get('revenueActual', None),
                        'event_type': 'earnings',
                        'timestamp': datetime.now().isoformat()
                    })

            return events

        except Exception as e:
            logger.error(f"Error fetching earnings calendar for {symbol}: {str(e)}")
            return []


if __name__ == "__main__":
    # Test the collector
    logging.basicConfig(level=logging.INFO)

    try:
        collector = FinnhubCollector()
        print("Testing Finnhub Collector...")

        print("\n1. Company News for AAPL:")
        news = collector.get_company_news("AAPL", days=3)
        for article in news[:3]:
            print(f"  - {article['headline']}")

        print("\n2. Company Profile for AAPL:")
        profile = collector.get_company_profile("AAPL")
        if profile:
            print(f"  Name: {profile['name']}")
            print(f"  Industry: {profile['industry']}")

    except ValueError as e:
        print(f"Error: {e}")
        print("Please set FINNHUB_API_KEY in your .env file")

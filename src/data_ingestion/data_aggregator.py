"""Data aggregator combining multiple financial data sources."""

import logging
from typing import Dict, List, Optional
from datetime import datetime
from .yahoo_finance_collector import YahooFinanceCollector
from .finnhub_collector import FinnhubCollector
from .news_collector import NewsAPICollector

logger = logging.getLogger(__name__)


class DataAggregator:
    """Aggregates data from multiple financial sources."""

    def __init__(self):
        """Initialize data aggregator with all collectors."""
        self.yahoo_collector = YahooFinanceCollector()

        try:
            self.finnhub_collector = FinnhubCollector()
        except ValueError:
            logger.warning("Finnhub collector not initialized - API key missing")
            self.finnhub_collector = None

        try:
            self.news_collector = NewsAPICollector()
        except ValueError:
            logger.warning("NewsAPI collector not initialized - API key missing")
            self.news_collector = None

    def collect_company_data(self, symbol: str) -> Dict:
        """
        Collect comprehensive data for a company.

        Args:
            symbol: Stock ticker symbol

        Returns:
            Dictionary with all collected data
        """
        logger.info(f"Collecting data for {symbol}")

        data = {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'stock_data': None,
            'company_info': None,
            'company_news': [],
            'profile': None,
            'financials': None
        }

        # Yahoo Finance data
        data['stock_data'] = self.yahoo_collector.get_stock_data(symbol)
        data['company_info'] = self.yahoo_collector.get_company_info(symbol)

        # Finnhub data
        if self.finnhub_collector:
            data['company_news'] = self.finnhub_collector.get_company_news(symbol, days=7)
            data['profile'] = self.finnhub_collector.get_company_profile(symbol)
            data['financials'] = self.finnhub_collector.get_basic_financials(symbol)

        # NewsAPI data
        if self.news_collector and data['company_info']:
            company_name = data['company_info'].get('name', symbol)
            news = self.news_collector.get_company_news(company_name, days=7)
            data['company_news'].extend(news)

        return data

    def collect_multiple_companies(self, symbols: List[str]) -> List[Dict]:
        """
        Collect data for multiple companies.

        Args:
            symbols: List of stock ticker symbols

        Returns:
            List of company data dictionaries
        """
        results = []
        for symbol in symbols:
            try:
                data = self.collect_company_data(symbol)
                results.append(data)
            except Exception as e:
                logger.error(f"Error collecting data for {symbol}: {str(e)}")

        return results

    def collect_market_news(self) -> List[Dict]:
        """
        Collect general market news.

        Returns:
            List of news articles
        """
        news = []

        # Finnhub market news
        if self.finnhub_collector:
            news.extend(self.finnhub_collector.get_market_news('general'))

        # NewsAPI top headlines
        if self.news_collector:
            news.extend(self.news_collector.get_top_headlines('business'))

        return news

    def get_real_time_snapshot(self, symbols: List[str]) -> Dict:
        """
        Get a real-time snapshot of market data.

        Args:
            symbols: List of stock ticker symbols

        Returns:
            Dictionary with market snapshot
        """
        logger.info(f"Creating real-time snapshot for {len(symbols)} companies")

        snapshot = {
            'timestamp': datetime.now().isoformat(),
            'companies': [],
            'market_news': [],
            'summary': {
                'total_companies': len(symbols),
                'gainers': [],
                'losers': [],
                'most_active': []
            }
        }

        # Collect company data
        company_data = self.collect_multiple_companies(symbols)
        snapshot['companies'] = company_data

        # Collect market news
        snapshot['market_news'] = self.collect_market_news()

        # Calculate summary statistics
        for data in company_data:
            stock = data.get('stock_data')
            if stock and stock.get('price_change_pct'):
                pct_change = stock['price_change_pct']
                symbol = stock['symbol']

                if pct_change > 2:
                    snapshot['summary']['gainers'].append({
                        'symbol': symbol,
                        'change': pct_change
                    })
                elif pct_change < -2:
                    snapshot['summary']['losers'].append({
                        'symbol': symbol,
                        'change': pct_change
                    })

        # Sort gainers and losers
        snapshot['summary']['gainers'].sort(key=lambda x: x['change'], reverse=True)
        snapshot['summary']['losers'].sort(key=lambda x: x['change'])

        return snapshot


if __name__ == "__main__":
    # Test the aggregator
    logging.basicConfig(level=logging.INFO)

    aggregator = DataAggregator()

    print("Testing Data Aggregator...")
    print("\n1. Collecting data for AAPL:")
    data = aggregator.collect_company_data("AAPL")

    if data['stock_data']:
        print(f"  Price: ${data['stock_data']['price']:.2f}")
        print(f"  Change: {data['stock_data']['price_change_pct']:.2f}%")

    if data['company_news']:
        print(f"  News articles: {len(data['company_news'])}")

"""Yahoo Finance data collector for stock prices and company information."""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class YahooFinanceCollector:
    """Collects financial data from Yahoo Finance."""

    def __init__(self):
        """Initialize Yahoo Finance collector."""
        self.cache = {}

    def get_stock_data(self, symbol: str, period: str = "1d") -> Optional[Dict]:
        """
        Get stock data for a symbol.

        Args:
            symbol: Stock ticker symbol
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)

        Returns:
            Dictionary with stock data or None if error
        """
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)

            if hist.empty:
                logger.warning(f"No data found for {symbol}")
                return None

            # Get latest data
            latest = hist.iloc[-1]
            previous = hist.iloc[-2] if len(hist) > 1 else hist.iloc[-1]

            # Calculate changes
            price_change = latest['Close'] - previous['Close']
            price_change_pct = (price_change / previous['Close']) * 100

            info = ticker.info

            return {
                'symbol': symbol,
                'name': info.get('longName', symbol),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                'price': float(latest['Close']),
                'previous_close': float(previous['Close']),
                'price_change': float(price_change),
                'price_change_pct': float(price_change_pct),
                'volume': int(latest['Volume']),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', None),
                'dividend_yield': info.get('dividendYield', None),
                'fifty_two_week_high': info.get('fiftyTwoWeekHigh', None),
                'fifty_two_week_low': info.get('fiftyTwoWeekLow', None),
                'timestamp': datetime.now().isoformat(),
                'currency': info.get('currency', 'USD')
            }

        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
            return None

    def get_multiple_stocks(self, symbols: List[str]) -> List[Dict]:
        """
        Get stock data for multiple symbols.

        Args:
            symbols: List of stock ticker symbols

        Returns:
            List of dictionaries with stock data
        """
        results = []
        for symbol in symbols:
            data = self.get_stock_data(symbol)
            if data:
                results.append(data)
        return results

    def get_company_info(self, symbol: str) -> Optional[Dict]:
        """
        Get detailed company information.

        Args:
            symbol: Stock ticker symbol

        Returns:
            Dictionary with company info or None if error
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            return {
                'symbol': symbol,
                'name': info.get('longName', symbol),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                'website': info.get('website', ''),
                'description': info.get('longBusinessSummary', ''),
                'employees': info.get('fullTimeEmployees', None),
                'city': info.get('city', ''),
                'state': info.get('state', ''),
                'country': info.get('country', ''),
                'market_cap': info.get('marketCap', 0),
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error fetching company info for {symbol}: {str(e)}")
            return None

    def get_historical_data(self, symbol: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """
        Get historical stock data.

        Args:
            symbol: Stock ticker symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            DataFrame with historical data or None if error
        """
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(start=start_date, end=end_date)
            return hist

        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {str(e)}")
            return None


if __name__ == "__main__":
    # Test the collector
    logging.basicConfig(level=logging.INFO)
    collector = YahooFinanceCollector()

    print("Testing Yahoo Finance Collector...")
    data = collector.get_stock_data("AAPL")
    if data:
        print(f"\nApple Stock Data:")
        for key, value in data.items():
            print(f"  {key}: {value}")

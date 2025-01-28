import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import logging
from typing import Dict, Any, Optional
import requests
from bs4 import BeautifulSoup

class DataCollector:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def collect_data(self, ticker: str) -> Dict[str, Any]:
        """Collect all data for a ticker"""
        try:
            self.logger.info(f"Fetching stock data for {ticker}")
            stock_data = self._get_stock_data(ticker)
            
            self.logger.info(f"Fetching options data for {ticker}")
            options_data = self._get_options_data(ticker)
            
            self.logger.info(f"Fetching news for {ticker}")
            news_data = self._get_news_data(ticker)
            
            return {
                'stock_data': stock_data,
                'options_data': options_data,
                'news_data': news_data,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error collecting data for {ticker}: {str(e)}")
            return None

    def _get_stock_data(self, ticker: str, period: str = '1y') -> pd.DataFrame:
        """Get historical stock data"""
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period=period)
            
            if df.empty:
                raise ValueError(f"No stock data found for {ticker}")
                
            return df
            
        except Exception as e:
            self.logger.error(f"Error fetching stock data: {str(e)}")
            return pd.DataFrame()

    def _get_options_data(self, ticker: str) -> Dict[str, pd.DataFrame]:
        """Get options chain data"""
        try:
            stock = yf.Ticker(ticker)
            
            # Get all available expiration dates
            expirations = stock.options
            
            if not expirations:
                return {}
                
            # Get options for the next few expiration dates
            calls_list = []
            puts_list = []
            
            for date in expirations[:3]:  # Look at next 3 expiration dates
                try:
                    chain = stock.option_chain(date)
                    
                    # Add expiration date to the dataframes
                    calls = chain.calls.copy()
                    calls['expirationDate'] = date
                    
                    puts = chain.puts.copy()
                    puts['expirationDate'] = date
                    
                    calls_list.append(calls)
                    puts_list.append(puts)
                    
                except Exception as e:
                    self.logger.warning(f"Error fetching options for {date}: {str(e)}")
                    continue
                    
            # Combine all options data
            if calls_list and puts_list:
                return {
                    'calls': pd.concat(calls_list, ignore_index=True),
                    'puts': pd.concat(puts_list, ignore_index=True)
                }
            return {}
            
        except Exception as e:
            self.logger.error(f"Error fetching options data: {str(e)}")
            return {}

    def _get_news_data(self, ticker: str) -> list:
        """Get recent news articles"""
        try:
            stock = yf.Ticker(ticker)
            news = stock.news
            
            # Process and filter news
            processed_news = []
            for article in news[:10]:  # Get last 10 news items
                processed_news.append({
                    'title': article.get('title', ''),
                    'link': article.get('link', ''),
                    'publisher': article.get('publisher', ''),
                    'published': datetime.fromtimestamp(article.get('providerPublishTime', 0)).isoformat(),
                    'type': article.get('type', ''),
                    'sentiment': self._analyze_news_sentiment(article.get('title', ''))
                })
                
            return processed_news
            
        except Exception as e:
            self.logger.error(f"Error fetching news data: {str(e)}")
            return []

    def _analyze_news_sentiment(self, text: str) -> str:
        """Simple sentiment analysis for news titles"""
        try:
            # List of positive and negative words
            positive_words = {'up', 'rise', 'gain', 'positive', 'growth', 'boost', 'surge'}
            negative_words = {'down', 'fall', 'drop', 'negative', 'decline', 'loss', 'plunge'}
            
            text = text.lower()
            pos_count = sum(1 for word in positive_words if word in text)
            neg_count = sum(1 for word in negative_words if word in text)
            
            if pos_count > neg_count:
                return 'positive'
            elif neg_count > pos_count:
                return 'negative'
            return 'neutral'
            
        except Exception as e:
            self.logger.error(f"Error analyzing news sentiment: {str(e)}")
            return 'neutral'

    def get_stock_data(self, ticker: str, period: str = "1mo", interval: str = "1d") -> Optional[pd.DataFrame]:
        """Fetch historical stock data"""
        try:
            # Get stock data from Yahoo Finance
            stock = yf.Ticker(ticker)
            df = stock.history(period=period, interval=interval)
            
            if df.empty:
                self.logger.error(f"No data received for {ticker}")
                return None
                
            # Ensure required columns exist
            required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            if not all(col in df.columns for col in required_columns):
                self.logger.error(f"Missing required columns for {ticker}")
                return None
                
            # Reset index to make date a column
            df = df.reset_index()
            df['Date'] = pd.to_datetime(df['Date'])
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error fetching stock data for {ticker}: {str(e)}")
            return None

    def get_options_data(self, ticker: str) -> Dict[str, Any]:
        """Fetch options data"""
        try:
            stock = yf.Ticker(ticker)
            # Get options expiration dates
            expirations = stock.options
            
            if not expirations:
                return {'error': 'No options data available'}

            # Get options for the nearest expiration date
            nearest_expiry = expirations[0]
            opt = stock.option_chain(nearest_expiry)
            
            return {
                'calls': opt.calls.to_dict('records'),
                'puts': opt.puts.to_dict('records'),
                'expiry': nearest_expiry,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error fetching options data for {ticker}: {str(e)}")
            return {'error': str(e)}

    def get_news(self, ticker: str) -> Dict[str, Any]:
        """Fetch recent news"""
        try:
            stock = yf.Ticker(ticker)
            news = stock.news
            
            return {
                'news': news if news else [],
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error fetching news for {ticker}: {str(e)}")
            return {'error': str(e)} 
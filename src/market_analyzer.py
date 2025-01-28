import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import yfinance as yf

# Update to use relative imports
from .data_collector import DataCollector
from .technical_analysis import TechnicalAnalysis

class MarketAnalyzer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.data_collector = DataCollector()
        self.technical_analyzer = TechnicalAnalysis()
        
    def analyze_market_conditions(self) -> Dict[str, Any]:
        """Analyze overall market conditions"""
        try:
            # Get market data (using SPY as proxy)
            market_data = self.data_collector.get_historical_data('SPY')
            
            # Technical analysis
            technical_indicators = self.technical_analyzer.calculate_indicators(market_data)
            
            # Market trend analysis
            trend = self._analyze_trend(market_data)
            
            # Volatility analysis
            volatility = self._analyze_volatility(market_data)
            
            return {
                'trend': trend,
                'volatility': volatility,
                'technical_indicators': technical_indicators,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing market conditions: {str(e)}")
            return None
            
    def calculate_atr(self, data: pd.DataFrame, period: int = 14) -> float:
        """Calculate Average True Range"""
        try:
            high = data['high']
            low = data['low']
            close = data['close']
            
            tr1 = abs(high - low)
            tr2 = abs(high - close.shift())
            tr3 = abs(low - close.shift())
            
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = tr.rolling(window=period).mean().iloc[-1]
            
            return float(atr)
            
        except Exception as e:
            self.logger.error(f"Error calculating ATR: {str(e)}")
            return 0.0
            
    def _analyze_trend(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze market trend"""
        try:
            # Calculate moving averages
            sma_20 = data['close'].rolling(window=20).mean()
            sma_50 = data['close'].rolling(window=50).mean()
            sma_200 = data['close'].rolling(window=200).mean()
            
            current_price = data['close'].iloc[-1]
            
            trend = {
                'short_term': 'bullish' if current_price > sma_20.iloc[-1] else 'bearish',
                'medium_term': 'bullish' if current_price > sma_50.iloc[-1] else 'bearish',
                'long_term': 'bullish' if current_price > sma_200.iloc[-1] else 'bearish'
            }
            
            return trend
            
        except Exception as e:
            self.logger.error(f"Error analyzing trend: {str(e)}")
            return {}
            
    def _analyze_volatility(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze market volatility"""
        try:
            # Calculate daily returns
            returns = data['close'].pct_change()
            
            # Calculate volatility metrics
            volatility = {
                'daily_volatility': returns.std(),
                'annualized_volatility': returns.std() * np.sqrt(252),
                'max_drawdown': self._calculate_max_drawdown(data['close']),
                'atr': self.calculate_atr(data)
            }
            
            return volatility
            
        except Exception as e:
            self.logger.error(f"Error analyzing volatility: {str(e)}")
            return {}
            
    def _calculate_max_drawdown(self, prices: pd.Series) -> float:
        """Calculate maximum drawdown"""
        try:
            rolling_max = prices.expanding().max()
            drawdowns = prices / rolling_max - 1.0
            max_drawdown = drawdowns.min()
            
            return float(max_drawdown)
            
        except Exception as e:
            self.logger.error(f"Error calculating max drawdown: {str(e)}")
            return 0.0

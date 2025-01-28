import pandas as pd
import numpy as np
import talib
from dataclasses import dataclass
from typing import Dict, Any, List, Tuple, Optional
import logging
from datetime import datetime

@dataclass
class TechnicalIndicators:
    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.calculate_all_indicators()
    
    def calculate_all_indicators(self):
        """Calculate all technical indicators"""
        # Trend Indicators
        self.calculate_moving_averages()
        self.calculate_macd()
        
        # Momentum Indicators
        self.calculate_rsi()
        self.calculate_stochastic()
        
        # Volatility Indicators
        self.calculate_bollinger_bands()
        
    def calculate_moving_averages(self):
        """Calculate various moving averages"""
        self.data['SMA_20'] = self.data['Close'].rolling(window=20).mean()
        self.data['SMA_50'] = self.data['Close'].rolling(window=50).mean()
        self.data['EMA_20'] = self.data['Close'].ewm(span=20, adjust=False).mean()
        self.data['EMA_50'] = self.data['Close'].ewm(span=50, adjust=False).mean()
    
    def calculate_macd(self):
        """Calculate MACD indicator"""
        exp1 = self.data['Close'].ewm(span=12, adjust=False).mean()
        exp2 = self.data['Close'].ewm(span=26, adjust=False).mean()
        self.data['MACD'] = exp1 - exp2
        self.data['MACD_signal'] = self.data['MACD'].ewm(span=9, adjust=False).mean()
        self.data['MACD_hist'] = self.data['MACD'] - self.data['MACD_signal']
    
    def calculate_rsi(self, periods=14):
        """Calculate RSI indicator"""
        delta = self.data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=periods).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=periods).mean()
        rs = gain / loss
        self.data['RSI'] = 100 - (100 / (1 + rs))
    
    def calculate_bollinger_bands(self, window=20, num_std=2):
        """Calculate Bollinger Bands"""
        self.data['BB_middle'] = self.data['Close'].rolling(window=window).mean()
        std = self.data['Close'].rolling(window=window).std()
        self.data['BB_upper'] = self.data['BB_middle'] + (std * num_std)
        self.data['BB_lower'] = self.data['BB_middle'] - (std * num_std)
    
    def calculate_stochastic(self, window=14):
        """Calculate Stochastic Oscillator"""
        low_min = self.data['Low'].rolling(window=window).min()
        high_max = self.data['High'].rolling(window=window).max()
        self.data['STOCH_K'] = 100 * (self.data['Close'] - low_min) / (high_max - low_min)
        self.data['STOCH_D'] = self.data['STOCH_K'].rolling(window=3).mean()
    
    def get_signals(self) -> Dict[str, Any]:
        """Generate trading signals based on technical indicators"""
        latest = self.data.iloc[-1]
        
        signals = {
            'trend': {
                'sma_20_50_cross': 'BULLISH' if latest['SMA_20'] > latest['SMA_50'] else 'BEARISH',
                'macd_signal': 'BULLISH' if latest['MACD'] > latest['MACD_signal'] else 'BEARISH'
            },
            'momentum': {
                'rsi': {
                    'value': latest['RSI'],
                    'signal': 'OVERSOLD' if latest['RSI'] < 30 else 'OVERBOUGHT' if latest['RSI'] > 70 else 'NEUTRAL'
                },
                'stochastic': {
                    'k': latest['STOCH_K'],
                    'd': latest['STOCH_D'],
                    'signal': 'OVERSOLD' if latest['STOCH_K'] < 20 else 'OVERBOUGHT' if latest['STOCH_K'] > 80 else 'NEUTRAL'
                }
            },
            'volatility': {
                'bollinger': {
                    'position': 'UPPER' if latest['Close'] > latest['BB_upper'] else 'LOWER' if latest['Close'] < latest['BB_lower'] else 'MIDDLE',
                    'bandwidth': (latest['BB_upper'] - latest['BB_lower']) / latest['BB_middle']
                }
            }
        }
        
        return signals 

class TechnicalAnalysis:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def _prepare_data(self, data: pd.DataFrame) -> np.ndarray:
        """Convert data to numpy array of doubles"""
        try:
            return data.astype(float).values
        except Exception as e:
            self.logger.error(f"Error converting data: {str(e)}")
            return np.array([])

    def validate_data(self, data: pd.DataFrame, required_columns: List[str]) -> bool:
        """Validate input data"""
        try:
            if data is None or not isinstance(data, pd.DataFrame) or data.empty:
                raise ValueError("Invalid or empty DataFrame")
            
            missing_columns = [col for col in required_columns if col not in data.columns]
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")
                
            return True
            
        except Exception as e:
            self.logger.error(f"Data validation error: {str(e)}")
            return False

    def calculate_sma(self, data: pd.DataFrame, period: int = 20) -> pd.Series:
        """Calculate Simple Moving Average"""
        try:
            return data['Close'].rolling(window=period).mean()
        except Exception as e:
            self.logger.error(f"Error calculating SMA: {str(e)}")
            return pd.Series(index=data.index)

    def calculate_rsi(self, data: pd.DataFrame, period: int = 14) -> float:
        """Calculate RSI"""
        try:
            if len(data) < period:
                return 50.0
            
            prices = self._prepare_data(data['Close'])
            if len(prices) == 0:
                return 50.0
                
            rsi = talib.RSI(prices, timeperiod=period)
            return float(rsi[-1]) if not np.isnan(rsi[-1]) else 50.0
            
        except Exception as e:
            self.logger.error(f"Error calculating RSI: {str(e)}")
            return 50.0

    def calculate_macd(self, data: pd.DataFrame) -> float:
        """Calculate MACD"""
        try:
            prices = self._prepare_data(data['Close'])
            if len(prices) == 0:
                return 0.0
                
            macd, signal, _ = talib.MACD(
                prices,
                fastperiod=12,
                slowperiod=26,
                signalperiod=9
            )
            return float(macd[-1] - signal[-1]) if not np.isnan(macd[-1]) else 0.0
            
        except Exception as e:
            self.logger.error(f"Error calculating MACD: {str(e)}")
            return 0.0

    def calculate_bollinger_bands(self, data: pd.DataFrame, period: int = 20) -> tuple:
        """Calculate Bollinger Bands"""
        try:
            prices = self._prepare_data(data['Close'])
            if len(prices) == 0:
                return data['Close'].iloc[-1], data['Close'].iloc[-1]
                
            upper, middle, lower = talib.BBANDS(
                prices,
                timeperiod=period
            )
            return (
                float(upper[-1]) if not np.isnan(upper[-1]) else prices[-1],
                float(lower[-1]) if not np.isnan(lower[-1]) else prices[-1]
            )
            
        except Exception as e:
            self.logger.error(f"Error calculating Bollinger Bands: {str(e)}")
            return data['Close'].iloc[-1], data['Close'].iloc[-1]

    def calculate_volume_profile(self, data: pd.DataFrame) -> Dict[str, float]:
        """Analyze volume profile"""
        try:
            avg_volume = data['Volume'].mean()
            volume_trend = (data['Volume'].iloc[-5:].mean() / avg_volume) - 1
            price_volume_correlation = data['Close'].pct_change().corr(data['Volume'].pct_change())
            
            return {
                'avg_volume': avg_volume,
                'volume_trend': volume_trend,
                'price_volume_corr': price_volume_correlation
            }
        except Exception as e:
            self.logger.error(f"Error calculating volume profile: {str(e)}")
            return {'avg_volume': 0, 'volume_trend': 0, 'price_volume_corr': 0}

    def detect_trend(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Detect price trends"""
        try:
            # Calculate short and long term trends
            short_sma = self.calculate_sma(data, 10)
            long_sma = self.calculate_sma(data, 50)
            
            # Calculate trend strength
            adr = (data['High'] - data['Low']).mean() / data['Close'].mean() * 100
            trend_strength = abs(short_sma.iloc[-1] - long_sma.iloc[-1]) / data['Close'].mean() * 100
            
            # Determine trend direction
            if short_sma.iloc[-1] > long_sma.iloc[-1]:
                trend = 'uptrend' if trend_strength > 1 else 'weak_uptrend'
            else:
                trend = 'downtrend' if trend_strength > 1 else 'weak_downtrend'
                
            return {
                'trend': trend,
                'strength': trend_strength,
                'adr': adr
            }
        except Exception as e:
            self.logger.error(f"Error detecting trend: {str(e)}")
            return {'trend': 'neutral', 'strength': 0, 'adr': 0}

    def generate_signals(self, indicators: Dict[str, Any]) -> Dict[str, Any]:
        """Generate trading signals based on all indicators"""
        try:
            signals = []
            confidence = 0
            
            # RSI signals
            if indicators['rsi'] < 30:
                signals.append('oversold')
                confidence += 0.2
            elif indicators['rsi'] > 70:
                signals.append('overbought')
                confidence -= 0.2
                
            # MACD signals
            if indicators['macd_signal'] > 0:
                signals.append('bullish_momentum')
                confidence += 0.15
            elif indicators['macd_signal'] < 0:
                signals.append('bearish_momentum')
                confidence -= 0.15
                
            # Volume signals
            if indicators['volume_profile']['volume_trend'] > 0.1:
                signals.append('increasing_volume')
                confidence += 0.1
                
            # Trend signals
            if indicators['trend']['trend'] in ['uptrend', 'weak_uptrend']:
                signals.append('uptrend')
                confidence += 0.25 if indicators['trend']['trend'] == 'uptrend' else 0.1
            elif indicators['trend']['trend'] in ['downtrend', 'weak_downtrend']:
                signals.append('downtrend')
                confidence -= 0.25 if indicators['trend']['trend'] == 'downtrend' else 0.1
                
            return {
                'signals': signals,
                'confidence': max(min(confidence, 1.0), -1.0),  # Bound between -1 and 1
                'strength': abs(confidence)
            }
        except Exception as e:
            self.logger.error(f"Error generating signals: {str(e)}")
            return {'signals': [], 'confidence': 0, 'strength': 0}

    def analyze(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Perform technical analysis"""
        try:
            if data is None or data.empty:
                raise ValueError("No data provided for analysis")

            # Ensure data types are correct
            data = data.copy()
            for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
                data[col] = pd.to_numeric(data[col], errors='coerce')

            # Calculate indicators
            rsi = self.calculate_rsi(data)
            macd = self.calculate_macd(data)
            upper_band, lower_band = self.calculate_bollinger_bands(data)
            
            # Calculate trend
            prices = self._prepare_data(data['Close'])
            sma_20 = talib.SMA(prices, timeperiod=20)
            sma_50 = talib.SMA(prices, timeperiod=50)
            trend = 'bullish' if sma_20[-1] > sma_50[-1] else 'bearish'
            
            # Volume analysis
            volumes = self._prepare_data(data['Volume'])
            volume_sma = talib.SMA(volumes, timeperiod=20)
            volume_trend = 'high' if volumes[-1] > volume_sma[-1] else 'low'
            
            return {
                'rsi': rsi,
                'macd_signal': macd,
                'bollinger_upper': float(upper_band),
                'bollinger_lower': float(lower_band),
                'trend': trend,
                'volume_trend': volume_trend,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error in technical analysis: {str(e)}")
            return {
                'rsi': 50.0,
                'macd_signal': 0.0,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            } 
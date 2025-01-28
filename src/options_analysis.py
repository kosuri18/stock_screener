import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging

@dataclass
class OptionsStrategy:
    strategy_type: str
    entry_price: float
    exit_price: float
    max_loss: float
    max_profit: float
    probability_profit: float
    risk_reward_ratio: float
    days_to_expiry: int
    implied_volatility: float

class OptionsAnalysis:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def calculate_put_call_ratio(self, options_data: Dict[str, pd.DataFrame]) -> float:
        """Calculate put/call ratio"""
        try:
            if not options_data or 'calls' not in options_data or 'puts' not in options_data:
                return 1.0  # Neutral ratio
                
            calls_volume = options_data['calls']['volume'].sum()
            puts_volume = options_data['puts']['volume'].sum()
            
            if calls_volume == 0:
                return 2.0  # Bearish signal
                
            return puts_volume / calls_volume
            
        except Exception as e:
            self.logger.error(f"Error calculating put/call ratio: {str(e)}")
            return 1.0

    def calculate_implied_volatility(self, options_data: Dict[str, pd.DataFrame]) -> float:
        """Calculate average implied volatility"""
        try:
            if not options_data:
                return 0.0
                
            all_options = pd.concat([
                options_data.get('calls', pd.DataFrame()),
                options_data.get('puts', pd.DataFrame())
            ])
            
            if 'impliedVolatility' in all_options.columns:
                return float(all_options['impliedVolatility'].mean())
            return 0.0
            
        except Exception as e:
            self.logger.error(f"Error calculating implied volatility: {str(e)}")
            return 0.0

    def analyze_options_flow(self, options_data: Dict[str, pd.DataFrame]) -> str:
        """Analyze options flow for sentiment"""
        try:
            if not options_data:
                return 'neutral'
                
            # Calculate put/call ratio
            pc_ratio = self.calculate_put_call_ratio(options_data)
            
            # Analyze large trades
            calls = options_data.get('calls', pd.DataFrame())
            puts = options_data.get('puts', pd.DataFrame())
            
            if not calls.empty and not puts.empty:
                # Look for large trades
                large_calls = calls[calls['volume'] > calls['volume'].mean() + calls['volume'].std()]
                large_puts = puts[puts['volume'] > puts['volume'].mean() + puts['volume'].std()]
                
                call_premium = (large_calls['volume'] * large_calls['lastPrice']).sum()
                put_premium = (large_puts['volume'] * large_puts['lastPrice']).sum()
                
                # Determine sentiment
                if pc_ratio < 0.7 and call_premium > put_premium:
                    return 'bullish'
                elif pc_ratio > 1.3 and put_premium > call_premium:
                    return 'bearish'
                    
            return 'neutral'
            
        except Exception as e:
            self.logger.error(f"Error analyzing options flow: {str(e)}")
            return 'neutral'

    def analyze(self, options_data: Optional[Dict[str, pd.DataFrame]]) -> Dict[str, Any]:
        """Perform options analysis"""
        try:
            if options_data is None:
                return {
                    'sentiment': 'neutral',
                    'iv_percentile': 0.0,
                    'put_call_ratio': 1.0,
                    'timestamp': datetime.now().isoformat()
                }

            # Calculate metrics
            put_call_ratio = self.calculate_put_call_ratio(options_data)
            implied_vol = self.calculate_implied_volatility(options_data)
            sentiment = self.analyze_options_flow(options_data)
            
            # Analyze near-term options
            near_term_options = self._filter_near_term_options(options_data)
            near_term_sentiment = self.analyze_options_flow(near_term_options)
            
            return {
                'sentiment': sentiment,
                'near_term_sentiment': near_term_sentiment,
                'iv_percentile': implied_vol,
                'put_call_ratio': put_call_ratio,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error in options analysis: {str(e)}")
            return {
                'sentiment': 'neutral',
                'iv_percentile': 0.0,
                'put_call_ratio': 1.0,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def _filter_near_term_options(self, options_data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """Filter options expiring within 30 days"""
        try:
            if not options_data:
                return {}
                
            near_term = datetime.now() + timedelta(days=30)
            
            filtered_data = {}
            for option_type in ['calls', 'puts']:
                if option_type in options_data:
                    df = options_data[option_type]
                    if 'expirationDate' in df.columns:
                        df['expirationDate'] = pd.to_datetime(df['expirationDate'])
                        filtered_data[option_type] = df[df['expirationDate'] <= near_term]
                        
            return filtered_data
            
        except Exception as e:
            self.logger.error(f"Error filtering near-term options: {str(e)}")
            return {}

    def analyze_options_chain(self, stock_data: pd.DataFrame, options_chain: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Analyze options chain and return relevant metrics"""
        try:
            self.calls = options_chain['calls']
            self.puts = options_chain['puts']
            self.current_price = stock_data['Close'].iloc[-1]
            self.volatility = stock_data['Close'].pct_change().std() * np.sqrt(252)  # Annualized volatility
            
            call_analysis = self._analyze_calls()
            put_analysis = self._analyze_puts()
            iv_skew = self._calculate_iv_skew()
            
            return {
                'call_analysis': call_analysis,
                'put_analysis': put_analysis,
                'iv_skew': iv_skew,
                'current_price': self.current_price,
                'historical_volatility': self.volatility
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _analyze_calls(self) -> Dict[str, Any]:
        """Analyze call options"""
        atm_calls = self.calls[
            (self.calls['strike'] >= self.current_price * 0.95) &
            (self.calls['strike'] <= self.current_price * 1.05)
        ]
        
        return {
            'avg_iv': atm_calls['impliedVolatility'].mean(),
            'avg_volume': atm_calls['volume'].mean(),
            'avg_open_interest': atm_calls['openInterest'].mean(),
            'most_active_strike': atm_calls.loc[atm_calls['volume'].idxmax(), 'strike']
            if not atm_calls.empty else None
        }
    
    def _analyze_puts(self) -> Dict[str, Any]:
        """Analyze put options"""
        atm_puts = self.puts[
            (self.puts['strike'] >= self.current_price * 0.95) &
            (self.puts['strike'] <= self.current_price * 1.05)
        ]
        
        return {
            'avg_iv': atm_puts['impliedVolatility'].mean(),
            'avg_volume': atm_puts['volume'].mean(),
            'avg_open_interest': atm_puts['openInterest'].mean(),
            'most_active_strike': atm_puts.loc[atm_puts['volume'].idxmax(), 'strike']
            if not atm_puts.empty else None
        }
    
    def _calculate_iv_skew(self) -> float:
        """Calculate implied volatility skew"""
        atm_call_iv = self.calls[
            (self.calls['strike'] >= self.current_price * 0.99) &
            (self.calls['strike'] <= self.current_price * 1.01)
        ]['impliedVolatility'].mean()
        
        otm_call_iv = self.calls[
            self.calls['strike'] > self.current_price * 1.05
        ]['impliedVolatility'].mean()
        
        return otm_call_iv - atm_call_iv if not np.isnan(otm_call_iv - atm_call_iv) else 0
    
    def suggest_strategies(self, 
                         technical_signals: Dict[str, Any], 
                         sentiment_score: float) -> List[OptionsStrategy]:
        """Suggest options strategies based on technical and sentiment analysis"""
        strategies = []
        
        # Bullish scenarios
        if (technical_signals['trend']['sma_20_50_cross'] == 'BULLISH' and 
            sentiment_score > 0.6):
            strategies.extend(self._get_bullish_strategies())
            
        # Bearish scenarios
        elif (technical_signals['trend']['sma_20_50_cross'] == 'BEARISH' and 
              sentiment_score < 0.4):
            strategies.extend(self._get_bearish_strategies())
            
        # Neutral scenarios
        else:
            strategies.extend(self._get_neutral_strategies())
            
        return strategies
    
    def _get_bullish_strategies(self) -> List[OptionsStrategy]:
        """Generate bullish options strategies"""
        strategies = []
        
        # Covered Call
        atm_call = self._find_atm_option(self.calls)
        if atm_call is not None:
            strategies.append(
                OptionsStrategy(
                    strategy_type="Covered Call",
                    entry_price=self.current_price,
                    exit_price=float(atm_call['strike']),
                    max_loss=self.current_price - float(atm_call['lastPrice']),
                    max_profit=float(atm_call['lastPrice']),
                    probability_profit=0.68,  # Approximate based on 1 standard deviation
                    risk_reward_ratio=float(atm_call['lastPrice']) / (self.current_price - float(atm_call['lastPrice'])),
                    days_to_expiry=30,  # Assuming 30-day options
                    implied_volatility=float(atm_call['impliedVolatility'])
                )
            )
            
        return strategies
    
    def _get_bearish_strategies(self) -> List[OptionsStrategy]:
        """Generate bearish options strategies"""
        strategies = []
        
        # Put Spread
        atm_put = self._find_atm_option(self.puts)
        if atm_put is not None:
            strategies.append(
                OptionsStrategy(
                    strategy_type="Put Spread",
                    entry_price=float(atm_put['strike']),
                    exit_price=float(atm_put['strike']) * 0.95,
                    max_loss=float(atm_put['lastPrice']),
                    max_profit=float(atm_put['strike']) * 0.05 - float(atm_put['lastPrice']),
                    probability_profit=0.45,
                    risk_reward_ratio=float(atm_put['lastPrice']) / (float(atm_put['strike']) * 0.05 - float(atm_put['lastPrice'])),
                    days_to_expiry=30,
                    implied_volatility=float(atm_put['impliedVolatility'])
                )
            )
            
        return strategies
    
    def _get_neutral_strategies(self) -> List[OptionsStrategy]:
        """Generate neutral options strategies"""
        strategies = []
        
        # Iron Condor
        atm_call = self._find_atm_option(self.calls)
        atm_put = self._find_atm_option(self.puts)
        
        if atm_call is not None and atm_put is not None:
            strategies.append(
                OptionsStrategy(
                    strategy_type="Iron Condor",
                    entry_price=self.current_price,
                    exit_price=self.current_price,
                    max_loss=float(atm_call['strike']) - float(atm_put['strike']),
                    max_profit=float(atm_call['lastPrice']) + float(atm_put['lastPrice']),
                    probability_profit=0.68,
                    risk_reward_ratio=(float(atm_call['strike']) - float(atm_put['strike'])) / 
                                    (float(atm_call['lastPrice']) + float(atm_put['lastPrice'])),
                    days_to_expiry=30,
                    implied_volatility=(float(atm_call['impliedVolatility']) + float(atm_put['impliedVolatility'])) / 2
                )
            )
            
        return strategies
    
    def _find_atm_option(self, chain: pd.DataFrame) -> Optional[pd.Series]:
        """Find at-the-money option"""
        if chain.empty:
            return None
            
        chain['strike_diff'] = abs(chain['strike'] - self.current_price)
        atm_idx = chain['strike_diff'].idxmin()
        return chain.loc[atm_idx] if atm_idx is not None else None 
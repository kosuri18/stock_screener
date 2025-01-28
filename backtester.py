from typing import Dict, Any
import pandas as pd
import numpy as np
import logging
from datetime import datetime

class Backtester:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def calculate_returns(self, data: pd.DataFrame) -> float:
        """Calculate historical returns"""
        try:
            returns = data['Close'].pct_change().dropna()
            return float(returns.mean() * 252)  # Annualized return
        except Exception as e:
            self.logger.error(f"Error calculating returns: {str(e)}")
            return 0.0

    def calculate_volatility(self, data: pd.DataFrame) -> float:
        """Calculate historical volatility"""
        try:
            returns = data['Close'].pct_change().dropna()
            return float(returns.std() * np.sqrt(252))  # Annualized volatility
        except Exception as e:
            self.logger.error(f"Error calculating volatility: {str(e)}")
            return 1.0

    def calculate_sharpe_ratio(self, returns: float, volatility: float, risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe ratio"""
        try:
            if volatility == 0:
                return 0.0
            return (returns - risk_free_rate) / volatility
        except Exception as e:
            self.logger.error(f"Error calculating Sharpe ratio: {str(e)}")
            return 0.0

    def run_backtest(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Run backtest analysis"""
        try:
            if data is None or data.empty:
                raise ValueError("No data provided for backtest")

            # Calculate metrics
            returns = self.calculate_returns(data)
            volatility = self.calculate_volatility(data)
            sharpe_ratio = self.calculate_sharpe_ratio(returns, volatility)
            
            # Calculate max drawdown
            cumulative_returns = (1 + data['Close'].pct_change()).cumprod()
            rolling_max = cumulative_returns.expanding().max()
            drawdowns = cumulative_returns / rolling_max - 1
            max_drawdown = float(drawdowns.min())
            
            return {
                'returns': returns,
                'volatility': volatility,
                'sharpe_ratio': sharpe_ratio,
                'max_drawdown': max_drawdown,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error in backtest: {str(e)}")
            return {
                'returns': 0.0,
                'volatility': 1.0,
                'sharpe_ratio': 0.0,
                'max_drawdown': 0.0,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            } 
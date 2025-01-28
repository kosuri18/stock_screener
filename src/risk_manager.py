import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import yfinance as yf

# Update to use relative imports
from .market_analyzer import MarketAnalyzer

class RiskManager:
    def __init__(self, max_position_size: float = 0.1, max_portfolio_risk: float = 0.02):
        self.logger = logging.getLogger(__name__)
        self.market_analyzer = MarketAnalyzer()
        self.max_position_size = max_position_size
        self.max_portfolio_risk = max_portfolio_risk
        
    def validate_trade(self, signal: Dict[str, Any], portfolio: Dict[str, Any]) -> bool:
        """Validate if a trade meets risk management criteria"""
        try:
            # Check if we have enough buying power
            if not self._check_buying_power(signal, portfolio):
                return False
                
            # Check if position size is within limits
            if not self._check_position_size(signal, portfolio):
                return False
                
            # Check if total portfolio risk is acceptable
            if not self._check_portfolio_risk(signal, portfolio):
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating trade: {str(e)}")
            return False
            
    def calculate_position_size(self, signal: Dict[str, Any], portfolio: Dict[str, Any], stock_data: pd.DataFrame) -> float:
        """Calculate appropriate position size based on risk parameters"""
        try:
            portfolio_value = float(portfolio.get('portfolio_value', 0))
            if portfolio_value <= 0:
                return 0
                
            # Get current price
            current_price = stock_data['close'].iloc[-1]
            if current_price <= 0:
                return 0
                
            # Calculate maximum position value based on portfolio size
            max_position_value = portfolio_value * self.max_position_size
            
            # Calculate position size based on maximum position value
            position_size = max_position_value / current_price
            
            return position_size
            
        except Exception as e:
            self.logger.error(f"Error calculating position size: {str(e)}")
            return 0
            
    def _check_buying_power(self, signal: Dict[str, Any], portfolio: Dict[str, Any]) -> bool:
        """Check if we have enough buying power for the trade"""
        try:
            buying_power = float(portfolio.get('buying_power', 0))
            estimated_cost = signal.get('price', 0) * signal.get('quantity', 0)
            
            return buying_power >= estimated_cost
            
        except Exception as e:
            self.logger.error(f"Error checking buying power: {str(e)}")
            return False
            
    def _check_position_size(self, signal: Dict[str, Any], portfolio: Dict[str, Any]) -> bool:
        """Check if position size is within acceptable limits"""
        try:
            portfolio_value = float(portfolio.get('portfolio_value', 0))
            position_value = signal.get('price', 0) * signal.get('quantity', 0)
            
            return position_value <= (portfolio_value * self.max_position_size)
            
        except Exception as e:
            self.logger.error(f"Error checking position size: {str(e)}")
            return False
            
    def _check_portfolio_risk(self, signal: Dict[str, Any], portfolio: Dict[str, Any]) -> bool:
        """Check if total portfolio risk is within acceptable limits"""
        try:
            current_risk = self._calculate_current_portfolio_risk(portfolio)
            new_risk = self._calculate_trade_risk(signal)
            
            return (current_risk + new_risk) <= self.max_portfolio_risk
            
        except Exception as e:
            self.logger.error(f"Error checking portfolio risk: {str(e)}")
            return False
            
    def _calculate_current_portfolio_risk(self, portfolio: Dict[str, Any]) -> float:
        """Calculate current portfolio risk from existing positions"""
        try:
            positions = portfolio.get('positions', [])
            total_risk = 0.0
            
            for position in positions:
                total_risk += self._calculate_position_risk(position)
                
            return total_risk
            
        except Exception as e:
            self.logger.error(f"Error calculating portfolio risk: {str(e)}")
            return 0.0
            
    def _calculate_trade_risk(self, signal: Dict[str, Any]) -> float:
        """Calculate risk for a specific trade"""
        try:
            price = signal.get('price', 0)
            stop_loss = signal.get('stop_loss', 0)
            quantity = signal.get('quantity', 0)
            
            if price <= 0 or stop_loss <= 0 or quantity <= 0:
                return 0.0
                
            risk_per_share = abs(price - stop_loss)
            total_risk = risk_per_share * quantity
            
            return total_risk
            
        except Exception as e:
            self.logger.error(f"Error calculating trade risk: {str(e)}")
            return 0.0
            
    def _calculate_position_risk(self, position: Dict[str, Any]) -> float:
        """Calculate risk for an existing position"""
        try:
            current_price = position.get('current_price', 0)
            stop_loss = position.get('stop_loss', 0)
            quantity = position.get('quantity', 0)
            
            if current_price <= 0 or stop_loss <= 0 or quantity <= 0:
                return 0.0
                
            risk_per_share = abs(current_price - stop_loss)
            total_risk = risk_per_share * quantity
            
            return total_risk
            
        except Exception as e:
            self.logger.error(f"Error calculating position risk: {str(e)}")
            return 0.0

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import os
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi
import random

class BrokerIntegration:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Get Alpaca API credentials from environment variables
        self.api_key = os.getenv('ALPACA_API_KEY')
        self.api_secret = os.getenv('ALPACA_SECRET_KEY')
        self.base_url = os.getenv('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets')
        
        # Add verbose logging
        self.logger.info("Checking Alpaca API credentials...")
        self.logger.info(f"Base URL: {self.base_url}")
        self.logger.info(f"API Key present: {bool(self.api_key)}")
        self.logger.info(f"Secret Key present: {bool(self.api_secret)}")
        
        if not self.api_key or not self.api_secret:
            self.logger.warning("Missing Alpaca API credentials. Running in simulation mode.")
            self.simulation_mode = True
            self.api = None
        else:
            try:
                self.simulation_mode = False
                self.api = tradeapi.REST(
                    self.api_key,
                    self.api_secret,
                    base_url=self.base_url,
                    api_version='v2'
                )
                # Test API connection
                account = self.api.get_account()
                self.logger.info(f"Connected to Alpaca API. Account status: {account.status}")
            except Exception as e:
                self.logger.error(f"Failed to connect to Alpaca API: {str(e)}")
                self.simulation_mode = True
                self.api = None

    def get_portfolio(self) -> Dict[str, Any]:
        """Get current portfolio from Alpaca"""
        try:
            if self.simulation_mode:
                return self._simulate_portfolio()
                
            # Get account information
            account = self.api.get_account()
            
            # Get positions
            positions = self.api.list_positions()
            positions_dict = {}
            
            for position in positions:
                positions_dict[position.symbol] = {
                    'quantity': float(position.qty),
                    'market_value': float(position.market_value),
                    'avg_entry_price': float(position.avg_entry_price),
                    'current_price': float(position.current_price),
                    'unrealized_pl': float(position.unrealized_pl)
                }
            
            return {
                'portfolio_value': float(account.portfolio_value),
                'cash': float(account.cash),
                'positions': positions_dict
            }
            
        except Exception as e:
            self.logger.error(f"Error getting portfolio: {str(e)}")
            return {'portfolio_value': 0, 'cash': 0, 'positions': {}}

    def execute_trade(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """Execute trade through Alpaca API"""
        try:
            if self.simulation_mode:
                return self._simulate_trade(signal)
                
            ticker = signal.get('ticker')
            action = signal.get('action', '').lower()
            quantity = signal.get('quantity', 0)
            
            if not all([ticker, action, quantity]):
                self.logger.error("Missing required trade parameters")
                return {'status': 'error', 'message': 'Missing parameters'}
            
            # Convert buy/sell to Alpaca's side format
            side = 'buy' if action == 'buy' else 'sell'
            
            # Submit order to Alpaca
            try:
                order = self.api.submit_order(
                    symbol=ticker,
                    qty=quantity,
                    side=side,
                    type='market',
                    time_in_force='day'
                )
                
                self.logger.info(f"Order submitted to Alpaca: {order.id}")
                
                # Wait for order to fill
                filled_order = self.api.get_order(order.id)
                while filled_order.status not in ['filled', 'canceled', 'expired']:
                    filled_order = self.api.get_order(order.id)
                
                if filled_order.status == 'filled':
                    return {
                        'status': 'filled',
                        'ticker': ticker,
                        'action': action,
                        'quantity': quantity,
                        'price': float(filled_order.filled_avg_price),
                        'timestamp': datetime.now().isoformat()
                    }
                else:
                    self.logger.error(f"Order failed: {filled_order.status}")
                    return {'status': 'error', 'message': f"Order {filled_order.status}"}
                    
            except Exception as e:
                self.logger.error(f"Alpaca API error: {str(e)}")
                return {'status': 'error', 'message': str(e)}
                
        except Exception as e:
            self.logger.error(f"Error executing trade: {str(e)}")
            return {'status': 'error', 'message': str(e)}

    def get_position(self, ticker: str) -> Dict[str, Any]:
        """Get current position for a ticker"""
        try:
            position = self.api.get_position(ticker)
            return {
                'symbol': position.symbol,
                'qty': int(position.qty),
                'market_value': float(position.market_value),
                'current_price': float(position.current_price),
                'avg_entry_price': float(position.avg_entry_price),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error getting position for {ticker}: {str(e)}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def _simulate_trade(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate trade execution for testing"""
        return {
            'status': 'filled',
            'ticker': signal.get('ticker'),
            'action': signal.get('action'),
            'quantity': signal.get('quantity'),
            'price': signal.get('price', 100.0),
            'timestamp': datetime.now().isoformat()
        }

    def _simulate_portfolio(self) -> Dict[str, Any]:
        """Simulate portfolio for testing"""
        return {
            'portfolio_value': 100000.0,
            'cash': 100000.0,
            'positions': {}
        } 
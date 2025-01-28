import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import time

# Update imports to use relative imports
from .broker_integration import BrokerIntegration
from .pipeline import Pipeline
from .risk_manager import RiskManager

class TradingBot:
    def __init__(self, tickers: List[str]):
        self.logger = logging.getLogger(__name__)
        self.tickers = tickers
        self.broker = BrokerIntegration()
        self.pipeline = Pipeline()
        self.risk_manager = RiskManager()
        
    def run(self, test_mode: bool = False):
        """Run the trading bot"""
        self.logger.info("Starting trading bot...")
        self.logger.info(f"Current portfolio value: ${self.get_portfolio_value():,.2f}")
        
        try:
            while True:
                for ticker in self.tickers:
                    self.logger.info(f"Processing {ticker}")
                    self._process_ticker(ticker)
                
                if test_mode:
                    self.logger.info("Test mode - completing single run")
                    break
                    
                time.sleep(300)  # 5-minute delay between checks
                
        except Exception as e:
            self.logger.error(f"Error in trading bot: {str(e)}")
            
    def _process_ticker(self, ticker: str):
        """Process a single ticker"""
        try:
            # Get current portfolio
            portfolio = self.broker.get_portfolio()
            
            # Get trading signal from pipeline
            signal = self.pipeline.process(ticker)
            
            if not signal:
                self.logger.info(f"No trade signal for {ticker}")
                return
            
            # Validate trade with risk manager
            if not self.risk_manager.validate_trade(signal, portfolio):
                self.logger.info(f"Trade rejected by risk manager for {ticker}")
                return
                
            # Calculate position size
            position_size = self.risk_manager.calculate_position_size(
                signal,
                portfolio,
                self.pipeline.get_stock_data(ticker)
            )
            
            if position_size <= 0:
                self.logger.info(f"Invalid position size for {ticker}")
                return
                
            # Execute trade
            signal['quantity'] = position_size
            result = self.broker.execute_trade(signal)
            
            self.logger.info(f"Trade executed for {ticker}: {result}")
            self.logger.info(f"Current portfolio value: ${self.get_portfolio_value():,.2f}")
            
        except Exception as e:
            self.logger.error(f"Error processing {ticker}: {str(e)}")
            
    def get_portfolio_value(self) -> float:
        """Get current portfolio value"""
        try:
            portfolio = self.broker.get_portfolio()
            return float(portfolio.get('portfolio_value', 0))
        except Exception as e:
            self.logger.error(f"Error getting portfolio value: {str(e)}")
            return 0.0

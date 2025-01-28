#!/usr/bin/env python3

import os
import sys
from dotenv import load_dotenv
import logging
from pathlib import Path

# Add the current directory to Python path
current_dir = str(Path(__file__).parent.absolute())
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Load environment variables at the very start
load_dotenv(verbose=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Verify environment variables are loaded
alpaca_key = os.getenv('ALPACA_API_KEY')
alpaca_secret = os.getenv('ALPACA_SECRET_KEY')
alpaca_url = os.getenv('ALPACA_BASE_URL')

print("Environment variables loaded:")
print(f"API Key present: {bool(alpaca_key)}")
print(f"Secret Key present: {bool(alpaca_secret)}")
print(f"Base URL: {alpaca_url}")

# Import from src directory (using absolute imports)
from src.trading_bot import TradingBot

def main():
    # Initialize logging
    root_logger = logging.getLogger()
    root_logger.info("Starting trading bot...")

    # Define your tickers
    tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META']
    root_logger.info(f"Monitoring tickers: {', '.join(tickers)}")

    # Set check interval (in seconds)
    check_interval = 300  # 5 minutes
    root_logger.info(f"Check interval: {check_interval} seconds")

    # Initialize and run the trading bot
    bot = TradingBot(tickers=tickers)
    bot.run(test_mode=True)  # Set to False for continuous operation

if __name__ == "__main__":
    main()

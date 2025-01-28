import alpaca_trade_api as tradeapi
from dotenv import load_dotenv
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_alpaca_connection():
    # Load environment variables
    load_dotenv(verbose=True)
    
    # Get and log credentials (safely)
    api_key = os.getenv('ALPACA_API_KEY')
    secret_key = os.getenv('ALPACA_SECRET_KEY')
    base_url = os.getenv('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets')
    
    logger.info(f"API Key present: {bool(api_key)}")
    logger.info(f"Secret Key present: {bool(secret_key)}")
    logger.info(f"Base URL: {base_url}")
    
    if not api_key or not secret_key:
        logger.error("Missing API credentials!")
        return False
        
    try:
        # Initialize API connection
        api = tradeapi.REST(
            api_key,
            secret_key,
            base_url=base_url,
            api_version='v2'
        )
        
        # Test connection by getting account info
        account = api.get_account()
        logger.info(f"Connected successfully!")
        logger.info(f"Account status: {account.status}")
        logger.info(f"Cash balance: ${float(account.cash)}")
        logger.info(f"Portfolio value: ${float(account.portfolio_value)}")
        
        # Test getting positions
        positions = api.list_positions()
        logger.info(f"Current positions: {len(positions)}")
        for position in positions:
            logger.info(f"- {position.symbol}: {position.qty} shares at ${float(position.avg_entry_price)}")
            
        return True
        
    except Exception as e:
        logger.error(f"Connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_alpaca_connection()
    if not success:
        logger.error("Failed to connect to Alpaca API")
        logger.info("Please check your .env file contains:")
        logger.info("ALPACA_API_KEY=your_api_key_here")
        logger.info("ALPACA_SECRET_KEY=your_secret_key_here")
        logger.info("ALPACA_BASE_URL=https://paper-api.alpaca.markets") 
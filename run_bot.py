import logging
from trading_bot import TradingBot
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    # Load environment variables
    load_dotenv()
    
    # Define your stock tickers
    tickers = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META',
        'NVDA', 'TSLA', 'JPM', 'V', 'WMT',
        'DIS', 'NFLX', 'PYPL', 'ADBE', 'INTC'
    ]
    
    # Create trading bot instance
    # check_interval is in seconds (300 = 5 minutes)
    bot = TradingBot(
        tickers=tickers,
        check_interval=300,  # Check every 5 minutes
        test_mode=False      # Set to True for testing
    )
    
    try:
        # Run the bot
        bot.run()
    except KeyboardInterrupt:
        logging.info("Shutting down bot...")
    except Exception as e:
        logging.error(f"Bot error: {str(e)}")

if __name__ == "__main__":
    main() 
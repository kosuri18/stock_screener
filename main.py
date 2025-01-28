from data_collector import DataCollector
import logging
from config import STOCK_UNIVERSE, SCREENING_PARAMS
import pandas as pd

def main():
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize data collector
        collector = DataCollector()
        
        # Store results for each stock
        results = []
        
        # Process each stock in universe
        for ticker in STOCK_UNIVERSE:
            try:
                logger.info(f"Processing {ticker}")
                
                # Fetch stock data
                stock_data = collector.fetch_stock_data(ticker)
                
                # Fetch options data
                options_data = collector.fetch_options_chain(ticker)
                
                # Fetch news
                news_data = collector.fetch_market_news(ticker)
                
                # Store basic results
                result = {
                    'ticker': ticker,
                    'current_price': stock_data['Close'][-1],
                    'volume': stock_data['Volume'][-1],
                    'sma_20': stock_data['SMA_20'][-1],
                    'sma_50': stock_data['SMA_50'][-1],
                    'volatility': stock_data['Volatility'][-1],
                    'news_count': len(news_data),
                    'options_available': len(options_data['calls']) + len(options_data['puts'])
                }
                
                results.append(result)
                
            except Exception as e:
                logger.error(f"Error processing {ticker}: {str(e)}")
                continue
        
        # Convert results to DataFrame
        results_df = pd.DataFrame(results)
        print("\nScreening Results:")
        print(results_df)
        
    except Exception as e:
        logger.error(f"Critical error in main: {str(e)}")
        raise

if __name__ == "__main__":
    main() 
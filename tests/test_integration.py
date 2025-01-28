import logging
import time
from trading_bot import TradingBot
from data_collector import DataCollector
from technical_analysis import TechnicalAnalysis
from pipeline import Pipeline
from broker_integration import BrokerIntegration

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_single_stock():
    """Test the entire flow with a single stock"""
    try:
        # Initialize components
        dc = DataCollector()
        ta = TechnicalAnalysis()
        pipeline = Pipeline()
        broker = BrokerIntegration()
        
        # Test data collection
        logger.info("Testing data collection for AAPL...")
        data = dc.collect_data('AAPL')
        assert data is not None, "Data collection failed"
        assert 'stock_data' in data, "No stock data in response"
        assert not data['stock_data'].empty, "Empty stock data"
        
        # Test technical analysis
        logger.info("Testing technical analysis...")
        analysis = ta.analyze(data['stock_data'])
        assert analysis is not None, "Technical analysis failed"
        assert 'signals' in analysis, "No signals generated"
        
        # Test pipeline
        logger.info("Testing pipeline processing...")
        signal = pipeline.process('AAPL')
        assert signal is not None, "Pipeline processing failed"
        assert 'action' in signal, "No action in signal"
        
        # Test broker integration
        logger.info("Testing broker integration...")
        portfolio = broker.get_portfolio()
        assert portfolio is not None, "Portfolio retrieval failed"
        
        logger.info("All component tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        return False

def test_full_bot():
    """Test the complete trading bot"""
    try:
        # Initialize bot with test settings
        bot = TradingBot(
            tickers=['AAPL', 'MSFT'],
            check_interval=60,
            test_mode=True
        )
        
        # Run one complete cycle
        logger.info("Running one complete trading cycle...")
        bot.check_positions()
        
        # Wait for processing
        time.sleep(5)
        
        logger.info("Full bot test completed!")
        return True
        
    except Exception as e:
        logger.error(f"Bot test failed: {str(e)}")
        return False

def main():
    """Run all tests"""
    try:
        # Run component test
        logger.info("Starting component integration test...")
        component_test = test_single_stock()
        
        if not component_test:
            logger.error("Component integration test failed!")
            return
            
        # Run full bot test
        logger.info("Starting full bot test...")
        bot_test = test_full_bot()
        
        if not bot_test:
            logger.error("Full bot test failed!")
            return
            
        logger.info("All tests completed successfully!")
        
    except Exception as e:
        logger.error(f"Testing failed: {str(e)}")

if __name__ == "__main__":
    main() 
import logging
import pandas as pd
from data_collector import DataCollector
from technical_analysis import TechnicalAnalysis
from options_analysis import OptionsAnalysis
from backtester import Backtester
from pipeline import Pipeline
from broker_integration import BrokerIntegration

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_data_collector():
    logger.info("Testing Data Collector...")
    dc = DataCollector()
    data = dc.collect_data('AAPL')
    assert data is not None, "Data collector returned None"
    assert 'stock_data' in data, "No stock data found"
    logger.info("Stock data shape: %s", data['stock_data'].shape)
    return data

def test_technical_analysis(data):
    logger.info("Testing Technical Analysis...")
    ta = TechnicalAnalysis()
    analysis = ta.analyze(data['stock_data'])
    assert analysis is not None, "Technical analysis returned None"
    logger.info("Technical analysis results: %s", analysis)
    return analysis

def test_options_analysis(data):
    logger.info("Testing Options Analysis...")
    oa = OptionsAnalysis()
    analysis = oa.analyze(data['options_data'])
    assert analysis is not None, "Options analysis returned None"
    logger.info("Options analysis results: %s", analysis)
    return analysis

def test_backtester(data):
    logger.info("Testing Backtester...")
    bt = Backtester()
    results = bt.run(data)
    assert results is not None, "Backtester returned None"
    logger.info("Backtest results: %s", results)
    return results

def test_pipeline():
    logger.info("Testing Pipeline...")
    pipeline = Pipeline()
    signal = pipeline.process('AAPL')
    assert signal is not None, "Pipeline returned None"
    assert 'action' in signal, "No action in signal"
    logger.info("Trade signal: %s", signal)
    return signal

def test_broker():
    logger.info("Testing Broker Integration...")
    broker = BrokerIntegration()
    portfolio = broker.get_portfolio()
    assert portfolio is not None, "Broker returned None for portfolio"
    logger.info("Portfolio: %s", portfolio)
    return portfolio

def main():
    try:
        # Test each component
        data = test_data_collector()
        technical = test_technical_analysis(data)
        options = test_options_analysis(data)
        backtest = test_backtester(data)
        signal = test_pipeline()
        portfolio = test_broker()
        
        logger.info("All tests completed successfully!")
        
    except Exception as e:
        logger.error("Test failed: %s", str(e))
        raise

if __name__ == "__main__":
    main() 
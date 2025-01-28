import argparse
import json
from pipeline import ScreenerPipeline
from config import STOCK_UNIVERSE
import logging
import pandas as pd
from datetime import datetime
import os
from typing import Dict, Any
import yfinance as yf

class StockScreenerApp:
    def __init__(self):
        self.pipeline = ScreenerPipeline()
        self.setup_logging()
        
    def setup_logging(self):
        """Set up logging configuration"""
        log_dir = 'logs'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'logs/screener_{datetime.now().strftime("%Y%m%d")}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def format_chat_response(self, analysis: Dict[str, Any], ticker: str) -> str:
        """Format analysis results as a chatbot-like response"""
        try:
            # Get company info
            company = yf.Ticker(ticker)
            info = company.info
            company_name = info.get('longName', ticker)
            sector = info.get('sector', 'N/A')
            industry = info.get('industry', 'N/A')
            
            # Format the response
            response = [
                f"📊 Analysis Report for {company_name} ({ticker}) 📊\n",
                f"Sector: {sector}",
                f"Industry: {industry}\n",
                
                "🎯 Current Market Status:",
                f"Current Price: ${analysis['current_price']:.2f}",
                f"Market Cap: ${info.get('marketCap', 0)/1e9:.2f}B",
                f"52-Week Range: ${info.get('fiftyTwoWeekLow', 0):.2f} - ${info.get('fiftyTwoWeekHigh', 0):.2f}\n",
                
                "📈 Technical Analysis:",
                f"Trend: {analysis['technical_analysis']['trend']['sma_20_50_cross']}",
                f"RSI ({analysis['technical_analysis']['momentum']['rsi']['value']:.2f}): {analysis['technical_analysis']['momentum']['rsi']['signal']}",
                f"MACD Signal: {analysis['technical_analysis']['trend']['macd_signal']}",
                f"Stochastic Oscillator: {analysis['technical_analysis']['momentum']['stochastic']['signal']}\n",
                
                "💡 Market Sentiment:",
                f"Overall Sentiment Score: {analysis['sentiment_score']:.2f}",
                "Interpretation: " + self._interpret_sentiment(analysis['sentiment_score']),
                
                "\n🎯 Trading Opportunities:"
            ]
            
            # Add trade suggestions
            for suggestion in analysis['trade_suggestions']:
                response.extend([
                    f"\nStrategy: {suggestion['strategy_type']}",
                    f"Entry Price: ${suggestion['entry_price']:.2f}",
                    f"Exit Price: ${suggestion['exit_price']:.2f}",
                    f"Max Profit: ${suggestion['max_profit']:.2f}",
                    f"Max Loss: ${suggestion['max_loss']:.2f}",
                    f"Risk/Reward Ratio: {suggestion['risk_reward_ratio']:.2f}",
                    f"Probability of Profit: {suggestion['probability_profit']*100:.1f}%"
                ])
            
            # Add volatility analysis
            vol_analysis = analysis['technical_analysis']['volatility']['bollinger']
            response.extend([
                "\n📊 Volatility Analysis:",
                f"Bollinger Band Position: {vol_analysis['position']}",
                f"Volatility Bandwidth: {vol_analysis['bandwidth']:.2f}",
                self._interpret_volatility(vol_analysis)
            ])
            
            # Add recommendation
            response.extend([
                "\n🎯 Overall Recommendation:",
                self._generate_recommendation(analysis)
            ])
            
            return "\n".join(response)
            
        except Exception as e:
            self.logger.error(f"Error formatting chat response: {str(e)}")
            return f"Error generating detailed analysis for {ticker}. Please try again later."
    
    def _interpret_sentiment(self, score: float) -> str:
        if score >= 0.7:
            return "Very Bullish - Strong positive sentiment in the market"
        elif score >= 0.6:
            return "Bullish - Generally positive market sentiment"
        elif score >= 0.4:
            return "Neutral - Mixed market sentiment"
        elif score >= 0.3:
            return "Bearish - Generally negative market sentiment"
        else:
            return "Very Bearish - Strong negative sentiment in the market"
    
    def _interpret_volatility(self, vol_analysis: Dict) -> str:
        position = vol_analysis['position']
        bandwidth = vol_analysis['bandwidth']
        
        if position == 'UPPER':
            return "⚠️ Stock is trading above upper Bollinger Band - potentially overbought"
        elif position == 'LOWER':
            return "💡 Stock is trading below lower Bollinger Band - potentially oversold"
        else:
            if bandwidth > 0.2:
                return "⚠️ High volatility - consider reducing position sizes"
            else:
                return "✅ Normal volatility levels - standard position sizing recommended"
    
    def _generate_recommendation(self, analysis: Dict) -> str:
        trend = analysis['technical_analysis']['trend']['sma_20_50_cross']
        rsi = analysis['technical_analysis']['momentum']['rsi']
        sentiment = analysis['sentiment_score']
        
        if trend == 'BULLISH' and rsi['signal'] == 'OVERSOLD' and sentiment > 0.5:
            return "Strong Buy - Technical indicators and sentiment align for a potential upward move"
        elif trend == 'BEARISH' and rsi['signal'] == 'OVERBOUGHT' and sentiment < 0.5:
            return "Strong Sell - Technical indicators and sentiment suggest potential downside"
        elif trend == 'BULLISH' and sentiment > 0.5:
            return "Buy - Positive trend with supporting market sentiment"
        elif trend == 'BEARISH' and sentiment < 0.5:
            return "Sell - Negative trend with weak market sentiment"
        else:
            return "Hold/Neutral - Mixed signals suggest waiting for clearer direction"
    
    def save_results(self, results, output_dir='results'):
        """Save analysis results to files"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        json_file = f'{output_dir}/analysis_{timestamp}.json'
        with open(json_file, 'w') as f:
            json.dump(results, f, indent=4)
        
        summary_data = []
        for ticker, analysis in results.items():
            if 'error' not in analysis:
                summary_data.append({
                    'Ticker': ticker,
                    'Price': analysis['current_price'],
                    'Trend': analysis['technical_analysis']['trend']['sma_20_50_cross'],
                    'RSI': analysis['technical_analysis']['momentum']['rsi']['value'],
                    'Sentiment': analysis['sentiment_score']
                })
        
        summary_df = pd.DataFrame(summary_data)
        csv_file = f'{output_dir}/summary_{timestamp}.csv'
        summary_df.to_csv(csv_file, index=False)
        
        return json_file, csv_file
    
    def run_single_stock(self, ticker):
        """Analyze a single stock"""
        self.logger.info(f"Analyzing {ticker}")
        results = self.pipeline.analyze_stock(ticker)
        return {ticker: results}
    
    def run_stock_universe(self, tickers=None):
        """Analyze multiple stocks"""
        if tickers is None:
            tickers = STOCK_UNIVERSE
            
        results = {}
        for ticker in tickers:
            try:
                self.logger.info(f"Analyzing {ticker}")
                results[ticker] = self.pipeline.analyze_stock(ticker)
            except Exception as e:
                self.logger.error(f"Error analyzing {ticker}: {str(e)}")
                results[ticker] = {"error": str(e)}
        
        return results

def main():
    parser = argparse.ArgumentParser(description='Stock Screener and Options Trade Suggester')
    parser.add_argument('--ticker', type=str, help='Single stock ticker to analyze')
    parser.add_argument('--universe', action='store_true', help='Analyze entire stock universe')
    parser.add_argument('--output', type=str, default='results', help='Output directory for results')
    
    args = parser.parse_args()
    
    app = StockScreenerApp()
    
    try:
        if args.ticker:
            results = app.run_single_stock(args.ticker)
            json_file, csv_file = app.save_results(results, args.output)
            
            # Print chatbot-style response
            ticker = args.ticker
            if 'error' not in results[ticker]:
                print("\n" + "="*80)
                print(app.format_chat_response(results[ticker], ticker))
                print("="*80 + "\n")
                print(f"Detailed results saved to: {json_file}")
                print(f"Summary saved to: {csv_file}")
            else:
                print(f"Error analyzing {ticker}: {results[ticker]['error']}")
                
        elif args.universe:
            results = app.run_stock_universe()
            json_file, csv_file = app.save_results(results, args.output)
            
            print("\nAnalysis completed for stock universe!")
            print(f"Detailed results saved to: {json_file}")
            print(f"Summary saved to: {csv_file}")
            
            # Print summary of interesting findings
            print("\nHighlights from analysis:")
            for ticker, analysis in results.items():
                if 'error' not in analysis:
                    if (analysis['technical_analysis']['momentum']['rsi']['signal'] in ['OVERSOLD', 'OVERBOUGHT'] or
                        abs(analysis['sentiment_score'] - 0.5) > 0.2):
                        print(f"\n{ticker}:")
                        print(app.format_chat_response(analysis, ticker))
        else:
            print("Please specify either --ticker or --universe")
            
    except Exception as e:
        print(f"Error running analysis: {str(e)}")

if __name__ == "__main__":
    main() 
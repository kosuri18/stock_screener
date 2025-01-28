import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os
from typing import Dict, Any
import yfinance as yf

class TradingDashboard:
    def __init__(self):
        st.set_page_config(
            page_title="Trading Bot Dashboard",
            page_icon="📈",
            layout="wide"
        )
        self.load_data()
        
    def load_data(self):
        """Load trading data from results directory"""
        try:
            # Load latest analysis results
            results_dir = 'results'
            analysis_files = [f for f in os.listdir(results_dir) if f.startswith('analysis_')]
            if analysis_files:
                latest_file = max(analysis_files)
                with open(os.path.join(results_dir, latest_file), 'r') as f:
                    self.analysis_data = json.load(f)
            else:
                self.analysis_data = {}
                
            # Load trading history
            history_file = 'data/trading_history.csv'
            if os.path.exists(history_file):
                self.trading_history = pd.read_csv(history_file)
                self.trading_history['date'] = pd.to_datetime(self.trading_history['date'])
            else:
                self.trading_history = pd.DataFrame()
                
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
    
    def render_header(self):
        """Render dashboard header"""
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.title("📊 Trading Bot Dashboard")
            st.markdown("Real-time monitoring of trading activities and performance")
    
    def render_portfolio_metrics(self):
        """Render portfolio performance metrics"""
        st.subheader("Portfolio Performance")
        
        # Create metrics columns
        col1, col2, col3, col4 = st.columns(4)
        
        try:
            # Calculate metrics
            if not self.trading_history.empty:
                total_trades = len(self.trading_history)
                win_rate = (self.trading_history['profit'] > 0).mean() * 100
                total_profit = self.trading_history['profit'].sum()
                avg_profit_per_trade = self.trading_history['profit'].mean()
                
                # Display metrics
                col1.metric("Total Trades", total_trades)
                col2.metric("Win Rate", f"{win_rate:.1f}%")
                col3.metric("Total Profit", f"${total_profit:,.2f}")
                col4.metric("Avg Profit/Trade", f"${avg_profit_per_trade:,.2f}")
            else:
                st.info("No trading history available yet")
                
        except Exception as e:
            st.error(f"Error calculating metrics: {str(e)}")
    
    def render_profit_chart(self):
        """Render cumulative profit chart"""
        st.subheader("Cumulative Profit Over Time")
        
        try:
            if not self.trading_history.empty:
                # Calculate cumulative profit
                cum_profit = self.trading_history.sort_values('date')
                cum_profit['cumulative_profit'] = cum_profit['profit'].cumsum()
                
                # Create profit chart
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=cum_profit['date'],
                    y=cum_profit['cumulative_profit'],
                    mode='lines',
                    name='Cumulative Profit',
                    line=dict(color='green')
                ))
                
                fig.update_layout(
                    title='Cumulative Profit',
                    xaxis_title='Date',
                    yaxis_title='Profit ($)',
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No profit data available yet")
                
        except Exception as e:
            st.error(f"Error creating profit chart: {str(e)}")
    
    def render_active_positions(self):
        """Render active positions table"""
        st.subheader("Active Positions")
        
        try:
            # Get active positions from broker
            positions = pd.DataFrame(self.analysis_data.get('positions', []))
            
            if not positions.empty:
                # Format positions data
                positions['unrealized_pl'] = positions['unrealized_pl'].map('${:,.2f}'.format)
                positions['market_value'] = positions['market_value'].map('${:,.2f}'.format)
                
                # Display positions
                st.dataframe(positions, use_container_width=True)
            else:
                st.info("No active positions")
                
        except Exception as e:
            st.error(f"Error displaying positions: {str(e)}")
    
    def render_recent_trades(self):
        """Render recent trades table"""
        st.subheader("Recent Trades")
        
        try:
            if not self.trading_history.empty:
                # Get last 10 trades
                recent_trades = self.trading_history.sort_values('date', ascending=False).head(10)
                
                # Format trade data
                recent_trades['profit'] = recent_trades['profit'].map('${:,.2f}'.format)
                recent_trades['price'] = recent_trades['price'].map('${:,.2f}'.format)
                
                # Display trades
                st.dataframe(recent_trades, use_container_width=True)
            else:
                st.info("No trade history available")
                
        except Exception as e:
            st.error(f"Error displaying recent trades: {str(e)}")
    
    def render_market_analysis(self):
        """Render market analysis section"""
        st.subheader("Market Analysis")
        
        try:
            # Display technical analysis for monitored stocks
            for ticker, analysis in self.analysis_data.items():
                if isinstance(analysis, dict) and 'technical_analysis' in analysis:
                    with st.expander(f"{ticker} Analysis"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write("Technical Indicators")
                            st.write(f"Trend: {analysis['technical_analysis']['trend']['sma_20_50_cross']}")
                            st.write(f"RSI: {analysis['technical_analysis']['momentum']['rsi']['value']:.2f}")
                            
                        with col2:
                            st.write("Market Sentiment")
                            st.write(f"Sentiment Score: {analysis.get('sentiment_score', 'N/A')}")
                            
        except Exception as e:
            st.error(f"Error displaying market analysis: {str(e)}")
    
    def run(self):
        """Run the dashboard"""
        self.render_header()
        self.render_portfolio_metrics()
        
        # Create two columns for charts
        col1, col2 = st.columns(2)
        
        with col1:
            self.render_profit_chart()
            
        with col2:
            self.render_active_positions()
            
        self.render_recent_trades()
        self.render_market_analysis()
        
        # Auto-refresh every minute
        st.empty()
        st.markdown(
            """
            <meta http-equiv="refresh" content="60">
            """,
            unsafe_allow_html=True
        )

if __name__ == "__main__":
    dashboard = TradingDashboard()
    dashboard.run() 
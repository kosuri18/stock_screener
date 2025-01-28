"""
Configuration settings for the stock screener application.
"""

# Stock Universe - Default stocks to analyze
STOCK_UNIVERSE = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META',
    'NVDA', 'TSLA', 'JPM', 'V', 'WMT',
    'DIS', 'NFLX', 'PYPL', 'ADBE', 'INTC'
]

# Technical Analysis Parameters
TECHNICAL_PARAMS = {
    # Moving Averages
    'sma_short': 20,
    'sma_long': 50,
    'ema_short': 12,
    'ema_long': 26,
    
    # RSI
    'rsi_period': 14,
    'rsi_oversold': 30,
    'rsi_overbought': 70,
    
    # MACD
    'macd_fast': 12,
    'macd_slow': 26,
    'macd_signal': 9,
    
    # Bollinger Bands
    'bb_period': 20,
    'bb_std': 2,
    
    # Volume
    'volume_ma_period': 20,
    'min_volume': 100000
}

# Options Screening Parameters
OPTIONS_PARAMS = {
    'min_volume': 100,
    'min_open_interest': 500,
    'max_dte': 45,  # Days to expiration
    'min_delta': 0.2,
    'max_delta': 0.8,
    'min_iv': 0.2,  # Minimum implied volatility
    'max_iv': 1.5   # Maximum implied volatility
}

# Backtesting Parameters
BACKTEST_PARAMS = {
    'initial_capital': 100000,
    'position_size': 0.1,  # 10% of capital per trade
    'max_positions': 5,
    'stop_loss': 0.05,    # 5% stop loss
    'take_profit': 0.15   # 15% take profit
}

# Trading Strategy Parameters
STRATEGY_PARAMS = {
    'covered_call': {
        'otm_pct': 0.05,  # 5% out of the money
        'min_premium': 0.02,  # Minimum premium as % of stock price
        'days_to_expiry': 30
    },
    'put_spread': {
        'width': 0.05,    # 5% width between strikes
        'max_risk': 0.02  # Maximum risk as % of capital
    },
    'iron_condor': {
        'wing_width': 0.1,  # 10% wing width
        'body_width': 0.05  # 5% body width
    }
}

# Data Collection Parameters
DATA_PARAMS = {
    'default_period': '1y',
    'default_interval': '1d',
    'min_price': 5.0,
    'max_price': 1000.0,
    'min_market_cap': 1e9  # $1 billion minimum market cap
}

# Sentiment Analysis Parameters
SENTIMENT_PARAMS = {
    'min_news_items': 5,
    'sentiment_threshold': 0.6,
    'news_lookback_days': 7
}

# File Paths
PATHS = {
    'data_dir': 'data',
    'results_dir': 'results',
    'logs_dir': 'logs',
    'reports_dir': 'reports'
}

# API Configuration
API_CONFIG = {
    'retry_attempts': 3,
    'retry_delay': 5,
    'timeout': 30,
    'rate_limit': 5  # requests per second
}

# Logging Configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'date_format': '%Y-%m-%d %H:%M:%S'
}

# Risk Management Parameters
RISK_PARAMS = {
    'max_portfolio_risk': 0.02,  # Maximum 2% risk per portfolio
    'max_position_risk': 0.01,   # Maximum 1% risk per position
    'max_correlation': 0.7,      # Maximum correlation between positions
    'min_sharpe_ratio': 1.5,     # Minimum Sharpe ratio for suggestions
    'max_vix': 45               # Maximum VIX level for new positions
} 
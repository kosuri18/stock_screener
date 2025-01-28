import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os

# Create sample trading history
dates = pd.date_range(start='2024-01-01', end=datetime.now(), freq='D')
trading_history = pd.DataFrame({
    'date': dates,
    'ticker': np.random.choice(['AAPL', 'GOOGL', 'MSFT', 'AMZN'], len(dates)),
    'action': np.random.choice(['BUY', 'SELL'], len(dates)),
    'price': np.random.uniform(100, 200, len(dates)),
    'quantity': np.random.randint(1, 100, len(dates)),
    'profit': np.random.uniform(-500, 1000, len(dates))
})

# Save trading history
os.makedirs('data', exist_ok=True)
trading_history.to_csv('data/trading_history.csv', index=False)

# Create sample analysis data
analysis_data = {
    'AAPL': {
        'technical_analysis': {
            'trend': {'sma_20_50_cross': 'BULLISH'},
            'momentum': {'rsi': {'value': 65.5}}
        },
        'sentiment_score': 0.75
    },
    'GOOGL': {
        'technical_analysis': {
            'trend': {'sma_20_50_cross': 'BEARISH'},
            'momentum': {'rsi': {'value': 45.2}}
        },
        'sentiment_score': 0.60
    }
}

# Save analysis data
os.makedirs('results', exist_ok=True)
with open(f'results/analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json', 'w') as f:
    json.dump(analysis_data, f)

print("Sample data created successfully!") 
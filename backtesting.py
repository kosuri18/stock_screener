import pandas as pd
import numpy as np
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class TradeResult:
    entry_date: str
    exit_date: str
    entry_price: float
    exit_price: float
    profit_loss: float
    profit_loss_pct: float
    holding_period: int
    strategy: str

class Backtester:
    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.trades: List[TradeResult] = []
        self.initial_capital = 100000
        self.current_capital = self.initial_capital
        
    def run_backtest(self, strategy: str = 'momentum') -> Dict[str, Any]:
        """Run backtest for the specified strategy"""
        if strategy == 'momentum':
            return self._backtest_momentum()
        elif strategy == 'mean_reversion':
            return self._backtest_mean_reversion()
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
    
    def _backtest_momentum(self) -> Dict[str, Any]:
        """Momentum strategy backtest"""
        position = 0
        entry_price = 0
        entry_date = None
        
        for i in range(20, len(self.data)):
            current_row = self.data.iloc[i]
            prev_row = self.data.iloc[i-1]
            
            # Entry conditions
            if position == 0:
                if (current_row['SMA_20'] > current_row['SMA_50'] and 
                    prev_row['SMA_20'] <= prev_row['SMA_50']):
                    position = 1
                    entry_price = current_row['Close']
                    entry_date = current_row.name
            
            # Exit conditions
            elif position == 1:
                if (current_row['SMA_20'] < current_row['SMA_50'] and 
                    prev_row['SMA_20'] >= prev_row['SMA_50']):
                    exit_price = current_row['Close']
                    profit_loss = exit_price - entry_price
                    profit_loss_pct = (profit_loss / entry_price) * 100
                    holding_period = (current_row.name - entry_date).days
                    
                    self.trades.append(TradeResult(
                        entry_date=str(entry_date),
                        exit_date=str(current_row.name),
                        entry_price=entry_price,
                        exit_price=exit_price,
                        profit_loss=profit_loss,
                        profit_loss_pct=profit_loss_pct,
                        holding_period=holding_period,
                        strategy='momentum'
                    ))
                    
                    position = 0
                    self.current_capital *= (1 + profit_loss_pct/100)
        
        return self._generate_backtest_stats()
    
    def _backtest_mean_reversion(self) -> Dict[str, Any]:
        """Mean reversion strategy backtest"""
        position = 0
        entry_price = 0
        entry_date = None
        
        for i in range(20, len(self.data)):
            current_row = self.data.iloc[i]
            
            # Entry conditions
            if position == 0:
                if current_row['RSI'] < 30:
                    position = 1
                    entry_price = current_row['Close']
                    entry_date = current_row.name
            
            # Exit conditions
            elif position == 1:
                if current_row['RSI'] > 70:
                    exit_price = current_row['Close']
                    profit_loss = exit_price - entry_price
                    profit_loss_pct = (profit_loss / entry_price) * 100
                    holding_period = (current_row.name - entry_date).days
                    
                    self.trades.append(TradeResult(
                        entry_date=str(entry_date),
                        exit_date=str(current_row.name),
                        entry_price=entry_price,
                        exit_price=exit_price,
                        profit_loss=profit_loss,
                        profit_loss_pct=profit_loss_pct,
                        holding_period=holding_period,
                        strategy='mean_reversion'
                    ))
                    
                    position = 0
                    self.current_capital *= (1 + profit_loss_pct/100)
        
        return self._generate_backtest_stats()
    
    def _generate_backtest_stats(self) -> Dict[str, Any]:
        """Generate backtest statistics"""
        if not self.trades:
            return {"error": "No trades executed"}
        
        profits = [trade.profit_loss for trade in self.trades]
        profit_pcts = [trade.profit_loss_pct for trade in self.trades]
        holding_periods = [trade.holding_period for trade in self.trades]
        
        return {
            "total_trades": len(self.trades),
            "winning_trades": len([p for p in profits if p > 0]),
            "losing_trades": len([p for p in profits if p <= 0]),
            "avg_profit_loss": np.mean(profits),
            "avg_profit_loss_pct": np.mean(profit_pcts),
            "max_profit": max(profits),
            "max_loss": min(profits),
            "avg_holding_period": np.mean(holding_periods),
            "final_capital": self.current_capital,
            "total_return_pct": ((self.current_capital - self.initial_capital) / self.initial_capital) * 100,
            "sharpe_ratio": np.mean(profit_pcts) / np.std(profit_pcts) if len(profit_pcts) > 1 else 0
        } 
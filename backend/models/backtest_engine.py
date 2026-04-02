"""Backtesting engine for strategy evaluation."""

import pandas as pd
import numpy as np
from typing import Dict, Optional
from pathlib import Path

from config import config
from utils.logger import get_logger
from utils.helpers import (
    calculate_sharpe_ratio,
    calculate_max_drawdown,
    calculate_win_rate,
    calculate_profit_factor,
    ensure_dir
)
from .strategies import BaseStrategy

logger = get_logger(__name__)


class BacktestEngine:
    """Engine for backtesting trading strategies."""
    
    def __init__(
        self,
        initial_capital: float = 100000,
        commission: float = 0.001,
        slippage: float = 0.0005
    ):
        """
        Initialize backtest engine.
        
        Args:
            initial_capital: Starting capital
            commission: Commission rate (0.001 = 0.1%)
            slippage: Slippage rate (0.0005 = 0.05%)
        """
        self.initial_capital = initial_capital or config.get('backtesting.initial_capital', 100000)
        self.commission = commission or config.get('backtesting.commission', 0.001)
        self.slippage = slippage or config.get('backtesting.slippage', 0.0005)
        
        self.results = {}
        
        logger.info("BacktestEngine initialized")
        logger.info(f"Initial capital: ${self.initial_capital:,.2f}")
        logger.info(f"Commission: {self.commission*100:.2f}%")
        logger.info(f"Slippage: {self.slippage*100:.3f}%")
    
    def run_backtest(
        self,
        df: pd.DataFrame,
        strategy: BaseStrategy,
        position_size: float = 0.1
    ) -> Dict:
        """
        Run backtest for a strategy.
        
        Args:
            df: DataFrame with features and prices
            strategy: Trading strategy
            position_size: Position size as fraction of capital
            
        Returns:
            Dictionary with backtest results
        """
        logger.info(f"Running backtest for {strategy.name}...")
        
        # Ensure data is sorted
        df = df.sort_values('date').reset_index(drop=True)
        
        # Generate signals
        signals = strategy.generate_signals(df)
        
        # Initialize tracking variables
        capital = self.initial_capital
        position = 0  # Number of shares
        cash = capital
        portfolio_values = []
        trades = []
        
        for i in range(len(df)):
            row = df.iloc[i]
            signal = signals.iloc[i]
            price = row['close']
            
            # Calculate portfolio value
            portfolio_value = cash + (position * price)
            portfolio_values.append(portfolio_value)
            
            # Execute trades based on signals
            if signal == 1 and position == 0:  # Buy signal
                # Calculate position size
                position_value = portfolio_value * position_size
                shares_to_buy = int(position_value / (price * (1 + self.slippage)))
                
                if shares_to_buy > 0:
                    cost = shares_to_buy * price * (1 + self.slippage + self.commission)
                    
                    if cost <= cash:
                        position = shares_to_buy
                        cash -= cost
                        
                        trades.append({
                            'date': row['date'],
                            'type': 'BUY',
                            'price': price,
                            'shares': shares_to_buy,
                            'cost': cost,
                            'portfolio_value': portfolio_value
                        })
            
            elif signal == -1 and position > 0:  # Sell signal
                proceeds = position * price * (1 - self.slippage - self.commission)
                cash += proceeds
                
                trades.append({
                    'date': row['date'],
                    'type': 'SELL',
                    'price': price,
                    'shares': position,
                    'proceeds': proceeds,
                    'portfolio_value': portfolio_value
                })
                
                position = 0
        
        # Close any open position at the end
        if position > 0:
            final_price = df.iloc[-1]['close']
            proceeds = position * final_price * (1 - self.slippage - self.commission)
            cash += proceeds
            position = 0
        
        # Calculate final portfolio value
        final_value = cash
        
        # Create portfolio series
        df['portfolio_value'] = portfolio_values
        df['signal'] = signals
        
        # Calculate returns
        df['portfolio_return'] = df['portfolio_value'].pct_change()
        df['buy_hold_value'] = self.initial_capital * (df['close'] / df['close'].iloc[0])
        df['buy_hold_return'] = df['buy_hold_value'].pct_change()
        
        # Calculate metrics
        metrics = self._calculate_metrics(df, trades, final_value)
        
        # Store results
        results = {
            'strategy': strategy.name,
            'params': strategy.params,
            'metrics': metrics,
            'trades': pd.DataFrame(trades),
            'portfolio_history': df[['date', 'close', 'portfolio_value', 'buy_hold_value', 'signal']].copy()
        }
        
        self.results[strategy.name] = results
        
        logger.info(f"Backtest complete for {strategy.name}")
        logger.info(f"Total Return: {metrics['total_return']:.2%}")
        logger.info(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
        logger.info(f"Max Drawdown: {metrics['max_drawdown']:.2%}")
        logger.info(f"Number of Trades: {metrics['num_trades']}")
        
        return results
    
    def _calculate_metrics(
        self,
        df: pd.DataFrame,
        trades: list,
        final_value: float
    ) -> Dict:
        """Calculate performance metrics."""
        # Total return
        total_return = (final_value - self.initial_capital) / self.initial_capital
        
        # Buy and hold return
        buy_hold_return = (df['close'].iloc[-1] - df['close'].iloc[0]) / df['close'].iloc[0]
        
        # Sharpe ratio
        portfolio_returns = df['portfolio_return'].dropna()
        sharpe_ratio = calculate_sharpe_ratio(portfolio_returns) if len(portfolio_returns) > 0 else 0
        
        # Max drawdown
        max_drawdown = calculate_max_drawdown(portfolio_returns) if len(portfolio_returns) > 0 else 0
        
        # Win rate
        if trades:
            trade_returns = []
            for i in range(0, len(trades) - 1, 2):
                if i + 1 < len(trades) and trades[i]['type'] == 'BUY' and trades[i+1]['type'] == 'SELL':
                    buy_price = trades[i]['price']
                    sell_price = trades[i+1]['price']
                    trade_return = (sell_price - buy_price) / buy_price
                    trade_returns.append(trade_return)
            
            if trade_returns:
                trade_returns_series = pd.Series(trade_returns)
                win_rate = calculate_win_rate(trade_returns_series)
                profit_factor = calculate_profit_factor(trade_returns_series)
            else:
                win_rate = 0
                profit_factor = 0
        else:
            win_rate = 0
            profit_factor = 0
        
        metrics = {
            'initial_capital': self.initial_capital,
            'final_value': final_value,
            'total_return': total_return,
            'buy_hold_return': buy_hold_return,
            'excess_return': total_return - buy_hold_return,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'num_trades': len(trades),
            'num_days': len(df)
        }
        
        return metrics
    
    def compare_strategies(self, results_list: list) -> pd.DataFrame:
        """
        Compare multiple strategy results.
        
        Args:
            results_list: List of backtest results
            
        Returns:
            DataFrame with comparison
        """
        comparison = []
        
        for result in results_list:
            metrics = result['metrics']
            comparison.append({
                'Strategy': result['strategy'],
                'Total Return': f"{metrics['total_return']:.2%}",
                'Buy & Hold': f"{metrics['buy_hold_return']:.2%}",
                'Excess Return': f"{metrics['excess_return']:.2%}",
                'Sharpe Ratio': f"{metrics['sharpe_ratio']:.2f}",
                'Max Drawdown': f"{metrics['max_drawdown']:.2%}",
                'Win Rate': f"{metrics['win_rate']:.2%}",
                'Profit Factor': f"{metrics['profit_factor']:.2f}",
                'Num Trades': metrics['num_trades']
            })
        
        return pd.DataFrame(comparison)
    
    def save_results(self, output_dir: str = "./data/backtesting") -> None:
        """
        Save backtest results to disk.
        
        Args:
            output_dir: Output directory
        """
        output_path = Path(output_dir)
        ensure_dir(output_path)
        
        for strategy_name, results in self.results.items():
            # Save trades
            if not results['trades'].empty:
                trades_file = output_path / f"{strategy_name.replace(' ', '_')}_trades.csv"
                results['trades'].to_csv(trades_file, index=False)
            
            # Save portfolio history
            history_file = output_path / f"{strategy_name.replace(' ', '_')}_history.parquet"
            results['portfolio_history'].to_parquet(history_file, index=False)
            
            # Save metrics
            metrics_file = output_path / f"{strategy_name.replace(' ', '_')}_metrics.txt"
            with open(metrics_file, 'w') as f:
                f.write(f"Backtest Results: {strategy_name}\n")
                f.write("=" * 60 + "\n\n")
                for key, value in results['metrics'].items():
                    f.write(f"{key}: {value}\n")
        
        logger.info(f"Results saved to {output_path}")


def main():
    """Main entry point for backtesting."""
    import argparse
    from feature_store import OfflineFeatureStore
    from .strategies import RSIStrategy, MACDStrategy, TrendFollowingStrategy
    
    parser = argparse.ArgumentParser(description='Run strategy backtesting')
    parser.add_argument('--strategy', choices=['rsi', 'macd', 'trend', 'all'], default='all',
                       help='Strategy to backtest')
    parser.add_argument('--ticker', type=str, default='AAPL',
                       help='Ticker to backtest')
    
    args = parser.parse_args()
    
    # Load features
    store = OfflineFeatureStore()
    df = store.read_features('market_features', filters={'ticker': args.ticker})
    
    if df.empty:
        logger.error(f"No data found for {args.ticker}")
        return
    
    # Initialize engine
    engine = BacktestEngine()
    
    # Run backtests
    strategies = []
    
    if args.strategy in ['rsi', 'all']:
        strategies.append(RSIStrategy())
    
    if args.strategy in ['macd', 'all']:
        strategies.append(MACDStrategy())
    
    if args.strategy in ['trend', 'all']:
        strategies.append(TrendFollowingStrategy())
    
    results_list = []
    for strategy in strategies:
        result = engine.run_backtest(df, strategy)
        results_list.append(result)
    
    # Compare strategies
    if len(results_list) > 1:
        comparison = engine.compare_strategies(results_list)
        print("\n" + "=" * 80)
        print("STRATEGY COMPARISON")
        print("=" * 80)
        print(comparison.to_string(index=False))
    
    # Save results
    engine.save_results()


if __name__ == '__main__':
    main()

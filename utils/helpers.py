"""Helper utility functions."""

import os
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Union, Optional


def ensure_dir(directory: Union[str, Path]) -> Path:
    """
    Ensure directory exists, create if it doesn't.
    
    Args:
        directory: Directory path
        
    Returns:
        Path object
    """
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_timestamp(fmt: str = "%Y%m%d_%H%M%S") -> str:
    """
    Get current timestamp as formatted string.
    
    Args:
        fmt: Timestamp format
        
    Returns:
        Formatted timestamp string
    """
    return datetime.now().strftime(fmt)


def calculate_returns(prices: pd.Series, method: str = "simple") -> pd.Series:
    """
    Calculate returns from price series.
    
    Args:
        prices: Price series
        method: 'simple' or 'log'
        
    Returns:
        Returns series
    """
    if method == "simple":
        return prices.pct_change()
    elif method == "log":
        return np.log(prices / prices.shift(1))
    else:
        raise ValueError(f"Unknown method: {method}")


def calculate_sharpe_ratio(
    returns: pd.Series,
    risk_free_rate: float = 0.02,
    periods_per_year: int = 252
) -> float:
    """
    Calculate annualized Sharpe ratio.
    
    Args:
        returns: Returns series
        risk_free_rate: Annual risk-free rate
        periods_per_year: Number of periods in a year (252 for daily)
        
    Returns:
        Sharpe ratio
    """
    excess_returns = returns - (risk_free_rate / periods_per_year)
    
    if excess_returns.std() == 0:
        return 0.0
    
    sharpe = np.sqrt(periods_per_year) * (excess_returns.mean() / excess_returns.std())
    return sharpe


def calculate_max_drawdown(returns: pd.Series) -> float:
    """
    Calculate maximum drawdown from returns series.
    
    Args:
        returns: Returns series
        
    Returns:
        Maximum drawdown (negative value)
    """
    cumulative = (1 + returns).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    return drawdown.min()


def calculate_win_rate(returns: pd.Series) -> float:
    """
    Calculate win rate (percentage of positive returns).
    
    Args:
        returns: Returns series
        
    Returns:
        Win rate (0 to 1)
    """
    if len(returns) == 0:
        return 0.0
    return (returns > 0).sum() / len(returns)


def calculate_profit_factor(returns: pd.Series) -> float:
    """
    Calculate profit factor (gross profit / gross loss).
    
    Args:
        returns: Returns series
        
    Returns:
        Profit factor
    """
    gains = returns[returns > 0].sum()
    losses = abs(returns[returns < 0].sum())
    
    if losses == 0:
        return np.inf if gains > 0 else 0.0
    
    return gains / losses


def format_percentage(value: float, decimals: int = 2) -> str:
    """
    Format value as percentage string.
    
    Args:
        value: Value to format (0.1 = 10%)
        decimals: Number of decimal places
        
    Returns:
        Formatted percentage string
    """
    return f"{value * 100:.{decimals}f}%"


def format_currency(value: float, symbol: str = "$") -> str:
    """
    Format value as currency string.
    
    Args:
        value: Value to format
        symbol: Currency symbol
        
    Returns:
        Formatted currency string
    """
    return f"{symbol}{value:,.2f}"

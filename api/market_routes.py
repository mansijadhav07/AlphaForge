"""
Market data and analytics API routes.

Provides endpoints for market overview, stock features, backtesting, and insights.
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import random
from datetime import datetime, timedelta

from api.schemas import (
    MarketOverview,
    StockFeatures,
    BacktestResult,
    Insight
)

router = APIRouter(prefix="/api", tags=["Market Data"])


@router.get("/market-overview", response_model=MarketOverview)
async def get_market_overview():
    """
    Get market overview with top stocks and signals.
    
    Returns:
        Market overview data including regime, volatility, top stocks, and signals
    """
    # Mock data for now - replace with real data later
    regimes = ["Bull", "Bear", "Sideways"]
    regime = random.choice(regimes)
    
    return MarketOverview(
        timestamp=datetime.now().isoformat(),
        market_regime=regime,
        volatility_index=random.uniform(10, 30),
        top_stocks=[
            {
                "ticker": "AAPL",
                "price": 175.50 + random.uniform(-5, 5),
                "change": random.uniform(-3, 3),
                "change_pct": random.uniform(-2, 2)
            },
            {
                "ticker": "TSLA",
                "price": 245.30 + random.uniform(-10, 10),
                "change": random.uniform(-5, 5),
                "change_pct": random.uniform(-3, 3)
            },
            {
                "ticker": "GOOGL",
                "price": 140.20 + random.uniform(-3, 3),
                "change": random.uniform(-2, 2),
                "change_pct": random.uniform(-1.5, 1.5)
            },
            {
                "ticker": "MSFT",
                "price": 380.75 + random.uniform(-8, 8),
                "change": random.uniform(-4, 4),
                "change_pct": random.uniform(-2, 2)
            }
        ],
        signals=[
            {
                "ticker": "AAPL",
                "signal": "BUY",
                "confidence": 0.75,
                "reason": "Strong momentum with RSI oversold and positive MACD crossover"
            },
            {
                "ticker": "TSLA",
                "signal": "HOLD",
                "confidence": 0.60,
                "reason": "Mixed signals - high volatility but neutral momentum"
            },
            {
                "ticker": "GOOGL",
                "signal": "SELL",
                "confidence": 0.68,
                "reason": "Overbought conditions with bearish divergence"
            }
        ]
    )


@router.get("/features/{symbol}")
async def get_features(symbol: str):
    """
    Get computed features for a stock symbol.
    
    Args:
        symbol: Stock ticker symbol (e.g., AAPL)
        
    Returns:
        List of feature data points with technical indicators
    """
    # Generate mock feature data
    features = []
    base_price = 175.0
    
    for i in range(30):
        date = (datetime.now() - timedelta(days=30-i)).strftime("%Y-%m-%d")
        price = base_price + random.uniform(-10, 10)
        
        features.append({
            "ticker": symbol,
            "date": date,
            "close": price,
            "open": price + random.uniform(-2, 2),
            "high": price + random.uniform(0, 3),
            "low": price - random.uniform(0, 3),
            "volume": random.randint(50000000, 150000000),
            "return": random.uniform(-0.03, 0.03),
            "rsi": random.uniform(30, 70),
            "macd": random.uniform(-2, 2),
            "macd_signal": random.uniform(-2, 2),
            "macd_diff": random.uniform(-1, 1),
            "sma_10": price + random.uniform(-5, 5),
            "sma_30": price + random.uniform(-8, 8),
            "sma_50": price + random.uniform(-10, 10),
            "volatility_10": random.uniform(0.01, 0.03),
            "volatility_30": random.uniform(0.015, 0.035),
            "momentum_score": random.uniform(-1, 1),
            "regime": random.choice([0, 1, 2]),
            "bb_upper": price + random.uniform(5, 10),
            "bb_middle": price,
            "bb_lower": price - random.uniform(5, 10),
            "atr": random.uniform(2, 5)
        })
    
    return features


@router.get("/backtest/{strategy}")
async def get_backtest_results(strategy: str, ticker: str = "AAPL"):
    """
    Get backtesting results for a strategy.
    
    Args:
        strategy: Strategy name (e.g., RSI_Strategy, MACD_Strategy)
        ticker: Stock ticker symbol
        
    Returns:
        Backtest results with performance metrics and equity curve
    """
    # Generate mock backtest data
    initial_capital = 10000
    final_value = initial_capital * random.uniform(0.9, 1.3)
    total_return = (final_value - initial_capital) / initial_capital
    
    # Generate equity curve
    equity_curve = []
    current_value = initial_capital
    
    for i in range(100):
        date = (datetime.now() - timedelta(days=100-i)).strftime("%Y-%m-%d")
        current_value *= (1 + random.uniform(-0.02, 0.02))
        equity_curve.append({
            "date": date,
            "value": current_value
        })
    
    return {
        "strategy": strategy,
        "ticker": ticker,
        "initial_capital": initial_capital,
        "final_value": final_value,
        "total_return": total_return,
        "sharpe_ratio": random.uniform(0.5, 2.5),
        "max_drawdown": random.uniform(-0.3, -0.05),
        "win_rate": random.uniform(0.45, 0.65),
        "num_trades": random.randint(20, 100),
        "equity_curve": equity_curve
    }


@router.get("/insights")
async def get_insights():
    """
    Get AI-powered market insights.
    
    Returns:
        List of insights with warnings, opportunities, and market updates
    """
    insights = [
        {
            "id": "1",
            "type": "warning",
            "title": "High Volatility Detected",
            "description": "Market volatility has increased by 25% in the last 3 days. Consider reducing position sizes.",
            "timestamp": datetime.now().isoformat(),
            "ticker": "SPY"
        },
        {
            "id": "2",
            "type": "success",
            "title": "Strong Momentum Signal",
            "description": "AAPL showing strong bullish momentum with RSI at 45 and positive MACD crossover.",
            "timestamp": (datetime.now() - timedelta(hours=2)).isoformat(),
            "ticker": "AAPL"
        },
        {
            "id": "3",
            "type": "info",
            "title": "Market Regime Change",
            "description": "Market has transitioned from Bull to Sideways regime. Expect range-bound trading.",
            "timestamp": (datetime.now() - timedelta(hours=5)).isoformat()
        },
        {
            "id": "4",
            "type": "warning",
            "title": "Overbought Conditions",
            "description": "TSLA RSI at 78 indicates overbought conditions. Potential pullback ahead.",
            "timestamp": (datetime.now() - timedelta(hours=8)).isoformat(),
            "ticker": "TSLA"
        },
        {
            "id": "5",
            "type": "success",
            "title": "Breakout Opportunity",
            "description": "GOOGL breaking above 50-day SMA with strong volume. Potential upside momentum.",
            "timestamp": (datetime.now() - timedelta(days=1)).isoformat(),
            "ticker": "GOOGL"
        }
    ]
    
    return insights

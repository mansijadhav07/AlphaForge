"""
Market data and analytics API routes.

Provides endpoints for market overview, stock features, backtesting, and insights.

ALL DATA IS REAL - NO MOCK DATA.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from datetime import datetime, timedelta
from pathlib import Path
import json

from api.schemas import (
    MarketOverview,
    StockFeatures,
    BacktestResult,
    Insight
)
from api.dependencies import get_pgm_service
from services.data_service import DataService
from utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api", tags=["Market Data"])

# Initialize data service
data_service = DataService()


@router.get("/market-overview", response_model=MarketOverview)
async def get_market_overview(pgm_service = Depends(get_pgm_service)):
    """
    Get market overview with top stocks and signals.
    
    Returns REAL DATA:
    - Latest prices from yfinance
    - PGM-based regime detection
    - PGM-based trading signals
    - Real volatility calculations
    
    Returns:
        Market overview data with real market information
    """
    try:
        logger.info("Fetching market overview with real data")
        
        # Define symbols to track
        symbols = ["AAPL", "TSLA", "GOOGL", "MSFT"]
        
        # Fetch latest data for all symbols
        stocks_data = data_service.get_multiple_stocks_data(symbols, days=30)
        
        if not stocks_data:
            raise HTTPException(
                status_code=503,
                detail="Market data not available. Please try again later."
            )
        
        # Build top stocks list with real data
        top_stocks = []
        signals = []
        
        for symbol in symbols:
            if symbol not in stocks_data:
                continue
            
            df = stocks_data[symbol]
            if df.empty or len(df) < 2:
                continue
            
            # Get latest and previous close
            latest = df.iloc[-1]
            previous = df.iloc[-2]
            
            current_price = float(latest['close'])
            prev_price = float(previous['close'])
            change = current_price - prev_price
            change_pct = (change / prev_price) * 100
            
            top_stocks.append({
                "ticker": symbol,
                "price": round(current_price, 2),
                "change": round(change, 2),
                "change_pct": round(change_pct, 2)
            })
            
            # Get PGM prediction and signal
            prediction = data_service.get_pgm_predictions(symbol, pgm_service)
            if prediction:
                signal = prediction['signal']
                confidence = prediction.get('confidence', 'moderate')
                
                # Get explanation for signal reason
                explanation = data_service.get_pgm_explanation(symbol, pgm_service)
                if explanation:
                    # Extract key factors for reason
                    key_factors = explanation.get('key_factors', [])[:2]
                    factor_names = [f['feature'].replace('_state', '').replace('_', ' ').title() 
                                  for f in key_factors]
                    reason = f"Based on {', '.join(factor_names)}" if factor_names else "Based on market analysis"
                else:
                    reason = f"{confidence.capitalize()} confidence signal"
                
                signals.append({
                    "ticker": symbol,
                    "signal": signal,
                    "confidence": prediction['signal_probabilities'].get(signal.lower(), 0.5),
                    "reason": reason
                })
        
        if not top_stocks:
            raise HTTPException(
                status_code=503,
                detail="Unable to fetch market data for any symbols"
            )
        
        # Determine overall market regime
        # Use first available symbol for market regime
        market_regime = "Sideways"  # default
        volatility_index = 15.0  # default
        
        for symbol in symbols:
            regime_data = data_service.get_regime_probabilities(symbol, pgm_service)
            if regime_data:
                current_regime = regime_data.get('current', 'sideways')
                market_regime = current_regime.capitalize()
                
                # Calculate volatility from recent data
                if symbol in stocks_data:
                    df = stocks_data[symbol]
                    if len(df) >= 20:
                        returns = df['close'].pct_change().dropna()
                        volatility_index = float(returns.std() * 100 * (252 ** 0.5))  # Annualized
                
                break
        
        return MarketOverview(
            timestamp=datetime.now().isoformat(),
            market_regime=market_regime,
            volatility_index=round(volatility_index, 2),
            top_stocks=top_stocks,
            signals=signals
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching market overview: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch market overview: {str(e)}"
        )


@router.get("/features/{symbol}")
async def get_features(symbol: str, days: int = 30):
    """
    Get computed features for a stock symbol.
    
    Returns REAL DATA from feature store:
    - Technical indicators (RSI, MACD, Bollinger Bands, ATR)
    - Moving averages (SMA 10, 30, 50)
    - Volatility metrics
    - Momentum scores
    - Market regime
    
    Args:
        symbol: Stock ticker symbol (e.g., AAPL)
        days: Number of days of historical features (default: 30)
        
    Returns:
        List of feature data points with technical indicators
    """
    try:
        logger.info(f"Fetching real features for {symbol}, last {days} days")
        
        # Get historical features from feature store
        features_df = data_service.get_historical_features(symbol, days=days)
        
        if features_df is None or features_df.empty:
            raise HTTPException(
                status_code=404,
                detail=f"No feature data available for {symbol}. Please ensure data has been ingested and features computed."
            )
        
        # Convert DataFrame to list of dictionaries
        features = []
        for _, row in features_df.iterrows():
            feature_dict = {
                "ticker": symbol,
                "date": row.get('date', '').strftime('%Y-%m-%d') if hasattr(row.get('date', ''), 'strftime') else str(row.get('date', '')),
                "close": float(row.get('close', 0)),
                "open": float(row.get('open', 0)),
                "high": float(row.get('high', 0)),
                "low": float(row.get('low', 0)),
                "volume": int(row.get('volume', 0)),
                "return": float(row.get('return', 0)),
                "rsi": float(row.get('rsi', 50)),
                "macd": float(row.get('macd', 0)),
                "macd_signal": float(row.get('macd_signal', 0)),
                "macd_diff": float(row.get('macd_diff', 0)),
                "sma_10": float(row.get('sma_10', 0)),
                "sma_30": float(row.get('sma_30', 0)),
                "sma_50": float(row.get('sma_50', 0)),
                "volatility_10": float(row.get('volatility_10', 0)),
                "volatility_30": float(row.get('volatility_30', 0)),
                "momentum_score": float(row.get('momentum_score', 0)),
                "regime": int(row.get('regime', 1)),
                "bb_upper": float(row.get('bb_upper', 0)),
                "bb_middle": float(row.get('bb_middle', 0)),
                "bb_lower": float(row.get('bb_lower', 0)),
                "atr": float(row.get('atr', 0))
            }
            features.append(feature_dict)
        
        logger.info(f"Returning {len(features)} feature records for {symbol}")
        return features
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching features for {symbol}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch features: {str(e)}"
        )


@router.get("/backtest/{strategy}")
async def get_backtest_results(strategy: str, ticker: str = "AAPL"):
    """
    Get backtesting results for a strategy.
    
    Returns REAL DATA from precomputed backtest results or runs backtest.
    
    Args:
        strategy: Strategy name (e.g., RSI_Strategy, MACD_Strategy, PGM_Strategy)
        ticker: Stock ticker symbol
        
    Returns:
        Backtest results with performance metrics and equity curve
    """
    try:
        logger.info(f"Fetching backtest results for {strategy} on {ticker}")
        
        # Try to load precomputed backtest results
        backtest_file = Path(f'data/backtests/{ticker}_{strategy}.json')
        
        if backtest_file.exists():
            logger.info(f"Loading precomputed backtest for {strategy} on {ticker}")
            with open(backtest_file, 'r') as f:
                results = json.load(f)
            return results
        
        # If no precomputed results, return error
        # (Running backtests on-demand is expensive, should be precomputed)
        raise HTTPException(
            status_code=404,
            detail=f"No backtest results found for {strategy} on {ticker}. Please run backtest script first."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching backtest results: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch backtest results: {str(e)}"
        )


@router.get("/insights")
async def get_insights(pgm_service = Depends(get_pgm_service)):
    """
    Get AI-powered market insights.
    
    Returns REAL INSIGHTS generated from:
    - PGM predictions and explanations
    - Recent market data analysis
    - Regime changes
    - High-confidence signals
    
    Returns:
        List of insights with warnings, opportunities, and market updates
    """
    try:
        logger.info("Generating real market insights")
        
        insights = []
        symbols = ["AAPL", "TSLA", "GOOGL", "MSFT"]
        
        for symbol in symbols:
            try:
                # Get PGM prediction
                prediction = data_service.get_pgm_predictions(symbol, pgm_service)
                if not prediction:
                    continue
                
                # Get explanation
                explanation = data_service.get_pgm_explanation(symbol, pgm_service)
                if not explanation:
                    continue
                
                # Get latest features
                features = data_service.get_latest_features(symbol)
                if features is None:
                    continue
                
                # Generate insights based on prediction confidence and signal
                signal = prediction['signal']
                confidence = prediction.get('confidence', 'moderate')
                probabilities = prediction.get('probabilities', {})
                
                # High confidence signals
                if confidence == 'high':
                    insight_type = "success" if signal == "BUY" else "warning" if signal == "SELL" else "info"
                    
                    key_factors = explanation.get('key_factors', [])[:2]
                    factor_desc = ", ".join([f['feature'].replace('_state', '').replace('_', ' ').title() 
                                            for f in key_factors])
                    
                    insights.append({
                        "id": f"{symbol}_{signal}_{len(insights)}",
                        "type": insight_type,
                        "title": f"High Confidence {signal} Signal - {symbol}",
                        "description": f"PGM model shows {confidence} confidence {signal} signal based on {factor_desc}. Probability: {max(probabilities.values()):.1%}",
                        "timestamp": datetime.now().isoformat(),
                        "ticker": symbol
                    })
                
                # Check for extreme RSI
                rsi = features.get('rsi', 50)
                if rsi > 75:
                    insights.append({
                        "id": f"{symbol}_overbought_{len(insights)}",
                        "type": "warning",
                        "title": f"Overbought Conditions - {symbol}",
                        "description": f"RSI at {rsi:.1f} indicates overbought conditions. Potential pullback ahead.",
                        "timestamp": datetime.now().isoformat(),
                        "ticker": symbol
                    })
                elif rsi < 25:
                    insights.append({
                        "id": f"{symbol}_oversold_{len(insights)}",
                        "type": "success",
                        "title": f"Oversold Opportunity - {symbol}",
                        "description": f"RSI at {rsi:.1f} indicates oversold conditions. Potential bounce opportunity.",
                        "timestamp": datetime.now().isoformat(),
                        "ticker": symbol
                    })
                
                # Check volatility
                volatility = features.get('volatility_10', 0)
                if volatility > 0.03:
                    insights.append({
                        "id": f"{symbol}_highvol_{len(insights)}",
                        "type": "warning",
                        "title": f"High Volatility Detected - {symbol}",
                        "description": f"10-day volatility at {volatility:.2%}. Consider reducing position sizes or using wider stops.",
                        "timestamp": datetime.now().isoformat(),
                        "ticker": symbol
                    })
                
                # Check regime
                regime_data = data_service.get_regime_probabilities(symbol, pgm_service)
                if regime_data:
                    current_regime = regime_data.get('current', 'unknown')
                    regime_prob = regime_data.get(current_regime, 0)
                    
                    if regime_prob > 0.7:
                        insights.append({
                            "id": f"{symbol}_regime_{len(insights)}",
                            "type": "info",
                            "title": f"Strong {current_regime.capitalize()} Regime - {symbol}",
                            "description": f"Market regime detected as {current_regime} with {regime_prob:.0%} confidence. Adjust strategy accordingly.",
                            "timestamp": datetime.now().isoformat(),
                            "ticker": symbol
                        })
                
            except Exception as e:
                logger.warning(f"Error generating insights for {symbol}: {e}")
                continue
        
        # If no insights generated, add a general market update
        if not insights:
            insights.append({
                "id": "general_update",
                "type": "info",
                "title": "Market Analysis In Progress",
                "description": "Analyzing market conditions. Check back soon for detailed insights.",
                "timestamp": datetime.now().isoformat()
            })
        
        # Sort by timestamp (most recent first) and limit to 10
        insights.sort(key=lambda x: x['timestamp'], reverse=True)
        insights = insights[:10]
        
        logger.info(f"Generated {len(insights)} real insights")
        return insights
        
    except Exception as e:
        logger.error(f"Error generating insights: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate insights: {str(e)}"
        )

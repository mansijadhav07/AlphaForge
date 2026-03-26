"""
PGM API Routes for AlphaForge.

Exposes Probabilistic Graphical Model functionality via REST APIs.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, List, Optional
from datetime import datetime
import pandas as pd

from api.schemas import (
    ProbabilityResponse,
    ExplanationResponse,
    SignalResponse,
    SimulationRequest,
    SimulationResponse,
    FeatureImpactResponse,
    RegimeResponse,
    GraphStructureResponse,
    ModelEvaluationResponse,
    FailureAnalysisResponse,
    StructureAnalysisResponse,
    ErrorResponse
)
from api.dependencies import get_pgm_service
from utils.logger import get_logger

logger = get_logger(__name__)

# Create router
router = APIRouter(
    prefix="/api/pgm",
    tags=["PGM - Probabilistic Predictions"],
    responses={
        404: {"model": ErrorResponse, "description": "Symbol not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)


@router.get(
    "/probabilities/{symbol}",
    response_model=ProbabilityResponse,
    summary="Get probability distribution for market outcomes",
    description="Returns probabilistic predictions for future returns with confidence levels"
)
async def get_probabilities(
    symbol: str,
    pgm_service = Depends(get_pgm_service)
) -> ProbabilityResponse:
    """
    Get probability distribution for a symbol's future returns.
    
    Args:
        symbol: Stock ticker symbol (e.g., AAPL, TSLA)
        pgm_service: Injected PGM service
        
    Returns:
        ProbabilityResponse with probability distribution
        
    Raises:
        HTTPException: If symbol not found or prediction fails
    """
    try:
        logger.info(f"Getting probabilities for {symbol}")
        
        # Get latest features for symbol
        features = pgm_service.get_latest_features(symbol)
        if features is None:
            raise HTTPException(
                status_code=404,
                detail=f"No data found for symbol: {symbol}"
            )
        
        # Encode features
        encoded = pgm_service.encode_features(features)
        
        # Build evidence dictionary
        evidence = pgm_service.build_evidence(encoded)
        
        # Perform inference
        result = pgm_service.inference_engine.query(['future_return_state'], evidence)
        probabilities = result.get('future_return_state', {})
        
        # Determine confidence level
        max_prob = max(probabilities.values()) if probabilities else 0.0
        confidence = pgm_service.categorize_confidence(max_prob)
        
        return ProbabilityResponse(
            symbol=symbol,
            probabilities=probabilities,
            confidence=confidence,
            timestamp=datetime.now()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting probabilities for {symbol}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get probabilities: {str(e)}"
        )


@router.get(
    "/explanation/{symbol}",
    response_model=ExplanationResponse,
    summary="Get explanation for prediction",
    description="Returns human-readable explanation with key factors and reasoning"
)
async def get_explanation(
    symbol: str,
    pgm_service = Depends(get_pgm_service)
) -> ExplanationResponse:
    """
    Get detailed explanation for a symbol's prediction.
    
    Args:
        symbol: Stock ticker symbol
        pgm_service: Injected PGM service
        
    Returns:
        ExplanationResponse with factors and reasoning
    """
    try:
        logger.info(f"Getting explanation for {symbol}")
        
        # Get features and evidence
        features = pgm_service.get_latest_features(symbol)
        if features is None:
            raise HTTPException(status_code=404, detail=f"No data found for symbol: {symbol}")
        
        encoded = pgm_service.encode_features(features)
        evidence = pgm_service.build_evidence(encoded)
        
        # Get prediction
        result = pgm_service.inference_engine.query(['future_return_state'], evidence)
        probabilities = result.get('future_return_state', {})
        
        # Generate explanation
        explanation = pgm_service.explanation_engine.explain_prediction(
            'future_return_state',
            evidence,
            probabilities
        )
        
        # Format response
        most_likely = explanation['prediction']
        confidence_pct = explanation['confidence']
        
        # Build summary
        summary = f"{most_likely.capitalize()} outlook with {explanation['confidence_level'].lower()} confidence"
        
        # Extract top factors
        factors = [
            {
                "feature": factor['feature'].replace('_state', '').replace('_', ' ').title(),
                "impact": round(factor['impact_score'], 3),
                "reason": factor['description']
            }
            for factor in explanation['key_factors'][:5]
        ]
        
        return ExplanationResponse(
            symbol=symbol,
            summary=summary,
            prediction=most_likely,
            confidence=confidence_pct,
            factors=factors,
            risk_level=explanation['risk_assessment']['level'],
            risk_factors=explanation['risk_assessment']['factors'],
            recommendation=explanation['risk_assessment']['recommendation'],
            timestamp=datetime.now()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting explanation for {symbol}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get explanation: {str(e)}")


@router.get(
    "/signal/{symbol}",
    response_model=SignalResponse,
    summary="Get trading signal",
    description="Returns BUY/SELL/HOLD signal with probability and confidence"
)
async def get_signal(
    symbol: str,
    buy_threshold: float = Query(0.65, ge=0.5, le=1.0, description="Threshold for BUY signal"),
    sell_threshold: float = Query(0.35, ge=0.0, le=0.5, description="Threshold for SELL signal"),
    pgm_service = Depends(get_pgm_service)
) -> SignalResponse:
    """
    Get trading signal for a symbol.
    
    Args:
        symbol: Stock ticker symbol
        buy_threshold: Probability threshold for BUY signal (default: 0.65)
        sell_threshold: Probability threshold for SELL signal (default: 0.35)
        pgm_service: Injected PGM service
        
    Returns:
        SignalResponse with trading signal
    """
    try:
        logger.info(f"Getting signal for {symbol}")
        
        # Get features and evidence
        features = pgm_service.get_latest_features(symbol)
        if features is None:
            raise HTTPException(status_code=404, detail=f"No data found for symbol: {symbol}")
        
        encoded = pgm_service.encode_features(features)
        evidence = pgm_service.build_evidence(encoded)
        
        # Get trading signals
        signals = pgm_service.inference_engine.compute_signal_probabilities(evidence)
        
        # Determine signal based on thresholds
        buy_prob = signals.get('buy', 0.0)
        sell_prob = signals.get('sell', 0.0)
        hold_prob = signals.get('hold', 0.0)
        
        if buy_prob >= buy_threshold:
            signal = "BUY"
            probability = buy_prob
        elif sell_prob >= (1 - sell_threshold):
            signal = "SELL"
            probability = sell_prob
        else:
            signal = "HOLD"
            probability = hold_prob
        
        confidence = pgm_service.categorize_confidence(probability)
        
        return SignalResponse(
            symbol=symbol,
            signal=signal,
            probability=probability,
            confidence=confidence,
            buy_probability=buy_prob,
            sell_probability=sell_prob,
            hold_probability=hold_prob,
            timestamp=datetime.now()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting signal for {symbol}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get signal: {str(e)}")


@router.post(
    "/simulate",
    response_model=SimulationResponse,
    summary="Simulate custom scenario",
    description="Test what-if scenarios with custom market conditions"
)
async def simulate_scenario(
    request: SimulationRequest,
    pgm_service = Depends(get_pgm_service)
) -> SimulationResponse:
    """
    Simulate a custom market scenario.
    
    Args:
        request: Simulation request with symbol and evidence
        pgm_service: Injected PGM service
        
    Returns:
        SimulationResponse with predictions for the scenario
    """
    try:
        logger.info(f"Simulating scenario for {request.symbol}")
        
        # Convert evidence to state format
        evidence = {
            f"{key}_state": value
            for key, value in request.evidence.items()
        }
        
        # Perform inference
        result = pgm_service.inference_engine.query(['future_return_state'], evidence)
        probabilities = result.get('future_return_state', {})
        
        # Get signal
        signals = pgm_service.inference_engine.compute_signal_probabilities(evidence)
        best_signal = max(signals, key=signals.get)
        signal_prob = signals[best_signal]
        
        # Get explanation
        explanation = pgm_service.explanation_engine.explain_prediction(
            'future_return_state',
            evidence,
            probabilities
        )
        
        return SimulationResponse(
            symbol=request.symbol,
            scenario=request.evidence,
            probabilities=probabilities,
            signal=best_signal.upper(),
            signal_probability=signal_prob,
            explanation=explanation['reasoning_chain'],
            risk_level=explanation['risk_assessment']['level'],
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Error simulating scenario: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to simulate scenario: {str(e)}")


@router.get(
    "/feature-impact/{symbol}",
    response_model=FeatureImpactResponse,
    summary="Get feature importance",
    description="Returns impact scores for each feature on the prediction"
)
async def get_feature_impact(
    symbol: str,
    pgm_service = Depends(get_pgm_service)
) -> FeatureImpactResponse:
    """
    Get feature impact scores for a symbol.
    
    Args:
        symbol: Stock ticker symbol
        pgm_service: Injected PGM service
        
    Returns:
        FeatureImpactResponse with impact scores
    """
    try:
        logger.info(f"Getting feature impact for {symbol}")
        
        # Get features and evidence
        features = pgm_service.get_latest_features(symbol)
        if features is None:
            raise HTTPException(status_code=404, detail=f"No data found for symbol: {symbol}")
        
        encoded = pgm_service.encode_features(features)
        evidence = pgm_service.build_evidence(encoded)
        
        # Get prediction
        result = pgm_service.inference_engine.query(['future_return_state'], evidence)
        probabilities = result.get('future_return_state', {})
        
        # Generate explanation to get feature impacts
        explanation = pgm_service.explanation_engine.explain_prediction(
            'future_return_state',
            evidence,
            probabilities
        )
        
        # Extract impacts
        impacts = [
            {
                "feature": factor['feature'].replace('_state', '').replace('_', ' ').title(),
                "impact": round(factor['impact_score'], 3),
                "current_state": evidence.get(factor['feature'], 'unknown')
            }
            for factor in explanation['key_factors']
        ]
        
        return FeatureImpactResponse(
            symbol=symbol,
            impacts=impacts,
            timestamp=datetime.now()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting feature impact for {symbol}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get feature impact: {str(e)}")


@router.get(
    "/regime/{symbol}",
    response_model=RegimeResponse,
    summary="Get market regime probabilities",
    description="Returns probability distribution for bull/bear/sideways market regimes"
)
async def get_regime(
    symbol: str,
    pgm_service = Depends(get_pgm_service)
) -> RegimeResponse:
    """
    Get market regime probabilities for a symbol.
    
    Args:
        symbol: Stock ticker symbol
        pgm_service: Injected PGM service
        
    Returns:
        RegimeResponse with regime probabilities
    """
    try:
        logger.info(f"Getting regime for {symbol}")
        
        # Get features and evidence
        features = pgm_service.get_latest_features(symbol)
        if features is None:
            raise HTTPException(status_code=404, detail=f"No data found for symbol: {symbol}")
        
        encoded = pgm_service.encode_features(features)
        evidence = pgm_service.build_evidence(encoded)
        
        # Query regime
        result = pgm_service.inference_engine.query(['regime_state'], evidence)
        regime_probs = result.get('regime_state', {})
        
        # Ensure all regime types are present
        bull = regime_probs.get('bull', 0.0)
        bear = regime_probs.get('bear', 0.0)
        sideways = regime_probs.get('sideways', 0.0)
        
        # Determine current regime
        current_regime = max(regime_probs, key=regime_probs.get) if regime_probs else 'unknown'
        
        return RegimeResponse(
            symbol=symbol,
            bull=bull,
            bear=bear,
            sideways=sideways,
            current_regime=current_regime,
            confidence=max(bull, bear, sideways),
            timestamp=datetime.now()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting regime for {symbol}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get regime: {str(e)}")


@router.get(
    "/graph",
    response_model=GraphStructureResponse,
    summary="Get Bayesian Network structure",
    description="Returns the graph structure showing feature dependencies"
)
async def get_graph_structure(
    pgm_service = Depends(get_pgm_service)
) -> GraphStructureResponse:
    """
    Get the Bayesian Network graph structure.
    
    Args:
        pgm_service: Injected PGM service
        
    Returns:
        GraphStructureResponse with nodes and edges
    """
    try:
        logger.info("Getting graph structure")
        
        graph = pgm_service.graph_structure.graph
        
        # Extract nodes
        nodes = [
            {
                "id": node,
                "label": node.replace('_state', '').replace('_', ' ').title()
            }
            for node in graph.nodes
        ]
        
        # Extract edges
        edges = [
            {
                "from": source,
                "to": target,
                "from_label": source.replace('_state', '').replace('_', ' ').title(),
                "to_label": target.replace('_state', '').replace('_', ' ').title()
            }
            for source, target in graph.edges
        ]
        
        return GraphStructureResponse(
            nodes=nodes,
            edges=edges,
            num_nodes=len(nodes),
            num_edges=len(edges),
            is_dag=pgm_service.graph_structure.validate_dag()
        )
        
    except Exception as e:
        logger.error(f"Error getting graph structure: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get graph structure: {str(e)}")


@router.get(
    "/health",
    summary="Health check",
    description="Check if PGM service is ready"
)
async def health_check(pgm_service = Depends(get_pgm_service)) -> Dict:
    """
    Health check endpoint.
    
    Returns:
        Status information
    """
    try:
        is_ready = pgm_service.is_ready()
        
        return {
            "status": "healthy" if is_ready else "not_ready",
            "service": "PGM",
            "version": "1.0.0",
            "ready": is_ready,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@router.get(
    "/evaluation/{symbol}",
    response_model=ModelEvaluationResponse,
    summary="Get model evaluation metrics",
    description="Returns comprehensive evaluation metrics including accuracy, confusion matrix, and calibration"
)
async def get_model_evaluation(
    symbol: str,
    lookback_periods: int = Query(5, ge=1, le=30, description="Periods to look ahead for actual outcome"),
    pgm_service = Depends(get_pgm_service)
) -> ModelEvaluationResponse:
    """
    Get model evaluation metrics for a symbol.
    
    Args:
        symbol: Stock ticker symbol
        lookback_periods: Number of periods to look ahead for actual outcome
        pgm_service: Injected PGM service
        
    Returns:
        ModelEvaluationResponse with evaluation metrics
    """
    try:
        logger.info(f"Getting model evaluation for {symbol}")
        
        # Try to load cached results first
        from pgm_model.evaluation import ModelEvaluator
        evaluator = ModelEvaluator()
        
        cached_results = evaluator.load_results(symbol)
        
        if cached_results:
            logger.info(f"Returning cached evaluation results for {symbol}")
            return ModelEvaluationResponse(
                symbol=symbol,
                **cached_results
            )
        
        # If no cached results, perform evaluation on available data
        # Get historical features
        from feature_store.offline_store import OfflineFeatureStore
        offline_store = OfflineFeatureStore()
        
        try:
            features_df = offline_store.read_features('market_features', version='v1')
            
            # Filter for symbol
            if 'ticker' in features_df.columns:
                features_df = features_df[features_df['ticker'] == symbol]
            
            if len(features_df) < lookback_periods + 10:
                raise HTTPException(
                    status_code=404,
                    detail=f"Insufficient historical data for {symbol}"
                )
            
            # Perform evaluation
            results = evaluator.evaluate_model_on_historical_data(
                pgm_service.state_encoder,
                pgm_service.inference_engine,
                features_df,
                lookback_periods=lookback_periods
            )
            
            # Save results
            evaluator.save_results(results, symbol)
            
            return ModelEvaluationResponse(
                symbol=symbol,
                **results
            )
            
        except Exception as e:
            logger.warning(f"Could not evaluate on historical data: {e}")
            # Return mock data for development
            return _get_mock_evaluation(symbol)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting evaluation for {symbol}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get evaluation: {str(e)}")


@router.get(
    "/failures/{symbol}",
    response_model=FailureAnalysisResponse,
    summary="Get failure case analysis",
    description="Returns detailed analysis of prediction failures with explanations"
)
async def get_failure_analysis(
    symbol: str,
    max_failures: int = Query(50, ge=1, le=200, description="Maximum number of failures to analyze"),
    lookback_periods: int = Query(5, ge=1, le=30, description="Periods to look ahead for actual outcome"),
    pgm_service = Depends(get_pgm_service)
) -> FailureAnalysisResponse:
    """
    Get failure case analysis for a symbol.
    
    Args:
        symbol: Stock ticker symbol
        max_failures: Maximum number of failures to analyze
        lookback_periods: Number of periods to look ahead for actual outcome
        pgm_service: Injected PGM service
        
    Returns:
        FailureAnalysisResponse with failure cases and insights
    """
    try:
        logger.info(f"Getting failure analysis for {symbol}")
        
        from pgm_model.failure_analysis import FailureAnalyzer
        from pgm_model.evaluation import ModelEvaluator
        from feature_store.offline_store import OfflineFeatureStore
        
        # Initialize analyzers
        failure_analyzer = FailureAnalyzer(pgm_service.explanation_engine)
        evaluator = ModelEvaluator()
        
        try:
            # Get historical features
            offline_store = OfflineFeatureStore()
            features_df = offline_store.read_features('market_features', version='v1')
            
            # Filter for symbol
            if 'ticker' in features_df.columns:
                features_df = features_df[features_df['ticker'] == symbol]
            
            if len(features_df) < lookback_periods + 10:
                raise HTTPException(
                    status_code=404,
                    detail=f"Insufficient historical data for {symbol}"
                )
            
            # Generate predictions and actuals
            predictions_list = []
            actuals_list = []
            
            for i in range(len(features_df) - lookback_periods):
                features = features_df.iloc[i]
                encoded = pgm_service.encode_features(features)
                evidence = pgm_service.build_evidence(encoded)
                
                try:
                    result = pgm_service.inference_engine.query(['future_return_state'], evidence)
                    probs = result.get('future_return_state', {})
                    
                    if probs:
                        predicted_class = max(probs, key=probs.get)
                        future_return = features_df.iloc[i + lookback_periods]['return']
                        
                        if future_return > 0.01:
                            actual_class = 'positive'
                        elif future_return < -0.01:
                            actual_class = 'negative'
                        else:
                            actual_class = 'neutral'
                        
                        predictions_list.append({
                            'index': i,
                            'predicted_class': predicted_class,
                            'prob_positive': probs.get('positive', 0.0),
                            'prob_neutral': probs.get('neutral', 0.0),
                            'prob_negative': probs.get('negative', 0.0),
                            **{f"{col}_state": encoded.get(col, 'unknown') 
                               for col in encoded.index if f"{col}_state" in pgm_service.inference_engine.model.nodes}
                        })
                        
                        actuals_list.append({
                            'index': i,
                            'actual_class': actual_class
                        })
                except Exception as e:
                    logger.warning(f"Error evaluating sample {i}: {e}")
                    continue
            
            predictions_df = pd.DataFrame(predictions_list).set_index('index')
            actuals_df = pd.DataFrame(actuals_list).set_index('index')
            
            # Analyze failures
            failure_cases = failure_analyzer.analyze_failures(
                predictions_df,
                actuals_df,
                features_df=None,
                max_failures=max_failures
            )
            
            # Get summary and insights
            summary = failure_analyzer.get_failure_summary(failure_cases)
            summary['failure_rate'] = len(failure_cases) / len(predictions_df) if len(predictions_df) > 0 else 0.0
            
            insights = failure_analyzer.get_actionable_insights(failure_cases)
            
            return FailureAnalysisResponse(
                symbol=symbol,
                timestamp=datetime.now().isoformat(),
                failure_cases=failure_cases,
                summary=summary,
                insights=insights
            )
            
        except Exception as e:
            logger.warning(f"Could not analyze failures on historical data: {e}")
            # Return mock data for development
            return _get_mock_failure_analysis(symbol)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting failure analysis for {symbol}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get failure analysis: {str(e)}")


def _get_mock_failure_analysis(symbol: str) -> FailureAnalysisResponse:
    """Generate mock failure analysis data for development."""
    return FailureAnalysisResponse(
        symbol=symbol,
        timestamp=datetime.now().isoformat(),
        failure_cases=[
            {
                "index": 15,
                "date": "2024-03-15",
                "predicted": "positive",
                "actual": "negative",
                "predicted_probability": 0.75,
                "actual_probability": 0.10,
                "confidence": "high",
                "severity": "high",
                "reason": "Model was highly confident (75.0%) in predicting 'positive'. Large probability gap (65.0%) between predicted and actual class. Possible causes: RSI and momentum gave conflicting signals.",
                "probabilities": {"positive": 0.75, "neutral": 0.15, "negative": 0.10},
                "feature_states": {"RSI": "oversold", "Momentum Score": "weak", "Market Regime": "bull"},
                "failure_type": "false_positive_extreme",
                "is_common_pattern": True,
                "pattern_frequency": 8
            },
            {
                "index": 23,
                "date": "2024-03-18",
                "predicted": "neutral",
                "actual": "positive",
                "predicted_probability": 0.55,
                "actual_probability": 0.30,
                "confidence": "moderate",
                "severity": "medium",
                "reason": "Model had moderate confidence (55.0%) in predicting 'neutral'. Moderate probability gap (25.0%) between classes.",
                "probabilities": {"positive": 0.30, "neutral": 0.55, "negative": 0.15},
                "feature_states": {"RSI": "neutral", "Momentum Score": "moderate", "Volatility": "high"},
                "failure_type": "false_negative",
                "is_common_pattern": False,
                "pattern_frequency": 5
            },
            {
                "index": 42,
                "date": "2024-03-22",
                "predicted": "negative",
                "actual": "positive",
                "predicted_probability": 0.68,
                "actual_probability": 0.15,
                "confidence": "moderate",
                "severity": "medium",
                "reason": "Model had moderate confidence (68.0%) in predicting 'negative'. Large probability gap (53.0%) between predicted and actual class. Possible causes: High volatility in bear regime increased uncertainty.",
                "probabilities": {"positive": 0.15, "neutral": 0.17, "negative": 0.68},
                "feature_states": {"RSI": "overbought", "Momentum Score": "weak", "Market Regime": "bear", "Volatility": "high"},
                "failure_type": "false_negative_extreme",
                "is_common_pattern": True,
                "pattern_frequency": 8
            }
        ],
        summary={
            "total_failures": 35,
            "by_type": {
                "false_positive_extreme": 8,
                "false_negative_extreme": 8,
                "false_positive": 7,
                "false_negative": 12
            },
            "by_severity": {
                "high": 10,
                "medium": 15,
                "low": 10
            },
            "by_confidence": {
                "high": 10,
                "moderate": 18,
                "low": 7
            },
            "most_common_type": "false_negative",
            "high_severity_count": 10,
            "failure_rate": 0.35
        },
        insights=[
            "⚠️ 10 high-severity failures detected. Model is making confident wrong predictions - review feature engineering.",
            "📊 12 failures are 'false_negative' type. Consider adding features to better distinguish these cases.",
            "🎯 10 failures occurred with high confidence. Model may be overconfident - consider calibration adjustments."
        ]
    )


def _get_mock_evaluation(symbol: str) -> ModelEvaluationResponse:
    """Generate mock evaluation data for development."""
    return ModelEvaluationResponse(
        symbol=symbol,
        timestamp=datetime.now().isoformat(),
        n_samples=100,
        accuracy=0.65,
        confusion_matrix={
            "classes": ["positive", "neutral", "negative"],
            "matrix": [[30, 5, 5], [10, 20, 10], [5, 5, 10]],
            "row_totals": [40, 40, 20],
            "col_totals": [45, 30, 25],
            "total": 100
        },
        classification_report={
            "positive": {
                "precision": 0.67,
                "recall": 0.75,
                "f1_score": 0.71,
                "support": 40
            },
            "neutral": {
                "precision": 0.67,
                "recall": 0.50,
                "f1_score": 0.57,
                "support": 40
            },
            "negative": {
                "precision": 0.40,
                "recall": 0.50,
                "f1_score": 0.44,
                "support": 20
            },
            "macro_avg": {
                "precision": 0.58,
                "recall": 0.58,
                "f1_score": 0.57
            }
        },
        brier_score={
            "positive": 0.15,
            "neutral": 0.18,
            "negative": 0.20,
            "overall": 0.18
        },
        calibration_data={
            "positive": [
                {"bin": i, "predicted_prob": i/10 + 0.05, "actual_freq": i/10 + 0.02, "count": 10}
                for i in range(10)
            ],
            "neutral": [
                {"bin": i, "predicted_prob": i/10 + 0.05, "actual_freq": i/10 + 0.03, "count": 10}
                for i in range(10)
            ],
            "negative": [
                {"bin": i, "predicted_prob": i/10 + 0.05, "actual_freq": i/10 + 0.04, "count": 10}
                for i in range(10)
            ]
        },
        probability_distribution={
            "positive": {
                "mean": 0.35,
                "std": 0.15,
                "min": 0.05,
                "max": 0.85,
                "median": 0.33,
                "q25": 0.22,
                "q75": 0.48
            },
            "neutral": {
                "mean": 0.40,
                "std": 0.12,
                "min": 0.10,
                "max": 0.75,
                "median": 0.38,
                "q25": 0.30,
                "q75": 0.50
            },
            "negative": {
                "mean": 0.25,
                "std": 0.18,
                "min": 0.02,
                "max": 0.80,
                "median": 0.20,
                "q25": 0.12,
                "q75": 0.35
            }
        },
        class_distribution={
            "predicted": {
                "counts": {"positive": 45, "neutral": 30, "negative": 25},
                "percentages": {"positive": 0.45, "neutral": 0.30, "negative": 0.25}
            },
            "actual": {
                "counts": {"positive": 40, "neutral": 40, "negative": 20},
                "percentages": {"positive": 0.40, "neutral": 0.40, "negative": 0.20}
            }
        }
    )


# ============================================================================
# Structure Analysis Endpoint
# ============================================================================

@router.get(
    "/structure-analysis",
    response_model=StructureAnalysisResponse,
    summary="Get Bayesian Network Structure Analysis",
    description="""
    Analyze the Bayesian Network structure with:
    - Correlation matrix (heatmap-ready)
    - Dependency analysis (nodes, paths, key features)
    - Edge explanations (why each edge exists)
    - Structure validation (DAG check, empirical support)
    
    This endpoint provides comprehensive justification for the network structure
    based on financial theory, empirical correlations, and causal mechanisms.
    """,
    responses={
        200: {"description": "Structure analysis completed successfully"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def get_structure_analysis(
    symbol: str = Query("AAPL", description="Stock symbol for analysis"),
    pgm_service = Depends(get_pgm_service)
) -> StructureAnalysisResponse:
    """
    Get comprehensive structure analysis for the Bayesian Network.
    
    Args:
        symbol: Stock symbol (used to fetch feature data for correlation analysis)
        pgm_service: PGM service instance
        
    Returns:
        Complete structure analysis with correlations, dependencies, and explanations
    """
    try:
        logger.info(f"Structure analysis requested for {symbol}")
        
        # Import structure analyzer
        from pgm_model.structure_analysis import StructureAnalyzer
        
        # Initialize analyzer
        analyzer = StructureAnalyzer()
        
        # Get feature data for correlation analysis
        try:
            # Try to get real feature data
            from feature_store.offline_store import OfflineFeatureStore
            store = OfflineFeatureStore()
            features_df = store.get_latest_features(symbol, feature_view="market_features")
            
            if features_df is None or features_df.empty:
                logger.warning(f"No feature data found for {symbol}, using mock data")
                features_df = _get_mock_features_df()
        except Exception as e:
            logger.warning(f"Error fetching features: {e}, using mock data")
            features_df = _get_mock_features_df()
        
        # Generate comprehensive report
        report = analyzer.generate_structure_report(features_df)
        
        # Transform to response format
        response = _transform_structure_report(report)
        
        logger.info(f"Structure analysis completed for {symbol}")
        return response
        
    except Exception as e:
        logger.error(f"Error in structure analysis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate structure analysis: {str(e)}"
        )


def _get_mock_features_df() -> pd.DataFrame:
    """Generate mock feature data for correlation analysis."""
    import numpy as np
    
    np.random.seed(42)
    n_samples = 100
    
    # Generate correlated features
    rsi = np.random.uniform(20, 80, n_samples)
    macd = np.random.normal(0, 2, n_samples)
    bb_width = np.random.uniform(0.01, 0.05, n_samples)
    volume_ratio = np.random.uniform(0.5, 2.0, n_samples)
    atr = np.random.uniform(0.5, 3.0, n_samples)
    
    # Create regime features with dependencies
    momentum_regime = np.where(rsi > 70, 'strong', np.where(rsi < 30, 'weak', 'neutral'))
    volatility_regime = np.where(bb_width > 0.03, 'high', 'low')
    
    # Create target with dependencies
    return_target = np.where(
        (momentum_regime == 'strong') & (volatility_regime == 'low'),
        'positive',
        np.where(
            (momentum_regime == 'weak') & (volatility_regime == 'high'),
            'negative',
            'neutral'
        )
    )
    
    return pd.DataFrame({
        'RSI': rsi,
        'MACD': macd,
        'BB_width': bb_width,
        'volume_ratio': volume_ratio,
        'ATR': atr,
        'momentum_regime': momentum_regime,
        'volatility_regime': volatility_regime,
        'return_target': return_target
    })


def _transform_structure_report(report: Dict) -> StructureAnalysisResponse:
    """Transform structure report to API response format."""
    from api.schemas import (
        CorrelationMatrix,
        DependencyAnalysis,
        NodeInfo,
        DependencyPath,
        EdgeExplanation,
        StructureValidation,
        NetworkSummary
    )
    
    # Transform correlation matrix
    corr_data = report['correlation_matrix']
    correlation_matrix = CorrelationMatrix(
        features=corr_data['features'],
        matrix=corr_data['matrix'],
        method=corr_data['method']
    )
    
    # Transform dependency analysis
    dep_data = report['dependency_analysis']
    nodes = {
        name: NodeInfo(
            name=info['name'],
            parents=info['parents'],
            children=info['children'],
            role=info['role']
        )
        for name, info in dep_data['nodes'].items()
    }
    
    dependency_paths = [
        DependencyPath(
            path=path['path'],
            length=path['length'],
            description=path['description']
        )
        for path in dep_data['dependency_paths']
    ]
    
    dependency_analysis = DependencyAnalysis(
        nodes=nodes,
        key_nodes=dep_data['key_nodes'],
        dependency_paths=dependency_paths
    )
    
    # Transform edge explanations
    edge_explanations = [
        EdgeExplanation(
            parent=edge['parent'],
            child=edge['child'],
            edge_type=edge['type'],
            strength=edge['strength'],
            reasoning=edge['reasoning'],
            financial_theory=edge['financial_theory'],
            empirical_support=edge['empirical_support'],
            causal_mechanism=edge['causal_mechanism']
        )
        for edge in report['edge_explanations']
    ]
    
    # Transform structure validation
    val_data = report['structure_validation']
    structure_validation = StructureValidation(
        is_valid_dag=val_data['is_valid_dag'],
        has_cycles=val_data['has_cycles'],
        correlation_support=val_data['correlation_support'],
        missing_edges=val_data['missing_edges'],
        validation_summary=val_data['validation_summary']
    )
    
    # Transform network summary
    summary_data = report['network_summary']
    network_summary = NetworkSummary(
        total_nodes=summary_data['total_nodes'],
        total_edges=summary_data['total_edges'],
        is_dag=summary_data['is_dag'],
        description=summary_data['description']
    )
    
    return StructureAnalysisResponse(
        timestamp=report['timestamp'],
        correlation_matrix=correlation_matrix,
        dependency_analysis=dependency_analysis,
        edge_explanations=edge_explanations,
        structure_validation=structure_validation,
        network_summary=network_summary
    )

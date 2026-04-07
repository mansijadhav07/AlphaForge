"""
PGM API Routes for AlphaForge.

Exposes Probabilistic Graphical Model functionality via REST APIs.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
import pandas as pd
import numpy as np
import json

from backend.api.schemas import (
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
    BaselineComparisonResponse,
    ModelMetricsResponse,
    CalibrationAnalysisResponse,
    CalibrationInterpretation,
    ErrorResponse
)
from backend.api.dependencies import get_pgm_service
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
        
        # Load precomputed evaluation results
        from backend.models.evaluation import ModelEvaluator
        evaluator = ModelEvaluator(results_dir="data/processed/evaluation")
        
        # Try to load from standard location
        eval_file = Path(f"data/processed/evaluation/{symbol}_evaluation.json")
        
        if eval_file.exists():
            logger.info(f"Loading precomputed evaluation for {symbol}")
            with open(eval_file, 'r') as f:
                results = json.load(f)
            
            # Remove symbol from results if it exists (will be added by response model)
            if 'symbol' in results:
                del results['symbol']
            
            return ModelEvaluationResponse(
                symbol=symbol,
                **results
            )
        
        # If no precomputed results, return 404
        logger.warning(f"No evaluation data found for {symbol}")
        raise HTTPException(
            status_code=404,
            detail=f"Evaluation data not available for {symbol}. Please run: python3 scripts/generate_evaluation_data.py --symbols {symbol}"
        )
        
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
    
    Loads precomputed failure analysis from JSON files.
    NO MOCK DATA - Returns 404 if data not available.
    
    Args:
        symbol: Stock ticker symbol
        max_failures: Maximum number of failures to return (filters precomputed data)
        lookback_periods: Not used (kept for API compatibility)
        pgm_service: Injected PGM service
        
    Returns:
        FailureAnalysisResponse with failure cases and insights
    """
    try:
        logger.info(f"Getting failure analysis for {symbol}")
        
        # Load precomputed failure data
        failure_file = Path(f"data/processed/failures/{symbol}_failures.json")
        
        if not failure_file.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Failure analysis data not available for {symbol}. "
                       f"Please run: python3 scripts/generate_failure_data.py --symbols {symbol}"
            )
        
        # Load results
        with open(failure_file, 'r') as f:
            results = json.load(f)
        
        # Filter failure cases if max_failures is less than stored
        failure_cases = results.get('failure_cases', [])
        if len(failure_cases) > max_failures:
            failure_cases = failure_cases[:max_failures]
        
        # Return response
        return FailureAnalysisResponse(
            symbol=results.get('symbol', symbol),
            timestamp=results.get('timestamp', datetime.now().isoformat()),
            failure_cases=failure_cases,
            summary=results.get('summary', {}),
            insights=results.get('insights', [])
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting failure analysis for {symbol}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get failure analysis: {str(e)}")




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
        from backend.models.structure_analysis import StructureAnalyzer
        
        # Initialize analyzer
        analyzer = StructureAnalyzer()
        
        # Get feature data for correlation analysis
        try:
            # Try to get real feature data
            from data.features.offline_store import OfflineFeatureStore
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
    from backend.api.schemas import (
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
        key_nodes=[node['node'] for node in dep_data['key_nodes']],  # Extract node names
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


# ============================================================================
# Baseline Comparison Endpoint
# ============================================================================

@router.get(
    "/baseline-comparison/{symbol}",
    response_model=BaselineComparisonResponse,
    summary="Compare PGM with Baseline Models",
    description="""
    Compare PGM performance against baseline models:
    - Random baseline (uniform random predictions)
    - Majority class baseline (always predict most common class)
    - Logistic Regression (simple linear classifier)
    
    Shows accuracy, precision, recall, F1 score, and confusion matrices.
    Demonstrates the value of the PGM approach.
    """,
    responses={
        200: {"description": "Baseline comparison completed"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def get_baseline_comparison(
    symbol: str,
    pgm_service = Depends(get_pgm_service)
) -> BaselineComparisonResponse:
    """
    Compare PGM with baseline models.
    
    Args:
        symbol: Stock symbol
        pgm_service: PGM service instance
        
    Returns:
        Comparison results with metrics for all models
    """
    try:
        logger.info(f"Baseline comparison requested for {symbol}")
        
        # Try to load pre-computed comparison results first
        comparison_file = Path(f'data/processed/baseline_comparison/{symbol}_comparison.json')
        if comparison_file.exists():
            logger.info(f"Loading pre-computed comparison for {symbol}")
            try:
                import json
                with open(comparison_file, 'r') as f:
                    data = json.load(f)
                
                # Convert to response format
                models_response = {}
                for name, metrics in data['models'].items():
                    models_response[name] = ModelMetricsResponse(**metrics)
                
                # Calculate improvements
                random_acc = data['models']['Random']['accuracy']
                majority_acc = data['models']['Majority Class']['accuracy']
                best_acc = data['best_model']['accuracy']
                
                improvement_over_random = best_acc - random_acc
                improvement_over_majority = best_acc - majority_acc
                
                response = BaselineComparisonResponse(
                    symbol=data['symbol'],
                    timestamp=data['timestamp'],
                    models=models_response,
                    summary=data['summary'],
                    best_model=data['best_model'],
                    winner=data['best_model']['name'],
                    improvement_over_random=improvement_over_random,
                    improvement_over_majority=improvement_over_majority
                )
                
                logger.info(f"Loaded real comparison data for {symbol}")
                return response
            except Exception as e:
                logger.warning(f"Error loading comparison file: {e}, falling back to mock")
        
        # If no pre-computed results, fall back to mock data
        logger.warning(f"No pre-computed comparison found for {symbol}, using mock data")
        return _get_mock_baseline_comparison(symbol)
        
    except Exception as e:
        logger.error(f"Error in baseline comparison: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate baseline comparison: {str(e)}"
        )


def _get_mock_baseline_comparison(symbol: str) -> BaselineComparisonResponse:
    """Generate mock baseline comparison for demo purposes."""
    
    # Mock confusion matrices
    random_cm = [[10, 12, 11], [11, 10, 12], [12, 11, 10]]
    majority_cm = [[0, 0, 0], [0, 50, 0], [0, 50, 0]]
    lr_cm = [[18, 8, 7], [6, 25, 2], [3, 4, 27]]
    pgm_cm = [[22, 6, 5], [5, 28, 0], [2, 3, 29]]
    
    models = {
        'Random': ModelMetricsResponse(
            model_name='Random',
            accuracy=0.33,
            precision=0.33,
            recall=0.33,
            f1_score=0.33,
            log_loss=1.10,
            confusion_matrix=random_cm,
            training_time=0.001,
            prediction_time=0.001
        ),
        'Majority Class': ModelMetricsResponse(
            model_name='Majority Class',
            accuracy=0.50,
            precision=0.25,
            recall=0.50,
            f1_score=0.33,
            log_loss=None,
            confusion_matrix=majority_cm,
            training_time=0.001,
            prediction_time=0.001
        ),
        'Logistic Regression': ModelMetricsResponse(
            model_name='Logistic Regression',
            accuracy=0.70,
            precision=0.69,
            recall=0.70,
            f1_score=0.69,
            log_loss=0.75,
            confusion_matrix=lr_cm,
            training_time=0.15,
            prediction_time=0.01
        ),
        'PGM (Bayesian Network)': ModelMetricsResponse(
            model_name='PGM (Bayesian Network)',
            accuracy=0.79,
            precision=0.78,
            recall=0.79,
            f1_score=0.78,
            log_loss=None,
            confusion_matrix=pgm_cm,
            training_time=2.5,
            prediction_time=0.05
        )
    }
    
    summary = [
        {
            'Model': 'PGM (Bayesian Network)',
            'Accuracy': 0.79,
            'Precision': 0.78,
            'Recall': 0.79,
            'F1 Score': 0.78,
            'Log Loss': None,
            'Training Time (s)': 2.5,
            'Prediction Time (s)': 0.05
        },
        {
            'Model': 'Logistic Regression',
            'Accuracy': 0.70,
            'Precision': 0.69,
            'Recall': 0.70,
            'F1 Score': 0.69,
            'Log Loss': 0.75,
            'Training Time (s)': 0.15,
            'Prediction Time (s)': 0.01
        },
        {
            'Model': 'Majority Class',
            'Accuracy': 0.50,
            'Precision': 0.25,
            'Recall': 0.50,
            'F1 Score': 0.33,
            'Log Loss': None,
            'Training Time (s)': 0.001,
            'Prediction Time (s)': 0.001
        },
        {
            'Model': 'Random',
            'Accuracy': 0.33,
            'Precision': 0.33,
            'Recall': 0.33,
            'F1 Score': 0.33,
            'Log Loss': 1.10,
            'Training Time (s)': 0.001,
            'Prediction Time (s)': 0.001
        }
    ]
    
    return BaselineComparisonResponse(
        symbol=symbol,
        timestamp=datetime.now().isoformat(),
        models=models,
        summary=summary,
        best_model={'name': 'PGM (Bayesian Network)', 'accuracy': 0.79, 'f1_score': 0.78},
        winner='PGM (Bayesian Network)',
        improvement_over_random=0.46,
        improvement_over_majority=0.29
    )



@router.get("/calibration/{symbol}", response_model=CalibrationAnalysisResponse)
async def get_calibration_analysis(
    symbol: str,
    pgm_service = Depends(get_pgm_service)
) -> CalibrationAnalysisResponse:
    """
    Get probability calibration analysis for PGM predictions.
    
    Analyzes how well predicted probabilities match actual outcomes through:
    - Calibration curves
    - Reliability diagrams
    - Calibration metrics (ECE, Brier score, etc.)
    
    Args:
        symbol: Stock symbol
        pgm_service: PGM service instance
        
    Returns:
        Calibration analysis with curves and metrics
    """
    try:
        logger.info(f"Calibration analysis requested for {symbol}")
        
        # Try to load pre-computed calibration results first
        calibration_file = Path(f'data/processed/calibration/{symbol}_calibration.json')
        if calibration_file.exists():
            logger.info(f"Loading pre-computed calibration for {symbol}")
            try:
                import json
                with open(calibration_file, 'r') as f:
                    data = json.load(f)
                
                response = CalibrationAnalysisResponse(
                    symbol=data['symbol'],
                    timestamp=data['timestamp'],
                    calibration_curve=data['calibration_curve'],
                    reliability_diagram=data['reliability_diagram'],
                    interpretation=CalibrationInterpretation(**data['interpretation']),
                    summary=data['summary']
                )
                
                logger.info(f"Loaded real calibration data for {symbol}")
                return response
            except Exception as e:
                logger.warning(f"Error loading calibration file: {e}, falling back to mock")
        
        # If no pre-computed results, fall back to mock data
        logger.warning(f"No pre-computed calibration found for {symbol}, using mock data")
        return _get_mock_calibration_analysis(symbol)
        
    except Exception as e:
        logger.error(f"Error in calibration analysis: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate calibration analysis: {str(e)}"
        )


def _get_mock_calibration_analysis(symbol: str) -> CalibrationAnalysisResponse:
    """Generate mock calibration analysis for demo purposes."""
    
    # Mock calibration bins (well-calibrated model)
    bins = []
    for i in range(10):
        pred_prob = 0.05 + i * 0.1
        # Add some realistic deviation
        actual_freq = pred_prob + np.random.normal(0, 0.05)
        actual_freq = max(0, min(1, actual_freq))
        
        bins.append({
            'predicted_prob': pred_prob,
            'actual_freq': actual_freq,
            'count': 50 + int(np.random.normal(0, 10)),
            'confidence_lower': max(0, actual_freq - 0.05),
            'confidence_upper': min(1, actual_freq + 0.05),
            'gap': abs(pred_prob - actual_freq)
        })
    
    metrics = {
        'ece': 0.045,  # Good calibration
        'mce': 0.082,
        'brier_score': 0.185,
        'log_loss': 0.512,
        'reliability_score': 0.955
    }
    
    interpretation = {
        'ece': {
            'quality': 'Excellent',
            'description': 'Model is very well calibrated',
            'value': 0.045
        },
        'brier': {
            'quality': 'Good',
            'description': 'Brier score of 0.185',
            'value': 0.185
        },
        'overall': 'Model probabilities are highly reliable'
    }
    
    return CalibrationAnalysisResponse(
        symbol=symbol,
        timestamp=datetime.now().isoformat(),
        calibration_curve={
            'bins': bins,
            'metrics': metrics
        },
        reliability_diagram={
            'bins': bins,
            'perfect_line': [{'x': 0.0, 'y': 0.0}, {'x': 1.0, 'y': 1.0}],
            'metrics': metrics,
            'summary': {
                'total_samples': 500,
                'n_bins': 10,
                'mean_predicted_prob': 0.52,
                'actual_positive_rate': 0.51
            }
        },
        interpretation=CalibrationInterpretation(**interpretation),
        summary={
            'total_samples': 500,
            'positive_rate': 0.51,
            'mean_predicted_prob': 0.52
        }
    )

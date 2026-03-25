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

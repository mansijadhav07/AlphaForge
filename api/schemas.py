"""
Pydantic schemas for PGM API request/response validation.
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum


# Enums
class SignalType(str, Enum):
    """Trading signal types."""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class ConfidenceLevel(str, Enum):
    """Confidence level categories."""
    HIGH = "high"
    MODERATE = "moderate"
    LOW = "low"


class RiskLevel(str, Enum):
    """Risk level categories."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RegimeType(str, Enum):
    """Market regime types."""
    BULL = "bull"
    BEAR = "bear"
    SIDEWAYS = "sideways"


# Response Models
class ProbabilityResponse(BaseModel):
    """Response model for probability distribution."""
    
    symbol: str = Field(..., description="Stock ticker symbol")
    probabilities: Dict[str, float] = Field(
        ..., 
        description="Probability distribution for outcomes",
        example={"positive": 0.65, "neutral": 0.25, "negative": 0.10}
    )
    confidence: str = Field(..., description="Confidence level (high/moderate/low)")
    timestamp: datetime = Field(..., description="Prediction timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "AAPL",
                "probabilities": {
                    "positive": 0.65,
                    "neutral": 0.25,
                    "negative": 0.10
                },
                "confidence": "high",
                "timestamp": "2024-03-25T10:30:00"
            }
        }


class FeatureFactor(BaseModel):
    """Individual feature factor in explanation."""
    
    feature: str = Field(..., description="Feature name")
    impact: float = Field(..., description="Impact score (0-1)", ge=0.0, le=1.0)
    reason: str = Field(..., description="Human-readable explanation")
    
    class Config:
        json_schema_extra = {
            "example": {
                "feature": "RSI",
                "impact": 0.234,
                "reason": "RSI indicates oversold conditions, suggesting potential upward reversal"
            }
        }


class ExplanationResponse(BaseModel):
    """Response model for prediction explanation."""
    
    symbol: str = Field(..., description="Stock ticker symbol")
    summary: str = Field(..., description="Brief summary of prediction")
    prediction: str = Field(..., description="Most likely outcome")
    confidence: float = Field(..., description="Confidence probability", ge=0.0, le=1.0)
    factors: List[FeatureFactor] = Field(..., description="Key contributing factors")
    risk_level: str = Field(..., description="Risk level assessment")
    risk_factors: List[str] = Field(..., description="Risk factors identified")
    recommendation: str = Field(..., description="Risk management recommendation")
    timestamp: datetime = Field(..., description="Prediction timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "AAPL",
                "summary": "Positive outlook with high confidence",
                "prediction": "positive",
                "confidence": 0.65,
                "factors": [
                    {
                        "feature": "RSI",
                        "impact": 0.234,
                        "reason": "RSI indicates oversold conditions"
                    }
                ],
                "risk_level": "low",
                "risk_factors": ["Low volatility suggests stable price action"],
                "recommendation": "Normal position sizing with standard risk controls",
                "timestamp": "2024-03-25T10:30:00"
            }
        }


class SignalResponse(BaseModel):
    """Response model for trading signal."""
    
    symbol: str = Field(..., description="Stock ticker symbol")
    signal: SignalType = Field(..., description="Trading signal (BUY/SELL/HOLD)")
    probability: float = Field(..., description="Signal probability", ge=0.0, le=1.0)
    confidence: str = Field(..., description="Confidence level")
    buy_probability: float = Field(..., description="Buy signal probability", ge=0.0, le=1.0)
    sell_probability: float = Field(..., description="Sell signal probability", ge=0.0, le=1.0)
    hold_probability: float = Field(..., description="Hold signal probability", ge=0.0, le=1.0)
    timestamp: datetime = Field(..., description="Signal timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "AAPL",
                "signal": "BUY",
                "probability": 0.65,
                "confidence": "high",
                "buy_probability": 0.65,
                "sell_probability": 0.10,
                "hold_probability": 0.25,
                "timestamp": "2024-03-25T10:30:00"
            }
        }


class SimulationRequest(BaseModel):
    """Request model for scenario simulation."""
    
    symbol: str = Field(..., description="Stock ticker symbol", example="AAPL")
    evidence: Dict[str, str] = Field(
        ..., 
        description="Market conditions to simulate",
        example={
            "rsi": "oversold",
            "momentum_score": "strong",
            "volatility_10": "low",
            "regime": "bull"
        }
    )
    
    @validator('evidence')
    def validate_evidence(cls, v):
        """Validate evidence dictionary."""
        if not v:
            raise ValueError("Evidence cannot be empty")
        
        # Valid feature names (without _state suffix)
        valid_features = {
            'rsi', 'momentum_score', 'volatility_10', 'trend_slope_30',
            'regime', 'macd_diff', 'bb_position', 'volume_to_sma', 'atr_pct'
        }
        
        for key in v.keys():
            if key not in valid_features:
                raise ValueError(f"Invalid feature: {key}. Must be one of {valid_features}")
        
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "AAPL",
                "evidence": {
                    "rsi": "oversold",
                    "momentum_score": "strong",
                    "volatility_10": "low",
                    "regime": "bull"
                }
            }
        }


class SimulationResponse(BaseModel):
    """Response model for scenario simulation."""
    
    symbol: str = Field(..., description="Stock ticker symbol")
    scenario: Dict[str, str] = Field(..., description="Simulated market conditions")
    probabilities: Dict[str, float] = Field(..., description="Predicted probabilities")
    signal: str = Field(..., description="Trading signal")
    signal_probability: float = Field(..., description="Signal probability", ge=0.0, le=1.0)
    explanation: List[str] = Field(..., description="Reasoning chain")
    risk_level: str = Field(..., description="Risk level")
    timestamp: datetime = Field(..., description="Simulation timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "AAPL",
                "scenario": {
                    "rsi": "oversold",
                    "momentum_score": "strong"
                },
                "probabilities": {
                    "positive": 0.65,
                    "neutral": 0.25,
                    "negative": 0.10
                },
                "signal": "BUY",
                "signal_probability": 0.65,
                "explanation": [
                    "RSI indicates oversold conditions",
                    "Strong momentum suggests directional movement"
                ],
                "risk_level": "low",
                "timestamp": "2024-03-25T10:30:00"
            }
        }


class FeatureImpact(BaseModel):
    """Individual feature impact."""
    
    feature: str = Field(..., description="Feature name")
    impact: float = Field(..., description="Impact score", ge=0.0, le=1.0)
    current_state: str = Field(..., description="Current state of the feature")
    
    class Config:
        json_schema_extra = {
            "example": {
                "feature": "RSI",
                "impact": 0.234,
                "current_state": "oversold"
            }
        }


class FeatureImpactResponse(BaseModel):
    """Response model for feature impact analysis."""
    
    symbol: str = Field(..., description="Stock ticker symbol")
    impacts: List[FeatureImpact] = Field(..., description="Feature impact scores")
    timestamp: datetime = Field(..., description="Analysis timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "AAPL",
                "impacts": [
                    {
                        "feature": "RSI",
                        "impact": 0.234,
                        "current_state": "oversold"
                    },
                    {
                        "feature": "Momentum Score",
                        "impact": 0.189,
                        "current_state": "strong"
                    }
                ],
                "timestamp": "2024-03-25T10:30:00"
            }
        }


class RegimeResponse(BaseModel):
    """Response model for market regime."""
    
    symbol: str = Field(..., description="Stock ticker symbol")
    bull: float = Field(..., description="Bull market probability", ge=0.0, le=1.0)
    bear: float = Field(..., description="Bear market probability", ge=0.0, le=1.0)
    sideways: float = Field(..., description="Sideways market probability", ge=0.0, le=1.0)
    current_regime: str = Field(..., description="Most likely regime")
    confidence: float = Field(..., description="Confidence in current regime", ge=0.0, le=1.0)
    timestamp: datetime = Field(..., description="Analysis timestamp")
    
    @validator('bull', 'bear', 'sideways')
    def validate_probability(cls, v):
        """Validate probability is between 0 and 1."""
        if not 0.0 <= v <= 1.0:
            raise ValueError("Probability must be between 0 and 1")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "AAPL",
                "bull": 0.60,
                "bear": 0.25,
                "sideways": 0.15,
                "current_regime": "bull",
                "confidence": 0.60,
                "timestamp": "2024-03-25T10:30:00"
            }
        }


class GraphNode(BaseModel):
    """Graph node representation."""
    
    id: str = Field(..., description="Node identifier")
    label: str = Field(..., description="Human-readable label")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "rsi_state",
                "label": "RSI"
            }
        }


class GraphEdge(BaseModel):
    """Graph edge representation."""
    
    from_: str = Field(..., alias="from", description="Source node")
    to: str = Field(..., description="Target node")
    from_label: str = Field(..., description="Source node label")
    to_label: str = Field(..., description="Target node label")
    
    class Config:
        json_schema_extra = {
            "example": {
                "from": "rsi_state",
                "to": "future_return_state",
                "from_label": "RSI",
                "to_label": "Future Return"
            }
        }


class GraphStructureResponse(BaseModel):
    """Response model for graph structure."""
    
    nodes: List[GraphNode] = Field(..., description="Graph nodes")
    edges: List[GraphEdge] = Field(..., description="Graph edges")
    num_nodes: int = Field(..., description="Number of nodes")
    num_edges: int = Field(..., description="Number of edges")
    is_dag: bool = Field(..., description="Whether graph is a valid DAG")
    
    class Config:
        json_schema_extra = {
            "example": {
                "nodes": [
                    {"id": "rsi_state", "label": "RSI"},
                    {"id": "momentum_score_state", "label": "Momentum Score"}
                ],
                "edges": [
                    {
                        "from": "rsi_state",
                        "to": "future_return_state",
                        "from_label": "RSI",
                        "to_label": "Future Return"
                    }
                ],
                "num_nodes": 11,
                "num_edges": 13,
                "is_dag": True
            }
        }


class ErrorResponse(BaseModel):
    """Error response model."""
    
    detail: str = Field(..., description="Error message")
    status_code: int = Field(..., description="HTTP status code")
    timestamp: Optional[datetime] = Field(None, description="Error timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Symbol not found",
                "status_code": 404,
                "timestamp": "2024-03-25T10:30:00"
            }
        }


class HealthResponse(BaseModel):
    """Health check response."""
    
    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    ready: bool = Field(..., description="Whether service is ready")
    timestamp: str = Field(..., description="Check timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "service": "PGM",
                "version": "1.0.0",
                "ready": True,
                "timestamp": "2024-03-25T10:30:00"
            }
        }

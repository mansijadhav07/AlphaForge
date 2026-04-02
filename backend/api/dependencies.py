"""
Dependency injection for PGM API.

Provides singleton PGM service instance for FastAPI routes.
"""

from typing import Optional
import pandas as pd
from pathlib import Path

from backend.models.state_encoding import StateEncoder, create_target_variable
from backend.models.graph_structure import GraphStructure, create_risk_node_data
from backend.models.probability_learning import ProbabilityLearner
from backend.models.inference_engine import InferenceEngine
from backend.models.explanation_engine import ExplanationEngine
from backend.models.scenario_simulator import ScenarioSimulator
from data.features.offline_store import OfflineFeatureStore
from utils.logger import get_logger

logger = get_logger(__name__)


class PGMService:
    """
    PGM Service for managing probabilistic predictions.
    
    Singleton service that initializes and manages all PGM components.
    """
    
    def __init__(self):
        """Initialize PGM service."""
        self.encoder: Optional[StateEncoder] = None
        self.graph_structure: Optional[GraphStructure] = None
        self.prob_learner: Optional[ProbabilityLearner] = None
        self.inference_engine: Optional[InferenceEngine] = None
        self.explanation_engine: Optional[ExplanationEngine] = None
        self.scenario_simulator: Optional[ScenarioSimulator] = None
        self.feature_store: Optional[OfflineFeatureStore] = None
        
        self._initialized = False
        self._model_path = Path("data/pgm_model")
        
        logger.info("PGMService instance created")
    
    def initialize(self, force_retrain: bool = False):
        """
        Initialize PGM components.
        
        Args:
            force_retrain: If True, retrain model even if saved model exists
        """
        if self._initialized and not force_retrain:
            logger.info("PGM service already initialized")
            return
        
        try:
            logger.info("Initializing PGM service...")
            
            # Initialize feature store
            self.feature_store = OfflineFeatureStore()
            
            # Check if trained model exists
            if self._model_exists() and not force_retrain:
                logger.info("Loading pre-trained PGM model...")
                self._load_model()
            else:
                logger.info("Training new PGM model...")
                self._train_model()
            
            self._initialized = True
            logger.info("PGM service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize PGM service: {e}", exc_info=True)
            raise
    
    def _model_exists(self) -> bool:
        """Check if trained model exists."""
        required_files = [
            self._model_path / "encoder_config.json",
            self._model_path / "graph_structure.json",
            self._model_path / "cpts.pkl"
        ]
        return all(f.exists() for f in required_files)
    
    def _load_model(self):
        """Load pre-trained model."""
        from backend.models.utils import load_pgm_model
        
        self.encoder, self.graph_structure, self.prob_learner = load_pgm_model(
            str(self._model_path)
        )
        
        # Initialize engines
        self.inference_engine = InferenceEngine(self.graph_structure, self.prob_learner)
        self.explanation_engine = ExplanationEngine(self.graph_structure, self.inference_engine)
        self.scenario_simulator = ScenarioSimulator(self.inference_engine, self.explanation_engine)
        
        logger.info("Pre-trained model loaded successfully")
    
    def _train_model(self):
        """Train new model from data."""
        # Load training data
        df = self.feature_store.read_features('market_features', use_latest=True)
        
        if len(df) == 0:
            raise ValueError("No training data available. Run example_workflow.py first.")
        
        logger.info(f"Training on {len(df)} samples")
        
        # Initialize encoder
        self.encoder = StateEncoder()
        
        # Prepare data
        from backend.models.utils import prepare_data_for_pgm
        encoded_df = prepare_data_for_pgm(df, self.encoder, horizon=5, threshold=0.02)
        
        # Build graph
        self.graph_structure = GraphStructure()
        self.graph_structure.build_default_structure()
        
        # Learn probabilities (use subset for faster training)
        self.prob_learner = ProbabilityLearner(self.graph_structure, smoothing_alpha=1.0)
        
        # Use up to 2000 samples for training
        train_df = encoded_df.head(min(2000, len(encoded_df)))
        self.prob_learner.learn_from_data(train_df)
        
        # Initialize engines
        self.inference_engine = InferenceEngine(self.graph_structure, self.prob_learner)
        self.explanation_engine = ExplanationEngine(self.graph_structure, self.inference_engine)
        self.scenario_simulator = ScenarioSimulator(self.inference_engine, self.explanation_engine)
        
        # Save model
        self._save_model()
        
        logger.info("Model trained and saved successfully")
    
    def _save_model(self):
        """Save trained model."""
        from backend.models.utils import save_pgm_model
        
        self._model_path.mkdir(parents=True, exist_ok=True)
        save_pgm_model(
            self.encoder,
            self.graph_structure,
            self.prob_learner,
            str(self._model_path)
        )
        
        logger.info(f"Model saved to {self._model_path}")
    
    def get_latest_features(self, symbol: str) -> Optional[pd.DataFrame]:
        """
        Get latest features for a symbol.
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            DataFrame with latest features or None if not found
        """
        try:
            df = self.feature_store.read_features('market_features', use_latest=True)
            
            if len(df) == 0:
                return None
            
            # Filter by symbol
            symbol_df = df[df['ticker'] == symbol.upper()]
            
            if len(symbol_df) == 0:
                logger.warning(f"No data found for symbol: {symbol}")
                return None
            
            # Get latest record
            latest = symbol_df.sort_values('date', ascending=False).iloc[0:1]
            
            return latest
            
        except Exception as e:
            logger.error(f"Error getting features for {symbol}: {e}")
            return None
    
    def encode_features(self, features: pd.DataFrame) -> pd.DataFrame:
        """
        Encode features to discrete states.
        
        Args:
            features: DataFrame with continuous features
            
        Returns:
            DataFrame with encoded state columns
        """
        encoded = self.encoder.transform(features)
        
        # Add risk state
        encoded = create_risk_node_data(encoded)
        
        return encoded
    
    def build_evidence(self, encoded_df: pd.DataFrame) -> dict:
        """
        Build evidence dictionary from encoded features.
        
        Args:
            encoded_df: DataFrame with encoded state columns
            
        Returns:
            Dictionary of evidence for inference
        """
        # Get state columns
        state_cols = [col for col in encoded_df.columns if col.endswith('_state')]
        
        # Exclude target variable
        evidence_cols = [col for col in state_cols if col != 'future_return_state']
        
        # Build evidence dictionary from first row
        evidence = {}
        for col in evidence_cols:
            value = encoded_df[col].iloc[0]
            if pd.notna(value):
                evidence[col] = value
        
        return evidence
    
    def categorize_confidence(self, probability: float) -> str:
        """
        Categorize confidence level.
        
        Args:
            probability: Probability value (0-1)
            
        Returns:
            Confidence level string (high/moderate/low)
        """
        if probability >= 0.75:
            return "high"
        elif probability >= 0.55:
            return "moderate"
        else:
            return "low"
    
    def is_ready(self) -> bool:
        """
        Check if service is ready.
        
        Returns:
            True if all components are initialized
        """
        return (
            self._initialized and
            self.encoder is not None and
            self.graph_structure is not None and
            self.prob_learner is not None and
            self.inference_engine is not None and
            self.explanation_engine is not None and
            self.scenario_simulator is not None
        )
    
    def get_status(self) -> dict:
        """
        Get service status.
        
        Returns:
            Dictionary with status information
        """
        return {
            "initialized": self._initialized,
            "encoder_ready": self.encoder is not None,
            "graph_ready": self.graph_structure is not None,
            "learner_ready": self.prob_learner is not None,
            "inference_ready": self.inference_engine is not None,
            "explanation_ready": self.explanation_engine is not None,
            "simulator_ready": self.scenario_simulator is not None,
            "model_path": str(self._model_path),
            "model_exists": self._model_exists()
        }


# Global singleton instance
_pgm_service: Optional[PGMService] = None


def get_pgm_service() -> PGMService:
    """
    Get or create PGM service singleton.
    
    This is used as a FastAPI dependency.
    
    Returns:
        PGMService instance
    """
    global _pgm_service
    
    if _pgm_service is None:
        logger.info("Creating new PGM service instance")
        _pgm_service = PGMService()
        
        # Initialize on first access
        try:
            _pgm_service.initialize()
        except Exception as e:
            logger.error(f"Failed to initialize PGM service: {e}")
            # Don't raise - allow service to start but mark as not ready
    
    return _pgm_service


def reset_pgm_service():
    """
    Reset PGM service singleton.
    
    Useful for testing or forcing reinitialization.
    """
    global _pgm_service
    _pgm_service = None
    logger.info("PGM service reset")


def initialize_pgm_service(force_retrain: bool = False):
    """
    Explicitly initialize PGM service.
    
    Args:
        force_retrain: If True, retrain model even if saved model exists
    """
    service = get_pgm_service()
    service.initialize(force_retrain=force_retrain)

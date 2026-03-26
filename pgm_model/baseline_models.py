"""
Baseline Models for PGM Comparison.

Implements simple baseline models to demonstrate the value of the PGM approach:
- Random baseline
- Logistic Regression classifier
- Comparison metrics
"""

from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
    log_loss
)
from dataclasses import dataclass
from datetime import datetime

from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ModelMetrics:
    """Metrics for a single model."""
    model_name: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    log_loss: Optional[float]
    confusion_matrix: List[List[int]]
    classification_report: Dict
    training_time: float
    prediction_time: float


class RandomBaseline:
    """
    Random baseline that predicts classes with uniform probability.
    
    This is the simplest baseline - any model should beat this.
    """
    
    def __init__(self, random_state: int = 42):
        """Initialize random baseline."""
        self.random_state = random_state
        self.classes_ = None
        self.class_probs_ = None
        logger.info("RandomBaseline initialized")
    
    def fit(self, X: pd.DataFrame, y: pd.Series) -> 'RandomBaseline':
        """
        Fit the random baseline.
        
        Args:
            X: Feature DataFrame (not used, but kept for API consistency)
            y: Target series
            
        Returns:
            Self for chaining
        """
        self.classes_ = np.unique(y)
        # Uniform probability for each class
        self.class_probs_ = np.ones(len(self.classes_)) / len(self.classes_)
        
        logger.info(f"RandomBaseline fitted with {len(self.classes_)} classes")
        return self
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Predict random classes.
        
        Args:
            X: Feature DataFrame
            
        Returns:
            Random predictions
        """
        np.random.seed(self.random_state)
        return np.random.choice(self.classes_, size=len(X), p=self.class_probs_)
    
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """
        Predict uniform probabilities.
        
        Args:
            X: Feature DataFrame
            
        Returns:
            Uniform probability matrix
        """
        n_samples = len(X)
        n_classes = len(self.classes_)
        return np.tile(self.class_probs_, (n_samples, 1))


class MajorityBaseline:
    """
    Majority class baseline that always predicts the most common class.
    
    This is slightly smarter than random - predicts the most frequent class.
    """
    
    def __init__(self):
        """Initialize majority baseline."""
        self.majority_class_ = None
        self.classes_ = None
        self.class_probs_ = None
        logger.info("MajorityBaseline initialized")
    
    def fit(self, X: pd.DataFrame, y: pd.Series) -> 'MajorityBaseline':
        """
        Fit the majority baseline.
        
        Args:
            X: Feature DataFrame (not used)
            y: Target series
            
        Returns:
            Self for chaining
        """
        self.classes_ = np.unique(y)
        value_counts = y.value_counts()
        self.majority_class_ = value_counts.index[0]
        
        # Probability is 1.0 for majority class, 0.0 for others
        self.class_probs_ = np.zeros(len(self.classes_))
        majority_idx = np.where(self.classes_ == self.majority_class_)[0][0]
        self.class_probs_[majority_idx] = 1.0
        
        logger.info(f"MajorityBaseline fitted: majority class = {self.majority_class_}")
        return self
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Predict majority class for all samples.
        
        Args:
            X: Feature DataFrame
            
        Returns:
            Majority class predictions
        """
        return np.full(len(X), self.majority_class_)
    
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """
        Predict probabilities (1.0 for majority, 0.0 for others).
        
        Args:
            X: Feature DataFrame
            
        Returns:
            Probability matrix
        """
        n_samples = len(X)
        return np.tile(self.class_probs_, (n_samples, 1))


class LogisticRegressionBaseline:
    """
    Logistic Regression baseline.
    
    A simple but effective linear classifier.
    """
    
    def __init__(self, max_iter: int = 1000, random_state: int = 42):
        """
        Initialize logistic regression baseline.
        
        Args:
            max_iter: Maximum iterations for solver
            random_state: Random seed
        """
        self.model = LogisticRegression(
            max_iter=max_iter,
            random_state=random_state,
            multi_class='multinomial',
            solver='lbfgs'
        )
        self.label_encoder = LabelEncoder()
        self.feature_names_ = None
        logger.info("LogisticRegressionBaseline initialized")
    
    def fit(self, X: pd.DataFrame, y: pd.Series) -> 'LogisticRegressionBaseline':
        """
        Fit logistic regression.
        
        Args:
            X: Feature DataFrame
            y: Target series
            
        Returns:
            Self for chaining
        """
        self.feature_names_ = X.columns.tolist()
        
        # Encode target if it's categorical
        if y.dtype == 'object' or isinstance(y.iloc[0], str):
            y_encoded = self.label_encoder.fit_transform(y)
        else:
            y_encoded = y
        
        self.model.fit(X, y_encoded)
        
        logger.info(f"LogisticRegressionBaseline fitted with {len(self.feature_names_)} features")
        return self
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Predict classes.
        
        Args:
            X: Feature DataFrame
            
        Returns:
            Predictions
        """
        predictions = self.model.predict(X)
        
        # Decode if we encoded during fit
        if hasattr(self.label_encoder, 'classes_'):
            return self.label_encoder.inverse_transform(predictions)
        return predictions
    
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """
        Predict class probabilities.
        
        Args:
            X: Feature DataFrame
            
        Returns:
            Probability matrix
        """
        return self.model.predict_proba(X)
    
    @property
    def classes_(self):
        """Get class labels."""
        if hasattr(self.label_encoder, 'classes_'):
            return self.label_encoder.classes_
        return self.model.classes_


class BaselineComparison:
    """
    Compare PGM against baseline models.
    
    Provides comprehensive comparison metrics.
    """
    
    def __init__(self):
        """Initialize baseline comparison."""
        self.models = {}
        self.results = {}
        logger.info("BaselineComparison initialized")
    
    def add_model(self, name: str, model) -> 'BaselineComparison':
        """
        Add a model to compare.
        
        Args:
            name: Model name
            model: Model instance with fit/predict/predict_proba methods
            
        Returns:
            Self for chaining
        """
        self.models[name] = model
        logger.info(f"Added model: {name}")
        return self
    
    def evaluate_model(self,
                      model,
                      model_name: str,
                      X_train: pd.DataFrame,
                      y_train: pd.Series,
                      X_test: pd.DataFrame,
                      y_test: pd.Series) -> ModelMetrics:
        """
        Evaluate a single model.
        
        Args:
            model: Model instance
            model_name: Model name
            X_train: Training features
            y_train: Training target
            X_test: Test features
            y_test: Test target
            
        Returns:
            Model metrics
        """
        logger.info(f"Evaluating {model_name}...")
        
        # Training
        start_time = datetime.now()
        model.fit(X_train, y_train)
        training_time = (datetime.now() - start_time).total_seconds()
        
        # Prediction
        start_time = datetime.now()
        y_pred = model.predict(X_test)
        prediction_time = (datetime.now() - start_time).total_seconds()
        
        # Probabilities (if available)
        try:
            y_pred_proba = model.predict_proba(X_test)
            # Calculate log loss
            # Need to encode y_test if it's categorical
            if y_test.dtype == 'object' or isinstance(y_test.iloc[0], str):
                le = LabelEncoder()
                y_test_encoded = le.fit_transform(y_test)
            else:
                y_test_encoded = y_test
            
            logloss = log_loss(y_test_encoded, y_pred_proba)
        except Exception as e:
            logger.warning(f"Could not calculate log loss for {model_name}: {e}")
            logloss = None
        
        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        
        # For multi-class, use weighted average
        precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
        recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
        f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
        
        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred)
        
        # Classification report
        report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
        
        metrics = ModelMetrics(
            model_name=model_name,
            accuracy=float(accuracy),
            precision=float(precision),
            recall=float(recall),
            f1_score=float(f1),
            log_loss=float(logloss) if logloss is not None else None,
            confusion_matrix=cm.tolist(),
            classification_report=report,
            training_time=training_time,
            prediction_time=prediction_time
        )
        
        logger.info(f"{model_name} - Accuracy: {accuracy:.4f}, F1: {f1:.4f}")
        
        return metrics
    
    def compare_all(self,
                   X_train: pd.DataFrame,
                   y_train: pd.Series,
                   X_test: pd.DataFrame,
                   y_test: pd.Series) -> Dict[str, ModelMetrics]:
        """
        Compare all models.
        
        Args:
            X_train: Training features
            y_train: Training target
            X_test: Test features
            y_test: Test target
            
        Returns:
            Dictionary of model metrics
        """
        logger.info(f"Comparing {len(self.models)} models...")
        
        results = {}
        for name, model in self.models.items():
            try:
                metrics = self.evaluate_model(
                    model, name, X_train, y_train, X_test, y_test
                )
                results[name] = metrics
            except Exception as e:
                logger.error(f"Error evaluating {name}: {e}", exc_info=True)
        
        self.results = results
        
        logger.info("Comparison complete")
        return results
    
    def get_comparison_summary(self) -> pd.DataFrame:
        """
        Get comparison summary as DataFrame.
        
        Returns:
            Summary DataFrame
        """
        if not self.results:
            raise ValueError("No results available. Run compare_all() first.")
        
        summary_data = []
        for name, metrics in self.results.items():
            summary_data.append({
                'Model': name,
                'Accuracy': metrics.accuracy,
                'Precision': metrics.precision,
                'Recall': metrics.recall,
                'F1 Score': metrics.f1_score,
                'Log Loss': metrics.log_loss,
                'Training Time (s)': metrics.training_time,
                'Prediction Time (s)': metrics.prediction_time
            })
        
        df = pd.DataFrame(summary_data)
        df = df.sort_values('Accuracy', ascending=False)
        
        return df
    
    def get_best_model(self, metric: str = 'accuracy') -> Tuple[str, ModelMetrics]:
        """
        Get the best performing model.
        
        Args:
            metric: Metric to use for comparison (accuracy, f1_score, etc.)
            
        Returns:
            Tuple of (model_name, metrics)
        """
        if not self.results:
            raise ValueError("No results available. Run compare_all() first.")
        
        metric_map = {
            'accuracy': lambda m: m.accuracy,
            'precision': lambda m: m.precision,
            'recall': lambda m: m.recall,
            'f1_score': lambda m: m.f1_score,
            'log_loss': lambda m: -m.log_loss if m.log_loss else float('inf')
        }
        
        if metric not in metric_map:
            raise ValueError(f"Unknown metric: {metric}")
        
        best_name = max(self.results.keys(), key=lambda k: metric_map[metric](self.results[k]))
        
        return best_name, self.results[best_name]


def create_baseline_comparison(X_train: pd.DataFrame,
                               y_train: pd.Series,
                               X_test: pd.DataFrame,
                               y_test: pd.Series,
                               include_pgm: bool = False,
                               pgm_predictions: Optional[np.ndarray] = None) -> Dict:
    """
    Create a complete baseline comparison.
    
    Args:
        X_train: Training features
        y_train: Training target
        X_test: Test features
        y_test: Test target
        include_pgm: Whether to include PGM in comparison
        pgm_predictions: PGM predictions (if include_pgm=True)
        
    Returns:
        Comparison results dictionary
    """
    logger.info("Creating baseline comparison...")
    
    # Initialize comparison
    comparison = BaselineComparison()
    
    # Add baseline models
    comparison.add_model('Random', RandomBaseline())
    comparison.add_model('Majority Class', MajorityBaseline())
    comparison.add_model('Logistic Regression', LogisticRegressionBaseline())
    
    # Run comparison
    results = comparison.compare_all(X_train, y_train, X_test, y_test)
    
    # Add PGM if provided
    if include_pgm and pgm_predictions is not None:
        logger.info("Adding PGM to comparison...")
        
        # Calculate PGM metrics
        accuracy = accuracy_score(y_test, pgm_predictions)
        precision = precision_score(y_test, pgm_predictions, average='weighted', zero_division=0)
        recall = recall_score(y_test, pgm_predictions, average='weighted', zero_division=0)
        f1 = f1_score(y_test, pgm_predictions, average='weighted', zero_division=0)
        cm = confusion_matrix(y_test, pgm_predictions)
        report = classification_report(y_test, pgm_predictions, output_dict=True, zero_division=0)
        
        pgm_metrics = ModelMetrics(
            model_name='PGM (Bayesian Network)',
            accuracy=float(accuracy),
            precision=float(precision),
            recall=float(recall),
            f1_score=float(f1),
            log_loss=None,  # PGM doesn't provide probabilities in same format
            confusion_matrix=cm.tolist(),
            classification_report=report,
            training_time=0.0,  # Already trained
            prediction_time=0.0  # Already predicted
        )
        
        results['PGM (Bayesian Network)'] = pgm_metrics
    
    # Get summary
    summary_df = comparison.get_comparison_summary()
    
    # Get best model
    best_name, best_metrics = comparison.get_best_model('accuracy')
    
    return {
        'results': results,
        'summary': summary_df.to_dict('records'),
        'best_model': {
            'name': best_name,
            'accuracy': best_metrics.accuracy,
            'f1_score': best_metrics.f1_score
        },
        'comparison': comparison
    }

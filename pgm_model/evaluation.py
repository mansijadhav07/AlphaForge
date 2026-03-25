"""
Model Evaluation Module for Probabilistic Graphical Model.

Evaluates PGM performance using various metrics including accuracy,
confusion matrix, calibration analysis, and Brier score.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

from utils.logger import get_logger

logger = get_logger(__name__)


class ModelEvaluator:
    """
    Evaluates probabilistic model performance.
    
    Provides comprehensive evaluation metrics including:
    - Classification accuracy
    - Confusion matrix
    - Calibration analysis
    - Brier score
    - Precision, recall, F1-score
    """
    
    def __init__(self, results_dir: str = "data/evaluation"):
        """
        Initialize ModelEvaluator.
        
        Args:
            results_dir: Directory to store evaluation results
        """
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"ModelEvaluator initialized with results_dir: {results_dir}")
    
    def evaluate_predictions(
        self,
        predictions: pd.DataFrame,
        actuals: pd.DataFrame,
        prediction_col: str = 'predicted_class',
        probability_cols: Dict[str, str] = None,
        actual_col: str = 'actual_class'
    ) -> Dict:
        """
        Comprehensive evaluation of model predictions.
        
        Args:
            predictions: DataFrame with predicted classes and probabilities
            actuals: DataFrame with actual outcomes
            prediction_col: Column name for predicted class
            probability_cols: Dict mapping class names to probability columns
            actual_col: Column name for actual class
            
        Returns:
            Dictionary with all evaluation metrics
        """
        logger.info("Starting model evaluation")
        
        # Merge predictions with actuals
        df = predictions.merge(actuals, left_index=True, right_index=True, how='inner')
        
        if len(df) == 0:
            logger.warning("No matching data for evaluation")
            return self._empty_results()
        
        # Default probability columns
        if probability_cols is None:
            probability_cols = {
                'positive': 'prob_positive',
                'neutral': 'prob_neutral',
                'negative': 'prob_negative'
            }
        
        # Calculate metrics
        results = {
            'timestamp': datetime.now().isoformat(),
            'n_samples': len(df),
            'accuracy': self._calculate_accuracy(df[prediction_col], df[actual_col]),
            'confusion_matrix': self._calculate_confusion_matrix(df[prediction_col], df[actual_col]),
            'classification_report': self._calculate_classification_metrics(df[prediction_col], df[actual_col]),
            'brier_score': self._calculate_brier_score(df, probability_cols, actual_col),
            'calibration_data': self._calculate_calibration(df, probability_cols, actual_col),
            'probability_distribution': self._analyze_probability_distribution(df, probability_cols),
            'class_distribution': self._analyze_class_distribution(df, prediction_col, actual_col)
        }
        
        logger.info(f"Evaluation complete. Accuracy: {results['accuracy']:.3f}")
        
        return results
    
    def _calculate_accuracy(self, predictions: pd.Series, actuals: pd.Series) -> float:
        """Calculate classification accuracy."""
        correct = (predictions == actuals).sum()
        total = len(predictions)
        return float(correct / total) if total > 0 else 0.0
    
    def _calculate_confusion_matrix(
        self,
        predictions: pd.Series,
        actuals: pd.Series
    ) -> Dict:
        """
        Calculate confusion matrix.
        
        Returns:
            Dictionary with confusion matrix data
        """
        classes = ['positive', 'neutral', 'negative']
        
        # Initialize matrix
        matrix = {
            'classes': classes,
            'matrix': []
        }
        
        # Calculate counts for each actual-predicted pair
        for actual_class in classes:
            row = []
            for pred_class in classes:
                count = ((actuals == actual_class) & (predictions == pred_class)).sum()
                row.append(int(count))
            matrix['matrix'].append(row)
        
        # Calculate totals
        matrix['row_totals'] = [sum(row) for row in matrix['matrix']]
        matrix['col_totals'] = [sum(col) for col in zip(*matrix['matrix'])]
        matrix['total'] = sum(matrix['row_totals'])
        
        return matrix
    
    def _calculate_classification_metrics(
        self,
        predictions: pd.Series,
        actuals: pd.Series
    ) -> Dict:
        """
        Calculate precision, recall, F1-score for each class.
        
        Returns:
            Dictionary with metrics per class
        """
        classes = ['positive', 'neutral', 'negative']
        metrics = {}
        
        for cls in classes:
            # True positives, false positives, false negatives
            tp = ((predictions == cls) & (actuals == cls)).sum()
            fp = ((predictions == cls) & (actuals != cls)).sum()
            fn = ((predictions != cls) & (actuals == cls)).sum()
            
            # Calculate metrics
            precision = float(tp / (tp + fp)) if (tp + fp) > 0 else 0.0
            recall = float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0
            f1 = float(2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
            
            metrics[cls] = {
                'precision': precision,
                'recall': recall,
                'f1_score': f1,
                'support': int((actuals == cls).sum())
            }
        
        # Calculate macro averages
        metrics['macro_avg'] = {
            'precision': np.mean([m['precision'] for m in metrics.values() if isinstance(m, dict)]),
            'recall': np.mean([m['recall'] for m in metrics.values() if isinstance(m, dict)]),
            'f1_score': np.mean([m['f1_score'] for m in metrics.values() if isinstance(m, dict)])
        }
        
        return metrics
    
    def _calculate_brier_score(
        self,
        df: pd.DataFrame,
        probability_cols: Dict[str, str],
        actual_col: str
    ) -> Dict:
        """
        Calculate Brier score for probability predictions.
        
        Brier score measures the mean squared difference between
        predicted probabilities and actual outcomes.
        
        Returns:
            Dictionary with Brier scores per class and overall
        """
        brier_scores = {}
        
        for class_name, prob_col in probability_cols.items():
            if prob_col not in df.columns:
                continue
            
            # Create binary indicator for this class
            actual_binary = (df[actual_col] == class_name).astype(int)
            predicted_prob = df[prob_col]
            
            # Calculate Brier score: mean((p - y)^2)
            brier = float(np.mean((predicted_prob - actual_binary) ** 2))
            brier_scores[class_name] = brier
        
        # Overall Brier score (average across classes)
        if brier_scores:
            brier_scores['overall'] = float(np.mean(list(brier_scores.values())))
        
        return brier_scores
    
    def _calculate_calibration(
        self,
        df: pd.DataFrame,
        probability_cols: Dict[str, str],
        actual_col: str,
        n_bins: int = 10
    ) -> Dict:
        """
        Calculate calibration data for reliability diagrams.
        
        Calibration measures how well predicted probabilities match
        actual frequencies.
        
        Args:
            df: DataFrame with predictions and actuals
            probability_cols: Probability column names
            actual_col: Actual class column
            n_bins: Number of bins for calibration curve
            
        Returns:
            Dictionary with calibration data per class
        """
        calibration_data = {}
        
        for class_name, prob_col in probability_cols.items():
            if prob_col not in df.columns:
                continue
            
            # Create binary indicator
            actual_binary = (df[actual_col] == class_name).astype(int)
            predicted_prob = df[prob_col]
            
            # Create bins
            bins = np.linspace(0, 1, n_bins + 1)
            bin_indices = np.digitize(predicted_prob, bins) - 1
            bin_indices = np.clip(bin_indices, 0, n_bins - 1)
            
            # Calculate mean predicted prob and actual frequency per bin
            bin_data = []
            for i in range(n_bins):
                mask = bin_indices == i
                if mask.sum() > 0:
                    mean_predicted = float(predicted_prob[mask].mean())
                    mean_actual = float(actual_binary[mask].mean())
                    count = int(mask.sum())
                    
                    bin_data.append({
                        'bin': i,
                        'predicted_prob': mean_predicted,
                        'actual_freq': mean_actual,
                        'count': count
                    })
            
            calibration_data[class_name] = bin_data
        
        return calibration_data
    
    def _analyze_probability_distribution(
        self,
        df: pd.DataFrame,
        probability_cols: Dict[str, str]
    ) -> Dict:
        """
        Analyze distribution of predicted probabilities.
        
        Returns:
            Statistics about probability distributions
        """
        distribution = {}
        
        for class_name, prob_col in probability_cols.items():
            if prob_col not in df.columns:
                continue
            
            probs = df[prob_col]
            
            distribution[class_name] = {
                'mean': float(probs.mean()),
                'std': float(probs.std()),
                'min': float(probs.min()),
                'max': float(probs.max()),
                'median': float(probs.median()),
                'q25': float(probs.quantile(0.25)),
                'q75': float(probs.quantile(0.75))
            }
        
        return distribution
    
    def _analyze_class_distribution(
        self,
        df: pd.DataFrame,
        prediction_col: str,
        actual_col: str
    ) -> Dict:
        """
        Analyze distribution of predicted and actual classes.
        
        Returns:
            Class counts and percentages
        """
        predicted_counts = df[prediction_col].value_counts().to_dict()
        actual_counts = df[actual_col].value_counts().to_dict()
        
        total = len(df)
        
        return {
            'predicted': {
                'counts': {k: int(v) for k, v in predicted_counts.items()},
                'percentages': {k: float(v / total) for k, v in predicted_counts.items()}
            },
            'actual': {
                'counts': {k: int(v) for k, v in actual_counts.items()},
                'percentages': {k: float(v / total) for k, v in actual_counts.items()}
            }
        }
    
    def _empty_results(self) -> Dict:
        """Return empty results structure."""
        return {
            'timestamp': datetime.now().isoformat(),
            'n_samples': 0,
            'accuracy': 0.0,
            'confusion_matrix': {'classes': [], 'matrix': []},
            'classification_report': {},
            'brier_score': {},
            'calibration_data': {},
            'probability_distribution': {},
            'class_distribution': {}
        }
    
    def save_results(self, results: Dict, symbol: str = 'overall') -> str:
        """
        Save evaluation results to JSON file.
        
        Args:
            results: Evaluation results dictionary
            symbol: Symbol identifier for the results
            
        Returns:
            Path to saved file
        """
        filename = f"evaluation_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.results_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Evaluation results saved to {filepath}")
        
        # Also save as latest
        latest_path = self.results_dir / f"evaluation_{symbol}_latest.json"
        with open(latest_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        return str(filepath)
    
    def load_results(self, symbol: str = 'overall') -> Optional[Dict]:
        """
        Load latest evaluation results for a symbol.
        
        Args:
            symbol: Symbol identifier
            
        Returns:
            Evaluation results dictionary or None
        """
        latest_path = self.results_dir / f"evaluation_{symbol}_latest.json"
        
        if not latest_path.exists():
            logger.warning(f"No evaluation results found for {symbol}")
            return None
        
        with open(latest_path, 'r') as f:
            results = json.load(f)
        
        logger.info(f"Loaded evaluation results for {symbol}")
        return results
    
    def evaluate_model_on_historical_data(
        self,
        state_encoder,
        inference_engine,
        features_df: pd.DataFrame,
        lookback_periods: int = 5
    ) -> Dict:
        """
        Evaluate model on historical data with actual outcomes.
        
        Args:
            state_encoder: StateEncoder instance
            inference_engine: InferenceEngine instance
            features_df: DataFrame with features and actual returns
            lookback_periods: Number of periods to look ahead for actual outcome
            
        Returns:
            Evaluation results dictionary
        """
        logger.info(f"Evaluating model on {len(features_df)} historical samples")
        
        predictions_list = []
        actuals_list = []
        
        # Iterate through historical data
        for i in range(len(features_df) - lookback_periods):
            # Get features at time t
            features = features_df.iloc[i]
            
            # Encode features
            encoded = state_encoder.encode_features(features)
            
            # Build evidence
            evidence = {
                f"{col}_state": encoded.get(col, 'unknown')
                for col in encoded.index
                if f"{col}_state" in inference_engine.model.nodes
            }
            
            # Get prediction
            try:
                result = inference_engine.query(['future_return_state'], evidence)
                probs = result.get('future_return_state', {})
                
                if probs:
                    predicted_class = max(probs, key=probs.get)
                    
                    # Get actual outcome (future return)
                    future_return = features_df.iloc[i + lookback_periods]['return']
                    
                    # Classify actual return
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
                        'prob_negative': probs.get('negative', 0.0)
                    })
                    
                    actuals_list.append({
                        'index': i,
                        'actual_class': actual_class,
                        'actual_return': future_return
                    })
            except Exception as e:
                logger.warning(f"Error evaluating sample {i}: {e}")
                continue
        
        # Create DataFrames
        predictions_df = pd.DataFrame(predictions_list).set_index('index')
        actuals_df = pd.DataFrame(actuals_list).set_index('index')
        
        # Evaluate
        results = self.evaluate_predictions(
            predictions_df,
            actuals_df,
            prediction_col='predicted_class',
            probability_cols={
                'positive': 'prob_positive',
                'neutral': 'prob_neutral',
                'negative': 'prob_negative'
            },
            actual_col='actual_class'
        )
        
        return results


def calculate_expected_calibration_error(calibration_data: Dict) -> float:
    """
    Calculate Expected Calibration Error (ECE).
    
    ECE measures the difference between predicted probabilities
    and actual frequencies, weighted by bin size.
    
    Args:
        calibration_data: Calibration data from _calculate_calibration
        
    Returns:
        ECE score (lower is better)
    """
    total_samples = 0
    weighted_error = 0.0
    
    for class_name, bins in calibration_data.items():
        for bin_data in bins:
            count = bin_data['count']
            predicted = bin_data['predicted_prob']
            actual = bin_data['actual_freq']
            
            total_samples += count
            weighted_error += count * abs(predicted - actual)
    
    ece = weighted_error / total_samples if total_samples > 0 else 0.0
    return float(ece)

"""
Probability Calibration Analysis for PGM.

This module provides tools to assess how well the PGM's predicted probabilities
match actual outcomes through calibration curves and reliability diagrams.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class CalibrationBin:
    """Represents a single bin in calibration analysis."""
    bin_index: int
    predicted_prob: float  # Mean predicted probability
    actual_freq: float     # Actual frequency of positive class
    count: int             # Number of samples in bin
    confidence_lower: float
    confidence_upper: float


@dataclass
class CalibrationMetrics:
    """Calibration quality metrics."""
    expected_calibration_error: float  # ECE
    maximum_calibration_error: float   # MCE
    brier_score: float
    log_loss: float
    reliability_score: float  # 1 - ECE (higher is better)


class ProbabilityCalibration:
    """
    Analyze probability calibration for PGM predictions.
    
    Calibration measures how well predicted probabilities match actual outcomes.
    A well-calibrated model predicting 70% probability should be correct 70% of the time.
    """
    
    def __init__(self, n_bins: int = 10):
        """
        Initialize calibration analyzer.
        
        Args:
            n_bins: Number of bins for calibration curve
        """
        self.n_bins = n_bins
        logger.info(f"ProbabilityCalibration initialized with {n_bins} bins")
    
    def compute_calibration_curve(
        self,
        y_true: np.ndarray,
        y_prob: np.ndarray,
        strategy: str = 'uniform'
    ) -> Tuple[List[CalibrationBin], CalibrationMetrics]:
        """
        Compute calibration curve and metrics.
        
        Args:
            y_true: True binary labels (0 or 1)
            y_prob: Predicted probabilities for positive class
            strategy: Binning strategy ('uniform' or 'quantile')
            
        Returns:
            Tuple of (calibration_bins, metrics)
        """
        logger.info(f"Computing calibration curve with {strategy} binning")
        
        # Create bins
        if strategy == 'uniform':
            bins = np.linspace(0, 1, self.n_bins + 1)
        elif strategy == 'quantile':
            bins = np.percentile(y_prob, np.linspace(0, 100, self.n_bins + 1))
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
        
        # Compute calibration for each bin
        calibration_bins = []
        bin_errors = []
        
        for i in range(self.n_bins):
            # Find samples in this bin
            if i == self.n_bins - 1:
                mask = (y_prob >= bins[i]) & (y_prob <= bins[i + 1])
            else:
                mask = (y_prob >= bins[i]) & (y_prob < bins[i + 1])
            
            if mask.sum() == 0:
                continue
            
            # Compute statistics for this bin
            bin_probs = y_prob[mask]
            bin_true = y_true[mask]
            
            mean_pred = bin_probs.mean()
            actual_freq = bin_true.mean()
            count = len(bin_probs)
            
            # Confidence interval (Wilson score interval)
            if count > 0:
                z = 1.96  # 95% confidence
                p = actual_freq
                n = count
                denominator = 1 + z**2 / n
                center = (p + z**2 / (2*n)) / denominator
                margin = z * np.sqrt(p*(1-p)/n + z**2/(4*n**2)) / denominator
                conf_lower = max(0, center - margin)
                conf_upper = min(1, center + margin)
            else:
                conf_lower = actual_freq
                conf_upper = actual_freq
            
            calibration_bins.append(CalibrationBin(
                bin_index=i,
                predicted_prob=float(mean_pred),
                actual_freq=float(actual_freq),
                count=int(count),
                confidence_lower=float(conf_lower),
                confidence_upper=float(conf_upper)
            ))
            
            # Track error for ECE/MCE
            bin_errors.append(abs(mean_pred - actual_freq) * count)
        
        # Compute calibration metrics
        metrics = self._compute_metrics(y_true, y_prob, calibration_bins, bin_errors)
        
        logger.info(f"Calibration curve computed: ECE={metrics.expected_calibration_error:.4f}")
        return calibration_bins, metrics
    
    def _compute_metrics(
        self,
        y_true: np.ndarray,
        y_prob: np.ndarray,
        bins: List[CalibrationBin],
        bin_errors: List[float]
    ) -> CalibrationMetrics:
        """Compute calibration quality metrics."""
        n_samples = len(y_true)
        
        # Expected Calibration Error (ECE)
        ece = sum(bin_errors) / n_samples if n_samples > 0 else 0.0
        
        # Maximum Calibration Error (MCE)
        mce = max([abs(b.predicted_prob - b.actual_freq) for b in bins]) if bins else 0.0
        
        # Brier Score
        brier = np.mean((y_prob - y_true) ** 2)
        
        # Log Loss
        epsilon = 1e-15
        y_prob_clipped = np.clip(y_prob, epsilon, 1 - epsilon)
        log_loss = -np.mean(y_true * np.log(y_prob_clipped) + 
                           (1 - y_true) * np.log(1 - y_prob_clipped))
        
        # Reliability Score (1 - ECE, higher is better)
        reliability = 1.0 - ece
        
        return CalibrationMetrics(
            expected_calibration_error=float(ece),
            maximum_calibration_error=float(mce),
            brier_score=float(brier),
            log_loss=float(log_loss),
            reliability_score=float(reliability)
        )
    
    def analyze_multiclass_calibration(
        self,
        y_true: np.ndarray,
        y_prob: np.ndarray,
        class_names: Optional[List[str]] = None
    ) -> Dict[str, Tuple[List[CalibrationBin], CalibrationMetrics]]:
        """
        Analyze calibration for multiclass predictions.
        
        Args:
            y_true: True class labels (integers)
            y_prob: Predicted probabilities (n_samples, n_classes)
            class_names: Optional class names
            
        Returns:
            Dictionary mapping class name to (bins, metrics)
        """
        n_classes = y_prob.shape[1]
        if class_names is None:
            class_names = [f"Class_{i}" for i in range(n_classes)]
        
        logger.info(f"Analyzing multiclass calibration for {n_classes} classes")
        
        results = {}
        for i, class_name in enumerate(class_names):
            # One-vs-rest for this class
            y_true_binary = (y_true == i).astype(int)
            y_prob_class = y_prob[:, i]
            
            bins, metrics = self.compute_calibration_curve(y_true_binary, y_prob_class)
            results[class_name] = (bins, metrics)
        
        return results
    
    def compute_reliability_diagram_data(
        self,
        y_true: np.ndarray,
        y_prob: np.ndarray
    ) -> Dict:
        """
        Compute data for reliability diagram visualization.
        
        Args:
            y_true: True binary labels
            y_prob: Predicted probabilities
            
        Returns:
            Dictionary with diagram data
        """
        bins, metrics = self.compute_calibration_curve(y_true, y_prob)
        
        # Prepare data for plotting
        bin_data = []
        for b in bins:
            bin_data.append({
                'predicted_prob': b.predicted_prob,
                'actual_freq': b.actual_freq,
                'count': b.count,
                'confidence_lower': b.confidence_lower,
                'confidence_upper': b.confidence_upper,
                'gap': abs(b.predicted_prob - b.actual_freq)
            })
        
        # Perfect calibration line
        perfect_line = [
            {'x': 0.0, 'y': 0.0},
            {'x': 1.0, 'y': 1.0}
        ]
        
        return {
            'bins': bin_data,
            'perfect_line': perfect_line,
            'metrics': {
                'ece': metrics.expected_calibration_error,
                'mce': metrics.maximum_calibration_error,
                'brier_score': metrics.brier_score,
                'log_loss': metrics.log_loss,
                'reliability_score': metrics.reliability_score
            },
            'summary': {
                'total_samples': len(y_true),
                'n_bins': len(bins),
                'mean_predicted_prob': float(y_prob.mean()),
                'actual_positive_rate': float(y_true.mean())
            }
        }
    
    def compare_calibration(
        self,
        models_data: Dict[str, Tuple[np.ndarray, np.ndarray]]
    ) -> pd.DataFrame:
        """
        Compare calibration across multiple models.
        
        Args:
            models_data: Dict mapping model name to (y_true, y_prob)
            
        Returns:
            DataFrame with comparison metrics
        """
        logger.info(f"Comparing calibration for {len(models_data)} models")
        
        results = []
        for model_name, (y_true, y_prob) in models_data.items():
            _, metrics = self.compute_calibration_curve(y_true, y_prob)
            
            results.append({
                'Model': model_name,
                'ECE': metrics.expected_calibration_error,
                'MCE': metrics.maximum_calibration_error,
                'Brier Score': metrics.brier_score,
                'Log Loss': metrics.log_loss,
                'Reliability': metrics.reliability_score
            })
        
        df = pd.DataFrame(results)
        df = df.sort_values('ECE')  # Best calibration first
        
        return df


def create_calibration_analysis(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    n_bins: int = 10
) -> Dict:
    """
    Convenience function to create complete calibration analysis.
    
    Args:
        y_true: True labels
        y_prob: Predicted probabilities
        n_bins: Number of bins
        
    Returns:
        Dictionary with complete analysis
    """
    calibrator = ProbabilityCalibration(n_bins=n_bins)
    
    # Compute calibration curve
    bins, metrics = calibrator.compute_calibration_curve(y_true, y_prob)
    
    # Get reliability diagram data
    diagram_data = calibrator.compute_reliability_diagram_data(y_true, y_prob)
    
    return {
        'calibration_curve': {
            'bins': [
                {
                    'predicted_prob': b.predicted_prob,
                    'actual_freq': b.actual_freq,
                    'count': b.count,
                    'confidence_lower': b.confidence_lower,
                    'confidence_upper': b.confidence_upper
                }
                for b in bins
            ],
            'metrics': {
                'ece': metrics.expected_calibration_error,
                'mce': metrics.maximum_calibration_error,
                'brier_score': metrics.brier_score,
                'log_loss': metrics.log_loss,
                'reliability_score': metrics.reliability_score
            }
        },
        'reliability_diagram': diagram_data,
        'interpretation': _interpret_calibration(metrics)
    }


def _interpret_calibration(metrics: CalibrationMetrics) -> Dict[str, str]:
    """Generate human-readable interpretation of calibration metrics."""
    interpretations = {}
    
    # ECE interpretation
    if metrics.expected_calibration_error < 0.05:
        ece_quality = "Excellent"
        ece_desc = "Model is very well calibrated"
    elif metrics.expected_calibration_error < 0.10:
        ece_quality = "Good"
        ece_desc = "Model has good calibration"
    elif metrics.expected_calibration_error < 0.15:
        ece_quality = "Fair"
        ece_desc = "Model calibration could be improved"
    else:
        ece_quality = "Poor"
        ece_desc = "Model is poorly calibrated"
    
    interpretations['ece'] = {
        'quality': ece_quality,
        'description': ece_desc,
        'value': metrics.expected_calibration_error
    }
    
    # Brier Score interpretation
    if metrics.brier_score < 0.10:
        brier_quality = "Excellent"
    elif metrics.brier_score < 0.20:
        brier_quality = "Good"
    elif metrics.brier_score < 0.30:
        brier_quality = "Fair"
    else:
        brier_quality = "Poor"
    
    interpretations['brier'] = {
        'quality': brier_quality,
        'description': f"Brier score of {metrics.brier_score:.3f}",
        'value': metrics.brier_score
    }
    
    # Overall assessment
    if metrics.reliability_score > 0.90:
        overall = "Model probabilities are highly reliable"
    elif metrics.reliability_score > 0.80:
        overall = "Model probabilities are reliable"
    elif metrics.reliability_score > 0.70:
        overall = "Model probabilities are moderately reliable"
    else:
        overall = "Model probabilities should be used with caution"
    
    interpretations['overall'] = overall
    
    return interpretations

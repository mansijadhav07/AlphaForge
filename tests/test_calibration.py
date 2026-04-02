"""Tests for probability calibration module."""

import pytest
import numpy as np
from backend.models.calibration import (
    ProbabilityCalibration,
    create_calibration_analysis,
    CalibrationMetrics
)


class TestProbabilityCalibration:
    """Test ProbabilityCalibration class."""
    
    def test_initialization(self):
        """Test calibration analyzer initialization."""
        calibrator = ProbabilityCalibration(n_bins=10)
        assert calibrator.n_bins == 10
    
    def test_perfect_calibration(self):
        """Test with perfectly calibrated predictions."""
        np.random.seed(42)
        n_samples = 1000
        
        # Generate perfectly calibrated data
        y_prob = np.random.uniform(0, 1, n_samples)
        y_true = (np.random.uniform(0, 1, n_samples) < y_prob).astype(int)
        
        calibrator = ProbabilityCalibration(n_bins=10)
        bins, metrics = calibrator.compute_calibration_curve(y_true, y_prob)
        
        # Perfect calibration should have low ECE
        assert metrics.expected_calibration_error < 0.15
        assert metrics.reliability_score > 0.85
        assert len(bins) > 0
    
    def test_poor_calibration(self):
        """Test with poorly calibrated predictions."""
        np.random.seed(42)
        n_samples = 1000
        
        # Generate poorly calibrated data (always predict 0.5)
        y_prob = np.full(n_samples, 0.5)
        y_true = np.random.binomial(1, 0.3, n_samples)  # Actual rate is 30%
        
        calibrator = ProbabilityCalibration(n_bins=10)
        bins, metrics = calibrator.compute_calibration_curve(y_true, y_prob)
        
        # Poor calibration should have higher ECE
        assert metrics.expected_calibration_error > 0.05
        assert len(bins) > 0
    
    def test_uniform_binning(self):
        """Test uniform binning strategy."""
        np.random.seed(42)
        y_true = np.random.binomial(1, 0.5, 500)
        y_prob = np.random.uniform(0, 1, 500)
        
        calibrator = ProbabilityCalibration(n_bins=10)
        bins, metrics = calibrator.compute_calibration_curve(
            y_true, y_prob, strategy='uniform'
        )
        
        assert len(bins) <= 10
        assert all(b.count > 0 for b in bins)
    
    def test_quantile_binning(self):
        """Test quantile binning strategy."""
        np.random.seed(42)
        y_true = np.random.binomial(1, 0.5, 500)
        y_prob = np.random.beta(2, 5, 500)  # Skewed distribution
        
        calibrator = ProbabilityCalibration(n_bins=10)
        bins, metrics = calibrator.compute_calibration_curve(
            y_true, y_prob, strategy='quantile'
        )
        
        assert len(bins) <= 10
        # Quantile binning should have more balanced bin sizes
        counts = [b.count for b in bins]
        assert max(counts) / min(counts) < 5  # Not too imbalanced
    
    def test_calibration_metrics(self):
        """Test calibration metrics computation."""
        np.random.seed(42)
        y_true = np.array([0, 0, 1, 1, 0, 1, 1, 0, 1, 0])
        y_prob = np.array([0.1, 0.2, 0.7, 0.8, 0.3, 0.9, 0.6, 0.4, 0.8, 0.2])
        
        calibrator = ProbabilityCalibration(n_bins=5)
        bins, metrics = calibrator.compute_calibration_curve(y_true, y_prob)
        
        # Check all metrics are computed
        assert 0 <= metrics.expected_calibration_error <= 1
        assert 0 <= metrics.maximum_calibration_error <= 1
        assert 0 <= metrics.brier_score <= 1
        assert metrics.log_loss > 0
        assert 0 <= metrics.reliability_score <= 1
    
    def test_confidence_intervals(self):
        """Test confidence interval computation."""
        np.random.seed(42)
        y_true = np.random.binomial(1, 0.5, 200)
        y_prob = np.random.uniform(0, 1, 200)
        
        calibrator = ProbabilityCalibration(n_bins=5)
        bins, _ = calibrator.compute_calibration_curve(y_true, y_prob)
        
        for bin in bins:
            # Confidence intervals should be valid
            assert 0 <= bin.confidence_lower <= bin.actual_freq
            assert bin.actual_freq <= bin.confidence_upper <= 1
            assert bin.confidence_lower < bin.confidence_upper
    
    def test_multiclass_calibration(self):
        """Test multiclass calibration analysis."""
        np.random.seed(42)
        n_samples = 300
        n_classes = 3
        
        # Generate multiclass data
        y_true = np.random.randint(0, n_classes, n_samples)
        y_prob = np.random.dirichlet(np.ones(n_classes), n_samples)
        
        calibrator = ProbabilityCalibration(n_bins=5)
        results = calibrator.analyze_multiclass_calibration(
            y_true, y_prob, class_names=['Class_0', 'Class_1', 'Class_2']
        )
        
        assert len(results) == n_classes
        for class_name, (bins, metrics) in results.items():
            assert len(bins) > 0
            assert isinstance(metrics, CalibrationMetrics)
    
    def test_reliability_diagram_data(self):
        """Test reliability diagram data generation."""
        np.random.seed(42)
        y_true = np.random.binomial(1, 0.5, 200)
        y_prob = np.random.uniform(0, 1, 200)
        
        calibrator = ProbabilityCalibration(n_bins=10)
        diagram_data = calibrator.compute_reliability_diagram_data(y_true, y_prob)
        
        assert 'bins' in diagram_data
        assert 'perfect_line' in diagram_data
        assert 'metrics' in diagram_data
        assert 'summary' in diagram_data
        
        # Check perfect line
        assert len(diagram_data['perfect_line']) == 2
        assert diagram_data['perfect_line'][0] == {'x': 0.0, 'y': 0.0}
        assert diagram_data['perfect_line'][1] == {'x': 1.0, 'y': 1.0}
    
    def test_model_comparison(self):
        """Test calibration comparison across models."""
        np.random.seed(42)
        n_samples = 200
        y_true = np.random.binomial(1, 0.5, n_samples)
        
        # Model 1: Well calibrated
        y_prob1 = np.random.uniform(0, 1, n_samples)
        
        # Model 2: Overconfident
        y_prob2 = np.where(y_true == 1, 0.9, 0.1)
        
        models_data = {
            'Model_1': (y_true, y_prob1),
            'Model_2': (y_true, y_prob2)
        }
        
        calibrator = ProbabilityCalibration(n_bins=5)
        comparison_df = calibrator.compare_calibration(models_data)
        
        assert len(comparison_df) == 2
        assert 'Model' in comparison_df.columns
        assert 'ECE' in comparison_df.columns
        assert 'Reliability' in comparison_df.columns


class TestCalibrationAnalysis:
    """Test calibration analysis convenience function."""
    
    def test_create_calibration_analysis(self):
        """Test complete calibration analysis creation."""
        np.random.seed(42)
        y_true = np.random.binomial(1, 0.5, 200)
        y_prob = np.random.uniform(0, 1, 200)
        
        analysis = create_calibration_analysis(y_true, y_prob, n_bins=10)
        
        assert 'calibration_curve' in analysis
        assert 'reliability_diagram' in analysis
        assert 'interpretation' in analysis
        
        # Check calibration curve
        assert 'bins' in analysis['calibration_curve']
        assert 'metrics' in analysis['calibration_curve']
        
        # Check interpretation
        assert 'ece' in analysis['interpretation']
        assert 'brier' in analysis['interpretation']
        assert 'overall' in analysis['interpretation']
    
    def test_interpretation_quality_levels(self):
        """Test interpretation quality levels."""
        np.random.seed(42)
        
        # Excellent calibration
        y_true = np.random.binomial(1, 0.5, 500)
        y_prob = np.random.uniform(0, 1, 500)
        
        analysis = create_calibration_analysis(y_true, y_prob)
        
        assert 'quality' in analysis['interpretation']['ece']
        assert 'description' in analysis['interpretation']['ece']
        assert analysis['interpretation']['ece']['quality'] in [
            'Excellent', 'Good', 'Fair', 'Poor'
        ]


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_bins(self):
        """Test handling of empty bins."""
        y_true = np.array([0, 0, 1, 1])
        y_prob = np.array([0.1, 0.2, 0.8, 0.9])
        
        calibrator = ProbabilityCalibration(n_bins=20)  # Many bins, few samples
        bins, metrics = calibrator.compute_calibration_curve(y_true, y_prob)
        
        # Should handle empty bins gracefully
        assert len(bins) <= len(y_true)
        assert all(b.count > 0 for b in bins)
    
    def test_single_probability(self):
        """Test with constant probability predictions."""
        y_true = np.array([0, 1, 0, 1, 1, 0])
        y_prob = np.full(6, 0.5)
        
        calibrator = ProbabilityCalibration(n_bins=5)
        bins, metrics = calibrator.compute_calibration_curve(y_true, y_prob)
        
        # Should have only one bin
        assert len(bins) == 1
        assert bins[0].predicted_prob == 0.5
    
    def test_extreme_probabilities(self):
        """Test with extreme probability values."""
        y_true = np.array([0, 0, 1, 1])
        y_prob = np.array([0.0, 0.01, 0.99, 1.0])
        
        calibrator = ProbabilityCalibration(n_bins=5)
        bins, metrics = calibrator.compute_calibration_curve(y_true, y_prob)
        
        # Should handle extreme values
        assert len(bins) > 0
        assert 0 <= metrics.brier_score <= 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

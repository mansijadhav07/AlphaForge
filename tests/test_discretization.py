"""
Tests for improved discretization module.
"""

import pytest
import pandas as pd
import numpy as np
from pgm_model.discretization import (
    FeatureDiscretizer,
    DiscretizationConfig,
    discretize_quantile,
    discretize_kmeans,
    discretize_threshold,
    auto_discretize
)


class TestDiscretizationConfig:
    """Test DiscretizationConfig dataclass."""
    
    def test_valid_config(self):
        """Test valid configuration."""
        config = DiscretizationConfig(
            method='quantile',
            n_bins=3,
            labels=['low', 'medium', 'high']
        )
        assert config.method == 'quantile'
        assert config.n_bins == 3
        assert config.labels == ['low', 'medium', 'high']
    
    def test_invalid_method(self):
        """Test invalid method raises error."""
        with pytest.raises(ValueError, match="Invalid method"):
            DiscretizationConfig(method='invalid', n_bins=3)
    
    def test_label_mismatch(self):
        """Test label count mismatch raises error."""
        with pytest.raises(ValueError, match="Number of labels"):
            DiscretizationConfig(
                method='quantile',
                n_bins=3,
                labels=['low', 'high']  # Only 2 labels for 3 bins
            )


class TestFeatureDiscretizer:
    """Test FeatureDiscretizer class."""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample data for testing."""
        np.random.seed(42)
        return pd.DataFrame({
            'feature1': np.random.normal(50, 10, 1000),
            'feature2': np.random.uniform(0, 100, 1000),
            'feature3': np.random.exponential(2, 1000)
        })
    
    def test_quantile_discretization(self, sample_data):
        """Test quantile-based discretization."""
        discretizer = FeatureDiscretizer()
        config = DiscretizationConfig(
            method='quantile',
            n_bins=3,
            labels=['low', 'medium', 'high']
        )
        
        result = discretizer.fit_transform(sample_data, 'feature1', config)
        
        assert len(result) == len(sample_data)
        assert set(result.unique()) == {'low', 'medium', 'high'}
        
        # Check approximately equal frequencies
        value_counts = result.value_counts()
        assert all(count > 300 for count in value_counts.values())
    
    def test_kmeans_discretization(self, sample_data):
        """Test K-means discretization."""
        discretizer = FeatureDiscretizer()
        config = DiscretizationConfig(
            method='kmeans',
            n_bins=3,
            labels=['cluster1', 'cluster2', 'cluster3']
        )
        
        result = discretizer.fit_transform(sample_data, 'feature1', config)
        
        assert len(result) == len(sample_data)
        assert set(result.unique()) == {'cluster1', 'cluster2', 'cluster3'}
    
    def test_threshold_discretization(self, sample_data):
        """Test threshold-based discretization."""
        discretizer = FeatureDiscretizer()
        config = DiscretizationConfig(
            method='threshold',
            n_bins=3,
            thresholds=[30, 70],
            labels=['low', 'medium', 'high']
        )
        
        result = discretizer.fit_transform(sample_data, 'feature2', config)
        
        assert len(result) == len(sample_data)
        assert set(result.unique()) == {'low', 'medium', 'high'}
    
    def test_equal_width_discretization(self, sample_data):
        """Test equal-width discretization."""
        discretizer = FeatureDiscretizer()
        config = DiscretizationConfig(
            method='equal_width',
            n_bins=4,
            labels=['q1', 'q2', 'q3', 'q4']
        )
        
        result = discretizer.fit_transform(sample_data, 'feature2', config)
        
        assert len(result) == len(sample_data)
        assert set(result.unique()) == {'q1', 'q2', 'q3', 'q4'}
    
    def test_fit_transform_separately(self, sample_data):
        """Test fit and transform as separate steps."""
        discretizer = FeatureDiscretizer()
        config = DiscretizationConfig(method='quantile', n_bins=3)
        
        # Fit on training data
        train_data = sample_data.iloc[:800]
        discretizer.fit(train_data, 'feature1', config)
        
        # Transform test data
        test_data = sample_data.iloc[800:]
        result = discretizer.transform(test_data, 'feature1')
        
        assert len(result) == len(test_data)
        assert all(label in ['q1', 'q2', 'q3'] for label in result.unique())
    
    def test_get_bin_info(self, sample_data):
        """Test getting bin information."""
        discretizer = FeatureDiscretizer()
        config = DiscretizationConfig(
            method='quantile',
            n_bins=3,
            labels=['low', 'medium', 'high']
        )
        
        discretizer.fit(sample_data, 'feature1', config)
        bin_info = discretizer.get_bin_info('feature1')
        
        assert len(bin_info) == 3
        assert list(bin_info.columns) == ['bin', 'label', 'lower', 'upper', 'range']
        assert list(bin_info['label']) == ['low', 'medium', 'high']
    
    def test_get_feature_info(self, sample_data):
        """Test getting complete feature information."""
        discretizer = FeatureDiscretizer()
        config = DiscretizationConfig(method='quantile', n_bins=3)
        
        discretizer.fit(sample_data, 'feature1', config)
        info = discretizer.get_feature_info('feature1')
        
        assert 'config' in info
        assert 'stats' in info
        assert 'bin_info' in info
        assert info['config']['method'] == 'quantile'
        assert 'mean' in info['stats']
    
    def test_handle_missing_values(self, sample_data):
        """Test handling of missing values."""
        data_with_nan = sample_data.copy()
        data_with_nan.loc[0:10, 'feature1'] = np.nan
        
        discretizer = FeatureDiscretizer()
        config = DiscretizationConfig(method='quantile', n_bins=3)
        
        result = discretizer.fit_transform(data_with_nan, 'feature1', config)
        
        assert result.isna().sum() == 11  # NaN values preserved


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    @pytest.fixture
    def sample_series(self):
        """Create sample series."""
        np.random.seed(42)
        return pd.Series(np.random.normal(50, 10, 100), name='test_feature')
    
    def test_discretize_quantile(self, sample_series):
        """Test quantile discretization convenience function."""
        result = discretize_quantile(sample_series, n_bins=4)
        
        assert len(result) == len(sample_series)
        assert len(result.unique()) == 4
    
    def test_discretize_kmeans(self, sample_series):
        """Test K-means discretization convenience function."""
        result = discretize_kmeans(sample_series, n_bins=3)
        
        assert len(result) == len(sample_series)
        assert len(result.unique()) == 3
    
    def test_discretize_threshold(self, sample_series):
        """Test threshold discretization convenience function."""
        result = discretize_threshold(
            sample_series,
            thresholds=[40, 50, 60],
            labels=['very_low', 'low', 'high', 'very_high']
        )
        
        assert len(result) == len(sample_series)
        assert set(result.unique()).issubset({'very_low', 'low', 'high', 'very_high'})
    
    def test_auto_discretize(self, sample_series):
        """Test automatic discretization."""
        result, info = auto_discretize(sample_series, n_bins=3)
        
        assert len(result) == len(sample_series)
        assert 'config' in info
        assert 'stats' in info
        assert info['config']['method'] in ['quantile', 'kmeans', 'equal_width']


class TestRealWorldScenarios:
    """Test real-world scenarios."""
    
    def test_rsi_discretization(self):
        """Test RSI discretization (0-100 range)."""
        np.random.seed(42)
        rsi_data = pd.DataFrame({
            'RSI': np.random.uniform(0, 100, 500)
        })
        
        discretizer = FeatureDiscretizer()
        config = DiscretizationConfig(
            method='threshold',
            n_bins=3,
            thresholds=[30, 70],
            labels=['oversold', 'neutral', 'overbought']
        )
        
        result = discretizer.fit_transform(rsi_data, 'RSI', config)
        
        assert set(result.unique()) == {'oversold', 'neutral', 'overbought'}
        
        # Check thresholds are correct
        oversold = rsi_data[result == 'oversold']['RSI']
        assert all(oversold <= 30)
        
        overbought = rsi_data[result == 'overbought']['RSI']
        assert all(overbought > 70)
    
    def test_return_discretization(self):
        """Test return discretization (symmetric around 0)."""
        np.random.seed(42)
        returns = pd.DataFrame({
            'return': np.random.normal(0, 0.02, 1000)
        })
        
        discretizer = FeatureDiscretizer()
        config = DiscretizationConfig(
            method='threshold',
            n_bins=3,
            thresholds=[-0.01, 0.01],
            labels=['negative', 'neutral', 'positive']
        )
        
        result = discretizer.fit_transform(returns, 'return', config)
        
        assert set(result.unique()) == {'negative', 'neutral', 'positive'}
    
    def test_volatility_discretization(self):
        """Test volatility discretization (quantile-based)."""
        np.random.seed(42)
        volatility = pd.DataFrame({
            'volatility': np.random.exponential(0.02, 1000)
        })
        
        discretizer = FeatureDiscretizer()
        config = DiscretizationConfig(
            method='quantile',
            n_bins=3,
            labels=['low', 'medium', 'high']
        )
        
        result = discretizer.fit_transform(volatility, 'volatility', config)
        
        # Check equal frequencies
        value_counts = result.value_counts()
        assert all(count > 300 for count in value_counts.values())


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

"""
Example usage of improved discretization module.

Demonstrates:
- Quantile-based binning
- K-means clustering
- Data-driven thresholds
- Configurable bins
- Reusable functions
"""

import sys
sys.path.insert(0, '.')

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


def example_1_quantile_binning():
    """Example 1: Quantile-based binning for equal frequency."""
    print("=" * 80)
    print("Example 1: Quantile-Based Binning")
    print("=" * 80)
    
    # Generate sample data (volatility-like)
    np.random.seed(42)
    data = pd.DataFrame({
        'volatility': np.random.exponential(0.02, 1000)
    })
    
    # Create discretizer
    discretizer = FeatureDiscretizer()
    config = DiscretizationConfig(
        method='quantile',
        n_bins=3,
        labels=['low', 'medium', 'high']
    )
    
    # Fit and transform
    result = discretizer.fit_transform(data, 'volatility', config)
    
    # Show results
    print(f"\nOriginal data range: [{data['volatility'].min():.4f}, {data['volatility'].max():.4f}]")
    print(f"\nValue counts (equal frequency):")
    print(result.value_counts().sort_index())
    
    # Show bin information
    print(f"\nBin edges:")
    bin_info = discretizer.get_bin_info('volatility')
    print(bin_info.to_string(index=False))
    
    print("\n✓ Quantile binning ensures equal frequency in each bin\n")


def example_2_kmeans_clustering():
    """Example 2: K-means clustering for natural groupings."""
    print("=" * 80)
    print("Example 2: K-Means Clustering")
    print("=" * 80)
    
    # Generate sample data with natural clusters
    np.random.seed(42)
    cluster1 = np.random.normal(30, 5, 300)
    cluster2 = np.random.normal(50, 5, 400)
    cluster3 = np.random.normal(70, 5, 300)
    
    data = pd.DataFrame({
        'feature': np.concatenate([cluster1, cluster2, cluster3])
    })
    
    # Use K-means discretization
    result = discretize_kmeans(data['feature'], n_bins=3, labels=['low', 'medium', 'high'])
    
    print(f"\nOriginal data range: [{data['feature'].min():.4f}, {data['feature'].max():.4f}]")
    print(f"\nValue counts:")
    print(result.value_counts().sort_index())
    
    print("\n✓ K-means finds natural clusters in the data\n")


def example_3_data_driven_thresholds():
    """Example 3: Data-driven thresholds using statistics."""
    print("=" * 80)
    print("Example 3: Data-Driven Thresholds")
    print("=" * 80)
    
    # Generate sample data
    np.random.seed(42)
    data = pd.DataFrame({
        'momentum': np.random.normal(0, 1, 1000)
    })
    
    # Calculate data-driven thresholds (mean ± 0.5 std)
    mean = data['momentum'].mean()
    std = data['momentum'].std()
    thresholds = [mean - 0.5 * std, mean + 0.5 * std]
    
    print(f"\nData statistics:")
    print(f"  Mean: {mean:.4f}")
    print(f"  Std:  {std:.4f}")
    print(f"\nData-driven thresholds: {[f'{t:.4f}' for t in thresholds]}")
    
    # Apply discretization
    result = discretize_threshold(
        data['momentum'],
        thresholds=thresholds,
        labels=['weak', 'moderate', 'strong']
    )
    
    print(f"\nValue counts:")
    print(result.value_counts().sort_index())
    
    print("\n✓ Thresholds adapt to data distribution\n")


def example_4_configurable_bins():
    """Example 4: Configurable number of bins."""
    print("=" * 80)
    print("Example 4: Configurable Bins")
    print("=" * 80)
    
    # Generate sample data
    np.random.seed(42)
    data = pd.DataFrame({
        'price': np.random.uniform(100, 200, 1000)
    })
    
    # Try different bin configurations
    for n_bins in [3, 5, 7]:
        result = discretize_quantile(data['price'], n_bins=n_bins)
        
        print(f"\n{n_bins} bins:")
        print(f"  Unique values: {result.nunique()}")
        print(f"  Distribution: {dict(result.value_counts().sort_index())}")
    
    print("\n✓ Easily configure number of bins\n")


def example_5_reusable_discretizer():
    """Example 5: Reusable discretizer for train/test split."""
    print("=" * 80)
    print("Example 5: Reusable Discretizer (Train/Test)")
    print("=" * 80)
    
    # Generate sample data
    np.random.seed(42)
    data = pd.DataFrame({
        'feature': np.random.normal(50, 10, 1000)
    })
    
    # Split into train/test
    train_data = data.iloc[:800]
    test_data = data.iloc[800:]
    
    # Fit on training data
    discretizer = FeatureDiscretizer()
    config = DiscretizationConfig(
        method='quantile',
        n_bins=3,
        labels=['low', 'medium', 'high']
    )
    
    discretizer.fit(train_data, 'feature', config)
    
    print(f"\nTrained on {len(train_data)} samples")
    print(f"\nBin edges (from training data):")
    print(discretizer.get_bin_info('feature').to_string(index=False))
    
    # Transform test data using same thresholds
    test_result = discretizer.transform(test_data, 'feature')
    
    print(f"\nTest data distribution:")
    print(test_result.value_counts().sort_index())
    
    print("\n✓ Same discretization applied to train and test data\n")


def example_6_auto_discretization():
    """Example 6: Automatic method selection."""
    print("=" * 80)
    print("Example 6: Automatic Discretization")
    print("=" * 80)
    
    # Generate different types of data
    np.random.seed(42)
    
    datasets = {
        'normal': np.random.normal(50, 10, 1000),
        'exponential': np.random.exponential(2, 1000),
        'uniform': np.random.uniform(0, 100, 1000),
        'bimodal': np.concatenate([
            np.random.normal(30, 5, 500),
            np.random.normal(70, 5, 500)
        ])
    }
    
    for name, values in datasets.items():
        series = pd.Series(values, name=name)
        result, info = auto_discretize(series, n_bins=3)
        
        print(f"\n{name.capitalize()} distribution:")
        print(f"  Auto-selected method: {info['config']['method']}")
        print(f"  Thresholds: {[f'{t:.2f}' for t in info['config']['thresholds']]}")
        print(f"  Distribution: {dict(result.value_counts())}")
    
    print("\n✓ Automatically selects best method for data\n")


def example_7_financial_features():
    """Example 7: Real financial feature discretization."""
    print("=" * 80)
    print("Example 7: Financial Features")
    print("=" * 80)
    
    np.random.seed(42)
    
    # Simulate financial features
    financial_data = pd.DataFrame({
        'RSI': np.random.uniform(0, 100, 1000),
        'return': np.random.normal(0, 0.02, 1000),
        'volatility': np.random.exponential(0.02, 1000),
        'volume_ratio': np.random.lognormal(0, 0.5, 1000)
    })
    
    discretizer = FeatureDiscretizer()
    
    # RSI: Fixed thresholds (domain knowledge)
    rsi_config = DiscretizationConfig(
        method='threshold',
        n_bins=3,
        thresholds=[30, 70],
        labels=['oversold', 'neutral', 'overbought']
    )
    rsi_discrete = discretizer.fit_transform(financial_data, 'RSI', rsi_config)
    
    print("\nRSI (threshold-based):")
    print(rsi_discrete.value_counts().sort_index())
    
    # Return: Symmetric thresholds
    return_config = DiscretizationConfig(
        method='threshold',
        n_bins=3,
        thresholds=[-0.01, 0.01],
        labels=['negative', 'neutral', 'positive']
    )
    return_discrete = discretizer.fit_transform(financial_data, 'return', return_config)
    
    print("\nReturn (threshold-based):")
    print(return_discrete.value_counts().sort_index())
    
    # Volatility: Quantile-based (data-driven)
    vol_config = DiscretizationConfig(
        method='quantile',
        n_bins=3,
        labels=['low', 'medium', 'high']
    )
    vol_discrete = discretizer.fit_transform(financial_data, 'volatility', vol_config)
    
    print("\nVolatility (quantile-based):")
    print(vol_discrete.value_counts().sort_index())
    print(f"Bin edges: {discretizer.get_bin_edges('volatility')}")
    
    # Volume ratio: K-means (natural clusters)
    volume_config = DiscretizationConfig(
        method='kmeans',
        n_bins=3,
        labels=['low', 'normal', 'high']
    )
    volume_discrete = discretizer.fit_transform(financial_data, 'volume_ratio', volume_config)
    
    print("\nVolume Ratio (K-means):")
    print(volume_discrete.value_counts().sort_index())
    
    print("\n✓ Different methods for different feature types\n")


def main():
    """Run all examples."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "DISCRETIZATION MODULE EXAMPLES" + " " * 28 + "║")
    print("╚" + "=" * 78 + "╝")
    print("\n")
    
    examples = [
        example_1_quantile_binning,
        example_2_kmeans_clustering,
        example_3_data_driven_thresholds,
        example_4_configurable_bins,
        example_5_reusable_discretizer,
        example_6_auto_discretization,
        example_7_financial_features
    ]
    
    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"\n✗ Error in {example.__name__}: {e}\n")
    
    print("=" * 80)
    print("All examples completed!")
    print("=" * 80)


if __name__ == '__main__':
    main()

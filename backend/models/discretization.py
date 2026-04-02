"""
Improved Feature Discretization Module for PGM.

Provides flexible, data-driven discretization methods:
- Quantile-based binning
- Data-driven thresholds
- Configurable bins
- Reusable functions
"""

from typing import Dict, List, Optional, Tuple, Union
import pandas as pd
import numpy as np
from dataclasses import dataclass
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class DiscretizationConfig:
    """Configuration for feature discretization."""
    method: str  # 'quantile', 'kmeans', 'threshold', 'equal_width'
    n_bins: int = 3
    labels: Optional[List[str]] = None
    thresholds: Optional[List[float]] = None
    quantiles: Optional[List[float]] = None
    
    def __post_init__(self):
        """Validate configuration."""
        if self.method not in ['quantile', 'kmeans', 'threshold', 'equal_width', 'custom']:
            raise ValueError(f"Invalid method: {self.method}")
        
        if self.labels and len(self.labels) != self.n_bins:
            raise ValueError(f"Number of labels ({len(self.labels)}) must match n_bins ({self.n_bins})")


class FeatureDiscretizer:
    """
    Flexible feature discretization with data-driven methods.
    
    Supports:
    - Quantile-based binning (equal frequency)
    - K-means clustering
    - Fixed thresholds
    - Equal-width binning
    - Custom discretization functions
    """
    
    def __init__(self):
        """Initialize discretizer."""
        self.fitted_configs: Dict[str, Dict] = {}
        self.feature_stats: Dict[str, Dict] = {}
        logger.info("FeatureDiscretizer initialized")
    
    def fit(self, 
            df: pd.DataFrame, 
            feature: str, 
            config: DiscretizationConfig) -> 'FeatureDiscretizer':
        """
        Fit discretization parameters to data.
        
        Args:
            df: DataFrame with feature data
            feature: Feature name to discretize
            config: Discretization configuration
            
        Returns:
            Self for chaining
        """
        if feature not in df.columns:
            raise ValueError(f"Feature '{feature}' not found in DataFrame")
        
        series = df[feature].dropna()
        
        if len(series) == 0:
            raise ValueError(f"No valid data for feature '{feature}'")
        
        logger.info(f"Fitting discretization for '{feature}' using method '{config.method}'")
        
        # Store feature statistics
        self.feature_stats[feature] = {
            'mean': float(series.mean()),
            'std': float(series.std()),
            'min': float(series.min()),
            'max': float(series.max()),
            'median': float(series.median()),
            'q25': float(series.quantile(0.25)),
            'q75': float(series.quantile(0.75))
        }
        
        # Fit based on method
        if config.method == 'quantile':
            fitted = self._fit_quantile(series, config)
        elif config.method == 'kmeans':
            fitted = self._fit_kmeans(series, config)
        elif config.method == 'threshold':
            fitted = self._fit_threshold(series, config)
        elif config.method == 'equal_width':
            fitted = self._fit_equal_width(series, config)
        else:
            fitted = {'method': config.method, 'config': config}
        
        self.fitted_configs[feature] = fitted
        
        logger.info(f"Discretization fitted for '{feature}': {fitted.get('thresholds', 'N/A')}")
        
        return self
    
    def transform(self, 
                  df: pd.DataFrame, 
                  feature: str,
                  handle_unseen: str = 'nearest') -> pd.Series:
        """
        Transform feature using fitted discretization.
        
        Args:
            df: DataFrame with feature data
            feature: Feature name to discretize
            handle_unseen: How to handle values outside fitted range
                          ('nearest', 'clip', 'nan')
            
        Returns:
            Series with discretized values
        """
        if feature not in self.fitted_configs:
            raise ValueError(f"Feature '{feature}' not fitted. Call fit() first.")
        
        if feature not in df.columns:
            raise ValueError(f"Feature '{feature}' not found in DataFrame")
        
        series = df[feature]
        config = self.fitted_configs[feature]
        
        logger.debug(f"Transforming '{feature}' using method '{config['method']}'")
        
        if config['method'] in ['quantile', 'threshold', 'equal_width']:
            return self._transform_threshold_based(series, config, handle_unseen)
        elif config['method'] == 'kmeans':
            return self._transform_kmeans(series, config, handle_unseen)
        else:
            raise ValueError(f"Unknown method: {config['method']}")
    
    def fit_transform(self,
                     df: pd.DataFrame,
                     feature: str,
                     config: DiscretizationConfig,
                     handle_unseen: str = 'nearest') -> pd.Series:
        """
        Fit and transform in one step.
        
        Args:
            df: DataFrame with feature data
            feature: Feature name to discretize
            config: Discretization configuration
            handle_unseen: How to handle values outside fitted range
            
        Returns:
            Series with discretized values
        """
        self.fit(df, feature, config)
        return self.transform(df, feature, handle_unseen)
    
    def _fit_quantile(self, series: pd.Series, config: DiscretizationConfig) -> Dict:
        """Fit quantile-based discretization."""
        if config.quantiles:
            quantiles = config.quantiles
        else:
            # Create equal-frequency bins
            quantiles = [i / config.n_bins for i in range(config.n_bins + 1)]
        
        thresholds = [series.quantile(q) for q in quantiles[1:-1]]
        
        # Handle duplicate thresholds (can happen with discrete data)
        thresholds = sorted(list(set(thresholds)))
        
        # Adjust n_bins if we have fewer unique thresholds
        actual_n_bins = len(thresholds) + 1
        
        labels = config.labels
        if labels and len(labels) != actual_n_bins:
            logger.warning(f"Adjusting labels from {len(labels)} to {actual_n_bins} bins")
            labels = labels[:actual_n_bins] if len(labels) > actual_n_bins else labels + [f'bin_{i}' for i in range(len(labels), actual_n_bins)]
        elif not labels:
            labels = [f'q{i+1}' for i in range(actual_n_bins)]
        
        return {
            'method': 'quantile',
            'thresholds': thresholds,
            'labels': labels,
            'n_bins': actual_n_bins,
            'quantiles': quantiles
        }
    
    def _fit_kmeans(self, series: pd.Series, config: DiscretizationConfig) -> Dict:
        """Fit K-means clustering discretization."""
        from sklearn.cluster import KMeans
        
        X = series.values.reshape(-1, 1)
        kmeans = KMeans(n_clusters=config.n_bins, random_state=42, n_init=10)
        kmeans.fit(X)
        
        # Get cluster centers and sort them
        centers = sorted(kmeans.cluster_centers_.flatten())
        
        # Create thresholds as midpoints between centers
        thresholds = [(centers[i] + centers[i+1]) / 2 for i in range(len(centers) - 1)]
        
        labels = config.labels or [f'cluster_{i}' for i in range(config.n_bins)]
        
        return {
            'method': 'kmeans',
            'thresholds': thresholds,
            'labels': labels,
            'n_bins': config.n_bins,
            'centers': centers
        }
    
    def _fit_threshold(self, series: pd.Series, config: DiscretizationConfig) -> Dict:
        """Fit fixed threshold discretization."""
        if not config.thresholds:
            raise ValueError("Thresholds must be provided for 'threshold' method")
        
        thresholds = sorted(config.thresholds)
        n_bins = len(thresholds) + 1
        
        labels = config.labels or [f'bin_{i}' for i in range(n_bins)]
        
        return {
            'method': 'threshold',
            'thresholds': thresholds,
            'labels': labels,
            'n_bins': n_bins
        }
    
    def _fit_equal_width(self, series: pd.Series, config: DiscretizationConfig) -> Dict:
        """Fit equal-width binning."""
        min_val = series.min()
        max_val = series.max()
        
        width = (max_val - min_val) / config.n_bins
        thresholds = [min_val + width * (i + 1) for i in range(config.n_bins - 1)]
        
        labels = config.labels or [f'bin_{i}' for i in range(config.n_bins)]
        
        return {
            'method': 'equal_width',
            'thresholds': thresholds,
            'labels': labels,
            'n_bins': config.n_bins,
            'width': width
        }
    
    def _transform_threshold_based(self, 
                                   series: pd.Series, 
                                   config: Dict,
                                   handle_unseen: str) -> pd.Series:
        """Transform using threshold-based discretization."""
        thresholds = config['thresholds']
        labels = config['labels']
        
        result = pd.Series(index=series.index, dtype='object')
        
        for idx, value in series.items():
            if pd.isna(value):
                result[idx] = np.nan
                continue
            
            # Find bin
            bin_idx = 0
            for threshold in thresholds:
                if value <= threshold:
                    break
                bin_idx += 1
            
            # Handle out-of-range values
            if handle_unseen == 'clip':
                bin_idx = max(0, min(bin_idx, len(labels) - 1))
            elif handle_unseen == 'nearest':
                bin_idx = max(0, min(bin_idx, len(labels) - 1))
            elif handle_unseen == 'nan' and (bin_idx < 0 or bin_idx >= len(labels)):
                result[idx] = np.nan
                continue
            
            result[idx] = labels[bin_idx]
        
        return result
    
    def _transform_kmeans(self, 
                         series: pd.Series, 
                         config: Dict,
                         handle_unseen: str) -> pd.Series:
        """Transform using K-means discretization."""
        # K-means uses threshold-based assignment after fitting
        return self._transform_threshold_based(series, config, handle_unseen)
    
    def get_bin_edges(self, feature: str) -> List[float]:
        """
        Get bin edges for a fitted feature.
        
        Args:
            feature: Feature name
            
        Returns:
            List of bin edges including min and max
        """
        if feature not in self.fitted_configs:
            raise ValueError(f"Feature '{feature}' not fitted")
        
        config = self.fitted_configs[feature]
        stats = self.feature_stats[feature]
        
        edges = [stats['min']] + config['thresholds'] + [stats['max']]
        return edges
    
    def get_bin_info(self, feature: str) -> pd.DataFrame:
        """
        Get detailed bin information for a feature.
        
        Args:
            feature: Feature name
            
        Returns:
            DataFrame with bin information
        """
        if feature not in self.fitted_configs:
            raise ValueError(f"Feature '{feature}' not fitted")
        
        config = self.fitted_configs[feature]
        edges = self.get_bin_edges(feature)
        
        bin_info = []
        for i, label in enumerate(config['labels']):
            bin_info.append({
                'bin': i,
                'label': label,
                'lower': edges[i],
                'upper': edges[i + 1],
                'range': f"({edges[i]:.4f}, {edges[i+1]:.4f}]"
            })
        
        return pd.DataFrame(bin_info)
    
    def get_feature_info(self, feature: str) -> Dict:
        """
        Get complete information about a fitted feature.
        
        Args:
            feature: Feature name
            
        Returns:
            Dictionary with feature information
        """
        if feature not in self.fitted_configs:
            raise ValueError(f"Feature '{feature}' not fitted")
        
        return {
            'config': self.fitted_configs[feature],
            'stats': self.feature_stats[feature],
            'bin_info': self.get_bin_info(feature).to_dict('records')
        }


# ============================================================================
# Convenience Functions
# ============================================================================

def discretize_quantile(series: pd.Series, 
                       n_bins: int = 3,
                       labels: Optional[List[str]] = None) -> pd.Series:
    """
    Quick quantile-based discretization.
    
    Args:
        series: Series to discretize
        n_bins: Number of bins
        labels: Bin labels
        
    Returns:
        Discretized series
    """
    discretizer = FeatureDiscretizer()
    config = DiscretizationConfig(method='quantile', n_bins=n_bins, labels=labels)
    
    df = pd.DataFrame({series.name or 'feature': series})
    return discretizer.fit_transform(df, series.name or 'feature', config)


def discretize_kmeans(series: pd.Series,
                     n_bins: int = 3,
                     labels: Optional[List[str]] = None) -> pd.Series:
    """
    Quick K-means discretization.
    
    Args:
        series: Series to discretize
        n_bins: Number of clusters
        labels: Cluster labels
        
    Returns:
        Discretized series
    """
    discretizer = FeatureDiscretizer()
    config = DiscretizationConfig(method='kmeans', n_bins=n_bins, labels=labels)
    
    df = pd.DataFrame({series.name or 'feature': series})
    return discretizer.fit_transform(df, series.name or 'feature', config)


def discretize_threshold(series: pd.Series,
                        thresholds: List[float],
                        labels: Optional[List[str]] = None) -> pd.Series:
    """
    Quick threshold-based discretization.
    
    Args:
        series: Series to discretize
        thresholds: Threshold values
        labels: Bin labels
        
    Returns:
        Discretized series
    """
    discretizer = FeatureDiscretizer()
    n_bins = len(thresholds) + 1
    config = DiscretizationConfig(
        method='threshold', 
        n_bins=n_bins, 
        thresholds=thresholds,
        labels=labels
    )
    
    df = pd.DataFrame({series.name or 'feature': series})
    return discretizer.fit_transform(df, series.name or 'feature', config)


def auto_discretize(series: pd.Series,
                   n_bins: int = 3,
                   method: str = 'auto',
                   labels: Optional[List[str]] = None) -> Tuple[pd.Series, Dict]:
    """
    Automatically choose and apply best discretization method.
    
    Args:
        series: Series to discretize
        n_bins: Number of bins
        method: 'auto', 'quantile', 'kmeans', or 'equal_width'
        labels: Bin labels
        
    Returns:
        Tuple of (discretized series, discretization info)
    """
    if method == 'auto':
        # Choose method based on data characteristics
        unique_ratio = len(series.unique()) / len(series)
        
        if unique_ratio < 0.05:
            # Very few unique values, use equal width
            method = 'equal_width'
        elif series.std() / series.mean() > 1.0:
            # High variance, use quantile
            method = 'quantile'
        else:
            # Moderate variance, use kmeans
            method = 'kmeans'
        
        logger.info(f"Auto-selected method '{method}' for series (unique_ratio={unique_ratio:.3f})")
    
    discretizer = FeatureDiscretizer()
    config = DiscretizationConfig(method=method, n_bins=n_bins, labels=labels)
    
    df = pd.DataFrame({series.name or 'feature': series})
    feature_name = series.name or 'feature'
    
    result = discretizer.fit_transform(df, feature_name, config)
    info = discretizer.get_feature_info(feature_name)
    
    return result, info

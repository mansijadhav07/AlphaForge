"""
Discretization API Routes for AlphaForge.

Exposes discretization functionality via REST APIs.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, List, Optional
import pandas as pd
import numpy as np

from api.schemas import ErrorResponse
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/discretization", tags=["discretization"])


@router.get(
    "/demo",
    summary="Discretization Demo",
    description="""
    Demonstrate different discretization methods on sample data.
    
    Shows how different methods (quantile, kmeans, threshold, equal_width)
    discretize the same data differently.
    """,
    responses={
        200: {"description": "Discretization demo results"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def get_discretization_demo(
    feature: str = Query("volatility", description="Feature type to demo"),
    n_samples: int = Query(1000, description="Number of samples", ge=100, le=10000)
) -> Dict:
    """
    Get discretization demo for different methods.
    
    Args:
        feature: Feature type (volatility, rsi, return, momentum)
        n_samples: Number of samples to generate
        
    Returns:
        Demo results with different discretization methods
    """
    try:
        logger.info(f"Generating discretization demo for {feature}")
        
        from pgm_model.discretization import (
            FeatureDiscretizer,
            DiscretizationConfig
        )
        
        # Generate sample data based on feature type
        np.random.seed(42)
        
        if feature == 'volatility':
            data = np.random.exponential(0.02, n_samples)
            feature_name = 'Volatility'
            unit = '%'
        elif feature == 'rsi':
            data = np.random.uniform(0, 100, n_samples)
            feature_name = 'RSI'
            unit = ''
        elif feature == 'return':
            data = np.random.normal(0, 0.02, n_samples)
            feature_name = 'Return'
            unit = '%'
        elif feature == 'momentum':
            # Bimodal distribution
            data = np.concatenate([
                np.random.normal(-0.5, 0.2, n_samples // 2),
                np.random.normal(0.5, 0.2, n_samples // 2)
            ])
            feature_name = 'Momentum Score'
            unit = ''
        else:
            data = np.random.normal(50, 10, n_samples)
            feature_name = feature.capitalize()
            unit = ''
        
        df = pd.DataFrame({feature: data})
        
        # Apply different discretization methods
        discretizer = FeatureDiscretizer()
        
        methods = []
        
        # Method 1: Quantile
        config_quantile = DiscretizationConfig(
            method='quantile',
            n_bins=3,
            labels=['low', 'medium', 'high']
        )
        result_quantile = discretizer.fit_transform(df, feature, config_quantile)
        quantile_info = discretizer.get_feature_info(feature)
        
        methods.append({
            'method': 'quantile',
            'name': 'Quantile-Based',
            'description': 'Equal frequency bins',
            'thresholds': [float(t) for t in quantile_info['config']['thresholds']],
            'bins': quantile_info['bin_info'],
            'distribution': result_quantile.value_counts().to_dict(),
            'stats': quantile_info['stats']
        })
        
        # Method 2: K-means
        try:
            config_kmeans = DiscretizationConfig(
                method='kmeans',
                n_bins=3,
                labels=['cluster1', 'cluster2', 'cluster3']
            )
            result_kmeans = discretizer.fit_transform(df, feature, config_kmeans)
            kmeans_info = discretizer.get_feature_info(feature)
            
            methods.append({
                'method': 'kmeans',
                'name': 'K-Means Clustering',
                'description': 'Natural cluster detection',
                'thresholds': [float(t) for t in kmeans_info['config']['thresholds']],
                'bins': kmeans_info['bin_info'],
                'distribution': result_kmeans.value_counts().to_dict(),
                'stats': kmeans_info['stats']
            })
        except Exception as e:
            logger.warning(f"K-means failed: {e}")
        
        # Method 3: Equal-width
        config_equal = DiscretizationConfig(
            method='equal_width',
            n_bins=3,
            labels=['bin1', 'bin2', 'bin3']
        )
        result_equal = discretizer.fit_transform(df, feature, config_equal)
        equal_info = discretizer.get_feature_info(feature)
        
        methods.append({
            'method': 'equal_width',
            'name': 'Equal-Width',
            'description': 'Equal-sized intervals',
            'thresholds': [float(t) for t in equal_info['config']['thresholds']],
            'bins': equal_info['bin_info'],
            'distribution': result_equal.value_counts().to_dict(),
            'stats': equal_info['stats']
        })
        
        # Method 4: Threshold (domain-specific)
        if feature == 'rsi':
            thresholds = [30, 70]
            labels = ['oversold', 'neutral', 'overbought']
        elif feature == 'return':
            thresholds = [-0.01, 0.01]
            labels = ['negative', 'neutral', 'positive']
        else:
            # Use data-driven thresholds
            mean = df[feature].mean()
            std = df[feature].std()
            thresholds = [mean - 0.5 * std, mean + 0.5 * std]
            labels = ['low', 'medium', 'high']
        
        config_threshold = DiscretizationConfig(
            method='threshold',
            n_bins=len(thresholds) + 1,
            thresholds=thresholds,
            labels=labels
        )
        result_threshold = discretizer.fit_transform(df, feature, config_threshold)
        threshold_info = discretizer.get_feature_info(feature)
        
        methods.append({
            'method': 'threshold',
            'name': 'Threshold-Based',
            'description': 'Fixed or data-driven thresholds',
            'thresholds': [float(t) for t in threshold_info['config']['thresholds']],
            'bins': threshold_info['bin_info'],
            'distribution': result_threshold.value_counts().to_dict(),
            'stats': threshold_info['stats']
        })
        
        # Generate histogram data
        hist, bin_edges = np.histogram(data, bins=50)
        histogram = {
            'counts': hist.tolist(),
            'edges': bin_edges.tolist()
        }
        
        return {
            'feature': feature_name,
            'unit': unit,
            'n_samples': n_samples,
            'data_stats': {
                'min': float(df[feature].min()),
                'max': float(df[feature].max()),
                'mean': float(df[feature].mean()),
                'median': float(df[feature].median()),
                'std': float(df[feature].std()),
                'q25': float(df[feature].quantile(0.25)),
                'q75': float(df[feature].quantile(0.75))
            },
            'histogram': histogram,
            'methods': methods
        }
        
    except Exception as e:
        logger.error(f"Error in discretization demo: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate discretization demo: {str(e)}"
        )


@router.get(
    "/compare",
    summary="Compare Discretization Methods",
    description="""
    Compare different discretization methods side-by-side.
    
    Useful for understanding which method works best for your data.
    """,
    responses={
        200: {"description": "Comparison results"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def compare_methods(
    n_bins: int = Query(3, description="Number of bins", ge=2, le=10)
) -> Dict:
    """
    Compare discretization methods across different data distributions.
    
    Args:
        n_bins: Number of bins for discretization
        
    Returns:
        Comparison results
    """
    try:
        logger.info(f"Comparing discretization methods with {n_bins} bins")
        
        from pgm_model.discretization import (
            FeatureDiscretizer,
            DiscretizationConfig
        )
        
        np.random.seed(42)
        
        # Different data distributions
        distributions = {
            'normal': {
                'name': 'Normal Distribution',
                'data': np.random.normal(50, 10, 1000)
            },
            'exponential': {
                'name': 'Exponential (Skewed)',
                'data': np.random.exponential(2, 1000)
            },
            'uniform': {
                'name': 'Uniform Distribution',
                'data': np.random.uniform(0, 100, 1000)
            },
            'bimodal': {
                'name': 'Bimodal Distribution',
                'data': np.concatenate([
                    np.random.normal(30, 5, 500),
                    np.random.normal(70, 5, 500)
                ])
            }
        }
        
        results = []
        
        for dist_key, dist_info in distributions.items():
            df = pd.DataFrame({'feature': dist_info['data']})
            discretizer = FeatureDiscretizer()
            
            dist_result = {
                'distribution': dist_key,
                'name': dist_info['name'],
                'methods': []
            }
            
            # Try each method
            for method in ['quantile', 'equal_width']:
                try:
                    config = DiscretizationConfig(method=method, n_bins=n_bins)
                    result = discretizer.fit_transform(df, 'feature', config)
                    info = discretizer.get_feature_info('feature')
                    
                    # Calculate balance score (how evenly distributed)
                    counts = result.value_counts()
                    balance_score = 1.0 - (counts.std() / counts.mean()) if counts.mean() > 0 else 0
                    
                    dist_result['methods'].append({
                        'method': method,
                        'thresholds': [float(t) for t in info['config']['thresholds']],
                        'distribution': result.value_counts().to_dict(),
                        'balance_score': float(balance_score)
                    })
                except Exception as e:
                    logger.warning(f"Method {method} failed for {dist_key}: {e}")
            
            results.append(dist_result)
        
        return {
            'n_bins': n_bins,
            'results': results,
            'recommendation': {
                'normal': 'Any method works well',
                'exponential': 'Use quantile for balanced bins',
                'uniform': 'Equal-width is simplest',
                'bimodal': 'Use K-means to find clusters'
            }
        }
        
    except Exception as e:
        logger.error(f"Error comparing methods: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to compare methods: {str(e)}"
        )

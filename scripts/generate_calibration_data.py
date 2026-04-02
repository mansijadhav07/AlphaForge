"""
Generate real calibration data for PGM predictions.

This script:
1. Loads feature data for each symbol
2. Uses a simple predictive model to generate probability predictions
3. Compares predictions with actual outcomes
4. Computes calibration analysis
5. Saves results for API to serve
"""

import sys
sys.path.insert(0, '.')

import pandas as pd
import numpy as np
import json
from pathlib import Path
from datetime import datetime
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

from data.features.offline_store import OfflineFeatureStore
from backend.models.calibration import create_calibration_analysis
from backend.models.state_encoding import create_target_variable
from utils.logger import get_logger

logger = get_logger(__name__)


def prepare_calibration_data(symbol: str):
    """
    Prepare data and generate predictions for calibration analysis.
    
    Args:
        symbol: Stock symbol
        
    Returns:
        Tuple of (y_true, y_prob) or None if failed
    """
    logger.info(f"Preparing calibration data for {symbol}...")
    
    # Load feature data
    store = OfflineFeatureStore()
    features_df = store.read_features(
        feature_group="market_features",
        use_latest=True,
        filters={'ticker': symbol}
    )
    
    if features_df is None or features_df.empty:
        logger.error(f"No feature data found for {symbol}")
        return None
    
    logger.info(f"Loaded {len(features_df)} samples for {symbol}")
    
    # Create target variable if it doesn't exist
    if 'future_return' not in features_df.columns:
        logger.info("Creating target variable from close prices...")
        features_df = create_target_variable(features_df, horizon=5)
    
    # Create binary target (positive return vs not)
    features_df['target_binary'] = (features_df['future_return'] > 0).astype(int)
    
    # Remove rows with NaN target
    features_df = features_df.dropna(subset=['target_binary'])
    
    if len(features_df) < 100:
        logger.error(f"Insufficient samples after cleaning: {len(features_df)}")
        return None
    
    # Select numerical features for prediction
    feature_cols = []
    for col in features_df.columns:
        if col in ['timestamp', 'date', 'ticker', 'symbol', 'target_binary', 
                   'future_return', '_write_timestamp', '_version']:
            continue
        if features_df[col].dtype in ['float64', 'int64']:
            # Skip state columns (already discretized)
            if not col.endswith('_state'):
                feature_cols.append(col)
    
    if len(feature_cols) == 0:
        logger.error("No numerical features found")
        return None
    
    logger.info(f"Using {len(feature_cols)} features for prediction")
    
    # Prepare X and y
    X = features_df[feature_cols].fillna(0)
    y = features_df['target_binary']
    
    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )
    
    logger.info(f"Train: {len(X_train)}, Test: {len(X_test)}")
    
    # Train a simple logistic regression model to get probability predictions
    logger.info("Training logistic regression model...")
    model = LogisticRegression(max_iter=1000, random_state=42)
    model.fit(X_train, y_train)
    
    # Get probability predictions for test set
    y_prob = model.predict_proba(X_test)[:, 1]  # Probability of positive class
    
    logger.info(f"Generated {len(y_prob)} probability predictions")
    logger.info(f"Actual positive rate: {y_test.mean():.3f}")
    logger.info(f"Mean predicted probability: {y_prob.mean():.3f}")
    
    return y_test.values, y_prob


def generate_calibration_analysis(symbol: str, save_results: bool = True):
    """
    Generate calibration analysis for a symbol.
    
    Args:
        symbol: Stock symbol
        save_results: Whether to save results to file
        
    Returns:
        Calibration analysis dictionary or None
    """
    logger.info(f"=" * 80)
    logger.info(f"Generating calibration analysis for {symbol}")
    logger.info(f"=" * 80)
    
    # Prepare data and get predictions
    result = prepare_calibration_data(symbol)
    if result is None:
        logger.error(f"Failed to prepare calibration data for {symbol}")
        return None
    
    y_true, y_prob = result
    
    # Create calibration analysis
    logger.info("Computing calibration metrics...")
    analysis = create_calibration_analysis(y_true, y_prob, n_bins=10)
    
    # Print results
    logger.info("\n" + "=" * 80)
    logger.info(f"Calibration Results for {symbol}")
    logger.info("=" * 80)
    
    metrics = analysis['calibration_curve']['metrics']
    logger.info(f"ECE: {metrics['ece']:.4f}")
    logger.info(f"MCE: {metrics['mce']:.4f}")
    logger.info(f"Brier Score: {metrics['brier_score']:.4f}")
    logger.info(f"Reliability Score: {metrics['reliability_score']:.4f}")
    logger.info(f"Overall: {analysis['interpretation']['overall']}")
    
    # Save results
    if save_results:
        output_dir = Path('data/calibration')
        output_dir.mkdir(exist_ok=True)
        
        output_file = output_dir / f'{symbol}_calibration.json'
        
        # Prepare JSON-serializable format
        json_data = {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'calibration_curve': {
                'bins': analysis['calibration_curve']['bins'],
                'metrics': metrics
            },
            'reliability_diagram': analysis['reliability_diagram'],
            'interpretation': analysis['interpretation'],
            'summary': {
                'total_samples': len(y_true),
                'positive_rate': float(y_true.mean()),
                'mean_predicted_prob': float(y_prob.mean())
            }
        }
        
        with open(output_file, 'w') as f:
            json.dump(json_data, f, indent=2)
        
        logger.info(f"\nResults saved to: {output_file}")
    
    return analysis


def main():
    """Generate calibration analysis for all symbols."""
    symbols = ['AAPL', 'TSLA', 'GOOGL', 'MSFT']
    
    logger.info("Starting calibration data generation...")
    logger.info(f"Symbols: {symbols}")
    
    all_results = {}
    
    for symbol in symbols:
        try:
            result = generate_calibration_analysis(symbol, save_results=True)
            if result:
                all_results[symbol] = result
        except Exception as e:
            logger.error(f"Error generating calibration for {symbol}: {e}", exc_info=True)
    
    logger.info("\n" + "=" * 80)
    logger.info("Calibration generation complete!")
    logger.info(f"Successfully generated: {list(all_results.keys())}")
    logger.info("=" * 80)
    
    # Print summary
    print("\n" + "=" * 80)
    print("CALIBRATION SUMMARY")
    print("=" * 80)
    
    for symbol, result in all_results.items():
        metrics = result['calibration_curve']['metrics']
        print(f"\n{symbol}:")
        print(f"  ECE: {metrics['ece']:.4f}")
        print(f"  Brier Score: {metrics['brier_score']:.4f}")
        print(f"  Reliability: {metrics['reliability_score']:.2%}")
        print(f"  Quality: {result['interpretation']['ece']['quality']}")


if __name__ == '__main__':
    main()

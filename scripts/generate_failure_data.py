#!/usr/bin/env python3
"""
Generate Failure Analysis Data - 100% Real Data

This script identifies and analyzes PGM model prediction failures
on historical data for specified symbols and saves results to JSON files.

NO MOCK DATA - All failures are real prediction errors.

Usage:
    python3 scripts/generate_failure_data.py --symbols AAPL TSLA GOOGL MSFT
    python3 scripts/generate_failure_data.py --all
"""

import sys
import argparse
import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.models.utils import load_pgm_model
from backend.models.failure_analysis_real import RealFailureAnalyzer
from data.features.offline_store import OfflineFeatureStore
from utils.logger import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


def prepare_failure_data(
    features_df: pd.DataFrame,
    state_encoder,
    inference_engine,
    test_split: float = 0.2,
    lookback_periods: int = 5
) -> tuple:
    """
    Prepare predictions and actuals for failure analysis.
    
    Args:
        features_df: Historical features DataFrame
        state_encoder: StateEncoder instance
        inference_engine: InferenceEngine instance
        test_split: Fraction of data for testing
        lookback_periods: Periods to look ahead for actual outcome
        
    Returns:
        Tuple of (predictions_df, actuals_df, features_df_test)
    """
    logger.info(f"Preparing failure data from {len(features_df)} samples")
    
    # Sort by date to ensure chronological order
    if 'date' in features_df.columns:
        features_df = features_df.sort_values('date').reset_index(drop=True)
    
    # Calculate split point (chronological split, no shuffling)
    split_idx = int(len(features_df) * (1 - test_split))
    test_df = features_df.iloc[split_idx:].reset_index(drop=True)
    
    logger.info(f"Using {len(test_df)} samples for failure analysis (last {test_split*100}%)")
    
    if len(test_df) < lookback_periods + 10:
        logger.error(f"Insufficient test data: {len(test_df)} samples")
        return None, None, None
    
    predictions_list = []
    actuals_list = []
    valid_indices = []
    
    # Iterate through test data
    for i in range(len(test_df) - lookback_periods):
        try:
            # Get features at time t
            row = test_df.iloc[i:i+1]  # Keep as DataFrame for transform
            
            # Transform features to states using state encoder
            try:
                encoded_df = state_encoder.transform(row)
                
                # Build evidence dictionary from encoded states
                evidence = {}
                for col in encoded_df.columns:
                    if col.endswith('_state'):
                        state_value = encoded_df[col].iloc[0]
                        if pd.notna(state_value) and col in inference_engine.graph.nodes:
                            evidence[col] = state_value
                
                # Skip if not enough features encoded
                if len(evidence) < 5:
                    continue
                
            except Exception as e:
                logger.debug(f"Error encoding features for sample {i}: {e}")
                continue
            
            # Get PGM prediction
            try:
                result = inference_engine.query(['future_return_state'], evidence)
                probs = result.get('future_return_state', {})
                
                if not probs or len(probs) == 0:
                    continue
                    
            except Exception as e:
                logger.debug(f"Inference failed for sample {i}: {e}")
                continue
            
            # Predicted class (max probability)
            predicted_class = max(probs, key=probs.get)
            
            # Get actual future return
            future_idx = i + lookback_periods
            if future_idx >= len(test_df):
                break
                
            future_row = test_df.iloc[future_idx]
            actual_return = future_row.get('return', 0.0)
            
            # Classify actual return into positive/neutral/negative
            if actual_return > 0.01:  # > 1%
                actual_class = 'positive'
            elif actual_return < -0.01:  # < -1%
                actual_class = 'negative'
            else:
                actual_class = 'neutral'
            
            # Store prediction with feature states
            pred_dict = {
                'index': i,
                'predicted_class': predicted_class,
                'prob_positive': float(probs.get('positive', 0.0)),
                'prob_neutral': float(probs.get('neutral', 0.0)),
                'prob_negative': float(probs.get('negative', 0.0))
            }
            
            # Add encoded state columns
            for col in encoded_df.columns:
                if col.endswith('_state'):
                    pred_dict[col] = encoded_df[col].iloc[0]
            
            # Add date if available
            if 'date' in test_df.columns:
                pred_dict['date'] = test_df.iloc[i]['date']
            
            predictions_list.append(pred_dict)
            
            # Store actual
            actuals_list.append({
                'index': i,
                'actual_class': actual_class,
                'actual_return': float(actual_return)
            })
            
            valid_indices.append(i)
            
        except Exception as e:
            logger.debug(f"Error processing sample {i}: {e}")
            continue
    
    if len(predictions_list) == 0:
        logger.error("No valid predictions generated")
        return None, None, None
    
    # Create DataFrames
    predictions_df = pd.DataFrame(predictions_list).set_index('index')
    actuals_df = pd.DataFrame(actuals_list).set_index('index')
    
    # Filter features_df to only valid indices
    features_df_test = test_df.iloc[valid_indices].set_index(pd.Index(valid_indices))
    
    logger.info(f"Generated {len(predictions_df)} predictions for failure analysis")
    
    return predictions_df, actuals_df, features_df_test


def generate_failures_for_symbol(
    symbol: str,
    pgm_model: dict,
    output_dir: Path,
    max_failures: int = 100
) -> bool:
    """
    Generate failure analysis data for a single symbol.
    
    Args:
        symbol: Stock ticker symbol
        pgm_model: Loaded PGM model dictionary
        output_dir: Directory to save results
        max_failures: Maximum number of failures to store
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"=" * 60)
        logger.info(f"Generating failure analysis for {symbol}")
        logger.info(f"=" * 60)
        
        # Load historical features
        feature_store = OfflineFeatureStore()
        features_df = feature_store.read_features(
            feature_group="market_features",
            use_latest=True,
            filters={'ticker': symbol}
        )
        
        if features_df is None or features_df.empty:
            logger.warning(f"No features found for {symbol}")
            return False
        
        logger.info(f"Loaded {len(features_df)} samples for {symbol}")
        
        # Check for required columns
        required_cols = ['return', 'rsi', 'momentum_score']
        missing_cols = [col for col in required_cols if col not in features_df.columns]
        if missing_cols:
            logger.error(f"Missing required columns: {missing_cols}")
            return False
        
        # Prepare failure data
        predictions_df, actuals_df, features_df_test = prepare_failure_data(
            features_df,
            pgm_model['state_encoder'],
            pgm_model['inference_engine'],
            test_split=0.2,
            lookback_periods=5
        )
        
        if predictions_df is None or actuals_df is None:
            logger.error(f"Failed to prepare failure data for {symbol}")
            return False
        
        # Initialize failure analyzer
        analyzer = RealFailureAnalyzer(explanation_engine=None)
        
        # Analyze failures
        logger.info(f"Analyzing failures from {len(predictions_df)} predictions...")
        failure_cases = analyzer.analyze_failures(
            predictions_df,
            actuals_df,
            features_df=features_df_test,
            max_failures=max_failures
        )
        
        if not failure_cases:
            logger.warning(f"No failures found for {symbol} (model perfect or no data)")
            # Still save empty result
            failure_cases = []
        
        # Get summary and insights
        summary = analyzer.get_failure_summary(failure_cases)
        insights = analyzer.get_actionable_insights(failure_cases)
        
        # Calculate failure rate
        total_predictions = len(predictions_df)
        total_failures = len([case for case in failure_cases])
        failure_rate = total_failures / total_predictions if total_predictions > 0 else 0.0
        
        summary['failure_rate'] = round(failure_rate, 4)
        summary['total_predictions'] = total_predictions
        
        # Prepare results
        results = {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'failure_cases': failure_cases,
            'summary': summary,
            'insights': insights
        }
        
        # Save results with symbol-specific filename
        output_file = output_dir / f"{symbol}_failures.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"✅ Failure analysis complete for {symbol}")
        logger.info(f"   Total Predictions: {total_predictions}")
        logger.info(f"   Total Failures: {total_failures}")
        logger.info(f"   Failure Rate: {failure_rate:.2%}")
        logger.info(f"   High Severity: {summary['by_severity']['high']}")
        logger.info(f"   Saved to: {output_file}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error generating failures for {symbol}: {e}", exc_info=True)
        import traceback
        traceback.print_exc()
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Generate failure analysis data from real predictions'
    )
    parser.add_argument(
        '--symbols',
        nargs='+',
        help='List of symbols to generate failures for (e.g., AAPL TSLA GOOGL)'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Generate failures for all available symbols'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='data/failures',
        help='Output directory for failure files'
    )
    parser.add_argument(
        '--max-failures',
        type=int,
        default=100,
        help='Maximum number of failures to store per symbol'
    )
    
    args = parser.parse_args()
    
    # Determine symbols to process
    if args.all:
        # Get all symbols from feature store
        feature_store = OfflineFeatureStore()
        df = feature_store.read_features(feature_group="market_features", use_latest=True)
        if df.empty or 'ticker' not in df.columns:
            logger.error("No symbols found in feature store")
            return 1
        symbols = sorted(df['ticker'].unique().tolist())
    elif args.symbols:
        symbols = args.symbols
    else:
        # Default symbols
        symbols = ['AAPL', 'TSLA', 'GOOGL', 'MSFT']
    
    logger.info(f"\n{'='*60}")
    logger.info(f"FAILURE ANALYSIS DATA GENERATION")
    logger.info(f"{'='*60}")
    logger.info(f"Symbols: {', '.join(symbols)}")
    logger.info(f"Output: {args.output_dir}")
    logger.info(f"Max Failures: {args.max_failures}")
    logger.info(f"{'='*60}\n")
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load PGM model
    try:
        logger.info("Loading PGM model...")
        state_encoder, graph_structure, prob_learner = load_pgm_model('data/pgm_model')
        
        # Create inference engine
        from backend.models.inference_engine import InferenceEngine
        inference_engine = InferenceEngine(graph_structure, prob_learner)
        
        # Package as dict for convenience
        pgm_model = {
            'state_encoder': state_encoder,
            'graph_structure': graph_structure,
            'probability_learner': prob_learner,
            'inference_engine': inference_engine
        }
        
        logger.info("✅ PGM model loaded successfully\n")
    except Exception as e:
        logger.error(f"Failed to load PGM model: {e}")
        return 1
    
    # Generate failures for each symbol
    success_count = 0
    failed_symbols = []
    
    for i, symbol in enumerate(symbols, 1):
        logger.info(f"\n[{i}/{len(symbols)}] Processing {symbol}...")
        
        if generate_failures_for_symbol(symbol, pgm_model, output_dir, args.max_failures):
            success_count += 1
        else:
            failed_symbols.append(symbol)
    
    # Summary
    logger.info(f"\n{'='*60}")
    logger.info(f"FAILURE ANALYSIS GENERATION COMPLETE")
    logger.info(f"{'='*60}")
    logger.info(f"✅ Successful: {success_count}/{len(symbols)}")
    if failed_symbols:
        logger.info(f"❌ Failed: {', '.join(failed_symbols)}")
    logger.info(f"📁 Output: {output_dir}")
    logger.info(f"{'='*60}\n")
    
    return 0 if success_count > 0 else 1


if __name__ == "__main__":
    sys.exit(main())

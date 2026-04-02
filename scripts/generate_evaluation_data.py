#!/usr/bin/env python3
"""
Generate Model Evaluation Data - 100% Real Data

This script generates comprehensive evaluation metrics for the PGM model
on historical data for specified symbols and saves results to JSON files.

NO MOCK DATA - All metrics computed from real predictions and outcomes.

Usage:
    python3 scripts/generate_evaluation_data.py --symbols AAPL TSLA GOOGL MSFT
    python3 scripts/generate_evaluation_data.py --all
"""

import sys
import argparse
import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.models.utils import load_pgm_model
from backend.models.evaluation import ModelEvaluator
from data.features.offline_store import OfflineFeatureStore
from utils.logger import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


def prepare_evaluation_data(
    features_df: pd.DataFrame,
    state_encoder,
    inference_engine,
    test_split: float = 0.2,
    lookback_periods: int = 5
) -> tuple:
    """
    Prepare data for evaluation with time-series safe split.
    
    Args:
        features_df: Historical features DataFrame
        state_encoder: StateEncoder instance
        inference_engine: InferenceEngine instance
        test_split: Fraction of data for testing
        lookback_periods: Periods to look ahead for actual outcome
        
    Returns:
        Tuple of (predictions_df, actuals_df)
    """
    logger.info(f"Preparing evaluation data from {len(features_df)} samples")
    
    # Sort by date to ensure chronological order
    if 'date' in features_df.columns:
        features_df = features_df.sort_values('date').reset_index(drop=True)
    
    # Calculate split point (chronological split, no shuffling)
    split_idx = int(len(features_df) * (1 - test_split))
    test_df = features_df.iloc[split_idx:].reset_index(drop=True)
    
    logger.info(f"Using {len(test_df)} samples for evaluation (last {test_split*100}%)")
    logger.info(f"Test data columns: {list(test_df.columns)[:15]}")
    
    if len(test_df) < lookback_periods + 10:
        logger.error(f"Insufficient test data: {len(test_df)} samples")
        return None, None
    
    predictions_list = []
    actuals_list = []
    processed_count = 0
    encoded_count = 0
    inference_count = 0
    
    # Iterate through test data
    for i in range(len(test_df) - lookback_periods):
        processed_count += 1
        
        if i == 0:
            print(f"DEBUG: Starting loop, will process {len(test_df) - lookback_periods} samples")
        
        try:
            # Get features at time t
            row = test_df.iloc[i:i+1]  # Keep as DataFrame for transform
            
            if i == 0:
                print(f"DEBUG: Got row {i}, shape: {row.shape}")
            
            # Transform features to states using state encoder
            try:
                if i == 0:
                    print(f"DEBUG: About to transform row {i}")
                    
                encoded_df = state_encoder.transform(row)
                
                if i == 0:
                    print(f"DEBUG: Transform complete, encoded_df shape: {encoded_df.shape}")
                    print(f"DEBUG: Encoded columns: {list(encoded_df.columns)}")
                
                # Build evidence dictionary from encoded states
                evidence = {}
                try:
                    for col in encoded_df.columns:
                        if col.endswith('_state'):
                            state_value = encoded_df[col].iloc[0]
                            if pd.notna(state_value) and col in inference_engine.graph.nodes:
                                evidence[col] = state_value
                except Exception as e:
                    if i == 0:
                        print(f"DEBUG: Error building evidence: {e}")
                        import traceback
                        traceback.print_exc()
                    raise
                
                if i == 0:
                    print(f"DEBUG: Evidence built: {evidence}")
                    print(f"DEBUG: Evidence length: {len(evidence)}")
                
                # Log first sample for debugging
                if i == 0:
                    print(f"DEBUG: Sample 0 - Encoded columns: {list(encoded_df.columns)}")
                    print(f"DEBUG: Sample 0 - Evidence: {evidence}")
                    print(f"DEBUG: Sample 0 - Model nodes sample: {list(inference_engine.model.nodes)[:10]}")
                    logger.info(f"Sample 0 - Encoded columns: {list(encoded_df.columns)}")
                    logger.info(f"Sample 0 - Evidence: {evidence}")
                    logger.info(f"Sample 0 - Model nodes: {list(inference_engine.model.nodes)[:10]}")
                
                # Skip if not enough features encoded
                if len(evidence) < 5:
                    if i < 5:  # Log first few failures
                        logger.debug(f"Sample {i}: Only {len(evidence)} features encoded, skipping. Evidence: {list(evidence.keys())}")
                    continue
                
                encoded_count += 1
                
            except Exception as e:
                logger.debug(f"Error encoding features for sample {i}: {e}")
                continue
            
            # Get PGM prediction
            try:
                result = inference_engine.query(['future_return_state'], evidence)
                probs = result.get('future_return_state', {})
                
                if not probs or len(probs) == 0:
                    logger.debug(f"No probabilities returned for sample {i}")
                    continue
                
                inference_count += 1
                    
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
            
            # Store prediction
            predictions_list.append({
                'index': i,
                'predicted_class': predicted_class,
                'prob_positive': float(probs.get('positive', 0.0)),
                'prob_neutral': float(probs.get('neutral', 0.0)),
                'prob_negative': float(probs.get('negative', 0.0))
            })
            
            # Store actual
            actuals_list.append({
                'index': i,
                'actual_class': actual_class,
                'actual_return': float(actual_return)
            })
            
        except Exception as e:
            logger.debug(f"Error processing sample {i}: {e}")
            continue
    
    if len(predictions_list) == 0:
        logger.error("No valid predictions generated")
        logger.error(f"Stats: Processed={processed_count}, Encoded={encoded_count}, Inference={inference_count}, Predictions={len(predictions_list)}")
        return None, None
    
    # Create DataFrames
    predictions_df = pd.DataFrame(predictions_list).set_index('index')
    actuals_df = pd.DataFrame(actuals_list).set_index('index')
    
    logger.info(f"Generated {len(predictions_df)} predictions for evaluation")
    
    return predictions_df, actuals_df


def generate_evaluation_for_symbol(
    symbol: str,
    pgm_model: dict,
    output_dir: Path
) -> bool:
    """
    Generate evaluation data for a single symbol.
    
    Args:
        symbol: Stock ticker symbol
        pgm_model: Loaded PGM model dictionary
        output_dir: Directory to save results
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"=" * 60)
        logger.info(f"Generating evaluation for {symbol}")
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
        required_cols = ['return', 'rsi', 'momentum_score', 'volatility_10']
        missing_cols = [col for col in required_cols if col not in features_df.columns]
        if missing_cols:
            logger.error(f"Missing required columns: {missing_cols}")
            return False
        
        # Prepare evaluation data
        predictions_df, actuals_df = prepare_evaluation_data(
            features_df,
            pgm_model['state_encoder'],
            pgm_model['inference_engine'],
            test_split=0.2,
            lookback_periods=5
        )
        
        if predictions_df is None or actuals_df is None:
            logger.error(f"Failed to prepare evaluation data for {symbol}")
            return False
        
        # Initialize evaluator
        evaluator = ModelEvaluator(results_dir=str(output_dir))
        
        # Run evaluation
        logger.info(f"Running evaluation on {len(predictions_df)} predictions...")
        results = evaluator.evaluate_predictions(
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
        
        # Add symbol to results
        results['symbol'] = symbol
        
        # Save results with symbol-specific filename
        output_file = output_dir / f"{symbol}_evaluation.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"✅ Evaluation complete for {symbol}")
        logger.info(f"   Samples: {results['n_samples']}")
        logger.info(f"   Accuracy: {results['accuracy']:.2%}")
        logger.info(f"   Saved to: {output_file}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error generating evaluation for {symbol}: {e}", exc_info=True)
        import traceback
        traceback.print_exc()
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Generate model evaluation data from real predictions'
    )
    parser.add_argument(
        '--symbols',
        nargs='+',
        help='List of symbols to generate evaluation for (e.g., AAPL TSLA GOOGL)'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Generate evaluation for all available symbols'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='data/evaluation',
        help='Output directory for evaluation files'
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
    logger.info(f"EVALUATION DATA GENERATION")
    logger.info(f"{'='*60}")
    logger.info(f"Symbols: {', '.join(symbols)}")
    logger.info(f"Output: {args.output_dir}")
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
    
    # Generate evaluation for each symbol
    success_count = 0
    failed_symbols = []
    
    for i, symbol in enumerate(symbols, 1):
        logger.info(f"\n[{i}/{len(symbols)}] Processing {symbol}...")
        
        if generate_evaluation_for_symbol(symbol, pgm_model, output_dir):
            success_count += 1
        else:
            failed_symbols.append(symbol)
    
    # Summary
    logger.info(f"\n{'='*60}")
    logger.info(f"EVALUATION GENERATION COMPLETE")
    logger.info(f"{'='*60}")
    logger.info(f"✅ Successful: {success_count}/{len(symbols)}")
    if failed_symbols:
        logger.info(f"❌ Failed: {', '.join(failed_symbols)}")
    logger.info(f"📁 Output: {output_dir}")
    logger.info(f"{'='*60}\n")
    
    return 0 if success_count > 0 else 1


if __name__ == "__main__":
    sys.exit(main())

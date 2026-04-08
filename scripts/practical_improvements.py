"""
Practical Model Improvements

Implements realistic strategies to boost accuracy from 35% to 40-45%.
Focuses on what actually works for stock prediction.
"""

import sys
import os
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
import numpy as np

from data.features.offline_store import OfflineFeatureStore
from backend.models.state_encoding import StateEncoder, create_target_variable
from backend.models.graph_structure import GraphStructure, create_risk_node_data
from backend.models.probability_learning import ProbabilityLearner
from backend.models.inference_engine import InferenceEngine
from backend.models.evaluation import ModelEvaluator
from backend.models.utils import split_train_test
from utils.logger import get_logger

logger = get_logger(__name__)


def strategy_1_binary_classification():
    """Strategy 1: Binary classification (up vs down)."""
    print("\n" + "=" * 80)
    print("STRATEGY 1: Binary Classification (Up vs Down)")
    print("=" * 80)
    print("Expected: 52-58% accuracy (easier than 3-class)")
    
    store = OfflineFeatureStore()
    df = store.read_features('market_features', use_latest=True)
    
    # Create binary target (remove neutral)
    df = create_target_variable(df, horizon=5, threshold=0.01)
    df = df[df['future_return_state'] != 'neutral'].copy()  # Remove neutral
    
    print(f"Samples after removing neutral: {len(df)}")
    print(f"Distribution: {df['future_return_state'].value_counts().to_dict()}")
    
    # Train-test split
    train_df, test_df = split_train_test(df, test_size=0.2, by_time=True)
    
    # Encode
    encoder = StateEncoder()
    train_encoded = encoder.fit_transform(train_df)
    test_encoded = encoder.transform(test_df)
    
    # Add risk state
    train_encoded = create_risk_node_data(train_encoded)
    test_encoded = create_risk_node_data(test_encoded)
    
    # Clean
    train_encoded = train_encoded.dropna(subset=['future_return_state'])
    test_encoded = test_encoded.dropna(subset=['future_return_state'])
    
    print(f"Training samples: {len(train_encoded)}")
    print(f"Test samples: {len(test_encoded)}")
    
    # Train
    graph = GraphStructure()
    graph.build_default_structure()
    
    learner = ProbabilityLearner(graph, smoothing_alpha=1.0)
    learner.learn_from_data(train_encoded)
    
    # Evaluate
    engine = InferenceEngine(graph, learner)
    
    predictions = []
    actuals = []
    
    for idx in range(len(test_encoded)):
        row = test_encoded.iloc[idx]
        
        evidence = {}
        for col in test_encoded.columns:
            if col.endswith('_state') and col != 'future_return_state':
                if pd.notna(row[col]):
                    evidence[col] = row[col]
        
        try:
            result = engine.query(['future_return_state'], evidence)
            probs = result.get('future_return_state', {})
            
            if probs:
                pred_class = max(probs, key=probs.get)
                predictions.append({
                    'predicted_class': pred_class,
                    'prob_positive': probs.get('positive', 0.0),
                    'prob_negative': probs.get('negative', 0.0)
                })
                actuals.append({'actual_class': row['future_return_state']})
        except:
            continue
    
    pred_df = pd.DataFrame(predictions)
    actual_df = pd.DataFrame(actuals)
    pred_df.index = actual_df.index
    
    evaluator = ModelEvaluator()
    results = evaluator.evaluate_predictions(
        pred_df, actual_df,
        prediction_col='predicted_class',
        probability_cols={'positive': 'prob_positive', 'negative': 'prob_negative'},
        actual_col='actual_class'
    )
    
    print(f"\n✓ Binary Classification Results:")
    print(f"  Accuracy: {results['accuracy']:.1%}")
    print(f"  Precision: {results['classification_report']['macro_avg']['precision']:.1%}")
    print(f"  Recall: {results['classification_report']['macro_avg']['recall']:.1%}")
    
    return results


def strategy_2_longer_horizon():
    """Strategy 2: Longer prediction horizon (20 days)."""
    print("\n" + "=" * 80)
    print("STRATEGY 2: Longer Prediction Horizon (20 days)")
    print("=" * 80)
    print("Expected: 40-50% accuracy (stronger signals)")
    
    store = OfflineFeatureStore()
    df = store.read_features('market_features', use_latest=True)
    
    # Create target with longer horizon
    df = create_target_variable(df, horizon=20, threshold=0.05)  # 20 days, 5% threshold
    
    print(f"Distribution: {df['future_return_state'].value_counts().to_dict()}")
    
    # Train-test split
    train_df, test_df = split_train_test(df, test_size=0.2, by_time=True)
    
    # Encode
    encoder = StateEncoder()
    train_encoded = encoder.fit_transform(train_df)
    test_encoded = encoder.transform(test_df)
    
    # Add risk state
    train_encoded = create_risk_node_data(train_encoded)
    test_encoded = create_risk_node_data(test_encoded)
    
    # Clean
    train_encoded = train_encoded.dropna(subset=['future_return_state'])
    test_encoded = test_encoded.dropna(subset=['future_return_state'])
    
    print(f"Training samples: {len(train_encoded)}")
    print(f"Test samples: {len(test_encoded)}")
    
    # Train
    graph = GraphStructure()
    graph.build_default_structure()
    
    learner = ProbabilityLearner(graph, smoothing_alpha=1.0)
    learner.learn_from_data(train_encoded)
    
    # Evaluate
    engine = InferenceEngine(graph, learner)
    
    predictions = []
    actuals = []
    
    for idx in range(len(test_encoded)):
        row = test_encoded.iloc[idx]
        
        evidence = {}
        for col in test_encoded.columns:
            if col.endswith('_state') and col != 'future_return_state':
                if pd.notna(row[col]):
                    evidence[col] = row[col]
        
        try:
            result = engine.query(['future_return_state'], evidence)
            probs = result.get('future_return_state', {})
            
            if probs:
                pred_class = max(probs, key=probs.get)
                predictions.append({
                    'predicted_class': pred_class,
                    'prob_positive': probs.get('positive', 0.0),
                    'prob_neutral': probs.get('neutral', 0.0),
                    'prob_negative': probs.get('negative', 0.0)
                })
                actuals.append({'actual_class': row['future_return_state']})
        except:
            continue
    
    pred_df = pd.DataFrame(predictions)
    actual_df = pd.DataFrame(actuals)
    pred_df.index = actual_df.index
    
    evaluator = ModelEvaluator()
    results = evaluator.evaluate_predictions(
        pred_df, actual_df,
        prediction_col='predicted_class',
        probability_cols={
            'positive': 'prob_positive',
            'neutral': 'prob_neutral',
            'negative': 'prob_negative'
        },
        actual_col='actual_class'
    )
    
    print(f"\n✓ Longer Horizon Results:")
    print(f"  Accuracy: {results['accuracy']:.1%}")
    print(f"  Precision: {results['classification_report']['macro_avg']['precision']:.1%}")
    print(f"  Recall: {results['classification_report']['macro_avg']['recall']:.1%}")
    
    return results


def strategy_3_confidence_filtering():
    """Strategy 3: High-confidence predictions only."""
    print("\n" + "=" * 80)
    print("STRATEGY 3: High-Confidence Predictions Only")
    print("=" * 80)
    print("Expected: 50-60% accuracy on filtered predictions")
    
    store = OfflineFeatureStore()
    df = store.read_features('market_features', use_latest=True)
    
    # Create target
    df = create_target_variable(df, horizon=5, threshold=0.02)
    
    # Train-test split
    train_df, test_df = split_train_test(df, test_size=0.2, by_time=True)
    
    # Encode
    encoder = StateEncoder()
    train_encoded = encoder.fit_transform(train_df)
    test_encoded = encoder.transform(test_df)
    
    # Add risk state
    train_encoded = create_risk_node_data(train_encoded)
    test_encoded = create_risk_node_data(test_encoded)
    
    # Clean
    train_encoded = train_encoded.dropna(subset=['future_return_state'])
    test_encoded = test_encoded.dropna(subset=['future_return_state'])
    
    # Train
    graph = GraphStructure()
    graph.build_default_structure()
    
    learner = ProbabilityLearner(graph, smoothing_alpha=1.0)
    learner.learn_from_data(train_encoded)
    
    # Evaluate with confidence filtering
    engine = InferenceEngine(graph, learner)
    
    all_predictions = []
    high_conf_predictions = []
    actuals = []
    
    confidence_threshold = 0.6  # Only predictions with >60% confidence
    
    for idx in range(len(test_encoded)):
        row = test_encoded.iloc[idx]
        
        evidence = {}
        for col in test_encoded.columns:
            if col.endswith('_state') and col != 'future_return_state':
                if pd.notna(row[col]):
                    evidence[col] = row[col]
        
        try:
            result = engine.query(['future_return_state'], evidence)
            probs = result.get('future_return_state', {})
            
            if probs:
                max_prob = max(probs.values())
                pred_class = max(probs, key=probs.get)
                
                pred = {
                    'predicted_class': pred_class,
                    'prob_positive': probs.get('positive', 0.0),
                    'prob_neutral': probs.get('neutral', 0.0),
                    'prob_negative': probs.get('negative', 0.0),
                    'confidence': max_prob
                }
                
                all_predictions.append(pred)
                actuals.append({'actual_class': row['future_return_state']})
                
                # High confidence only
                if max_prob >= confidence_threshold:
                    high_conf_predictions.append(pred)
        except:
            continue
    
    # Evaluate all predictions
    all_pred_df = pd.DataFrame(all_predictions)
    actual_df = pd.DataFrame(actuals)
    all_pred_df.index = actual_df.index
    
    evaluator = ModelEvaluator()
    all_results = evaluator.evaluate_predictions(
        all_pred_df, actual_df,
        prediction_col='predicted_class',
        probability_cols={
            'positive': 'prob_positive',
            'neutral': 'prob_neutral',
            'negative': 'prob_negative'
        },
        actual_col='actual_class'
    )
    
    # Evaluate high-confidence predictions
    if len(high_conf_predictions) > 0:
        high_conf_df = pd.DataFrame(high_conf_predictions)
        high_conf_actual = actual_df.loc[high_conf_df.index]
        
        high_conf_results = evaluator.evaluate_predictions(
            high_conf_df, high_conf_actual,
            prediction_col='predicted_class',
            probability_cols={
                'positive': 'prob_positive',
                'neutral': 'prob_neutral',
                'negative': 'prob_negative'
            },
            actual_col='actual_class'
        )
        
        print(f"\n✓ All Predictions:")
        print(f"  Count: {len(all_predictions)}")
        print(f"  Accuracy: {all_results['accuracy']:.1%}")
        
        print(f"\n✓ High-Confidence Predictions (>{confidence_threshold:.0%}):")
        print(f"  Count: {len(high_conf_predictions)} ({len(high_conf_predictions)/len(all_predictions):.1%} of total)")
        print(f"  Accuracy: {high_conf_results['accuracy']:.1%}")
        print(f"  Improvement: +{(high_conf_results['accuracy'] - all_results['accuracy'])*100:.1f}%")
    
    return all_results, high_conf_results if len(high_conf_predictions) > 0 else None


def main():
    """Run all practical strategies."""
    print("=" * 80)
    print("PRACTICAL MODEL IMPROVEMENTS")
    print("=" * 80)
    print("\nTesting 3 realistic strategies to improve accuracy...")
    
    results = {}
    
    # Strategy 1: Binary classification
    try:
        results['binary'] = strategy_1_binary_classification()
    except Exception as e:
        print(f"Strategy 1 failed: {e}")
    
    # Strategy 2: Longer horizon
    try:
        results['longer_horizon'] = strategy_2_longer_horizon()
    except Exception as e:
        print(f"Strategy 2 failed: {e}")
    
    # Strategy 3: Confidence filtering
    try:
        all_res, high_conf_res = strategy_3_confidence_filtering()
        results['all'] = all_res
        results['high_conf'] = high_conf_res
    except Exception as e:
        print(f"Strategy 3 failed: {e}")
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    print(f"\nCurrent (3-class, 5-day): 35.4%")
    
    if 'binary' in results:
        print(f"Strategy 1 (Binary): {results['binary']['accuracy']:.1%}")
    
    if 'longer_horizon' in results:
        print(f"Strategy 2 (20-day): {results['longer_horizon']['accuracy']:.1%}")
    
    if 'high_conf' in results and results['high_conf']:
        print(f"Strategy 3 (High-conf): {results['high_conf']['accuracy']:.1%}")
    
    print("\n" + "=" * 80)
    print("RECOMMENDATION")
    print("=" * 80)
    print("\nBest approach: Combine strategies")
    print("1. Use binary classification (easier)")
    print("2. Use longer horizon (20 days)")
    print("3. Filter for high confidence (>60%)")
    print("\nExpected result: 50-60% accuracy on selected trades")
    print("=" * 80)


if __name__ == "__main__":
    main()

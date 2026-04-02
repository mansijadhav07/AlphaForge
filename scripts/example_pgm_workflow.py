"""
Example workflow demonstrating the Probabilistic Graphical Model (PGM) module.

This script shows how to:
1. Encode continuous features into discrete states
2. Build a Bayesian Network structure
3. Learn conditional probabilities from data
4. Perform probabilistic inference
5. Generate explanations
6. Simulate scenarios
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Import PGM modules
from backend.models.state_encoding import StateEncoder, create_target_variable
from backend.models.graph_structure import GraphStructure, create_risk_node_data
from backend.models.probability_learning import ProbabilityLearner
from backend.models.inference_engine import InferenceEngine
from backend.models.explanation_engine import ExplanationEngine
from backend.models.scenario_simulator import ScenarioSimulator
from backend.models.utils import (
    prepare_data_for_pgm,
    split_train_test,
    evaluate_predictions,
    generate_trading_signals,
    save_pgm_model,
    create_summary_report
)

# Import existing modules
from data.features.offline_store import OfflineFeatureStore
from utils.logger import get_logger

logger = get_logger(__name__)


def main():
    """Run complete PGM workflow."""
    
    print("=" * 80)
    print("PROBABILISTIC GRAPHICAL MODEL - EXAMPLE WORKFLOW")
    print("=" * 80)
    
    # ========================================================================
    # STEP 1: LOAD FEATURE DATA
    # ========================================================================
    print("\n" + "=" * 80)
    print("STEP 1: LOADING FEATURE DATA")
    print("=" * 80)
    
    # Load features from offline store
    offline_store = OfflineFeatureStore()
    
    try:
        df = offline_store.read_features('market_features', use_latest=True)
        print(f"✓ Loaded {len(df)} records from feature store")
        print(f"  Tickers: {df['ticker'].unique().tolist()}")
        print(f"  Date range: {df['date'].min()} to {df['date'].max()}")
        print(f"  Features: {len(df.columns)} columns")
    except Exception as e:
        logger.error(f"Failed to load features: {e}")
        print(f"✗ Error loading features. Please run example_workflow.py first.")
        return
    
    # ========================================================================
    # STEP 2: STATE ENCODING
    # ========================================================================
    print("\n" + "=" * 80)
    print("STEP 2: ENCODING CONTINUOUS FEATURES TO DISCRETE STATES")
    print("=" * 80)
    
    encoder = StateEncoder()
    
    # Prepare data
    encoded_df = prepare_data_for_pgm(df, encoder, horizon=5, threshold=0.02)
    
    print(f"✓ Encoded {len(encoder.encoding_rules)} features")
    print(f"  Sample encoded features:")
    
    state_cols = [col for col in encoded_df.columns if col.endswith('_state')]
    for col in state_cols[:5]:
        dist = encoded_df[col].value_counts()
        print(f"    • {col}: {dist.to_dict()}")
    
    # ========================================================================
    # STEP 3: BUILD GRAPH STRUCTURE
    # ========================================================================
    print("\n" + "=" * 80)
    print("STEP 3: BUILDING BAYESIAN NETWORK STRUCTURE")
    print("=" * 80)
    
    graph_structure = GraphStructure()
    graph = graph_structure.build_default_structure()
    
    print(f"✓ Graph structure built")
    print(f"  Nodes: {len(graph.nodes)}")
    print(f"  Edges: {len(graph.edges)}")
    print(f"  Is DAG: {graph_structure.validate_dag()}")
    
    # Visualize graph
    viz_path = "data/analytics/pgm_graph_structure.png"
    Path("data/analytics").mkdir(parents=True, exist_ok=True)
    graph_structure.visualize(output_path=viz_path)
    print(f"  Graph visualization saved to {viz_path}")
    
    # ========================================================================
    # STEP 4: SPLIT DATA
    # ========================================================================
    print("\n" + "=" * 80)
    print("STEP 4: SPLITTING DATA INTO TRAIN/TEST SETS")
    print("=" * 80)
    
    train_df, test_df = split_train_test(encoded_df, test_size=0.2, by_time=True)
    
    print(f"✓ Data split complete")
    print(f"  Training set: {len(train_df)} samples")
    print(f"  Test set: {len(test_df)} samples")
    
    # ========================================================================
    # STEP 5: LEARN PROBABILITIES
    # ========================================================================
    print("\n" + "=" * 80)
    print("STEP 5: LEARNING CONDITIONAL PROBABILITY TABLES")
    print("=" * 80)
    
    prob_learner = ProbabilityLearner(graph_structure, smoothing_alpha=1.0)
    prob_learner.learn_from_data(train_df)
    
    print(f"✓ Learned {len(prob_learner.cpts)} CPTs")
    
    # Validate CPTs
    validation = prob_learner.validate_cpts()
    valid_count = sum(validation.values())
    print(f"  Valid CPTs: {valid_count}/{len(validation)}")
    
    # Show sample CPT
    print("\n  Sample CPT (RSI):")
    prob_learner.print_cpt('rsi_state')
    
    # ========================================================================
    # STEP 6: INFERENCE ENGINE
    # ========================================================================
    print("\n" + "=" * 80)
    print("STEP 6: PROBABILISTIC INFERENCE")
    print("=" * 80)
    
    inference_engine = InferenceEngine(graph_structure, prob_learner)
    
    # Example inference
    evidence = {
        'rsi_state': 'oversold',
        'momentum_score_state': 'strong',
        'volatility_10_state': 'low',
        'regime_state': 'bull'
    }
    
    print(f"\nExample Query:")
    print(f"  Evidence: {evidence}")
    
    result = inference_engine.query(['future_return_state'], evidence)
    
    print(f"\n  Prediction:")
    for state, prob in result['future_return_state'].items():
        bar = "█" * int(prob * 40)
        print(f"    {state:12s} {prob:6.1%} {bar}")
    
    # Trading signals
    signals = inference_engine.compute_signal_probabilities(evidence)
    print(f"\n  Trading Signals:")
    for signal, prob in signals.items():
        print(f"    {signal.upper():6s}: {prob:.1%}")
    
    # ========================================================================
    # STEP 7: EXPLANATION ENGINE
    # ========================================================================
    print("\n" + "=" * 80)
    print("STEP 7: GENERATING EXPLANATIONS")
    print("=" * 80)
    
    explanation_engine = ExplanationEngine(graph_structure, inference_engine)
    
    explanation = explanation_engine.explain_prediction(
        'future_return_state',
        evidence,
        result['future_return_state']
    )
    
    # Print formatted explanation
    text_explanation = explanation_engine.generate_text_explanation(explanation)
    print(text_explanation)
    
    # ========================================================================
    # STEP 8: SCENARIO SIMULATION
    # ========================================================================
    print("\n" + "=" * 80)
    print("STEP 8: SCENARIO SIMULATION")
    print("=" * 80)
    
    scenario_simulator = ScenarioSimulator(inference_engine, explanation_engine)
    
    # Sensitivity analysis
    print("\nSensitivity Analysis: Varying RSI")
    sensitivity_df = scenario_simulator.sensitivity_analysis(
        base_scenario=evidence,
        query_var='future_return_state',
        vary_feature='rsi_state'
    )
    print(sensitivity_df.to_string(index=False))
    
    # Find optimal scenario
    print("\nFinding Optimal Scenario for Positive Return:")
    optimal = scenario_simulator.find_optimal_scenario(
        query_var='future_return_state',
        desired_outcome='positive',
        fixed_features={'volatility_10_state': 'low'}
    )
    print(f"  Optimal scenario: {optimal['optimal_scenario']}")
    print(f"  Probability: {optimal['probability']:.1%}")
    
    # ========================================================================
    # STEP 9: BATCH PREDICTION ON TEST SET
    # ========================================================================
    print("\n" + "=" * 80)
    print("STEP 9: BATCH PREDICTION ON TEST SET")
    print("=" * 80)
    
    # Select evidence columns (all state columns except target)
    evidence_cols = [col for col in state_cols if col != 'future_return_state']
    
    # Perform batch inference (sample first 100 for speed)
    test_sample = test_df.head(100)
    
    predictions_df = inference_engine.batch_inference(
        test_sample,
        query_vars=['future_return_state'],
        evidence_cols=evidence_cols
    )
    
    print(f"✓ Generated predictions for {len(predictions_df)} test samples")
    
    # Get predicted labels
    prob_cols = [col for col in predictions_df.columns if col.startswith('future_return_state_')]
    y_pred_probs = predictions_df[prob_cols]
    y_pred_probs.columns = [col.replace('future_return_state_', '').replace('_prob', '') 
                            for col in y_pred_probs.columns]
    
    # Get most likely prediction
    y_pred = y_pred_probs.idxmax(axis=1)
    
    # Get true labels
    y_true = test_sample['future_return_state'].reset_index(drop=True)
    
    # Evaluate
    metrics = evaluate_predictions(y_true, y_pred, y_pred_probs)
    
    print(f"\n  Performance Metrics:")
    print(f"    Accuracy:  {metrics['accuracy']:.3f}")
    print(f"    Precision: {metrics['precision']:.3f}")
    print(f"    Recall:    {metrics['recall']:.3f}")
    print(f"    F1 Score:  {metrics['f1_score']:.3f}")
    
    # ========================================================================
    # STEP 10: SAVE MODEL
    # ========================================================================
    print("\n" + "=" * 80)
    print("STEP 10: SAVING PGM MODEL")
    print("=" * 80)
    
    model_dir = "data/pgm_model"
    save_pgm_model(encoder, graph_structure, prob_learner, model_dir)
    
    print(f"✓ Model saved to {model_dir}")
    
    # ========================================================================
    # SUMMARY REPORT
    # ========================================================================
    print("\n" + "=" * 80)
    print("SUMMARY REPORT")
    print("=" * 80)
    
    summary = create_summary_report(encoder, graph_structure, prob_learner, metrics)
    print(summary)
    
    # Save summary to file
    summary_path = "data/analytics/pgm_summary_report.txt"
    with open(summary_path, 'w') as f:
        f.write(summary)
    print(f"Summary report saved to {summary_path}")
    
    print("\n" + "=" * 80)
    print("✓ PGM WORKFLOW COMPLETE")
    print("=" * 80)
    print("\nNext steps:")
    print("  1. Integrate PGM predictions into main.py API")
    print("  2. Add PGM endpoints to FastAPI")
    print("  3. Update frontend to display probabilistic insights")
    print("  4. Implement real-time PGM updates in streaming pipeline")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Workflow failed: {e}", exc_info=True)
        print(f"\n✗ Error: {e}")
        print("Check logs in ./logs/ for details")

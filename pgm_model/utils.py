"""
Utility functions for PGM module.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import json
from pathlib import Path

from utils.logger import get_logger

logger = get_logger(__name__)


def prepare_data_for_pgm(df: pd.DataFrame, 
                         encoder,
                         horizon: int = 5,
                         threshold: float = 0.02) -> pd.DataFrame:
    """
    Prepare data for PGM training.
    
    Args:
        df: DataFrame with engineered features
        encoder: StateEncoder instance
        horizon: Prediction horizon
        threshold: Return threshold for classification
        
    Returns:
        DataFrame with encoded states and target variable
    """
    logger.info("Preparing data for PGM...")
    
    # Encode features
    encoded_df = encoder.fit_transform(df)
    
    # Create target variable
    from .state_encoding import create_target_variable
    encoded_df = create_target_variable(encoded_df, horizon=horizon, threshold=threshold)
    
    # Create risk state if needed
    from .graph_structure import create_risk_node_data
    encoded_df = create_risk_node_data(encoded_df)
    
    # Remove rows with missing target
    initial_rows = len(encoded_df)
    encoded_df = encoded_df.dropna(subset=['future_return_state'])
    final_rows = len(encoded_df)
    
    logger.info(f"Prepared {final_rows} samples ({initial_rows - final_rows} removed due to missing target)")
    
    return encoded_df


def split_train_test(df: pd.DataFrame, 
                     test_size: float = 0.2,
                     by_time: bool = True) -> tuple:
    """
    Split data into train and test sets.
    
    Args:
        df: DataFrame to split
        test_size: Fraction for test set
        by_time: If True, split by time (last test_size fraction)
                If False, random split
        
    Returns:
        Tuple of (train_df, test_df)
    """
    if by_time:
        # Sort by date
        df = df.sort_values('date')
        split_idx = int(len(df) * (1 - test_size))
        train_df = df.iloc[:split_idx]
        test_df = df.iloc[split_idx:]
    else:
        # Random split
        test_df = df.sample(frac=test_size, random_state=42)
        train_df = df.drop(test_df.index)
    
    logger.info(f"Split: {len(train_df)} train, {len(test_df)} test")
    
    return train_df, test_df


def evaluate_predictions(y_true: pd.Series, y_pred: pd.Series, 
                        y_prob: Optional[pd.DataFrame] = None) -> Dict:
    """
    Evaluate prediction performance.
    
    Args:
        y_true: True labels
        y_pred: Predicted labels
        y_prob: Predicted probabilities (optional)
        
    Returns:
        Dictionary with evaluation metrics
    """
    from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
    
    # Basic metrics
    accuracy = accuracy_score(y_true, y_pred)
    precision, recall, f1, support = precision_recall_fscore_support(
        y_true, y_pred, average='weighted', zero_division=0
    )
    
    metrics = {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1_score': f1,
        'confusion_matrix': confusion_matrix(y_true, y_pred).tolist()
    }
    
    # Calibration metrics if probabilities provided
    if y_prob is not None:
        from sklearn.calibration import calibration_curve
        
        # For each class
        calibration_scores = {}
        for col in y_prob.columns:
            if col in y_true.unique():
                y_binary = (y_true == col).astype(int)
                prob_true, prob_pred = calibration_curve(
                    y_binary, y_prob[col], n_bins=5, strategy='uniform'
                )
                calibration_scores[col] = {
                    'prob_true': prob_true.tolist(),
                    'prob_pred': prob_pred.tolist()
                }
        
        metrics['calibration'] = calibration_scores
    
    logger.info(f"Evaluation: Accuracy={accuracy:.3f}, F1={f1:.3f}")
    
    return metrics


def generate_trading_signals(predictions: pd.DataFrame,
                            buy_threshold: float = 0.65,
                            sell_threshold: float = 0.35) -> pd.DataFrame:
    """
    Generate trading signals from probabilistic predictions.
    
    Args:
        predictions: DataFrame with probability columns
        buy_threshold: Threshold for buy signal
        sell_threshold: Threshold for sell signal
        
    Returns:
        DataFrame with trading signals
    """
    signals = predictions.copy()
    
    # Assume columns: prob_positive, prob_neutral, prob_negative
    if 'prob_positive' in signals.columns and 'prob_negative' in signals.columns:
        signals['signal'] = 'hold'
        signals.loc[signals['prob_positive'] >= buy_threshold, 'signal'] = 'buy'
        signals.loc[signals['prob_negative'] >= buy_threshold, 'signal'] = 'sell'
        
        # Add confidence
        signals['signal_confidence'] = signals[['prob_positive', 'prob_neutral', 'prob_negative']].max(axis=1)
    
    logger.info(f"Generated signals: {signals['signal'].value_counts().to_dict()}")
    
    return signals


def save_pgm_model(encoder, graph_structure, prob_learner, 
                  output_dir: str):
    """
    Save complete PGM model.
    
    Args:
        encoder: StateEncoder instance
        graph_structure: GraphStructure instance
        prob_learner: ProbabilityLearner instance
        output_dir: Output directory
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Save encoder config
    encoder.save_config(str(output_path / 'encoder_config.json'))
    
    # Save graph structure
    graph_structure.save_structure(str(output_path / 'graph_structure.json'))
    
    # Save CPTs
    prob_learner.save_cpts(str(output_path / 'cpts.pkl'))
    
    logger.info(f"PGM model saved to {output_dir}")


def load_pgm_model(input_dir: str):
    """
    Load complete PGM model.
    
    Args:
        input_dir: Input directory
        
    Returns:
        Tuple of (encoder, graph_structure, prob_learner)
    """
    from .state_encoding import StateEncoder
    from .graph_structure import GraphStructure
    from .probability_learning import ProbabilityLearner
    
    input_path = Path(input_dir)
    
    # Load encoder
    encoder = StateEncoder(config_path=str(input_path / 'encoder_config.json'))
    
    # Load graph structure
    graph_structure = GraphStructure()
    graph_structure.load_structure(str(input_path / 'graph_structure.json'))
    
    # Load CPTs
    prob_learner = ProbabilityLearner(graph_structure)
    prob_learner.load_cpts(str(input_path / 'cpts.pkl'))
    
    logger.info(f"PGM model loaded from {input_dir}")
    
    return encoder, graph_structure, prob_learner


def create_summary_report(encoder, graph_structure, prob_learner, 
                         test_metrics: Dict) -> str:
    """
    Create comprehensive summary report.
    
    Args:
        encoder: StateEncoder instance
        graph_structure: GraphStructure instance
        prob_learner: ProbabilityLearner instance
        test_metrics: Evaluation metrics dictionary
        
    Returns:
        Formatted text report
    """
    lines = []
    
    lines.append("=" * 80)
    lines.append("PROBABILISTIC GRAPHICAL MODEL - SUMMARY REPORT")
    lines.append("=" * 80)
    
    # Graph structure
    lines.append("\nGRAPH STRUCTURE:")
    lines.append("─" * 80)
    graph_info = graph_structure.get_graph_info()
    lines.append(f"  Nodes: {graph_info['num_nodes']}")
    lines.append(f"  Edges: {graph_info['num_edges']}")
    lines.append(f"  Is DAG: {graph_info['is_dag']}")
    
    # Encoding
    lines.append("\nFEATURE ENCODING:")
    lines.append("─" * 80)
    lines.append(f"  Encoded Features: {len(encoder.encoding_rules)}")
    for feature, rule in list(encoder.encoding_rules.items())[:5]:
        lines.append(f"    • {feature}: {rule['labels']}")
    
    # CPTs
    lines.append("\nLEARNED PROBABILITIES:")
    lines.append("─" * 80)
    lines.append(f"  CPTs Learned: {len(prob_learner.cpts)}")
    
    # Validation
    validation = prob_learner.validate_cpts()
    valid_count = sum(validation.values())
    lines.append(f"  Valid CPTs: {valid_count}/{len(validation)}")
    
    # Performance
    lines.append("\nPERFORMANCE METRICS:")
    lines.append("─" * 80)
    lines.append(f"  Accuracy: {test_metrics.get('accuracy', 0):.3f}")
    lines.append(f"  Precision: {test_metrics.get('precision', 0):.3f}")
    lines.append(f"  Recall: {test_metrics.get('recall', 0):.3f}")
    lines.append(f"  F1 Score: {test_metrics.get('f1_score', 0):.3f}")
    
    lines.append("\n" + "=" * 80 + "\n")
    
    return "\n".join(lines)


def visualize_probability_distribution(prob_dist: Dict[str, float], 
                                       title: str = "Probability Distribution",
                                       output_path: Optional[str] = None):
    """
    Visualize probability distribution as bar chart.
    
    Args:
        prob_dist: Dictionary of {state: probability}
        title: Chart title
        output_path: Path to save figure (None = display)
    """
    import matplotlib.pyplot as plt
    
    states = list(prob_dist.keys())
    probs = list(prob_dist.values())
    
    plt.figure(figsize=(10, 6))
    bars = plt.bar(states, probs, color=['#FF6B6B', '#4ECDC4', '#95E1D3'])
    
    plt.xlabel('State', fontsize=12)
    plt.ylabel('Probability', fontsize=12)
    plt.title(title, fontsize=14, fontweight='bold')
    plt.ylim(0, 1.0)
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.2%}',
                ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        logger.info(f"Visualization saved to {output_path}")
    else:
        plt.show()
    
    plt.close()

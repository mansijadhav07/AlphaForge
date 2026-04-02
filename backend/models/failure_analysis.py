"""
Failure Case Analysis Module for Probabilistic Graphical Model.

Identifies and analyzes cases where the model makes incorrect predictions,
providing insights into why failures occur.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from collections import defaultdict

from utils.logger import get_logger

logger = get_logger(__name__)


class FailureAnalyzer:
    """
    Analyzes model prediction failures.
    
    Identifies incorrect predictions and provides detailed explanations
    about why the model failed, including feature states and patterns.
    """
    
    def __init__(self, explanation_engine=None):
        """
        Initialize FailureAnalyzer.
        
        Args:
            explanation_engine: ExplanationEngine instance for generating reasons
        """
        self.explanation_engine = explanation_engine
        logger.info("FailureAnalyzer initialized")
    
    def analyze_failures(
        self,
        predictions_df: pd.DataFrame,
        actuals_df: pd.DataFrame,
        features_df: pd.DataFrame = None,
        prediction_col: str = 'predicted_class',
        actual_col: str = 'actual_class',
        probability_cols: Dict[str, str] = None,
        max_failures: int = 50
    ) -> List[Dict]:
        """
        Analyze prediction failures and generate explanations.
        
        Args:
            predictions_df: DataFrame with predictions
            actuals_df: DataFrame with actual outcomes
            features_df: DataFrame with feature values (optional)
            prediction_col: Column name for predicted class
            actual_col: Column name for actual class
            probability_cols: Dict mapping class names to probability columns
            max_failures: Maximum number of failures to analyze
            
        Returns:
            List of failure case dictionaries
        """
        logger.info("Starting failure analysis")
        
        # Merge predictions with actuals
        df = predictions_df.merge(actuals_df, left_index=True, right_index=True, how='inner')
        
        # Identify failures (mismatches)
        failures_mask = df[prediction_col] != df[actual_col]
        failures_df = df[failures_mask].copy()
        
        logger.info(f"Found {len(failures_df)} failures out of {len(df)} predictions ({len(failures_df)/len(df)*100:.1f}%)")
        
        if len(failures_df) == 0:
            return []
        
        # Limit number of failures to analyze
        if len(failures_df) > max_failures:
            failures_df = failures_df.head(max_failures)
            logger.info(f"Limiting analysis to {max_failures} failures")
        
        # Merge with features if available
        if features_df is not None:
            failures_df = failures_df.merge(
                features_df,
                left_index=True,
                right_index=True,
                how='left',
                suffixes=('', '_feature')
            )
        
        # Default probability columns
        if probability_cols is None:
            probability_cols = {
                'positive': 'prob_positive',
                'neutral': 'prob_neutral',
                'negative': 'prob_negative'
            }
        
        # Analyze each failure
        failure_cases = []
        for idx, row in failures_df.iterrows():
            failure_case = self._analyze_single_failure(
                idx,
                row,
                prediction_col,
                actual_col,
                probability_cols,
                features_df
            )
            failure_cases.append(failure_case)
        
        # Add failure patterns
        failure_cases = self._add_failure_patterns(failure_cases)
        
        logger.info(f"Completed analysis of {len(failure_cases)} failure cases")
        
        return failure_cases
    
    def _analyze_single_failure(
        self,
        idx: int,
        row: pd.Series,
        prediction_col: str,
        actual_col: str,
        probability_cols: Dict[str, str],
        features_df: pd.DataFrame = None
    ) -> Dict:
        """
        Analyze a single failure case.
        
        Args:
            idx: Index of the failure
            row: Row data from failures DataFrame
            prediction_col: Predicted class column
            actual_col: Actual class column
            probability_cols: Probability column mapping
            features_df: Features DataFrame
            
        Returns:
            Dictionary with failure analysis
        """
        predicted = row[prediction_col]
        actual = row[actual_col]
        
        # Get probabilities
        probabilities = {}
        for class_name, prob_col in probability_cols.items():
            if prob_col in row:
                probabilities[class_name] = float(row[prob_col])
        
        # Get predicted and actual probabilities
        predicted_prob = probabilities.get(predicted, 0.0)
        actual_prob = probabilities.get(actual, 0.0)
        
        # Determine confidence level
        confidence = self._categorize_confidence(predicted_prob)
        
        # Determine failure severity
        severity = self._determine_severity(predicted, actual, predicted_prob, actual_prob)
        
        # Generate reason for failure
        reason = self._generate_failure_reason(
            predicted,
            actual,
            predicted_prob,
            actual_prob,
            confidence,
            row,
            features_df
        )
        
        # Extract feature states if available
        feature_states = self._extract_feature_states(row)
        
        # Get date if available
        date = None
        if 'date' in row:
            date = row['date']
        elif 'timestamp' in row:
            date = row['timestamp']
        elif hasattr(row, 'name'):
            date = str(row.name)
        
        failure_case = {
            'index': int(idx) if isinstance(idx, (int, np.integer)) else str(idx),
            'date': str(date) if date else None,
            'predicted': predicted,
            'actual': actual,
            'predicted_probability': predicted_prob,
            'actual_probability': actual_prob,
            'confidence': confidence,
            'severity': severity,
            'reason': reason,
            'probabilities': probabilities,
            'feature_states': feature_states,
            'failure_type': self._classify_failure_type(predicted, actual)
        }
        
        return failure_case
    
    def _categorize_confidence(self, probability: float) -> str:
        """Categorize confidence level."""
        if probability >= 0.75:
            return "high"
        elif probability >= 0.55:
            return "moderate"
        else:
            return "low"
    
    def _determine_severity(
        self,
        predicted: str,
        actual: str,
        predicted_prob: float,
        actual_prob: float
    ) -> str:
        """
        Determine failure severity.
        
        High severity: Wrong prediction with high confidence
        Medium severity: Wrong prediction with moderate confidence
        Low severity: Wrong prediction with low confidence (understandable)
        """
        if predicted_prob >= 0.75:
            return "high"
        elif predicted_prob >= 0.55:
            return "medium"
        else:
            return "low"
    
    def _classify_failure_type(self, predicted: str, actual: str) -> str:
        """
        Classify the type of failure.
        
        Returns:
            String describing the failure type
        """
        failure_types = {
            ('positive', 'negative'): 'false_positive_extreme',
            ('negative', 'positive'): 'false_negative_extreme',
            ('positive', 'neutral'): 'false_positive',
            ('neutral', 'positive'): 'false_negative',
            ('negative', 'neutral'): 'false_negative',
            ('neutral', 'negative'): 'false_positive',
        }
        
        return failure_types.get((predicted, actual), 'misclassification')
    
    def _generate_failure_reason(
        self,
        predicted: str,
        actual: str,
        predicted_prob: float,
        actual_prob: float,
        confidence: str,
        row: pd.Series,
        features_df: pd.DataFrame = None
    ) -> str:
        """
        Generate human-readable reason for failure.
        
        Args:
            predicted: Predicted class
            actual: Actual class
            predicted_prob: Probability of predicted class
            actual_prob: Probability of actual class
            confidence: Confidence level
            row: Row data
            features_df: Features DataFrame
            
        Returns:
            String explaining why the failure occurred
        """
        reasons = []
        
        # Confidence-based reasoning
        if confidence == "high":
            reasons.append(f"Model was highly confident ({predicted_prob:.1%}) in predicting '{predicted}'")
        elif confidence == "moderate":
            reasons.append(f"Model had moderate confidence ({predicted_prob:.1%}) in predicting '{predicted}'")
        else:
            reasons.append(f"Model had low confidence ({predicted_prob:.1%}), indicating uncertainty")
        
        # Probability gap analysis
        prob_gap = predicted_prob - actual_prob
        if prob_gap > 0.3:
            reasons.append(f"Large probability gap ({prob_gap:.1%}) between predicted and actual class")
        elif prob_gap > 0.1:
            reasons.append(f"Moderate probability gap ({prob_gap:.1%}) between classes")
        else:
            reasons.append(f"Small probability gap ({prob_gap:.1%}), classes were close")
        
        # Feature-based reasoning
        feature_reason = self._analyze_feature_contribution(row, predicted, actual)
        if feature_reason:
            reasons.append(feature_reason)
        
        # Combine reasons
        return ". ".join(reasons) + "."
    
    def _analyze_feature_contribution(
        self,
        row: pd.Series,
        predicted: str,
        actual: str
    ) -> Optional[str]:
        """
        Analyze which features may have contributed to the failure.
        
        Args:
            row: Row data with feature states
            predicted: Predicted class
            actual: Actual class
            
        Returns:
            String explaining feature contribution or None
        """
        # Look for feature state columns
        feature_states = {}
        for col in row.index:
            if '_state' in col:
                feature_states[col] = row[col]
        
        if not feature_states:
            return None
        
        # Analyze conflicting signals
        conflicting_features = []
        
        # Check for common conflicts
        if 'rsi_state' in feature_states and 'momentum_score_state' in feature_states:
            rsi = feature_states['rsi_state']
            momentum = feature_states['momentum_score_state']
            
            if (rsi == 'oversold' and momentum == 'weak') or \
               (rsi == 'overbought' and momentum == 'strong'):
                conflicting_features.append("RSI and momentum gave conflicting signals")
        
        if 'regime_state' in feature_states and 'volatility_10_state' in feature_states:
            regime = feature_states['regime_state']
            volatility = feature_states['volatility_10_state']
            
            if volatility == 'high':
                conflicting_features.append(f"High volatility in {regime} regime increased uncertainty")
        
        if conflicting_features:
            return "Possible causes: " + ", ".join(conflicting_features)
        
        return None
    
    def _extract_feature_states(self, row: pd.Series) -> Dict[str, str]:
        """
        Extract feature states from row.
        
        Args:
            row: Row data
            
        Returns:
            Dictionary of feature states
        """
        feature_states = {}
        
        for col in row.index:
            if '_state' in col:
                feature_name = col.replace('_state', '').replace('_', ' ').title()
                feature_states[feature_name] = str(row[col])
        
        return feature_states
    
    def _add_failure_patterns(self, failure_cases: List[Dict]) -> List[Dict]:
        """
        Identify common patterns across failures.
        
        Args:
            failure_cases: List of failure case dictionaries
            
        Returns:
            Updated failure cases with pattern information
        """
        if not failure_cases:
            return failure_cases
        
        # Analyze patterns
        failure_types = defaultdict(int)
        severity_counts = defaultdict(int)
        confidence_counts = defaultdict(int)
        
        for case in failure_cases:
            failure_types[case['failure_type']] += 1
            severity_counts[case['severity']] += 1
            confidence_counts[case['confidence']] += 1
        
        # Find most common pattern
        most_common_type = max(failure_types, key=failure_types.get)
        most_common_severity = max(severity_counts, key=severity_counts.get)
        
        # Add pattern info to each case
        for case in failure_cases:
            case['is_common_pattern'] = case['failure_type'] == most_common_type
            case['pattern_frequency'] = failure_types[case['failure_type']]
        
        return failure_cases
    
    def get_failure_summary(self, failure_cases: List[Dict]) -> Dict:
        """
        Generate summary statistics for failures.
        
        Args:
            failure_cases: List of failure case dictionaries
            
        Returns:
            Dictionary with summary statistics
        """
        if not failure_cases:
            return {
                'total_failures': 0,
                'by_type': {},
                'by_severity': {},
                'by_confidence': {},
                'most_common_type': None,
                'high_severity_count': 0
            }
        
        # Count by type
        by_type = defaultdict(int)
        by_severity = defaultdict(int)
        by_confidence = defaultdict(int)
        
        for case in failure_cases:
            by_type[case['failure_type']] += 1
            by_severity[case['severity']] += 1
            by_confidence[case['confidence']] += 1
        
        most_common_type = max(by_type, key=by_type.get)
        high_severity_count = by_severity.get('high', 0)
        
        return {
            'total_failures': len(failure_cases),
            'by_type': dict(by_type),
            'by_severity': dict(by_severity),
            'by_confidence': dict(by_confidence),
            'most_common_type': most_common_type,
            'high_severity_count': high_severity_count,
            'failure_rate': None  # To be filled by caller
        }
    
    def get_actionable_insights(self, failure_cases: List[Dict]) -> List[str]:
        """
        Generate actionable insights from failure analysis.
        
        Args:
            failure_cases: List of failure case dictionaries
            
        Returns:
            List of actionable insight strings
        """
        insights = []
        
        if not failure_cases:
            return ["No failures detected - model performing well!"]
        
        summary = self.get_failure_summary(failure_cases)
        
        # High severity failures
        if summary['high_severity_count'] > len(failure_cases) * 0.3:
            insights.append(
                f"⚠️ {summary['high_severity_count']} high-severity failures detected. "
                "Model is making confident wrong predictions - review feature engineering."
            )
        
        # Common failure patterns
        most_common = summary['most_common_type']
        if most_common:
            count = summary['by_type'][most_common]
            if count > len(failure_cases) * 0.4:
                insights.append(
                    f"📊 {count} failures are '{most_common}' type. "
                    "Consider adding features to better distinguish these cases."
                )
        
        # Confidence analysis
        high_conf_failures = summary['by_confidence'].get('high', 0)
        if high_conf_failures > 0:
            insights.append(
                f"🎯 {high_conf_failures} failures occurred with high confidence. "
                "Model may be overconfident - consider calibration adjustments."
            )
        
        # Low confidence failures
        low_conf_failures = summary['by_confidence'].get('low', 0)
        if low_conf_failures > len(failure_cases) * 0.5:
            insights.append(
                f"💡 {low_conf_failures} failures had low confidence. "
                "These are expected - model correctly identified uncertainty."
            )
        
        return insights


def analyze_failure_patterns(failure_cases: List[Dict]) -> Dict:
    """
    Analyze patterns in failure cases.
    
    Args:
        failure_cases: List of failure case dictionaries
        
    Returns:
        Dictionary with pattern analysis
    """
    if not failure_cases:
        return {}
    
    patterns = {
        'temporal_patterns': _analyze_temporal_patterns(failure_cases),
        'feature_patterns': _analyze_feature_patterns(failure_cases),
        'probability_patterns': _analyze_probability_patterns(failure_cases)
    }
    
    return patterns


def _analyze_temporal_patterns(failure_cases: List[Dict]) -> Dict:
    """Analyze if failures cluster in time."""
    # Placeholder for temporal analysis
    return {'has_temporal_clustering': False}


def _analyze_feature_patterns(failure_cases: List[Dict]) -> Dict:
    """Analyze common feature states in failures."""
    feature_counts = defaultdict(lambda: defaultdict(int))
    
    for case in failure_cases:
        for feature, state in case.get('feature_states', {}).items():
            feature_counts[feature][state] += 1
    
    return dict(feature_counts)


def _analyze_probability_patterns(failure_cases: List[Dict]) -> Dict:
    """Analyze probability distributions in failures."""
    predicted_probs = [case['predicted_probability'] for case in failure_cases]
    actual_probs = [case['actual_probability'] for case in failure_cases]
    
    return {
        'avg_predicted_prob': float(np.mean(predicted_probs)),
        'avg_actual_prob': float(np.mean(actual_probs)),
        'avg_prob_gap': float(np.mean([p - a for p, a in zip(predicted_probs, actual_probs)]))
    }

"""
Real Failure Analysis Module for PGM Model

This module identifies and analyzes prediction failures using real data.
NO MOCK DATA - All analysis based on actual model predictions vs outcomes.

Author: AlphaForge Team
Date: March 26, 2026
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from collections import Counter

from utils.logger import get_logger

logger = get_logger(__name__)


class RealFailureAnalyzer:
    """
    Analyzes PGM model prediction failures on real data.
    
    Identifies cases where predicted class != actual class and provides
    explanations for why the model failed.
    """
    
    def __init__(self, explanation_engine=None):
        """
        Initialize failure analyzer.
        
        Args:
            explanation_engine: Optional ExplanationEngine for feature impact analysis
        """
        self.explanation_engine = explanation_engine
        logger.info("RealFailureAnalyzer initialized")
    
    def analyze_failures(
        self,
        predictions_df: pd.DataFrame,
        actuals_df: pd.DataFrame,
        features_df: Optional[pd.DataFrame] = None,
        max_failures: int = 100
    ) -> List[Dict]:
        """
        Identify and analyze prediction failures.
        
        Args:
            predictions_df: DataFrame with columns: predicted_class, prob_positive, prob_neutral, prob_negative
            actuals_df: DataFrame with columns: actual_class, actual_return
            features_df: Optional DataFrame with feature states for each prediction
            max_failures: Maximum number of failures to return
            
        Returns:
            List of failure case dictionaries
        """
        logger.info(f"Analyzing failures from {len(predictions_df)} predictions")
        
        # Merge predictions and actuals
        merged = predictions_df.join(actuals_df, how='inner')
        
        if merged.empty:
            logger.warning("No data to analyze after merging predictions and actuals")
            return []
        
        # Identify failures (predicted != actual)
        failures = merged[merged['predicted_class'] != merged['actual_class']].copy()
        
        logger.info(f"Found {len(failures)} failures out of {len(merged)} predictions ({len(failures)/len(merged)*100:.1f}%)")
        
        if failures.empty:
            return []
        
        # Sort by most recent (highest index) and limit
        failures = failures.sort_index(ascending=False).head(max_failures)
        
        # Analyze each failure
        failure_cases = []
        for idx, row in failures.iterrows():
            try:
                failure_case = self._analyze_single_failure(
                    idx,
                    row,
                    features_df.loc[idx] if features_df is not None and idx in features_df.index else None
                )
                failure_cases.append(failure_case)
            except Exception as e:
                logger.debug(f"Error analyzing failure at index {idx}: {e}")
                continue
        
        # Add pattern analysis
        failure_cases = self._add_failure_patterns(failure_cases)
        
        logger.info(f"Successfully analyzed {len(failure_cases)} failure cases")
        
        return failure_cases
    
    def _analyze_single_failure(
        self,
        index: int,
        row: pd.Series,
        features: Optional[pd.Series] = None
    ) -> Dict:
        """
        Analyze a single failure case.
        
        Args:
            index: Index of the failure
            row: Series with prediction and actual data
            features: Optional Series with feature states
            
        Returns:
            Dictionary with failure analysis
        """
        predicted = row['predicted_class']
        actual = row['actual_class']
        
        # Get probabilities
        prob_positive = float(row.get('prob_positive', 0.0))
        prob_neutral = float(row.get('prob_neutral', 0.0))
        prob_negative = float(row.get('prob_negative', 0.0))
        
        probabilities = {
            'positive': prob_positive,
            'neutral': prob_neutral,
            'negative': prob_negative
        }
        
        # Predicted probability (confidence)
        predicted_prob = probabilities.get(predicted, 0.0)
        actual_prob = probabilities.get(actual, 0.0)
        
        # Confidence level
        confidence = self._categorize_confidence(predicted_prob)
        
        # Severity (how wrong was the prediction)
        severity = self._determine_severity(predicted, actual, predicted_prob)
        
        # Failure type
        failure_type = self._classify_failure_type(predicted, actual)
        
        # Extract feature states
        feature_states = self._extract_feature_states(row, features)
        
        # Generate explanation
        reason = self._generate_failure_reason(
            predicted, actual, predicted_prob, actual_prob,
            confidence, feature_states
        )
        
        # Get date if available
        date = None
        if features is not None and 'date' in features:
            date = str(features['date'])
        elif 'date' in row:
            date = str(row['date'])
        
        return {
            'index': int(index),
            'date': date,
            'predicted': predicted,
            'actual': actual,
            'predicted_probability': round(predicted_prob, 4),
            'actual_probability': round(actual_prob, 4),
            'confidence': confidence,
            'severity': severity,
            'reason': reason,
            'probabilities': {k: round(v, 4) for k, v in probabilities.items()},
            'feature_states': feature_states,
            'failure_type': failure_type
        }
    
    def _categorize_confidence(self, probability: float) -> str:
        """Categorize prediction confidence."""
        if probability >= 0.7:
            return 'high'
        elif probability >= 0.5:
            return 'medium'
        else:
            return 'low'
    
    def _determine_severity(
        self,
        predicted: str,
        actual: str,
        predicted_prob: float
    ) -> str:
        """
        Determine failure severity.
        
        High severity: Wrong direction with high confidence
        Medium severity: Wrong direction with medium confidence
        Low severity: Neutral mispredictions or low confidence
        """
        # Extreme failures (positive <-> negative)
        if (predicted == 'positive' and actual == 'negative') or \
           (predicted == 'negative' and actual == 'positive'):
            if predicted_prob >= 0.7:
                return 'high'
            elif predicted_prob >= 0.5:
                return 'medium'
            else:
                return 'low'
        
        # Moderate failures (involving neutral)
        else:
            if predicted_prob >= 0.7:
                return 'medium'
            else:
                return 'low'
    
    def _classify_failure_type(self, predicted: str, actual: str) -> str:
        """Classify the type of failure."""
        if predicted == 'positive' and actual == 'negative':
            return 'false_positive_extreme'
        elif predicted == 'negative' and actual == 'positive':
            return 'false_negative_extreme'
        elif predicted == 'positive' and actual == 'neutral':
            return 'false_positive_moderate'
        elif predicted == 'negative' and actual == 'neutral':
            return 'false_negative_moderate'
        elif predicted == 'neutral' and actual == 'positive':
            return 'missed_positive'
        elif predicted == 'neutral' and actual == 'negative':
            return 'missed_negative'
        else:
            return 'unknown'
    
    def _generate_failure_reason(
        self,
        predicted: str,
        actual: str,
        predicted_prob: float,
        actual_prob: float,
        confidence: str,
        feature_states: Dict[str, str]
    ) -> str:
        """
        Generate human-readable explanation for the failure.
        
        Args:
            predicted: Predicted class
            actual: Actual class
            predicted_prob: Probability of predicted class
            actual_prob: Probability of actual class
            confidence: Confidence level
            feature_states: Dictionary of feature states
            
        Returns:
            Explanation string
        """
        reasons = []
        
        # Confidence statement
        if confidence == 'high':
            reasons.append(f"Model was highly confident ({predicted_prob:.1%}) in predicting '{predicted}'")
        elif confidence == 'medium':
            reasons.append(f"Model had moderate confidence ({predicted_prob:.1%}) in predicting '{predicted}'")
        else:
            reasons.append(f"Model had low confidence ({predicted_prob:.1%}) in predicting '{predicted}'")
        
        # Probability gap
        prob_gap = abs(predicted_prob - actual_prob)
        if prob_gap > 0.4:
            reasons.append(f"Large probability gap ({prob_gap:.1%}) between predicted and actual class")
        elif prob_gap > 0.2:
            reasons.append(f"Moderate probability gap ({prob_gap:.1%}) between predicted and actual class")
        
        # Feature-based reasoning
        feature_reasons = self._analyze_feature_contribution(feature_states, predicted, actual)
        if feature_reasons:
            reasons.append(f"Possible causes: {feature_reasons}")
        
        return ". ".join(reasons) + "."
    
    def _analyze_feature_contribution(
        self,
        feature_states: Dict[str, str],
        predicted: str,
        actual: str
    ) -> str:
        """
        Analyze which features may have contributed to the failure.
        
        Args:
            feature_states: Dictionary of feature states
            predicted: Predicted class
            actual: Actual class
            
        Returns:
            String describing potential feature issues
        """
        issues = []
        
        # Check for conflicting signals
        if 'RSI' in feature_states and 'Momentum Score' in feature_states:
            rsi = feature_states['RSI']
            momentum = feature_states['Momentum Score']
            
            # Conflicting bullish/bearish signals
            if (rsi in ['oversold', 'low'] and momentum in ['weak', 'negative']) or \
               (rsi in ['overbought', 'high'] and momentum in ['strong', 'positive']):
                issues.append("RSI and momentum gave conflicting signals")
        
        # Check volatility
        if 'Volatility' in feature_states:
            vol = feature_states['Volatility']
            if vol in ['high', 'extreme']:
                issues.append("high volatility made predictions unstable")
        
        # Check regime mismatch
        if 'Market Regime' in feature_states:
            regime = feature_states['Market Regime']
            if regime == 'bear' and predicted == 'positive':
                issues.append("bearish regime contradicted bullish prediction")
            elif regime == 'bull' and predicted == 'negative':
                issues.append("bullish regime contradicted bearish prediction")
        
        # Check trend
        if 'Trend' in feature_states:
            trend = feature_states['Trend']
            if trend in ['downtrend', 'falling'] and predicted == 'positive':
                issues.append("downtrend contradicted positive prediction")
            elif trend in ['uptrend', 'rising'] and predicted == 'negative':
                issues.append("uptrend contradicted negative prediction")
        
        # Check volume
        if 'Volume' in feature_states:
            volume = feature_states['Volume']
            if volume in ['low', 'very_low']:
                issues.append("low volume reduced signal reliability")
        
        if not issues:
            return "feature states were ambiguous or conflicting"
        
        return ", ".join(issues)
    
    def _extract_feature_states(
        self,
        row: pd.Series,
        features: Optional[pd.Series] = None
    ) -> Dict[str, str]:
        """
        Extract feature states from row or features.
        
        Args:
            row: Prediction row
            features: Optional features row
            
        Returns:
            Dictionary mapping feature names to states
        """
        feature_states = {}
        
        # Feature name mapping (state column -> display name)
        feature_mapping = {
            'rsi_state': 'RSI',
            'momentum_score_state': 'Momentum Score',
            'regime_state': 'Market Regime',
            'volatility_10_state': 'Volatility',
            'macd_diff_state': 'MACD',
            'bb_position_state': 'Bollinger Bands',
            'volume_to_sma_state': 'Volume',
            'trend_slope_30_state': 'Trend',
            'return_state': 'Recent Return'
        }
        
        # Extract from row (state columns)
        for state_col, display_name in feature_mapping.items():
            if state_col in row and pd.notna(row[state_col]):
                feature_states[display_name] = str(row[state_col])
        
        # Extract from features if available
        if features is not None:
            for state_col, display_name in feature_mapping.items():
                if state_col in features and pd.notna(features[state_col]):
                    feature_states[display_name] = str(features[state_col])
        
        return feature_states
    
    def _add_failure_patterns(self, failure_cases: List[Dict]) -> List[Dict]:
        """
        Identify common failure patterns across cases.
        
        Args:
            failure_cases: List of failure case dictionaries
            
        Returns:
            Updated failure cases with pattern information
        """
        if not failure_cases:
            return failure_cases
        
        # Count failure types
        failure_type_counts = Counter(case['failure_type'] for case in failure_cases)
        
        # Add pattern information to each case
        for case in failure_cases:
            failure_type = case['failure_type']
            frequency = failure_type_counts[failure_type]
            
            case['is_common_pattern'] = frequency >= 3
            case['pattern_frequency'] = frequency
        
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
                'by_severity': {'high': 0, 'medium': 0, 'low': 0},
                'by_type': {},
                'by_confidence': {'high': 0, 'medium': 0, 'low': 0},
                'avg_predicted_probability': 0.0,
                'avg_actual_probability': 0.0
            }
        
        # Count by severity
        severity_counts = Counter(case['severity'] for case in failure_cases)
        
        # Count by type
        type_counts = Counter(case['failure_type'] for case in failure_cases)
        
        # Count by confidence
        confidence_counts = Counter(case['confidence'] for case in failure_cases)
        
        # Average probabilities
        avg_predicted_prob = np.mean([case['predicted_probability'] for case in failure_cases])
        avg_actual_prob = np.mean([case['actual_probability'] for case in failure_cases])
        
        return {
            'total_failures': len(failure_cases),
            'by_severity': {
                'high': severity_counts.get('high', 0),
                'medium': severity_counts.get('medium', 0),
                'low': severity_counts.get('low', 0)
            },
            'by_type': dict(type_counts),
            'by_confidence': {
                'high': confidence_counts.get('high', 0),
                'medium': confidence_counts.get('medium', 0),
                'low': confidence_counts.get('low', 0)
            },
            'avg_predicted_probability': round(float(avg_predicted_prob), 4),
            'avg_actual_probability': round(float(avg_actual_prob), 4)
        }
    
    def get_actionable_insights(self, failure_cases: List[Dict]) -> List[str]:
        """
        Generate actionable insights from failure patterns.
        
        Args:
            failure_cases: List of failure case dictionaries
            
        Returns:
            List of insight strings
        """
        if not failure_cases:
            return ["No failures detected - model performing well"]
        
        insights = []
        
        # Analyze severity distribution
        severity_counts = Counter(case['severity'] for case in failure_cases)
        high_severity = severity_counts.get('high', 0)
        
        if high_severity > len(failure_cases) * 0.3:
            insights.append(
                f"High severity failures account for {high_severity/len(failure_cases):.0%} of errors. "
                "Consider adding more features or adjusting probability thresholds."
            )
        
        # Analyze confidence distribution
        confidence_counts = Counter(case['confidence'] for case in failure_cases)
        high_confidence_failures = confidence_counts.get('high', 0)
        
        if high_confidence_failures > len(failure_cases) * 0.4:
            insights.append(
                f"Model is overconfident in {high_confidence_failures/len(failure_cases):.0%} of failures. "
                "Consider calibration adjustments or ensemble methods."
            )
        
        # Analyze failure types
        type_counts = Counter(case['failure_type'] for case in failure_cases)
        most_common_type = type_counts.most_common(1)[0] if type_counts else None
        
        if most_common_type and most_common_type[1] > len(failure_cases) * 0.3:
            failure_type, count = most_common_type
            insights.append(
                f"Most common failure type is '{failure_type}' ({count/len(failure_cases):.0%}). "
                "Focus on improving features that distinguish this scenario."
            )
        
        # Analyze feature patterns
        feature_issues = []
        for case in failure_cases:
            if 'volatility' in case['reason'].lower():
                feature_issues.append('volatility')
            if 'conflicting' in case['reason'].lower():
                feature_issues.append('conflicting_signals')
            if 'regime' in case['reason'].lower():
                feature_issues.append('regime_mismatch')
        
        feature_issue_counts = Counter(feature_issues)
        if feature_issue_counts:
            top_issue = feature_issue_counts.most_common(1)[0]
            if top_issue[1] > len(failure_cases) * 0.2:
                issue_name = top_issue[0].replace('_', ' ')
                insights.append(
                    f"'{issue_name}' appears in {top_issue[1]/len(failure_cases):.0%} of failures. "
                    "Consider adding features to better capture this dynamic."
                )
        
        # General recommendation
        if len(insights) == 0:
            insights.append(
                "Failures are distributed across various scenarios. "
                "Continue monitoring and consider ensemble methods for improvement."
            )
        
        return insights

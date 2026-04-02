"""
Explanation Engine for Probabilistic Predictions.

Generates human-readable explanations for probabilistic inference results,
including feature contributions and reasoning chains.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

from utils.logger import get_logger

logger = get_logger(__name__)


class ExplanationEngine:
    """
    Generates explanations for probabilistic predictions.
    
    Provides human-readable insights into why certain predictions were made
    and which features contributed most to the outcome.
    """
    
    def __init__(self, graph_structure, inference_engine):
        """
        Initialize ExplanationEngine.
        
        Args:
            graph_structure: GraphStructure instance
            inference_engine: InferenceEngine instance
        """
        self.graph = graph_structure.graph
        self.graph_structure = graph_structure
        self.inference_engine = inference_engine
        
        # Explanation templates
        self.templates = self._load_explanation_templates()
        
        logger.info("ExplanationEngine initialized")
    
    def _load_explanation_templates(self) -> Dict:
        """Load explanation templates for different features and states."""
        return {
            'rsi_state': {
                'oversold': "RSI indicates oversold conditions ({value}), suggesting potential upward reversal",
                'neutral': "RSI is in neutral territory ({value}), indicating balanced momentum",
                'overbought': "RSI shows overbought conditions ({value}), suggesting potential downward correction"
            },
            'momentum_score_state': {
                'weak': "Momentum is weak, indicating limited directional strength",
                'moderate': "Momentum is moderate, showing some directional bias",
                'strong': "Momentum is strong, indicating clear directional movement"
            },
            'volatility_10_state': {
                'low': "Volatility is low, suggesting stable price action",
                'medium': "Volatility is moderate, indicating normal market conditions",
                'high': "Volatility is elevated, suggesting increased uncertainty and risk"
            },
            'regime_state': {
                'bull': "Market regime is bullish, favoring upward price movement",
                'bear': "Market regime is bearish, favoring downward price movement",
                'sideways': "Market is in sideways regime, lacking clear directional trend"
            },
            'macd_diff_state': {
                'bearish': "MACD histogram is negative, indicating bearish momentum",
                'bullish': "MACD histogram is positive, indicating bullish momentum"
            },
            'bb_position_state': {
                'lower': "Price is near lower Bollinger Band, potentially oversold",
                'middle': "Price is in middle of Bollinger Bands, showing normal positioning",
                'upper': "Price is near upper Bollinger Band, potentially overbought"
            },
            'volume_to_sma_state': {
                'low': "Trading volume is below average, suggesting weak participation",
                'normal': "Trading volume is normal, indicating typical market activity",
                'high': "Trading volume is above average, suggesting strong participation"
            },
            'risk_state': {
                'low': "Market risk is low, favoring position taking",
                'medium': "Market risk is moderate, requiring standard risk management",
                'high': "Market risk is elevated, suggesting caution and reduced position sizes"
            },
            'trend_slope_30_state': {
                'downtrend': "30-day trend is negative, indicating downward price trajectory",
                'flat': "30-day trend is flat, showing no clear direction",
                'uptrend': "30-day trend is positive, indicating upward price trajectory"
            }
        }
    
    def explain_prediction(self, query_var: str, evidence: Dict[str, str], 
                          prediction_result: Dict[str, float]) -> Dict:
        """
        Generate comprehensive explanation for a prediction.
        
        Args:
            query_var: Variable that was predicted
            evidence: Evidence used for prediction
            prediction_result: Probability distribution from inference
            
        Returns:
            Dictionary with explanation components
        """
        # Get most likely outcome
        most_likely = max(prediction_result, key=prediction_result.get)
        confidence = prediction_result[most_likely]
        
        # Generate explanation
        explanation = {
            'query': query_var,
            'prediction': most_likely,
            'confidence': confidence,
            'confidence_level': self._categorize_confidence(confidence),
            'evidence_summary': self._summarize_evidence(evidence),
            'key_factors': self._identify_key_factors(query_var, evidence),
            'reasoning_chain': self._build_reasoning_chain(query_var, evidence, most_likely),
            'alternative_scenarios': self._generate_alternatives(prediction_result),
            'risk_assessment': self._assess_risk(evidence, prediction_result)
        }
        
        return explanation
    
    def _categorize_confidence(self, confidence: float) -> str:
        """Categorize confidence level."""
        if confidence >= 0.75:
            return "High"
        elif confidence >= 0.55:
            return "Moderate"
        else:
            return "Low"
    
    def _summarize_evidence(self, evidence: Dict[str, str]) -> List[str]:
        """Generate human-readable summary of evidence."""
        summaries = []
        
        for feature, state in evidence.items():
            # Get base feature name (remove _state suffix)
            base_feature = feature.replace('_state', '')
            
            # Get template
            if feature in self.templates and state in self.templates[feature]:
                summary = self.templates[feature][state]
                summaries.append(summary)
            else:
                summaries.append(f"{base_feature}: {state}")
        
        return summaries
    
    def _identify_key_factors(self, query_var: str, evidence: Dict[str, str]) -> List[Dict]:
        """
        Identify which evidence factors most influence the prediction.
        
        Uses sensitivity analysis: how much does prediction change if we
        remove each piece of evidence?
        """
        key_factors = []
        
        # Get baseline prediction
        baseline_result = self.inference_engine.query([query_var], evidence)
        baseline_probs = baseline_result.get(query_var, {})
        
        # Test removing each evidence variable
        for evidence_var in evidence.keys():
            # Create evidence without this variable
            reduced_evidence = {k: v for k, v in evidence.items() if k != evidence_var}
            
            # Get prediction without this evidence
            reduced_result = self.inference_engine.query([query_var], reduced_evidence)
            reduced_probs = reduced_result.get(query_var, {})
            
            # Calculate KL divergence or total variation distance
            impact = self._calculate_distribution_distance(baseline_probs, reduced_probs)
            
            key_factors.append({
                'feature': evidence_var,
                'state': evidence[evidence_var],
                'impact_score': impact,
                'description': self._get_feature_description(evidence_var, evidence[evidence_var])
            })
        
        # Sort by impact
        key_factors.sort(key=lambda x: x['impact_score'], reverse=True)
        
        return key_factors[:5]  # Top 5 factors
    
    def _calculate_distribution_distance(self, dist1: Dict[str, float], 
                                         dist2: Dict[str, float]) -> float:
        """Calculate total variation distance between two distributions."""
        all_states = set(dist1.keys()) | set(dist2.keys())
        
        distance = 0.0
        for state in all_states:
            p1 = dist1.get(state, 0.0)
            p2 = dist2.get(state, 0.0)
            distance += abs(p1 - p2)
        
        return distance / 2.0  # Total variation distance
    
    def _get_feature_description(self, feature: str, state: str) -> str:
        """Get description for a feature-state combination."""
        if feature in self.templates and state in self.templates[feature]:
            return self.templates[feature][state]
        return f"{feature}: {state}"
    
    def _build_reasoning_chain(self, query_var: str, evidence: Dict[str, str], 
                               prediction: str) -> List[str]:
        """
        Build a chain of reasoning from evidence to prediction.
        
        Uses graph structure to show causal path.
        """
        reasoning = []
        
        # Find paths from evidence to query variable
        evidence_vars = list(evidence.keys())
        
        # Get direct parents of query variable
        parents = self.graph_structure.get_parents(query_var)
        
        # Explain direct influences
        for parent in parents:
            if parent in evidence:
                state = evidence[parent]
                reasoning.append(
                    f"• {self._get_feature_description(parent, state)} "
                    f"directly influences {query_var.replace('_state', '')}"
                )
        
        # Explain indirect influences
        for evidence_var in evidence_vars:
            if evidence_var not in parents and evidence_var != query_var:
                # Check if there's a path
                try:
                    if self.graph.has_node(evidence_var) and self.graph.has_node(query_var):
                        if evidence_var in nx.ancestors(self.graph, query_var):
                            reasoning.append(
                                f"• {evidence_var.replace('_state', '')} = {evidence[evidence_var]} "
                                f"indirectly affects prediction through intermediate factors"
                            )
                except:
                    pass
        
        # Add conclusion
        reasoning.append(
            f"• Based on these factors, {query_var.replace('_state', '')} "
            f"is predicted to be '{prediction}'"
        )
        
        return reasoning
    
    def _generate_alternatives(self, prediction_result: Dict[str, float]) -> List[Dict]:
        """Generate alternative scenarios with their probabilities."""
        alternatives = []
        
        # Sort by probability
        sorted_outcomes = sorted(prediction_result.items(), key=lambda x: x[1], reverse=True)
        
        for outcome, prob in sorted_outcomes:
            alternatives.append({
                'outcome': outcome,
                'probability': prob,
                'likelihood': self._categorize_confidence(prob)
            })
        
        return alternatives
    
    def _assess_risk(self, evidence: Dict[str, str], 
                    prediction_result: Dict[str, float]) -> Dict:
        """Assess risk based on evidence and prediction uncertainty."""
        # Check for explicit risk indicators
        risk_level = "medium"
        risk_factors = []
        
        if 'risk_state' in evidence:
            risk_level = evidence['risk_state']
            risk_factors.append(f"Explicit risk indicator: {risk_level}")
        
        if 'volatility_10_state' in evidence:
            vol = evidence['volatility_10_state']
            if vol == 'high':
                risk_factors.append("High volatility increases uncertainty")
        
        # Check prediction uncertainty
        max_prob = max(prediction_result.values())
        if max_prob < 0.6:
            risk_factors.append("Low prediction confidence suggests higher uncertainty")
        
        # Check for conflicting signals
        if 'regime_state' in evidence and 'momentum_score_state' in evidence:
            regime = evidence['regime_state']
            momentum = evidence['momentum_score_state']
            
            if (regime == 'bull' and momentum == 'weak') or \
               (regime == 'bear' and momentum == 'strong'):
                risk_factors.append("Conflicting signals between regime and momentum")
        
        return {
            'level': risk_level,
            'factors': risk_factors,
            'recommendation': self._get_risk_recommendation(risk_level, max_prob)
        }
    
    def _get_risk_recommendation(self, risk_level: str, confidence: float) -> str:
        """Generate risk management recommendation."""
        if risk_level == 'high' or confidence < 0.55:
            return "Exercise caution: Consider reduced position sizes or wait for clearer signals"
        elif risk_level == 'medium':
            return "Standard risk management: Use appropriate position sizing and stop losses"
        else:
            return "Favorable conditions: Normal position sizing with standard risk controls"
    
    def generate_text_explanation(self, explanation: Dict) -> str:
        """
        Generate formatted text explanation.
        
        Args:
            explanation: Explanation dictionary from explain_prediction
            
        Returns:
            Formatted text string
        """
        lines = []
        
        lines.append("=" * 70)
        lines.append("PROBABILISTIC PREDICTION EXPLANATION")
        lines.append("=" * 70)
        
        lines.append(f"\nPrediction: {explanation['prediction'].upper()}")
        lines.append(f"Confidence: {explanation['confidence']:.1%} ({explanation['confidence_level']})")
        
        lines.append(f"\n{'─' * 70}")
        lines.append("KEY FACTORS (by importance):")
        lines.append(f"{'─' * 70}")
        for i, factor in enumerate(explanation['key_factors'], 1):
            lines.append(f"{i}. {factor['description']}")
            lines.append(f"   Impact Score: {factor['impact_score']:.3f}")
        
        lines.append(f"\n{'─' * 70}")
        lines.append("REASONING CHAIN:")
        lines.append(f"{'─' * 70}")
        for step in explanation['reasoning_chain']:
            lines.append(step)
        
        lines.append(f"\n{'─' * 70}")
        lines.append("ALTERNATIVE SCENARIOS:")
        lines.append(f"{'─' * 70}")
        for alt in explanation['alternative_scenarios']:
            lines.append(f"• {alt['outcome']}: {alt['probability']:.1%} ({alt['likelihood']} likelihood)")
        
        lines.append(f"\n{'─' * 70}")
        lines.append("RISK ASSESSMENT:")
        lines.append(f"{'─' * 70}")
        lines.append(f"Risk Level: {explanation['risk_assessment']['level'].upper()}")
        for factor in explanation['risk_assessment']['factors']:
            lines.append(f"• {factor}")
        lines.append(f"\nRecommendation: {explanation['risk_assessment']['recommendation']}")
        
        lines.append(f"\n{'=' * 70}\n")
        
        return "\n".join(lines)
    
    def explain_batch(self, df: pd.DataFrame, query_var: str, 
                     evidence_cols: List[str]) -> pd.DataFrame:
        """
        Generate explanations for multiple predictions.
        
        Args:
            df: DataFrame with evidence and predictions
            query_var: Variable that was predicted
            evidence_cols: Columns used as evidence
            
        Returns:
            DataFrame with explanation summaries
        """
        explanations = []
        
        for idx, row in df.iterrows():
            # Build evidence
            evidence = {col: row[col] for col in evidence_cols if pd.notna(row[col])}
            
            # Get prediction
            prediction_result = self.inference_engine.query([query_var], evidence)
            
            if query_var in prediction_result:
                # Generate explanation
                explanation = self.explain_prediction(
                    query_var, evidence, prediction_result[query_var]
                )
                
                # Extract key info
                explanations.append({
                    'index': idx,
                    'prediction': explanation['prediction'],
                    'confidence': explanation['confidence'],
                    'confidence_level': explanation['confidence_level'],
                    'top_factor': explanation['key_factors'][0]['feature'] if explanation['key_factors'] else None,
                    'risk_level': explanation['risk_assessment']['level']
                })
        
        return pd.DataFrame(explanations)


# Import networkx for path finding
try:
    import networkx as nx
except ImportError:
    logger.warning("networkx not imported in explanation_engine")

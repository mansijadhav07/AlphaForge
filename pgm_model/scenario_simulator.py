"""
Scenario Simulator for What-If Analysis.

Allows users to simulate different market scenarios and observe
how predictions change under various conditions.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import itertools

from utils.logger import get_logger

logger = get_logger(__name__)


class ScenarioSimulator:
    """
    Simulates different market scenarios for what-if analysis.
    
    Enables exploration of how predictions change under different
    combinations of market conditions.
    """
    
    def __init__(self, inference_engine, explanation_engine):
        """
        Initialize ScenarioSimulator.
        
        Args:
            inference_engine: InferenceEngine instance
            explanation_engine: ExplanationEngine instance
        """
        self.inference_engine = inference_engine
        self.explanation_engine = explanation_engine
        self.state_names = inference_engine.prob_learner.state_names
        
        logger.info("ScenarioSimulator initialized")
    
    def simulate_scenario(self, scenario: Dict[str, str], 
                         query_vars: List[str]) -> Dict:
        """
        Simulate a single scenario.
        
        Args:
            scenario: Dictionary of feature states
            query_vars: Variables to predict
            
        Returns:
            Dictionary with predictions and explanations
        """
        logger.info(f"Simulating scenario: {scenario}")
        
        # Perform inference
        predictions = self.inference_engine.query(query_vars, scenario)
        
        # Generate explanations
        explanations = {}
        for query_var in query_vars:
            if query_var in predictions:
                explanation = self.explanation_engine.explain_prediction(
                    query_var, scenario, predictions[query_var]
                )
                explanations[query_var] = explanation
        
        result = {
            'scenario': scenario,
            'predictions': predictions,
            'explanations': explanations
        }
        
        return result
    
    def compare_scenarios(self, scenarios: List[Dict[str, str]], 
                         query_var: str) -> pd.DataFrame:
        """
        Compare multiple scenarios side-by-side.
        
        Args:
            scenarios: List of scenario dictionaries
            query_var: Variable to predict
            
        Returns:
            DataFrame comparing scenarios
        """
        logger.info(f"Comparing {len(scenarios)} scenarios for {query_var}")
        
        results = []
        
        for i, scenario in enumerate(scenarios):
            # Simulate scenario
            prediction = self.inference_engine.query([query_var], scenario)
            
            if query_var not in prediction:
                continue
            
            prob_dist = prediction[query_var]
            most_likely = max(prob_dist, key=prob_dist.get)
            
            # Build result row
            row = {
                'scenario_id': i,
                'prediction': most_likely,
                'confidence': prob_dist[most_likely]
            }
            
            # Add scenario features
            for feature, state in scenario.items():
                row[feature] = state
            
            # Add all probabilities
            for state, prob in prob_dist.items():
                row[f'prob_{state}'] = prob
            
            results.append(row)
        
        return pd.DataFrame(results)
    
    def sensitivity_analysis(self, base_scenario: Dict[str, str], 
                            query_var: str, 
                            vary_feature: str) -> pd.DataFrame:
        """
        Perform sensitivity analysis by varying one feature.
        
        Args:
            base_scenario: Base scenario dictionary
            query_var: Variable to predict
            vary_feature: Feature to vary across its possible states
            
        Returns:
            DataFrame showing how prediction changes
        """
        logger.info(f"Sensitivity analysis: varying {vary_feature}")
        
        if vary_feature not in self.state_names:
            logger.error(f"Feature {vary_feature} not found")
            return pd.DataFrame()
        
        results = []
        
        # Vary the feature across all possible states
        for state in self.state_names[vary_feature]:
            # Create modified scenario
            scenario = base_scenario.copy()
            scenario[vary_feature] = state
            
            # Predict
            prediction = self.inference_engine.query([query_var], scenario)
            
            if query_var not in prediction:
                continue
            
            prob_dist = prediction[query_var]
            most_likely = max(prob_dist, key=prob_dist.get)
            
            # Record result
            row = {
                vary_feature: state,
                'prediction': most_likely,
                'confidence': prob_dist[most_likely]
            }
            
            # Add all probabilities
            for outcome, prob in prob_dist.items():
                row[f'prob_{outcome}'] = prob
            
            results.append(row)
        
        return pd.DataFrame(results)
    
    def multi_feature_sensitivity(self, base_scenario: Dict[str, str],
                                  query_var: str,
                                  vary_features: List[str]) -> pd.DataFrame:
        """
        Perform sensitivity analysis varying multiple features.
        
        Args:
            base_scenario: Base scenario dictionary
            query_var: Variable to predict
            vary_features: List of features to vary
            
        Returns:
            DataFrame with all combinations
        """
        logger.info(f"Multi-feature sensitivity: {vary_features}")
        
        # Get all combinations of states for varying features
        state_combinations = []
        for feature in vary_features:
            if feature in self.state_names:
                state_combinations.append(self.state_names[feature])
            else:
                logger.warning(f"Feature {feature} not found, skipping")
        
        if len(state_combinations) != len(vary_features):
            return pd.DataFrame()
        
        results = []
        
        # Iterate over all combinations
        for combo in itertools.product(*state_combinations):
            # Create scenario
            scenario = base_scenario.copy()
            for i, feature in enumerate(vary_features):
                scenario[feature] = combo[i]
            
            # Predict
            prediction = self.inference_engine.query([query_var], scenario)
            
            if query_var not in prediction:
                continue
            
            prob_dist = prediction[query_var]
            most_likely = max(prob_dist, key=prob_dist.get)
            
            # Record result
            row = {}
            for i, feature in enumerate(vary_features):
                row[feature] = combo[i]
            
            row['prediction'] = most_likely
            row['confidence'] = prob_dist[most_likely]
            
            for outcome, prob in prob_dist.items():
                row[f'prob_{outcome}'] = prob
            
            results.append(row)
        
        df = pd.DataFrame(results)
        
        # Sort by confidence
        df = df.sort_values('confidence', ascending=False)
        
        return df
    
    def find_optimal_scenario(self, query_var: str, 
                             desired_outcome: str,
                             fixed_features: Optional[Dict[str, str]] = None,
                             vary_features: Optional[List[str]] = None) -> Dict:
        """
        Find scenario that maximizes probability of desired outcome.
        
        Args:
            query_var: Variable to optimize
            desired_outcome: Desired state (e.g., 'positive')
            fixed_features: Features that must remain fixed
            vary_features: Features allowed to vary (None = all except fixed)
            
        Returns:
            Dictionary with optimal scenario and probability
        """
        logger.info(f"Finding optimal scenario for {query_var} = {desired_outcome}")
        
        if fixed_features is None:
            fixed_features = {}
        
        # Determine which features to vary
        if vary_features is None:
            all_features = set(self.state_names.keys())
            vary_features = list(all_features - set(fixed_features.keys()) - {query_var})
        
        # Get all combinations
        state_combinations = []
        for feature in vary_features:
            if feature in self.state_names:
                state_combinations.append(self.state_names[feature])
        
        best_scenario = None
        best_probability = 0.0
        
        # Search over all combinations
        for combo in itertools.product(*state_combinations):
            # Build scenario
            scenario = fixed_features.copy()
            for i, feature in enumerate(vary_features):
                scenario[feature] = combo[i]
            
            # Predict
            prediction = self.inference_engine.query([query_var], scenario)
            
            if query_var not in prediction:
                continue
            
            prob = prediction[query_var].get(desired_outcome, 0.0)
            
            if prob > best_probability:
                best_probability = prob
                best_scenario = scenario.copy()
        
        result = {
            'optimal_scenario': best_scenario,
            'probability': best_probability,
            'outcome': desired_outcome
        }
        
        logger.info(f"Optimal scenario found with probability {best_probability:.3f}")
        
        return result
    
    def generate_scenario_report(self, scenario: Dict[str, str], 
                                query_vars: List[str]) -> str:
        """
        Generate comprehensive text report for a scenario.
        
        Args:
            scenario: Scenario dictionary
            query_vars: Variables to predict
            
        Returns:
            Formatted text report
        """
        # Simulate scenario
        result = self.simulate_scenario(scenario, query_vars)
        
        lines = []
        
        lines.append("=" * 80)
        lines.append("SCENARIO SIMULATION REPORT")
        lines.append("=" * 80)
        
        lines.append("\nSCENARIO INPUTS:")
        lines.append("─" * 80)
        for feature, state in scenario.items():
            feature_name = feature.replace('_state', '').replace('_', ' ').title()
            lines.append(f"  • {feature_name}: {state}")
        
        lines.append("\n" + "=" * 80)
        lines.append("PREDICTIONS:")
        lines.append("=" * 80)
        
        for query_var in query_vars:
            if query_var not in result['predictions']:
                continue
            
            lines.append(f"\n{query_var.replace('_state', '').replace('_', ' ').title()}:")
            lines.append("─" * 80)
            
            prob_dist = result['predictions'][query_var]
            
            # Sort by probability
            sorted_outcomes = sorted(prob_dist.items(), key=lambda x: x[1], reverse=True)
            
            for outcome, prob in sorted_outcomes:
                bar_length = int(prob * 40)
                bar = "█" * bar_length
                lines.append(f"  {outcome:12s} {prob:6.1%} {bar}")
            
            # Add explanation if available
            if query_var in result['explanations']:
                explanation = result['explanations'][query_var]
                lines.append(f"\n  Prediction: {explanation['prediction'].upper()}")
                lines.append(f"  Confidence: {explanation['confidence']:.1%} ({explanation['confidence_level']})")
                
                lines.append(f"\n  Top Contributing Factors:")
                for i, factor in enumerate(explanation['key_factors'][:3], 1):
                    lines.append(f"    {i}. {factor['description']}")
        
        lines.append("\n" + "=" * 80 + "\n")
        
        return "\n".join(lines)
    
    def batch_simulate(self, scenarios_df: pd.DataFrame, 
                      query_var: str) -> pd.DataFrame:
        """
        Simulate multiple scenarios from DataFrame.
        
        Args:
            scenarios_df: DataFrame where each row is a scenario
            query_var: Variable to predict
            
        Returns:
            DataFrame with predictions added
        """
        results = []
        
        for idx, row in scenarios_df.iterrows():
            # Build scenario from row
            scenario = row.to_dict()
            
            # Predict
            prediction = self.inference_engine.query([query_var], scenario)
            
            if query_var not in prediction:
                continue
            
            prob_dist = prediction[query_var]
            most_likely = max(prob_dist, key=prob_dist.get)
            
            # Add predictions to row
            result_row = row.to_dict()
            result_row['prediction'] = most_likely
            result_row['confidence'] = prob_dist[most_likely]
            
            for state, prob in prob_dist.items():
                result_row[f'prob_{state}'] = prob
            
            results.append(result_row)
        
        return pd.DataFrame(results)
    
    def create_scenario_grid(self, feature1: str, feature2: str, 
                            query_var: str,
                            fixed_features: Optional[Dict[str, str]] = None) -> pd.DataFrame:
        """
        Create 2D grid showing how prediction varies with two features.
        
        Args:
            feature1: First feature to vary (rows)
            feature2: Second feature to vary (columns)
            query_var: Variable to predict
            fixed_features: Other features to hold constant
            
        Returns:
            DataFrame with grid of predictions
        """
        if fixed_features is None:
            fixed_features = {}
        
        results = []
        
        for state1 in self.state_names.get(feature1, []):
            for state2 in self.state_names.get(feature2, []):
                # Build scenario
                scenario = fixed_features.copy()
                scenario[feature1] = state1
                scenario[feature2] = state2
                
                # Predict
                prediction = self.inference_engine.query([query_var], scenario)
                
                if query_var not in prediction:
                    continue
                
                prob_dist = prediction[query_var]
                most_likely = max(prob_dist, key=prob_dist.get)
                
                results.append({
                    feature1: state1,
                    feature2: state2,
                    'prediction': most_likely,
                    'confidence': prob_dist[most_likely],
                    **{f'prob_{k}': v for k, v in prob_dist.items()}
                })
        
        return pd.DataFrame(results)

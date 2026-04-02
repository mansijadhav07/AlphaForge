"""
Inference Engine for Bayesian Networks.

Performs probabilistic inference using Variable Elimination algorithm
to compute posterior probabilities given evidence.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Set
from collections import defaultdict
import itertools

from utils.logger import get_logger

logger = get_logger(__name__)


class InferenceEngine:
    """
    Performs probabilistic inference on Bayesian Networks.
    
    Implements Variable Elimination algorithm for exact inference.
    """
    
    def __init__(self, graph_structure, probability_learner):
        """
        Initialize InferenceEngine.
        
        Args:
            graph_structure: GraphStructure instance
            probability_learner: ProbabilityLearner instance with learned CPTs
        """
        self.graph = graph_structure.graph
        self.graph_structure = graph_structure
        self.prob_learner = probability_learner
        self.cpts = probability_learner.cpts
        self.state_names = probability_learner.state_names
        
        logger.info("InferenceEngine initialized")
    
    def query(self, query_vars: List[str], evidence: Optional[Dict[str, str]] = None) -> Dict:
        """
        Perform probabilistic inference.
        
        Compute P(query_vars | evidence) using Variable Elimination.
        
        Args:
            query_vars: List of variables to query
            evidence: Dictionary of observed variables {var: state}
            
        Returns:
            Dictionary with probability distributions for query variables
        """
        if evidence is None:
            evidence = {}
        
        logger.info(f"Query: P({', '.join(query_vars)} | {evidence})")
        
        results = {}
        
        for query_var in query_vars:
            if query_var not in self.graph.nodes:
                logger.warning(f"Query variable {query_var} not in graph")
                continue
            
            # Compute marginal probability for this query variable
            prob_dist = self._variable_elimination(query_var, evidence)
            results[query_var] = prob_dist
        
        return results
    
    def _variable_elimination(self, query_var: str, evidence: Dict[str, str]) -> Dict[str, float]:
        """
        Variable Elimination algorithm for exact inference.
        
        Args:
            query_var: Variable to query
            evidence: Observed variables
            
        Returns:
            Probability distribution over query variable states
        """
        # Get all variables in the network
        all_vars = set(self.graph.nodes)
        
        # Variables to eliminate = all vars - query var - evidence vars
        evidence_vars = set(evidence.keys())
        eliminate_vars = all_vars - {query_var} - evidence_vars
        
        # Get elimination order (use topological order as heuristic)
        elimination_order = [v for v in self.graph_structure.get_topological_order() 
                           if v in eliminate_vars]
        
        # Initialize factors from CPTs
        factors = self._initialize_factors(evidence)
        
        # Eliminate variables one by one
        for var in elimination_order:
            factors = self._eliminate_variable(var, factors)
        
        # Multiply remaining factors
        result_factor = self._multiply_factors(factors)
        
        # Marginalize to get distribution over query variable
        prob_dist = self._marginalize_to_query(result_factor, query_var)
        
        # Normalize
        prob_dist = self._normalize(prob_dist)
        
        return prob_dist
    
    def _initialize_factors(self, evidence: Dict[str, str]) -> List[Dict]:
        """
        Initialize factors from CPTs, incorporating evidence.
        
        Args:
            evidence: Observed variables
            
        Returns:
            List of factor dictionaries
        """
        factors = []
        
        for node in self.graph.nodes:
            if node not in self.cpts:
                continue
            
            cpt = self.cpts[node]
            
            # Create factor from CPT
            factor = self._cpt_to_factor(cpt, evidence)
            
            if factor is not None:
                factors.append(factor)
        
        return factors
    
    def _cpt_to_factor(self, cpt: Dict, evidence: Dict[str, str]) -> Optional[Dict]:
        """
        Convert CPT to factor, incorporating evidence.
        
        Args:
            cpt: Conditional Probability Table
            evidence: Observed variables
            
        Returns:
            Factor dictionary or None if fully observed
        """
        node = cpt['node']
        
        # If node is observed, create evidence factor
        if node in evidence:
            observed_state = evidence[node]
            return {
                'vars': [node],
                'values': {observed_state: 1.0},
                'type': 'evidence'
            }
        
        if cpt['type'] == 'marginal':
            return {
                'vars': [node],
                'values': cpt['probabilities'].copy(),
                'type': 'marginal'
            }
        
        elif cpt['type'] == 'conditional':
            parents = cpt['parents']
            
            # Check if all parents are observed
            observed_parents = {p: evidence[p] for p in parents if p in evidence}
            unobserved_parents = [p for p in parents if p not in evidence]
            
            if len(observed_parents) == len(parents):
                # All parents observed - reduce to marginal
                if len(parents) == 1:
                    parent_key = list(observed_parents.values())[0]
                else:
                    parent_key = tuple(observed_parents[p] for p in parents)
                
                if parent_key in cpt['table']:
                    return {
                        'vars': [node],
                        'values': cpt['table'][parent_key]['probabilities'].copy(),
                        'type': 'reduced'
                    }
            
            # Some or no parents observed - keep as conditional factor
            factor_vars = [node] + unobserved_parents
            factor_values = {}
            
            # Build factor table
            for node_state in self.state_names.get(node, []):
                if len(unobserved_parents) == 0:
                    # All parents observed (handled above, but just in case)
                    pass
                else:
                    # Iterate over unobserved parent combinations
                    parent_combinations = itertools.product(
                        *[self.state_names.get(p, []) for p in unobserved_parents]
                    )
                    
                    for parent_combo in parent_combinations:
                        # Build full parent key including observed parents
                        full_parent_dict = observed_parents.copy()
                        for i, p in enumerate(unobserved_parents):
                            full_parent_dict[p] = parent_combo[i]
                        
                        # Get probability from CPT
                        prob = self.prob_learner.get_probability(node, node_state, full_parent_dict)
                        
                        # Create factor key
                        if len(unobserved_parents) == 0:
                            factor_key = (node_state,)
                        else:
                            factor_key = (node_state,) + parent_combo
                        
                        factor_values[factor_key] = prob
            
            return {
                'vars': factor_vars,
                'values': factor_values,
                'type': 'conditional'
            }
        
        return None
    
    def _eliminate_variable(self, var: str, factors: List[Dict]) -> List[Dict]:
        """
        Eliminate a variable by multiplying relevant factors and summing out.
        
        Args:
            var: Variable to eliminate
            factors: List of factors
            
        Returns:
            Updated list of factors
        """
        # Find factors containing the variable
        relevant_factors = [f for f in factors if var in f['vars']]
        other_factors = [f for f in factors if var not in f['vars']]
        
        if len(relevant_factors) == 0:
            return factors
        
        # Multiply relevant factors
        product_factor = self._multiply_factors(relevant_factors)
        
        # Sum out the variable
        marginalized_factor = self._sum_out_variable(product_factor, var)
        
        # Return updated factor list
        if marginalized_factor is not None:
            return other_factors + [marginalized_factor]
        else:
            return other_factors
    
    def _multiply_factors(self, factors: List[Dict]) -> Dict:
        """
        Multiply multiple factors together.
        
        Args:
            factors: List of factors to multiply
            
        Returns:
            Product factor
        """
        if len(factors) == 0:
            return {'vars': [], 'values': {(): 1.0}, 'type': 'empty'}
        
        if len(factors) == 1:
            return factors[0]
        
        # Start with first factor
        result = factors[0]
        
        # Multiply with remaining factors
        for factor in factors[1:]:
            result = self._multiply_two_factors(result, factor)
        
        return result
    
    def _multiply_two_factors(self, factor1: Dict, factor2: Dict) -> Dict:
        """
        Multiply two factors.
        
        Args:
            factor1: First factor
            factor2: Second factor
            
        Returns:
            Product factor
        """
        # Get union of variables
        vars1 = factor1['vars']
        vars2 = factor2['vars']
        result_vars = list(dict.fromkeys(vars1 + vars2))  # Preserve order, remove duplicates
        
        # Build result factor
        result_values = {}
        
        # Get all combinations of result variables
        var_states = [self.state_names.get(v, ['unknown']) for v in result_vars]
        
        for state_combo in itertools.product(*var_states):
            # Map to variable assignments
            assignment = dict(zip(result_vars, state_combo))
            
            # Get values from both factors
            val1 = self._get_factor_value(factor1, assignment)
            val2 = self._get_factor_value(factor2, assignment)
            
            # Multiply
            result_values[state_combo] = val1 * val2
        
        return {
            'vars': result_vars,
            'values': result_values,
            'type': 'product'
        }
    
    def _get_factor_value(self, factor: Dict, assignment: Dict[str, str]) -> float:
        """
        Get value from factor given variable assignment.
        
        Args:
            factor: Factor dictionary
            assignment: Variable assignments
            
        Returns:
            Factor value
        """
        # Build key from assignment
        key = tuple(assignment[v] for v in factor['vars'])
        
        if len(key) == 0:
            key = ()
        elif len(key) == 1:
            # Try both tuple and single value
            if key in factor['values']:
                return factor['values'][key]
            elif key[0] in factor['values']:
                return factor['values'][key[0]]
        
        return factor['values'].get(key, 0.0)
    
    def _sum_out_variable(self, factor: Dict, var: str) -> Optional[Dict]:
        """
        Sum out (marginalize) a variable from a factor.
        
        Args:
            factor: Factor to marginalize
            var: Variable to sum out
            
        Returns:
            Marginalized factor or None if factor becomes empty
        """
        if var not in factor['vars']:
            return factor
        
        # Get remaining variables
        remaining_vars = [v for v in factor['vars'] if v != var]
        
        if len(remaining_vars) == 0:
            # Factor becomes a constant
            total = sum(factor['values'].values())
            return {'vars': [], 'values': {(): total}, 'type': 'constant'}
        
        # Build new factor
        result_values = defaultdict(float)
        
        for state_combo, value in factor['values'].items():
            # Remove the variable being summed out
            var_idx = factor['vars'].index(var)
            
            if isinstance(state_combo, tuple):
                remaining_combo = tuple(s for i, s in enumerate(state_combo) if i != var_idx)
            else:
                remaining_combo = ()
            
            result_values[remaining_combo] += value
        
        return {
            'vars': remaining_vars,
            'values': dict(result_values),
            'type': 'marginalized'
        }
    
    def _marginalize_to_query(self, factor: Dict, query_var: str) -> Dict[str, float]:
        """
        Marginalize factor to get distribution over query variable.
        
        Args:
            factor: Factor to marginalize
            query_var: Query variable
            
        Returns:
            Probability distribution
        """
        if query_var not in factor['vars']:
            # Query variable not in factor - return uniform
            states = self.state_names.get(query_var, ['unknown'])
            uniform_prob = 1.0 / len(states)
            return {state: uniform_prob for state in states}
        
        # Sum out all variables except query variable
        result = factor
        for var in factor['vars']:
            if var != query_var:
                result = self._sum_out_variable(result, var)
        
        # Convert to dictionary
        prob_dist = {}
        for state_combo, value in result['values'].items():
            if isinstance(state_combo, tuple) and len(state_combo) > 0:
                state = state_combo[0]
            elif isinstance(state_combo, str):
                state = state_combo
            else:
                continue
            
            prob_dist[state] = value
        
        return prob_dist
    
    def _normalize(self, prob_dist: Dict[str, float]) -> Dict[str, float]:
        """
        Normalize probability distribution to sum to 1.
        
        Args:
            prob_dist: Probability distribution
            
        Returns:
            Normalized distribution
        """
        total = sum(prob_dist.values())
        
        if total == 0:
            # Uniform distribution
            n = len(prob_dist)
            return {state: 1.0/n for state in prob_dist.keys()}
        
        return {state: prob / total for state, prob in prob_dist.items()}
    
    def predict_most_likely(self, query_var: str, evidence: Optional[Dict[str, str]] = None) -> Tuple[str, float]:
        """
        Predict most likely state for a query variable.
        
        Args:
            query_var: Variable to predict
            evidence: Observed variables
            
        Returns:
            Tuple of (most_likely_state, probability)
        """
        prob_dist = self.query([query_var], evidence)[query_var]
        
        most_likely_state = max(prob_dist, key=prob_dist.get)
        probability = prob_dist[most_likely_state]
        
        return most_likely_state, probability
    
    def compute_signal_probabilities(self, evidence: Dict[str, str]) -> Dict[str, float]:
        """
        Compute trading signal probabilities.
        
        Args:
            evidence: Current market state
            
        Returns:
            Dictionary with buy/sell/hold probabilities
        """
        # Query future return
        result = self.query(['future_return_state'], evidence)
        
        if 'future_return_state' not in result:
            return {'buy': 0.33, 'hold': 0.34, 'sell': 0.33}
        
        prob_dist = result['future_return_state']
        
        # Map to trading signals
        signals = {
            'buy': prob_dist.get('positive', 0.0),
            'hold': prob_dist.get('neutral', 0.0),
            'sell': prob_dist.get('negative', 0.0)
        }
        
        return signals
    
    def batch_inference(self, df: pd.DataFrame, query_vars: List[str], 
                       evidence_cols: List[str]) -> pd.DataFrame:
        """
        Perform inference on multiple data points.
        
        Args:
            df: DataFrame with evidence
            query_vars: Variables to query
            evidence_cols: Columns to use as evidence
            
        Returns:
            DataFrame with predicted probabilities
        """
        results = []
        
        for idx, row in df.iterrows():
            # Build evidence dictionary
            evidence = {col: row[col] for col in evidence_cols if pd.notna(row[col])}
            
            # Perform inference
            query_result = self.query(query_vars, evidence)
            
            # Flatten results
            row_result = {'index': idx}
            for var, prob_dist in query_result.items():
                for state, prob in prob_dist.items():
                    row_result[f'{var}_{state}_prob'] = prob
            
            results.append(row_result)
        
        return pd.DataFrame(results)

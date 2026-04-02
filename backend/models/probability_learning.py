"""
Probability Learning Engine for Bayesian Networks.

Learns Conditional Probability Tables (CPTs) from historical data
using frequency-based estimation with Laplace smoothing.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import pickle
from pathlib import Path
from collections import defaultdict
import itertools

from utils.logger import get_logger

logger = get_logger(__name__)


class ProbabilityLearner:
    """
    Learns conditional probability distributions for Bayesian Network nodes.
    
    Uses frequency-based estimation with Laplace smoothing to handle
    sparse data and unseen combinations.
    """
    
    def __init__(self, graph_structure, smoothing_alpha: float = 1.0):
        """
        Initialize ProbabilityLearner.
        
        Args:
            graph_structure: GraphStructure instance defining the network
            smoothing_alpha: Laplace smoothing parameter (default: 1.0)
        """
        self.graph = graph_structure.graph
        self.smoothing_alpha = smoothing_alpha
        self.cpts = {}  # Conditional Probability Tables
        self.cardinalities = {}  # Number of states per variable
        self.state_names = {}  # Possible states for each variable
        
        logger.info(f"ProbabilityLearner initialized with alpha={smoothing_alpha}")
    
    def learn_from_data(self, df: pd.DataFrame):
        """
        Learn all CPTs from data.
        
        Args:
            df: DataFrame with encoded state columns
        """
        logger.info("Learning conditional probability tables from data...")
        
        # First pass: learn cardinalities and state names
        self._learn_cardinalities(df)
        
        # Second pass: learn CPTs for each node
        for node in self.graph.nodes:
            if node not in df.columns:
                logger.warning(f"Node {node} not found in data, skipping")
                continue
            
            parents = list(self.graph.predecessors(node))
            
            if len(parents) == 0:
                # Root node: learn marginal probability
                self.cpts[node] = self._learn_marginal(df, node)
            else:
                # Non-root node: learn conditional probability
                self.cpts[node] = self._learn_conditional(df, node, parents)
        
        logger.info(f"Learned {len(self.cpts)} CPTs")
    
    def _learn_cardinalities(self, df: pd.DataFrame):
        """Learn the number of states for each variable."""
        for node in self.graph.nodes:
            if node in df.columns:
                unique_states = df[node].dropna().unique()
                self.cardinalities[node] = len(unique_states)
                self.state_names[node] = sorted(unique_states)
                logger.debug(f"{node}: {self.cardinalities[node]} states = {self.state_names[node]}")
    
    def _learn_marginal(self, df: pd.DataFrame, node: str) -> Dict:
        """
        Learn marginal probability P(X) for a root node.
        
        Args:
            df: DataFrame with data
            node: Node name
            
        Returns:
            Dictionary with probability distribution
        """
        # Count occurrences
        counts = df[node].value_counts().to_dict()
        total = df[node].notna().sum()
        
        # Apply Laplace smoothing
        cardinality = self.cardinalities[node]
        smoothed_total = total + self.smoothing_alpha * cardinality
        
        probabilities = {}
        for state in self.state_names[node]:
            count = counts.get(state, 0)
            probabilities[state] = (count + self.smoothing_alpha) / smoothed_total
        
        cpt = {
            'type': 'marginal',
            'node': node,
            'probabilities': probabilities,
            'sample_size': total
        }
        
        logger.debug(f"Learned marginal for {node}: {probabilities}")
        
        return cpt
    
    def _learn_conditional(self, df: pd.DataFrame, node: str, parents: List[str]) -> Dict:
        """
        Learn conditional probability P(X | Parents) for a non-root node.
        
        Args:
            df: DataFrame with data
            node: Node name
            parents: List of parent node names
            
        Returns:
            Dictionary with conditional probability table
        """
        # Filter out rows with missing values
        required_cols = [node] + parents
        valid_df = df[required_cols].dropna()
        
        if len(valid_df) == 0:
            logger.warning(f"No valid data for {node} given {parents}")
            return self._create_uniform_cpt(node, parents)
        
        # Group by parent states and count child states
        parent_cols = parents
        grouped = valid_df.groupby(parent_cols)[node].value_counts()
        
        # Build CPT
        cpt_table = {}
        cardinality = self.cardinalities[node]
        
        # Get all possible parent combinations
        parent_state_combinations = list(itertools.product(
            *[self.state_names[p] for p in parents]
        ))
        
        for parent_combo in parent_state_combinations:
            # Convert to tuple for dictionary key
            if len(parents) == 1:
                parent_key = parent_combo[0]
                lookup_key = parent_combo[0]
            else:
                parent_key = parent_combo
                lookup_key = parent_combo
            
            # Count occurrences for this parent combination
            try:
                if len(parents) == 1:
                    counts = grouped[lookup_key].to_dict() if lookup_key in grouped.index else {}
                else:
                    counts = grouped[lookup_key].to_dict() if lookup_key in grouped.index else {}
            except (KeyError, TypeError):
                counts = {}
            
            total = sum(counts.values())
            
            # Apply Laplace smoothing
            smoothed_total = total + self.smoothing_alpha * cardinality
            
            # Calculate probabilities
            probabilities = {}
            for state in self.state_names[node]:
                count = counts.get(state, 0)
                probabilities[state] = (count + self.smoothing_alpha) / smoothed_total
            
            cpt_table[parent_key] = {
                'probabilities': probabilities,
                'sample_size': total
            }
        
        cpt = {
            'type': 'conditional',
            'node': node,
            'parents': parents,
            'table': cpt_table
        }
        
        logger.debug(f"Learned conditional for {node} | {parents}")
        
        return cpt
    
    def _create_uniform_cpt(self, node: str, parents: List[str]) -> Dict:
        """Create uniform CPT when no data is available."""
        cardinality = self.cardinalities.get(node, 2)
        uniform_prob = 1.0 / cardinality
        
        probabilities = {state: uniform_prob for state in self.state_names.get(node, ['unknown'])}
        
        cpt = {
            'type': 'conditional',
            'node': node,
            'parents': parents,
            'table': {'default': {'probabilities': probabilities, 'sample_size': 0}}
        }
        
        logger.warning(f"Created uniform CPT for {node}")
        
        return cpt
    
    def get_probability(self, node: str, state: str, evidence: Optional[Dict] = None) -> float:
        """
        Get probability P(node=state | evidence).
        
        Args:
            node: Node name
            state: State value
            evidence: Dictionary of parent states (if applicable)
            
        Returns:
            Probability value
        """
        if node not in self.cpts:
            logger.warning(f"No CPT for {node}")
            return 1.0 / self.cardinalities.get(node, 2)
        
        cpt = self.cpts[node]
        
        if cpt['type'] == 'marginal':
            return cpt['probabilities'].get(state, 0.0)
        
        elif cpt['type'] == 'conditional':
            parents = cpt['parents']
            
            if evidence is None:
                logger.warning(f"No evidence provided for conditional node {node}")
                return 1.0 / self.cardinalities.get(node, 2)
            
            # Build parent key from evidence
            if len(parents) == 1:
                parent_key = evidence.get(parents[0])
            else:
                parent_key = tuple(evidence.get(p) for p in parents)
            
            # Look up in table
            if parent_key in cpt['table']:
                return cpt['table'][parent_key]['probabilities'].get(state, 0.0)
            else:
                # Unseen parent combination - use uniform
                logger.debug(f"Unseen parent combination for {node}: {parent_key}")
                return 1.0 / self.cardinalities.get(node, 2)
        
        return 0.0
    
    def get_cpt_summary(self, node: str) -> Dict:
        """
        Get summary of CPT for a node.
        
        Args:
            node: Node name
            
        Returns:
            Dictionary with CPT summary
        """
        if node not in self.cpts:
            return {'error': f'No CPT for {node}'}
        
        cpt = self.cpts[node]
        
        summary = {
            'node': node,
            'type': cpt['type'],
            'cardinality': self.cardinalities.get(node, 0),
            'states': self.state_names.get(node, [])
        }
        
        if cpt['type'] == 'marginal':
            summary['probabilities'] = cpt['probabilities']
            summary['sample_size'] = cpt['sample_size']
        
        elif cpt['type'] == 'conditional':
            summary['parents'] = cpt['parents']
            summary['num_parent_combinations'] = len(cpt['table'])
            
            # Sample a few entries
            sample_entries = dict(list(cpt['table'].items())[:3])
            summary['sample_entries'] = sample_entries
        
        return summary
    
    def validate_cpts(self) -> Dict[str, bool]:
        """
        Validate that all CPTs sum to 1.0.
        
        Returns:
            Dictionary mapping node names to validation status
        """
        validation = {}
        
        for node, cpt in self.cpts.items():
            if cpt['type'] == 'marginal':
                prob_sum = sum(cpt['probabilities'].values())
                validation[node] = np.isclose(prob_sum, 1.0, atol=1e-6)
                
                if not validation[node]:
                    logger.warning(f"{node} marginal probabilities sum to {prob_sum}")
            
            elif cpt['type'] == 'conditional':
                all_valid = True
                for parent_key, entry in cpt['table'].items():
                    prob_sum = sum(entry['probabilities'].values())
                    if not np.isclose(prob_sum, 1.0, atol=1e-6):
                        logger.warning(f"{node} | {parent_key} probabilities sum to {prob_sum}")
                        all_valid = False
                
                validation[node] = all_valid
        
        return validation
    
    def save_cpts(self, path: str):
        """
        Save learned CPTs to file.
        
        Args:
            path: Output file path
        """
        data = {
            'cpts': self.cpts,
            'cardinalities': self.cardinalities,
            'state_names': self.state_names,
            'smoothing_alpha': self.smoothing_alpha
        }
        
        with open(path, 'wb') as f:
            pickle.dump(data, f)
        
        logger.info(f"CPTs saved to {path}")
    
    def load_cpts(self, path: str):
        """
        Load CPTs from file.
        
        Args:
            path: Input file path
        """
        with open(path, 'rb') as f:
            data = pickle.load(f)
        
        self.cpts = data['cpts']
        self.cardinalities = data['cardinalities']
        self.state_names = data['state_names']
        self.smoothing_alpha = data['smoothing_alpha']
        
        logger.info(f"CPTs loaded from {path}")
    
    def get_all_cpts(self) -> Dict:
        """Get all learned CPTs."""
        return self.cpts
    
    def print_cpt(self, node: str):
        """
        Print CPT for a node in human-readable format.
        
        Args:
            node: Node name
        """
        if node not in self.cpts:
            print(f"No CPT for {node}")
            return
        
        cpt = self.cpts[node]
        
        print(f"\n{'='*60}")
        print(f"CPT for: {node}")
        print(f"Type: {cpt['type']}")
        print(f"{'='*60}")
        
        if cpt['type'] == 'marginal':
            print(f"\nP({node}):")
            for state, prob in cpt['probabilities'].items():
                print(f"  {state}: {prob:.4f}")
            print(f"\nSample size: {cpt['sample_size']}")
        
        elif cpt['type'] == 'conditional':
            print(f"\nP({node} | {', '.join(cpt['parents'])}):")
            print(f"\nNumber of parent combinations: {len(cpt['table'])}")
            
            for parent_key, entry in list(cpt['table'].items())[:5]:  # Show first 5
                print(f"\n  Given {cpt['parents']} = {parent_key}:")
                for state, prob in entry['probabilities'].items():
                    print(f"    {state}: {prob:.4f}")
                print(f"    (n={entry['sample_size']})")
            
            if len(cpt['table']) > 5:
                print(f"\n  ... and {len(cpt['table']) - 5} more combinations")
        
        print(f"{'='*60}\n")

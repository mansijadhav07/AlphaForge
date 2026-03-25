"""
Graph Structure Definition for Bayesian Networks.

Defines the directed acyclic graph (DAG) structure representing
causal and probabilistic dependencies between financial features.
"""

import networkx as nx
import matplotlib.pyplot as plt
from typing import List, Tuple, Dict, Optional
import json
from pathlib import Path

from utils.logger import get_logger

logger = get_logger(__name__)


class GraphStructure:
    """
    Manages Bayesian Network graph structure (DAG).
    
    Defines nodes (features) and edges (dependencies) for probabilistic modeling.
    """
    
    def __init__(self):
        """Initialize empty graph structure."""
        self.graph = nx.DiGraph()
        self.node_metadata = {}
        logger.info("GraphStructure initialized")
    
    def build_default_structure(self) -> nx.DiGraph:
        """
        Build default financial feature dependency graph.
        
        Returns:
            NetworkX DiGraph representing the Bayesian Network structure
        """
        logger.info("Building default graph structure...")
        
        # Define nodes (features)
        nodes = [
            'rsi_state',
            'momentum_score_state',
            'volatility_10_state',
            'trend_slope_30_state',
            'regime_state',
            'macd_diff_state',
            'bb_position_state',
            'volume_to_sma_state',
            'atr_pct_state',
            'risk_state',
            'future_return_state'
        ]
        
        # Add nodes with metadata
        for node in nodes:
            self.add_node(node, description=self._get_node_description(node))
        
        # Define edges (dependencies)
        # Format: (parent, child)
        edges = [
            # Technical indicators -> Future return
            ('rsi_state', 'future_return_state'),
            ('momentum_score_state', 'future_return_state'),
            ('macd_diff_state', 'future_return_state'),
            
            # Volatility -> Risk
            ('volatility_10_state', 'risk_state'),
            ('atr_pct_state', 'risk_state'),
            
            # Trend -> Regime
            ('trend_slope_30_state', 'regime_state'),
            ('momentum_score_state', 'regime_state'),
            
            # Regime -> Future return
            ('regime_state', 'future_return_state'),
            
            # Risk -> Future return
            ('risk_state', 'future_return_state'),
            
            # Bollinger Bands -> Future return
            ('bb_position_state', 'future_return_state'),
            
            # Volume -> Future return
            ('volume_to_sma_state', 'future_return_state'),
            
            # Cross-dependencies
            ('volatility_10_state', 'regime_state'),
            ('rsi_state', 'momentum_score_state'),
        ]
        
        # Add edges
        for parent, child in edges:
            self.add_edge(parent, child)
        
        # Validate DAG
        if not nx.is_directed_acyclic_graph(self.graph):
            raise ValueError("Graph contains cycles! Must be a DAG.")
        
        logger.info(f"Graph structure built: {len(self.graph.nodes)} nodes, {len(self.graph.edges)} edges")
        
        return self.graph
    
    def add_node(self, node: str, description: str = ""):
        """
        Add a node to the graph.
        
        Args:
            node: Node name (feature state)
            description: Human-readable description
        """
        self.graph.add_node(node)
        self.node_metadata[node] = {'description': description}
        logger.debug(f"Added node: {node}")
    
    def add_edge(self, parent: str, child: str, weight: float = 1.0):
        """
        Add a directed edge to the graph.
        
        Args:
            parent: Parent node
            child: Child node
            weight: Edge weight (optional)
        """
        if parent not in self.graph.nodes:
            raise ValueError(f"Parent node {parent} not in graph")
        if child not in self.graph.nodes:
            raise ValueError(f"Child node {child} not in graph")
        
        self.graph.add_edge(parent, child, weight=weight)
        logger.debug(f"Added edge: {parent} -> {child}")
    
    def remove_edge(self, parent: str, child: str):
        """Remove an edge from the graph."""
        if self.graph.has_edge(parent, child):
            self.graph.remove_edge(parent, child)
            logger.debug(f"Removed edge: {parent} -> {child}")
    
    def get_parents(self, node: str) -> List[str]:
        """
        Get parent nodes of a given node.
        
        Args:
            node: Node name
            
        Returns:
            List of parent node names
        """
        return list(self.graph.predecessors(node))
    
    def get_children(self, node: str) -> List[str]:
        """
        Get child nodes of a given node.
        
        Args:
            node: Node name
            
        Returns:
            List of child node names
        """
        return list(self.graph.successors(node))
    
    def get_markov_blanket(self, node: str) -> List[str]:
        """
        Get Markov blanket of a node.
        
        The Markov blanket includes:
        - Parents
        - Children
        - Parents of children (co-parents)
        
        Args:
            node: Node name
            
        Returns:
            List of nodes in Markov blanket
        """
        blanket = set()
        
        # Add parents
        blanket.update(self.get_parents(node))
        
        # Add children
        children = self.get_children(node)
        blanket.update(children)
        
        # Add co-parents (parents of children)
        for child in children:
            blanket.update(self.get_parents(child))
        
        # Remove the node itself
        blanket.discard(node)
        
        return list(blanket)
    
    def get_topological_order(self) -> List[str]:
        """
        Get topological ordering of nodes.
        
        Returns:
            List of nodes in topological order
        """
        return list(nx.topological_sort(self.graph))
    
    def validate_dag(self) -> bool:
        """
        Validate that graph is a valid DAG.
        
        Returns:
            True if valid DAG, False otherwise
        """
        is_dag = nx.is_directed_acyclic_graph(self.graph)
        
        if is_dag:
            logger.info("Graph is a valid DAG")
        else:
            logger.error("Graph contains cycles!")
            try:
                cycle = nx.find_cycle(self.graph)
                logger.error(f"Cycle found: {cycle}")
            except nx.NetworkXNoCycle:
                pass
        
        return is_dag
    
    def visualize(self, output_path: Optional[str] = None, figsize: Tuple[int, int] = (14, 10)):
        """
        Visualize the graph structure.
        
        Args:
            output_path: Path to save figure (None = display only)
            figsize: Figure size
        """
        plt.figure(figsize=figsize)
        
        # Use hierarchical layout
        pos = nx.spring_layout(self.graph, k=2, iterations=50, seed=42)
        
        # Try to use hierarchical layout if possible
        try:
            pos = self._hierarchical_layout()
        except:
            pass
        
        # Color nodes by type
        node_colors = []
        for node in self.graph.nodes():
            if 'future_return' in node:
                node_colors.append('#FF6B6B')  # Red for target
            elif 'risk' in node or 'regime' in node:
                node_colors.append('#4ECDC4')  # Teal for derived
            else:
                node_colors.append('#95E1D3')  # Light green for features
        
        # Draw graph
        nx.draw(
            self.graph,
            pos,
            with_labels=True,
            node_color=node_colors,
            node_size=3000,
            font_size=9,
            font_weight='bold',
            arrows=True,
            arrowsize=20,
            edge_color='#666',
            linewidths=2,
            arrowstyle='->',
            connectionstyle='arc3,rad=0.1'
        )
        
        plt.title("Bayesian Network Structure - Financial Features", fontsize=16, fontweight='bold')
        plt.axis('off')
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            logger.info(f"Graph visualization saved to {output_path}")
        else:
            plt.show()
        
        plt.close()
    
    def _hierarchical_layout(self) -> Dict:
        """Create hierarchical layout for DAG."""
        # Get topological generations
        generations = list(nx.topological_generations(self.graph))
        
        pos = {}
        for i, generation in enumerate(generations):
            nodes = list(generation)
            for j, node in enumerate(nodes):
                x = j - (len(nodes) - 1) / 2
                y = -i
                pos[node] = (x, y)
        
        return pos
    
    def _get_node_description(self, node: str) -> str:
        """Get description for a node."""
        descriptions = {
            'rsi_state': 'Relative Strength Index (momentum)',
            'momentum_score_state': 'Composite momentum indicator',
            'volatility_10_state': '10-day volatility',
            'trend_slope_30_state': '30-day trend direction',
            'regime_state': 'Market regime (bull/bear/sideways)',
            'macd_diff_state': 'MACD histogram',
            'bb_position_state': 'Bollinger Band position',
            'volume_to_sma_state': 'Volume relative to average',
            'atr_pct_state': 'Average True Range percentage',
            'risk_state': 'Market risk level',
            'future_return_state': 'Future return prediction'
        }
        return descriptions.get(node, node)
    
    def get_graph_info(self) -> Dict:
        """
        Get comprehensive graph information.
        
        Returns:
            Dictionary with graph statistics and structure
        """
        info = {
            'num_nodes': len(self.graph.nodes),
            'num_edges': len(self.graph.edges),
            'is_dag': nx.is_directed_acyclic_graph(self.graph),
            'nodes': list(self.graph.nodes),
            'edges': list(self.graph.edges),
            'topological_order': self.get_topological_order() if nx.is_directed_acyclic_graph(self.graph) else None,
            'node_metadata': self.node_metadata
        }
        
        # Add node statistics
        info['node_stats'] = {}
        for node in self.graph.nodes:
            info['node_stats'][node] = {
                'parents': self.get_parents(node),
                'children': self.get_children(node),
                'markov_blanket_size': len(self.get_markov_blanket(node))
            }
        
        return info
    
    def save_structure(self, path: str):
        """
        Save graph structure to JSON file.
        
        Args:
            path: Output file path
        """
        structure = {
            'nodes': [
                {'name': node, 'metadata': self.node_metadata.get(node, {})}
                for node in self.graph.nodes
            ],
            'edges': [
                {'parent': u, 'child': v, 'weight': self.graph[u][v].get('weight', 1.0)}
                for u, v in self.graph.edges
            ]
        }
        
        with open(path, 'w') as f:
            json.dump(structure, f, indent=2)
        
        logger.info(f"Graph structure saved to {path}")
    
    def load_structure(self, path: str):
        """
        Load graph structure from JSON file.
        
        Args:
            path: Input file path
        """
        with open(path, 'r') as f:
            structure = json.load(f)
        
        # Clear existing graph
        self.graph.clear()
        self.node_metadata.clear()
        
        # Add nodes
        for node_data in structure['nodes']:
            self.add_node(
                node_data['name'],
                description=node_data['metadata'].get('description', '')
            )
        
        # Add edges
        for edge_data in structure['edges']:
            self.add_edge(
                edge_data['parent'],
                edge_data['child'],
                weight=edge_data.get('weight', 1.0)
            )
        
        logger.info(f"Graph structure loaded from {path}")
        
        # Validate
        self.validate_dag()
    
    def get_conditional_independencies(self) -> List[Tuple]:
        """
        Get conditional independencies implied by the graph structure.
        
        Returns:
            List of (X, Y, Z) tuples where X is independent of Y given Z
        """
        independencies = []
        
        # For each pair of nodes
        nodes = list(self.graph.nodes)
        for i, x in enumerate(nodes):
            for y in nodes[i+1:]:
                # Check if they are d-separated given various conditioning sets
                markov_blanket_x = set(self.get_markov_blanket(x))
                markov_blanket_y = set(self.get_markov_blanket(y))
                
                # Simple check: if not in each other's Markov blanket
                if y not in markov_blanket_x and x not in markov_blanket_y:
                    conditioning_set = markov_blanket_x.union(markov_blanket_y)
                    independencies.append((x, y, list(conditioning_set)))
        
        return independencies


def create_risk_node_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create synthetic 'risk_state' node based on volatility and ATR.
    
    Args:
        df: DataFrame with encoded states
        
    Returns:
        DataFrame with risk_state column
    """
    result = df.copy()
    
    # Simple rule: combine volatility and ATR
    if 'volatility_10_state' in df.columns and 'atr_pct_state' in df.columns:
        risk_mapping = {
            ('low', 'low'): 'low',
            ('low', 'medium'): 'low',
            ('low', 'high'): 'medium',
            ('medium', 'low'): 'low',
            ('medium', 'medium'): 'medium',
            ('medium', 'high'): 'high',
            ('high', 'low'): 'medium',
            ('high', 'medium'): 'high',
            ('high', 'high'): 'high',
        }
        
        result['risk_state'] = result.apply(
            lambda row: risk_mapping.get(
                (row.get('volatility_10_state', 'medium'), 
                 row.get('atr_pct_state', 'medium')),
                'medium'
            ),
            axis=1
        )
        
        logger.info("Created risk_state node")
    else:
        logger.warning("Required columns for risk_state not found")
    
    return result

"""
Probabilistic Graphical Model (PGM) Module for AlphaForge.

This module implements Bayesian Networks for modeling dependencies between
financial features and performing probabilistic inference for market outcomes.
"""

from .state_encoding import StateEncoder
from .graph_structure import GraphStructure
from .probability_learning import ProbabilityLearner
from .inference_engine import InferenceEngine
from .explanation_engine import ExplanationEngine
from .scenario_simulator import ScenarioSimulator

__all__ = [
    'StateEncoder',
    'GraphStructure',
    'ProbabilityLearner',
    'InferenceEngine',
    'ExplanationEngine',
    'ScenarioSimulator',
]

__version__ = '1.0.0'

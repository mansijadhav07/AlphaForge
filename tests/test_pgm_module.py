"""
Unit tests for PGM module.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path

from backend.models.state_encoding import StateEncoder, create_target_variable
from backend.models.graph_structure import GraphStructure, create_risk_node_data
from backend.models.probability_learning import ProbabilityLearner
from backend.models.inference_engine import InferenceEngine
from backend.models.explanation_engine import ExplanationEngine
from backend.models.scenario_simulator import ScenarioSimulator


@pytest.fixture
def sample_data():
    """Create sample financial data for testing."""
    np.random.seed(42)
    n = 100
    
    df = pd.DataFrame({
        'ticker': ['AAPL'] * n,
        'date': pd.date_range('2024-01-01', periods=n),
        'close': 150 + np.cumsum(np.random.randn(n) * 2),
        'rsi': np.random.uniform(20, 80, n),
        'momentum_score': np.random.uniform(-1, 1, n),
        'volatility_10': np.random.uniform(0.01, 0.05, n),
        'trend_slope_30': np.random.uniform(-1, 1, n),
        'regime': np.random.choice([-1, 0, 1], n),
        'macd_diff': np.random.uniform(-2, 2, n),
        'bb_position': np.random.uniform(0, 1, n),
        'volume_to_sma': np.random.uniform(0.5, 1.5, n),
        'atr_pct': np.random.uniform(0.01, 0.04, n),
    })
    
    return df


class TestStateEncoder:
    """Test StateEncoder functionality."""
    
    def test_initialization(self):
        """Test encoder initialization."""
        encoder = StateEncoder()
        assert encoder is not None
        assert len(encoder.encoding_rules) > 0
    
    def test_fit_transform(self, sample_data):
        """Test fit and transform."""
        encoder = StateEncoder()
        encoded_df = encoder.fit_transform(sample_data)
        
        # Check that state columns were created
        state_cols = [col for col in encoded_df.columns if col.endswith('_state')]
        assert len(state_cols) > 0
        
        # Check RSI encoding
        assert 'rsi_state' in encoded_df.columns
        assert set(encoded_df['rsi_state'].dropna().unique()).issubset({'oversold', 'neutral', 'overbought'})
    
    def test_custom_rule(self):
        """Test adding custom encoding rule."""
        encoder = StateEncoder()
        
        custom_rule = {
            'type': 'threshold',
            'thresholds': [50],
            'labels': ['low', 'high'],
            'description': 'Test feature'
        }
        
        encoder.add_custom_rule('test_feature', custom_rule)
        assert 'test_feature' in encoder.encoding_rules


class TestGraphStructure:
    """Test GraphStructure functionality."""
    
    def test_build_default_structure(self):
        """Test building default graph."""
        graph_structure = GraphStructure()
        graph = graph_structure.build_default_structure()
        
        assert len(graph.nodes) > 0
        assert len(graph.edges) > 0
        assert graph_structure.validate_dag()
    
    def test_get_parents(self):
        """Test getting parent nodes."""
        graph_structure = GraphStructure()
        graph_structure.build_default_structure()
        
        parents = graph_structure.get_parents('future_return_state')
        assert len(parents) > 0
    
    def test_markov_blanket(self):
        """Test Markov blanket computation."""
        graph_structure = GraphStructure()
        graph_structure.build_default_structure()
        
        blanket = graph_structure.get_markov_blanket('regime_state')
        assert isinstance(blanket, list)


class TestProbabilityLearner:
    """Test ProbabilityLearner functionality."""
    
    def test_learn_from_data(self, sample_data):
        """Test learning CPTs from data."""
        # Prepare data
        encoder = StateEncoder()
        encoded_df = encoder.fit_transform(sample_data)
        encoded_df = create_target_variable(encoded_df, horizon=5)
        encoded_df = create_risk_node_data(encoded_df)
        
        # Build graph
        graph_structure = GraphStructure()
        graph_structure.build_default_structure()
        
        # Learn probabilities
        learner = ProbabilityLearner(graph_structure, smoothing_alpha=1.0)
        learner.learn_from_data(encoded_df.dropna())
        
        assert len(learner.cpts) > 0
        assert 'future_return_state' in learner.cpts
    
    def test_validate_cpts(self, sample_data):
        """Test CPT validation."""
        encoder = StateEncoder()
        encoded_df = encoder.fit_transform(sample_data)
        encoded_df = create_target_variable(encoded_df, horizon=5)
        encoded_df = create_risk_node_data(encoded_df)
        
        graph_structure = GraphStructure()
        graph_structure.build_default_structure()
        
        learner = ProbabilityLearner(graph_structure)
        learner.learn_from_data(encoded_df.dropna())
        
        validation = learner.validate_cpts()
        assert isinstance(validation, dict)
        assert all(isinstance(v, bool) for v in validation.values())


class TestInferenceEngine:
    """Test InferenceEngine functionality."""
    
    @pytest.fixture
    def trained_engine(self, sample_data):
        """Create trained inference engine."""
        encoder = StateEncoder()
        encoded_df = encoder.fit_transform(sample_data)
        encoded_df = create_target_variable(encoded_df, horizon=5)
        encoded_df = create_risk_node_data(encoded_df)
        
        graph_structure = GraphStructure()
        graph_structure.build_default_structure()
        
        learner = ProbabilityLearner(graph_structure)
        learner.learn_from_data(encoded_df.dropna())
        
        engine = InferenceEngine(graph_structure, learner)
        return engine
    
    def test_query(self, trained_engine):
        """Test probabilistic query."""
        evidence = {
            'rsi_state': 'oversold',
            'momentum_score_state': 'strong',
            'regime_state': 'bull'
        }
        
        result = trained_engine.query(['future_return_state'], evidence)
        
        assert 'future_return_state' in result
        assert isinstance(result['future_return_state'], dict)
        
        # Check probabilities sum to ~1
        prob_sum = sum(result['future_return_state'].values())
        assert abs(prob_sum - 1.0) < 0.01
    
    def test_trading_signals(self, trained_engine):
        """Test trading signal generation."""
        evidence = {
            'rsi_state': 'oversold',
            'regime_state': 'bull'
        }
        
        signals = trained_engine.compute_signal_probabilities(evidence)
        
        assert 'buy' in signals
        assert 'sell' in signals
        assert 'hold' in signals
        
        # Check probabilities sum to ~1
        signal_sum = sum(signals.values())
        assert abs(signal_sum - 1.0) < 0.01


class TestExplanationEngine:
    """Test ExplanationEngine functionality."""
    
    @pytest.fixture
    def trained_explainer(self, sample_data):
        """Create trained explanation engine."""
        encoder = StateEncoder()
        encoded_df = encoder.fit_transform(sample_data)
        encoded_df = create_target_variable(encoded_df, horizon=5)
        encoded_df = create_risk_node_data(encoded_df)
        
        graph_structure = GraphStructure()
        graph_structure.build_default_structure()
        
        learner = ProbabilityLearner(graph_structure)
        learner.learn_from_data(encoded_df.dropna())
        
        engine = InferenceEngine(graph_structure, learner)
        explainer = ExplanationEngine(graph_structure, engine)
        
        return explainer, engine
    
    def test_explain_prediction(self, trained_explainer):
        """Test explanation generation."""
        explainer, engine = trained_explainer
        
        evidence = {
            'rsi_state': 'oversold',
            'momentum_score_state': 'strong'
        }
        
        result = engine.query(['future_return_state'], evidence)
        explanation = explainer.explain_prediction(
            'future_return_state',
            evidence,
            result['future_return_state']
        )
        
        assert 'prediction' in explanation
        assert 'confidence' in explanation
        assert 'key_factors' in explanation
        assert 'reasoning_chain' in explanation
        assert 'risk_assessment' in explanation
    
    def test_text_explanation(self, trained_explainer):
        """Test text explanation generation."""
        explainer, engine = trained_explainer
        
        evidence = {'rsi_state': 'oversold'}
        result = engine.query(['future_return_state'], evidence)
        explanation = explainer.explain_prediction(
            'future_return_state', evidence, result['future_return_state']
        )
        
        text = explainer.generate_text_explanation(explanation)
        assert isinstance(text, str)
        assert len(text) > 0


class TestScenarioSimulator:
    """Test ScenarioSimulator functionality."""
    
    @pytest.fixture
    def trained_simulator(self, sample_data):
        """Create trained scenario simulator."""
        encoder = StateEncoder()
        encoded_df = encoder.fit_transform(sample_data)
        encoded_df = create_target_variable(encoded_df, horizon=5)
        encoded_df = create_risk_node_data(encoded_df)
        
        graph_structure = GraphStructure()
        graph_structure.build_default_structure()
        
        learner = ProbabilityLearner(graph_structure)
        learner.learn_from_data(encoded_df.dropna())
        
        engine = InferenceEngine(graph_structure, learner)
        explainer = ExplanationEngine(graph_structure, engine)
        simulator = ScenarioSimulator(engine, explainer)
        
        return simulator
    
    def test_simulate_scenario(self, trained_simulator):
        """Test scenario simulation."""
        scenario = {
            'rsi_state': 'oversold',
            'regime_state': 'bull'
        }
        
        result = trained_simulator.simulate_scenario(
            scenario,
            ['future_return_state']
        )
        
        assert 'scenario' in result
        assert 'predictions' in result
        assert 'explanations' in result
    
    def test_sensitivity_analysis(self, trained_simulator):
        """Test sensitivity analysis."""
        base_scenario = {
            'momentum_score_state': 'strong',
            'regime_state': 'bull'
        }
        
        sensitivity_df = trained_simulator.sensitivity_analysis(
            base_scenario,
            'future_return_state',
            'rsi_state'
        )
        
        assert isinstance(sensitivity_df, pd.DataFrame)
        assert len(sensitivity_df) > 0
        assert 'rsi_state' in sensitivity_df.columns
        assert 'prediction' in sensitivity_df.columns


def test_end_to_end_workflow(sample_data):
    """Test complete end-to-end workflow."""
    # 1. Encode
    encoder = StateEncoder()
    encoded_df = encoder.fit_transform(sample_data)
    encoded_df = create_target_variable(encoded_df, horizon=5)
    encoded_df = create_risk_node_data(encoded_df)
    
    # 2. Build graph
    graph_structure = GraphStructure()
    graph_structure.build_default_structure()
    
    # 3. Learn probabilities
    learner = ProbabilityLearner(graph_structure)
    learner.learn_from_data(encoded_df.dropna())
    
    # 4. Inference
    engine = InferenceEngine(graph_structure, learner)
    evidence = {'rsi_state': 'oversold', 'regime_state': 'bull'}
    result = engine.query(['future_return_state'], evidence)
    
    # 5. Explanation
    explainer = ExplanationEngine(graph_structure, engine)
    explanation = explainer.explain_prediction(
        'future_return_state', evidence, result['future_return_state']
    )
    
    # 6. Simulation
    simulator = ScenarioSimulator(engine, explainer)
    scenario_result = simulator.simulate_scenario(evidence, ['future_return_state'])
    
    # Verify all components worked
    assert result is not None
    assert explanation is not None
    assert scenario_result is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

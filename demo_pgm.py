"""
Quick demo to visualize PGM predictions.
"""

import pandas as pd
from pgm_model.state_encoding import StateEncoder
from pgm_model.graph_structure import GraphStructure
from pgm_model.probability_learning import ProbabilityLearner
from pgm_model.inference_engine import InferenceEngine
from pgm_model.explanation_engine import ExplanationEngine
from feature_store.offline_store import OfflineFeatureStore
from utils.logger import get_logger

logger = get_logger(__name__)


def demo_pgm():
    """Quick demo of PGM predictions."""
    
    print("\n" + "="*80)
    print("PGM LAYER DEMO - Probabilistic Market Predictions")
    print("="*80)
    
    # Load data
    print("\n📊 Loading market data...")
    store = OfflineFeatureStore()
    df = store.read_features('market_features', use_latest=True)
    
    if len(df) == 0:
        print("❌ No data found. Run example_workflow.py first.")
        return
    
    print(f"✓ Loaded {len(df)} records for {df['ticker'].nunique()} tickers")
    
    # Encode features
    print("\n🔄 Encoding features to discrete states...")
    encoder = StateEncoder()
    encoded_df = encoder.fit_transform(df)
    
    # Add target
    from pgm_model.state_encoding import create_target_variable
    from pgm_model.graph_structure import create_risk_node_data
    encoded_df = create_target_variable(encoded_df, horizon=5)
    encoded_df = create_risk_node_data(encoded_df)
    encoded_df = encoded_df.dropna(subset=['future_return_state'])
    
    print(f"✓ Encoded {len([c for c in encoded_df.columns if c.endswith('_state')])} features")
    
    # Build graph
    print("\n🕸️  Building Bayesian Network...")
    graph = GraphStructure()
    graph.build_default_structure()
    print(f"✓ Network: {len(graph.graph.nodes)} nodes, {len(graph.graph.edges)} edges")
    
    # Learn probabilities
    print("\n📚 Learning probabilities from historical data...")
    learner = ProbabilityLearner(graph, smoothing_alpha=1.0)
    learner.learn_from_data(encoded_df.head(1000))  # Use subset for speed
    print(f"✓ Learned {len(learner.cpts)} conditional probability tables")
    
    # Create inference engine
    print("\n🔮 Creating inference engine...")
    engine = InferenceEngine(graph, learner)
    explainer = ExplanationEngine(graph, engine)
    print("✓ Ready for predictions")
    
    # Demo predictions for different scenarios
    print("\n" + "="*80)
    print("SCENARIO PREDICTIONS")
    print("="*80)
    
    scenarios = [
        {
            'name': '🟢 BULLISH: Oversold + Strong Momentum',
            'evidence': {
                'rsi_state': 'oversold',
                'momentum_score_state': 'strong',
                'regime_state': 'bull',
                'volatility_10_state': 'low'
            }
        },
        {
            'name': '🔴 BEARISH: Overbought + Weak Momentum',
            'evidence': {
                'rsi_state': 'overbought',
                'momentum_score_state': 'weak',
                'regime_state': 'bear',
                'volatility_10_state': 'high'
            }
        },
        {
            'name': '🟡 NEUTRAL: Mixed Signals',
            'evidence': {
                'rsi_state': 'neutral',
                'momentum_score_state': 'moderate',
                'regime_state': 'sideways',
                'volatility_10_state': 'medium'
            }
        }
    ]
    
    for scenario in scenarios:
        print(f"\n{scenario['name']}")
        print("-" * 80)
        
        # Show evidence
        print("Market Conditions:")
        for feature, state in scenario['evidence'].items():
            feature_name = feature.replace('_state', '').replace('_', ' ').title()
            print(f"  • {feature_name}: {state}")
        
        # Predict
        result = engine.query(['future_return_state'], scenario['evidence'])
        probs = result['future_return_state']
        
        # Show probabilities
        print("\nPredicted Probabilities:")
        for outcome in ['positive', 'neutral', 'negative']:
            prob = probs.get(outcome, 0.0)
            bar_length = int(prob * 40)
            bar = "█" * bar_length
            color = '🟢' if outcome == 'positive' else '🔴' if outcome == 'negative' else '🟡'
            print(f"  {color} {outcome.upper():10s} {prob:6.1%} {bar}")
        
        # Trading signal
        signals = engine.compute_signal_probabilities(scenario['evidence'])
        best_signal = max(signals, key=signals.get)
        confidence = signals[best_signal]
        
        signal_emoji = '🟢' if best_signal == 'buy' else '🔴' if best_signal == 'sell' else '🟡'
        print(f"\n  {signal_emoji} Trading Signal: {best_signal.upper()} ({confidence:.1%} confidence)")
        
        # Get explanation
        explanation = explainer.explain_prediction(
            'future_return_state',
            scenario['evidence'],
            probs
        )
        
        print(f"\n  Risk Level: {explanation['risk_assessment']['level'].upper()}")
        print(f"  Confidence: {explanation['confidence_level']}")
    
    # Show graph visualization
    print("\n" + "="*80)
    print("BAYESIAN NETWORK STRUCTURE")
    print("="*80)
    print("\n📊 Graph visualization saved to: data/analytics/pgm_graph_structure.png")
    print("\nNetwork shows how features influence predictions:")
    print("  • RSI, Momentum, MACD → Future Return")
    print("  • Volatility, ATR → Risk → Future Return")
    print("  • Trend, Momentum → Regime → Future Return")
    
    print("\n" + "="*80)
    print("✅ PGM DEMO COMPLETE")
    print("="*80)
    print("\nWhat you can do:")
    print("  1. View graph: open data/analytics/pgm_graph_structure.png")
    print("  2. Read docs: PGM_DOCUMENTATION.md")
    print("  3. Integration: PGM_INTEGRATION_GUIDE.md")
    print("  4. Full workflow: python example_pgm_workflow.py")
    print("\nTo integrate with frontend:")
    print("  • Follow PGM_INTEGRATION_GUIDE.md")
    print("  • Add API endpoints")
    print("  • Create React components")
    print("="*80 + "\n")


if __name__ == "__main__":
    try:
        demo_pgm()
    except Exception as e:
        logger.error(f"Demo failed: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        print("Make sure you've run example_workflow.py first to generate data.")

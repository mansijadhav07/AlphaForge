"""
Model Diagnosis Script

Analyzes why accuracy is low and provides specific recommendations.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
import numpy as np
from collections import Counter

from data.features.offline_store import OfflineFeatureStore
from backend.models.state_encoding import StateEncoder, create_target_variable
from utils.logger import get_logger

logger = get_logger(__name__)


def diagnose_data():
    """Diagnose data quality issues."""
    print("=" * 80)
    print("MODEL DIAGNOSIS - DATA QUALITY ANALYSIS")
    print("=" * 80)
    
    # Load data
    store = OfflineFeatureStore()
    df = store.read_features('market_features', use_latest=True)
    
    print(f"\n1. DATA SIZE")
    print(f"   Total samples: {len(df)}")
    print(f"   Tickers: {df['ticker'].nunique()}")
    print(f"   Date range: {df['date'].min()} to {df['date'].max()}")
    
    # Check for missing values
    print(f"\n2. MISSING VALUES")
    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(2)
    critical_missing = missing_pct[missing_pct > 20]
    if len(critical_missing) > 0:
        print(f"   ⚠️  Features with >20% missing:")
        for col, pct in critical_missing.items():
            print(f"      - {col}: {pct}%")
    else:
        print(f"   ✓ No critical missing values")
    
    # Check target distribution
    print(f"\n3. TARGET VARIABLE ANALYSIS")
    
    # Test different thresholds
    for threshold in [0.005, 0.01, 0.02]:
        df_temp = create_target_variable(df.copy(), horizon=5, threshold=threshold)
        dist = df_temp['future_return_state'].value_counts()
        dist_pct = (dist / dist.sum() * 100).round(1)
        
        print(f"\n   Threshold: {threshold*100}%")
        print(f"   Distribution:")
        for state, count in dist.items():
            pct = dist_pct[state]
            print(f"      {state:10s}: {count:5d} ({pct:5.1f}%)")
        
        # Check balance
        max_pct = dist_pct.max()
        min_pct = dist_pct.min()
        imbalance = max_pct / min_pct
        if imbalance > 2:
            print(f"   ⚠️  Class imbalance ratio: {imbalance:.1f}x")
        else:
            print(f"   ✓ Balanced classes")
    
    # Check feature quality
    print(f"\n4. FEATURE QUALITY")
    
    key_features = ['rsi', 'macd_diff', 'volatility_10', 'momentum_score', 
                    'return', 'volume_to_sma']
    
    for feat in key_features:
        if feat in df.columns:
            valid_pct = (df[feat].notna().sum() / len(df) * 100)
            unique_vals = df[feat].nunique()
            print(f"   {feat:20s}: {valid_pct:5.1f}% valid, {unique_vals:5d} unique values")
        else:
            print(f"   {feat:20s}: ❌ MISSING")
    
    # Check for data leakage
    print(f"\n5. DATA LEAKAGE CHECK")
    df_with_target = create_target_variable(df.copy(), horizon=5, threshold=0.02)
    
    # Check if future data is in features
    future_cols = [col for col in df.columns if 'future' in col.lower()]
    if len(future_cols) > 0:
        print(f"   ⚠️  Found {len(future_cols)} columns with 'future' in name:")
        for col in future_cols:
            print(f"      - {col}")
    else:
        print(f"   ✓ No obvious data leakage")
    
    # Check correlation with target
    print(f"\n6. FEATURE-TARGET CORRELATION")
    df_with_target['target_numeric'] = df_with_target['future_return_state'].map({
        'negative': -1, 'neutral': 0, 'positive': 1
    })
    
    correlations = []
    for feat in key_features:
        if feat in df_with_target.columns:
            corr = df_with_target[[feat, 'target_numeric']].corr().iloc[0, 1]
            correlations.append((feat, abs(corr)))
    
    correlations.sort(key=lambda x: x[1], reverse=True)
    
    print(f"   Top correlated features:")
    for feat, corr in correlations[:5]:
        print(f"      {feat:20s}: {corr:.3f}")
    
    if correlations[0][1] < 0.1:
        print(f"   ⚠️  Weak correlations - features may not be predictive")
    
    # Check discretization quality
    print(f"\n7. DISCRETIZATION ANALYSIS")
    encoder = StateEncoder()
    df_encoded = encoder.fit_transform(df_with_target.head(1000))
    
    state_cols = [col for col in df_encoded.columns if col.endswith('_state')]
    print(f"   Encoded {len(state_cols)} features")
    
    for col in state_cols[:5]:
        dist = df_encoded[col].value_counts()
        entropy = -(dist / dist.sum() * np.log2(dist / dist.sum() + 1e-10)).sum()
        print(f"   {col:30s}: {len(dist)} states, entropy={entropy:.2f}")
    
    return df


def recommend_improvements(df):
    """Provide specific recommendations."""
    print("\n" + "=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    
    recommendations = []
    
    # Check sample size
    if len(df) < 1000:
        recommendations.append({
            'priority': 'HIGH',
            'issue': 'Insufficient training data',
            'recommendation': 'Collect more historical data (need 2000+ samples)',
            'action': 'python3 -m data.ingestion.ingestion --start-date 2020-01-01'
        })
    
    # Check target distribution
    df_temp = create_target_variable(df.copy(), horizon=5, threshold=0.02)
    dist = df_temp['future_return_state'].value_counts()
    dist_pct = (dist / dist.sum() * 100)
    
    if dist_pct.max() / dist_pct.min() > 2:
        recommendations.append({
            'priority': 'HIGH',
            'issue': 'Class imbalance',
            'recommendation': 'Use smaller threshold (0.5%) or apply class weights',
            'action': 'Modify create_target_variable(threshold=0.005)'
        })
    
    # Check feature quality
    key_features = ['rsi', 'macd_diff', 'momentum_score']
    missing_features = [f for f in key_features if f not in df.columns]
    
    if len(missing_features) > 0:
        recommendations.append({
            'priority': 'CRITICAL',
            'issue': f'Missing key features: {missing_features}',
            'recommendation': 'Regenerate features with FeatureEngineer',
            'action': 'Run feature engineering pipeline'
        })
    
    # Check for weak signals
    df_temp['target_numeric'] = df_temp['future_return_state'].map({
        'negative': -1, 'neutral': 0, 'positive': 1
    })
    
    max_corr = 0
    for feat in ['rsi', 'macd_diff', 'momentum_score', 'return']:
        if feat in df_temp.columns:
            corr = abs(df_temp[[feat, 'target_numeric']].corr().iloc[0, 1])
            max_corr = max(max_corr, corr)
    
    if max_corr < 0.05:
        recommendations.append({
            'priority': 'HIGH',
            'issue': 'Weak feature-target correlation',
            'recommendation': 'Stock prediction is inherently difficult. Consider ensemble methods or different features',
            'action': 'Try longer prediction horizons or different technical indicators'
        })
    
    # Print recommendations
    for i, rec in enumerate(recommendations, 1):
        print(f"\n{i}. [{rec['priority']}] {rec['issue']}")
        print(f"   Recommendation: {rec['recommendation']}")
        print(f"   Action: {rec['action']}")
    
    if len(recommendations) == 0:
        print("\n✓ No critical issues found")
        print("\nNote: Stock prediction is inherently difficult.")
        print("35% accuracy on 3-class classification is actually reasonable.")
        print("Random guessing would give 33% accuracy.")
        print("\nTo improve further:")
        print("1. Try ensemble methods (combine multiple models)")
        print("2. Use longer prediction horizons (10-20 days)")
        print("3. Focus on high-confidence predictions only")
        print("4. Consider binary classification (up/down) instead of 3-class")


def main():
    """Main execution."""
    df = diagnose_data()
    recommend_improvements(df)
    
    print("\n" + "=" * 80)
    print("DIAGNOSIS COMPLETE")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Address HIGH priority recommendations")
    print("2. Run: python3 scripts/improve_model_accuracy.py")
    print("3. Consider realistic expectations (35-45% is good for 3-class)")
    print("=" * 80)


if __name__ == "__main__":
    main()

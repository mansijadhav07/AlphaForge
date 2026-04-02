"""
State Encoding Layer for Probabilistic Graphical Models.

Converts continuous financial features into discrete states suitable for
Bayesian Network modeling.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Union
import json
from pathlib import Path

from utils.logger import get_logger

logger = get_logger(__name__)


class StateEncoder:
    """
    Encodes continuous features into discrete states for PGM.
    
    Supports multiple encoding strategies:
    - Quantile-based binning
    - Threshold-based binning
    - Custom rule-based encoding
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize StateEncoder.
        
        Args:
            config_path: Path to encoding configuration JSON file
        """
        self.encoding_rules = self._load_default_rules()
        self.learned_thresholds = {}
        
        if config_path and Path(config_path).exists():
            self._load_config(config_path)
        
        logger.info("StateEncoder initialized")
    
    def _load_default_rules(self) -> Dict:
        """Load default encoding rules for common financial features."""
        return {
            'rsi': {
                'type': 'threshold',
                'thresholds': [30, 70],
                'labels': ['oversold', 'neutral', 'overbought'],
                'description': 'RSI momentum indicator'
            },
            'return': {
                'type': 'threshold',
                'thresholds': [-0.01, 0.01],
                'labels': ['negative', 'neutral', 'positive'],
                'description': 'Daily return'
            },
            'volatility_10': {
                'type': 'quantile',
                'n_bins': 3,
                'labels': ['low', 'medium', 'high'],
                'description': '10-day volatility'
            },
            'momentum_score': {
                'type': 'threshold',
                'thresholds': [-0.3, 0.3],
                'labels': ['weak', 'moderate', 'strong'],
                'description': 'Composite momentum score'
            },
            'regime': {
                'type': 'direct',
                'mapping': {-1: 'bear', 0: 'sideways', 1: 'bull'},
                'description': 'Market regime'
            },
            'macd_diff': {
                'type': 'threshold',
                'thresholds': [0],
                'labels': ['bearish', 'bullish'],
                'description': 'MACD histogram'
            },
            'bb_position': {
                'type': 'threshold',
                'thresholds': [0.2, 0.8],
                'labels': ['lower', 'middle', 'upper'],
                'description': 'Bollinger Band position'
            },
            'volume_to_sma': {
                'type': 'threshold',
                'thresholds': [0.8, 1.2],
                'labels': ['low', 'normal', 'high'],
                'description': 'Volume relative to average'
            },
            'atr_pct': {
                'type': 'quantile',
                'n_bins': 3,
                'labels': ['low', 'medium', 'high'],
                'description': 'Average True Range percentage'
            },
            'trend_slope_30': {
                'type': 'threshold',
                'thresholds': [-0.5, 0.5],
                'labels': ['downtrend', 'flat', 'uptrend'],
                'description': '30-day trend slope'
            }
        }
    
    def _load_config(self, config_path: str):
        """Load encoding configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Load encoding rules
            if 'encoding_rules' in config:
                self.encoding_rules.update(config['encoding_rules'])
            else:
                # Backward compatibility: if no 'encoding_rules' key, treat whole config as rules
                self.encoding_rules.update(config)
            
            # Load learned thresholds
            if 'learned_thresholds' in config:
                self.learned_thresholds.update(config['learned_thresholds'])
            
            logger.info(f"Loaded encoding config from {config_path}")
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
    
    def fit(self, df: pd.DataFrame, features: Optional[List[str]] = None):
        """
        Learn thresholds from data for quantile-based encoding.
        
        Args:
            df: DataFrame with continuous features
            features: List of features to fit (None = all configured features)
        """
        if features is None:
            features = [f for f in self.encoding_rules.keys() if f in df.columns]
        
        logger.info(f"Learning thresholds for {len(features)} features...")
        
        for feature in features:
            if feature not in df.columns:
                logger.warning(f"Feature {feature} not found in data")
                continue
            
            rule = self.encoding_rules.get(feature)
            if not rule or rule['type'] != 'quantile':
                continue
            
            # Learn quantile thresholds
            n_bins = rule.get('n_bins', 3)
            quantiles = np.linspace(0, 1, n_bins + 1)[1:-1]
            
            # Remove NaN values for quantile calculation
            valid_data = df[feature].dropna()
            if len(valid_data) == 0:
                logger.warning(f"No valid data for {feature}")
                continue
            
            thresholds = valid_data.quantile(quantiles).tolist()
            self.learned_thresholds[feature] = thresholds
            
            logger.debug(f"{feature}: learned thresholds = {thresholds}")
        
        logger.info(f"Threshold learning complete for {len(self.learned_thresholds)} features")
    
    def transform(self, df: pd.DataFrame, features: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Transform continuous features to discrete states.
        
        Args:
            df: DataFrame with continuous features
            features: List of features to encode (None = all configured features)
            
        Returns:
            DataFrame with encoded state columns (suffix: _state)
        """
        result = df.copy()
        
        if features is None:
            features = [f for f in self.encoding_rules.keys() if f in df.columns]
        
        logger.info(f"Encoding {len(features)} features to discrete states...")
        
        for feature in features:
            if feature not in df.columns:
                logger.warning(f"Feature {feature} not in DataFrame, skipping")
                continue
            
            rule = self.encoding_rules.get(feature)
            if not rule:
                logger.warning(f"No encoding rule for {feature}, skipping")
                continue
            
            state_col = f"{feature}_state"
            
            try:
                if rule['type'] == 'threshold':
                    result[state_col] = self._encode_threshold(
                        df[feature], rule['thresholds'], rule['labels']
                    )
                elif rule['type'] == 'quantile':
                    thresholds = self.learned_thresholds.get(feature, rule.get('thresholds', []))
                    result[state_col] = self._encode_threshold(
                        df[feature], thresholds, rule['labels']
                    )
                elif rule['type'] == 'direct':
                    result[state_col] = df[feature].map(rule['mapping'])
                else:
                    logger.warning(f"Unknown encoding type for {feature}: {rule['type']}")
                    continue
                
                logger.debug(f"Encoded {feature} -> {state_col}")
                
            except Exception as e:
                logger.error(f"Failed to encode {feature}: {e}")
        
        # Count encoded features
        encoded_cols = [c for c in result.columns if c.endswith('_state')]
        logger.info(f"Successfully encoded {len(encoded_cols)} features")
        
        return result
    
    def fit_transform(self, df: pd.DataFrame, features: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Fit and transform in one step.
        
        Args:
            df: DataFrame with continuous features
            features: List of features to encode
            
        Returns:
            DataFrame with encoded state columns
        """
        self.fit(df, features)
        return self.transform(df, features)
    
    def _encode_threshold(self, series: pd.Series, thresholds: List[float], 
                         labels: List[str]) -> pd.Series:
        """
        Encode series using threshold-based binning.
        
        Args:
            series: Input series
            thresholds: List of threshold values
            labels: List of labels (len = len(thresholds) + 1)
            
        Returns:
            Series with categorical labels
        """
        if len(labels) != len(thresholds) + 1:
            raise ValueError(f"Labels length ({len(labels)}) must be thresholds length + 1 ({len(thresholds) + 1})")
        
        # Create bins
        bins = [-np.inf] + thresholds + [np.inf]
        
        # Use pd.cut for binning
        result = pd.cut(series, bins=bins, labels=labels, include_lowest=True)
        
        return result.astype(str)
    
    def get_state_distribution(self, df: pd.DataFrame, feature: str) -> pd.Series:
        """
        Get distribution of states for a feature.
        
        Args:
            df: DataFrame with encoded states
            feature: Feature name (will look for {feature}_state column)
            
        Returns:
            Series with state counts
        """
        state_col = f"{feature}_state"
        if state_col not in df.columns:
            raise ValueError(f"State column {state_col} not found")
        
        return df[state_col].value_counts()
    
    def get_encoding_info(self, feature: str) -> Dict:
        """
        Get encoding information for a feature.
        
        Args:
            feature: Feature name
            
        Returns:
            Dictionary with encoding rule and learned thresholds
        """
        info = {
            'rule': self.encoding_rules.get(feature, {}),
            'learned_thresholds': self.learned_thresholds.get(feature, None)
        }
        return info
    
    def add_custom_rule(self, feature: str, rule: Dict):
        """
        Add or update a custom encoding rule.
        
        Args:
            feature: Feature name
            rule: Encoding rule dictionary
        """
        required_keys = ['type', 'labels', 'description']
        if not all(k in rule for k in required_keys):
            raise ValueError(f"Rule must contain: {required_keys}")
        
        self.encoding_rules[feature] = rule
        logger.info(f"Added custom rule for {feature}")
    
    def save_config(self, path: str):
        """
        Save encoding configuration to JSON file.
        
        Args:
            path: Output file path
        """
        config = {
            'encoding_rules': self.encoding_rules,
            'learned_thresholds': self.learned_thresholds
        }
        
        with open(path, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"Saved encoding config to {path}")
    
    def get_feature_states(self, df: pd.DataFrame) -> List[str]:
        """
        Get list of all encoded state columns in DataFrame.
        
        Args:
            df: DataFrame with encoded states
            
        Returns:
            List of state column names
        """
        return [col for col in df.columns if col.endswith('_state')]
    
    def decode_state(self, feature: str, state: str) -> str:
        """
        Get human-readable description of a state.
        
        Args:
            feature: Feature name
            state: State value
            
        Returns:
            Description string
        """
        rule = self.encoding_rules.get(feature, {})
        description = rule.get('description', feature)
        
        return f"{description}: {state}"


def create_target_variable(df: pd.DataFrame, horizon: int = 5, 
                          threshold: float = 0.02) -> pd.DataFrame:
    """
    Create target variable for future return prediction.
    
    Args:
        df: DataFrame with price data
        horizon: Number of periods ahead to predict
        threshold: Threshold for positive/negative classification
        
    Returns:
        DataFrame with future_return and future_return_state columns
    """
    result = df.copy()
    
    # Calculate future return
    result['future_return'] = result.groupby('ticker')['close'].shift(-horizon) / result['close'] - 1
    
    # Encode future return as state
    result['future_return_state'] = pd.cut(
        result['future_return'],
        bins=[-np.inf, -threshold, threshold, np.inf],
        labels=['negative', 'neutral', 'positive']
    ).astype(str)
    
    logger.info(f"Created target variable with {horizon}-period horizon")
    
    return result

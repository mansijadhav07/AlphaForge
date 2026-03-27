# Encoder Configuration Fix - Complete

## Issue
The system was showing warnings for `volatility_10` and `atr_pct` features:
```
ERROR | Failed to encode volatility_10: Labels length (3) must be thresholds length + 1 (1)
ERROR | Failed to encode atr_pct: Labels length (3) must be thresholds length + 1 (1)
```

This resulted in only 8 features being encoded instead of 10.

## Root Cause
The `StateEncoder._load_config()` method was only loading `encoding_rules` from the JSON config file, but not the `learned_thresholds`. 

For quantile-based features like `volatility_10` and `atr_pct`, the encoder needs pre-computed thresholds (2 thresholds for 3 bins). These thresholds were present in `data/pgm_model/encoder_config.json` under the `learned_thresholds` key, but weren't being loaded into the encoder instance.

## Solution
Updated `pgm_model/state_encoding.py` to properly load both `encoding_rules` and `learned_thresholds` from the config file:

```python
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
```

## Additional Fix
Also fixed a related issue in `services/data_service.py` where `get_pgm_explanation()` was receiving a Series but expecting a DataFrame. Added Series to DataFrame conversion:

```python
# Convert Series to DataFrame if needed
if isinstance(features, pd.Series):
    features = features.to_frame().T
```

## Results
- ✅ All 10 features now encode successfully
- ✅ No more encoder warnings in logs
- ✅ `volatility_10_state` and `atr_pct_state` are now included in PGM queries
- ✅ System uses full feature set for predictions

## Verification
Check the logs after server restart:
```
INFO | Encoding 10 features to discrete states...
INFO | Successfully encoded 10 features
```

And in the inference queries, you'll see both features being used:
```
'volatility_10_state': 'low'/'medium'/'high'
'atr_pct_state': 'low'/'medium'/'high'
```

## Files Modified
1. `pgm_model/state_encoding.py` - Fixed `_load_config()` method
2. `services/data_service.py` - Fixed `get_pgm_explanation()` method

## Date
March 27, 2026

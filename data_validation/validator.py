"""Data validation and cleaning logic."""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional

from config import config
from utils.logger import get_logger
from utils.helpers import ensure_dir

logger = get_logger(__name__)


class DataValidator:
    """Validate and clean financial market data."""
    
    def __init__(self):
        """Initialize data validator."""
        self.validated_data_dir = Path(config.get('storage.validated_data_dir', './data/validated'))
        ensure_dir(self.validated_data_dir)
        
        # Quality thresholds from config
        self.max_missing_pct = config.get('monitoring.quality.max_missing_pct', 0.05)
        self.max_price_change_pct = config.get('monitoring.quality.max_price_change_pct', 0.25)
        self.min_volume = config.get('monitoring.quality.min_volume', 1000)
        
        self.validation_report = {}
    
    def validate(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
        """
        Run all validation checks and cleaning.
        
        Args:
            df: Raw data DataFrame
            
        Returns:
            Tuple of (cleaned DataFrame, validation report)
        """
        logger.info("Starting data validation...")
        
        df_clean = df.copy()
        self.validation_report = {
            'original_rows': len(df),
            'checks': {}
        }
        
        # Run validation checks
        df_clean = self._check_missing_values(df_clean)
        df_clean = self._check_duplicates(df_clean)
        df_clean = self._check_data_types(df_clean)
        df_clean = self._check_price_anomalies(df_clean)
        df_clean = self._check_volume_anomalies(df_clean)
        df_clean = self._sort_data(df_clean)
        df_clean = self._check_date_gaps(df_clean)
        
        self.validation_report['final_rows'] = len(df_clean)
        self.validation_report['rows_removed'] = self.validation_report['original_rows'] - len(df_clean)
        self.validation_report['removal_pct'] = (
            self.validation_report['rows_removed'] / self.validation_report['original_rows'] * 100
        )
        
        logger.info(f"Validation complete. Removed {self.validation_report['rows_removed']} rows "
                   f"({self.validation_report['removal_pct']:.2f}%)")
        
        return df_clean, self.validation_report
    
    def _check_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Check and handle missing values."""
        logger.info("Checking missing values...")
        
        missing_counts = df.isnull().sum()
        missing_pct = (missing_counts / len(df)) * 100
        
        self.validation_report['checks']['missing_values'] = {
            'total_missing': int(missing_counts.sum()),
            'by_column': missing_counts.to_dict()
        }
        
        # Log columns with missing values
        for col, pct in missing_pct.items():
            if pct > 0:
                logger.warning(f"Column '{col}' has {pct:.2f}% missing values")
        
        # Drop rows with missing critical columns
        critical_cols = ['date', 'open', 'high', 'low', 'close', 'volume']
        before_count = len(df)
        df = df.dropna(subset=[col for col in critical_cols if col in df.columns])
        after_count = len(df)
        
        if before_count > after_count:
            logger.info(f"Removed {before_count - after_count} rows with missing critical values")
        
        return df
    
    def _check_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Check and remove duplicate records."""
        logger.info("Checking duplicates...")
        
        # Check for duplicates based on ticker and date
        if 'ticker' in df.columns and 'date' in df.columns:
            duplicates = df.duplicated(subset=['ticker', 'date'], keep='first')
            dup_count = duplicates.sum()
            
            self.validation_report['checks']['duplicates'] = {
                'count': int(dup_count)
            }
            
            if dup_count > 0:
                logger.warning(f"Found {dup_count} duplicate records. Keeping first occurrence.")
                df = df[~duplicates]
        
        return df
    
    def _check_data_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Ensure correct data types."""
        logger.info("Checking data types...")
        
        # Convert date column to datetime
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
        
        # Ensure numeric columns are float
        numeric_cols = ['open', 'high', 'low', 'close', 'volume']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        self.validation_report['checks']['data_types'] = 'passed'
        
        return df
    
    def _check_price_anomalies(self, df: pd.DataFrame) -> pd.DataFrame:
        """Check for price anomalies."""
        logger.info("Checking price anomalies...")
        
        anomalies = []
        
        # Check for negative or zero prices
        price_cols = ['open', 'high', 'low', 'close']
        for col in price_cols:
            if col in df.columns:
                invalid = (df[col] <= 0)
                if invalid.any():
                    count = invalid.sum()
                    anomalies.append(f"{col}: {count} non-positive values")
                    df = df[~invalid]
        
        # Check for extreme price changes
        if 'close' in df.columns and 'ticker' in df.columns:
            df = df.sort_values(['ticker', 'date'])
            df['price_change'] = df.groupby('ticker')['close'].pct_change()
            
            extreme_changes = (df['price_change'].abs() > self.max_price_change_pct)
            extreme_count = extreme_changes.sum()
            
            if extreme_count > 0:
                anomalies.append(f"Extreme price changes: {extreme_count}")
                logger.warning(f"Found {extreme_count} extreme price changes (>{self.max_price_change_pct*100}%)")
                # Don't remove these, just flag them
            
            df = df.drop('price_change', axis=1)
        
        # Check OHLC relationships
        if all(col in df.columns for col in ['open', 'high', 'low', 'close']):
            invalid_ohlc = (
                (df['high'] < df['low']) |
                (df['high'] < df['open']) |
                (df['high'] < df['close']) |
                (df['low'] > df['open']) |
                (df['low'] > df['close'])
            )
            
            if invalid_ohlc.any():
                count = invalid_ohlc.sum()
                anomalies.append(f"Invalid OHLC relationships: {count}")
                df = df[~invalid_ohlc]
        
        self.validation_report['checks']['price_anomalies'] = anomalies
        
        return df
    
    def _check_volume_anomalies(self, df: pd.DataFrame) -> pd.DataFrame:
        """Check for volume anomalies."""
        logger.info("Checking volume anomalies...")
        
        if 'volume' not in df.columns:
            return df
        
        # Check for negative volume
        negative_volume = (df['volume'] < 0)
        if negative_volume.any():
            count = negative_volume.sum()
            logger.warning(f"Found {count} negative volume values")
            df = df[~negative_volume]
        
        # Check for suspiciously low volume
        low_volume = (df['volume'] < self.min_volume)
        low_count = low_volume.sum()
        
        self.validation_report['checks']['volume_anomalies'] = {
            'low_volume_count': int(low_count),
            'low_volume_threshold': self.min_volume
        }
        
        if low_count > 0:
            logger.warning(f"Found {low_count} records with volume < {self.min_volume}")
        
        return df
    
    def _sort_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Sort data by ticker and date."""
        logger.info("Sorting data...")
        
        sort_cols = []
        if 'ticker' in df.columns:
            sort_cols.append('ticker')
        if 'date' in df.columns:
            sort_cols.append('date')
        
        if sort_cols:
            df = df.sort_values(sort_cols).reset_index(drop=True)
        
        return df
    
    def _check_date_gaps(self, df: pd.DataFrame) -> pd.DataFrame:
        """Check for gaps in date series."""
        logger.info("Checking date gaps...")
        
        if 'date' not in df.columns or 'ticker' not in df.columns:
            return df
        
        gaps_by_ticker = {}
        
        for ticker in df['ticker'].unique():
            ticker_df = df[df['ticker'] == ticker].copy()
            ticker_df = ticker_df.sort_values('date')
            
            # Calculate date differences
            date_diffs = ticker_df['date'].diff()
            
            # Find gaps larger than expected (e.g., > 5 days for daily data)
            large_gaps = date_diffs[date_diffs > pd.Timedelta(days=5)]
            
            if len(large_gaps) > 0:
                gaps_by_ticker[ticker] = len(large_gaps)
        
        self.validation_report['checks']['date_gaps'] = gaps_by_ticker
        
        if gaps_by_ticker:
            logger.warning(f"Found date gaps in {len(gaps_by_ticker)} tickers")
        
        return df
    
    def save_validated_data(self, df: pd.DataFrame, filename: str = "validated_data.parquet") -> None:
        """
        Save validated data to disk.
        
        Args:
            df: Validated DataFrame
            filename: Output filename
        """
        filepath = self.validated_data_dir / filename
        df.to_parquet(filepath, index=False, compression='snappy')
        logger.info(f"Validated data saved to {filepath}")
    
    def get_validation_report(self) -> Dict:
        """Get the validation report."""
        return self.validation_report


def validate_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
    """
    Convenience function to validate data.
    
    Args:
        df: Raw data DataFrame
        
    Returns:
        Tuple of (cleaned DataFrame, validation report)
    """
    validator = DataValidator()
    return validator.validate(df)

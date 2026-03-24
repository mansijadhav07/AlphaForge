"""Offline feature store using Parquet files."""

import pandas as pd
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime

from config import config
from utils.logger import get_logger
from utils.helpers import ensure_dir, get_timestamp

logger = get_logger(__name__)


class OfflineFeatureStore:
    """Manage offline feature storage using Parquet files."""
    
    def __init__(self, store_dir: Optional[str] = None):
        """
        Initialize offline feature store.
        
        Args:
            store_dir: Directory for feature storage
        """
        self.store_dir = Path(store_dir or config.get('storage.offline_store_dir', './data/features/offline'))
        ensure_dir(self.store_dir)
        
        logger.info(f"OfflineFeatureStore initialized at {self.store_dir}")
    
    def write_features(
        self,
        df: pd.DataFrame,
        feature_group: str = "default",
        partition_by: Optional[List[str]] = None,
        version: Optional[str] = None
    ) -> None:
        """
        Write features to offline store.
        
        Args:
            df: DataFrame with features
            feature_group: Feature group name
            partition_by: Columns to partition by (e.g., ['ticker'])
            version: Feature version
        """
        logger.info(f"Writing features to offline store: {feature_group}")
        
        # Create feature group directory
        version = version or config.get('versioning.current_version', 'v1')
        group_dir = self.store_dir / feature_group / version
        ensure_dir(group_dir)
        
        # Add metadata
        df = df.copy()
        df['_write_timestamp'] = datetime.now()
        df['_version'] = version
        
        if partition_by:
            # Write partitioned data
            self._write_partitioned(df, group_dir, partition_by)
        else:
            # Write single file
            timestamp = get_timestamp()
            filepath = group_dir / f"features_{timestamp}.parquet"
            df.to_parquet(filepath, index=False, compression='snappy')
            logger.info(f"Features written to {filepath}")
        
        # Write latest version
        latest_path = group_dir / "features_latest.parquet"
        df.to_parquet(latest_path, index=False, compression='snappy')
        logger.info(f"Latest features written to {latest_path}")
    
    def _write_partitioned(
        self,
        df: pd.DataFrame,
        base_dir: Path,
        partition_by: List[str]
    ) -> None:
        """Write data partitioned by specified columns."""
        # Group by partition columns
        for partition_values, group_df in df.groupby(partition_by):
            # Create partition directory
            if isinstance(partition_values, tuple):
                partition_path = "/".join([f"{col}={val}" for col, val in zip(partition_by, partition_values)])
            else:
                partition_path = f"{partition_by[0]}={partition_values}"
            
            partition_dir = base_dir / partition_path
            ensure_dir(partition_dir)
            
            # Write partition
            timestamp = get_timestamp()
            filepath = partition_dir / f"features_{timestamp}.parquet"
            group_df.to_parquet(filepath, index=False, compression='snappy')
        
        logger.info(f"Partitioned features written to {base_dir}")
    
    def read_features(
        self,
        feature_group: str = "default",
        version: Optional[str] = None,
        use_latest: bool = True,
        filters: Optional[Dict] = None
    ) -> pd.DataFrame:
        """
        Read features from offline store.
        
        Args:
            feature_group: Feature group name
            version: Feature version
            use_latest: Whether to read latest file
            filters: Dictionary of filters (e.g., {'ticker': 'AAPL'})
            
        Returns:
            DataFrame with features
        """
        version = version or config.get('versioning.current_version', 'v1')
        group_dir = self.store_dir / feature_group / version
        
        if not group_dir.exists():
            logger.warning(f"Feature group not found: {group_dir}")
            return pd.DataFrame()
        
        if use_latest:
            filepath = group_dir / "features_latest.parquet"
            if filepath.exists():
                df = pd.read_parquet(filepath)
                logger.info(f"Read {len(df)} records from {filepath}")
            else:
                logger.warning(f"Latest features not found: {filepath}")
                return pd.DataFrame()
        else:
            # Read all parquet files in directory
            parquet_files = list(group_dir.rglob("*.parquet"))
            if not parquet_files:
                logger.warning(f"No feature files found in {group_dir}")
                return pd.DataFrame()
            
            dfs = [pd.read_parquet(f) for f in parquet_files]
            df = pd.concat(dfs, ignore_index=True)
            logger.info(f"Read {len(df)} records from {len(parquet_files)} files")
        
        # Apply filters
        if filters:
            for col, value in filters.items():
                if col in df.columns:
                    df = df[df[col] == value]
            logger.info(f"Applied filters. Remaining records: {len(df)}")
        
        return df
    
    def list_feature_groups(self) -> List[str]:
        """
        List all feature groups in the store.
        
        Returns:
            List of feature group names
        """
        if not self.store_dir.exists():
            return []
        
        groups = [d.name for d in self.store_dir.iterdir() if d.is_dir()]
        return groups
    
    def list_versions(self, feature_group: str) -> List[str]:
        """
        List all versions for a feature group.
        
        Args:
            feature_group: Feature group name
            
        Returns:
            List of version names
        """
        group_dir = self.store_dir / feature_group
        if not group_dir.exists():
            return []
        
        versions = [d.name for d in group_dir.iterdir() if d.is_dir()]
        return versions
    
    def get_feature_stats(
        self,
        feature_group: str = "default",
        version: Optional[str] = None
    ) -> Dict:
        """
        Get statistics about stored features.
        
        Args:
            feature_group: Feature group name
            version: Feature version
            
        Returns:
            Dictionary with statistics
        """
        df = self.read_features(feature_group, version, use_latest=True)
        
        if df.empty:
            return {}
        
        stats = {
            'total_records': len(df),
            'date_range': {
                'start': df['date'].min() if 'date' in df.columns else None,
                'end': df['date'].max() if 'date' in df.columns else None
            },
            'tickers': df['ticker'].unique().tolist() if 'ticker' in df.columns else [],
            'num_features': len(df.columns),
            'feature_names': df.columns.tolist(),
            'last_updated': df['_write_timestamp'].max() if '_write_timestamp' in df.columns else None
        }
        
        return stats
    
    def delete_feature_group(
        self,
        feature_group: str,
        version: Optional[str] = None
    ) -> None:
        """
        Delete a feature group or version.
        
        Args:
            feature_group: Feature group name
            version: Feature version (if None, deletes entire group)
        """
        if version:
            group_dir = self.store_dir / feature_group / version
        else:
            group_dir = self.store_dir / feature_group
        
        if group_dir.exists():
            import shutil
            shutil.rmtree(group_dir)
            logger.info(f"Deleted feature group: {group_dir}")
        else:
            logger.warning(f"Feature group not found: {group_dir}")

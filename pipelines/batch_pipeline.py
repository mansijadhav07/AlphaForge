"""Batch pipeline for historical data processing."""

import pandas as pd
from typing import List, Optional
from datetime import datetime

from config import config
from utils.logger import get_logger, setup_logging
from data_ingestion import DataIngestion
from data_validation import DataValidator
from feature_engineering import FeatureEngineer
from feature_store import OfflineFeatureStore, OnlineFeatureStore

logger = get_logger(__name__)


class BatchPipeline:
    """Orchestrate batch processing pipeline."""
    
    def __init__(
        self,
        tickers: Optional[List[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ):
        """
        Initialize batch pipeline.
        
        Args:
            tickers: List of stock tickers
            start_date: Start date for data
            end_date: End date for data
        """
        self.tickers = tickers or config.get('data.tickers')
        self.start_date = start_date or config.get('data.start_date')
        self.end_date = end_date or config.get('data.end_date')
        
        # Initialize components
        self.ingestion = DataIngestion(
            tickers=self.tickers,
            start_date=self.start_date,
            end_date=self.end_date
        )
        self.validator = DataValidator()
        self.feature_engineer = FeatureEngineer()
        self.offline_store = OfflineFeatureStore()
        self.online_store = OnlineFeatureStore()
        
        logger.info("BatchPipeline initialized")
    
    def run_full_pipeline(self) -> pd.DataFrame:
        """
        Run complete pipeline: ingest -> validate -> engineer -> store.
        
        Returns:
            DataFrame with final features
        """
        logger.info("=" * 80)
        logger.info("Starting FULL BATCH PIPELINE")
        logger.info("=" * 80)
        
        start_time = datetime.now()
        
        try:
            # Step 1: Data Ingestion
            logger.info("\n[STEP 1/5] Data Ingestion")
            logger.info("-" * 80)
            raw_data = self.ingestion.fetch_multiple_tickers(self.tickers)
            
            if raw_data.empty:
                logger.error("No data ingested. Pipeline aborted.")
                return pd.DataFrame()
            
            logger.info(f"✓ Ingested {len(raw_data)} records for {len(self.tickers)} tickers")
            
            # Step 2: Data Validation
            logger.info("\n[STEP 2/5] Data Validation")
            logger.info("-" * 80)
            validated_data, validation_report = self.validator.validate(raw_data)
            
            logger.info(f"✓ Validation complete. {len(validated_data)} records passed")
            
            # Save validated data
            self.validator.save_validated_data(validated_data)
            
            # Step 3: Feature Engineering
            logger.info("\n[STEP 3/5] Feature Engineering")
            logger.info("-" * 80)
            features_df = self.feature_engineer.compute_all_features(validated_data)
            
            logger.info(f"✓ Computed {len(features_df.columns)} features")
            
            # Step 4: Store in Offline Store
            logger.info("\n[STEP 4/5] Offline Feature Store")
            logger.info("-" * 80)
            self.offline_store.write_features(
                features_df,
                feature_group="market_features",
                partition_by=['ticker']
            )
            
            logger.info("✓ Features written to offline store")
            
            # Step 5: Update Online Store
            logger.info("\n[STEP 5/5] Online Feature Store")
            logger.info("-" * 80)
            
            if self.online_store.is_connected():
                count = self.online_store.write_batch(features_df)
                logger.info(f"✓ Updated {count} tickers in online store")
            else:
                logger.warning("⚠ Online store not available (Redis not connected)")
            
            # Pipeline Summary
            duration = (datetime.now() - start_time).total_seconds()
            
            logger.info("\n" + "=" * 80)
            logger.info("PIPELINE COMPLETED SUCCESSFULLY")
            logger.info("=" * 80)
            logger.info(f"Duration: {duration:.2f} seconds")
            logger.info(f"Records processed: {len(features_df)}")
            logger.info(f"Tickers: {', '.join(self.tickers)}")
            logger.info(f"Features: {len(features_df.columns)}")
            logger.info("=" * 80)
            
            return features_df
            
        except Exception as e:
            logger.error(f"Pipeline failed: {str(e)}", exc_info=True)
            return pd.DataFrame()
    
    def run_incremental_update(self, lookback_days: int = 5) -> pd.DataFrame:
        """
        Run incremental update for recent data.
        
        Args:
            lookback_days: Number of days to look back
            
        Returns:
            DataFrame with updated features
        """
        logger.info("Starting INCREMENTAL UPDATE")
        logger.info(f"Lookback: {lookback_days} days")
        
        all_features = []
        
        for ticker in self.tickers:
            # Fetch latest data
            latest_data = self.ingestion.fetch_latest(ticker, lookback_days)
            
            if latest_data is None or latest_data.empty:
                logger.warning(f"No new data for {ticker}")
                continue
            
            # Validate
            validated_data, _ = self.validator.validate(latest_data)
            
            # Compute features
            features = self.feature_engineer.compute_all_features(validated_data)
            
            all_features.append(features)
        
        if not all_features:
            logger.warning("No features computed in incremental update")
            return pd.DataFrame()
        
        # Combine all features
        combined_features = pd.concat(all_features, ignore_index=True)
        
        # Update stores
        self.offline_store.write_features(
            combined_features,
            feature_group="market_features",
            partition_by=['ticker']
        )
        
        if self.online_store.is_connected():
            self.online_store.write_batch(combined_features)
        
        logger.info(f"Incremental update complete. Updated {len(combined_features)} records")
        
        return combined_features
    
    def get_pipeline_stats(self) -> dict:
        """
        Get statistics about the pipeline and stored features.
        
        Returns:
            Dictionary with pipeline statistics
        """
        stats = {
            'tickers': self.tickers,
            'date_range': {
                'start': self.start_date,
                'end': self.end_date
            },
            'offline_store': self.offline_store.get_feature_stats('market_features'),
            'online_store': self.online_store.get_stats()
        }
        
        return stats


def main():
    """Main entry point for batch pipeline."""
    import argparse
    
    # Setup logging
    setup_logging()
    
    parser = argparse.ArgumentParser(description='Run batch feature pipeline')
    parser.add_argument('--mode', choices=['full', 'incremental'], default='full',
                       help='Pipeline mode')
    parser.add_argument('--tickers', type=str, help='Comma-separated list of tickers')
    parser.add_argument('--start-date', type=str, help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str, help='End date (YYYY-MM-DD)')
    parser.add_argument('--lookback-days', type=int, default=5,
                       help='Lookback days for incremental mode')
    
    args = parser.parse_args()
    
    # Parse tickers
    tickers = None
    if args.tickers:
        tickers = [t.strip() for t in args.tickers.split(',')]
    
    # Initialize pipeline
    pipeline = BatchPipeline(
        tickers=tickers,
        start_date=args.start_date,
        end_date=args.end_date
    )
    
    # Run pipeline
    if args.mode == 'full':
        pipeline.run_full_pipeline()
    else:
        pipeline.run_incremental_update(args.lookback_days)


if __name__ == '__main__':
    main()

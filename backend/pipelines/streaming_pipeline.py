"""Streaming pipeline for real-time simulation."""

import time
import pandas as pd
from typing import List, Optional
from datetime import datetime

from config import config
from utils.logger import get_logger, setup_logging
from data.ingestion import DataIngestion
from data.validation import DataValidator
from backend.models import FeatureEngineer
from data.features import OnlineFeatureStore

logger = get_logger(__name__)


class StreamingPipeline:
    """Simulate real-time streaming data processing."""
    
    def __init__(
        self,
        tickers: Optional[List[str]] = None,
        update_interval: int = 60,
        lookback_days: int = 90
    ):
        """
        Initialize streaming pipeline.
        
        Args:
            tickers: List of stock tickers
            update_interval: Update interval in seconds
            lookback_days: Days of historical data for feature calculation
        """
        self.tickers = tickers or config.get('data.tickers')
        self.update_interval = update_interval or config.get('pipeline.streaming.update_interval', 60)
        self.lookback_days = lookback_days or config.get('pipeline.streaming.lookback_days', 90)
        
        # Initialize components
        self.ingestion = DataIngestion(tickers=self.tickers)
        self.validator = DataValidator()
        self.feature_engineer = FeatureEngineer()
        self.online_store = OnlineFeatureStore()
        
        self.is_running = False
        self.iteration_count = 0
        
        logger.info("StreamingPipeline initialized")
        logger.info(f"Update interval: {self.update_interval}s")
        logger.info(f"Lookback: {self.lookback_days} days")
    
    def start(self, max_iterations: Optional[int] = None) -> None:
        """
        Start streaming pipeline.
        
        Args:
            max_iterations: Maximum iterations (None = infinite)
        """
        logger.info("=" * 80)
        logger.info("STARTING STREAMING PIPELINE")
        logger.info("=" * 80)
        
        if not self.online_store.is_connected():
            logger.error("Online store not available. Cannot start streaming pipeline.")
            return
        
        self.is_running = True
        
        try:
            while self.is_running:
                iteration_start = datetime.now()
                
                logger.info(f"\n[Iteration {self.iteration_count + 1}] {iteration_start}")
                logger.info("-" * 80)
                
                # Process each ticker
                for ticker in self.tickers:
                    try:
                        self._process_ticker(ticker)
                    except Exception as e:
                        logger.error(f"Error processing {ticker}: {e}")
                
                self.iteration_count += 1
                
                # Check if max iterations reached
                if max_iterations and self.iteration_count >= max_iterations:
                    logger.info(f"Reached max iterations ({max_iterations}). Stopping.")
                    break
                
                # Calculate sleep time
                elapsed = (datetime.now() - iteration_start).total_seconds()
                sleep_time = max(0, self.update_interval - elapsed)
                
                logger.info(f"Iteration complete. Sleeping for {sleep_time:.1f}s...")
                time.sleep(sleep_time)
                
        except KeyboardInterrupt:
            logger.info("\nReceived interrupt signal. Stopping pipeline...")
        finally:
            self.stop()
    
    def stop(self) -> None:
        """Stop streaming pipeline."""
        self.is_running = False
        logger.info("=" * 80)
        logger.info("STREAMING PIPELINE STOPPED")
        logger.info(f"Total iterations: {self.iteration_count}")
        logger.info("=" * 80)
    
    def _process_ticker(self, ticker: str) -> None:
        """
        Process a single ticker update.
        
        Args:
            ticker: Stock ticker symbol
        """
        try:
            # Fetch latest data with lookback for feature calculation
            data = self.ingestion.fetch_latest(ticker, lookback_days=self.lookback_days)
            
            if data is None or data.empty:
                logger.warning(f"No data for {ticker}")
                return
            
            # Validate
            validated_data, _ = self.validator.validate(data)
            
            if validated_data.empty:
                logger.warning(f"No valid data for {ticker}")
                return
            
            # Compute features
            features_df = self.feature_engineer.compute_all_features(validated_data)
            
            # Get latest record
            latest_features = features_df.iloc[-1].to_dict()
            
            # Write to online store
            success = self.online_store.write_features(
                ticker=ticker,
                features=latest_features,
                timestamp=latest_features.get('date')
            )
            
            if success:
                logger.info(f"✓ {ticker}: Updated features (close=${latest_features.get('close', 0):.2f})")
            else:
                logger.warning(f"✗ {ticker}: Failed to update features")
                
        except Exception as e:
            logger.error(f"Error processing {ticker}: {e}")
    
    def get_latest_features(self, ticker: str) -> Optional[dict]:
        """
        Get latest features for a ticker.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with latest features
        """
        return self.online_store.read_features(ticker)
    
    def get_all_latest_features(self) -> pd.DataFrame:
        """
        Get latest features for all tickers.
        
        Returns:
            DataFrame with latest features
        """
        return self.online_store.read_batch(self.tickers)


def main():
    """Main entry point for streaming pipeline."""
    import argparse
    
    # Setup logging
    setup_logging()
    
    parser = argparse.ArgumentParser(description='Run streaming feature pipeline')
    parser.add_argument('--tickers', type=str, help='Comma-separated list of tickers')
    parser.add_argument('--interval', type=int, default=60,
                       help='Update interval in seconds')
    parser.add_argument('--lookback', type=int, default=90,
                       help='Lookback days for feature calculation')
    parser.add_argument('--max-iterations', type=int, default=None,
                       help='Maximum iterations (default: infinite)')
    
    args = parser.parse_args()
    
    # Parse tickers
    tickers = None
    if args.tickers:
        tickers = [t.strip() for t in args.tickers.split(',')]
    
    # Initialize pipeline
    pipeline = StreamingPipeline(
        tickers=tickers,
        update_interval=args.interval,
        lookback_days=args.lookback
    )
    
    # Start streaming
    pipeline.start(max_iterations=args.max_iterations)


if __name__ == '__main__':
    main()

"""Stock market data ingestion using yfinance."""

import yfinance as yf
import pandas as pd
from pathlib import Path
from typing import List, Optional, Union
from datetime import datetime, timedelta

from config import config
from utils.logger import get_logger
from utils.helpers import ensure_dir, get_timestamp

logger = get_logger(__name__)


class DataIngestion:
    """Handle stock market data ingestion from yfinance."""
    
    def __init__(
        self,
        tickers: Optional[List[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        interval: str = "1d"
    ):
        """
        Initialize data ingestion.
        
        Args:
            tickers: List of stock tickers
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            interval: Data interval (1d, 1h, 5m, etc.)
        """
        self.tickers = tickers or config.get('data.tickers', ['AAPL'])
        self.start_date = start_date or config.get('data.start_date', '2020-01-01')
        self.end_date = end_date or config.get('data.end_date', datetime.now().strftime('%Y-%m-%d'))
        self.interval = interval or config.get('data.interval', '1d')
        
        self.raw_data_dir = Path(config.get('storage.raw_data_dir', './data/raw'))
        ensure_dir(self.raw_data_dir)
        
        logger.info(f"DataIngestion initialized for tickers: {self.tickers}")
        logger.info(f"Date range: {self.start_date} to {self.end_date}")
    
    def fetch_single_ticker(
        self,
        ticker: str,
        save: bool = True
    ) -> Optional[pd.DataFrame]:
        """
        Fetch data for a single ticker.
        
        Args:
            ticker: Stock ticker symbol
            save: Whether to save data to disk
            
        Returns:
            DataFrame with OHLCV data
        """
        try:
            logger.info(f"Fetching data for {ticker}...")
            
            # Download data from yfinance
            stock = yf.Ticker(ticker)
            df = stock.history(
                start=self.start_date,
                end=self.end_date,
                interval=self.interval
            )
            
            if df.empty:
                logger.warning(f"No data retrieved for {ticker}")
                return None
            
            # Reset index to make Date a column
            df.reset_index(inplace=True)
            
            # Rename columns to standard format
            df.columns = [col.lower().replace(' ', '_') for col in df.columns]
            
            # Add ticker column
            df['ticker'] = ticker
            
            # Add ingestion timestamp
            df['ingestion_timestamp'] = datetime.now()
            
            # Reorder columns
            cols = ['ticker', 'date'] + [col for col in df.columns if col not in ['ticker', 'date']]
            df = df[cols]
            
            logger.info(f"Retrieved {len(df)} records for {ticker}")
            
            # Save to parquet
            if save:
                self._save_data(df, ticker)
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching data for {ticker}: {str(e)}")
            return None
    
    def fetch_multiple_tickers(
        self,
        tickers: Optional[List[str]] = None,
        save: bool = True
    ) -> pd.DataFrame:
        """
        Fetch data for multiple tickers.
        
        Args:
            tickers: List of ticker symbols
            save: Whether to save data to disk
            
        Returns:
            Combined DataFrame with all tickers
        """
        tickers = tickers or self.tickers
        all_data = []
        
        logger.info(f"Fetching data for {len(tickers)} tickers...")
        
        for ticker in tickers:
            df = self.fetch_single_ticker(ticker, save=save)
            if df is not None:
                all_data.append(df)
        
        if not all_data:
            logger.error("No data retrieved for any ticker")
            return pd.DataFrame()
        
        # Combine all data
        combined_df = pd.concat(all_data, ignore_index=True)
        logger.info(f"Total records retrieved: {len(combined_df)}")
        
        return combined_df
    
    def fetch_latest(
        self,
        ticker: str,
        lookback_days: int = 1
    ) -> Optional[pd.DataFrame]:
        """
        Fetch latest data for streaming simulation.
        
        Args:
            ticker: Stock ticker symbol
            lookback_days: Number of days to look back
            
        Returns:
            DataFrame with latest data
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=lookback_days + 5)  # Extra buffer
        
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(
                start=start_date.strftime('%Y-%m-%d'),
                end=end_date.strftime('%Y-%m-%d'),
                interval=self.interval
            )
            
            if df.empty:
                return None
            
            df.reset_index(inplace=True)
            df.columns = [col.lower().replace(' ', '_') for col in df.columns]
            df['ticker'] = ticker
            df['ingestion_timestamp'] = datetime.now()
            
            # Get only the latest records
            df = df.tail(lookback_days)
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching latest data for {ticker}: {str(e)}")
            return None
    
    def _save_data(self, df: pd.DataFrame, ticker: str) -> None:
        """
        Save data to parquet file.
        
        Args:
            df: DataFrame to save
            ticker: Ticker symbol for filename
        """
        timestamp = get_timestamp()
        filename = f"{ticker}_{timestamp}.parquet"
        filepath = self.raw_data_dir / filename
        
        df.to_parquet(filepath, index=False, compression='snappy')
        logger.info(f"Data saved to {filepath}")
        
        # Also save as latest
        latest_filepath = self.raw_data_dir / f"{ticker}_latest.parquet"
        df.to_parquet(latest_filepath, index=False, compression='snappy')
    
    def load_data(self, ticker: str, use_latest: bool = True) -> Optional[pd.DataFrame]:
        """
        Load previously saved data.
        
        Args:
            ticker: Stock ticker symbol
            use_latest: Whether to load latest file
            
        Returns:
            DataFrame with loaded data
        """
        if use_latest:
            filepath = self.raw_data_dir / f"{ticker}_latest.parquet"
        else:
            # Find most recent file for ticker
            files = list(self.raw_data_dir.glob(f"{ticker}_*.parquet"))
            if not files:
                logger.warning(f"No data files found for {ticker}")
                return None
            filepath = max(files, key=lambda p: p.stat().st_mtime)
        
        if not filepath.exists():
            logger.warning(f"Data file not found: {filepath}")
            return None
        
        df = pd.read_parquet(filepath)
        logger.info(f"Loaded {len(df)} records from {filepath}")
        return df


def fetch_stock_data(
    tickers: Union[str, List[str]],
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    interval: str = "1d"
) -> pd.DataFrame:
    """
    Convenience function to fetch stock data.
    
    Args:
        tickers: Single ticker or list of tickers
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        interval: Data interval
        
    Returns:
        DataFrame with stock data
    """
    if isinstance(tickers, str):
        tickers = [tickers]
    
    ingestion = DataIngestion(
        tickers=tickers,
        start_date=start_date,
        end_date=end_date,
        interval=interval
    )
    
    return ingestion.fetch_multiple_tickers()

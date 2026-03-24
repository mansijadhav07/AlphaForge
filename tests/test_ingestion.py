"""Tests for data ingestion module."""

import pytest
import pandas as pd
from datetime import datetime, timedelta

from data_ingestion import DataIngestion


class TestDataIngestion:
    """Test data ingestion functionality."""
    
    def test_initialization(self):
        """Test DataIngestion initialization."""
        ingestion = DataIngestion(
            tickers=['AAPL'],
            start_date='2023-01-01',
            end_date='2023-12-31'
        )
        
        assert ingestion.tickers == ['AAPL']
        assert ingestion.start_date == '2023-01-01'
        assert ingestion.end_date == '2023-12-31'
    
    def test_fetch_single_ticker(self):
        """Test fetching data for a single ticker."""
        ingestion = DataIngestion(
            tickers=['AAPL'],
            start_date='2023-01-01',
            end_date='2023-01-31'
        )
        
        df = ingestion.fetch_single_ticker('AAPL', save=False)
        
        assert df is not None
        assert not df.empty
        assert 'ticker' in df.columns
        assert 'date' in df.columns
        assert 'close' in df.columns
        assert df['ticker'].iloc[0] == 'AAPL'
    
    def test_invalid_ticker(self):
        """Test handling of invalid ticker."""
        ingestion = DataIngestion(
            tickers=['INVALID_TICKER_XYZ'],
            start_date='2023-01-01',
            end_date='2023-01-31'
        )
        
        df = ingestion.fetch_single_ticker('INVALID_TICKER_XYZ', save=False)
        
        # Should return None or empty DataFrame
        assert df is None or df.empty

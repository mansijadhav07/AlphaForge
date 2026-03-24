"""Data ingestion module for fetching financial market data."""

from .ingestion import DataIngestion, fetch_stock_data

__all__ = ['DataIngestion', 'fetch_stock_data']

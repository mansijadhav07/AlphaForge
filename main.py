"""Main entry point for the Financial Feature Store platform."""

import argparse
import sys
from pathlib import Path

from config import config
from utils.logger import setup_logging, get_logger
from pipelines import BatchPipeline, StreamingPipeline
from analytics import FeatureAnalyzer
from feature_store import OfflineFeatureStore, OnlineFeatureStore

# Setup logging
setup_logging()
logger = get_logger(__name__)


def run_batch_pipeline(args):
    """Run batch pipeline."""
    logger.info("Starting batch pipeline...")
    
    tickers = None
    if args.tickers:
        tickers = [t.strip() for t in args.tickers.split(',')]
    
    pipeline = BatchPipeline(
        tickers=tickers,
        start_date=args.start_date,
        end_date=args.end_date
    )
    
    if args.mode == 'full':
        pipeline.run_full_pipeline()
    elif args.mode == 'incremental':
        pipeline.run_incremental_update(args.lookback_days)
    
    logger.info("Batch pipeline completed")


def run_streaming_pipeline(args):
    """Run streaming pipeline."""
    logger.info("Starting streaming pipeline...")
    
    tickers = None
    if args.tickers:
        tickers = [t.strip() for t in args.tickers.split(',')]
    
    pipeline = StreamingPipeline(
        tickers=tickers,
        update_interval=args.interval,
        lookback_days=args.lookback
    )
    
    pipeline.start(max_iterations=args.max_iterations)
    
    logger.info("Streaming pipeline completed")


def run_analytics(args):
    """Run analytics."""
    logger.info("Running analytics...")
    
    # Load features
    store = OfflineFeatureStore()
    df = store.read_features('market_features')
    
    if df.empty:
        logger.error("No features found. Run batch pipeline first.")
        return
    
    # Filter by ticker if specified
    if args.ticker:
        df = df[df['ticker'] == args.ticker]
    
    # Initialize analyzer
    analyzer = FeatureAnalyzer()
    
    # Generate report
    report = analyzer.generate_report(df, ticker=args.ticker)
    print(report)
    
    # Generate plots
    if args.plots:
        logger.info("Generating plots...")
        
        # Feature importance
        analyzer.plot_feature_importance(df, save=True)
        
        # Correlation heatmap
        analyzer.plot_correlation_heatmap(df, save=True)
        
        # Feature trends
        if args.ticker:
            key_features = ['close', 'rsi', 'macd', 'volatility_10']
            available_features = [f for f in key_features if f in df.columns]
            if available_features:
                analyzer.plot_feature_trends(df, available_features, ticker=args.ticker, save=True)
        
        logger.info("Plots saved to ./data/analytics/")
    
    logger.info("Analytics completed")


def run_dashboard(args):
    """Run Streamlit dashboard."""
    logger.info("Starting dashboard...")
    
    import subprocess
    
    dashboard_path = Path(__file__).parent / "dashboard" / "app.py"
    
    cmd = ["streamlit", "run", str(dashboard_path)]
    
    if args.port:
        cmd.extend(["--server.port", str(args.port)])
    
    subprocess.run(cmd)


def show_status(args):
    """Show system status."""
    print("=" * 80)
    print("FINANCIAL FEATURE STORE - SYSTEM STATUS")
    print("=" * 80)
    
    # Offline store
    print("\n📦 OFFLINE FEATURE STORE")
    print("-" * 80)
    offline_store = OfflineFeatureStore()
    feature_groups = offline_store.list_feature_groups()
    
    if feature_groups:
        for group in feature_groups:
            stats = offline_store.get_feature_stats(group)
            print(f"\nFeature Group: {group}")
            print(f"  Records: {stats.get('total_records', 0):,}")
            print(f"  Features: {stats.get('num_features', 0)}")
            print(f"  Tickers: {', '.join(stats.get('tickers', []))}")
            print(f"  Date Range: {stats.get('date_range', {}).get('start')} to {stats.get('date_range', {}).get('end')}")
    else:
        print("  No feature groups found")
    
    # Online store
    print("\n\n🔴 ONLINE FEATURE STORE (Redis)")
    print("-" * 80)
    online_store = OnlineFeatureStore()
    
    if online_store.is_connected():
        print("  Status: ✅ Connected")
        stats = online_store.get_stats()
        print(f"  Host: {stats.get('host')}:{stats.get('port')}")
        print(f"  Active Tickers: {stats.get('num_tickers', 0)}")
        print(f"  Tickers: {', '.join(stats.get('tickers', []))}")
        print(f"  Memory Used: {stats.get('used_memory_human', 'N/A')}")
    else:
        print("  Status: ❌ Not Connected")
    
    # Configuration
    print("\n\n⚙️  CONFIGURATION")
    print("-" * 80)
    print(f"  Tickers: {', '.join(config.get('data.tickers', []))}")
    print(f"  Date Range: {config.get('data.start_date')} to {config.get('data.end_date')}")
    print(f"  Data Directory: {config.get('storage.data_dir')}")
    
    print("\n" + "=" * 80)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Real-Time Financial Feature Store & Analytics Platform',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Batch pipeline
    batch_parser = subparsers.add_parser('batch', help='Run batch pipeline')
    batch_parser.add_argument('--mode', choices=['full', 'incremental'], default='full',
                             help='Pipeline mode')
    batch_parser.add_argument('--tickers', type=str, help='Comma-separated list of tickers')
    batch_parser.add_argument('--start-date', type=str, help='Start date (YYYY-MM-DD)')
    batch_parser.add_argument('--end-date', type=str, help='End date (YYYY-MM-DD)')
    batch_parser.add_argument('--lookback-days', type=int, default=5,
                             help='Lookback days for incremental mode')
    
    # Streaming pipeline
    stream_parser = subparsers.add_parser('stream', help='Run streaming pipeline')
    stream_parser.add_argument('--tickers', type=str, help='Comma-separated list of tickers')
    stream_parser.add_argument('--interval', type=int, default=60,
                              help='Update interval in seconds')
    stream_parser.add_argument('--lookback', type=int, default=90,
                              help='Lookback days for feature calculation')
    stream_parser.add_argument('--max-iterations', type=int, default=None,
                              help='Maximum iterations (default: infinite)')
    
    # Analytics
    analytics_parser = subparsers.add_parser('analytics', help='Run analytics')
    analytics_parser.add_argument('--ticker', type=str, help='Specific ticker to analyze')
    analytics_parser.add_argument('--plots', action='store_true', help='Generate plots')
    
    # Dashboard
    dashboard_parser = subparsers.add_parser('dashboard', help='Launch dashboard')
    dashboard_parser.add_argument('--port', type=int, default=8501, help='Dashboard port')
    
    # Status
    subparsers.add_parser('status', help='Show system status')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'batch':
            run_batch_pipeline(args)
        elif args.command == 'stream':
            run_streaming_pipeline(args)
        elif args.command == 'analytics':
            run_analytics(args)
        elif args.command == 'dashboard':
            run_dashboard(args)
        elif args.command == 'status':
            show_status(args)
    except KeyboardInterrupt:
        logger.info("\nOperation cancelled by user")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()

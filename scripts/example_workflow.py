"""
Example workflow demonstrating the complete feature store pipeline.

This script shows how to:
1. Ingest data
2. Validate and clean
3. Engineer features
4. Store in offline/online stores
5. Run analytics
6. Backtest strategies
"""

from datetime import datetime, timedelta

from config import config
from utils.logger import setup_logging, get_logger
from data_ingestion import DataIngestion
from data_validation import DataValidator
from feature_engineering import FeatureEngineer
from feature_store import OfflineFeatureStore, OnlineFeatureStore
from analytics import FeatureAnalyzer
from backtesting import BacktestEngine, RSIStrategy, MACDStrategy

# Setup
setup_logging()
logger = get_logger(__name__)


def main():
    """Run complete workflow example."""
    
    print("=" * 80)
    print("FINANCIAL FEATURE STORE - EXAMPLE WORKFLOW")
    print("=" * 80)
    
    # Configuration
    tickers = ['AAPL', 'TSLA']
    start_date = '2023-01-01'
    end_date = datetime.now().strftime('%Y-%m-%d')
    
    print(f"\nTickers: {', '.join(tickers)}")
    print(f"Date Range: {start_date} to {end_date}")
    print()
    
    # =========================================================================
    # STEP 1: DATA INGESTION
    # =========================================================================
    print("\n" + "=" * 80)
    print("STEP 1: DATA INGESTION")
    print("=" * 80)
    
    ingestion = DataIngestion(
        tickers=tickers,
        start_date=start_date,
        end_date=end_date
    )
    
    raw_data = ingestion.fetch_multiple_tickers()
    print(f"\n✓ Ingested {len(raw_data)} records")
    print(f"  Columns: {', '.join(raw_data.columns[:8])}...")
    
    # =========================================================================
    # STEP 2: DATA VALIDATION
    # =========================================================================
    print("\n" + "=" * 80)
    print("STEP 2: DATA VALIDATION")
    print("=" * 80)
    
    validator = DataValidator()
    validated_data, validation_report = validator.validate(raw_data)
    
    print(f"\n✓ Validation complete")
    print(f"  Original records: {validation_report['original_rows']}")
    print(f"  Valid records: {validation_report['final_rows']}")
    print(f"  Removed: {validation_report['rows_removed']} ({validation_report['removal_pct']:.2f}%)")
    
    # =========================================================================
    # STEP 3: FEATURE ENGINEERING
    # =========================================================================
    print("\n" + "=" * 80)
    print("STEP 3: FEATURE ENGINEERING")
    print("=" * 80)
    
    engineer = FeatureEngineer()
    features_df = engineer.compute_all_features(validated_data)
    
    print(f"\n✓ Computed {len(features_df.columns)} features")
    
    # Show sample features
    feature_cols = [col for col in features_df.columns 
                   if not col.startswith('_') and col not in ['ticker', 'date']]
    print(f"  Sample features: {', '.join(feature_cols[:10])}...")
    
    # =========================================================================
    # STEP 4: FEATURE STORAGE
    # =========================================================================
    print("\n" + "=" * 80)
    print("STEP 4: FEATURE STORAGE")
    print("=" * 80)
    
    # Offline store
    print("\n📦 Offline Feature Store (Parquet)")
    offline_store = OfflineFeatureStore()
    offline_store.write_features(
        features_df,
        feature_group="example_features",
        partition_by=['ticker']
    )
    print("✓ Features written to offline store")
    
    # Online store
    print("\n🔴 Online Feature Store (Redis)")
    online_store = OnlineFeatureStore()
    
    if online_store.is_connected():
        count = online_store.write_batch(features_df)
        print(f"✓ Updated {count} tickers in online store")
        
        # Retrieve latest features
        latest = online_store.read_features('AAPL')
        if latest:
            print(f"\nLatest AAPL features:")
            print(f"  Close: ${latest.get('close', 0):.2f}")
            print(f"  RSI: {latest.get('rsi', 0):.2f}")
            print(f"  MACD: {latest.get('macd', 0):.4f}")
    else:
        print("⚠ Redis not available - skipping online store")
    
    # =========================================================================
    # STEP 5: ANALYTICS
    # =========================================================================
    print("\n" + "=" * 80)
    print("STEP 5: ANALYTICS")
    print("=" * 80)
    
    analyzer = FeatureAnalyzer()
    
    # Analyze AAPL
    aapl_data = features_df[features_df['ticker'] == 'AAPL'].copy()
    
    print("\n📊 Feature Analysis for AAPL")
    analysis = analyzer.analyze_features(aapl_data)
    
    if not analysis['feature_importance'].empty:
        print("\nTop 5 Features by Importance:")
        top_features = analysis['feature_importance'].head(5)
        for idx, row in top_features.iterrows():
            print(f"  {row['feature']}: {row['importance']:.4f} (corr: {row['correlation']:.4f})")
    
    # Generate plots
    print("\n📈 Generating plots...")
    analyzer.plot_feature_importance(aapl_data, save=True)
    analyzer.plot_correlation_heatmap(aapl_data, save=True)
    print("✓ Plots saved to ./data/analytics/")
    
    # =========================================================================
    # STEP 6: BACKTESTING
    # =========================================================================
    print("\n" + "=" * 80)
    print("STEP 6: BACKTESTING")
    print("=" * 80)
    
    # Initialize backtest engine
    engine = BacktestEngine(
        initial_capital=100000,
        commission=0.001,
        slippage=0.0005
    )
    
    # Test RSI strategy
    print("\n🎯 Testing RSI Strategy on AAPL")
    rsi_strategy = RSIStrategy(buy_threshold=30, sell_threshold=70)
    rsi_result = engine.run_backtest(aapl_data, rsi_strategy, position_size=0.1)
    
    print(f"\nRSI Strategy Results:")
    print(f"  Total Return: {rsi_result['metrics']['total_return']:.2%}")
    print(f"  Buy & Hold: {rsi_result['metrics']['buy_hold_return']:.2%}")
    print(f"  Sharpe Ratio: {rsi_result['metrics']['sharpe_ratio']:.2f}")
    print(f"  Max Drawdown: {rsi_result['metrics']['max_drawdown']:.2%}")
    print(f"  Win Rate: {rsi_result['metrics']['win_rate']:.2%}")
    print(f"  Number of Trades: {rsi_result['metrics']['num_trades']}")
    
    # Test MACD strategy
    print("\n🎯 Testing MACD Strategy on AAPL")
    macd_strategy = MACDStrategy()
    macd_result = engine.run_backtest(aapl_data, macd_strategy, position_size=0.15)
    
    print(f"\nMACD Strategy Results:")
    print(f"  Total Return: {macd_result['metrics']['total_return']:.2%}")
    print(f"  Buy & Hold: {macd_result['metrics']['buy_hold_return']:.2%}")
    print(f"  Sharpe Ratio: {macd_result['metrics']['sharpe_ratio']:.2f}")
    print(f"  Max Drawdown: {macd_result['metrics']['max_drawdown']:.2%}")
    print(f"  Win Rate: {macd_result['metrics']['win_rate']:.2%}")
    print(f"  Number of Trades: {macd_result['metrics']['num_trades']}")
    
    # Compare strategies
    print("\n📊 Strategy Comparison")
    comparison = engine.compare_strategies([rsi_result, macd_result])
    print("\n" + comparison.to_string(index=False))
    
    # Save results
    engine.save_results()
    print("\n✓ Backtest results saved to ./data/backtesting/")
    
    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("\n" + "=" * 80)
    print("WORKFLOW COMPLETED SUCCESSFULLY")
    print("=" * 80)
    
    print("\n📁 Generated Files:")
    print("  - Raw data: ./data/raw/")
    print("  - Validated data: ./data/validated/")
    print("  - Features: ./data/features/offline/")
    print("  - Analytics: ./data/analytics/")
    print("  - Backtesting: ./data/backtesting/")
    print("  - Logs: ./logs/")
    
    print("\n🚀 Next Steps:")
    print("  1. Launch dashboard: python main.py dashboard")
    print("  2. Run streaming: python main.py stream")
    print("  3. Check status: python main.py status")
    print("  4. Explore data in ./data/ directory")
    
    print("\n" + "=" * 80)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nWorkflow interrupted by user")
    except Exception as e:
        logger.error(f"Workflow failed: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        print("Check logs in ./logs/ for details")

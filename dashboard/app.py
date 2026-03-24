"""Streamlit dashboard for the Financial Feature Store."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from config import config
from feature_store import OfflineFeatureStore, OnlineFeatureStore
from analytics import FeatureAnalyzer
from utils.logger import setup_logging

# Setup
setup_logging()
st.set_page_config(
    page_title="Financial Feature Store Dashboard",
    page_icon="📈",
    layout="wide"
)

# Initialize stores
@st.cache_resource
def init_stores():
    """Initialize feature stores."""
    offline_store = OfflineFeatureStore()
    online_store = OnlineFeatureStore()
    analyzer = FeatureAnalyzer()
    return offline_store, online_store, analyzer

offline_store, online_store, analyzer = init_stores()

# Sidebar
st.sidebar.title("📊 Feature Store Dashboard")
st.sidebar.markdown("---")

# Page selection
page = st.sidebar.selectbox(
    "Select Page",
    ["Overview", "Feature Explorer", "Real-Time Features", "Analytics", "Backtesting Results"]
)

# Ticker selection
tickers = config.get('data.tickers', ['AAPL', 'TSLA', 'GOOGL'])
selected_ticker = st.sidebar.selectbox("Select Ticker", tickers)

st.sidebar.markdown("---")
st.sidebar.info(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Main content
if page == "Overview":
    st.title("📈 Financial Feature Store - Overview")
    
    col1, col2, col3 = st.columns(3)
    
    # Offline store stats
    stats = offline_store.get_feature_stats('market_features')
    
    with col1:
        st.metric("Total Records", f"{stats.get('total_records', 0):,}")
    
    with col2:
        st.metric("Number of Features", stats.get('num_features', 0))
    
    with col3:
        st.metric("Tickers", len(stats.get('tickers', [])))
    
    st.markdown("---")
    
    # Feature groups
    st.subheader("📁 Feature Groups")
    feature_groups = offline_store.list_feature_groups()
    
    if feature_groups:
        for group in feature_groups:
            with st.expander(f"📦 {group}"):
                versions = offline_store.list_versions(group)
                st.write(f"**Versions:** {', '.join(versions)}")
                
                group_stats = offline_store.get_feature_stats(group)
                st.write(f"**Records:** {group_stats.get('total_records', 0):,}")
                st.write(f"**Date Range:** {group_stats.get('date_range', {}).get('start')} to {group_stats.get('date_range', {}).get('end')}")
    else:
        st.info("No feature groups found. Run the batch pipeline first.")
    
    # Online store status
    st.markdown("---")
    st.subheader("🔴 Online Store Status")
    
    if online_store.is_connected():
        st.success("✅ Connected to Redis")
        online_stats = online_store.get_stats()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Active Tickers", online_stats.get('num_tickers', 0))
        with col2:
            st.metric("Memory Used", online_stats.get('used_memory_human', 'N/A'))
    else:
        st.error("❌ Not connected to Redis")

elif page == "Feature Explorer":
    st.title(f"🔍 Feature Explorer - {selected_ticker}")
    
    # Load data
    df = offline_store.read_features('market_features', filters={'ticker': selected_ticker})
    
    if df.empty:
        st.warning(f"No data found for {selected_ticker}")
    else:
        # Date range filter
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            min_date = df['date'].min().date()
            max_date = df['date'].max().date()
            
            date_range = st.slider(
                "Select Date Range",
                min_value=min_date,
                max_value=max_date,
                value=(min_date, max_date)
            )
            
            df = df[(df['date'].dt.date >= date_range[0]) & (df['date'].dt.date <= date_range[1])]
        
        # Feature selection
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        feature_cols = [col for col in numeric_cols if not col.startswith('_')]
        
        selected_features = st.multiselect(
            "Select Features to Display",
            feature_cols,
            default=['close', 'rsi', 'macd'] if all(f in feature_cols for f in ['close', 'rsi', 'macd']) else feature_cols[:3]
        )
        
        if selected_features:
            # Plot features
            for feature in selected_features:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df['date'],
                    y=df[feature],
                    mode='lines',
                    name=feature
                ))
                fig.update_layout(
                    title=f"{feature} Over Time",
                    xaxis_title="Date",
                    yaxis_title=feature,
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Data table
        st.subheader("📊 Data Table")
        display_cols = ['date'] + selected_features if selected_features else df.columns.tolist()
        st.dataframe(df[display_cols].tail(100), use_container_width=True)

elif page == "Real-Time Features":
    st.title("⚡ Real-Time Features")
    
    if not online_store.is_connected():
        st.error("❌ Online store not available. Please start Redis.")
    else:
        # Get latest features
        features = online_store.read_features(selected_ticker)
        
        if features:
            st.success(f"✅ Latest features for {selected_ticker}")
            
            # Display key metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Close Price", f"${features.get('close', 0):.2f}")
            
            with col2:
                st.metric("RSI", f"{features.get('rsi', 0):.2f}")
            
            with col3:
                st.metric("MACD", f"{features.get('macd', 0):.4f}")
            
            with col4:
                regime = features.get('regime', 0)
                regime_label = {1: "🟢 Bull", 0: "🟡 Sideways", -1: "🔴 Bear"}.get(regime, "Unknown")
                st.metric("Regime", regime_label)
            
            # Full feature table
            st.subheader("All Features")
            feature_df = pd.DataFrame([features]).T
            feature_df.columns = ['Value']
            st.dataframe(feature_df, use_container_width=True)
            
            # Timestamp
            st.info(f"Last Updated: {features.get('_timestamp', 'N/A')}")
        else:
            st.warning(f"No real-time features found for {selected_ticker}")
        
        # Auto-refresh
        if st.button("🔄 Refresh"):
            st.rerun()

elif page == "Analytics":
    st.title("📊 Feature Analytics")
    
    # Load data
    df = offline_store.read_features('market_features', filters={'ticker': selected_ticker})
    
    if df.empty:
        st.warning(f"No data found for {selected_ticker}")
    else:
        # Feature importance
        st.subheader("🎯 Feature Importance")
        
        if 'return' in df.columns:
            numeric_cols = df.select_dtypes(include=['number']).columns
            feature_cols = [col for col in numeric_cols 
                           if not col.startswith('_') and col not in ['date', 'return']]
            
            correlations = df[feature_cols].corrwith(df['return']).abs().sort_values(ascending=False).head(20)
            
            fig = px.bar(
                x=correlations.values,
                y=correlations.index,
                orientation='h',
                title="Top 20 Features by Correlation with Returns"
            )
            fig.update_layout(xaxis_title="Absolute Correlation", yaxis_title="Feature")
            st.plotly_chart(fig, use_container_width=True)
        
        # Correlation heatmap
        st.subheader("🔥 Feature Correlations")
        
        key_features = ['close', 'rsi', 'macd', 'volatility_10', 'momentum_score']
        available_features = [f for f in key_features if f in df.columns]
        
        if len(available_features) >= 2:
            corr_matrix = df[available_features].corr()
            
            fig = px.imshow(
                corr_matrix,
                text_auto=True,
                aspect="auto",
                title="Feature Correlation Matrix"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Summary statistics
        st.subheader("📈 Summary Statistics")
        st.dataframe(df[available_features].describe(), use_container_width=True)

elif page == "Backtesting Results":
    st.title("🎯 Backtesting Results")
    
    st.info("Run backtesting using: `python -m backtesting.backtest_engine --ticker AAPL`")
    
    # Try to load backtest results
    backtest_dir = Path("./data/backtesting")
    
    if backtest_dir.exists():
        result_files = list(backtest_dir.glob("*_history.parquet"))
        
        if result_files:
            selected_result = st.selectbox(
                "Select Backtest Result",
                [f.stem.replace('_history', '') for f in result_files]
            )
            
            # Load result
            history_file = backtest_dir / f"{selected_result}_history.parquet"
            history_df = pd.read_parquet(history_file)
            
            # Plot portfolio value
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=history_df['date'],
                y=history_df['portfolio_value'],
                mode='lines',
                name='Strategy',
                line=dict(color='blue')
            ))
            fig.add_trace(go.Scatter(
                x=history_df['date'],
                y=history_df['buy_hold_value'],
                mode='lines',
                name='Buy & Hold',
                line=dict(color='gray', dash='dash')
            ))
            fig.update_layout(
                title=f"{selected_result} - Portfolio Value",
                xaxis_title="Date",
                yaxis_title="Portfolio Value ($)",
                height=500
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Load metrics
            metrics_file = backtest_dir / f"{selected_result}_metrics.txt"
            if metrics_file.exists():
                with open(metrics_file, 'r') as f:
                    metrics_text = f.read()
                st.text(metrics_text)
        else:
            st.warning("No backtest results found.")
    else:
        st.warning("Backtesting directory not found.")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("**Real-Time Financial Feature Store**")
st.sidebar.markdown("Built with Streamlit 🎈")

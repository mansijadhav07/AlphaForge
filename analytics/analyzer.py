"""Feature analysis and insights generation."""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import List, Optional, Dict, Tuple

from config import config
from utils.logger import get_logger
from utils.helpers import ensure_dir

logger = get_logger(__name__)


class FeatureAnalyzer:
    """Analyze features and generate insights."""
    
    def __init__(self, output_dir: str = "./data/analytics"):
        """
        Initialize feature analyzer.
        
        Args:
            output_dir: Directory for saving plots and reports
        """
        self.output_dir = Path(output_dir)
        ensure_dir(self.output_dir)
        
        # Set plot style (use seaborn-v0_8 for newer matplotlib versions)
        try:
            plt.style.use(config.get('analytics.plot_style', 'seaborn-v0_8-darkgrid'))
        except:
            try:
                plt.style.use('seaborn-darkgrid')
            except:
                plt.style.use('default')
        
        try:
            sns.set_palette("husl")
        except:
            pass  # Seaborn not available or palette issue
        
        logger.info("FeatureAnalyzer initialized")
    
    def analyze_features(self, df: pd.DataFrame) -> Dict:
        """
        Perform comprehensive feature analysis.
        
        Args:
            df: DataFrame with features
            
        Returns:
            Dictionary with analysis results
        """
        logger.info("Starting feature analysis...")
        
        results = {
            'summary_stats': self._get_summary_stats(df),
            'missing_values': self._analyze_missing_values(df),
            'correlations': self._analyze_correlations(df),
            'feature_importance': self._analyze_feature_importance(df)
        }
        
        logger.info("Feature analysis complete")
        return results
    
    def _get_summary_stats(self, df: pd.DataFrame) -> pd.DataFrame:
        """Get summary statistics for features."""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        stats = df[numeric_cols].describe()
        return stats
    
    def _analyze_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Analyze missing values in features."""
        missing = pd.DataFrame({
            'count': df.isnull().sum(),
            'percentage': (df.isnull().sum() / len(df)) * 100
        })
        missing = missing[missing['count'] > 0].sort_values('count', ascending=False)
        return missing
    
    def _analyze_correlations(self, df: pd.DataFrame) -> pd.DataFrame:
        """Analyze feature correlations."""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        # Remove metadata columns
        feature_cols = [col for col in numeric_cols 
                       if not col.startswith('_') and col not in ['date', 'ticker']]
        
        if 'return' in df.columns:
            # Correlation with returns
            correlations = df[feature_cols].corrwith(df['return']).sort_values(ascending=False)
            return correlations
        else:
            return pd.Series()
    
    def _analyze_feature_importance(self, df: pd.DataFrame) -> pd.DataFrame:
        """Analyze feature importance based on correlation with returns."""
        if 'return' not in df.columns:
            logger.warning("No 'return' column found. Cannot compute feature importance.")
            return pd.DataFrame()
        
        correlations = self._analyze_correlations(df)
        
        # Get top features by absolute correlation
        top_n = config.get('analytics.feature_importance_top_n', 20)
        importance = correlations.abs().sort_values(ascending=False).head(top_n)
        
        return pd.DataFrame({
            'feature': importance.index,
            'importance': importance.values,
            'correlation': correlations[importance.index].values
        })
    
    def plot_feature_trends(
        self,
        df: pd.DataFrame,
        features: List[str],
        ticker: Optional[str] = None,
        save: bool = True
    ) -> None:
        """
        Plot feature trends over time.
        
        Args:
            df: DataFrame with features
            features: List of feature names to plot
            ticker: Specific ticker to plot (None = all)
            save: Whether to save plot
        """
        if ticker:
            df = df[df['ticker'] == ticker].copy()
        
        if 'date' not in df.columns:
            logger.warning("No 'date' column found")
            return
        
        df = df.sort_values('date')
        
        n_features = len(features)
        fig, axes = plt.subplots(n_features, 1, figsize=(12, 4 * n_features))
        
        if n_features == 1:
            axes = [axes]
        
        for ax, feature in zip(axes, features):
            if feature not in df.columns:
                logger.warning(f"Feature '{feature}' not found")
                continue
            
            ax.plot(df['date'], df[feature], linewidth=1.5)
            ax.set_title(f'{feature} Over Time', fontsize=12, fontweight='bold')
            ax.set_xlabel('Date')
            ax.set_ylabel(feature)
            ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save:
            filename = f"feature_trends_{ticker or 'all'}.png"
            filepath = self.output_dir / filename
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            logger.info(f"Plot saved to {filepath}")
        
        plt.close()
    
    def plot_correlation_heatmap(
        self,
        df: pd.DataFrame,
        features: Optional[List[str]] = None,
        save: bool = True
    ) -> None:
        """
        Plot correlation heatmap.
        
        Args:
            df: DataFrame with features
            features: Specific features to include (None = all numeric)
            save: Whether to save plot
        """
        if features is None:
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            features = [col for col in numeric_cols 
                       if not col.startswith('_') and col not in ['date', 'ticker']]
        
        # Limit to available features
        features = [f for f in features if f in df.columns]
        
        if len(features) < 2:
            logger.warning("Not enough features for correlation heatmap")
            return
        
        # Calculate correlation matrix
        corr_matrix = df[features].corr()
        
        # Create heatmap
        fig, ax = plt.subplots(figsize=(12, 10))
        
        sns.heatmap(
            corr_matrix,
            annot=False,
            cmap='coolwarm',
            center=0,
            square=True,
            linewidths=0.5,
            cbar_kws={"shrink": 0.8},
            ax=ax
        )
        
        ax.set_title('Feature Correlation Heatmap', fontsize=14, fontweight='bold', pad=20)
        plt.tight_layout()
        
        if save:
            filepath = self.output_dir / "correlation_heatmap.png"
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            logger.info(f"Heatmap saved to {filepath}")
        
        plt.close()
    
    def plot_feature_importance(
        self,
        df: pd.DataFrame,
        top_n: int = 20,
        save: bool = True
    ) -> None:
        """
        Plot feature importance.
        
        Args:
            df: DataFrame with features
            top_n: Number of top features to show
            save: Whether to save plot
        """
        importance_df = self._analyze_feature_importance(df)
        
        if importance_df.empty:
            logger.warning("No feature importance data available")
            return
        
        importance_df = importance_df.head(top_n)
        
        fig, ax = plt.subplots(figsize=(10, 8))
        
        colors = ['green' if x > 0 else 'red' for x in importance_df['correlation']]
        
        ax.barh(importance_df['feature'], importance_df['importance'], color=colors, alpha=0.7)
        ax.set_xlabel('Absolute Correlation with Returns', fontsize=12)
        ax.set_title(f'Top {top_n} Features by Importance', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        
        if save:
            filepath = self.output_dir / "feature_importance.png"
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            logger.info(f"Feature importance plot saved to {filepath}")
        
        plt.close()
    
    def generate_report(self, df: pd.DataFrame, ticker: Optional[str] = None) -> str:
        """
        Generate comprehensive analysis report.
        
        Args:
            df: DataFrame with features
            ticker: Specific ticker (None = all)
            
        Returns:
            Report as string
        """
        if ticker:
            df = df[df['ticker'] == ticker].copy()
        
        analysis = self.analyze_features(df)
        
        report = []
        report.append("=" * 80)
        report.append("FEATURE ANALYSIS REPORT")
        report.append("=" * 80)
        report.append(f"\nGenerated: {pd.Timestamp.now()}")
        report.append(f"Ticker: {ticker or 'All'}")
        report.append(f"Records: {len(df)}")
        report.append(f"Features: {len(df.columns)}")
        
        if 'date' in df.columns:
            report.append(f"Date Range: {df['date'].min()} to {df['date'].max()}")
        
        report.append("\n" + "-" * 80)
        report.append("MISSING VALUES")
        report.append("-" * 80)
        
        if not analysis['missing_values'].empty:
            report.append(analysis['missing_values'].to_string())
        else:
            report.append("No missing values found")
        
        report.append("\n" + "-" * 80)
        report.append("TOP FEATURES BY IMPORTANCE")
        report.append("-" * 80)
        
        if not analysis['feature_importance'].empty:
            top_features = analysis['feature_importance'].head(10)
            report.append(top_features.to_string(index=False))
        else:
            report.append("Feature importance not available")
        
        report.append("\n" + "=" * 80)
        
        report_text = "\n".join(report)
        
        # Save report
        filename = f"analysis_report_{ticker or 'all'}.txt"
        filepath = self.output_dir / filename
        with open(filepath, 'w') as f:
            f.write(report_text)
        
        logger.info(f"Report saved to {filepath}")
        
        return report_text

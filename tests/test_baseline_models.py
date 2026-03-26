"""
Tests for baseline models module.
"""

import pytest
import pandas as pd
import numpy as np
from pgm_model.baseline_models import (
    RandomBaseline,
    MajorityBaseline,
    LogisticRegressionBaseline,
    BaselineComparison,
    create_baseline_comparison
)


class TestRandomBaseline:
    """Test RandomBaseline class."""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample data."""
        np.random.seed(42)
        X = pd.DataFrame({
            'feature1': np.random.normal(0, 1, 100),
            'feature2': np.random.normal(0, 1, 100)
        })
        y = pd.Series(np.random.choice(['A', 'B', 'C'], 100))
        return X, y
    
    def test_fit_predict(self, sample_data):
        """Test fit and predict."""
        X, y = sample_data
        
        model = RandomBaseline()
        model.fit(X, y)
        
        predictions = model.predict(X)
        
        assert len(predictions) == len(X)
        assert set(predictions).issubset(set(y.unique()))
    
    def test_predict_proba(self, sample_data):
        """Test predict_proba."""
        X, y = sample_data
        
        model = RandomBaseline()
        model.fit(X, y)
        
        probas = model.predict_proba(X)
        
        assert probas.shape == (len(X), len(y.unique()))
        assert np.allclose(probas.sum(axis=1), 1.0)
        # All rows should be identical (uniform probability)
        assert np.allclose(probas[0], probas[1])


class TestMajorityBaseline:
    """Test MajorityBaseline class."""
    
    @pytest.fixture
    def imbalanced_data(self):
        """Create imbalanced data."""
        np.random.seed(42)
        X = pd.DataFrame({
            'feature1': np.random.normal(0, 1, 100),
            'feature2': np.random.normal(0, 1, 100)
        })
        # Imbalanced: 60% A, 30% B, 10% C
        y = pd.Series(['A'] * 60 + ['B'] * 30 + ['C'] * 10)
        return X, y
    
    def test_fit_predict(self, imbalanced_data):
        """Test fit and predict."""
        X, y = imbalanced_data
        
        model = MajorityBaseline()
        model.fit(X, y)
        
        predictions = model.predict(X)
        
        assert len(predictions) == len(X)
        # All predictions should be the majority class
        assert all(predictions == 'A')
    
    def test_predict_proba(self, imbalanced_data):
        """Test predict_proba."""
        X, y = imbalanced_data
        
        model = MajorityBaseline()
        model.fit(X, y)
        
        probas = model.predict_proba(X)
        
        assert probas.shape == (len(X), len(y.unique()))
        # Probability should be 1.0 for majority class, 0.0 for others
        assert probas[0, 0] == 1.0  # Assuming 'A' is first class
        assert probas[0, 1] == 0.0
        assert probas[0, 2] == 0.0


class TestLogisticRegressionBaseline:
    """Test LogisticRegressionBaseline class."""
    
    @pytest.fixture
    def linearly_separable_data(self):
        """Create linearly separable data."""
        np.random.seed(42)
        
        # Class A: high feature1, low feature2
        X_A = pd.DataFrame({
            'feature1': np.random.normal(2, 0.5, 30),
            'feature2': np.random.normal(-2, 0.5, 30)
        })
        y_A = pd.Series(['A'] * 30)
        
        # Class B: low feature1, high feature2
        X_B = pd.DataFrame({
            'feature1': np.random.normal(-2, 0.5, 30),
            'feature2': np.random.normal(2, 0.5, 30)
        })
        y_B = pd.Series(['B'] * 30)
        
        # Class C: middle
        X_C = pd.DataFrame({
            'feature1': np.random.normal(0, 0.5, 30),
            'feature2': np.random.normal(0, 0.5, 30)
        })
        y_C = pd.Series(['C'] * 30)
        
        X = pd.concat([X_A, X_B, X_C], ignore_index=True)
        y = pd.concat([y_A, y_B, y_C], ignore_index=True)
        
        return X, y
    
    def test_fit_predict(self, linearly_separable_data):
        """Test fit and predict."""
        X, y = linearly_separable_data
        
        model = LogisticRegressionBaseline()
        model.fit(X, y)
        
        predictions = model.predict(X)
        
        assert len(predictions) == len(X)
        assert set(predictions).issubset(set(y.unique()))
        
        # Should have reasonable accuracy on linearly separable data
        accuracy = (predictions == y).mean()
        assert accuracy > 0.7
    
    def test_predict_proba(self, linearly_separable_data):
        """Test predict_proba."""
        X, y = linearly_separable_data
        
        model = LogisticRegressionBaseline()
        model.fit(X, y)
        
        probas = model.predict_proba(X)
        
        assert probas.shape == (len(X), len(y.unique()))
        assert np.allclose(probas.sum(axis=1), 1.0)


class TestBaselineComparison:
    """Test BaselineComparison class."""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample data."""
        np.random.seed(42)
        
        # Create somewhat separable data
        X = pd.DataFrame({
            'feature1': np.random.normal(0, 1, 200),
            'feature2': np.random.normal(0, 1, 200),
            'feature3': np.random.normal(0, 1, 200)
        })
        
        # Target based on features
        y = pd.Series(['A'] * 70 + ['B'] * 70 + ['C'] * 60)
        
        # Train/test split
        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.3, random_state=42
        )
        
        return X_train, X_test, y_train, y_test
    
    def test_add_model(self):
        """Test adding models."""
        comparison = BaselineComparison()
        
        comparison.add_model('Random', RandomBaseline())
        comparison.add_model('Majority', MajorityBaseline())
        
        assert len(comparison.models) == 2
        assert 'Random' in comparison.models
        assert 'Majority' in comparison.models
    
    def test_compare_all(self, sample_data):
        """Test comparing all models."""
        X_train, X_test, y_train, y_test = sample_data
        
        comparison = BaselineComparison()
        comparison.add_model('Random', RandomBaseline())
        comparison.add_model('Majority', MajorityBaseline())
        comparison.add_model('Logistic Regression', LogisticRegressionBaseline())
        
        results = comparison.compare_all(X_train, y_train, X_test, y_test)
        
        assert len(results) == 3
        assert 'Random' in results
        assert 'Majority' in results
        assert 'Logistic Regression' in results
        
        # Check metrics
        for name, metrics in results.items():
            assert 0 <= metrics.accuracy <= 1
            assert 0 <= metrics.precision <= 1
            assert 0 <= metrics.recall <= 1
            assert 0 <= metrics.f1_score <= 1
            assert metrics.training_time >= 0
            assert metrics.prediction_time >= 0
    
    def test_get_comparison_summary(self, sample_data):
        """Test getting comparison summary."""
        X_train, X_test, y_train, y_test = sample_data
        
        comparison = BaselineComparison()
        comparison.add_model('Random', RandomBaseline())
        comparison.add_model('Logistic Regression', LogisticRegressionBaseline())
        
        comparison.compare_all(X_train, y_train, X_test, y_test)
        
        summary = comparison.get_comparison_summary()
        
        assert isinstance(summary, pd.DataFrame)
        assert len(summary) == 2
        assert 'Model' in summary.columns
        assert 'Accuracy' in summary.columns
        assert 'F1 Score' in summary.columns
    
    def test_get_best_model(self, sample_data):
        """Test getting best model."""
        X_train, X_test, y_train, y_test = sample_data
        
        comparison = BaselineComparison()
        comparison.add_model('Random', RandomBaseline())
        comparison.add_model('Logistic Regression', LogisticRegressionBaseline())
        
        comparison.compare_all(X_train, y_train, X_test, y_test)
        
        best_name, best_metrics = comparison.get_best_model('accuracy')
        
        assert best_name in ['Random', 'Logistic Regression']
        assert best_metrics.accuracy >= 0


class TestCreateBaselineComparison:
    """Test create_baseline_comparison function."""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample data."""
        np.random.seed(42)
        
        X = pd.DataFrame({
            'feature1': np.random.normal(0, 1, 200),
            'feature2': np.random.normal(0, 1, 200)
        })
        y = pd.Series(np.random.choice(['A', 'B', 'C'], 200))
        
        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.3, random_state=42
        )
        
        return X_train, X_test, y_train, y_test
    
    def test_create_comparison(self, sample_data):
        """Test creating complete comparison."""
        X_train, X_test, y_train, y_test = sample_data
        
        results = create_baseline_comparison(
            X_train, y_train, X_test, y_test
        )
        
        assert 'results' in results
        assert 'summary' in results
        assert 'best_model' in results
        assert 'comparison' in results
        
        # Should have 3 baseline models
        assert len(results['results']) == 3
        
        # Summary should be a list of dicts
        assert isinstance(results['summary'], list)
        assert len(results['summary']) == 3
        
        # Best model should have name and metrics
        assert 'name' in results['best_model']
        assert 'accuracy' in results['best_model']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

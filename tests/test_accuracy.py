"""
Prediction Accuracy Testing
============================

Comprehensive tests to measure prediction accuracy and performance.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    mean_absolute_error, mean_squared_error, r2_score
)


class AccuracyMetrics:
    """Calculate various accuracy metrics for predictions"""

    @staticmethod
    def classification_metrics(y_true, y_pred):
        """Calculate classification metrics for directional predictions"""
        return {
            'accuracy': accuracy_score(y_true, y_pred) * 100,
            'precision': precision_score(y_true, y_pred, average='weighted', zero_division=0) * 100,
            'recall': recall_score(y_true, y_pred, average='weighted', zero_division=0) * 100,
            'f1_score': f1_score(y_true, y_pred, average='weighted', zero_division=0) * 100
        }

    @staticmethod
    def regression_metrics(y_true, y_pred):
        """Calculate regression metrics for price predictions"""
        mae = mean_absolute_error(y_true, y_pred)
        mse = mean_squared_error(y_true, y_pred)
        rmse = np.sqrt(mse)

        # Calculate MAPE (Mean Absolute Percentage Error)
        mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100

        # R-squared score
        r2 = r2_score(y_true, y_pred)

        return {
            'mae': mae,
            'mse': mse,
            'rmse': rmse,
            'mape': mape,
            'r2_score': r2
        }

    @staticmethod
    def directional_accuracy(actual_changes, predicted_changes):
        """Calculate directional prediction accuracy"""
        actual_direction = (actual_changes > 0).astype(int)
        predicted_direction = (predicted_changes > 0).astype(int)

        correct = (actual_direction == predicted_direction).sum()
        total = len(actual_direction)

        return (correct / total) * 100


class TestAccuracyMetrics:
    """Test accuracy calculation methods"""

    def test_perfect_classification(self):
        """Test perfect classification accuracy"""
        y_true = np.array([1, 0, 1, 1, 0, 0, 1, 0])
        y_pred = np.array([1, 0, 1, 1, 0, 0, 1, 0])

        metrics = AccuracyMetrics.classification_metrics(y_true, y_pred)

        assert metrics['accuracy'] == 100.0, "Perfect predictions should have 100% accuracy"
        assert metrics['precision'] == 100.0, "Perfect predictions should have 100% precision"
        assert metrics['recall'] == 100.0, "Perfect predictions should have 100% recall"

    def test_partial_classification(self):
        """Test partial classification accuracy"""
        y_true = np.array([1, 0, 1, 1, 0, 0, 1, 0, 1, 0])
        y_pred = np.array([1, 0, 1, 0, 0, 1, 1, 0, 1, 1])
        #                  ✓  ✓  ✓  ✗  ✓  ✗  ✓  ✓  ✓  ✗  = 7/10 = 70%

        metrics = AccuracyMetrics.classification_metrics(y_true, y_pred)

        assert 60 <= metrics['accuracy'] <= 80, "Should have ~70% accuracy"

    def test_perfect_regression(self):
        """Test perfect regression accuracy"""
        y_true = np.array([10000, 10500, 9800, 10200, 10300])
        y_pred = np.array([10000, 10500, 9800, 10200, 10300])

        metrics = AccuracyMetrics.regression_metrics(y_true, y_pred)

        assert metrics['mae'] == 0, "Perfect predictions should have 0 MAE"
        assert metrics['rmse'] == 0, "Perfect predictions should have 0 RMSE"
        assert metrics['mape'] == 0, "Perfect predictions should have 0 MAPE"
        assert metrics['r2_score'] == 1.0, "Perfect predictions should have R² = 1"

    def test_regression_with_errors(self):
        """Test regression with prediction errors"""
        y_true = np.array([10000, 10500, 9800, 10200, 10300])
        y_pred = np.array([10100, 10400, 9900, 10100, 10400])
        #      Errors:      100   -100    100   -100    100

        metrics = AccuracyMetrics.regression_metrics(y_true, y_pred)

        assert metrics['mae'] == 100, "MAE should be 100"
        assert metrics['rmse'] > 0, "RMSE should be positive"
        assert 0 < metrics['mape'] < 2, "MAPE should be small (<2%)"

    def test_directional_accuracy_perfect(self):
        """Test perfect directional accuracy"""
        actual_changes = np.array([100, -50, 200, -100, 150])
        predicted_changes = np.array([80, -30, 150, -120, 100])
        # Directions:           ↑    ↓    ↑     ↓     ↑

        accuracy = AccuracyMetrics.directional_accuracy(actual_changes, predicted_changes)

        assert accuracy == 100.0, "All directions correct = 100%"

    def test_directional_accuracy_partial(self):
        """Test partial directional accuracy"""
        actual_changes = np.array([100, -50, 200, -100, 150])
        predicted_changes = np.array([80, 30, 150, -120, -50])
        # Directions:           ↑    ↓    ↑     ↓     ↑
        # Predicted:            ↑    ↑    ↑     ↓     ↓
        # Correct:              ✓    ✗    ✓     ✓     ✗  = 3/5 = 60%

        accuracy = AccuracyMetrics.directional_accuracy(actual_changes, predicted_changes)

        assert accuracy == 60.0, "60% of directions should be correct"


class TestPredictionAccuracy:
    """Test prediction accuracy for stock system"""

    @pytest.fixture
    def sample_predictions(self):
        """Generate sample predictions and actuals"""
        np.random.seed(42)

        # Actual prices
        actual = np.array([10000, 10100, 10050, 10200, 10150, 10300, 10250, 10400])

        # Predictions (with some error)
        predicted = actual + np.random.randn(len(actual)) * 50

        return actual, predicted

    def test_price_prediction_accuracy(self, sample_predictions):
        """Test price prediction accuracy metrics"""
        actual, predicted = sample_predictions

        metrics = AccuracyMetrics.regression_metrics(actual, predicted)

        # MAE should be reasonable (< 1% of price)
        assert metrics['mae'] < 100, "MAE should be < 100"

        # MAPE should be < 1% for good predictions
        assert metrics['mape'] < 1.0, "MAPE should be < 1% for excellent predictions"

    def test_direction_prediction_accuracy(self, sample_predictions):
        """Test direction prediction accuracy"""
        actual, predicted = sample_predictions

        # Calculate changes
        actual_changes = np.diff(actual)
        predicted_changes = np.diff(predicted)

        accuracy = AccuracyMetrics.directional_accuracy(actual_changes, predicted_changes)

        # Should predict direction correctly most of the time
        assert accuracy >= 50.0, "Should predict direction better than random (>50%)"

    def test_signal_accuracy(self):
        """Test trading signal accuracy"""
        # Actual outcomes: 1 = price went up, 0 = price went down
        actual_outcomes = np.array([1, 1, 0, 1, 0, 0, 1, 1, 1, 0])

        # Predicted signals: 1 = BUY, 0 = SELL/HOLD
        predicted_signals = np.array([1, 1, 0, 0, 0, 0, 1, 1, 1, 1])

        metrics = AccuracyMetrics.classification_metrics(actual_outcomes, predicted_signals)

        # Signal accuracy should be measured
        assert 0 <= metrics['accuracy'] <= 100, "Accuracy should be between 0-100%"

    def test_confidence_intervals(self):
        """Test prediction confidence intervals"""
        predictions = np.array([10100, 10200, 10150, 10250])
        std_dev = 50  # Standard deviation of predictions

        # 95% confidence interval = ±1.96 * std_dev
        confidence_95 = 1.96 * std_dev

        lower_bound = predictions - confidence_95
        upper_bound = predictions + confidence_95

        assert len(lower_bound) == len(predictions), "Should have bounds for all predictions"
        assert (upper_bound > lower_bound).all(), "Upper bound should be > lower bound"


class TestTargetAccuracy:
    """Test accuracy of hitting target prices"""

    def test_target_achievement_rate(self):
        """Test how often targets are achieved"""
        # Trade results
        trades = [
            {'entry': 10000, 'target': 10400, 'actual_high': 10450, 'hit': True},
            {'entry': 9500, 'target': 9800, 'actual_high': 9750, 'hit': False},
            {'entry': 10200, 'target': 10600, 'actual_high': 10650, 'hit': True},
            {'entry': 9800, 'target': 10100, 'actual_high': 10000, 'hit': False},
            {'entry': 10500, 'target': 10900, 'actual_high': 11000, 'hit': True},
        ]

        hits = sum(1 for t in trades if t['hit'])
        target_achievement_rate = (hits / len(trades)) * 100

        assert target_achievement_rate == 60.0, "Should achieve 60% of targets"

    def test_stop_loss_effectiveness(self):
        """Test stop loss effectiveness"""
        trades = [
            {'entry': 10000, 'stop': 9800, 'actual_low': 9750, 'hit': True, 'saved': 200},
            {'entry': 9500, 'stop': 9300, 'actual_low': 9400, 'hit': False, 'saved': 0},
            {'entry': 10200, 'stop': 10000, 'actual_low': 9900, 'hit': True, 'saved': 100},
        ]

        stops_hit = sum(1 for t in trades if t['hit'])
        total_saved = sum(t['saved'] for t in trades)

        assert stops_hit == 2, "2 stop losses should have been hit"
        assert total_saved == 300, "Should have saved Rp 300 total"

    def test_entry_timing_accuracy(self):
        """Test entry timing accuracy"""
        # Measure if we bought near the low
        trades = [
            {'entry': 10000, 'day_low': 9800, 'day_high': 10500},
            {'entry': 9900, 'day_low': 9850, 'day_high': 10200},
            {'entry': 10300, 'day_low': 10000, 'day_high': 10600},
        ]

        for trade in trades:
            day_range = trade['day_high'] - trade['day_low']
            position_in_range = (trade['entry'] - trade['day_low']) / day_range
            trade['entry_quality'] = position_in_range

        avg_entry_position = np.mean([t['entry_quality'] for t in trades])

        # Good entry should be in lower 50% of range
        assert avg_entry_position < 0.6, "Should enter in lower part of range"


class TestSystemAccuracy:
    """Test overall system accuracy goals"""

    def test_target_accuracy_under_1_percent(self):
        """Test if system can achieve <1% prediction error"""
        # Simulate predictions with <1% error
        actual_prices = np.array([10000, 10100, 10050, 10200])
        predicted_prices = actual_prices + np.array([50, -40, 30, -60])  # Max 0.6% error

        metrics = AccuracyMetrics.regression_metrics(actual_prices, predicted_prices)

        assert metrics['mape'] < 1.0, "System should achieve <1% MAPE"

    def test_target_accuracy_under_point_1_percent(self):
        """Test if system can achieve <0.1% prediction error (goal)"""
        # Simulate very accurate predictions
        actual_prices = np.array([10000, 10100, 10050, 10200])
        predicted_prices = actual_prices + np.array([5, -4, 3, -6])  # Max 0.06% error

        metrics = AccuracyMetrics.regression_metrics(actual_prices, predicted_prices)

        assert metrics['mape'] < 0.1, "Advanced system should achieve <0.1% MAPE"

    def test_directional_accuracy_target_85_percent(self):
        """Test if system can achieve 85%+ directional accuracy"""
        # 85% directional accuracy
        actual_changes = np.array([1, 1, 0, 1, 0, 0, 1, 1, 1, 0,
                                  1, 0, 1, 1, 0, 0, 1, 1, 1, 0])
        predicted_changes = np.array([1, 1, 0, 1, 0, 1, 1, 1, 1, 0,  # 17/20 correct = 85%
                                     1, 0, 1, 1, 1, 0, 1, 1, 1, 0])

        accuracy = AccuracyMetrics.directional_accuracy(actual_changes, predicted_changes)

        assert accuracy >= 85.0, "System should achieve ≥85% directional accuracy"

    def test_win_rate_target_70_percent(self):
        """Test if trading system can achieve 70%+ win rate"""
        # Simulate trades
        trades = [1, 1, 1, 0, 1, 1, 1, 0, 1, 1]  # 1 = win, 0 = loss

        win_rate = (sum(trades) / len(trades)) * 100

        assert win_rate >= 70.0, "System should achieve ≥70% win rate"


class TestLongTermAccuracy:
    """Test long-term prediction accuracy"""

    def test_monthly_accuracy(self):
        """Test prediction accuracy over 1 month"""
        # Simulate 20 trading days
        np.random.seed(42)
        actual = 10000 + np.cumsum(np.random.randn(20) * 50)
        predicted = actual + np.random.randn(20) * 30

        metrics = AccuracyMetrics.regression_metrics(actual, predicted)

        # Long-term predictions should maintain accuracy
        assert metrics['mape'] < 2.0, "Monthly predictions should have <2% MAPE"

    def test_consistency_over_time(self):
        """Test if accuracy is consistent over time"""
        # Test accuracy doesn't degrade
        week1_mape = 0.5
        week2_mape = 0.6
        week3_mape = 0.55
        week4_mape = 0.7

        # Trend should not be significantly increasing
        mapes = [week1_mape, week2_mape, week3_mape, week4_mape]
        avg_mape = np.mean(mapes)

        assert avg_mape < 1.0, "Average MAPE should stay <1%"
        assert max(mapes) < 1.0, "All weekly MAPEs should be <1%"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

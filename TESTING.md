```markdown
# Testing & Validation Guide
**Stock Prediction Indonesia - Comprehensive Test Suite**

Panduan lengkap untuk menjalankan unit tests, integration tests, dan backtesting untuk mengukur akurasi prediksi sistem.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Test Suite Structure](#test-suite-structure)
3. [Running Tests](#running-tests)
4. [Test Coverage](#test-coverage)
5. [Backtesting Framework](#backtesting-framework)
6. [Accuracy Metrics](#accuracy-metrics)
7. [Continuous Testing](#continuous-testing)

---

## 🎯 Overview

Test suite ini dirancang untuk:
- ✅ **Validate** semua 18 technical indicators
- ✅ **Test** entry/exit calculations untuk multibagger trading
- ✅ **Backtest** strategi dengan historical data
- ✅ **Measure** akurasi prediksi secara objektif
- ✅ **Ensure** sistem mencapai target <0.1% error

### Accuracy Goals

| Metric | Target | Current |
|--------|--------|---------|
| **Price Prediction (MAPE)** | <0.1% | Testing Required |
| **Directional Accuracy** | ≥85% | Testing Required |
| **Win Rate (Trading)** | ≥70% | Testing Required |
| **Risk/Reward Ratio** | ≥1.5:1 | Testing Required |

---

## 📁 Test Suite Structure

```
tests/
├── __init__.py                 # Test package initialization
├── test_indicators.py          # Test 18 technical indicators
├── test_multibagger.py         # Test entry/exit calculations
├── test_backtest.py            # Backtesting framework
└── test_accuracy.py            # Accuracy measurement
```

### File Descriptions

#### `test_indicators.py` (18 Indicators)
Tests all technical indicators:
1. SMA (Simple Moving Average)
2. EMA (Exponential Moving Average)
3. RSI (Relative Strength Index)
4. MACD (Moving Average Convergence Divergence)
5. Bollinger Bands
6. Volume Analysis
7. Stochastic Oscillator
8. ATR (Average True Range)
9. Momentum
10. OBV (On-Balance Volume)
11-15. Additional indicators
16. Chart Pattern Detection
17. Candlestick Pattern Detection
18. Volume Profile Analysis

#### `test_multibagger.py`
Tests multibagger daily trading system:
- Entry price calculation
- Target price calculation
- Stop loss calculation
- Risk/reward ratio
- Support/resistance levels
- Signal generation (6-component algorithm)
- Portfolio simulation
- Trading scenarios

#### `test_backtest.py`
Backtesting framework:
- Trade execution engine
- Portfolio tracking
- Performance metrics
- Real data backtesting
- Strategy comparison

#### `test_accuracy.py`
Accuracy measurement:
- Classification metrics (accuracy, precision, recall, F1)
- Regression metrics (MAE, MSE, RMSE, MAPE, R²)
- Directional accuracy
- Target achievement rate
- Stop loss effectiveness
- Long-term accuracy

---

## 🚀 Running Tests

### Prerequisites

Install dependencies:
```bash
pip install -r requirements.txt
```

Dependencies include:
- `pytest>=7.4.0` - Testing framework
- `pytest-cov>=4.1.0` - Coverage reporting
- `scikit-learn>=1.3.0` - Metrics calculation
- `numpy>=1.24.0` - Numerical operations
- `pandas>=2.0.0` - Data manipulation

### Run All Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=. --cov-report=html

# Run specific test file
pytest tests/test_indicators.py -v

# Run specific test class
pytest tests/test_multibagger.py::TestEntryExitCalculations -v

# Run specific test function
pytest tests/test_accuracy.py::TestAccuracyMetrics::test_perfect_classification -v
```

### Test Output Example

```
tests/test_indicators.py::TestTechnicalIndicators::test_sma_calculation PASSED     [ 10%]
tests/test_indicators.py::TestTechnicalIndicators::test_ema_calculation PASSED     [ 20%]
tests/test_indicators.py::TestTechnicalIndicators::test_rsi_calculation PASSED     [ 30%]
tests/test_multibagger.py::TestEntryExitCalculations::test_entry_price_at_high PASSED [ 40%]
tests/test_multibagger.py::TestEntryExitCalculations::test_risk_reward_ratio PASSED [ 50%]
tests/test_backtest.py::TestBacktesting::test_buy_trade PASSED                    [ 60%]
tests/test_accuracy.py::TestAccuracyMetrics::test_perfect_classification PASSED   [ 70%]

========================== 50 passed in 5.23s ==========================
```

---

## 📊 Test Coverage

### View Coverage Report

After running tests with `--cov`:
```bash
# Generate HTML coverage report
pytest tests/ --cov=. --cov-report=html

# Open report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### Coverage Goals

| Component | Target Coverage | Description |
|-----------|----------------|-------------|
| Technical Indicators | 90%+ | All 18 indicators tested |
| Multibagger System | 95%+ | Entry/exit logic critical |
| Prediction Engine | 85%+ | Core prediction functionality |
| Overall System | 80%+ | Complete codebase |

---

## 🔄 Backtesting Framework

### How Backtesting Works

```python
from tests.test_backtest import BacktestEngine

# Initialize with capital
engine = BacktestEngine(initial_capital=100_000_000)

# Execute trades
engine.execute_trade('BBCA', 'BUY', 10_000, 1000, date='2024-01-01')
engine.execute_trade('BBCA', 'SELL', 10_500, 1000, date='2024-01-10')

# Get performance metrics
metrics = engine.calculate_metrics()
print(f"Total Profit: Rp {metrics['total_profit']:,.0f}")
print(f"Win Rate: {metrics['win_rate']:.1f}%")
```

### Backtest Metrics

The framework calculates:
- **Total Trades**: Number of completed trades
- **Winning Trades**: Trades that made profit
- **Losing Trades**: Trades that lost money
- **Win Rate**: (Winning / Total) × 100%
- **Total Profit**: Sum of all P/L
- **Average Profit**: Mean profit per trade
- **Average Profit %**: Mean percentage return
- **Max Profit**: Largest winning trade
- **Max Loss**: Largest losing trade
- **Final Capital**: Ending capital value
- **Total Return**: (Final - Initial) / Initial × 100%

### Example Backtest Scenario

```python
# Test momentum strategy
def test_momentum_strategy():
    engine = BacktestEngine(initial_capital=50_000_000)

    # Historical prices
    prices = [10_000, 10_100, 10_300, 10_200, 10_500]

    # Buy on momentum
    engine.execute_trade('TEST', 'BUY', prices[0], 1000, '2024-01-01')

    # Sell after 5 days
    engine.execute_trade('TEST', 'SELL', prices[4], 1000, '2024-01-05')

    metrics = engine.calculate_metrics()

    # Assertions
    assert metrics['total_profit'] == 500_000  # Rp 500k profit
    assert metrics['avg_profit_pct'] == 5.0    # 5% return
    assert metrics['win_rate'] == 100.0        # 100% win rate
```

---

## 📈 Accuracy Metrics

### Classification Metrics (Directional Predictions)

**Accuracy**: Percentage of correct predictions
```python
accuracy = (correct_predictions / total_predictions) × 100
```

**Precision**: Of all BUY signals, how many were correct
```python
precision = (true_positives / (true_positives + false_positives)) × 100
```

**Recall**: Of all actual uptrends, how many did we catch
```python
recall = (true_positives / (true_positives + false_negatives)) × 100
```

**F1 Score**: Harmonic mean of precision and recall
```python
f1 = 2 × (precision × recall) / (precision + recall)
```

### Regression Metrics (Price Predictions)

**MAE (Mean Absolute Error)**: Average absolute difference
```python
MAE = mean(|actual - predicted|)
```

**RMSE (Root Mean Squared Error)**: Penalizes large errors more
```python
RMSE = sqrt(mean((actual - predicted)²))
```

**MAPE (Mean Absolute Percentage Error)**: Percentage error
```python
MAPE = mean(|actual - predicted| / actual) × 100
```

**R² Score**: How well predictions fit actual data (0 to 1)
```python
R² = 1 - (SS_residual / SS_total)
```

### Trading Performance Metrics

**Win Rate**: Percentage of profitable trades
```python
win_rate = (winning_trades / total_trades) × 100
```

**Profit Factor**: Gross profit ÷ Gross loss
```python
profit_factor = sum(profits) / abs(sum(losses))
```

**Sharpe Ratio**: Risk-adjusted returns
```python
sharpe = (mean_return - risk_free_rate) / std_return
```

**Max Drawdown**: Largest peak-to-trough decline
```python
max_drawdown = min((equity - running_max) / running_max)
```

---

## 🎯 Target Accuracy Validation

### Test: <1% Price Prediction Error

```python
def test_target_accuracy_under_1_percent():
    actual = [10000, 10100, 10050, 10200]
    predicted = [10050, 10060, 10080, 10150]

    mape = mean(abs((actual - predicted) / actual)) * 100

    assert mape < 1.0, "MAPE should be <1%"
```

### Test: <0.1% Price Prediction Error (Goal)

```python
def test_target_accuracy_under_point_1_percent():
    actual = [10000, 10100, 10050, 10200]
    predicted = [10005, 10104, 10047, 10194]

    mape = mean(abs((actual - predicted) / actual)) * 100

    assert mape < 0.1, "MAPE should be <0.1% (advanced goal)"
```

### Test: 85%+ Directional Accuracy

```python
def test_directional_accuracy_target_85_percent():
    actual_directions = [1, 1, 0, 1, 0, 0, 1, 1, 1, 0]
    predicted_directions = [1, 1, 0, 1, 0, 1, 1, 1, 1, 0]

    correct = sum(a == p for a, p in zip(actual, predicted))
    accuracy = (correct / len(actual)) * 100

    assert accuracy >= 85.0, "Directional accuracy should be ≥85%"
```

### Test: 70%+ Win Rate

```python
def test_win_rate_target_70_percent():
    trades = [1, 1, 1, 0, 1, 1, 1, 0, 1, 1]  # 1=win, 0=loss
    win_rate = (sum(trades) / len(trades)) * 100

    assert win_rate >= 70.0, "Win rate should be ≥70%"
```

---

## ⚡ Continuous Testing

### Pre-Commit Testing

Add to `.git/hooks/pre-commit`:
```bash
#!/bin/bash
pytest tests/ --maxfail=1 --disable-warnings -q
```

### Automated Daily Tests

Create cron job or scheduled task:
```bash
# Run tests daily at 9 AM
0 9 * * * cd /path/to/project && pytest tests/ --cov=.
```

### CI/CD Integration

**GitHub Actions** (`.github/workflows/test.yml`):
```yaml
name: Run Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest tests/ --cov=. --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

---

## 📊 Sample Test Results

### Expected Output

```
================================ test session starts ================================
platform linux -- Python 3.10.0, pytest-7.4.0
collected 85 items

tests/test_indicators.py::TestTechnicalIndicators
  ✓ test_sma_calculation                                                     [  1%]
  ✓ test_ema_calculation                                                     [  2%]
  ✓ test_rsi_calculation                                                     [  3%]
  ✓ test_macd_calculation                                                    [  4%]
  ✓ test_bollinger_bands                                                     [  5%]
  ... (15 more indicator tests)

tests/test_multibagger.py::TestEntryExitCalculations
  ✓ test_entry_price_at_high                                                 [ 25%]
  ✓ test_entry_price_at_support                                              [ 26%]
  ✓ test_target_price_strong_buy                                             [ 27%]
  ✓ test_stop_loss_calculation                                               [ 28%]
  ✓ test_risk_reward_ratio                                                   [ 29%]
  ... (20 more multibagger tests)

tests/test_backtest.py::TestBacktesting
  ✓ test_buy_trade                                                           [ 50%]
  ✓ test_sell_trade                                                          [ 51%]
  ✓ test_portfolio_value                                                     [ 52%]
  ✓ test_performance_metrics                                                 [ 53%]
  ... (15 more backtest tests)

tests/test_accuracy.py::TestAccuracyMetrics
  ✓ test_perfect_classification                                              [ 70%]
  ✓ test_regression_with_errors                                              [ 71%]
  ✓ test_directional_accuracy_perfect                                        [ 72%]
  ... (15 more accuracy tests)

================================ 85 passed in 12.45s ================================

Coverage Report:
--------------
Name                                  Stmts   Miss  Cover
---------------------------------------------------------
utils/chart_pattern_detector.py        245     15    94%
utils/candlestick_pattern_detector.py  310     20    94%
utils/volume_profile_analyzer.py       180     10    94%
utils/multibagger_tracker.py           220      8    96%
app.py                                2500    350    86%
---------------------------------------------------------
TOTAL                                 3455    403    88%
```

---

## 🔧 Troubleshooting

### Common Issues

**Issue: Tests fail with "Module not found"**
```bash
# Solution: Install dependencies
pip install -r requirements.txt
```

**Issue: Tests timeout**
```bash
# Solution: Increase timeout
pytest tests/ --timeout=300
```

**Issue: Coverage report not generated**
```bash
# Solution: Install pytest-cov
pip install pytest-cov
```

### Debug Mode

Run tests with detailed output:
```bash
# Show print statements
pytest tests/ -v -s

# Show local variables on failure
pytest tests/ -l

# Enter debugger on failure
pytest tests/ --pdb
```

---

## 📚 Best Practices

### Writing New Tests

1. **Follow naming convention**: `test_<feature>_<scenario>.py`
2. **Use fixtures**: Reuse test data with `@pytest.fixture`
3. **Test edge cases**: Not just happy path
4. **Assert clearly**: Use descriptive error messages
5. **Keep tests independent**: No shared state between tests

### Example Test Template

```python
import pytest

class TestNewFeature:
    """Test new feature description"""

    @pytest.fixture
    def sample_data(self):
        """Create sample data for testing"""
        return {'key': 'value'}

    def test_feature_success(self, sample_data):
        """Test feature succeeds under normal conditions"""
        result = my_function(sample_data)
        assert result is not None, "Result should not be None"

    def test_feature_edge_case(self):
        """Test feature handles edge case"""
        result = my_function(None)
        assert result == expected, "Should handle None input"
```

---

## 🎓 Next Steps

1. **Run baseline tests**: `pytest tests/ -v`
2. **Review coverage**: `pytest tests/ --cov=. --cov-report=html`
3. **Fix failing tests**: Address any test failures
4. **Add new tests**: As you add features
5. **Integrate CI/CD**: Automate testing
6. **Monitor metrics**: Track accuracy over time
7. **Optimize strategies**: Use backtest results to improve

---

## 📞 Support

Jika ada pertanyaan atau masalah dengan testing:
1. Check test output untuk error messages
2. Review TESTING.md documentation
3. Check GitHub Issues
4. Consult with development team

**Happy Testing! 🧪📊**
```

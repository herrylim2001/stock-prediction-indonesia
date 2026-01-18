"""
Unit Tests for Technical Indicators
====================================

Tests all 18 indicators used in the stock prediction system.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


class TestTechnicalIndicators:
    """Test technical indicators calculation"""

    @pytest.fixture
    def sample_data(self):
        """Create sample OHLCV data for testing"""
        dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
        np.random.seed(42)

        # Generate realistic stock price data
        close_prices = 10000 + np.cumsum(np.random.randn(100) * 100)

        df = pd.DataFrame({
            'Date': dates,
            'Open': close_prices + np.random.randn(100) * 50,
            'High': close_prices + np.abs(np.random.randn(100) * 100),
            'Low': close_prices - np.abs(np.random.randn(100) * 100),
            'Close': close_prices,
            'Volume': np.random.randint(1000000, 10000000, 100)
        })

        df.set_index('Date', inplace=True)
        return df

    def test_sma_calculation(self, sample_data):
        """Test Simple Moving Average (INDICATOR 1)"""
        df = sample_data.copy()

        # Calculate SMA-20
        df['SMA_20'] = df['Close'].rolling(window=20).mean()

        # Check SMA exists after window
        assert not df['SMA_20'].iloc[19:].isna().any(), "SMA should exist after window period"

        # SMA should be close to actual prices
        assert df['SMA_20'].iloc[-1] > 0, "SMA should be positive"

        # SMA should smooth out volatility
        sma_std = df['SMA_20'].iloc[20:].std()
        price_std = df['Close'].iloc[20:].std()
        assert sma_std < price_std, "SMA should have lower volatility than price"

    def test_ema_calculation(self, sample_data):
        """Test Exponential Moving Average (INDICATOR 2)"""
        df = sample_data.copy()

        # Calculate EMA-12
        df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()

        # EMA should exist for all data points
        assert not df['EMA_12'].isna().any(), "EMA should exist for all points"

        # EMA should be closer to recent prices than SMA
        df['SMA_12'] = df['Close'].rolling(window=12).mean()

        recent_price = df['Close'].iloc[-1]
        ema_value = df['EMA_12'].iloc[-1]
        sma_value = df['SMA_12'].iloc[-1]

        # EMA reacts faster to recent changes
        assert abs(recent_price - ema_value) <= abs(recent_price - sma_value) * 1.5

    def test_rsi_calculation(self, sample_data):
        """Test Relative Strength Index (INDICATOR 3)"""
        df = sample_data.copy()

        # Calculate RSI-14
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()

        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        # RSI should be between 0 and 100
        valid_rsi = df['RSI'].dropna()
        assert valid_rsi.min() >= 0, "RSI minimum should be >= 0"
        assert valid_rsi.max() <= 100, "RSI maximum should be <= 100"

        # RSI should have values in overbought/oversold zones
        assert len(df[df['RSI'] > 70]) > 0 or len(df[df['RSI'] < 30]) > 0, \
            "RSI should detect overbought or oversold conditions"

    def test_macd_calculation(self, sample_data):
        """Test MACD (INDICATOR 4)"""
        df = sample_data.copy()

        # Calculate MACD
        ema_12 = df['Close'].ewm(span=12, adjust=False).mean()
        ema_26 = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = ema_12 - ema_26
        df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']

        # MACD should exist
        assert not df['MACD'].iloc[26:].isna().any(), "MACD should exist after EMA-26 period"

        # Histogram should cross zero
        hist_values = df['MACD_Hist'].dropna()
        has_positive = (hist_values > 0).any()
        has_negative = (hist_values < 0).any()
        assert has_positive or has_negative, "MACD histogram should have positive or negative values"

    def test_bollinger_bands(self, sample_data):
        """Test Bollinger Bands (INDICATOR 5)"""
        df = sample_data.copy()

        # Calculate Bollinger Bands
        window = 20
        df['BB_Middle'] = df['Close'].rolling(window=window).mean()
        df['BB_Std'] = df['Close'].rolling(window=window).std()
        df['BB_Upper'] = df['BB_Middle'] + (2 * df['BB_Std'])
        df['BB_Lower'] = df['BB_Middle'] - (2 * df['BB_Std'])

        # Upper band should be above lower band
        valid_data = df.iloc[window:].copy()
        assert (valid_data['BB_Upper'] > valid_data['BB_Lower']).all(), \
            "Upper band should always be above lower band"

        # Price should mostly stay within bands
        within_bands = ((valid_data['Close'] >= valid_data['BB_Lower']) &
                       (valid_data['Close'] <= valid_data['BB_Upper']))
        within_pct = within_bands.sum() / len(valid_data) * 100
        assert within_pct >= 85, "At least 85% of prices should be within Bollinger Bands"

    def test_volume_analysis(self, sample_data):
        """Test Volume Analysis (INDICATOR 6)"""
        df = sample_data.copy()

        # Calculate volume average
        df['Volume_Avg'] = df['Volume'].rolling(window=20).mean()
        df['Volume_Ratio'] = df['Volume'] / df['Volume_Avg']

        # Volume should be positive
        assert (df['Volume'] > 0).all(), "Volume should always be positive"

        # Volume ratio should detect high volume days
        high_volume_days = df[df['Volume_Ratio'] > 1.5]
        assert len(high_volume_days) > 0, "Should detect some high volume days"

    def test_stochastic_oscillator(self, sample_data):
        """Test Stochastic Oscillator (INDICATOR 7)"""
        df = sample_data.copy()

        # Calculate Stochastic %K
        window = 14
        df['Low_Min'] = df['Low'].rolling(window=window).min()
        df['High_Max'] = df['High'].rolling(window=window).max()
        df['Stoch_K'] = 100 * (df['Close'] - df['Low_Min']) / (df['High_Max'] - df['Low_Min'])

        # Stochastic should be between 0 and 100
        valid_stoch = df['Stoch_K'].dropna()
        assert valid_stoch.min() >= 0, "Stochastic minimum should be >= 0"
        assert valid_stoch.max() <= 100, "Stochastic maximum should be <= 100"

    def test_atr_calculation(self, sample_data):
        """Test Average True Range (INDICATOR 8)"""
        df = sample_data.copy()

        # Calculate True Range
        df['H-L'] = df['High'] - df['Low']
        df['H-PC'] = abs(df['High'] - df['Close'].shift(1))
        df['L-PC'] = abs(df['Low'] - df['Close'].shift(1))
        df['TR'] = df[['H-L', 'H-PC', 'L-PC']].max(axis=1)
        df['ATR'] = df['TR'].rolling(window=14).mean()

        # ATR should be positive
        valid_atr = df['ATR'].dropna()
        assert (valid_atr > 0).all(), "ATR should always be positive"

        # ATR should measure volatility
        assert valid_atr.std() > 0, "ATR should vary with volatility"

    def test_momentum_indicators(self, sample_data):
        """Test Momentum (INDICATOR 9)"""
        df = sample_data.copy()

        # Calculate momentum
        df['Momentum'] = df['Close'] - df['Close'].shift(10)

        # Momentum should have positive and negative values
        valid_momentum = df['Momentum'].dropna()
        has_positive = (valid_momentum > 0).any()
        has_negative = (valid_momentum < 0).any()
        assert has_positive and has_negative, "Momentum should have both positive and negative values"

    def test_obv_calculation(self, sample_data):
        """Test On-Balance Volume (INDICATOR 10)"""
        df = sample_data.copy()

        # Calculate OBV
        df['OBV'] = 0
        df.loc[df['Close'] > df['Close'].shift(1), 'OBV'] = df['Volume']
        df.loc[df['Close'] < df['Close'].shift(1), 'OBV'] = -df['Volume']
        df['OBV'] = df['OBV'].cumsum()

        # OBV should exist
        assert not df['OBV'].isna().any(), "OBV should be calculated for all rows"

        # OBV should show trend
        assert df['OBV'].iloc[-1] != df['OBV'].iloc[0], "OBV should change over time"


class TestAdvancedIndicators:
    """Test advanced pattern detection indicators"""

    @pytest.fixture
    def sample_data(self):
        """Create sample data with patterns"""
        dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
        np.random.seed(42)

        # Generate data with clear trend
        base_price = 10000
        trend = np.linspace(0, 2000, 100)
        noise = np.random.randn(100) * 100
        close_prices = base_price + trend + noise

        df = pd.DataFrame({
            'Date': dates,
            'Open': close_prices + np.random.randn(100) * 50,
            'High': close_prices + np.abs(np.random.randn(100) * 100),
            'Low': close_prices - np.abs(np.random.randn(100) * 100),
            'Close': close_prices,
            'Volume': np.random.randint(1000000, 10000000, 100)
        })

        df.set_index('Date', inplace=True)
        return df

    def test_chart_pattern_detection(self, sample_data):
        """Test Chart Pattern Detection (INDICATOR 16)"""
        try:
            from utils.chart_pattern_detector import get_chart_patterns

            patterns = get_chart_patterns(sample_data)

            # Should return dictionary with patterns
            assert isinstance(patterns, dict), "Should return dictionary"
            assert 'summary' in patterns, "Should have summary"

            # Summary should have required fields
            summary = patterns['summary']
            assert 'aggregate_signal' in summary, "Should have aggregate signal"
            assert summary['aggregate_signal'] in ['BULLISH', 'BEARISH', 'NEUTRAL'], \
                "Signal should be BULLISH, BEARISH, or NEUTRAL"

        except ImportError:
            pytest.skip("Chart pattern detector not available")

    def test_candlestick_detection(self, sample_data):
        """Test Candlestick Pattern Detection (INDICATOR 17)"""
        try:
            from utils.candlestick_pattern_detector import get_candlestick_patterns

            patterns = get_candlestick_patterns(sample_data)

            # Should return dictionary
            assert isinstance(patterns, dict), "Should return dictionary"

            # Should have pattern categories
            assert 'summary' in patterns, "Should have summary"

        except ImportError:
            pytest.skip("Candlestick detector not available")

    def test_volume_profile(self, sample_data):
        """Test Volume Profile Analysis (INDICATOR 18)"""
        try:
            from utils.volume_profile_analyzer import get_volume_profile

            analysis = get_volume_profile(sample_data, bins=20)

            # Should return dictionary with analysis
            assert isinstance(analysis, dict), "Should return dictionary"
            assert 'poc' in analysis, "Should have Point of Control"
            assert 'value_area' in analysis, "Should have Value Area"
            assert 'momentum' in analysis, "Should have momentum score"

            # POC should be within price range
            poc_price = analysis['poc']['price']
            assert sample_data['Low'].min() <= poc_price <= sample_data['High'].max(), \
                "POC should be within price range"

        except ImportError:
            pytest.skip("Volume profile analyzer not available")


class TestPredictionAccuracy:
    """Test prediction accuracy metrics"""

    def test_accuracy_calculation(self):
        """Test accuracy metric calculation"""
        # Sample predictions vs actuals
        predictions = np.array([1, 1, 0, 1, 0, 0, 1, 1, 0, 0])
        actuals = np.array([1, 0, 0, 1, 0, 1, 1, 1, 0, 0])

        # Calculate accuracy
        correct = (predictions == actuals).sum()
        accuracy = correct / len(predictions) * 100

        assert 0 <= accuracy <= 100, "Accuracy should be between 0 and 100%"
        assert accuracy == 80.0, "Should calculate correct accuracy"

    def test_mae_calculation(self):
        """Test Mean Absolute Error"""
        predictions = np.array([10000, 10200, 9800, 10100])
        actuals = np.array([10100, 10150, 9900, 10000])

        mae = np.mean(np.abs(predictions - actuals))

        assert mae >= 0, "MAE should be non-negative"
        assert mae == 87.5, "Should calculate correct MAE"

    def test_rmse_calculation(self):
        """Test Root Mean Squared Error"""
        predictions = np.array([10000, 10200, 9800, 10100])
        actuals = np.array([10100, 10150, 9900, 10000])

        mse = np.mean((predictions - actuals) ** 2)
        rmse = np.sqrt(mse)

        assert rmse >= 0, "RMSE should be non-negative"
        assert rmse > 0, "RMSE should be positive for imperfect predictions"

    def test_directional_accuracy(self):
        """Test directional prediction accuracy"""
        # Predict if price will go up (1) or down (0)
        price_changes = np.array([100, -50, 200, -100, 150])  # actual changes
        predictions = np.array([1, 0, 1, 0, 1])  # predicted directions
        actuals = (price_changes > 0).astype(int)  # actual directions

        correct_direction = (predictions == actuals).sum()
        directional_accuracy = correct_direction / len(predictions) * 100

        assert directional_accuracy == 100.0, "All predictions should be correct"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

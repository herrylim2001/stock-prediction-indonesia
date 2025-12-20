"""
Data Collector for LSTM Training
Collects and prepares historical stock data with technical indicators
"""
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_fetcher import IDX_STOCKS
from ta.trend import SMAIndicator, EMAIndicator, MACD
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.volatility import BollingerBands, AverageTrueRange
from ta.volume import OnBalanceVolumeIndicator


class StockDataCollector:
    """Collect and prepare stock data for LSTM training"""

    def __init__(self):
        self.stocks = IDX_STOCKS

    def fetch_historical_data(self, stock_code, period="2y", interval="1d"):
        """
        Fetch historical data from Yahoo Finance

        Args:
            stock_code: Stock code (e.g., 'BBCA')
            period: Data period (1y, 2y, 5y, max)
            interval: Data interval (1d, 1h)

        Returns:
            DataFrame with OHLCV data
        """
        ticker = f"{stock_code}.JK"

        print(f"Fetching {stock_code} data...")

        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period=period, interval=interval)

            if df.empty:
                print(f"❌ No data for {stock_code}")
                return None

            df = df.reset_index()
            df.columns = [col.lower() for col in df.columns]
            df['stock_code'] = stock_code

            print(f"✓ Fetched {len(df)} rows for {stock_code}")
            return df

        except Exception as e:
            print(f"❌ Error fetching {stock_code}: {e}")
            return None

    def add_technical_indicators(self, df):
        """Add technical indicators to dataframe"""

        if df is None or len(df) < 50:
            print("⚠️ Insufficient data for indicators")
            return df

        print("Adding technical indicators...")

        try:
            # Price-based features
            df['returns'] = df['close'].pct_change()
            df['log_returns'] = np.log(df['close'] / df['close'].shift(1))

            # Moving Averages
            df['sma_5'] = SMAIndicator(df['close'], window=5).sma_indicator()
            df['sma_10'] = SMAIndicator(df['close'], window=10).sma_indicator()
            df['sma_20'] = SMAIndicator(df['close'], window=20).sma_indicator()
            df['sma_50'] = SMAIndicator(df['close'], window=50).sma_indicator()
            df['ema_12'] = EMAIndicator(df['close'], window=12).sma_indicator()
            df['ema_26'] = EMAIndicator(df['close'], window=26).ema_indicator()

            # RSI
            df['rsi'] = RSIIndicator(df['close'], window=14).rsi()

            # MACD
            macd = MACD(df['close'])
            df['macd'] = macd.macd()
            df['macd_signal'] = macd.macd_signal()
            df['macd_diff'] = macd.macd_diff()

            # Bollinger Bands
            bb = BollingerBands(df['close'], window=20, window_dev=2)
            df['bb_upper'] = bb.bollinger_hband()
            df['bb_middle'] = bb.bollinger_mavg()
            df['bb_lower'] = bb.bollinger_lband()
            df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']

            # ATR (Volatility)
            df['atr'] = AverageTrueRange(df['high'], df['low'], df['close'], window=14).average_true_range()

            # Stochastic
            stoch = StochasticOscillator(df['high'], df['low'], df['close'])
            df['stoch_k'] = stoch.stoch()
            df['stoch_d'] = stoch.stoch_signal()

            # Volume indicators
            df['obv'] = OnBalanceVolumeIndicator(df['close'], df['volume']).on_balance_volume()
            df['volume_sma'] = df['volume'].rolling(window=20).mean()
            df['volume_ratio'] = df['volume'] / df['volume_sma']

            # Price position relative to moving averages
            df['price_to_sma20'] = df['close'] / df['sma_20']
            df['price_to_sma50'] = df['close'] / df['sma_50']

            # Volatility
            df['volatility'] = df['returns'].rolling(window=20).std()

            print(f"✓ Added {len([c for c in df.columns if c not in ['date', 'stock_code']])} features")

        except Exception as e:
            print(f"❌ Error adding indicators: {e}")

        return df

    def create_sequences(self, df, sequence_length=60, target_columns=['close']):
        """
        Create sequences for LSTM training

        Args:
            df: DataFrame with features
            sequence_length: Number of timesteps to look back
            target_columns: Columns to predict

        Returns:
            X (sequences), y (targets)
        """
        # Remove non-numeric and target columns
        feature_columns = [col for col in df.columns if col not in
                          ['date', 'datetime', 'stock_code'] + target_columns]

        # Drop rows with NaN
        df_clean = df[feature_columns + target_columns].dropna()

        if len(df_clean) < sequence_length + 1:
            print(f"⚠️ Insufficient data after cleaning: {len(df_clean)} rows")
            return None, None

        # Normalize features
        from sklearn.preprocessing import MinMaxScaler

        scaler_X = MinMaxScaler()
        scaler_y = MinMaxScaler()

        X_scaled = scaler_X.fit_transform(df_clean[feature_columns])
        y_scaled = scaler_y.fit_transform(df_clean[target_columns])

        # Create sequences
        X_sequences = []
        y_sequences = []

        for i in range(sequence_length, len(X_scaled)):
            X_sequences.append(X_scaled[i-sequence_length:i])
            y_sequences.append(y_scaled[i])

        X = np.array(X_sequences)
        y = np.array(y_sequences)

        print(f"✓ Created {len(X)} sequences with shape {X.shape}")

        return X, y, scaler_X, scaler_y, feature_columns

    def prepare_training_data(self, stock_codes, period="2y", sequence_length=60):
        """
        Prepare training data for multiple stocks

        Args:
            stock_codes: List of stock codes
            period: Historical period
            sequence_length: Sequence length for LSTM

        Returns:
            X_train, y_train, scalers, metadata
        """
        all_X = []
        all_y = []
        metadata = {
            'stocks': [],
            'scalers_X': {},
            'scalers_y': {},
            'feature_columns': None,
            'sequence_length': sequence_length
        }

        for stock_code in stock_codes:
            # Fetch data
            df = self.fetch_historical_data(stock_code, period=period)
            if df is None:
                continue

            # Add indicators
            df = self.add_technical_indicators(df)

            # Create sequences
            X, y, scaler_X, scaler_y, feature_cols = self.create_sequences(
                df, sequence_length=sequence_length
            )

            if X is not None:
                all_X.append(X)
                all_y.append(y)
                metadata['stocks'].append(stock_code)
                metadata['scalers_X'][stock_code] = scaler_X
                metadata['scalers_y'][stock_code] = scaler_y

                if metadata['feature_columns'] is None:
                    metadata['feature_columns'] = feature_cols

        if not all_X:
            print("❌ No data collected")
            return None, None, None

        # Combine all data
        X_combined = np.concatenate(all_X, axis=0)
        y_combined = np.concatenate(all_y, axis=0)

        print(f"\n✓ Training data prepared:")
        print(f"  - Total sequences: {len(X_combined)}")
        print(f"  - Input shape: {X_combined.shape}")
        print(f"  - Output shape: {y_combined.shape}")
        print(f"  - Stocks: {', '.join(metadata['stocks'])}")

        return X_combined, y_combined, metadata


# Example usage
if __name__ == "__main__":
    collector = StockDataCollector()

    # Collect data for top 5 stocks
    stock_codes = ["BBCA", "BBRI", "TLKM", "ASII", "BMRI"]

    print("="*60)
    print("STOCK DATA COLLECTION FOR LSTM TRAINING")
    print("="*60)

    X_train, y_train, metadata = collector.prepare_training_data(
        stock_codes=stock_codes,
        period="2y",
        sequence_length=60
    )

    if X_train is not None:
        print("\n✓ Data collection successful!")
        print(f"Ready for LSTM training with {len(X_train)} samples")
    else:
        print("\n❌ Data collection failed")

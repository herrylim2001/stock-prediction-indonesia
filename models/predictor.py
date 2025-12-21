"""
Stock Price Predictor - Inference Module
Load trained LSTM model and make real-time predictions
"""
import numpy as np
import pandas as pd
import os
import joblib
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Check if TensorFlow is available
try:
    from tensorflow import keras
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    print("⚠️ TensorFlow not installed. Using mock predictions.")


class StockPredictor:
    """Make stock predictions using trained LSTM model"""

    def __init__(self, model_path='models/saved/stock_lstm_model.keras',
                 metadata_path='models/saved/training_metadata.pkl'):
        """
        Initialize predictor

        Args:
            model_path: Path to trained model
            metadata_path: Path to training metadata
        """
        self.model = None
        self.metadata = None
        self.scalers_X = {}
        self.scalers_y = {}
        self.feature_columns = []
        self.sequence_length = 60
        self.model_loaded = False

        # Try to load model
        if TENSORFLOW_AVAILABLE and os.path.exists(model_path) and os.path.exists(metadata_path):
            try:
                self.load_model(model_path, metadata_path)
                self.model_loaded = True
                print("✓ LSTM model loaded successfully!")
            except Exception as e:
                print(f"⚠️ Could not load model: {e}")
                print("⚠️ Using mock predictions instead.")
        else:
            if not TENSORFLOW_AVAILABLE:
                print("⚠️ TensorFlow not available. Install with: pip install tensorflow")
            else:
                print(f"⚠️ Model files not found:")
                print(f"  - Model: {model_path}")
                print(f"  - Metadata: {metadata_path}")
            print("⚠️ Using mock predictions. Train model first with:")
            print("   python models/train_model.py")

    def load_model(self, model_path, metadata_path):
        """Load trained model and metadata"""
        # Load model
        self.model = keras.models.load_model(model_path)

        # Load metadata
        self.metadata = joblib.load(metadata_path)
        self.scalers_X = self.metadata.get('scalers_X', {})
        self.scalers_y = self.metadata.get('scalers_y', {})
        self.feature_columns = self.metadata.get('feature_columns', [])
        self.sequence_length = self.metadata.get('sequence_length', 60)

        print(f"Model info:")
        print(f"  - Sequence length: {self.sequence_length}")
        print(f"  - Features: {len(self.feature_columns)}")
        print(f"  - Stocks trained: {', '.join(self.metadata.get('stocks', []))}")

    def prepare_input_data(self, df, stock_code):
        """
        Prepare input data for prediction

        Args:
            df: DataFrame with OHLCV and technical indicators
            stock_code: Stock code for getting correct scaler

        Returns:
            Prepared input array for model
        """
        if df is None or len(df) < self.sequence_length:
            return None

        # Get features in same order as training
        try:
            X = df[self.feature_columns].values
        except KeyError:
            print(f"⚠️ Missing features in data")
            return None

        # Handle NaN values
        if np.isnan(X).any():
            X = pd.DataFrame(X).fillna(method='ffill').fillna(method='bfill').values

        # Scale data
        scaler_X = self.scalers_X.get(stock_code)
        if scaler_X is None:
            # Use scaler from first available stock
            scaler_X = list(self.scalers_X.values())[0] if self.scalers_X else None

        if scaler_X:
            X_scaled = scaler_X.transform(X)
        else:
            # Simple min-max scaling as fallback
            X_scaled = (X - X.min(axis=0)) / (X.max(axis=0) - X.min(axis=0) + 1e-8)

        # Get last sequence
        if len(X_scaled) >= self.sequence_length:
            X_sequence = X_scaled[-self.sequence_length:]
            return np.expand_dims(X_sequence, axis=0)  # Add batch dimension

        return None

    def predict_price(self, df, stock_code, current_price):
        """
        Predict future price

        Args:
            df: DataFrame with historical data and indicators
            stock_code: Stock code
            current_price: Current price

        Returns:
            dict with predictions
        """
        # If model not loaded, use mock predictions
        if not self.model_loaded or self.model is None:
            return self._mock_predictions(current_price)

        # Prepare input
        X_input = self.prepare_input_data(df, stock_code)

        if X_input is None:
            return self._mock_predictions(current_price)

        try:
            # Make prediction
            prediction_scaled = self.model.predict(X_input, verbose=0)

            # Inverse transform
            scaler_y = self.scalers_y.get(stock_code)
            if scaler_y is None:
                scaler_y = list(self.scalers_y.values())[0] if self.scalers_y else None

            if scaler_y:
                predicted_price = scaler_y.inverse_transform(prediction_scaled)[0][0]
            else:
                # Fallback: use percentage change
                predicted_price = current_price * (1 + prediction_scaled[0][0])

            # Calculate confidence based on recent volatility
            if len(df) > 20:
                volatility = df['close'].pct_change().tail(20).std()
                confidence = max(0.5, min(0.95, 1 - (volatility * 5)))
            else:
                confidence = 0.65

            # Determine trend
            price_change_pct = ((predicted_price - current_price) / current_price) * 100

            if price_change_pct > 1:
                trend = "UP"
            elif price_change_pct < -1:
                trend = "DOWN"
            else:
                trend = "NEUTRAL"

            return {
                "1d": {
                    "price": float(predicted_price),
                    "confidence": float(confidence),
                    "trend": trend,
                    "change_pct": float(price_change_pct),
                    "model_used": "LSTM"
                }
            }

        except Exception as e:
            print(f"⚠️ Prediction error: {e}")
            return self._mock_predictions(current_price)

    def predict_multiple_horizons(self, df, stock_code, current_price):
        """
        Predict multiple time horizons (1h, 3h, 1d)

        Note: Current model predicts 1d. For multiple horizons,
        either train separate models or use extrapolation.

        Args:
            df: DataFrame with historical data
            stock_code: Stock code
            current_price: Current price

        Returns:
            dict with predictions for multiple horizons
        """
        # Get 1-day prediction
        pred_1d = self.predict_price(df, stock_code, current_price)

        # Extrapolate for shorter horizons (simplified)
        if self.model_loaded and "1d" in pred_1d:
            change_1d = pred_1d["1d"]["change_pct"]

            # 1-hour: ~1/7 of daily change
            pred_1h = {
                "price": current_price * (1 + (change_1d / 700)),
                "confidence": pred_1d["1d"]["confidence"] * 0.9,
                "trend": pred_1d["1d"]["trend"],
                "change_pct": change_1d / 7,
                "model_used": "LSTM (extrapolated)"
            }

            # 3-hour: ~3/7 of daily change
            pred_3h = {
                "price": current_price * (1 + (change_1d / 700) * 3),
                "confidence": pred_1d["1d"]["confidence"] * 0.85,
                "trend": pred_1d["1d"]["trend"],
                "change_pct": (change_1d / 7) * 3,
                "model_used": "LSTM (extrapolated)"
            }

            return {
                "1h": pred_1h,
                "3h": pred_3h,
                "1d": pred_1d["1d"],
                "3d": {  # 3-day: extrapolate from 1-day
                    "price": current_price * (1 + (change_1d / 100) * 3 * 0.8),
                    "confidence": pred_1d["1d"]["confidence"] * 0.75,
                    "trend": pred_1d["1d"]["trend"],
                    "change_pct": change_1d * 3 * 0.8,
                    "model_used": "LSTM (extrapolated)"
                }
            }
        else:
            # Fallback to mock
            return self._mock_predictions(current_price)

    def _mock_predictions(self, current_price, volatility=0.02):
        """Generate mock predictions when model not available"""
        trend = np.random.choice([-1, 0, 1], p=[0.3, 0.2, 0.5])

        # Calculate price changes
        change_1h = np.random.normal(0.001 * trend, volatility * 0.3)
        change_3h = np.random.normal(0.003 * trend, volatility * 0.5)
        change_1d = np.random.normal(0.01 * trend, volatility)
        change_3d = np.random.normal(0.03 * trend, volatility * 1.5)

        return {
            "1h": {
                "price": current_price * (1 + change_1h),
                "confidence": np.random.uniform(0.65, 0.75),
                "trend": "UP" if trend > 0 else "DOWN" if trend < 0 else "NEUTRAL",
                "change_pct": change_1h * 100,
                "model_used": "Mock (model not loaded)"
            },
            "3h": {
                "price": current_price * (1 + change_3h),
                "confidence": np.random.uniform(0.63, 0.73),
                "trend": "UP" if trend > 0 else "DOWN" if trend < 0 else "NEUTRAL",
                "change_pct": change_3h * 100,
                "model_used": "Mock (model not loaded)"
            },
            "1d": {
                "price": current_price * (1 + change_1d),
                "confidence": np.random.uniform(0.68, 0.78),
                "trend": "UP" if trend > 0 else "DOWN" if trend < 0 else "NEUTRAL",
                "change_pct": change_1d * 100,
                "model_used": "Mock (model not loaded)"
            },
            "3d": {
                "price": current_price * (1 + change_3d),
                "confidence": np.random.uniform(0.60, 0.72),
                "trend": "UP" if trend > 0 else "DOWN" if trend < 0 else "NEUTRAL",
                "change_pct": change_3d * 100,
                "model_used": "Mock (model not loaded)"
            }
        }

    def is_model_loaded(self):
        """Check if real model is loaded"""
        return self.model_loaded


# Singleton instance
_predictor_instance = None

def get_predictor():
    """Get or create predictor instance"""
    global _predictor_instance
    if _predictor_instance is None:
        _predictor_instance = StockPredictor()
    return _predictor_instance


# Example usage
if __name__ == "__main__":
    print("="*60)
    print("STOCK PREDICTOR TEST")
    print("="*60)

    predictor = StockPredictor()

    print(f"\nModel loaded: {predictor.is_model_loaded()}")

    # Test with dummy data
    current_price = 9500
    predictions = predictor._mock_predictions(current_price)

    print(f"\nTest predictions for price {current_price}:")
    for horizon, pred in predictions.items():
        print(f"{horizon}: {pred['price']:.0f} ({pred['trend']}) - "
              f"Confidence: {pred['confidence']:.2%} - {pred.get('model_used', 'N/A')}")

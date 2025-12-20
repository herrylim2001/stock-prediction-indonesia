"""
LSTM Model for Stock Price Prediction
Multi-output predictions: 1h, 3h, 1d
"""
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, Model
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
import joblib
import os


class StockLSTMModel:
    """LSTM Model for stock prediction"""

    def __init__(self, sequence_length=60, n_features=30):
        """
        Initialize LSTM model

        Args:
            sequence_length: Number of timesteps to look back
            n_features: Number of input features
        """
        self.sequence_length = sequence_length
        self.n_features = n_features
        self.model = None
        self.history = None

    def build_model(self, n_outputs=1):
        """
        Build LSTM architecture

        Args:
            n_outputs: Number of output predictions (1 for single, 3 for 1h/3h/1d)

        Returns:
            Compiled Keras model
        """
        print("Building LSTM model...")

        # Input layer
        inputs = layers.Input(shape=(self.sequence_length, self.n_features))

        # LSTM layers with dropout
        x = layers.LSTM(128, return_sequences=True)(inputs)
        x = layers.Dropout(0.2)(x)

        x = layers.LSTM(64, return_sequences=True)(x)
        x = layers.Dropout(0.2)(x)

        x = layers.LSTM(32, return_sequences=False)(x)
        x = layers.Dropout(0.2)(x)

        # Dense layers
        x = layers.Dense(16, activation='relu')(x)
        x = layers.Dropout(0.1)(x)

        # Output layer
        outputs = layers.Dense(n_outputs, activation='linear')(x)

        # Create model
        model = Model(inputs=inputs, outputs=outputs, name="StockLSTM")

        # Compile
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae', 'mape']
        )

        print(f"✓ Model built with {model.count_params():,} parameters")
        model.summary()

        self.model = model
        return model

    def train(self, X_train, y_train, X_val=None, y_val=None,
              epochs=100, batch_size=32, verbose=1):
        """
        Train the model

        Args:
            X_train: Training sequences
            y_train: Training targets
            X_val: Validation sequences
            y_val: Validation targets
            epochs: Number of epochs
            batch_size: Batch size
            verbose: Verbosity level

        Returns:
            Training history
        """
        if self.model is None:
            self.build_model(n_outputs=y_train.shape[1] if len(y_train.shape) > 1 else 1)

        # Callbacks
        callbacks = [
            EarlyStopping(
                monitor='val_loss' if X_val is not None else 'loss',
                patience=15,
                restore_best_weights=True,
                verbose=1
            ),
            ReduceLROnPlateau(
                monitor='val_loss' if X_val is not None else 'loss',
                factor=0.5,
                patience=5,
                min_lr=0.00001,
                verbose=1
            ),
            ModelCheckpoint(
                filepath='models/checkpoints/lstm_best.keras',
                monitor='val_loss' if X_val is not None else 'loss',
                save_best_only=True,
                verbose=1
            )
        ]

        # Create checkpoint directory
        os.makedirs('models/checkpoints', exist_ok=True)

        print("\nStarting training...")
        print(f"Training samples: {len(X_train)}")
        if X_val is not None:
            print(f"Validation samples: {len(X_val)}")
        print(f"Epochs: {epochs}, Batch size: {batch_size}")
        print("=" * 60)

        # Train
        history = self.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val) if X_val is not None else None,
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks,
            verbose=verbose
        )

        self.history = history
        print("\n✓ Training completed!")

        return history

    def predict(self, X):
        """Make predictions"""
        if self.model is None:
            raise ValueError("Model not built or loaded")

        return self.model.predict(X, verbose=0)

    def evaluate(self, X_test, y_test):
        """Evaluate model performance"""
        if self.model is None:
            raise ValueError("Model not built or loaded")

        print("\nEvaluating model...")
        results = self.model.evaluate(X_test, y_test, verbose=0)

        metrics = {}
        for name, value in zip(self.model.metrics_names, results):
            metrics[name] = value
            print(f"{name}: {value:.4f}")

        return metrics

    def save(self, filepath='models/stock_lstm_model.keras', save_metadata=True):
        """Save model and metadata"""
        if self.model is None:
            raise ValueError("No model to save")

        print(f"\nSaving model to {filepath}...")

        # Save model
        self.model.save(filepath)

        # Save metadata
        if save_metadata:
            metadata = {
                'sequence_length': self.sequence_length,
                'n_features': self.n_features,
                'history': self.history.history if self.history else None
            }
            metadata_path = filepath.replace('.keras', '_metadata.pkl')
            joblib.dump(metadata, metadata_path)
            print(f"✓ Metadata saved to {metadata_path}")

        print(f"✓ Model saved successfully!")

    def load(self, filepath='models/stock_lstm_model.keras'):
        """Load saved model"""
        print(f"Loading model from {filepath}...")

        self.model = keras.models.load_model(filepath)

        # Load metadata if available
        metadata_path = filepath.replace('.keras', '_metadata.pkl')
        if os.path.exists(metadata_path):
            metadata = joblib.dump(metadata_path)
            self.sequence_length = metadata.get('sequence_length', 60)
            self.n_features = metadata.get('n_features', 30)
            print(f"✓ Metadata loaded")

        print(f"✓ Model loaded successfully!")

    def get_feature_importance(self, X_sample, feature_names):
        """
        Analyze feature importance using gradients

        Args:
            X_sample: Sample input
            feature_names: List of feature names

        Returns:
            DataFrame with feature importance scores
        """
        import pandas as pd

        # This is a simplified version - for production, use SHAP or similar
        predictions = self.predict(X_sample)
        importance_scores = np.abs(X_sample[:, -1, :]).mean(axis=0)

        importance_df = pd.DataFrame({
            'feature': feature_names,
            'importance': importance_scores
        }).sort_values('importance', ascending=False)

        return importance_df


# Example usage
if __name__ == "__main__":
    print("="*60)
    print("LSTM MODEL ARCHITECTURE TEST")
    print("="*60)

    # Create dummy data
    sequence_length = 60
    n_features = 30
    n_samples = 1000

    X_dummy = np.random.randn(n_samples, sequence_length, n_features)
    y_dummy = np.random.randn(n_samples, 1)

    # Initialize and build model
    lstm_model = StockLSTMModel(sequence_length=sequence_length, n_features=n_features)
    lstm_model.build_model(n_outputs=1)

    print("\n✓ Model architecture created successfully!")
    print(f"Input shape: (batch_size, {sequence_length}, {n_features})")
    print(f"Output shape: (batch_size, 1)")

    # Quick test
    print("\nTesting prediction...")
    test_pred = lstm_model.predict(X_dummy[:5])
    print(f"✓ Prediction successful! Output shape: {test_pred.shape}")

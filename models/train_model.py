"""
LSTM Model Training Script
Train stock prediction model with historical data
"""
import numpy as np
import sys
import os
from sklearn.model_selection import train_test_split
import joblib

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.data_collector import StockDataCollector
from models.lstm_model import StockLSTMModel


def train_stock_prediction_model(
    stock_codes=None,
    period="2y",
    sequence_length=60,
    epochs=100,
    batch_size=32,
    validation_split=0.2
):
    """
    Main training function

    Args:
        stock_codes: List of stock codes to train on
        period: Historical data period
        sequence_length: LSTM sequence length
        epochs: Number of training epochs
        batch_size: Training batch size
        validation_split: Validation data split ratio

    Returns:
        Trained model, metadata, history
    """
    print("="*70)
    print("  LSTM STOCK PREDICTION MODEL TRAINING")
    print("="*70)

    # Default stocks if not specified
    if stock_codes is None:
        stock_codes = ["BBCA", "BBRI", "TLKM", "ASII", "BMRI", "UNVR"]

    print(f"\nConfiguration:")
    print(f"  Stocks: {', '.join(stock_codes)}")
    print(f"  Period: {period}")
    print(f"  Sequence length: {sequence_length}")
    print(f"  Epochs: {epochs}")
    print(f"  Batch size: {batch_size}")
    print(f"  Validation split: {validation_split*100}%")
    print("="*70)

    # Step 1: Collect and prepare data
    print("\n📊 STEP 1: Collecting historical data...")
    print("-"*70)

    collector = StockDataCollector()
    X, y, metadata = collector.prepare_training_data(
        stock_codes=stock_codes,
        period=period,
        sequence_length=sequence_length
    )

    if X is None:
        print("\n❌ Data collection failed. Aborting training.")
        return None, None, None

    # Step 2: Split data
    print("\n📊 STEP 2: Splitting data...")
    print("-"*70)

    X_train, X_val, y_train, y_val = train_test_split(
        X, y,
        test_size=validation_split,
        shuffle=True,
        random_state=42
    )

    print(f"Training set: {len(X_train)} samples")
    print(f"Validation set: {len(X_val)} samples")

    # Step 3: Build and train model
    print("\n🤖 STEP 3: Building LSTM model...")
    print("-"*70)

    n_features = X_train.shape[2]
    n_outputs = y_train.shape[1] if len(y_train.shape) > 1 else 1

    lstm_model = StockLSTMModel(
        sequence_length=sequence_length,
        n_features=n_features
    )

    lstm_model.build_model(n_outputs=n_outputs)

    # Step 4: Train
    print("\n🚀 STEP 4: Training model...")
    print("-"*70)

    history = lstm_model.train(
        X_train=X_train,
        y_train=y_train,
        X_val=X_val,
        y_val=y_val,
        epochs=epochs,
        batch_size=batch_size,
        verbose=1
    )

    # Step 5: Evaluate
    print("\n📊 STEP 5: Evaluating model...")
    print("-"*70)

    metrics = lstm_model.evaluate(X_val, y_val)

    # Step 6: Save model
    print("\n💾 STEP 6: Saving model...")
    print("-"*70)

    os.makedirs('models/saved', exist_ok=True)

    model_path = 'models/saved/stock_lstm_model.keras'
    lstm_model.save(model_path, save_metadata=True)

    # Save scalers and metadata
    metadata_path = 'models/saved/training_metadata.pkl'
    joblib.dump(metadata, metadata_path)
    print(f"✓ Training metadata saved to {metadata_path}")

    # Training summary
    print("\n" + "="*70)
    print("  TRAINING COMPLETED!")
    print("="*70)
    print(f"\nModel Performance:")
    for metric_name, metric_value in metrics.items():
        print(f"  {metric_name}: {metric_value:.4f}")

    print(f"\nSaved Files:")
    print(f"  - Model: {model_path}")
    print(f"  - Metadata: {metadata_path}")
    print(f"  - Best checkpoint: models/checkpoints/lstm_best.keras")

    print("\n✓ Model is ready for predictions!")
    print("="*70)

    return lstm_model, metadata, history


def quick_test_prediction(model_path='models/saved/stock_lstm_model.keras',
                          metadata_path='models/saved/training_metadata.pkl'):
    """
    Quick test to verify model can make predictions

    Args:
        model_path: Path to saved model
        metadata_path: Path to metadata file
    """
    print("\n" + "="*70)
    print("  TESTING TRAINED MODEL")
    print("="*70)

    # Load model
    lstm_model = StockLSTMModel()
    lstm_model.load(model_path)

    # Load metadata
    metadata = joblib.load(metadata_path)
    sequence_length = metadata['sequence_length']
    n_features = len(metadata['feature_columns'])

    # Create dummy input
    dummy_input = np.random.randn(1, sequence_length, n_features)

    # Make prediction
    prediction = lstm_model.predict(dummy_input)

    print(f"\n✓ Model loaded successfully!")
    print(f"Input shape: {dummy_input.shape}")
    print(f"Output shape: {prediction.shape}")
    print(f"Sample prediction: {prediction[0]}")
    print("\n✓ Model is working correctly!")
    print("="*70)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Train LSTM stock prediction model')
    parser.add_argument('--stocks', nargs='+', default=None,
                       help='Stock codes to train on')
    parser.add_argument('--period', type=str, default='2y',
                       help='Historical data period (default: 2y)')
    parser.add_argument('--epochs', type=int, default=100,
                       help='Number of epochs (default: 100)')
    parser.add_argument('--batch-size', type=int, default=32,
                       help='Batch size (default: 32)')
    parser.add_argument('--test', action='store_true',
                       help='Test trained model')

    args = parser.parse_args()

    if args.test:
        # Test mode
        quick_test_prediction()
    else:
        # Training mode
        model, metadata, history = train_stock_prediction_model(
            stock_codes=args.stocks,
            period=args.period,
            epochs=args.epochs,
            batch_size=args.batch_size
        )

        if model is not None:
            print("\n💡 To test the model, run:")
            print("   python models/train_model.py --test")

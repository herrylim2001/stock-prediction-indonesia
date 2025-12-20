"""
Quick Training Visualization Script
Run this after training to see comprehensive visualizations
"""
import sys
import os

# Add parent directory to path
if '/content/stock-prediction-indonesia' not in sys.path:
    sys.path.append('/content/stock-prediction-indonesia')

print("="*70)
print("  LSTM TRAINING RESULTS VISUALIZATION")
print("="*70)

# Install visualization dependencies
print("\n📦 Installing matplotlib and seaborn...")
os.system("pip install -q matplotlib seaborn")

import matplotlib.pyplot as plt
import numpy as np
import joblib
from models.visualizer import TrainingVisualizer
from models.lstm_model import StockLSTMModel
from models.data_collector import StockDataCollector
from sklearn.model_selection import train_test_split

print("✓ Visualization tools loaded!\n")

# Initialize visualizer
viz = TrainingVisualizer(
    model_path='models/saved/stock_lstm_model.keras',
    metadata_path='models/saved/training_metadata.pkl'
)

# ============================================================================
# 1. TRAINING HISTORY
# ============================================================================
print("\n📊 1. Plotting Training History...")
print("-"*70)
try:
    viz.plot_training_history(save_path='training_history.png')
    print("✓ Training history plot saved!")
except Exception as e:
    print(f"⚠️ Could not plot training history: {e}")

# ============================================================================
# 2. PREPARE TEST DATA
# ============================================================================
print("\n📊 2. Preparing Test Data...")
print("-"*70)

try:
    # Load model and metadata
    model = StockLSTMModel()
    model.load('models/saved/stock_lstm_model.keras')

    metadata = joblib.load('models/saved/training_metadata.pkl')

    # Collect some test data
    collector = StockDataCollector()
    stock_code = 'BBCA'

    print(f"Fetching test data for {stock_code}...")
    df = collector.fetch_historical_data(stock_code, period='6mo')
    df = collector.add_technical_indicators(df)

    # Prepare sequences
    X, y, _, _, _ = collector.create_sequences(df, sequence_length=60)

    if X is not None and len(X) > 0:
        # Split for visualization
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, shuffle=False
        )

        print(f"✓ Test data ready: {len(X_test)} samples")

        # ====================================================================
        # 3. PREDICTIONS VS ACTUAL
        # ====================================================================
        print("\n📊 3. Plotting Predictions vs Actual...")
        print("-"*70)

        r2 = viz.plot_predictions_vs_actual(
            X_test, y_test, model.model,
            n_samples=min(100, len(X_test)),
            save_path='predictions_vs_actual.png'
        )
        print(f"✓ R² Score: {r2:.4f}")

        # ====================================================================
        # 4. ERROR DISTRIBUTION
        # ====================================================================
        print("\n📊 4. Plotting Error Distribution...")
        print("-"*70)

        viz.plot_error_distribution(
            X_test, y_test, model.model,
            save_path='error_distribution.png'
        )
        print("✓ Error distribution plotted!")

        # ====================================================================
        # 5. FEATURE IMPORTANCE
        # ====================================================================
        print("\n📊 5. Plotting Feature Importance...")
        print("-"*70)

        feature_names = metadata.get('feature_columns', [])
        if feature_names:
            viz.plot_feature_importance(
                feature_names,
                save_path='feature_importance.png'
            )
            print("✓ Feature importance plotted!")
        else:
            print("⚠️ No feature names found in metadata")

        # ====================================================================
        # 6. COMPREHENSIVE DASHBOARD
        # ====================================================================
        print("\n📊 6. Creating Performance Dashboard...")
        print("-"*70)

        viz.create_performance_dashboard(
            X_test, y_test, model.model,
            save_path='performance_dashboard.png'
        )
        print("✓ Performance dashboard created!")

        # ====================================================================
        # 7. DOWNLOAD ALL VISUALIZATIONS
        # ====================================================================
        print("\n💾 Creating visualization package...")
        print("-"*70)

        os.system("zip -q visualizations.zip *.png")

        print("\n✓ All visualizations saved!")
        print("\nGenerated files:")
        print("  1. training_history.png")
        print("  2. predictions_vs_actual.png")
        print("  3. error_distribution.png")
        print("  4. feature_importance.png")
        print("  5. performance_dashboard.png")
        print("  6. visualizations.zip (all above)")

        print("\n💡 To download visualizations:")
        print("  - Run the download cell below")
        print("  - Or find visualizations.zip in the file browser")

    else:
        print("❌ Could not create test sequences")

except Exception as e:
    print(f"❌ Error during visualization: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
print("  VISUALIZATION COMPLETE!")
print("="*70)
print("\n✓ Check the plots above and download visualization files")
print("✓ All visualizations are also saved as PNG files")

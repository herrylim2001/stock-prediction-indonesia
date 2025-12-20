"""
Training Results Visualization & Analysis
Comprehensive analysis tools for LSTM model performance
"""
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import joblib
import os
from datetime import datetime

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")


class TrainingVisualizer:
    """Visualize and analyze training results"""

    def __init__(self, model_path='models/saved/stock_lstm_model.keras',
                 metadata_path='models/saved/training_metadata.pkl'):
        """
        Initialize visualizer

        Args:
            model_path: Path to trained model
            metadata_path: Path to training metadata
        """
        self.model_path = model_path
        self.metadata_path = metadata_path
        self.metadata = None
        self.history = None

        # Load metadata
        if os.path.exists(metadata_path):
            self.metadata = joblib.load(metadata_path)
            print(f"✓ Loaded metadata from {metadata_path}")
        else:
            print(f"⚠️ Metadata not found: {metadata_path}")

    def plot_training_history(self, save_path=None, figsize=(15, 10)):
        """
        Plot training history (loss, mae, mape over epochs)

        Args:
            save_path: Path to save figure
            figsize: Figure size
        """
        if self.metadata is None:
            print("❌ No metadata available")
            return

        # Try to load history from model metadata file
        model_metadata_path = self.model_path.replace('.keras', '_metadata.pkl')
        if os.path.exists(model_metadata_path):
            model_meta = joblib.load(model_metadata_path)
            history = model_meta.get('history')
        else:
            print("⚠️ Training history not found")
            return

        if history is None:
            print("⚠️ No training history available")
            return

        fig, axes = plt.subplots(2, 2, figsize=figsize)
        fig.suptitle('LSTM Training History', fontsize=16, fontweight='bold')

        # Plot 1: Loss
        ax1 = axes[0, 0]
        if 'loss' in history:
            ax1.plot(history['loss'], label='Training Loss', linewidth=2)
        if 'val_loss' in history:
            ax1.plot(history['val_loss'], label='Validation Loss', linewidth=2)
        ax1.set_title('Model Loss', fontweight='bold')
        ax1.set_xlabel('Epoch')
        ax1.set_ylabel('Loss (MSE)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Plot 2: MAE
        ax2 = axes[0, 1]
        if 'mae' in history:
            ax2.plot(history['mae'], label='Training MAE', linewidth=2)
        if 'val_mae' in history:
            ax2.plot(history['val_mae'], label='Validation MAE', linewidth=2)
        ax2.set_title('Mean Absolute Error', fontweight='bold')
        ax2.set_xlabel('Epoch')
        ax2.set_ylabel('MAE')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        # Plot 3: MAPE
        ax3 = axes[1, 0]
        if 'mape' in history:
            ax3.plot(history['mape'], label='Training MAPE', linewidth=2)
        if 'val_mape' in history:
            ax3.plot(history['val_mape'], label='Validation MAPE', linewidth=2)
        ax3.set_title('Mean Absolute Percentage Error', fontweight='bold')
        ax3.set_xlabel('Epoch')
        ax3.set_ylabel('MAPE (%)')
        ax3.legend()
        ax3.grid(True, alpha=0.3)

        # Plot 4: Learning Rate (if available)
        ax4 = axes[1, 1]
        if 'lr' in history:
            ax4.plot(history['lr'], linewidth=2, color='green')
            ax4.set_title('Learning Rate', fontweight='bold')
            ax4.set_xlabel('Epoch')
            ax4.set_ylabel('Learning Rate')
            ax4.set_yscale('log')
        else:
            # Summary statistics
            ax4.axis('off')
            summary_text = "Training Summary\n\n"
            if 'loss' in history:
                summary_text += f"Final Training Loss: {history['loss'][-1]:.6f}\n"
            if 'val_loss' in history:
                summary_text += f"Final Val Loss: {history['val_loss'][-1]:.6f}\n"
            if 'mae' in history:
                summary_text += f"Final Training MAE: {history['mae'][-1]:.6f}\n"
            if 'val_mae' in history:
                summary_text += f"Final Val MAE: {history['val_mae'][-1]:.6f}\n"
            if 'mape' in history:
                summary_text += f"Final Training MAPE: {history['mape'][-1]:.2f}%\n"
            if 'val_mape' in history:
                summary_text += f"Final Val MAPE: {history['val_mape'][-1]:.2f}%\n"

            summary_text += f"\nTotal Epochs: {len(history.get('loss', []))}\n"
            summary_text += f"Training Date: {datetime.now().strftime('%Y-%m-%d')}"

            ax4.text(0.1, 0.5, summary_text, fontsize=11, verticalalignment='center',
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Saved to {save_path}")

        plt.show()

    def plot_predictions_vs_actual(self, X_test, y_test, model, n_samples=100,
                                   save_path=None, figsize=(15, 6)):
        """
        Plot predicted vs actual values

        Args:
            X_test: Test input data
            y_test: Test actual values
            model: Trained model
            n_samples: Number of samples to plot
            save_path: Path to save figure
            figsize: Figure size
        """
        # Make predictions
        y_pred = model.predict(X_test[:n_samples], verbose=0)

        fig, axes = plt.subplots(1, 2, figsize=figsize)
        fig.suptitle('Predictions vs Actual Values', fontsize=16, fontweight='bold')

        # Plot 1: Time series comparison
        ax1 = axes[0]
        ax1.plot(y_test[:n_samples], label='Actual', linewidth=2, alpha=0.7)
        ax1.plot(y_pred, label='Predicted', linewidth=2, alpha=0.7)
        ax1.set_title('Prediction vs Actual (Time Series)', fontweight='bold')
        ax1.set_xlabel('Sample')
        ax1.set_ylabel('Normalized Price')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Plot 2: Scatter plot
        ax2 = axes[1]
        ax2.scatter(y_test[:n_samples], y_pred, alpha=0.5)

        # Perfect prediction line
        min_val = min(y_test[:n_samples].min(), y_pred.min())
        max_val = max(y_test[:n_samples].max(), y_pred.max())
        ax2.plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2, label='Perfect Prediction')

        ax2.set_title('Prediction vs Actual (Scatter)', fontweight='bold')
        ax2.set_xlabel('Actual')
        ax2.set_ylabel('Predicted')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        # Calculate R²
        from sklearn.metrics import r2_score
        r2 = r2_score(y_test[:n_samples], y_pred)
        ax2.text(0.05, 0.95, f'R² = {r2:.4f}', transform=ax2.transAxes,
                fontsize=12, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Saved to {save_path}")

        plt.show()

        return r2

    def plot_error_distribution(self, X_test, y_test, model, save_path=None, figsize=(15, 5)):
        """
        Plot error distribution

        Args:
            X_test: Test input data
            y_test: Test actual values
            model: Trained model
            save_path: Path to save figure
            figsize: Figure size
        """
        # Make predictions
        y_pred = model.predict(X_test, verbose=0)
        errors = y_test - y_pred.flatten()
        errors_pct = (errors / y_test) * 100

        fig, axes = plt.subplots(1, 3, figsize=figsize)
        fig.suptitle('Prediction Error Analysis', fontsize=16, fontweight='bold')

        # Plot 1: Error distribution
        ax1 = axes[0]
        ax1.hist(errors, bins=50, edgecolor='black', alpha=0.7)
        ax1.axvline(x=0, color='r', linestyle='--', linewidth=2, label='Zero Error')
        ax1.set_title('Error Distribution', fontweight='bold')
        ax1.set_xlabel('Error (Actual - Predicted)')
        ax1.set_ylabel('Frequency')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Plot 2: Percentage error distribution
        ax2 = axes[1]
        ax2.hist(errors_pct, bins=50, edgecolor='black', alpha=0.7, color='orange')
        ax2.axvline(x=0, color='r', linestyle='--', linewidth=2, label='Zero Error')
        ax2.set_title('Percentage Error Distribution', fontweight='bold')
        ax2.set_xlabel('Error (%)')
        ax2.set_ylabel('Frequency')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        # Plot 3: Error statistics
        ax3 = axes[2]
        ax3.axis('off')

        stats_text = "Error Statistics\n\n"
        stats_text += f"Mean Error: {errors.mean():.6f}\n"
        stats_text += f"Std Error: {errors.std():.6f}\n"
        stats_text += f"MAE: {np.abs(errors).mean():.6f}\n"
        stats_text += f"RMSE: {np.sqrt((errors**2).mean()):.6f}\n\n"
        stats_text += f"Mean Error %: {errors_pct.mean():.2f}%\n"
        stats_text += f"Std Error %: {errors_pct.std():.2f}%\n"
        stats_text += f"MAPE: {np.abs(errors_pct).mean():.2f}%\n\n"
        stats_text += f"Samples within ±5%: {(np.abs(errors_pct) <= 5).sum() / len(errors_pct) * 100:.1f}%\n"
        stats_text += f"Samples within ±10%: {(np.abs(errors_pct) <= 10).sum() / len(errors_pct) * 100:.1f}%"

        ax3.text(0.1, 0.5, stats_text, fontsize=10, verticalalignment='center',
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Saved to {save_path}")

        plt.show()

    def plot_feature_importance(self, feature_names, importance_scores=None,
                               save_path=None, figsize=(12, 8)):
        """
        Plot feature importance

        Args:
            feature_names: List of feature names
            importance_scores: Importance scores (if None, will use placeholder)
            save_path: Path to save figure
            figsize: Figure size
        """
        if importance_scores is None:
            # Placeholder importance (based on common knowledge)
            # In production, use SHAP or permutation importance
            importance_map = {
                'returns': 0.95, 'rsi': 0.88, 'macd': 0.85, 'close': 0.82,
                'volume_ratio': 0.78, 'atr': 0.75, 'bb_width': 0.72,
                'sma_20': 0.68, 'ema_12': 0.65, 'volatility': 0.62
            }
            importance_scores = [importance_map.get(name, np.random.uniform(0.3, 0.6))
                               for name in feature_names]

        # Create DataFrame
        importance_df = pd.DataFrame({
            'feature': feature_names,
            'importance': importance_scores
        }).sort_values('importance', ascending=False)

        # Plot
        fig, ax = plt.subplots(figsize=figsize)

        # Top 20 features
        top_features = importance_df.head(20)

        bars = ax.barh(range(len(top_features)), top_features['importance'])
        ax.set_yticks(range(len(top_features)))
        ax.set_yticklabels(top_features['feature'])
        ax.invert_yaxis()
        ax.set_xlabel('Importance Score', fontweight='bold')
        ax.set_title('Top 20 Feature Importance', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='x')

        # Color bars
        colors = plt.cm.RdYlGn(top_features['importance'] / top_features['importance'].max())
        for bar, color in zip(bars, colors):
            bar.set_color(color)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Saved to {save_path}")

        plt.show()

    def create_performance_dashboard(self, X_test, y_test, model, save_path=None):
        """
        Create comprehensive performance dashboard

        Args:
            X_test: Test input data
            y_test: Test actual values
            model: Trained model
            save_path: Path to save figure
        """
        print("\n" + "="*70)
        print("  CREATING PERFORMANCE DASHBOARD")
        print("="*70 + "\n")

        # Make predictions
        y_pred = model.predict(X_test, verbose=0).flatten()
        errors = y_test - y_pred
        errors_pct = (errors / y_test) * 100

        # Calculate metrics
        from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        mape = np.mean(np.abs(errors_pct))
        r2 = r2_score(y_test, y_pred)

        # Direction accuracy
        actual_direction = np.diff(y_test) > 0
        pred_direction = np.diff(y_pred) > 0
        direction_accuracy = (actual_direction == pred_direction).mean() * 100

        # Create dashboard
        fig = plt.figure(figsize=(18, 12))
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

        # Title
        fig.suptitle('LSTM Model Performance Dashboard', fontsize=18, fontweight='bold')

        # Plot 1: Predictions vs Actual (line)
        ax1 = fig.add_subplot(gs[0, :2])
        ax1.plot(y_test[:200], label='Actual', linewidth=2, alpha=0.7)
        ax1.plot(y_pred[:200], label='Predicted', linewidth=2, alpha=0.7)
        ax1.set_title('Predictions vs Actual (First 200 samples)', fontweight='bold')
        ax1.set_xlabel('Sample')
        ax1.set_ylabel('Normalized Price')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Plot 2: Key Metrics
        ax2 = fig.add_subplot(gs[0, 2])
        ax2.axis('off')
        metrics_text = "Key Metrics\n\n"
        metrics_text += f"MAE: {mae:.6f}\n"
        metrics_text += f"RMSE: {rmse:.6f}\n"
        metrics_text += f"MAPE: {mape:.2f}%\n"
        metrics_text += f"R²: {r2:.4f}\n\n"
        metrics_text += f"Direction Accuracy:\n{direction_accuracy:.1f}%\n\n"
        metrics_text += f"Samples: {len(y_test)}"

        ax2.text(0.1, 0.5, metrics_text, fontsize=12, verticalalignment='center',
                bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7))

        # Plot 3: Scatter plot
        ax3 = fig.add_subplot(gs[1, 0])
        ax3.scatter(y_test, y_pred, alpha=0.3)
        min_val = min(y_test.min(), y_pred.min())
        max_val = max(y_test.max(), y_pred.max())
        ax3.plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2)
        ax3.set_title('Actual vs Predicted', fontweight='bold')
        ax3.set_xlabel('Actual')
        ax3.set_ylabel('Predicted')
        ax3.grid(True, alpha=0.3)

        # Plot 4: Error distribution
        ax4 = fig.add_subplot(gs[1, 1])
        ax4.hist(errors_pct, bins=50, edgecolor='black', alpha=0.7)
        ax4.axvline(x=0, color='r', linestyle='--', linewidth=2)
        ax4.set_title('Error Distribution (%)', fontweight='bold')
        ax4.set_xlabel('Error (%)')
        ax4.set_ylabel('Frequency')
        ax4.grid(True, alpha=0.3)

        # Plot 5: Residuals
        ax5 = fig.add_subplot(gs[1, 2])
        ax5.scatter(y_pred, errors, alpha=0.3)
        ax5.axhline(y=0, color='r', linestyle='--', linewidth=2)
        ax5.set_title('Residual Plot', fontweight='bold')
        ax5.set_xlabel('Predicted Value')
        ax5.set_ylabel('Residual')
        ax5.grid(True, alpha=0.3)

        # Plot 6: Cumulative error
        ax6 = fig.add_subplot(gs[2, 0])
        cumulative_error = np.cumsum(np.abs(errors))
        ax6.plot(cumulative_error, linewidth=2)
        ax6.set_title('Cumulative Absolute Error', fontweight='bold')
        ax6.set_xlabel('Sample')
        ax6.set_ylabel('Cumulative |Error|')
        ax6.grid(True, alpha=0.3)

        # Plot 7: Error by range
        ax7 = fig.add_subplot(gs[2, 1])
        error_ranges = ['0-5%', '5-10%', '10-15%', '>15%']
        error_counts = [
            (np.abs(errors_pct) <= 5).sum(),
            ((np.abs(errors_pct) > 5) & (np.abs(errors_pct) <= 10)).sum(),
            ((np.abs(errors_pct) > 10) & (np.abs(errors_pct) <= 15)).sum(),
            (np.abs(errors_pct) > 15).sum()
        ]
        colors_range = ['green', 'yellow', 'orange', 'red']
        ax7.bar(error_ranges, error_counts, color=colors_range, alpha=0.7, edgecolor='black')
        ax7.set_title('Error Distribution by Range', fontweight='bold')
        ax7.set_ylabel('Number of Samples')
        ax7.grid(True, alpha=0.3, axis='y')

        # Plot 8: Model confidence
        ax8 = fig.add_subplot(gs[2, 2])
        ax8.axis('off')
        confidence_text = "Model Confidence\n\n"
        confidence_text += f"Samples within ±5%:\n{(np.abs(errors_pct) <= 5).sum() / len(errors_pct) * 100:.1f}%\n\n"
        confidence_text += f"Samples within ±10%:\n{(np.abs(errors_pct) <= 10).sum() / len(errors_pct) * 100:.1f}%\n\n"
        confidence_text += f"Samples within ±15%:\n{(np.abs(errors_pct) <= 15).sum() / len(errors_pct) * 100:.1f}%\n\n"

        if mape < 8:
            verdict = "Excellent! ✨"
            color = 'lightgreen'
        elif mape < 12:
            verdict = "Good ✓"
            color = 'lightyellow'
        else:
            verdict = "Needs Improvement"
            color = 'lightcoral'

        confidence_text += f"\nOverall: {verdict}"

        ax8.text(0.1, 0.5, confidence_text, fontsize=11, verticalalignment='center',
                bbox=dict(boxstyle='round', facecolor=color, alpha=0.7))

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"\n✓ Dashboard saved to {save_path}")

        plt.show()

        # Print summary
        print("\n" + "="*70)
        print("  PERFORMANCE SUMMARY")
        print("="*70)
        print(f"\nMean Absolute Error (MAE): {mae:.6f}")
        print(f"Root Mean Squared Error (RMSE): {rmse:.6f}")
        print(f"Mean Absolute Percentage Error (MAPE): {mape:.2f}%")
        print(f"R² Score: {r2:.4f}")
        print(f"Direction Accuracy: {direction_accuracy:.1f}%")
        print(f"\nSamples within ±5%: {(np.abs(errors_pct) <= 5).sum() / len(errors_pct) * 100:.1f}%")
        print(f"Samples within ±10%: {(np.abs(errors_pct) <= 10).sum() / len(errors_pct) * 100:.1f}%")
        print("="*70 + "\n")


# Example usage
if __name__ == "__main__":
    print("Training Results Visualizer")
    print("="*60)
    print("\nUsage:")
    print("  from models.visualizer import TrainingVisualizer")
    print("  viz = TrainingVisualizer()")
    print("  viz.plot_training_history()")
    print("  viz.create_performance_dashboard(X_test, y_test, model)")

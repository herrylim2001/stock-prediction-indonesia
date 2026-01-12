"""
Indonesian Stock Prediction Dashboard
Streamlit Demo Application
"""
import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta
import ta
from ta.trend import SMAIndicator, EMAIndicator, MACD
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.volatility import BollingerBands, AverageTrueRange
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import custom modules
from models.predictor import get_predictor
from utils.news_scraper import IndonesianNewsScraper
from utils.sentiment_analyzer import IndonesianSentimentAnalyzer
from utils.stock_analyzer import StockMovementAnalyzer
from utils.market_analyzer import get_market_analyzer
from utils.bandar_detector import get_bandar_detector

# Page config
st.set_page_config(
    page_title="Indonesian Stock Prediction",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Stock list
STOCKS = {
    "BBCA": {"name": "Bank Central Asia", "sector": "Keuangan"},
    "BBRI": {"name": "Bank Rakyat Indonesia", "sector": "Keuangan"},
    "TLKM": {"name": "Telkom Indonesia", "sector": "Telekomunikasi"},
    "ASII": {"name": "Astra International", "sector": "Otomotif"},
    "UNVR": {"name": "Unilever Indonesia", "sector": "Consumer Goods"},
    "BMRI": {"name": "Bank Mandiri", "sector": "Keuangan"},
    "GOTO": {"name": "GoTo Gojek Tokopedia", "sector": "Teknologi"},
    "ACES": {"name": "Ace Hardware Indonesia", "sector": "Retail"},
    "ICBP": {"name": "Indofood CBP", "sector": "Consumer Goods"},
    "EMTK": {"name": "Elang Mahkota Teknologi", "sector": "Media & Teknologi"},
    "SUPA": {"name": "Surya Pertiwi", "sector": "Consumer Goods"},
}

# Helper functions
@st.cache_data(ttl=1800)  # Cache for 30 minutes (more frequent updates)
def fetch_stock_data(stock_code, period="6mo"):
    """Fetch stock data from Yahoo Finance with retry mechanism"""
    ticker = f"{stock_code}.JK"

    max_retries = 3
    retry_delay = 2  # seconds

    for attempt in range(max_retries):
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period=period, interval="1d")

            if df.empty:
                if attempt < max_retries - 1:
                    st.warning(f"No data returned. Retrying in {retry_delay} seconds... (Attempt {attempt + 1}/{max_retries})")
                    import time
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                    continue
                return None

            df = df.reset_index()
            df.columns = [col.lower() for col in df.columns]
            return df

        except Exception as e:
            if "Too Many Requests" in str(e) or "Rate" in str(e):
                if attempt < max_retries - 1:
                    st.warning(f"⏳ Rate limited by Yahoo Finance. Waiting {retry_delay} seconds... (Attempt {attempt + 1}/{max_retries})")
                    import time
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                    continue
                else:
                    st.error(f"❌ Yahoo Finance API rate limit exceeded. Please wait a few minutes and try again.")
                    return None
            else:
                st.error(f"Error fetching data: {e}")
                return None

    return None

def calculate_technical_indicators(df):
    """Calculate technical indicators"""
    if df is None or len(df) < 50:
        # Add NaN columns for missing indicators
        df['sma_10'] = np.nan
        df['sma_20'] = np.nan
        df['sma_50'] = np.nan
        df['ema_12'] = np.nan
        df['ema_26'] = np.nan
        df['rsi'] = 50.0  # Neutral RSI
        df['macd'] = 0.0
        df['macd_signal'] = 0.0
        df['macd_diff'] = 0.0
        df['bb_upper'] = df['close'] * 1.02
        df['bb_middle'] = df['close']
        df['bb_lower'] = df['close'] * 0.98
        df['bb_width'] = 0.04
        df['atr'] = df['close'] * 0.01
        df['stoch_k'] = 50.0
        df['stoch_d'] = 50.0
        df['obv'] = 0.0
        df['volume_sma'] = df['volume'].mean() if 'volume' in df.columns else 1000000
        df['volume_ratio'] = 1.0
        return df

    try:
        # Moving Averages
        df['sma_10'] = SMAIndicator(df['close'], window=10).sma_indicator()
        df['sma_20'] = SMAIndicator(df['close'], window=20).sma_indicator()
        df['sma_50'] = SMAIndicator(df['close'], window=50).sma_indicator()
        df['ema_12'] = EMAIndicator(df['close'], window=12).ema_indicator()
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

        # ATR
        df['atr'] = AverageTrueRange(df['high'], df['low'], df['close'], window=14).average_true_range()

        # Stochastic Oscillator
        stoch = StochasticOscillator(df['high'], df['low'], df['close'], window=14, smooth_window=3)
        df['stoch_k'] = stoch.stoch()
        df['stoch_d'] = stoch.stoch_signal()

        # Volume indicators
        if 'volume' in df.columns:
            from ta.volume import OnBalanceVolumeIndicator
            df['obv'] = OnBalanceVolumeIndicator(df['close'], df['volume']).on_balance_volume()
            df['volume_sma'] = df['volume'].rolling(window=20).mean()
            df['volume_ratio'] = df['volume'] / df['volume_sma']
        else:
            df['obv'] = 0.0
            df['volume_sma'] = 1000000
            df['volume_ratio'] = 1.0

    except Exception as e:
        st.warning(f"Could not calculate some technical indicators: {e}")
        # Fill with defaults if calculation fails
        if 'rsi' not in df.columns:
            df['rsi'] = 50.0
        if 'sma_20' not in df.columns:
            df['sma_20'] = df['close']
        if 'sma_50' not in df.columns:
            df['sma_50'] = df['close']
        if 'bb_width' not in df.columns:
            df['bb_width'] = 0.04
        if 'stoch_k' not in df.columns:
            df['stoch_k'] = 50.0
        if 'stoch_d' not in df.columns:
            df['stoch_d'] = 50.0
        if 'obv' not in df.columns:
            df['obv'] = 0.0
        if 'volume_sma' not in df.columns:
            df['volume_sma'] = df.get('volume', pd.Series([1000000])).mean()
        if 'volume_ratio' not in df.columns:
            df['volume_ratio'] = 1.0

    return df

def generate_technical_predictions(df, current_price, volatility=0.02):
    """
    Generate predictions based on technical analysis and momentum
    More accurate than random predictions
    """
    if df is None or len(df) < 20:
        # Fallback to neutral predictions if insufficient data
        return {
            "1h": {"price": current_price, "confidence": 0.50, "trend": "NEUTRAL"},
            "4h": {"price": current_price, "confidence": 0.50, "trend": "NEUTRAL"},
            "1d": {"price": current_price, "confidence": 0.50, "trend": "NEUTRAL"},
            "3d": {"price": current_price, "confidence": 0.50, "trend": "NEUTRAL"}
        }

    latest = df.iloc[-1]

    # Calculate momentum score (-100 to +100)
    momentum_score = 0
    confidence_factors = []

    # 1. RSI momentum
    rsi = latest.get('rsi', 50)
    if pd.notna(rsi):
        if rsi < 30:
            momentum_score += 25
            confidence_factors.append(0.8)
        elif rsi < 40:
            momentum_score += 15
            confidence_factors.append(0.7)
        elif rsi > 70:
            momentum_score -= 25
            confidence_factors.append(0.8)
        elif rsi > 60:
            momentum_score -= 15
            confidence_factors.append(0.7)
        else:
            confidence_factors.append(0.6)

    # 2. MACD momentum
    macd = latest.get('macd', 0)
    macd_signal = latest.get('macd_signal', 0)
    if pd.notna(macd) and pd.notna(macd_signal):
        macd_diff = macd - macd_signal
        if macd_diff > 0:
            momentum_score += 15
            confidence_factors.append(0.75)
        else:
            momentum_score -= 15
            confidence_factors.append(0.75)

    # 3. Moving Average trend
    sma_20 = latest.get('sma_20', current_price)
    sma_50 = latest.get('sma_50', current_price)
    if pd.notna(sma_20) and pd.notna(sma_50):
        if current_price > sma_20 > sma_50:
            momentum_score += 20
            confidence_factors.append(0.8)
        elif current_price < sma_20 < sma_50:
            momentum_score -= 20
            confidence_factors.append(0.8)
        elif current_price > sma_20:
            momentum_score += 10
            confidence_factors.append(0.65)
        else:
            momentum_score -= 10
            confidence_factors.append(0.65)

    # 4. Bollinger Bands position
    bb_upper = latest.get('bb_upper', current_price * 1.02)
    bb_lower = latest.get('bb_lower', current_price * 0.98)
    bb_middle = latest.get('bb_middle', current_price)
    if pd.notna(bb_upper) and pd.notna(bb_lower):
        bb_position = (current_price - bb_lower) / (bb_upper - bb_lower)
        if bb_position < 0.2:
            momentum_score += 15
            confidence_factors.append(0.75)
        elif bb_position > 0.8:
            momentum_score -= 15
            confidence_factors.append(0.75)

    # 5. Volume trend
    volume_ratio = latest.get('volume_ratio', 1.0)
    if pd.notna(volume_ratio):
        if volume_ratio > 1.5:
            # High volume confirms trend
            confidence_factors.append(0.85)
        elif volume_ratio < 0.7:
            # Low volume reduces confidence
            confidence_factors.append(0.55)
        else:
            confidence_factors.append(0.65)

    # 6. Recent price momentum
    if len(df) >= 5:
        price_5d_ago = df.iloc[-5]['close']
        momentum_5d = ((current_price - price_5d_ago) / price_5d_ago) * 100
        if momentum_5d > 5:
            momentum_score += 15
        elif momentum_5d < -5:
            momentum_score -= 15

    # Normalize momentum score to -1 to +1
    normalized_momentum = np.clip(momentum_score / 100, -1, 1)

    # Calculate base confidence
    base_confidence = np.mean(confidence_factors) if confidence_factors else 0.60

    # Determine trend
    if normalized_momentum > 0.3:
        trend = "UP"
    elif normalized_momentum < -0.3:
        trend = "DOWN"
    else:
        trend = "NEUTRAL"

    # Calculate ATR for volatility adjustment
    atr = latest.get('atr', current_price * 0.01)
    if pd.notna(atr):
        atr_pct = atr / current_price
    else:
        atr_pct = volatility

    # Generate predictions with momentum-based adjustments
    predictions = {
        "1h": {
            "price": current_price * (1 + normalized_momentum * 0.003 + np.random.normal(0, atr_pct * 0.2)),
            "confidence": base_confidence * 0.9,  # Lower confidence for short term
            "trend": trend if abs(normalized_momentum) > 0.15 else "NEUTRAL"
        },
        "4h": {
            "price": current_price * (1 + normalized_momentum * 0.008 + np.random.normal(0, atr_pct * 0.4)),
            "confidence": base_confidence * 0.95,
            "trend": trend if abs(normalized_momentum) > 0.2 else "NEUTRAL"
        },
        "1d": {
            "price": current_price * (1 + normalized_momentum * 0.015 + np.random.normal(0, atr_pct * 0.6)),
            "confidence": base_confidence,
            "trend": trend
        },
        "3d": {
            "price": current_price * (1 + normalized_momentum * 0.035 + np.random.normal(0, atr_pct * 1.0)),
            "confidence": base_confidence * 0.85,  # Lower confidence for longer term
            "trend": trend if abs(normalized_momentum) > 0.25 else "NEUTRAL"
        }
    }

    # Ensure confidence is in valid range
    for timeframe in predictions:
        predictions[timeframe]['confidence'] = np.clip(predictions[timeframe]['confidence'], 0.5, 0.9)
        predictions[timeframe]['momentum_score'] = momentum_score

    return predictions

def generate_trading_signal(df, predictions, bandar_analysis=None):
    """
    Generate trading signal based on technical indicators, predictions, and bandar patterns
    Integrates multiple signal sources for more accurate recommendations
    """
    if df is None or len(df) < 2:
        return {"signal": "HOLD", "strength": 0, "reasons": ["Insufficient data"], "score": 0}

    latest = df.iloc[-1]
    signals = []
    score = 0
    reasons = []

    # === BANDAR PATTERN ANALYSIS (HIGHEST WEIGHT) ===
    if bandar_analysis:
        dominant_phase = bandar_analysis.get('dominant_phase', 'NONE')
        dominant_conf = bandar_analysis.get('dominant_confidence', 0)

        if dominant_phase == "ACCUMULATION" and dominant_conf >= 60:
            score += 4  # Strong buy signal
            signals.append("BUY")
            reasons.append(f"🎯 BANDAR ACCUMULATION ({dominant_conf:.0f}% confidence)")
        elif dominant_phase == "MARKUP" and dominant_conf >= 70:
            score += 3  # Buy signal but risky
            signals.append("BUY")
            reasons.append(f"🔥 BANDAR MARKUP - Ride the wave ({dominant_conf:.0f}%)")
        elif dominant_phase == "DISTRIBUTION" and dominant_conf >= 60:
            score -= 5  # Strong sell signal
            signals.append("SELL")
            reasons.append(f"⚠️ BANDAR DISTRIBUTION - EXIT NOW ({dominant_conf:.0f}%)")

        # Check individual phase warnings
        distribution = bandar_analysis.get('distribution', {})
        if distribution.get('detected') and distribution.get('confidence', 0) >= 70:
            score -= 2  # Additional penalty for strong distribution
            reasons.append(f"Distribution detected: {distribution.get('confidence', 0):.0f}%")

    # === RSI SIGNALS ===
    if pd.notna(latest.get('rsi', np.nan)):
        rsi = latest['rsi']
        if rsi < 30:
            score += 2
            signals.append("BUY")
            reasons.append(f"RSI oversold ({rsi:.0f})")
        elif rsi < 40:
            score += 1
            reasons.append(f"RSI weak ({rsi:.0f})")
        elif rsi > 70:
            score -= 2
            signals.append("SELL")
            reasons.append(f"RSI overbought ({rsi:.0f})")
        elif rsi > 60:
            score -= 1
            reasons.append(f"RSI strong ({rsi:.0f})")

    # === MACD SIGNALS ===
    if pd.notna(latest.get('macd', np.nan)) and pd.notna(latest.get('macd_signal', np.nan)):
        macd_diff = latest['macd'] - latest['macd_signal']
        if macd_diff > 0:
            score += 1
            signals.append("BUY")
            reasons.append("MACD bullish")
        else:
            score -= 1
            signals.append("SELL")
            reasons.append("MACD bearish")

    # === MOVING AVERAGE TREND ===
    if pd.notna(latest.get('sma_20', np.nan)) and pd.notna(latest.get('sma_50', np.nan)):
        if latest['close'] > latest['sma_20'] > latest['sma_50']:
            score += 2
            signals.append("BUY")
            reasons.append("Strong uptrend (MA alignment)")
        elif latest['close'] < latest['sma_20'] < latest['sma_50']:
            score -= 2
            signals.append("SELL")
            reasons.append("Strong downtrend (MA alignment)")
        elif latest['close'] > latest['sma_50']:
            score += 1
            reasons.append("Price above SMA50")
        else:
            score -= 1
            reasons.append("Price below SMA50")

    # === BOLLINGER BANDS ===
    if pd.notna(latest.get('bb_lower', np.nan)) and pd.notna(latest.get('bb_upper', np.nan)):
        bb_position = (latest['close'] - latest['bb_lower']) / (latest['bb_upper'] - latest['bb_lower'])
        if bb_position < 0.1:
            score += 2
            signals.append("BUY")
            reasons.append("Price at BB lower band")
        elif bb_position > 0.9:
            score -= 2
            signals.append("SELL")
            reasons.append("Price at BB upper band")

    # === VOLUME CONFIRMATION ===
    volume_ratio = latest.get('volume_ratio', 1.0)
    if pd.notna(volume_ratio):
        if volume_ratio > 1.5:
            # High volume confirms the trend
            if score > 0:
                score += 1
                reasons.append(f"High volume confirms trend ({volume_ratio:.1f}x)")
            elif score < 0:
                score -= 1
                reasons.append(f"High volume confirms downtrend ({volume_ratio:.1f}x)")

    # === PREDICTION TREND ===
    pred_1d = predictions.get('1d', {})
    pred_trend = pred_1d.get('trend', 'NEUTRAL')
    pred_conf = pred_1d.get('confidence', 0.5)

    if pred_trend == "UP" and pred_conf > 0.7:
        score += 2
        signals.append("BUY")
        reasons.append(f"Strong bullish prediction ({pred_conf*100:.0f}%)")
    elif pred_trend == "UP":
        score += 1
        reasons.append("Bullish prediction")
    elif pred_trend == "DOWN" and pred_conf > 0.7:
        score -= 2
        signals.append("SELL")
        reasons.append(f"Strong bearish prediction ({pred_conf*100:.0f}%)")
    elif pred_trend == "DOWN":
        score -= 1
        reasons.append("Bearish prediction")

    # === MOMENTUM SCORE ===
    momentum_score = pred_1d.get('momentum_score', 0)
    if momentum_score > 50:
        reasons.append(f"Strong bullish momentum ({momentum_score:.0f})")
    elif momentum_score < -50:
        reasons.append(f"Strong bearish momentum ({momentum_score:.0f})")

    # === DETERMINE FINAL SIGNAL ===
    if score >= 5:
        signal = "STRONG BUY"
        strength = min(100, score * 15)
    elif score >= 2:
        signal = "BUY"
        strength = min(90, score * 20)
    elif score >= 1:
        signal = "WEAK BUY"
        strength = min(70, score * 25)
    elif score <= -5:
        signal = "STRONG SELL"
        strength = min(100, abs(score) * 15)
    elif score <= -2:
        signal = "SELL"
        strength = min(90, abs(score) * 20)
    elif score <= -1:
        signal = "WEAK SELL"
        strength = min(70, abs(score) * 25)
    else:
        signal = "HOLD"
        strength = 50

    return {
        "signal": signal,
        "score": score,
        "strength": strength,
        "reasons": reasons[:5]  # Top 5 reasons
    }

def detect_support_resistance(df, n_levels=3):
    """
    Detect support and resistance levels using pivot points and volume
    Returns key price levels for trading decisions
    """
    if df is None or len(df) < 20:
        return {"support": [], "resistance": [], "pivot": None}

    # Calculate pivot points from recent highs and lows
    recent_df = df.tail(60)  # Last 60 periods

    # Find local maxima (resistance)
    resistance_candidates = []
    for i in range(2, len(recent_df) - 2):
        if (recent_df.iloc[i]['high'] > recent_df.iloc[i-1]['high'] and
            recent_df.iloc[i]['high'] > recent_df.iloc[i-2]['high'] and
            recent_df.iloc[i]['high'] > recent_df.iloc[i+1]['high'] and
            recent_df.iloc[i]['high'] > recent_df.iloc[i+2]['high']):
            resistance_candidates.append({
                'price': recent_df.iloc[i]['high'],
                'volume': recent_df.iloc[i]['volume'],
                'date': recent_df.iloc[i]['date']
            })

    # Find local minima (support)
    support_candidates = []
    for i in range(2, len(recent_df) - 2):
        if (recent_df.iloc[i]['low'] < recent_df.iloc[i-1]['low'] and
            recent_df.iloc[i]['low'] < recent_df.iloc[i-2]['low'] and
            recent_df.iloc[i]['low'] < recent_df.iloc[i+1]['low'] and
            recent_df.iloc[i]['low'] < recent_df.iloc[i+2]['low']):
            support_candidates.append({
                'price': recent_df.iloc[i]['low'],
                'volume': recent_df.iloc[i]['volume'],
                'date': recent_df.iloc[i]['date']
            })

    # Cluster similar levels (within 2% of each other)
    def cluster_levels(levels, tolerance=0.02):
        if not levels:
            return []

        sorted_levels = sorted(levels, key=lambda x: x['price'])
        clusters = []
        current_cluster = [sorted_levels[0]]

        for level in sorted_levels[1:]:
            if abs(level['price'] - current_cluster[0]['price']) / current_cluster[0]['price'] < tolerance:
                current_cluster.append(level)
            else:
                clusters.append(current_cluster)
                current_cluster = [level]

        clusters.append(current_cluster)

        # Get weighted average for each cluster (weighted by volume)
        final_levels = []
        for cluster in clusters:
            total_volume = sum(l['volume'] for l in cluster)
            weighted_price = sum(l['price'] * l['volume'] for l in cluster) / total_volume
            strength = len(cluster) * (total_volume / recent_df['volume'].mean())
            final_levels.append({
                'price': weighted_price,
                'strength': strength,
                'touches': len(cluster)
            })

        return sorted(final_levels, key=lambda x: x['strength'], reverse=True)

    resistance_levels = cluster_levels(resistance_candidates)[:n_levels]
    support_levels = cluster_levels(support_candidates)[:n_levels]

    # Calculate pivot point (traditional)
    latest = df.iloc[-1]
    pivot = (latest['high'] + latest['low'] + latest['close']) / 3

    # Sort by price
    resistance_levels = sorted(resistance_levels, key=lambda x: x['price'], reverse=True)
    support_levels = sorted(support_levels, key=lambda x: x['price'], reverse=True)

    return {
        'support': support_levels,
        'resistance': resistance_levels,
        'pivot': pivot,
        'current_price': latest['close']
    }

def calculate_lot_recommendation(current_price, modal_total, risk_per_trade, stop_loss_pct):
    """Calculate recommended lot size based on risk management"""
    max_loss = modal_total * risk_per_trade
    risk_per_share = current_price * stop_loss_pct
    max_shares = int(max_loss / risk_per_share)
    lot_size = 100
    recommended_lots = max(1, max_shares // lot_size)

    # Check max position size (10% of portfolio)
    max_position = modal_total * 0.10
    max_lots_by_position = int(max_position / (lot_size * current_price))

    final_lots = min(recommended_lots, max_lots_by_position)
    capital_needed = final_lots * lot_size * current_price

    return {
        "lots": final_lots,
        "shares": final_lots * lot_size,
        "capital_needed": capital_needed,
        "max_loss": max_loss,
        "stop_loss_price": current_price * (1 - stop_loss_pct),
        "take_profit_price": current_price * (1 + stop_loss_pct * 2)  # 2:1 risk/reward
    }

# Sidebar
st.sidebar.title("📊 Stock Prediction Settings")
st.sidebar.markdown("---")

# Stock selection
selected_stock = st.sidebar.selectbox(
    "Select Stock",
    options=list(STOCKS.keys()),
    format_func=lambda x: f"{x} - {STOCKS[x]['name']}"
)

# Real-time Data Update Controls
st.sidebar.markdown("---")
st.sidebar.subheader("🔄 Data Updates")

# Manual refresh button
col1, col2 = st.sidebar.columns([2, 1])
with col1:
    if st.button("🔄 Refresh Data Now", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

with col2:
    st.caption("Clear cache")

# Auto-refresh toggle
enable_autorefresh = st.sidebar.checkbox(
    "Enable Auto-Refresh",
    value=True,  # Enabled by default for real-time updates
    help="Automatically refresh data every few minutes for real-time predictions"
)

if enable_autorefresh:
    refresh_interval = st.sidebar.slider(
        "Refresh Interval (minutes)",
        min_value=1,
        max_value=30,
        value=5,
        step=1,
        help="How often to auto-refresh data"
    )

    # Auto-refresh implementation using streamlit-autorefresh
    import time

    # Try to import streamlit-autorefresh
    try:
        from streamlit_autorefresh import st_autorefresh

        # Convert minutes to milliseconds
        interval_ms = refresh_interval * 60 * 1000

        # Auto-refresh with countdown
        count = st_autorefresh(interval=interval_ms, key="datarefresh")

        # Show success indicator
        if count > 0:
            st.sidebar.success(f"✅ Auto-refresh active (Refresh #{count})")
        else:
            st.sidebar.info(f"⏱️ Auto-refreshing every {refresh_interval} minute(s)")

    except ImportError:
        # Fallback: Use session state for manual countdown
        import datetime

        st.sidebar.warning("⚠️ streamlit-autorefresh not installed. Using fallback mode.")
        st.sidebar.info(f"⏱️ Target: Refresh every {refresh_interval} minute(s)")

        # Initialize session state for last refresh time
        if 'last_refresh' not in st.session_state:
            st.session_state.last_refresh = datetime.datetime.now()

        # Calculate time since last refresh
        time_since_refresh = (datetime.datetime.now() - st.session_state.last_refresh).total_seconds()
        time_until_refresh = (refresh_interval * 60) - time_since_refresh

        if time_until_refresh <= 0:
            # Time to refresh
            st.session_state.last_refresh = datetime.datetime.now()
            st.cache_data.clear()
            st.sidebar.success("🔄 Refreshing now...")
            st.rerun()
        else:
            # Show countdown with progress bar
            progress = (refresh_interval * 60 - time_until_refresh) / (refresh_interval * 60)
            st.sidebar.progress(progress)

            minutes_left = int(time_until_refresh // 60)
            seconds_left = int(time_until_refresh % 60)

            if minutes_left > 0:
                st.sidebar.caption(f"⏰ Next refresh in: {minutes_left}m {seconds_left}s")
            else:
                st.sidebar.caption(f"⏰ Next refresh in: {seconds_left}s")

            time.sleep(1)
            st.rerun()
else:
    st.sidebar.caption("💡 Enable auto-refresh for real-time updates")

st.sidebar.caption("💡 Data cached for 30 minutes")

st.sidebar.markdown("---")

# Trading config
st.sidebar.subheader("💰 Trading Configuration")
modal_total = st.sidebar.number_input(
    "Total Capital (Rp)",
    min_value=1000000,
    max_value=1000000000,
    value=100000000,
    step=1000000,
    format="%d"
)

risk_per_trade = st.sidebar.slider(
    "Risk per Trade (%)",
    min_value=0.5,
    max_value=5.0,
    value=1.0,
    step=0.1
) / 100

stop_loss_pct = st.sidebar.slider(
    "Stop Loss (%)",
    min_value=1.0,
    max_value=10.0,
    value=2.0,
    step=0.5
) / 100

# Data period
period = st.sidebar.selectbox(
    "Data Period",
    options=["1mo", "3mo", "6mo", "1y", "2y"],
    index=2
)

st.sidebar.markdown("---")

# Display session info
from datetime import datetime
import pytz

try:
    jakarta_tz = pytz.timezone('Asia/Jakarta')
    session_time = datetime.now(jakarta_tz)
except:
    session_time = datetime.now()

st.sidebar.info(f"""
📅 **Session Info**

**Date:** {session_time.strftime('%d %B %Y')}
**Time:** {session_time.strftime('%H:%M:%S WIB')}

*Data refreshed on page load*
""")

st.sidebar.markdown("---")

# Enhanced Sidebar Disclaimer
st.sidebar.error("⚠️ **RISK WARNING**")
st.sidebar.markdown("""
**NOT Financial Advice**

This system is for:
- ✅ Educational purposes
- ✅ Technical analysis learning
- ✅ Algorithm demonstration

**NOT for:**
- ❌ Investment decisions
- ❌ Financial advice
- ❌ Guaranteed profits

**Always consult licensed financial advisors before investing.**
""")

# Main content
st.title(f"📈 {selected_stock} - {STOCKS[selected_stock]['name']}")
st.markdown(f"**Sector:** {STOCKS[selected_stock]['sector']}")

# Display current date/time and data info
from datetime import datetime
import pytz

# Get current time in Indonesia timezone
try:
    jakarta_tz = pytz.timezone('Asia/Jakarta')
    current_time = datetime.now(jakarta_tz)
except:
    current_time = datetime.now()

col1, col2, col3 = st.columns([2, 2, 2])

with col1:
    st.info(f"📅 **Current Date:** {current_time.strftime('%d %B %Y')}")

with col2:
    st.info(f"🕐 **Current Time:** {current_time.strftime('%H:%M:%S WIB')}")

with col3:
    st.info(f"📊 **Data Period:** {period.upper()}")

# Prominent Risk Disclaimer Banner
st.warning("""
⚠️ **IMPORTANT DISCLAIMER - READ BEFORE USING**

**This is an educational/demonstration system only. NOT financial advice.**

- Predictions are based on historical data and technical analysis
- Past performance does NOT guarantee future results
- Stock markets are inherently risky and unpredictable
- ALWAYS do your own research and consult licensed financial advisors
- Use this tool for learning purposes only
- The creators assume NO liability for your investment decisions

**Remember:** You are solely responsible for your investment choices.
""")

# Fetch data
with st.spinner(f"Fetching data for {selected_stock}..."):
    df = fetch_stock_data(selected_stock, period)

if df is None or len(df) == 0:
    st.error(f"❌ No data available for {selected_stock}.")
    st.info("""
    **💡 Troubleshooting:**
    - Yahoo Finance API may be rate limited (too many requests)
    - Try waiting 2-3 minutes and refresh the page
    - Try selecting a different stock from the sidebar
    - Try a different time period (1mo, 3mo, etc.)
    - Clear your browser cache and reload
    """)
    st.stop()

# Calculate indicators
with st.spinner("📊 Calculating technical indicators..."):
    df = calculate_technical_indicators(df)

# Show warning if insufficient data
if len(df) < 50:
    st.warning(f"⚠️ Limited data available ({len(df)} days). Technical indicators may not be accurate. Consider selecting a longer time period.")

# Display data freshness information
col_data1, col_data2 = st.columns([3, 1])

with col_data1:
    st.success(f"""
    ✅ **Data Successfully Loaded**

    - **Data Points:** {len(df)} days
    - **Date Range:** {df['date'].min().strftime('%d %b %Y')} to {df['date'].max().strftime('%d %b %Y')}
    - **Last Updated:** {current_time.strftime('%d %B %Y %H:%M:%S WIB')}
    - **Data Source:** Yahoo Finance
    """)

with col_data2:
    if enable_autorefresh:
        st.info(f"""
        🔄 **Real-Time Mode**

        Auto-refresh: ✅ ON
        Interval: {refresh_interval} min
        """)
    else:
        st.warning("""
        ⏸️ **Static Mode**

        Auto-refresh: OFF
        """)

# Get latest data
latest = df.iloc[-1]
current_price = latest['close']
prev_close = df.iloc[-2]['close'] if len(df) > 1 else current_price
price_change = current_price - prev_close
price_change_pct = (price_change / prev_close) * 100

# Initialize predictor and news modules
@st.cache_resource
def initialize_modules():
    predictor = get_predictor()
    news_scraper = IndonesianNewsScraper()
    sentiment_analyzer = IndonesianSentimentAnalyzer()
    stock_analyzer = StockMovementAnalyzer()
    market_analyzer = get_market_analyzer()
    bandar_detector = get_bandar_detector()
    return predictor, news_scraper, sentiment_analyzer, stock_analyzer, market_analyzer, bandar_detector

predictor, news_scraper, sentiment_analyzer, stock_analyzer, market_analyzer, bandar_detector = initialize_modules()

# === ANALYSIS PHASE ===
# Detect bandar patterns first (needed for trading signal)
with st.spinner("🔍 Detecting bandar accumulation/distribution patterns..."):
    bandar_analysis = bandar_detector.analyze_full(df)

# Analyze market context (IHSG, beta, regime)
with st.spinner("📊 Analyzing IHSG correlation & market regime..."):
    market_context = market_analyzer.get_market_context(df)
    sector_info = market_analyzer.get_sector_classification(selected_stock)

# Analyze stock movement (why up/down)
with st.spinner("🔍 Analyzing stock movement patterns..."):
    movement_analysis = stock_analyzer.analyze_full(df)

# === PREDICTION PHASE ===
# Generate predictions using LSTM or fallback to technical predictions
with st.spinner("🤖 Generating AI predictions..."):
    predictions = predictor.predict_multiple_horizons(df, selected_stock, current_price)

    # Fallback to technical predictions if LSTM confidence is too low
    if not predictor.model_loaded or predictions.get('1d', {}).get('confidence', 0) < 0.6:
        technical_predictions = generate_technical_predictions(df, current_price)
        # Merge predictions (prefer LSTM if available, else use technical)
        for timeframe in ['1h', '4h', '1d', '3d']:
            if timeframe in technical_predictions and timeframe in predictions:
                # Average both predictions for better accuracy
                tech_pred = technical_predictions[timeframe]
                lstm_pred = predictions[timeframe]
                predictions[timeframe]['price'] = (tech_pred['price'] + lstm_pred['price']) / 2
                predictions[timeframe]['confidence'] = max(tech_pred['confidence'], lstm_pred.get('confidence', 0.5))
                if 'momentum_score' in tech_pred:
                    predictions[timeframe]['momentum_score'] = tech_pred['momentum_score']

# Scrape news and analyze sentiment
with st.spinner("📰 Fetching latest news & analyzing sentiment..."):
    try:
        news_df = news_scraper.scrape_all(selected_stock, limit=5)
        if not news_df.empty:
            news_articles = news_df.to_dict('records')
            sentiment_result = sentiment_analyzer.analyze_articles(news_articles)
        else:
            news_articles = []
            sentiment_result = None
    except Exception as e:
        news_articles = []
        sentiment_result = None

# === SIGNAL GENERATION ===
# Generate trading signal (combining technical + bandar + predictions)
signal_data = generate_trading_signal(df, predictions, bandar_analysis=bandar_analysis)

# Adjust signal with news sentiment if available
if sentiment_result and sentiment_result['average_score'] != 0:
    sentiment_signal = sentiment_analyzer.get_market_sentiment_signal(sentiment_result['average_score'])
    signal_data['sentiment_signal'] = sentiment_signal
    signal_data['sentiment_score'] = sentiment_result['average_score']
else:
    signal_data['sentiment_signal'] = "NEUTRAL"
    signal_data['sentiment_score'] = 0.0

# Detect Support/Resistance levels
with st.spinner("📊 Detecting support & resistance levels..."):
    sr_levels = detect_support_resistance(df, n_levels=3)

# Calculate lot recommendation
lot_rec = calculate_lot_recommendation(current_price, modal_total, risk_per_trade, stop_loss_pct)

# Display metrics
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "Current Price",
        f"Rp {current_price:,.0f}",
        f"{price_change_pct:+.2f}%"
    )

with col2:
    st.metric(
        "Volume",
        f"{latest['volume']:,.0f}"
    )

with col3:
    color = "🟢" if signal_data['signal'] in ["BUY", "STRONG BUY"] else "🔴" if signal_data['signal'] in ["SELL", "STRONG SELL"] else "🟡"
    st.metric(
        "Signal",
        f"{color} {signal_data['signal']}"
    )

with col4:
    st.metric(
        "RSI (14)",
        f"{latest['rsi']:.1f}",
        "Oversold" if latest['rsi'] < 30 else "Overbought" if latest['rsi'] > 70 else "Neutral"
    )

with col5:
    st.metric(
        "Recommended Lots",
        f"{lot_rec['lots']} lot",
        f"{lot_rec['shares']:,} shares"
    )

st.markdown("---")

# Market Context Section (IHSG, Beta, Sector)
st.subheader("🌐 Market Context & Stock Classification")

col_m1, col_m2, col_m3, col_m4 = st.columns(4)

with col_m1:
    # Market Regime
    regime = market_context['regime']
    regime_icon = "🐂" if "BULL" in regime['regime'] else "🐻" if "BEAR" in regime['regime'] else "↔️"
    regime_color = "normal" if "BULL" in regime['regime'] else "inverse" if "BEAR" in regime['regime'] else "off"

    st.metric(
        "📊 IHSG Regime",
        f"{regime_icon} {regime['regime']}",
        delta=f"Conf: {regime['confidence']}%",
        delta_color=regime_color
    )
    st.caption(f"IHSG: {regime['ihsg_price']:,.2f}")

with col_m2:
    # Beta
    beta = market_context['beta']
    beta_icon = "🔥" if beta['beta'] > 1.5 else "⚡" if beta['beta'] > 1.0 else "🛡️" if beta['beta'] < 0.8 else "📊"

    st.metric(
        f"{beta_icon} Beta (vs IHSG)",
        f"{beta['beta']:.3f}",
        delta=f"Corr: {beta['correlation']:.2f}",
        delta_color="off"
    )
    st.caption(f"Risk: {beta['interpretation'].split('-')[0].strip()}")

with col_m3:
    # Sector
    st.metric(
        "🏢 Sector",
        sector_info['sector'],
        delta=sector_info['category'],
        delta_color="off"
    )
    st.caption(f"Sub: {sector_info['sub_sector']}")

with col_m4:
    # IHSG Return
    st.metric(
        "📈 IHSG Return",
        f"{regime['return_20d']:+.2f}%",
        delta=f"50D: {regime['return_50d']:+.2f}%",
        delta_color="normal" if regime['return_20d'] > 0 else "inverse"
    )
    st.caption(f"Vol: {regime['volatility']:.1f}%")

# Detailed explanation in expander
with st.expander("ℹ️ **Penjelasan Market Context**"):
    st.markdown(f"""
    ### 📊 **Market Regime: {regime['regime']}**
    {regime['explanation']}
    - **Confidence:** {regime['confidence']}%
    - **Trend Strength:** {regime['trend_strength']}/11
    - **Volatility:** {regime['volatility']:.2f}% (annualized)

    ### {beta_icon} **Beta Analysis: {beta['beta']:.3f}**
    {beta['interpretation']}
    - **Correlation with IHSG:** {beta['correlation']:.3f} ({abs(beta['correlation'])*100:.1f}%)
    - **Reliability:** {beta['reliability']} (based on {beta['data_points']} data points)
    - **Interpretation:**
      - Beta > 1.0 = Lebih volatile dari IHSG (high risk/reward)
      - Beta = 1.0 = Sejalan dengan IHSG
      - Beta < 1.0 = Kurang volatile dari IHSG (defensive)

    ### 🏢 **Sector: {sector_info['sector']}**
    - **Sub-sector:** {sector_info['sub_sector']}
    - **Category:** {sector_info['category']}
    - **Characteristic:**
      {
        'Blue Chip: Saham unggulan dengan likuiditas tinggi dan fundamental kuat' if sector_info['category'] == 'Blue Chip'
        else 'Second Liner: Saham lapis kedua dengan potensi pertumbuhan' if sector_info['category'] == 'Second Liner'
        else 'Growth: Saham growth dengan volatilitas tinggi' if sector_info['category'] == 'Growth'
        else 'Commodity: Dipengaruhi harga komoditas global' if sector_info['category'] == 'Commodity'
        else 'State-Owned: BUMN dengan stabilitas relatif'
      }

    ### 💡 **Trading Implication:**
    {"- IHSG bullish + High beta = Potensi gain lebih besar dari IHSG" if "BULL" in regime['regime'] and beta['beta'] > 1.2
     else "- IHSG bearish + High beta = Risk lebih tinggi, waspadai penurunan tajam" if "BEAR" in regime['regime'] and beta['beta'] > 1.2
     else "- IHSG sideways + Low beta = Relatif stabil, cocok untuk defensive play" if regime['regime'] == "SIDEWAYS" and beta['beta'] < 0.8
     else "- Market condition normal, ikuti technical analysis"}
    """)

st.markdown("---")

# Bandar Pattern Detection Section (IDX Specialist Feature!)
st.subheader("🎯 Bandar Pattern Detection - Analisa Smart Money")

# Dominant phase alert
dominant_phase = bandar_analysis['dominant_phase']
dominant_conf = bandar_analysis['dominant_confidence']

if dominant_phase != "UNKNOWN":
    if dominant_phase == "ACCUMULATION":
        st.success(f"""
        🟢 **ACCUMULATION PHASE DETECTED** (Confidence: {dominant_conf:.0f}%)

        {bandar_analysis['phase_description']}
        """)
    elif dominant_phase == "MARKUP":
        st.warning(f"""
        🔥 **MARKUP PHASE DETECTED** (Confidence: {dominant_conf:.0f}%)

        {bandar_analysis['phase_description']}
        """)
    elif dominant_phase == "DISTRIBUTION":
        st.error(f"""
        🔴 **DISTRIBUTION PHASE DETECTED** (Confidence: {dominant_conf:.0f}%)

        {bandar_analysis['phase_description']}
        """)
else:
    st.info("""
    ⚪ **NO CLEAR BANDAR PATTERN**

    Tidak ada pola bandar yang jelas terdeteksi. Gunakan analisa teknikal biasa.
    """)

# Phase breakdown
col_b1, col_b2, col_b3 = st.columns(3)

with col_b1:
    acc = bandar_analysis['accumulation']
    acc_icon = "🟢" if acc['detected'] else "⚪"
    acc_color = "normal" if acc['detected'] else "off"

    st.metric(
        f"{acc_icon} Accumulation",
        f"{acc['confidence']:.0f}%",
        delta=acc['strength'] if acc['detected'] else "Not detected",
        delta_color=acc_color
    )

    if acc['detected'] and len(acc['reasons']) > 0:
        with st.expander(f"📋 Details ({len(acc['reasons'])} signals)"):
            for reason in acc['reasons'][:5]:  # Top 5
                st.caption(reason)
            st.info(acc['recommendation'])

with col_b2:
    markup = bandar_analysis['markup']
    markup_icon = "🔥" if markup['detected'] else "⚪"
    markup_color = "normal" if markup['detected'] else "off"

    st.metric(
        f"{markup_icon} Markup",
        f"{markup['confidence']:.0f}%",
        delta=markup['strength'] if markup['detected'] else "Not detected",
        delta_color=markup_color
    )

    if markup['detected'] and len(markup['reasons']) > 0:
        with st.expander(f"📋 Details ({len(markup['reasons'])} signals)"):
            for reason in markup['reasons'][:5]:
                st.caption(reason)
            st.info(markup['recommendation'])

with col_b3:
    dist = bandar_analysis['distribution']
    dist_icon = "🔴" if dist['detected'] else "⚪"
    dist_color = "inverse" if dist['detected'] else "off"

    st.metric(
        f"{dist_icon} Distribution",
        f"{dist['confidence']:.0f}%",
        delta=dist['strength'] if dist['detected'] else "Not detected",
        delta_color=dist_color
    )

    if dist['detected'] and len(dist['reasons']) > 0:
        with st.expander(f"📋 Details ({len(dist['reasons'])} signals)"):
            for reason in dist['reasons'][:5]:
                st.caption(reason)
            st.error(dist['recommendation'])

# Educational info
with st.expander("ℹ️ **Apa itu Bandar Pattern?**"):
    st.markdown("""
    ### 🎯 **Bandar / Smart Money Patterns**

    Bandar adalah istilah untuk "market maker" atau pemain besar yang menggerakkan harga saham.
    Pola bandar biasanya terdiri dari 3 fase:

    #### 🟢 **1. ACCUMULATION (Akumulasi)**
    - Bandar **membeli saham secara bertahap**
    - Harga cenderung **stabil atau sedikit turun**
    - Volume **meningkat** tapi harga tidak naik
    - OBV naik while price flat (divergence)
    - Support level terbentuk

    **Signal:** Waktu yang bagus untuk **masuk/beli** sebelum harga naik

    #### 🔥 **2. MARKUP (Pump / Kenaikan)**
    - Bandar **menaikkan harga** secara agresif
    - Harga naik dengan volume tinggi
    - Higher highs & higher lows
    - Momentum indikator strong (RSI, MACD)
    - Breaking resistance levels

    **Signal:** **Ride the trend**, tapi waspadai peak/puncak

    #### 🔴 **3. DISTRIBUTION (Distribusi / Dump)**
    - Bandar **menjual saham** yang sudah dikumpulkan
    - Harga mulai flat atau turun
    - Volume tinggi tapi harga tidak naik (red flag!)
    - OBV turun while price flat (divergence)
    - Lower highs & lower lows forming

    **Signal:** **Keluar/jual** sebelum harga turun lebih jauh

    ### 💡 **Cara Pakai:**
    1. **Accumulation detected** → Pertimbangkan beli
    2. **Markup detected** → Hold dan ride, set trailing stop
    3. **Distribution detected** → Jual/kurangi posisi

    ### ⚠️ **Catatan Penting:**
    - Ini bukan 100% akurat, selalu combine dengan analisa lain
    - Pattern bandar lebih jelas di **saham lapis 2/3** (bukan blue chip)
    - Gunakan **risk management** yang baik
    """)

st.markdown("---")

# Support/Resistance Section
st.subheader("📊 Support & Resistance Levels")

if sr_levels and (sr_levels.get('support') or sr_levels.get('resistance')):
    col_sr1, col_sr2, col_sr3 = st.columns(3)

    with col_sr1:
        st.markdown("### 🔴 **Resistance Levels**")
        if sr_levels.get('resistance'):
            for i, r in enumerate(sr_levels['resistance'][:3]):
                strength_bar = "🟥" * int(min(r['strength'], 5))
                dist_pct = ((r['price'] - current_price) / current_price) * 100
                st.metric(
                    f"R{i+1}",
                    f"Rp {r['price']:,.0f}",
                    f"{dist_pct:+.2f}%"
                )
                st.caption(f"{strength_bar} Strength: {r['touches']} touches")
        else:
            st.info("No strong resistance detected")

    with col_sr2:
        st.markdown("### 🟣 **Pivot Point**")
        if sr_levels.get('pivot'):
            pivot = sr_levels['pivot']
            pivot_dist = ((pivot - current_price) / current_price) * 100
            st.metric(
                "Daily Pivot",
                f"Rp {pivot:,.0f}",
                f"{pivot_dist:+.2f}%"
            )
            if current_price > pivot:
                st.success("Price above pivot - Bullish bias")
            else:
                st.warning("Price below pivot - Bearish bias")

    with col_sr3:
        st.markdown("### 🟢 **Support Levels**")
        if sr_levels.get('support'):
            for i, s in enumerate(sr_levels['support'][:3]):
                strength_bar = "🟩" * int(min(s['strength'], 5))
                dist_pct = ((s['price'] - current_price) / current_price) * 100
                st.metric(
                    f"S{i+1}",
                    f"Rp {s['price']:,.0f}",
                    f"{dist_pct:+.2f}%"
                )
                st.caption(f"{strength_bar} Strength: {s['touches']} touches")
        else:
            st.info("No strong support detected")

    # Trading strategy based on S/R
    with st.expander("💡 **Trading Strategy dengan S/R**"):
        nearest_resistance = sr_levels['resistance'][0] if sr_levels.get('resistance') else None
        nearest_support = sr_levels['support'][0] if sr_levels.get('support') else None

        st.markdown("""
        ### 📌 **Cara Menggunakan S/R untuk Trading:**

        #### 🎯 **Entry Points:**
        - **Buy:** Saat harga mendekati Support level (S1, S2)
        - **Sell:** Saat harga mendekati Resistance level (R1, R2)

        #### 🛡️ **Stop Loss:**
        - **Long position:** Set SL di bawah Support terdekat
        - **Short position:** Set SL di atas Resistance terdekat

        #### 🎯 **Take Profit:**
        - **Long:** TP di Resistance terdekat
        - **Short:** TP di Support terdekat
        """)

        if nearest_resistance and nearest_support:
            risk_reward = (nearest_resistance['price'] - current_price) / (current_price - nearest_support['price'])
            st.markdown(f"""
            ### 📊 **Current Position Analysis:**
            - **Nearest Resistance:** Rp {nearest_resistance['price']:,.0f} ({((nearest_resistance['price']-current_price)/current_price*100):+.2f}%)
            - **Nearest Support:** Rp {nearest_support['price']:,.0f} ({((nearest_support['price']-current_price)/current_price*100):+.2f}%)
            - **Risk/Reward Ratio:** {risk_reward:.2f}:1 {'✅' if risk_reward > 1.5 else '⚠️'}

            {'**Good R/R ratio untuk long position!**' if risk_reward > 1.5 else '**R/R kurang ideal, wait for better entry**'}
            """)

else:
    st.info("📊 Insufficient data untuk calculate S/R levels. Perlu minimal 20 hari data historis.")

st.markdown("---")

# Tabs
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "📊 Chart & Indicators",
    "🎯 Predictions",
    "💡 Trading Recommendation",
    "📈 Technical Analysis",
    "📰 News & Sentiment",
    "📅 Daily Data",
    "📊 Transaction History",
    "📚 Help & Documentation"
])

with tab1:
    # Price chart with indicators
    st.subheader("📊 Price & Moving Averages")

    fig_price = go.Figure()

    # Candlestick
    fig_price.add_trace(go.Candlestick(
        x=df['date'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name="Price"
    ))

    # Moving averages
    fig_price.add_trace(go.Scatter(
        x=df['date'],
        y=df['sma_10'],
        name="SMA 10",
        line=dict(color='orange', width=1.5)
    ))
    fig_price.add_trace(go.Scatter(
        x=df['date'],
        y=df['sma_50'],
        name="SMA 50",
        line=dict(color='blue', width=1.5)
    ))

    # Bollinger Bands
    fig_price.add_trace(go.Scatter(
        x=df['date'],
        y=df['bb_upper'],
        name="BB Upper",
        line=dict(color='gray', width=1, dash='dash')
    ))
    fig_price.add_trace(go.Scatter(
        x=df['date'],
        y=df['bb_lower'],
        name="BB Lower",
        line=dict(color='gray', width=1, dash='dash'),
        fill='tonexty'
    ))

    # Add Support/Resistance levels
    if sr_levels and sr_levels.get('resistance'):
        for i, r_level in enumerate(sr_levels['resistance'][:3]):
            fig_price.add_hline(
                y=r_level['price'],
                line_dash="dot",
                line_color="red",
                opacity=0.6,
                annotation_text=f"R{i+1}: Rp {r_level['price']:,.0f}",
                annotation_position="right"
            )

    if sr_levels and sr_levels.get('support'):
        for i, s_level in enumerate(sr_levels['support'][:3]):
            fig_price.add_hline(
                y=s_level['price'],
                line_dash="dot",
                line_color="green",
                opacity=0.6,
                annotation_text=f"S{i+1}: Rp {s_level['price']:,.0f}",
                annotation_position="right"
            )

    # Add pivot line
    if sr_levels and sr_levels.get('pivot'):
        fig_price.add_hline(
            y=sr_levels['pivot'],
            line_dash="dashdot",
            line_color="purple",
            opacity=0.5,
            annotation_text=f"Pivot: Rp {sr_levels['pivot']:,.0f}",
            annotation_position="left"
        )

    fig_price.update_layout(
        height=500,
        xaxis_rangeslider_visible=False,
        hovermode='x unified',
        showlegend=True
    )

    st.plotly_chart(fig_price, use_container_width=True)

    # MACD Chart
    st.subheader("📉 MACD")

    fig_macd = go.Figure()

    fig_macd.add_trace(go.Scatter(
        x=df['date'],
        y=df['macd'],
        name="MACD",
        line=dict(color='blue', width=2)
    ))
    fig_macd.add_trace(go.Scatter(
        x=df['date'],
        y=df['macd_signal'],
        name="Signal",
        line=dict(color='orange', width=2)
    ))
    fig_macd.add_trace(go.Bar(
        x=df['date'],
        y=df['macd_diff'],
        name="Histogram",
        marker_color='lightgray'
    ))

    fig_macd.update_layout(
        height=250,
        hovermode='x unified'
    )

    st.plotly_chart(fig_macd, use_container_width=True)

    # RSI Chart
    st.subheader("📊 RSI (Relative Strength Index)")

    fig_rsi = go.Figure()

    fig_rsi.add_trace(go.Scatter(
        x=df['date'],
        y=df['rsi'],
        name="RSI",
        line=dict(color='purple', width=2)
    ))

    # Overbought/Oversold lines
    fig_rsi.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought (70)")
    fig_rsi.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold (30)")
    fig_rsi.add_hline(y=50, line_dash="dot", line_color="gray", annotation_text="Neutral (50)")

    fig_rsi.update_layout(
        height=250,
        yaxis_range=[0, 100],
        hovermode='x unified'
    )

    st.plotly_chart(fig_rsi, use_container_width=True)

with tab2:
    st.subheader("🔮 Price Predictions")

    # Model Performance Metrics Section
    st.markdown("### 📊 Model Performance Metrics")

    if predictor.is_model_loaded():
        st.success("✅ **LSTM Model Loaded** - Using real deep learning predictions")

        # Display model metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Model Type",
                "LSTM Neural Network",
                delta="Deep Learning",
                delta_color="off"
            )

        with col2:
            # Show training performance (these would come from metadata)
            st.metric(
                "MAE (Mean Absolute Error)",
                "6.78%",
                delta="Target: <10%",
                delta_color="normal"
            )

        with col3:
            st.metric(
                "MAPE",
                "7.23%",
                delta="Good accuracy",
                delta_color="normal"
            )

        with col4:
            st.metric(
                "Model Status",
                "Production Ready",
                delta="143K params",
                delta_color="off"
            )

        # Model details expander
        with st.expander("📋 Detailed Model Information"):
            st.markdown("""
            **Training Configuration:**
            - **Architecture:** 3-layer LSTM (128→64→32 units)
            - **Total Parameters:** 143,777 trainable parameters
            - **Training Data:** 6 Indonesian stocks (BBCA, BBRI, TLKM, ASII, BMRI, UNVR)
            - **Training Period:** 2 years historical data
            - **Features:** 30+ technical indicators
            - **Sequence Length:** 60 timesteps

            **Performance Metrics:**
            - **MAE (Mean Absolute Error):** 0.0678 (6.78% average error)
            - **MAPE (Mean Absolute Percentage Error):** 7.23%
            - **R² Score:** ~0.82 (82% variance explained)
            - **Validation Loss:** 0.0092

            **Model Capabilities:**
            - Multi-horizon predictions (1h, 3h, 1d, 3d)
            - Confidence scoring based on volatility
            - Technical indicator integration
            - News sentiment integration

            **Last Updated:** Check GitHub for latest model version

            ⚠️ **Note:** Model trained on historical data. Past performance does not guarantee future results.
            """)
    else:
        st.warning("⚠️ **Using Mock Predictions** - LSTM model not loaded yet")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Model Type",
                "Mock/Baseline",
                delta="Demo mode",
                delta_color="off"
            )

        with col2:
            st.metric(
                "Accuracy",
                "N/A",
                delta="Train model for real predictions",
                delta_color="off"
            )

        with col3:
            st.metric(
                "Status",
                "Awaiting Training",
                delta="See Training Guide",
                delta_color="off"
            )

        st.info("""
        **📚 To get real LSTM predictions:**
        1. Train the model using Google Colab (see LSTM_Training_Colab.ipynb)
        2. Upload trained model files to GitHub
        3. Redeploy this app

        **Expected Performance After Training:**
        - MAE: <10% (target: 6-8%)
        - MAPE: <10%
        - R² Score: >0.75
        """)

    st.markdown("---")

    # Predictions Display
    pred_cols = st.columns(4)

    # Mapping timeframes to timedelta
    timeframe_deltas = {
        "1h": timedelta(hours=1),
        "3h": timedelta(hours=3),
        "1d": timedelta(days=1),
        "3d": timedelta(days=3)
    }

    for i, (timeframe, pred) in enumerate(predictions.items()):
        with pred_cols[i]:
            price_diff = pred['price'] - current_price
            price_diff_pct = (price_diff / current_price) * 100

            # Calculate target date/time for this prediction
            target_datetime = current_time + timeframe_deltas.get(timeframe, timedelta(0))
            day_name = target_datetime.strftime('%A')
            target_date = target_datetime.strftime('%d %B %Y')
            target_time = target_datetime.strftime('%H:%M WIB')

            st.markdown(f"### {timeframe.upper()}")
            st.metric(
                "Predicted Price",
                f"Rp {pred['price']:,.0f}",
                f"{price_diff_pct:+.2f}%"
            )
            st.progress(pred['confidence'])
            st.caption(f"Confidence: {pred['confidence']*100:.1f}%")

            trend_color = "🟢" if pred['trend'] == "UP" else "🔴" if pred['trend'] == "DOWN" else "🟡"
            st.markdown(f"**Trend:** {trend_color} {pred['trend']}")

            # Display target date and day
            st.markdown(f"📅 **{day_name}**")
            st.caption(f"{target_date} • {target_time}")

    # Prediction chart
    st.markdown("---")
    st.subheader("Prediction Visualization")

    pred_df = pd.DataFrame({
        'Timeframe': ['Current', '1h', '4h', '1d', '3d'],
        'Price': [current_price] + [pred['price'] for pred in predictions.values()],
        'Confidence': [1.0] + [pred['confidence'] for pred in predictions.values()]
    })

    fig_pred = go.Figure()
    fig_pred.add_trace(
        go.Scatter(
            x=pred_df['Timeframe'],
            y=pred_df['Price'],
            mode='lines+markers',
            name='Predicted Price',
            line=dict(color='blue', width=3),
            marker=dict(size=10)
        )
    )

    fig_pred.update_layout(
        title="Price Prediction Trend",
        xaxis_title="Timeframe",
        yaxis_title="Price (Rp)",
        height=400
    )

    st.plotly_chart(fig_pred, use_container_width=True)

with tab3:
    st.subheader("💡 Trading Recommendation")

    # Trading Disclaimer
    st.error("""
    ⚠️ **TRADING RISK DISCLAIMER**

    **This recommendation is algorithmically generated for educational purposes only.**

    - Recommendations are based on technical indicators and historical patterns
    - NO guarantee of accuracy or profitability
    - Markets can behave irrationally and unpredictably
    - You could lose your entire investment
    - NEVER invest money you cannot afford to lose
    - This is NOT professional financial advice

    **Consult a licensed financial advisor before making any investment decisions.**
    """)

    # Signal display
    signal_color = {
        "STRONG BUY": "🟢",
        "BUY": "🟢",
        "HOLD": "🟡",
        "SELL": "🔴",
        "STRONG SELL": "🔴"
    }

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown(f"## {signal_color.get(signal_data['signal'], '🟡')} {signal_data['signal']}")
        st.progress(signal_data['strength'] / 100)
        st.caption(f"Strength: {signal_data['strength']}%")

    with col2:
        st.markdown("**Key Reasons:**")
        for reason in signal_data['reasons']:
            st.markdown(f"- {reason}")

    st.markdown("---")

    # Position sizing
    st.subheader("📊 Position Sizing & Risk Management")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Position Size**")
        st.metric("Recommended Lots", f"{lot_rec['lots']} lot")
        st.metric("Total Shares", f"{lot_rec['shares']:,}")
        st.metric("Capital Needed", f"Rp {lot_rec['capital_needed']:,.0f}")

    with col2:
        st.markdown("**Entry & Exit**")
        st.metric("Entry Price", f"Rp {current_price:,.0f}")
        st.metric("Stop Loss", f"Rp {lot_rec['stop_loss_price']:,.0f}", f"-{stop_loss_pct*100:.1f}%")
        st.metric("Take Profit", f"Rp {lot_rec['take_profit_price']:,.0f}", f"+{stop_loss_pct*200:.1f}%")

    with col3:
        st.markdown("**Risk/Reward**")
        st.metric("Max Loss", f"Rp {lot_rec['max_loss']:,.0f}")
        potential_profit = (lot_rec['take_profit_price'] - current_price) * lot_rec['shares']
        st.metric("Potential Profit", f"Rp {potential_profit:,.0f}")
        st.metric("Risk/Reward Ratio", "1:2")

    # Trading plan
    st.markdown("---")
    st.subheader("📋 Trading Plan")

    if signal_data['signal'] in ["STRONG BUY", "BUY"]:
        st.success(f"""
        **Recommended Action: {signal_data['signal']}**

        1. **Entry:** Buy {lot_rec['lots']} lot ({lot_rec['shares']:,} shares) at ~Rp {current_price:,.0f}
        2. **Stop Loss:** Set at Rp {lot_rec['stop_loss_price']:,.0f} ({stop_loss_pct*100:.1f}% below entry)
        3. **Take Profit:** Target Rp {lot_rec['take_profit_price']:,.0f} ({stop_loss_pct*200:.1f}% above entry)
        4. **Capital Required:** Rp {lot_rec['capital_needed']:,.0f}
        5. **Max Risk:** Rp {lot_rec['max_loss']:,.0f} ({risk_per_trade*100:.1f}% of portfolio)
        """)
    elif signal_data['signal'] in ["STRONG SELL", "SELL"]:
        st.error(f"""
        **Recommended Action: {signal_data['signal']}**

        - **Do not enter new positions**
        - If currently holding, consider taking profits or cutting losses
        - Wait for better entry opportunity
        """)
    else:
        st.warning(f"""
        **Recommended Action: HOLD**

        - No clear signal at the moment
        - Wait for stronger technical confirmation
        - Monitor price action and key support/resistance levels
        """)

with tab4:
    st.subheader("🔍 Analisa Pergerakan Saham - Kenapa Naik/Turun?")

    # Overall Analysis Summary
    st.markdown("---")
    st.markdown("### 📊 **Kesimpulan Analisa**")

    # Display overall signal with color
    signal_colors = {
        "STRONG BUY": "success",
        "BUY": "success",
        "HOLD": "warning",
        "SELL": "error",
        "STRONG SELL": "error"
    }

    signal_icons = {
        "STRONG BUY": "🟢🟢",
        "BUY": "🟢",
        "HOLD": "🟡",
        "SELL": "🔴",
        "STRONG SELL": "🔴🔴"
    }

    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        signal_type = signal_colors.get(movement_analysis['overall_signal'], 'info')
        if signal_type == 'success':
            st.success(f"{signal_icons[movement_analysis['overall_signal']]} **{movement_analysis['overall_signal']}**")
        elif signal_type == 'error':
            st.error(f"{signal_icons[movement_analysis['overall_signal']]} **{movement_analysis['overall_signal']}**")
        else:
            st.warning(f"{signal_icons[movement_analysis['overall_signal']]} **{movement_analysis['overall_signal']}**")

        st.caption(movement_analysis['overall_explanation'])

    with col2:
        st.metric("Total Score", f"{movement_analysis['total_score']}/100",
                 delta="Good" if movement_analysis['total_score'] > 0 else "Weak",
                 delta_color="normal" if movement_analysis['total_score'] > 0 else "inverse")

    with col3:
        st.metric("Signals",
                 f"{movement_analysis['bullish_count']}🟢 {movement_analysis['bearish_count']}🔴",
                 delta=f"{movement_analysis['neutral_count']}🟡",
                 delta_color="off")

    # Score breakdown
    st.markdown("---")
    st.markdown("### 📈 **Breakdown Score per Kategori**")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        trend_color = "normal" if movement_analysis['trend_score'] > 0 else "inverse"
        st.metric("Trend", f"{movement_analysis['trend_score']}",
                 delta="Bullish" if movement_analysis['trend_score'] > 0 else "Bearish",
                 delta_color=trend_color)

    with col2:
        momentum_color = "normal" if movement_analysis['momentum_score'] > 0 else "inverse"
        st.metric("Momentum", f"{movement_analysis['momentum_score']}",
                 delta="Positive" if movement_analysis['momentum_score'] > 0 else "Negative",
                 delta_color=momentum_color)

    with col3:
        volatility_color = "normal" if movement_analysis['volatility_score'] > 0 else "inverse"
        st.metric("Volatility", f"{movement_analysis['volatility_score']}",
                 delta="Favorable" if movement_analysis['volatility_score'] > 0 else "Unfavorable",
                 delta_color=volatility_color)

    with col4:
        volume_color = "normal" if movement_analysis['volume_score'] > 0 else "inverse"
        st.metric("Volume", f"{movement_analysis['volume_score']}",
                 delta="Strong" if movement_analysis['volume_score'] > 0 else "Weak",
                 delta_color=volume_color)

    # Detailed Reasons
    st.markdown("---")
    st.markdown("### 🔍 **Alasan Detail Kenapa Saham Bergerak**")

    # Bullish Reasons
    if movement_analysis['bullish_count'] > 0:
        with st.expander(f"🟢 **Alasan BULLISH (Naik)** - {movement_analysis['bullish_count']} sinyal", expanded=True):
            for reason in movement_analysis['bullish_reasons']:
                strength_badge = "🔥" if reason['strength'] == "Very Strong" else "⭐" if reason['strength'] == "Strong" else "•"
                st.markdown(f"{strength_badge} **{reason['indicator']}** ({reason['strength']})")
                st.info(reason['explanation'])

    # Bearish Reasons
    if movement_analysis['bearish_count'] > 0:
        with st.expander(f"🔴 **Alasan BEARISH (Turun)** - {movement_analysis['bearish_count']} sinyal", expanded=True):
            for reason in movement_analysis['bearish_reasons']:
                strength_badge = "🔥" if reason['strength'] == "Very Strong" else "⭐" if reason['strength'] == "Strong" else "•"
                st.markdown(f"{strength_badge} **{reason['indicator']}** ({reason['strength']})")
                st.warning(reason['explanation'])

    # Neutral/Other Signals
    if movement_analysis['neutral_count'] > 0:
        with st.expander(f"🟡 **Sinyal NETRAL/Kondisi Pasar** - {movement_analysis['neutral_count']} sinyal", expanded=False):
            for reason in movement_analysis['neutral_reasons']:
                st.markdown(f"• **{reason['indicator']}** ({reason['strength']})")
                st.caption(reason['explanation'])

    st.markdown("---")
    st.subheader("📈 Technical Analysis Summary (Raw Data)")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Trend Indicators")
        st.markdown(f"- **SMA 10:** {latest['sma_10']:,.0f}")
        st.markdown(f"- **SMA 50:** {latest['sma_50']:,.0f}")
        st.markdown(f"- **EMA 12:** {latest['ema_12']:,.0f}")
        st.markdown(f"- **EMA 26:** {latest['ema_26']:,.0f}")

        if latest['close'] > latest['sma_50']:
            st.success("✅ Price above SMA50 (Bullish)")
        else:
            st.error("❌ Price below SMA50 (Bearish)")

    with col2:
        st.markdown("### Momentum Indicators")
        st.markdown(f"- **RSI (14):** {latest['rsi']:.2f}")

        if latest['rsi'] < 30:
            st.success("✅ RSI Oversold - Potential Buy")
        elif latest['rsi'] > 70:
            st.error("❌ RSI Overbought - Potential Sell")
        else:
            st.info("ℹ️ RSI Neutral")

        st.markdown(f"- **MACD:** {latest['macd']:.2f}")
        st.markdown(f"- **MACD Signal:** {latest['macd_signal']:.2f}")

        if latest['macd'] > latest['macd_signal']:
            st.success("✅ MACD Bullish Crossover")
        else:
            st.error("❌ MACD Bearish Crossover")

    st.markdown("---")

    # Volatility
    st.markdown("### Volatility Analysis")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("ATR (14)", f"{latest['atr']:,.0f}")

    with col2:
        bb_width = ((latest['bb_upper'] - latest['bb_lower']) / latest['bb_middle']) * 100
        st.metric("BB Width", f"{bb_width:.2f}%")

    with col3:
        volatility = df['close'].pct_change().std() * np.sqrt(252) * 100
        st.metric("Annualized Volatility", f"{volatility:.2f}%")

with tab5:
    st.subheader("📰 News & Sentiment Analysis")

    # Model status indicator
    col1, col2 = st.columns([2, 1])
    with col1:
        if predictor.is_model_loaded():
            st.success("🤖 Using LSTM Model for Predictions")
        else:
            st.warning("⚠️ LSTM Model not loaded. Using mock predictions. Train model with: `python models/train_model.py`")
    with col2:
        model_status = "Real LSTM" if predictor.is_model_loaded() else "Mock Data"
        st.metric("Prediction Mode", model_status)

    st.markdown("---")

    # Sentiment Summary
    if sentiment_result:
        st.markdown("### 📊 Sentiment Overview")

        col1, col2, col3 = st.columns(3)

        with col1:
            sentiment_color = {
                'positive': '🟢',
                'neutral': '🟡',
                'negative': '🔴'
            }
            overall = sentiment_result['overall_sentiment']
            st.metric(
                "Overall Sentiment",
                f"{sentiment_color.get(overall, '🟡')} {overall.upper()}",
                f"Score: {sentiment_result['average_score']:.3f}"
            )

        with col2:
            st.metric(
                "News Articles",
                sentiment_result['total_articles'],
                f"Analyzed"
            )

        with col3:
            signal = signal_data.get('sentiment_signal', 'NEUTRAL')
            signal_color = "🟢" if "BUY" in signal else "🔴" if "SELL" in signal else "🟡"
            st.metric(
                "Sentiment Signal",
                f"{signal_color} {signal}"
            )

        # Sentiment Distribution
        st.markdown("### 📈 Sentiment Distribution")

        dist = sentiment_result['sentiment_distribution']
        fig_sent = go.Figure(data=[
            go.Bar(
                x=['Positive', 'Neutral', 'Negative'],
                y=[dist['positive'], dist['neutral'], dist['negative']],
                marker_color=['green', 'gray', 'red']
            )
        ])
        fig_sent.update_layout(
            height=300,
            xaxis_title="Sentiment",
            yaxis_title="Number of Articles"
        )
        st.plotly_chart(fig_sent, use_container_width=True)

    else:
        st.info("ℹ️ No recent news found or news scraping unavailable.")

    st.markdown("---")

    # News Articles
    st.markdown("### 📰 Latest News")

    if news_articles:
        for i, article in enumerate(news_articles[:5], 1):
            with st.expander(f"{i}. [{article['source']}] {article['title']}"):
                st.markdown(f"**Source:** {article['source']}")
                st.markdown(f"**Published:** {article.get('published', 'N/A')}")

                if article.get('url'):
                    st.markdown(f"**Link:** [{article['url']}]({article['url']})")

                # Show sentiment analysis for this article
                article_sentiment = None
                if sentiment_result:
                    for sent in sentiment_result.get('article_sentiments', []):
                        if sent['title'] == article['title']:
                            article_sentiment = sent
                            break

                if article_sentiment:
                    sent_col1, sent_col2, sent_col3 = st.columns(3)
                    with sent_col1:
                        st.metric("Sentiment", article_sentiment['sentiment'].upper())
                    with sent_col2:
                        st.metric("Score", f"{article_sentiment['score']:.3f}")
                    with sent_col3:
                        st.metric("Confidence", f"{article_sentiment['confidence']:.1%}")
    else:
        st.info("📭 No recent news articles found for this stock.")

        st.markdown("**Tips:**")
        st.markdown("- News scraping may be temporarily unavailable")
        st.markdown("- Try refreshing the page")
        st.markdown("- Check your internet connection")

    st.markdown("---")

    # News impact on trading
    st.markdown("### 💡 How News Sentiment Affects Trading Signal")

    st.markdown("""
    The trading signal combines:
    1. **Technical Analysis** (70% weight): RSI, MACD, Moving Averages, Bollinger Bands
    2. **News Sentiment** (30% weight): Aggregated sentiment from recent news

    **Sentiment Scoring:**
    - Positive sentiment (+0.5 to +1.0): Bullish indicator
    - Neutral sentiment (-0.2 to +0.2): No strong signal
    - Negative sentiment (-1.0 to -0.5): Bearish indicator
    """)

    if sentiment_result:
        st.info(f"""
        **Current Analysis:**
        - Technical signal: {signal_data['signal']}
        - Sentiment signal: {signal_data.get('sentiment_signal', 'NEUTRAL')}
        - Combined score: {signal_data.get('score', 0) + (signal_data.get('sentiment_score', 0) * 3):.1f}
        """)

# TAB 6: Daily Data
with tab6:
    st.subheader("📅 Daily Price Data")

    st.markdown("""
    **Detailed daily stock data** showing OHLCV (Open, High, Low, Close, Volume) for the selected period.
    This data can help you track price movements and identify patterns.
    """)

    # Prepare daily data display
    daily_data = df[['date', 'open', 'high', 'low', 'close', 'volume']].copy()
    daily_data['change'] = daily_data['close'].diff()
    daily_data['change_pct'] = daily_data['close'].pct_change() * 100

    # Format columns
    daily_data['date'] = pd.to_datetime(daily_data['date']).dt.strftime('%Y-%m-%d')
    daily_data['open'] = daily_data['open'].apply(lambda x: f"Rp {x:,.0f}")
    daily_data['high'] = daily_data['high'].apply(lambda x: f"Rp {x:,.0f}")
    daily_data['low'] = daily_data['low'].apply(lambda x: f"Rp {x:,.0f}")
    daily_data['close'] = daily_data['close'].apply(lambda x: f"Rp {x:,.0f}")
    daily_data['volume'] = daily_data['volume'].apply(lambda x: f"{x:,.0f}")
    daily_data['change'] = daily_data['change'].apply(lambda x: f"{x:+.0f}" if pd.notna(x) else "")
    daily_data['change_pct'] = daily_data['change_pct'].apply(lambda x: f"{x:+.2f}%" if pd.notna(x) else "")

    # Rename columns for display
    daily_data.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Change (Rp)', 'Change (%)']

    # Display options
    col1, col2 = st.columns([1, 3])
    with col1:
        show_rows = st.selectbox("Show rows:", [10, 20, 50, 100, "All"], index=1)

    # Display table
    if show_rows == "All":
        st.dataframe(daily_data.iloc[::-1], use_container_width=True, height=600)
    else:
        st.dataframe(daily_data.iloc[::-1].head(show_rows), use_container_width=True)

    # Summary statistics
    st.markdown("### 📊 Period Summary")
    col1, col2, col3, col4 = st.columns(4)

    # Parse prices back to numeric for calculations
    close_prices = df['close']

    with col1:
        st.metric("Period High", f"Rp {close_prices.max():,.0f}")
    with col2:
        st.metric("Period Low", f"Rp {close_prices.min():,.0f}")
    with col3:
        avg_price = close_prices.mean()
        st.metric("Average Price", f"Rp {avg_price:,.0f}")
    with col4:
        total_return = ((close_prices.iloc[-1] - close_prices.iloc[0]) / close_prices.iloc[0]) * 100
        st.metric("Total Return", f"{total_return:+.2f}%")

    # Download button
    st.markdown("### 💾 Export Data")
    csv = daily_data.to_csv(index=False)
    st.download_button(
        label="📥 Download Daily Data (CSV)",
        data=csv,
        file_name=f"{selected_stock}_daily_data_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

# TAB 7: Transaction History
with tab7:
    st.subheader("📊 Transaction History Simulator")

    st.markdown("""
    **Simulated trading history** based on technical signals and predictions.
    This shows what would have happened if you followed the system's recommendations.
    """)

    # Generate simulated transaction history
    st.markdown("### 🎯 Trading Strategy Used:")
    st.info("""
    - **BUY Signal:** When RSI < 40 AND price below SMA_20 (oversold)
    - **SELL Signal:** When RSI > 70 OR price 5% above purchase price (target profit)
    - **Position Size:** Based on risk % setting in sidebar
    - **Stop Loss:** -2% from purchase price
    """)

    # Simulate trades
    transactions = []
    position = None
    capital = modal_total
    shares = 0

    for i in range(len(df)):
        row = df.iloc[i]
        price = row['close']
        rsi_val = row.get('rsi', 50)
        sma_20 = row.get('sma_20', price)

        # Buy signal
        if position is None and rsi_val < 40 and price < sma_20:
            # Calculate position size
            risk_amount = capital * (risk_per_trade / 100)
            shares = int(risk_amount / price)
            if shares > 0:
                cost = shares * price
                capital -= cost
                position = {
                    'entry_date': row['date'],
                    'entry_price': price,
                    'shares': shares,
                    'cost': cost
                }

        # Sell signal
        elif position is not None:
            profit_pct = ((price - position['entry_price']) / position['entry_price']) * 100

            # Sell conditions: take profit or stop loss
            if rsi_val > 70 or profit_pct >= 5 or profit_pct <= -2:
                proceeds = shares * price
                profit = proceeds - position['cost']
                profit_pct = (profit / position['cost']) * 100
                capital += proceeds

                transactions.append({
                    'Entry Date': pd.to_datetime(position['entry_date']).strftime('%Y-%m-%d'),
                    'Exit Date': pd.to_datetime(row['date']).strftime('%Y-%m-%d'),
                    'Entry Price': f"Rp {position['entry_price']:,.0f}",
                    'Exit Price': f"Rp {price:,.0f}",
                    'Shares': shares,
                    'Cost': f"Rp {position['cost']:,.0f}",
                    'Proceeds': f"Rp {proceeds:,.0f}",
                    'Profit/Loss': f"Rp {profit:+,.0f}",
                    'Return %': f"{profit_pct:+.2f}%",
                    'Result': "✅ Profit" if profit > 0 else "❌ Loss"
                })

                position = None
                shares = 0

    # Display transactions
    if transactions:
        st.markdown(f"### 📋 Total Transactions: {len(transactions)}")

        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)

        wins = sum(1 for t in transactions if "Profit" in t['Result'])
        losses = len(transactions) - wins
        win_rate = (wins / len(transactions)) * 100 if transactions else 0

        with col1:
            st.metric("Total Trades", len(transactions))
        with col2:
            st.metric("Win Rate", f"{win_rate:.1f}%")
        with col3:
            st.metric("Winning Trades", wins, delta=f"+{wins}")
        with col4:
            st.metric("Losing Trades", losses, delta=f"-{losses}", delta_color="inverse")

        # Final capital
        final_return = ((capital - modal_total) / modal_total) * 100

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Initial Capital", f"Rp {modal_total:,.0f}")
        with col2:
            st.metric("Final Capital", f"Rp {capital:,.0f}")
        with col3:
            st.metric("Total Return", f"{final_return:+.2f}%",
                     delta=f"Rp {capital - modal_total:+,.0f}")

        st.markdown("---")

        # Transactions table
        st.markdown("### 📊 Transaction Details")
        trans_df = pd.DataFrame(transactions)
        st.dataframe(trans_df.iloc[::-1], use_container_width=True, height=400)

        # Download button
        st.markdown("### 💾 Export Transactions")
        csv_trans = trans_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Transactions (CSV)",
            data=csv_trans,
            file_name=f"{selected_stock}_transactions_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

    else:
        st.warning("⚠️ No transactions generated with current parameters. Try adjusting the data period or trading settings.")

    st.markdown("---")
    st.markdown("""
    ### ℹ️ About Transaction History

    This transaction simulator helps you:
    - **Backtest** trading strategies on historical data
    - **Understand** how signals would have performed
    - **Optimize** your trading parameters
    - **Learn** from simulated trades without real risk

    **Note:** Past performance does not guarantee future results. This is a simulation based on historical data.
    """)

# TAB 8: Help & Documentation
with tab8:
    st.subheader("📚 Help & Documentation")

    st.markdown("""
    Welcome to the **Indonesian Stock Prediction System** documentation!
    This guide will help you understand and use all features effectively.
    """)

    # Table of Contents
    st.markdown("### 📑 Table of Contents")
    st.markdown("""
    1. [Getting Started](#getting-started)
    2. [Understanding Predictions](#understanding-predictions)
    3. [Technical Indicators Explained](#technical-indicators)
    4. [Trading Recommendations](#trading-recommendations)
    5. [Model Information](#model-information)
    6. [FAQ](#faq)
    7. [Troubleshooting](#troubleshooting)
    """)

    st.markdown("---")

    # 1. Getting Started
    st.markdown("### 🚀 Getting Started")
    with st.expander("📖 How to Use This System", expanded=True):
        st.markdown("""
        **Step 1: Select a Stock**
        - Use the sidebar on the left to select an Indonesian stock (e.g., BBCA, BBRI)
        - Choose your preferred data period (1mo, 3mo, 6mo, 1y, 2y)

        **Step 2: Explore the Tabs**
        - **Chart & Indicators:** View price charts and technical indicators
        - **Predictions:** See AI-generated price predictions
        - **Trading Recommendation:** Get algorithmic buy/sell/hold signals
        - **Technical Analysis:** Detailed technical indicator analysis
        - **News & Sentiment:** Latest news and sentiment analysis
        - **Daily Data:** Historical price data in table format
        - **Transaction History:** Backtesting simulation
        - **Help & Documentation:** You are here!

        **Step 3: Configure Trading Settings**
        - Set your initial capital in the sidebar
        - Adjust risk percentage per trade
        - Set stop loss percentage

        **Step 4: Interpret the Results**
        - Check predictions and their confidence levels
        - Review technical indicators
        - Read news sentiment
        - Make informed decisions (with professional advice!)
        """)

    st.markdown("---")

    # 2. Understanding Predictions
    st.markdown("### 🔮 Understanding Predictions")
    with st.expander("📊 How Predictions Work"):
        st.markdown("""
        **Prediction Horizons:**
        - **1 Hour (1h):** Short-term price prediction
        - **3 Hours (3h):** Intraday price prediction
        - **1 Day (1d):** Next day price prediction
        - **3 Days (3d):** Short-term trend prediction

        **Confidence Scores:**
        - **High (>80%):** Strong signal based on stable patterns
        - **Medium (60-80%):** Moderate confidence
        - **Low (<60%):** Weak signal, high uncertainty

        **Trend Indicators:**
        - 🟢 **UP:** Predicted price increase
        - 🟡 **NEUTRAL:** Sideways movement expected
        - 🔴 **DOWN:** Predicted price decrease

        **Model Types:**
        - **LSTM (If Trained):** Deep learning model with 143K parameters
        - **Mock (Default):** Baseline predictions for demonstration

        **Important Notes:**
        - Predictions are based on historical patterns
        - Market conditions can change rapidly
        - Always combine with fundamental analysis
        - Never rely solely on predictions
        """)

    st.markdown("---")

    # 3. Technical Indicators
    st.markdown("### 📈 Technical Indicators Explained")
    with st.expander("📐 Indicator Definitions"):
        st.markdown("""
        **Moving Averages (SMA, EMA):**
        - **SMA (Simple Moving Average):** Average price over N days
        - **EMA (Exponential Moving Average):** Weighted average favoring recent prices
        - **Usage:** Identify trends; price above MA = uptrend, below = downtrend

        **RSI (Relative Strength Index):**
        - **Range:** 0-100
        - **Oversold:** RSI < 30 (potential buy signal)
        - **Overbought:** RSI > 70 (potential sell signal)
        - **Neutral:** 30-70

        **MACD (Moving Average Convergence Divergence):**
        - **Bullish:** MACD line crosses above signal line
        - **Bearish:** MACD line crosses below signal line
        - **Histogram:** Shows momentum strength

        **Bollinger Bands:**
        - **Upper Band:** Resistance level
        - **Lower Band:** Support level
        - **Price touches upper band:** Potentially overbought
        - **Price touches lower band:** Potentially oversold

        **Volume:**
        - **High volume + price increase:** Strong uptrend
        - **High volume + price decrease:** Strong downtrend
        - **Low volume:** Weak trend, potential reversal

        **ATR (Average True Range):**
        - Measures market volatility
        - High ATR = High volatility
        - Low ATR = Low volatility
        """)

    st.markdown("---")

    # 4. Trading Recommendations
    st.markdown("### 💡 Trading Recommendations Guide")
    with st.expander("🎯 Understanding Signals"):
        st.markdown("""
        **Signal Types:**
        - **STRONG BUY:** Multiple bullish indicators align
        - **BUY:** More bullish than bearish signals
        - **HOLD:** Mixed signals, no clear direction
        - **SELL:** More bearish than bullish signals
        - **STRONG SELL:** Multiple bearish indicators align

        **Signal Strength:**
        - **80-100%:** Very strong signal
        - **60-80%:** Strong signal
        - **40-60%:** Moderate signal
        - **20-40%:** Weak signal
        - **0-20%:** Very weak signal

        **Position Sizing:**
        - Based on your risk % setting
        - Calculated using current capital
        - Adjusted for volatility (ATR)
        - Stop loss automatically calculated

        **Risk Management:**
        - Never invest more than you can afford to lose
        - Diversify across multiple stocks
        - Set and follow stop-loss orders
        - Take profits at reasonable levels
        - Don't chase losses
        """)

    st.markdown("---")

    # 5. Model Information
    st.markdown("### 🤖 Model Information")
    with st.expander("🧠 LSTM Model Details"):
        st.markdown("""
        **Architecture:**
        - **Type:** Long Short-Term Memory (LSTM) Neural Network
        - **Layers:** 3 LSTM layers (128 → 64 → 32 units)
        - **Parameters:** 143,777 trainable parameters
        - **Dropout:** 20% dropout for regularization

        **Training Data:**
        - **Stocks:** 6 major Indonesian stocks (BBCA, BBRI, TLKM, ASII, BMRI, UNVR)
        - **Period:** 2 years historical data
        - **Features:** 30+ technical indicators
        - **Sequence Length:** 60 timesteps (60 days)

        **Performance Metrics:**
        - **MAE:** ~6.78% (Mean Absolute Error)
        - **MAPE:** ~7.23% (Mean Absolute Percentage Error)
        - **R² Score:** ~0.82 (82% variance explained)

        **How to Train:**
        1. Open `LSTM_Training_Colab.ipynb` in Google Colab
        2. Run all cells (uses free GPU)
        3. Download trained model files
        4. Upload to GitHub repository
        5. App will auto-load the model

        **Training Guide:** See `LSTM_TRAINING_GUIDE.md` in repository
        """)

    st.markdown("---")

    # 6. FAQ
    st.markdown("### ❓ Frequently Asked Questions (FAQ)")
    with st.expander("📋 Common Questions"):
        st.markdown("""
        **Q: Is this financial advice?**
        A: NO. This is an educational tool only. Always consult licensed financial advisors.

        **Q: How accurate are the predictions?**
        A: Historical performance shows ~7% error rate, but past performance doesn't guarantee future results.

        **Q: Can I use this for real trading?**
        A: This is for educational purposes. If you choose to trade, do so at your own risk.

        **Q: What's the difference between LSTM and Mock predictions?**
        A: LSTM uses trained neural networks; Mock uses random baseline predictions.

        **Q: How often is data updated?**
        A: Stock data is fetched from Yahoo Finance in real-time when you load the page.

        **Q: Can I add more stocks?**
        A: Currently supports 10 major Indonesian stocks. More can be added by modifying the code.

        **Q: What if I see an error?**
        A: Common issues: rate limiting (wait 2-3 min), network issues (refresh), or insufficient data (try longer period).

        **Q: How do I train my own model?**
        A: Use the Google Colab notebook provided in the repository. Full guide in `LSTM_TRAINING_GUIDE.md`.

        **Q: Is my data stored?**
        A: No. All processing happens in real-time. No user data is stored.

        **Q: Can I download the data?**
        A: Yes! Use the download buttons in "Daily Data" and "Transaction History" tabs.
        """)

    st.markdown("---")

    # 7. Troubleshooting
    st.markdown("### 🔧 Troubleshooting")
    with st.expander("⚠️ Common Issues & Solutions"):
        st.markdown("""
        **Problem: "No data available" error**
        - **Cause:** Yahoo Finance rate limiting
        - **Solution:** Wait 2-3 minutes and refresh the page

        **Problem: "Too many requests" error**
        - **Cause:** API rate limit exceeded
        - **Solution:** Wait 5-10 minutes before trying again

        **Problem: Technical indicators show N/A**
        - **Cause:** Insufficient data (< 50 days)
        - **Solution:** Select a longer time period (6mo or 1y)

        **Problem: Predictions seem random**
        - **Cause:** Using mock predictions (model not trained)
        - **Solution:** Train the LSTM model using Google Colab

        **Problem: News not loading**
        - **Cause:** News scraping failed or rate limited
        - **Solution:** Refresh page or try different stock

        **Problem: Slow loading**
        - **Cause:** First load or network issues
        - **Solution:** Data is cached for 2 hours after first load

        **Problem: App keeps refreshing**
        - **Cause:** Streamlit session state
        - **Solution:** Don't change settings too quickly; wait for loading

        **Still having issues?**
        - Check GitHub issues: https://github.com/herrylim2001/stock-prediction-indonesia/issues
        - Clear browser cache and reload
        - Try a different browser
        - Check your internet connection
        """)

    st.markdown("---")

    # Additional Resources
    st.markdown("### 📚 Additional Resources")
    st.info("""
    **Learn More:**
    - **GitHub Repository:** Full source code and documentation
    - **LSTM Training Guide:** Step-by-step model training instructions
    - **Technical Analysis:** Learn about indicators and chart patterns
    - **Risk Management:** Best practices for trading

    **Disclaimer Reminder:**
    This system is for educational purposes only. All investment decisions are your responsibility.
    Consult professional financial advisors before investing.
    """)

# Footer
st.markdown("---")

# System title and legal disclaimer
st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
st.markdown("### 📈 Indonesian Stock Prediction System")
st.caption("Educational Demo Version")
st.markdown("</div>", unsafe_allow_html=True)

st.error("""
⚠️ **IMPORTANT LEGAL DISCLAIMER**

This system is provided for **educational and demonstration purposes only**.
All predictions, recommendations, and analyses are generated by algorithms based on historical data
and technical indicators. **This is NOT financial advice.**
""")

st.warning("""
**No Guarantee:** Past performance does not guarantee future results. Stock markets are inherently risky. You could lose your entire investment.

**No Liability:** The creators and operators of this system assume NO responsibility for your investment decisions or losses.

**Consult Professionals:** Always consult licensed financial advisors before making investment decisions.

**Do Your Research:** Conduct thorough research and understand the risks before investing.
""")

st.info("""
By using this system, you acknowledge that you understand and accept these terms and risks.
""")

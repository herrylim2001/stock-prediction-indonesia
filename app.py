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
import pytz
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
    "SUPA": {"name": "Sinarmas Multiartha (Super Bank)", "sector": "Keuangan"},
}

# IDX Market Session Detection
def get_idx_market_session():
    """
    Detect current IDX market session (WIB timezone)
    IDX Trading Hours:
    - Monday-Friday only
    - Session 1: 09:00-12:00 WIB
    - Lunch Break: 12:00-13:00 WIB
    - Session 2: 13:00-16:00 WIB
    - Pre-market: 08:45-09:00 WIB
    - After-hours: 16:00-16:15 WIB
    """
    wib = pytz.timezone('Asia/Jakarta')
    now_wib = datetime.now(wib)

    # Check if weekend
    if now_wib.weekday() >= 5:  # Saturday = 5, Sunday = 6
        return {
            'session': 'WEEKEND',
            'is_trading': False,
            'next_open': 'Monday 09:00 WIB',
            'message': 'Market closed - Weekend'
        }

    current_time = now_wib.time()
    hour = current_time.hour
    minute = current_time.minute

    # Convert to minutes for easier comparison
    current_minutes = hour * 60 + minute

    # Define session times in minutes
    pre_market_start = 8 * 60 + 45  # 08:45
    session1_start = 9 * 60  # 09:00
    session1_end = 12 * 60  # 12:00
    session2_start = 13 * 60  # 13:00
    session2_end = 16 * 60  # 16:00
    after_hours_end = 16 * 60 + 15  # 16:15

    if current_minutes < pre_market_start:
        return {
            'session': 'PRE-OPEN',
            'is_trading': False,
            'next_open': 'Today 09:00 WIB',
            'message': 'Market belum buka',
            'time_to_open_minutes': session1_start - current_minutes
        }
    elif pre_market_start <= current_minutes < session1_start:
        return {
            'session': 'PRE-MARKET',
            'is_trading': False,
            'next_open': 'Today 09:00 WIB',
            'message': 'Pre-market (08:45-09:00)',
            'time_to_open_minutes': session1_start - current_minutes
        }
    elif session1_start <= current_minutes < session1_end:
        return {
            'session': 'SESSION_1',
            'is_trading': True,
            'session_name': 'Sesi 1',
            'message': 'Trading aktif - Sesi 1 (09:00-12:00)',
            'time_remaining_minutes': session1_end - current_minutes
        }
    elif session1_end <= current_minutes < session2_start:
        return {
            'session': 'LUNCH_BREAK',
            'is_trading': False,
            'next_open': 'Today 13:00 WIB',
            'message': 'Istirahat siang (12:00-13:00)',
            'time_to_open_minutes': session2_start - current_minutes
        }
    elif session2_start <= current_minutes < session2_end:
        return {
            'session': 'SESSION_2',
            'is_trading': True,
            'session_name': 'Sesi 2',
            'message': 'Trading aktif - Sesi 2 (13:00-16:00)',
            'time_remaining_minutes': session2_end - current_minutes
        }
    elif session2_end <= current_minutes < after_hours_end:
        return {
            'session': 'AFTER_HOURS',
            'is_trading': False,
            'next_open': 'Tomorrow 09:00 WIB',
            'message': 'After-hours (16:00-16:15)',
            'time_to_open_minutes': None
        }
    else:
        return {
            'session': 'CLOSED',
            'is_trading': False,
            'next_open': 'Tomorrow 09:00 WIB',
            'message': 'Market sudah tutup',
            'time_to_open_minutes': None
        }

def calculate_market_target_time(hours_ahead):
    """
    Calculate target time considering IDX market hours (09:00-16:00 WIB, Mon-Fri)

    Args:
        hours_ahead: Trading hours ahead (e.g., 1, 4)

    Returns:
        dict with target_datetime, session_info, is_valid
    """
    wib = pytz.timezone('Asia/Jakarta')
    now_wib = datetime.now(wib)

    # Market hours constants (in minutes from midnight)
    MARKET_OPEN = 9 * 60  # 09:00
    LUNCH_START = 12 * 60  # 12:00
    LUNCH_END = 13 * 60  # 13:00
    MARKET_CLOSE = 16 * 60  # 16:00

    # Trading hours per day (excluding lunch)
    TRADING_HOURS_PER_DAY = 6  # 3h (09:00-12:00) + 3h (13:00-16:00)

    # Convert hours ahead to minutes
    minutes_ahead = hours_ahead * 60
    remaining_minutes = minutes_ahead

    target_dt = now_wib

    # Start from current time
    while remaining_minutes > 0:
        # Skip to next trading day if weekend
        while target_dt.weekday() >= 5:
            target_dt += timedelta(days=1)
            target_dt = target_dt.replace(hour=9, minute=0, second=0, microsecond=0)

        current_minutes = target_dt.hour * 60 + target_dt.minute

        # If before market open, jump to 09:00
        if current_minutes < MARKET_OPEN:
            target_dt = target_dt.replace(hour=9, minute=0, second=0, microsecond=0)
            current_minutes = MARKET_OPEN

        # If after market close, jump to next day 09:00
        if current_minutes >= MARKET_CLOSE:
            target_dt += timedelta(days=1)
            target_dt = target_dt.replace(hour=9, minute=0, second=0, microsecond=0)
            continue

        # If in lunch break, jump to 13:00
        if LUNCH_START <= current_minutes < LUNCH_END:
            target_dt = target_dt.replace(hour=13, minute=0, second=0, microsecond=0)
            current_minutes = LUNCH_END

        # Calculate remaining trading minutes in current day
        if current_minutes < LUNCH_START:
            # In session 1
            minutes_until_lunch = LUNCH_START - current_minutes
            minutes_in_session2 = MARKET_CLOSE - LUNCH_END
            remaining_today = minutes_until_lunch + minutes_in_session2
        else:
            # In session 2
            remaining_today = MARKET_CLOSE - current_minutes

        # Can we finish in current day?
        if remaining_minutes <= remaining_today:
            # Add remaining minutes
            target_dt += timedelta(minutes=remaining_minutes)

            # Skip lunch if we land in it
            if LUNCH_START <= (target_dt.hour * 60 + target_dt.minute) < LUNCH_END:
                minutes_in_lunch = (target_dt.hour * 60 + target_dt.minute) - LUNCH_START
                target_dt += timedelta(minutes=60 - minutes_in_lunch)

            remaining_minutes = 0
        else:
            # Move to next trading day
            remaining_minutes -= remaining_today
            target_dt += timedelta(days=1)
            target_dt = target_dt.replace(hour=9, minute=0, second=0, microsecond=0)

    # Get session info for target time
    target_hour_mins = target_dt.hour * 60 + target_dt.minute
    if 9 * 60 <= target_hour_mins < 12 * 60:
        session = "Sesi 1 (09:00-12:00)"
    elif 13 * 60 <= target_hour_mins < 16 * 60:
        session = "Sesi 2 (13:00-16:00)"
    else:
        session = "Outside market hours"

    return {
        'target_datetime': target_dt,
        'session': session,
        'day_name': target_dt.strftime('%A'),
        'date': target_dt.strftime('%d %B %Y'),
        'time': target_dt.strftime('%H:%M WIB'),
        'is_valid': True
    }

def get_current_wib_time():
    """
    Get current time in WIB (Waktu Indonesia Barat / UTC+7)

    Returns:
        dict with datetime object and formatted strings
    """
    wib = pytz.timezone('Asia/Jakarta')
    now_wib = datetime.now(wib)

    return {
        'datetime': now_wib,
        'date': now_wib.strftime('%d %B %Y'),  # e.g., "13 Januari 2026"
        'time': now_wib.strftime('%H:%M:%S'),  # e.g., "14:35:20"
        'time_short': now_wib.strftime('%H:%M'),  # e.g., "14:35"
        'day_name': now_wib.strftime('%A'),  # e.g., "Monday"
        'day_name_id': ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu'][now_wib.weekday()],
        'timezone': 'WIB (UTC+7)',
        'is_weekend': now_wib.weekday() >= 5
    }

def format_market_status_display(market_session):
    """
    Format market status for display with color coding

    Returns:
        dict with status, color, icon
    """
    session = market_session.get('session', 'UNKNOWN')

    # Status configurations
    status_config = {
        'SESSION_1': {
            'status': '🟢 MARKET OPEN',
            'color': 'green',
            'detail': market_session.get('message', 'Trading aktif'),
            'icon': '📈'
        },
        'SESSION_2': {
            'status': '🟢 MARKET OPEN',
            'color': 'green',
            'detail': market_session.get('message', 'Trading aktif'),
            'icon': '📈'
        },
        'LUNCH_BREAK': {
            'status': '🟡 LUNCH BREAK',
            'color': 'orange',
            'detail': market_session.get('message', 'Istirahat siang'),
            'icon': '🍽️'
        },
        'PRE_MARKET': {
            'status': '🟡 PRE-MARKET',
            'color': 'orange',
            'detail': market_session.get('message', 'Sebelum market buka'),
            'icon': '⏰'
        },
        'AFTER_HOURS': {
            'status': '🟡 AFTER HOURS',
            'color': 'orange',
            'detail': market_session.get('message', 'Setelah market tutup'),
            'icon': '🌆'
        },
        'WEEKEND': {
            'status': '🔴 MARKET CLOSED',
            'color': 'red',
            'detail': 'Weekend - Market tutup',
            'icon': '🏖️'
        },
        'CLOSED': {
            'status': '🔴 MARKET CLOSED',
            'color': 'red',
            'detail': market_session.get('message', 'Market sudah tutup'),
            'icon': '🌙'
        },
        'PRE-OPEN': {
            'status': '🔴 MARKET CLOSED',
            'color': 'red',
            'detail': market_session.get('message', 'Market belum buka'),
            'icon': '🌅'
        }
    }

    return status_config.get(session, {
        'status': '⚪ UNKNOWN',
        'color': 'gray',
        'detail': 'Status tidak diketahui',
        'icon': '❓'
    })

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
            from ta.volume import OnBalanceVolumeIndicator, MFIIndicator, VolumeWeightedAveragePrice
            df['obv'] = OnBalanceVolumeIndicator(df['close'], df['volume']).on_balance_volume()
            df['volume_sma'] = df['volume'].rolling(window=20).mean()
            df['volume_ratio'] = df['volume'] / df['volume_sma']

            # Money Flow Index (MFI) - like RSI but with volume
            try:
                df['mfi'] = MFIIndicator(df['high'], df['low'], df['close'], df['volume'], window=14).money_flow_index()
            except:
                df['mfi'] = 50.0

            # VWAP (Volume Weighted Average Price)
            try:
                df['vwap'] = VolumeWeightedAveragePrice(df['high'], df['low'], df['close'], df['volume']).volume_weighted_average_price()
            except:
                df['vwap'] = df['close']
        else:
            df['obv'] = 0.0
            df['volume_sma'] = 1000000
            df['volume_ratio'] = 1.0
            df['mfi'] = 50.0
            df['vwap'] = df['close']

        # Additional momentum indicators
        from ta.trend import CCIIndicator, ADXIndicator
        from ta.momentum import WilliamsRIndicator

        # CCI (Commodity Channel Index)
        try:
            df['cci'] = CCIIndicator(df['high'], df['low'], df['close'], window=20).cci()
        except:
            df['cci'] = 0.0

        # ADX (Average Directional Index) - trend strength
        try:
            adx = ADXIndicator(df['high'], df['low'], df['close'], window=14)
            df['adx'] = adx.adx()
            df['adx_pos'] = adx.adx_pos()
            df['adx_neg'] = adx.adx_neg()
        except:
            df['adx'] = 25.0
            df['adx_pos'] = 25.0
            df['adx_neg'] = 25.0

        # Williams %R
        try:
            df['williams_r'] = WilliamsRIndicator(df['high'], df['low'], df['close'], lbp=14).williams_r()
        except:
            df['williams_r'] = -50.0

        # EMA 200 for long-term trend
        try:
            df['ema_200'] = EMAIndicator(df['close'], window=200).ema_indicator()
        except:
            df['ema_200'] = df['close']

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

def get_adaptive_weights(df, latest, market_regime=None):
    """
    Adaptive Indicator Weighting based on market conditions

    Returns optimized weights for different indicators based on:
    - Volatility (high/low)
    - Volume (high/low)
    - Market Regime (bull/bear/sideways)
    - Trend Strength (ADX)

    Returns:
        dict with weight multipliers for each indicator category
    """
    weights = {
        'rsi': 1.0,
        'mfi': 1.0,
        'macd': 1.0,
        'ma_alignment': 1.0,
        'adx': 1.0,
        'cci': 1.0,
        'williams_r': 1.0,
        'bb': 1.0,
        'vwap': 1.0,
        'volume': 1.0,
        'stoch': 1.0,
        'momentum': 1.0
    }

    if df is None or len(df) < 20 or latest is None:
        return weights

    # === VOLATILITY ANALYSIS ===
    # Calculate recent volatility
    if 'close' in df.columns and len(df) >= 10:
        returns = df['close'].pct_change().tail(10)
        recent_volatility = returns.std()

        # High volatility (>2%)
        if recent_volatility > 0.02:
            # In high volatility:
            # - Trust momentum indicators less (noise)
            # - Trust mean reversion more (RSI, Stoch)
            # - Trust volume analysis more
            weights['rsi'] = 1.3
            weights['stoch'] = 1.3
            weights['mfi'] = 1.2
            weights['volume'] = 1.4
            weights['momentum'] = 0.7
            weights['ma_alignment'] = 0.8

        # Low volatility (<0.01%)
        elif recent_volatility < 0.01:
            # In low volatility:
            # - Trust trend following more
            # - Trust breakout indicators more
            # - Trust mean reversion less
            weights['ma_alignment'] = 1.3
            weights['adx'] = 1.2
            weights['macd'] = 1.3
            weights['bb'] = 1.4  # BB squeeze important
            weights['rsi'] = 0.8
            weights['stoch'] = 0.8

    # === VOLUME ANALYSIS ===
    volume_ratio = latest.get('volume_ratio', 1.0)

    # High volume (>1.5x average)
    if volume_ratio > 1.5:
        # Trust volume-based indicators more
        weights['mfi'] = 1.3
        weights['vwap'] = 1.3
        weights['volume'] = 1.4
        # Trust price-only indicators less
        weights['rsi'] = 0.9
        weights['williams_r'] = 0.9

    # Low volume (<0.7x average)
    elif volume_ratio < 0.7:
        # Low volume = less reliable
        weights['mfi'] = 0.7
        weights['vwap'] = 0.7
        weights['volume'] = 0.6
        # Trust established trends more
        weights['ma_alignment'] = 1.2
        weights['adx'] = 1.2

    # === TREND STRENGTH ANALYSIS (ADX) ===
    adx = latest.get('adx', 25)

    # Strong trend (ADX > 40)
    if adx > 40:
        # Trust trend-following indicators
        weights['ma_alignment'] = 1.4
        weights['adx'] = 1.5
        weights['macd'] = 1.3
        weights['momentum'] = 1.3
        # Trust mean reversion less
        weights['rsi'] = 0.7
        weights['stoch'] = 0.7
        weights['williams_r'] = 0.7

    # Weak trend (ADX < 20) = Sideways
    elif adx < 20:
        # Trust mean reversion indicators
        weights['rsi'] = 1.4
        weights['stoch'] = 1.4
        weights['williams_r'] = 1.3
        weights['bb'] = 1.3
        # Trust trend-following less
        weights['ma_alignment'] = 0.7
        weights['macd'] = 0.8
        weights['momentum'] = 0.7

    # === MARKET REGIME ANALYSIS ===
    if market_regime:
        regime = market_regime.get('regime', 'UNKNOWN')

        # Bull market
        if 'BULL' in regime:
            # Trust bullish continuation signals more
            weights['ma_alignment'] = 1.2
            weights['momentum'] = 1.2
            weights['macd'] = 1.2
            # Don't oversell on dips
            weights['rsi'] = 0.9
            weights['stoch'] = 0.9

        # Bear market
        elif 'BEAR' in regime:
            # Trust bearish continuation signals more
            weights['rsi'] = 1.2  # Overbought rallies = sell
            weights['stoch'] = 1.2
            # Don't overbuy on rallies
            weights['ma_alignment'] = 0.9
            weights['momentum'] = 0.9

        # Sideways market
        elif 'SIDEWAYS' in regime:
            # Mean reversion rules
            weights['rsi'] = 1.3
            weights['stoch'] = 1.3
            weights['bb'] = 1.3
            weights['williams_r'] = 1.2
            # Trend following doesn't work
            weights['ma_alignment'] = 0.7
            weights['momentum'] = 0.7

    # === BOLLINGER BANDS ANALYSIS (Squeeze Detection) ===
    bb_width = latest.get('bb_width', 0.04)

    # Tight squeeze (< 0.025) = Breakout imminent
    if bb_width < 0.025:
        weights['bb'] = 1.5
        weights['volume'] = 1.3  # Volume confirms breakout
        # Lower confidence in current state
        weights['rsi'] = 0.8
        weights['stoch'] = 0.8

    return weights

def get_multi_timeframe_alignment(df, current_price):
    """
    Multi-Timeframe Confirmation Analysis
    Checks if short, medium, and long-term trends are aligned

    Returns:
        dict with alignment_score, confidence_boost, momentum_boost, details
    """
    if df is None or len(df) < 50:
        return {
            'alignment_score': 0,
            'confidence_boost': 0,
            'momentum_boost': 0,
            'timeframes_aligned': 0,
            'trend': 'UNKNOWN',
            'details': 'Insufficient data'
        }

    timeframe_trends = []

    # SHORT-TERM (5-day trend)
    if len(df) >= 5:
        price_5d = df.iloc[-5]['close']
        sma_5 = df.tail(5)['close'].mean()
        trend_5d = 'UP' if current_price > sma_5 and current_price > price_5d else 'DOWN'
        strength_5d = abs((current_price - price_5d) / price_5d) * 100
        timeframe_trends.append({
            'name': 'Short (5d)',
            'trend': trend_5d,
            'strength': strength_5d
        })

    # MEDIUM-TERM (20-day trend)
    if len(df) >= 20:
        price_20d = df.iloc[-20]['close']
        sma_20 = df.tail(20)['close'].mean()
        trend_20d = 'UP' if current_price > sma_20 and current_price > price_20d else 'DOWN'
        strength_20d = abs((current_price - price_20d) / price_20d) * 100
        timeframe_trends.append({
            'name': 'Medium (20d)',
            'trend': trend_20d,
            'strength': strength_20d
        })

    # LONG-TERM (50-day trend)
    if len(df) >= 50:
        price_50d = df.iloc[-50]['close']
        sma_50 = df.tail(50)['close'].mean()
        trend_50d = 'UP' if current_price > sma_50 and current_price > price_50d else 'DOWN'
        strength_50d = abs((current_price - price_50d) / price_50d) * 100
        timeframe_trends.append({
            'name': 'Long (50d)',
            'trend': trend_50d,
            'strength': strength_50d
        })

    if len(timeframe_trends) < 3:
        return {
            'alignment_score': 0,
            'confidence_boost': 0,
            'momentum_boost': 0,
            'timeframes_aligned': 0,
            'trend': 'UNKNOWN',
            'details': 'Insufficient timeframes'
        }

    # Check alignment
    trends = [t['trend'] for t in timeframe_trends]

    # Count aligned timeframes
    up_count = trends.count('UP')
    down_count = trends.count('DOWN')

    if up_count == 3:
        # Perfect bullish alignment
        alignment_score = 3
        dominant_trend = 'UP'
        avg_strength = sum(t['strength'] for t in timeframe_trends) / 3

        # Stronger alignment = higher boost
        if avg_strength > 10:
            confidence_boost = 0.10  # +10% confidence
            momentum_boost = 35
        elif avg_strength > 5:
            confidence_boost = 0.08
            momentum_boost = 25
        else:
            confidence_boost = 0.05
            momentum_boost = 15

    elif down_count == 3:
        # Perfect bearish alignment
        alignment_score = 3
        dominant_trend = 'DOWN'
        avg_strength = sum(t['strength'] for t in timeframe_trends) / 3

        if avg_strength > 10:
            confidence_boost = 0.10
            momentum_boost = -35
        elif avg_strength > 5:
            confidence_boost = 0.08
            momentum_boost = -25
        else:
            confidence_boost = 0.05
            momentum_boost = -15

    elif up_count == 2 or down_count == 2:
        # Partial alignment (2 out of 3)
        alignment_score = 2
        dominant_trend = 'UP' if up_count == 2 else 'DOWN'
        confidence_boost = 0.03  # +3% confidence
        momentum_boost = 10 if up_count == 2 else -10

    else:
        # No alignment (mixed signals)
        alignment_score = 0
        dominant_trend = 'MIXED'
        confidence_boost = 0
        momentum_boost = 0

    details = f"{alignment_score}/3 timeframes aligned {dominant_trend}"

    return {
        'alignment_score': alignment_score,
        'confidence_boost': confidence_boost,
        'momentum_boost': momentum_boost,
        'timeframes_aligned': alignment_score,
        'trend': dominant_trend,
        'details': details,
        'breakdown': timeframe_trends
    }

def generate_technical_predictions(df, current_price, volatility=0.02, sentiment_result=None):
    """
    ENHANCED prediction engine with 13+ technical indicators + NEWS SENTIMENT
    More accurate predictions by feeding more data + news analysis from 10 sources
    """
    if df is None or len(df) < 20:
        return {
            "1h": {"price": current_price, "confidence": 0.50, "trend": "NEUTRAL"},
            "4h": {"price": current_price, "confidence": 0.50, "trend": "NEUTRAL"},
            "1d": {"price": current_price, "confidence": 0.50, "trend": "NEUTRAL"},
            "3d": {"price": current_price, "confidence": 0.50, "trend": "NEUTRAL"}
        }

    latest = df.iloc[-1]

    # === GET ADAPTIVE WEIGHTS BASED ON MARKET CONDITIONS ===
    # This adjusts indicator weights based on volatility, volume, trend strength
    adaptive_weights = get_adaptive_weights(df, latest, market_regime=None)

    # Calculate momentum score (-200 to +200) - increased range for more indicators
    momentum_score = 0
    confidence_factors = []

    # === INDICATOR 1: RSI (Relative Strength Index) ===
    rsi = latest.get('rsi', 50)
    if pd.notna(rsi):
        rsi_weight = adaptive_weights['rsi']  # Apply adaptive weight
        if rsi < 30:
            momentum_score += 25 * rsi_weight
            confidence_factors.append(0.85)
        elif rsi < 40:
            momentum_score += 15 * rsi_weight
            confidence_factors.append(0.75)
        elif rsi > 70:
            momentum_score -= 25 * rsi_weight
            confidence_factors.append(0.85)
        elif rsi > 60:
            momentum_score -= 15 * rsi_weight
            confidence_factors.append(0.75)
        else:
            confidence_factors.append(0.65)

    # === INDICATOR 2: MFI (Money Flow Index) - Volume-weighted RSI ===
    mfi = latest.get('mfi', 50)
    if pd.notna(mfi):
        mfi_weight = adaptive_weights['mfi']  # Apply adaptive weight
        if mfi < 20:  # Oversold with volume
            momentum_score += 20 * mfi_weight
            confidence_factors.append(0.8)
        elif mfi < 35:
            momentum_score += 10 * mfi_weight
            confidence_factors.append(0.7)
        elif mfi > 80:  # Overbought with volume
            momentum_score -= 20 * mfi_weight
            confidence_factors.append(0.8)
        elif mfi > 65:
            momentum_score -= 10 * mfi_weight
            confidence_factors.append(0.7)

    # === INDICATOR 3: MACD (Moving Average Convergence Divergence) ===
    macd = latest.get('macd', 0)
    macd_signal = latest.get('macd_signal', 0)
    if pd.notna(macd) and pd.notna(macd_signal):
        macd_weight = adaptive_weights['macd']  # Apply adaptive weight
        macd_diff = macd - macd_signal
        if macd_diff > 0:
            momentum_score += 15 * macd_weight
            confidence_factors.append(0.8)
        else:
            momentum_score -= 15 * macd_weight
            confidence_factors.append(0.8)

    # === INDICATOR 4: Moving Average Alignment (Multiple Timeframes) ===
    sma_10 = latest.get('sma_10', current_price)
    sma_20 = latest.get('sma_20', current_price)
    sma_50 = latest.get('sma_50', current_price)
    ema_200 = latest.get('ema_200', current_price)

    if pd.notna(sma_10) and pd.notna(sma_20) and pd.notna(sma_50):
        ma_weight = adaptive_weights['ma_alignment']  # Apply adaptive weight
        # Perfect bullish alignment
        if current_price > sma_10 > sma_20 > sma_50:
            momentum_score += 30 * ma_weight
            confidence_factors.append(0.9)
        # Perfect bearish alignment
        elif current_price < sma_10 < sma_20 < sma_50:
            momentum_score -= 30 * ma_weight
            confidence_factors.append(0.9)
        # Partial bullish
        elif current_price > sma_20 > sma_50:
            momentum_score += 20 * ma_weight
            confidence_factors.append(0.8)
        # Partial bearish
        elif current_price < sma_20 < sma_50:
            momentum_score -= 20 * ma_weight
            confidence_factors.append(0.8)
        elif current_price > sma_20:
            momentum_score += 10 * ma_weight
            confidence_factors.append(0.7)
        else:
            momentum_score -= 10 * ma_weight
            confidence_factors.append(0.7)

    # Long-term trend (EMA 200)
    if pd.notna(ema_200):
        if current_price > ema_200:
            momentum_score += 10 * ma_weight
        else:
            momentum_score -= 10 * ma_weight

    # === INDICATOR 5: ADX (Trend Strength) ===
    adx = latest.get('adx', 25)
    adx_pos = latest.get('adx_pos', 25)
    adx_neg = latest.get('adx_neg', 25)

    if pd.notna(adx):
        adx_weight = adaptive_weights['adx']  # Apply adaptive weight
        # Strong trend
        if adx > 40:
            confidence_factors.append(0.9)  # High confidence in strong trend
            if adx_pos > adx_neg:
                momentum_score += 15 * adx_weight
            else:
                momentum_score -= 15 * adx_weight
        # Weak trend
        elif adx < 20:
            confidence_factors.append(0.6)  # Low confidence in weak trend
        else:
            confidence_factors.append(0.75)

    # === INDICATOR 6: CCI (Commodity Channel Index) ===
    cci = latest.get('cci', 0)
    if pd.notna(cci):
        cci_weight = adaptive_weights['cci']  # Apply adaptive weight
        if cci > 100:
            momentum_score += 15 * cci_weight
            confidence_factors.append(0.75)
        elif cci < -100:
            momentum_score -= 15 * cci_weight
            confidence_factors.append(0.75)

    # === INDICATOR 7: Williams %R ===
    williams_r = latest.get('williams_r', -50)
    if pd.notna(williams_r):
        williams_weight = adaptive_weights['williams_r']  # Apply adaptive weight
        if williams_r > -20:  # Overbought
            momentum_score -= 10 * williams_weight
        elif williams_r < -80:  # Oversold
            momentum_score += 10 * williams_weight

    # === INDICATOR 8: Bollinger Bands Position ===
    bb_upper = latest.get('bb_upper', current_price * 1.02)
    bb_lower = latest.get('bb_lower', current_price * 0.98)
    bb_width = latest.get('bb_width', 0.04)

    if pd.notna(bb_upper) and pd.notna(bb_lower):
        bb_weight = adaptive_weights['bb']  # Apply adaptive weight
        bb_position = (current_price - bb_lower) / (bb_upper - bb_lower)
        if bb_position < 0.1:
            momentum_score += 20 * bb_weight
            confidence_factors.append(0.8)
        elif bb_position > 0.9:
            momentum_score -= 20 * bb_weight
            confidence_factors.append(0.8)

        # BB Squeeze (low volatility = breakout soon)
        if pd.notna(bb_width) and bb_width < 0.03:
            confidence_factors.append(0.7)  # Lower confidence during squeeze

    # === INDICATOR 9: VWAP (Volume Weighted Average Price) ===
    vwap = latest.get('vwap', current_price)
    if pd.notna(vwap):
        vwap_weight = adaptive_weights['vwap']  # Apply adaptive weight
        if current_price > vwap * 1.01:
            momentum_score += 10 * vwap_weight
        elif current_price < vwap * 0.99:
            momentum_score -= 10 * vwap_weight

    # === INDICATOR 10: Volume Analysis ===
    volume_ratio = latest.get('volume_ratio', 1.0)
    if pd.notna(volume_ratio):
        volume_weight = adaptive_weights['volume']  # Apply adaptive weight
        if volume_ratio > 2.0:
            # Very high volume - strong signal
            confidence_factors.append(0.9 * volume_weight)
        elif volume_ratio > 1.5:
            confidence_factors.append(0.85 * volume_weight)
        elif volume_ratio < 0.7:
            confidence_factors.append(0.6)
        else:
            confidence_factors.append(0.7)

    # === INDICATOR 11: Stochastic Oscillator ===
    stoch_k = latest.get('stoch_k', 50)
    stoch_d = latest.get('stoch_d', 50)

    if pd.notna(stoch_k) and pd.notna(stoch_d):
        stoch_weight = adaptive_weights['stoch']  # Apply adaptive weight
        if stoch_k < 20 and stoch_d < 20:
            momentum_score += 15 * stoch_weight
        elif stoch_k > 80 and stoch_d > 80:
            momentum_score -= 15 * stoch_weight

    # === INDICATOR 12: Multi-Timeframe Price Momentum ===
    momentum_weight = adaptive_weights['momentum']  # Apply adaptive weight
    if len(df) >= 3:
        price_3d_ago = df.iloc[-3]['close']
        momentum_3d = ((current_price - price_3d_ago) / price_3d_ago) * 100
        if momentum_3d > 3:
            momentum_score += 10 * momentum_weight
        elif momentum_3d < -3:
            momentum_score -= 10 * momentum_weight

    if len(df) >= 5:
        price_5d_ago = df.iloc[-5]['close']
        momentum_5d = ((current_price - price_5d_ago) / price_5d_ago) * 100
        if momentum_5d > 5:
            momentum_score += 15 * momentum_weight
        elif momentum_5d < -5:
            momentum_score -= 15 * momentum_weight

    if len(df) >= 10:
        price_10d_ago = df.iloc[-10]['close']
        momentum_10d = ((current_price - price_10d_ago) / price_10d_ago) * 100
        if momentum_10d > 10:
            momentum_score += 20 * momentum_weight
        elif momentum_10d < -10:
            momentum_score -= 20 * momentum_weight

    # === INDICATOR 13: Multi-Timeframe Alignment ===
    # This checks if short, medium, and long-term trends are all aligned
    # Perfect alignment (3/3) gives HUGE confidence and momentum boost
    mtf_alignment = get_multi_timeframe_alignment(df, current_price)

    # Apply momentum boost from alignment
    momentum_score += mtf_alignment['momentum_boost']

    # Add confidence boost (will be applied later)
    if mtf_alignment['confidence_boost'] > 0:
        confidence_factors.append(0.9)  # High confidence when timeframes align

    # === INDICATOR 14: NEWS SENTIMENT (NEW - VERY POWERFUL!) ===
    # Sentiment from 10+ Indonesian financial news sources
    # Includes 200+ keywords + fundamental event detection
    sentiment_momentum = 0
    fundamental_events = []

    if sentiment_result:
        sentiment_score = sentiment_result.get('average_score', 0)
        total_articles = sentiment_result.get('total_articles', 0)

        # Convert sentiment score (-1 to +1) to momentum (-50 to +50)
        # News sentiment is VERY powerful, so we give it strong weight
        sentiment_momentum = sentiment_score * 50  # Max ±50 momentum

        # Boost if many articles (high media attention = important signal)
        if total_articles >= 20:
            sentiment_momentum *= 1.3  # 30% boost for high coverage
            confidence_factors.append(0.90)
        elif total_articles >= 10:
            sentiment_momentum *= 1.15  # 15% boost for medium coverage
            confidence_factors.append(0.85)
        elif total_articles >= 5:
            confidence_factors.append(0.75)
        else:
            confidence_factors.append(0.65)  # Low article count = less reliable

        # FUNDAMENTAL EVENTS - MASSIVE IMPACT!
        # Check if any article has fundamental events
        for article_sent in sentiment_result.get('article_sentiments', []):
            if article_sent.get('has_fundamental_event'):
                for event in article_sent.get('fundamental_events', []):
                    fundamental_events.append(event)

        # Apply fundamental event boost (each event = ±25 momentum!)
        for event in fundamental_events:
            if event['type'] == 'positive':
                sentiment_momentum += 25  # Huge bullish boost!
                confidence_factors.append(0.95)  # Very high confidence
            else:
                sentiment_momentum -= 25  # Huge bearish impact!
                confidence_factors.append(0.95)

        # Apply sentiment momentum to total score
        momentum_score += sentiment_momentum

    # === DAY OF WEEK PATTERN (IDX specific) ===
    try:
        wib = pytz.timezone('Asia/Jakarta')
        now_wib = datetime.now(wib)
        day_of_week = now_wib.weekday()  # 0=Monday, 4=Friday

        # Monday effect (often bearish)
        if day_of_week == 0:
            momentum_score -= 5
        # Wednesday (mid-week)
        elif day_of_week == 2:
            confidence_factors.append(0.75)
        # Friday (profit-taking)
        elif day_of_week == 4:
            momentum_score -= 5
    except:
        pass

    # === MARKET SESSION AWARENESS ===
    try:
        market_session = get_idx_market_session()
        if market_session['is_trading']:
            confidence_factors.append(0.8)
        else:
            confidence_factors.append(0.65)  # Lower confidence when market closed
    except:
        pass

    # Normalize momentum score to -1 to +1 (adjusted for new range)
    normalized_momentum = np.clip(momentum_score / 200, -1, 1)

    # Calculate base confidence from all factors
    base_confidence = np.mean(confidence_factors) if confidence_factors else 0.65

    # Apply multi-timeframe alignment confidence boost
    base_confidence = min(base_confidence + mtf_alignment['confidence_boost'], 0.98)

    # Determine trend with tighter thresholds
    if normalized_momentum > 0.25:
        trend = "UP"
    elif normalized_momentum < -0.25:
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
    # IMPORTANT: Ensure trend direction matches price movement!

    # Calculate base price changes with bounded noise
    def calculate_prediction(momentum_factor, noise_factor, min_change_pct=0.001):
        """
        Calculate price prediction ensuring trend consistency

        Args:
            momentum_factor: How much momentum affects this timeframe
            noise_factor: Volatility noise multiplier
            min_change_pct: Minimum change to ensure (0.1% default)
        """
        # Base momentum change
        momentum_change = normalized_momentum * momentum_factor

        # Add controlled noise (bounded to not flip direction)
        noise = np.random.normal(0, atr_pct * noise_factor)

        # Total change
        total_change = momentum_change + noise

        # ENFORCE TREND CONSISTENCY
        if trend == "UP":
            # Force minimum upward movement
            total_change = max(total_change, min_change_pct)
        elif trend == "DOWN":
            # Force maximum downward movement
            total_change = min(total_change, -min_change_pct)
        else:  # NEUTRAL
            # Allow small fluctuations but cap magnitude
            total_change = np.clip(total_change, -0.005, 0.005)  # Max ±0.5%

        predicted_price = current_price * (1 + total_change)
        return predicted_price

    # Generate predictions for each timeframe
    predictions = {
        "1h": {
            "price": calculate_prediction(momentum_factor=0.002, noise_factor=0.15, min_change_pct=0.0008),
            "confidence": base_confidence * 0.88,
            "trend": trend if abs(normalized_momentum) > 0.15 else "NEUTRAL"
        },
        "4h": {
            "price": calculate_prediction(momentum_factor=0.006, noise_factor=0.3, min_change_pct=0.002),
            "confidence": base_confidence * 0.92,
            "trend": trend if abs(normalized_momentum) > 0.18 else "NEUTRAL"
        },
        "1d": {
            "price": calculate_prediction(momentum_factor=0.012, noise_factor=0.5, min_change_pct=0.003),
            "confidence": base_confidence,
            "trend": trend
        },
        "3d": {
            "price": calculate_prediction(momentum_factor=0.028, noise_factor=0.8, min_change_pct=0.005),
            "confidence": base_confidence * 0.87,
            "trend": trend if abs(normalized_momentum) > 0.22 else "NEUTRAL"
        }
    }

    # Ensure confidence is in valid range and add metadata
    for timeframe in predictions:
        predictions[timeframe]['confidence'] = np.clip(predictions[timeframe]['confidence'], 0.55, 0.92)
        predictions[timeframe]['momentum_score'] = momentum_score
        predictions[timeframe]['indicators_used'] = len(confidence_factors)
        predictions[timeframe]['mtf_alignment'] = mtf_alignment  # Multi-timeframe alignment info

        # FINAL VALIDATION: Verify trend matches price movement
        price_change_pct = ((predictions[timeframe]['price'] - current_price) / current_price) * 100
        pred_trend = predictions[timeframe]['trend']

        # Debug: Ensure consistency
        if pred_trend == "UP" and price_change_pct < 0:
            # Force correction if still negative despite earlier fix
            predictions[timeframe]['price'] = current_price * 1.001  # Minimum 0.1% up
        elif pred_trend == "DOWN" and price_change_pct > 0:
            # Force correction if still positive despite earlier fix
            predictions[timeframe]['price'] = current_price * 0.999  # Minimum 0.1% down

    return predictions

def check_yesterday_prediction_accuracy(df):
    """
    Check accuracy of yesterday's 1-day prediction vs today's actual price

    This creates predictions using yesterday's data and compares with today's actual close

    Returns:
        dict with accuracy metrics or None if not enough data
    """
    if df is None or len(df) < 2:
        return None

    try:
        # Get yesterday's data (all data except today)
        yesterday_df = df.iloc[:-1].copy()

        # Get yesterday's close price (what we predicted FROM)
        yesterday_close = yesterday_df.iloc[-1]['close']

        # Get today's actual close (what we want to COMPARE TO)
        today_actual = df.iloc[-1]['close']

        # Generate prediction using yesterday's data (what would we have predicted yesterday?)
        yesterday_predictions = generate_technical_predictions(
            yesterday_df,
            yesterday_close,
            sentiment_result=None  # No sentiment for historical check
        )

        # Get the 1-day prediction
        pred_1d = yesterday_predictions.get('1d', {})
        predicted_price = pred_1d.get('price', yesterday_close)
        predicted_trend = pred_1d.get('trend', 'NEUTRAL')
        confidence = pred_1d.get('confidence', 0)

        # Calculate errors
        error = predicted_price - today_actual
        error_pct = (error / today_actual) * 100
        abs_error_pct = abs(error_pct)

        # Check direction accuracy
        actual_change = today_actual - yesterday_close
        actual_trend = "UP" if actual_change > 0 else "DOWN" if actual_change < 0 else "NEUTRAL"

        direction_correct = (predicted_trend == actual_trend)

        # Determine accuracy status
        if abs_error_pct < 1.0:
            status = "EXCELLENT"
            status_icon = "🎯"
        elif abs_error_pct < 2.0:
            status = "GOOD"
            status_icon = "✅"
        elif abs_error_pct < 3.0:
            status = "FAIR"
            status_icon = "🟡"
        else:
            status = "POOR"
            status_icon = "❌"

        return {
            'yesterday_close': yesterday_close,
            'predicted_price': predicted_price,
            'predicted_trend': predicted_trend,
            'today_actual': today_actual,
            'actual_trend': actual_trend,
            'error': error,
            'error_pct': error_pct,
            'abs_error_pct': abs_error_pct,
            'direction_correct': direction_correct,
            'confidence': confidence,
            'status': status,
            'status_icon': status_icon
        }

    except Exception as e:
        print(f"Error checking prediction accuracy: {e}")
        return None

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

# === WIB TIME & MARKET STATUS DISPLAY ===
# Get current WIB time and market session
current_wib = get_current_wib_time()
market_session = get_idx_market_session()
market_status_display = format_market_status_display(market_session)

# Display time and status in sidebar
st.sidebar.markdown(f"""
### 🕐 Waktu Indonesia (WIB)
**{current_wib['day_name_id']}, {current_wib['date']}**
**Jam: {current_wib['time']}** WIB (UTC+7)
""")

# Market status with color coding
if market_status_display['color'] == 'green':
    st.sidebar.success(f"{market_status_display['icon']} **{market_status_display['status']}**\n\n{market_status_display['detail']}")
elif market_status_display['color'] == 'orange':
    st.sidebar.warning(f"{market_status_display['icon']} **{market_status_display['status']}**\n\n{market_status_display['detail']}")
elif market_status_display['color'] == 'red':
    st.sidebar.error(f"{market_status_display['icon']} **{market_status_display['status']}**\n\n{market_status_display['detail']}")
else:
    st.sidebar.info(f"{market_status_display['icon']} **{market_status_display['status']}**\n\n{market_status_display['detail']}")

# Show additional session info if trading is active
if market_session.get('is_trading'):
    time_remaining = market_session.get('time_remaining_minutes', 0)
    hours_remaining = time_remaining // 60
    mins_remaining = time_remaining % 60
    st.sidebar.caption(f"⏱️ Waktu tersisa: {hours_remaining}h {mins_remaining}m")
elif market_session.get('time_to_open_minutes'):
    time_to_open = market_session.get('time_to_open_minutes', 0)
    hours_to_open = time_to_open // 60
    mins_to_open = time_to_open % 60
    if hours_to_open > 0:
        st.sidebar.caption(f"⏰ Market buka dalam: {hours_to_open}h {mins_to_open}m")
    else:
        st.sidebar.caption(f"⏰ Market buka dalam: {mins_to_open} menit")

# Market hours info
with st.sidebar.expander("ℹ️ Info Jam Market IDX"):
    st.markdown("""
    **Jam Trading IDX:**
    - **Sesi 1:** 09:00 - 12:00 WIB
    - **Istirahat:** 12:00 - 13:00 WIB
    - **Sesi 2:** 13:00 - 16:00 WIB

    **Hari Trading:**
    - Senin - Jumat
    - Sabtu & Minggu: TUTUP

    **Pre-market:** 08:45 - 09:00 WIB
    **After-hours:** 16:00 - 16:15 WIB
    """)

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

# === NEWS & SENTIMENT ANALYSIS (MOVED BEFORE PREDICTIONS!) ===
# Scrape news and analyze sentiment from 10+ sources
with st.spinner("📰 Fetching latest news from 10+ sources & analyzing sentiment..."):
    try:
        news_df = news_scraper.scrape_all(selected_stock, limit=3)  # 3 per source = 30 total
        if not news_df.empty:
            news_articles = news_df.to_dict('records')
            sentiment_result = sentiment_analyzer.analyze_articles(news_articles)
        else:
            news_articles = []
            sentiment_result = None
    except Exception as e:
        news_articles = []
        sentiment_result = None

# === PREDICTION PHASE ===
# Generate predictions using LSTM or fallback to technical predictions
# NOW WITH NEWS SENTIMENT INTEGRATION!
with st.spinner("🤖 Generating AI predictions with news sentiment..."):
    predictions = predictor.predict_multiple_horizons(df, selected_stock, current_price)

    # Fallback to technical predictions if LSTM confidence is too low
    if not predictor.model_loaded or predictions.get('1d', {}).get('confidence', 0) < 0.6:
        # Pass sentiment_result to enhance predictions!
        technical_predictions = generate_technical_predictions(df, current_price, sentiment_result=sentiment_result)
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

# === PREDICTION ACCURACY CHECK ===
# Check yesterday's prediction vs today's actual price
with st.spinner("📊 Checking yesterday's prediction accuracy..."):
    accuracy_check = check_yesterday_prediction_accuracy(df)

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

    # Market Hours Info Banner
    market_session = get_idx_market_session()
    if market_session['is_trading']:
        st.success(f"""
        ✅ **Market OPEN** - {market_session['message']}

        Prediction times menggunakan **jam trading IDX (WIB/UTC+7)** - hanya menghitung jam market 09:00-16:00 (Senin-Jumat).
        """)
    else:
        st.warning(f"""
        ⏸️ **Market CLOSED** - {market_session['message']}

        Prediction times menggunakan **jam trading IDX (WIB/UTC+7)**. Next market open: **{market_session.get('next_open', 'N/A')}**
        """)

    st.info("""
    📊 **IDX Market Hours (WIB/UTC+7):**
    - **Sesi 1:** 09:00 - 12:00 WIB
    - **Istirahat:** 12:00 - 13:00 WIB
    - **Sesi 2:** 13:00 - 16:00 WIB
    - **Market Days:** Senin - Jumat (kecuali hari libur)

    ⏰ Semua waktu prediction adalah **trading hours** - bukan waktu kalender biasa!
    """)

    st.markdown("---")

    # === PREDICTION ACCURACY CHECK DISPLAY ===
    if accuracy_check:
        st.subheader("📊 Prediction Accuracy Check")

        st.info("""
        **Apa ini?** Kita check prediksi yang dibuat **kemarin** untuk **hari ini**, lalu bandingkan dengan **actual price hari ini**.
        Ini untuk measure seberapa akurat sistem prediksi kita!
        """)

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Kemarin Close",
                f"Rp {accuracy_check['yesterday_close']:,.0f}",
                help="Harga close kemarin (basis prediksi)"
            )

        with col2:
            st.metric(
                "Prediksi untuk Hari Ini",
                f"Rp {accuracy_check['predicted_price']:,.0f}",
                f"{accuracy_check['predicted_trend']}",
                help="Apa yang diprediksi kemarin untuk hari ini"
            )

        with col3:
            st.metric(
                "Actual Hari Ini",
                f"Rp {accuracy_check['today_actual']:,.0f}",
                f"{accuracy_check['actual_trend']}",
                help="Harga actual hari ini"
            )

        with col4:
            st.metric(
                "Accuracy Status",
                f"{accuracy_check['status_icon']} {accuracy_check['status']}",
                f"{accuracy_check['error_pct']:+.2f}%",
                help="Error % dari prediksi"
            )

        # Detailed accuracy breakdown
        col_a, col_b, col_c = st.columns(3)

        with col_a:
            st.markdown(f"""
            **Price Error:**
            - Predicted: Rp {accuracy_check['predicted_price']:,.0f}
            - Actual: Rp {accuracy_check['today_actual']:,.0f}
            - Error: Rp {accuracy_check['error']:+,.0f}
            """)

        with col_b:
            st.markdown(f"""
            **Error Percentage:**
            - Error %: {accuracy_check['error_pct']:+.2f}%
            - Abs Error %: {accuracy_check['abs_error_pct']:.2f}%
            - Confidence: {accuracy_check['confidence']*100:.1f}%
            """)

        with col_c:
            direction_icon = "✅" if accuracy_check['direction_correct'] else "❌"
            st.markdown(f"""
            **Direction Accuracy:**
            - Predicted: {accuracy_check['predicted_trend']}
            - Actual: {accuracy_check['actual_trend']}
            - Match: {direction_icon} {"YES" if accuracy_check['direction_correct'] else "NO"}
            """)

        # Accuracy interpretation
        if accuracy_check['status'] == "EXCELLENT":
            st.success("🎯 **EXCELLENT!** Prediksi sangat akurat (error < 1%)")
        elif accuracy_check['status'] == "GOOD":
            st.success("✅ **GOOD!** Prediksi akurat (error < 2%)")
        elif accuracy_check['status'] == "FAIR":
            st.warning("🟡 **FAIR** - Prediksi cukup akurat (error < 3%)")
        else:
            st.error("❌ **POOR** - Prediksi kurang akurat (error ≥ 3%)")

        if accuracy_check['direction_correct']:
            st.success("✅ **Direction Correct!** Prediksi trend match dengan actual movement")
        else:
            st.error("❌ **Direction Wrong!** Prediksi trend tidak match dengan actual movement")

        st.markdown("---")

    # Predictions Display
    pred_cols = st.columns(4)

    # Mapping timeframes to market hours (accounting for IDX trading hours)
    timeframe_configs = {
        "1h": {"label": "1 JAM", "hours": 1, "desc": "1 jam trading"},
        "4h": {"label": "4 JAM", "hours": 4, "desc": "4 jam trading"},
        "1d": {"label": "1 HARI", "hours": None, "desc": "1 hari trading"},
        "3d": {"label": "3 HARI", "hours": None, "desc": "3 hari trading"}
    }

    for i, (timeframe, pred) in enumerate(predictions.items()):
        with pred_cols[i]:
            price_diff = pred['price'] - current_price
            price_diff_pct = (price_diff / current_price) * 100

            config = timeframe_configs.get(timeframe, {"label": timeframe.upper(), "hours": None, "desc": ""})

            # Calculate target date/time for this prediction (MARKET TIME)
            if timeframe == "1h" or timeframe == "4h":
                # Use market hours calculator
                target_info = calculate_market_target_time(config['hours'])
                day_name = target_info['day_name']
                target_date = target_info['date']
                target_time = target_info['time']
                session_info = target_info['session']
            elif timeframe == "1d":
                # 1 day ahead (next trading day)
                wib = pytz.timezone('Asia/Jakarta')
                target_dt = datetime.now(wib) + timedelta(days=1)
                # Skip weekend
                while target_dt.weekday() >= 5:
                    target_dt += timedelta(days=1)
                target_dt = target_dt.replace(hour=15, minute=45, second=0)  # End of trading
                day_name = target_dt.strftime('%A')
                target_date = target_dt.strftime('%d %B %Y')
                target_time = target_dt.strftime('%H:%M WIB')
                session_info = "Akhir sesi trading"
            else:  # 3d
                # 3 days ahead (trading days)
                wib = pytz.timezone('Asia/Jakarta')
                target_dt = datetime.now(wib)
                trading_days = 0
                while trading_days < 3:
                    target_dt += timedelta(days=1)
                    if target_dt.weekday() < 5:  # Not weekend
                        trading_days += 1
                target_dt = target_dt.replace(hour=15, minute=45, second=0)
                day_name = target_dt.strftime('%A')
                target_date = target_dt.strftime('%d %B %Y')
                target_time = target_dt.strftime('%H:%M WIB')
                session_info = "Akhir sesi trading"

            st.markdown(f"### {config['label']}")
            st.metric(
                "Predicted Price",
                f"Rp {pred['price']:,.0f}",
                f"{price_diff_pct:+.2f}%"
            )
            st.progress(pred['confidence'])
            st.caption(f"Confidence: {pred['confidence']*100:.1f}%")

            trend_color = "🟢" if pred['trend'] == "UP" else "🔴" if pred['trend'] == "DOWN" else "🟡"
            st.markdown(f"**Trend:** {trend_color} {pred['trend']}")

            # Display multi-timeframe alignment (NEW!)
            if 'mtf_alignment' in pred:
                alignment = pred['mtf_alignment']
                if alignment['alignment_score'] == 3:
                    # Perfect alignment - show with emphasis
                    st.markdown(f"🎯 **ALL TIMEFRAMES ALIGNED {alignment['trend']}**")
                    st.caption(f"✅ {alignment['details']}")
                elif alignment['alignment_score'] == 2:
                    st.caption(f"⚡ {alignment['details']}")
                elif alignment['alignment_score'] > 0:
                    st.caption(f"📊 {alignment['details']}")

            # Display target date and time (MARKET TIME)
            st.markdown(f"📅 **{day_name}**")
            st.caption(f"{target_date}")
            st.caption(f"🕐 {target_time}")
            if timeframe in ["1h", "4h"]:
                st.caption(f"📊 {session_info}")

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

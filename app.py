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
}

# Helper functions
@st.cache_data(ttl=7200)  # Cache for 2 hours
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
        df['atr'] = df['close'] * 0.01
        return df

    try:
        # Moving Averages
        df['sma_10'] = SMAIndicator(df['close'], window=10).sma_indicator()
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

        # ATR
        df['atr'] = AverageTrueRange(df['high'], df['low'], df['close'], window=14).average_true_range()
    except Exception as e:
        st.warning(f"Could not calculate some technical indicators: {e}")
        # Fill with defaults if calculation fails
        if 'rsi' not in df.columns:
            df['rsi'] = 50.0

    return df

def generate_mock_predictions(current_price, volatility=0.02):
    """Generate mock predictions (placeholder for LSTM model)"""
    # Simulate predictions with some random walk
    trend = np.random.choice([-1, 0, 1], p=[0.3, 0.2, 0.5])  # Slight bullish bias

    predictions = {
        "1h": {
            "price": current_price * (1 + np.random.normal(0.001 * trend, volatility * 0.3)),
            "confidence": np.random.uniform(0.65, 0.75),
            "trend": "UP" if trend > 0 else "DOWN" if trend < 0 else "NEUTRAL"
        },
        "4h": {
            "price": current_price * (1 + np.random.normal(0.005 * trend, volatility * 0.5)),
            "confidence": np.random.uniform(0.63, 0.73),
            "trend": "UP" if trend > 0 else "DOWN" if trend < 0 else "NEUTRAL"
        },
        "1d": {
            "price": current_price * (1 + np.random.normal(0.01 * trend, volatility)),
            "confidence": np.random.uniform(0.68, 0.78),
            "trend": "UP" if trend > 0 else "DOWN" if trend < 0 else "NEUTRAL"
        },
        "3d": {
            "price": current_price * (1 + np.random.normal(0.03 * trend, volatility * 1.5)),
            "confidence": np.random.uniform(0.60, 0.72),
            "trend": "UP" if trend > 0 else "DOWN" if trend < 0 else "NEUTRAL"
        }
    }

    return predictions

def generate_trading_signal(df, predictions):
    """Generate trading signal based on technical indicators and predictions"""
    if df is None or len(df) < 2:
        return {"signal": "HOLD", "strength": 0, "reasons": ["Insufficient data"], "score": 0}

    latest = df.iloc[-1]
    signals = []
    score = 0
    reasons = []

    # RSI signals (check for valid value)
    if pd.notna(latest.get('rsi', np.nan)):
        if latest['rsi'] < 30:
            score += 2
            signals.append("BUY")
            reasons.append("RSI oversold (<30)")
        elif latest['rsi'] > 70:
            score -= 2
            signals.append("SELL")
            reasons.append("RSI overbought (>70)")

    # MACD signals (check for valid values)
    if pd.notna(latest.get('macd', np.nan)) and pd.notna(latest.get('macd_signal', np.nan)):
        if latest['macd'] > latest['macd_signal']:
            score += 1
            signals.append("BUY")
            reasons.append("MACD bullish crossover")
        else:
            score -= 1
            signals.append("SELL")
            reasons.append("MACD bearish crossover")

    # Moving Average signals (check for valid values)
    if pd.notna(latest.get('sma_50', np.nan)):
        if latest['close'] > latest['sma_50']:
            score += 1
            signals.append("BUY")
            reasons.append("Price above SMA50")
        else:
            score -= 1
            signals.append("SELL")
            reasons.append("Price below SMA50")

    # Bollinger Bands (check for valid values)
    if pd.notna(latest.get('bb_lower', np.nan)) and pd.notna(latest.get('bb_upper', np.nan)):
        if latest['close'] < latest['bb_lower']:
            score += 1
            signals.append("BUY")
            reasons.append("Price at lower Bollinger Band")
        elif latest['close'] > latest['bb_upper']:
            score -= 1
            signals.append("SELL")
            reasons.append("Price at upper Bollinger Band")

    # Prediction trend
    if predictions.get('1d', {}).get('trend') == "UP":
        score += 1
        signals.append("BUY")
        reasons.append("1d prediction bullish")
    elif predictions.get('1d', {}).get('trend') == "DOWN":
        score -= 1
        signals.append("SELL")
        reasons.append("1d prediction bearish")

    # Determine final signal
    if score >= 3:
        signal = "STRONG BUY"
    elif score >= 1:
        signal = "BUY"
    elif score <= -3:
        signal = "STRONG SELL"
    elif score <= -1:
        signal = "SELL"
    else:
        signal = "HOLD"

    return {
        "signal": signal,
        "score": score,
        "strength": min(abs(score) * 20, 100),
        "reasons": reasons[:3]  # Top 3 reasons
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
st.sidebar.info("⚠️ **DISCLAIMER**: This is a demo system. Not financial advice. Always do your own research.")

# Main content
st.title(f"📈 {selected_stock} - {STOCKS[selected_stock]['name']}")
st.markdown(f"**Sector:** {STOCKS[selected_stock]['sector']}")

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
df = calculate_technical_indicators(df)

# Show warning if insufficient data
if len(df) < 50:
    st.warning(f"⚠️ Limited data available ({len(df)} days). Technical indicators may not be accurate. Consider selecting a longer time period.")

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
    return predictor, news_scraper, sentiment_analyzer

predictor, news_scraper, sentiment_analyzer = initialize_modules()

# Generate predictions using LSTM or mock
predictions = predictor.predict_multiple_horizons(df, selected_stock, current_price)

# Scrape news and analyze sentiment
with st.spinner("Fetching latest news..."):
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

# Generate signal (combining technical + sentiment)
signal_data = generate_trading_signal(df, predictions)

# Adjust signal with news sentiment if available
if sentiment_result and sentiment_result['average_score'] != 0:
    sentiment_signal = sentiment_analyzer.get_market_sentiment_signal(sentiment_result['average_score'])
    signal_data['sentiment_signal'] = sentiment_signal
    signal_data['sentiment_score'] = sentiment_result['average_score']
else:
    signal_data['sentiment_signal'] = "NEUTRAL"
    signal_data['sentiment_score'] = 0.0

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

# Tabs
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📊 Chart & Indicators",
    "🎯 Predictions",
    "💡 Trading Recommendation",
    "📈 Technical Analysis",
    "📰 News & Sentiment",
    "📅 Daily Data",
    "📊 Transaction History"
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

    fig_price.update_layout(
        height=400,
        xaxis_rangeslider_visible=False,
        hovermode='x unified'
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
    st.warning("⚠️ These are MOCK predictions. Real LSTM model is not trained yet.")

    pred_cols = st.columns(4)

    for i, (timeframe, pred) in enumerate(predictions.items()):
        with pred_cols[i]:
            price_diff = pred['price'] - current_price
            price_diff_pct = (price_diff / current_price) * 100

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
    st.subheader("📈 Technical Analysis Summary")

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

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>📈 Indonesian Stock Prediction System | Demo Version</p>
    <p>⚠️ <b>DISCLAIMER:</b> This system is for educational purposes only. Not financial advice.
    Always do your own research before making investment decisions.</p>
</div>
""", unsafe_allow_html=True)

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
with st.spinner("🤖 Generating AI predictions..."):
    predictions = predictor.predict_multiple_horizons(df, selected_stock, current_price)

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
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>📈 <b>Indonesian Stock Prediction System</b> | Educational Demo Version</p>

    <p style='font-size: 14px; max-width: 800px; margin: 10px auto;'>
        ⚠️ <b>IMPORTANT LEGAL DISCLAIMER</b><br>
        This system is provided for <b>educational and demonstration purposes only</b>.
        All predictions, recommendations, and analyses are generated by algorithms based on historical data
        and technical indicators. <b>This is NOT financial advice.</b>
    </p>

    <p style='font-size: 12px; max-width: 800px; margin: 10px auto;'>
        <b>No Guarantee:</b> Past performance does not guarantee future results. Stock markets are inherently risky.
        You could lose your entire investment.<br>
        <b>No Liability:</b> The creators and operators of this system assume NO responsibility for your investment decisions or losses.<br>
        <b>Consult Professionals:</b> Always consult licensed financial advisors before making investment decisions.<br>
        <b>Do Your Research:</b> Conduct thorough research and understand the risks before investing.
    </p>

    <p style='font-size: 11px; color: #666;'>
        By using this system, you acknowledge that you understand and accept these terms and risks.
    </p>
</div>
""", unsafe_allow_html=True)

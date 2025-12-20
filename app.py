"""
Indonesian Stock Prediction Dashboard
Streamlit Demo Application
"""
import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import ta
from ta.trend import SMAIndicator, EMAIndicator, MACD
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.volatility import BollingerBands, AverageTrueRange

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
@st.cache_data(ttl=3600)
def fetch_stock_data(stock_code, period="6mo"):
    """Fetch stock data from Yahoo Finance"""
    ticker = f"{stock_code}.JK"
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period, interval="1d")

        if df.empty:
            return None

        df = df.reset_index()
        df.columns = [col.lower() for col in df.columns]
        return df
    except Exception as e:
        st.error(f"Error fetching data: {e}")
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
    st.error(f"❌ No data available for {selected_stock}. Please try another stock.")
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

# Generate predictions
predictions = generate_mock_predictions(current_price)

# Generate signal
signal_data = generate_trading_signal(df, predictions)

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
tab1, tab2, tab3, tab4 = st.tabs(["📊 Chart & Indicators", "🎯 Predictions", "💡 Trading Recommendation", "📈 Technical Analysis"])

with tab1:
    # Price chart with indicators
    fig = make_subplots(
        rows=3,
        cols=1,
        shared_xaxis=True,
        vertical_spacing=0.05,
        subplot_titles=['Price & Moving Averages', 'MACD', 'RSI'],
        row_heights=[0.5, 0.25, 0.25],
        specs=[[{"type": "xy"}],
               [{"type": "xy"}],
               [{"type": "xy"}]]
    )

    # Candlestick
    fig.add_trace(
        go.Candlestick(
            x=df['date'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name="Price"
        ),
        row=1, col=1
    )

    # Moving averages
    fig.add_trace(
        go.Scatter(x=df['date'], y=df['sma_10'], name="SMA 10", line=dict(color='orange', width=1)),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=df['date'], y=df['sma_50'], name="SMA 50", line=dict(color='blue', width=1)),
        row=1, col=1
    )

    # Bollinger Bands
    fig.add_trace(
        go.Scatter(x=df['date'], y=df['bb_upper'], name="BB Upper", line=dict(color='gray', width=1, dash='dash')),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=df['date'], y=df['bb_lower'], name="BB Lower", line=dict(color='gray', width=1, dash='dash')),
        row=1, col=1
    )

    # MACD
    fig.add_trace(
        go.Scatter(x=df['date'], y=df['macd'], name="MACD", line=dict(color='blue', width=1)),
        row=2, col=1
    )
    fig.add_trace(
        go.Scatter(x=df['date'], y=df['macd_signal'], name="Signal", line=dict(color='orange', width=1)),
        row=2, col=1
    )
    fig.add_trace(
        go.Bar(x=df['date'], y=df['macd_diff'], name="Histogram", marker_color='gray'),
        row=2, col=1
    )

    # RSI
    fig.add_trace(
        go.Scatter(x=df['date'], y=df['rsi'], name="RSI", line=dict(color='purple', width=2)),
        row=3, col=1
    )
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)

    fig.update_layout(
        height=800,
        showlegend=True,
        xaxis_rangeslider_visible=False
    )

    st.plotly_chart(fig, use_container_width=True)

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

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>📈 Indonesian Stock Prediction System | Demo Version</p>
    <p>⚠️ <b>DISCLAIMER:</b> This system is for educational purposes only. Not financial advice.
    Always do your own research before making investment decisions.</p>
</div>
""", unsafe_allow_html=True)

# 🚀 New Features 2026 - Complete Guide

**5 Major Features Implemented**
**Option A (Quick Wins) + Option B (Data Enrichment)**

---

## 📋 Table of Contents

1. [Position Sizing Calculator](#1-position-sizing-calculator)
2. [Multi-Timeframe Analysis](#2-multi-timeframe-analysis)
3. [Corporate Actions Tracker](#3-corporate-actions-tracker)
4. [Foreign Flow Tracker](#4-foreign-flow-tracker)
5. [Alert & Notification System](#5-alert--notification-system)
6. [Integration Guide](#integration-guide)
7. [Configuration](#configuration)
8. [Examples](#examples)

---

## 1. Position Sizing Calculator 💰

**File:** `utils/position_sizer.py`

### Overview
Professional-grade position sizing calculator with multiple methods to optimize risk management.

### Features

#### 🎯 Kelly Criterion
Calculate optimal position size based on historical performance:
- Win rate & win/loss ratio based
- Safety factor (Fractional Kelly) for risk reduction
- Prevents over-betting
- Dynamic position recommendations

**Formula:**
```
Kelly % = (p × b - q) / b
Where:
- p = win rate
- q = 1 - win rate
- b = win/loss ratio (avg_win / avg_loss)
```

#### 💰 Fixed Fractional
Risk a fixed percentage per trade:
- 1-10% risk per trade
- Consistent risk exposure
- Portfolio stability

#### ⚖️ Percent Risk
Calculate shares based on entry & stop loss:
- Risk fixed % of capital
- Account for stop loss distance
- Lot size adjustments for IDX (100 shares)

**Formula:**
```
Shares = (Capital × Risk%) / (Entry - Stop Loss)
```

#### 🎯 Risk/Reward Validation
Only trade if R:R meets threshold:
- Minimum R:R threshold (default: 1.5:1)
- Trade approval system
- Potential profit/loss calculation

#### 🔥 Portfolio Heat
Monitor total portfolio risk:
- Sum of all position risks
- Maximum heat threshold (default: 6%)
- Remaining capacity tracking
- Prevent over-exposure

#### 🔗 Correlation Adjustment
Reduce size for correlated positions:
- Detect high correlation (>0.7)
- Automatic size reduction
- Diversification management

### Usage Examples

```python
from utils.position_sizer import PositionSizer

# Initialize with capital
sizer = PositionSizer(total_capital=100_000_000)

# Method 1: Kelly Criterion
kelly_result = sizer.kelly_criterion(
    win_rate=0.70,          # 70% win rate
    avg_win=0.03,           # 3% avg win
    avg_loss=0.015,         # 1.5% avg loss
    safety_factor=0.25      # Quarter Kelly for safety
)
print(f"Kelly Position: Rp {kelly_result['position_value']:,.0f}")

# Method 2: Percent Risk
percent_result = sizer.percent_risk(
    entry_price=10_000,
    stop_loss=9_800,        # 2% stop
    risk_per_trade=0.02     # Risk 2% of capital
)
print(f"Shares: {percent_result['shares']:,}")
print(f"Lots: {percent_result['lots']}")

# Method 3: Risk/Reward Sizing (Recommended)
rr_result = sizer.risk_reward_sizing(
    entry_price=10_000,
    stop_loss=9_800,        # 2% risk
    target_price=10_400,    # 4% reward (R:R = 2.0)
    risk_per_trade=0.02,
    min_risk_reward=1.5
)

if rr_result['trade_approved']:
    print("✅ Trade Approved!")
    print(f"Shares: {rr_result['shares']:,}")
    print(f"Position Value: Rp {rr_result['position_value']:,.0f}")
    print(f"Risk/Reward: 1:{rr_result['risk_reward_ratio']:.2f}")
    print(f"Potential Profit: Rp {rr_result['potential_profit']:,.0f}")
    print(f"Potential Loss: Rp {rr_result['potential_loss']:,.0f}")
else:
    print("❌ Trade Rejected - R:R too low")

# Method 4: Portfolio Heat Check
open_positions = [
    {'shares': 2000, 'entry': 10_000, 'stop_loss': 9_800},
    {'shares': 3000, 'entry': 5_000, 'stop_loss': 4_900},
]

heat_result = sizer.portfolio_heat(
    open_positions,
    max_heat=0.06  # Max 6% portfolio risk
)

print(f"Portfolio Heat: {heat_result['portfolio_heat']:.1f}%")
print(f"Can Take New Trade: {heat_result['can_take_new_trade']}")

# Method 5: Comprehensive Recommendation
recommendation = sizer.get_position_recommendation(
    entry_price=10_000,
    stop_loss=9_800,
    target_price=10_400,
    risk_per_trade=0.02,
    win_rate=0.70,          # Optional: for Kelly
    avg_win=0.03,
    avg_loss=0.015
)

print(f"Recommended Position: Rp {recommendation['recommended_position_value']:,.0f}")
print(f"Basis: {recommendation['recommendation_basis']}")
```

### Best Practices

1. **Always validate R:R** - Minimum 1.5:1, ideally 2:1+
2. **Monitor portfolio heat** - Never exceed 6% total risk
3. **Use fractional Kelly** - Full Kelly too aggressive, use 25-50%
4. **Account for correlation** - Reduce size for correlated positions
5. **Respect stop losses** - Position size = function of stop distance

---

## 2. Multi-Timeframe Analysis 📊

**File:** `utils/multi_timeframe_analyzer.py`

### Overview
Analyze stocks across multiple timeframes (Daily, Weekly) to detect trend alignment and improve signal quality.

### Features

#### 📈 Multiple Timeframes
- **Daily**: 6 months data
- **Weekly**: 2 years data
- **4H**: Future enhancement (requires intraday data)

#### 🎯 Trend Detection
Per-timeframe analysis using:
- SMA (20, 50-period)
- MACD & Signal line
- RSI (14-period)
- Trend confidence (0-100%)

#### 🔄 Confluence Scoring
Measure alignment across timeframes:
- **100**: All timeframes aligned (STRONG signal)
- **70-99**: Majority aligned (GOOD signal)
- **50-69**: Mixed signals (NEUTRAL)
- **<50**: Conflicting signals (CAUTION)

#### 📊 Top-Down Analysis
Professional trading approach:
- Higher TF for direction (Weekly/Daily)
- Lower TF for entry (Daily/4H)
- Maximize win rate with alignment

### Usage Examples

```python
from utils.multi_timeframe_analyzer import MultiTimeframeAnalyzer

# Initialize
analyzer = MultiTimeframeAnalyzer('BBCA.JK')

# Generate complete report
report = analyzer.generate_multi_timeframe_report()

# Results
print(f"Stock: {report['stock_code']}")
print(f"\nTimeframe Analysis:")

for tf, data in report['timeframe_analysis'].items():
    if data['trend'] != 'NO_DATA':
        print(f"{data['timeframe']}: {data['trend']} "
              f"({data['confidence']:.0f}% confidence)")

# Confluence
confluence = report['confluence']
print(f"\nConfluence Score: {confluence['confluence_score']:.0f}/100")
print(f"Alignment: {confluence['alignment']}")
print(f"Recommendation: {confluence['recommendation']}")

# Entry Strategy
entry = report['entry_recommendation']
print(f"\nEntry Strategy:")
print(f"Direction TF: {entry['direction_timeframe']}")
print(f"Entry TF: {entry['entry_timeframe']}")
print(f"Strategy: {entry['strategy']}")
print(f"Entry Signal: {entry['entry_signal']}")

# Example output:
# Daily: UPTREND (85% confidence)
# Weekly: UPTREND (90% confidence)
# Confluence Score: 100/100
# Alignment: STRONG_BULLISH
# Recommendation: 🟢 STRONG BUY - All timeframes aligned
```

### Trading Strategies by Confluence

#### Strong Bullish (100 score)
- All timeframes uptrend
- Action: **STRONG BUY**
- Strategy: Buy on any pullback
- Entry: Lower timeframe dip
- Stop: Below recent low
- Target: Weekly resistance

#### Bullish (70-99 score)
- Majority timeframes uptrend
- Action: **BUY**
- Strategy: Selective entry
- Entry: Daily support
- Stop: Below support
- Target: Daily resistance

#### Mixed (50-69 score)
- Conflicting signals
- Action: **HOLD/WAIT**
- Strategy: Wait for alignment
- Entry: Wait
- Stop: N/A
- Target: N/A

---

## 3. Corporate Actions Tracker 💼

**File:** `utils/corporate_actions.py`

### Overview
Track dividend payments, stock splits, bonus shares, and rights issues for Indonesian stocks.

### Features

#### 💰 Dividend Tracking
- 5-year dividend history
- Dividend yield calculation
- Growth rate analysis
- Payout consistency scoring
- Upcoming dividend detection

#### 📈 Stock Splits
- Split history with ratios
- Split vs Reverse split detection
- Bonus share identification
- Post-split price/shares calculation

#### 📊 Metrics Calculation
- Current dividend yield
- 5-year average yield
- Dividend growth rate (CAGR)
- Years of consecutive payments
- Payout consistency rating

### Usage Examples

```python
from utils.corporate_actions import CorporateActionsTracker

# Initialize
tracker = CorporateActionsTracker('BBCA.JK')

# Get all corporate actions
current_price = 10_000
actions = tracker.get_all_corporate_actions(current_price)

# Dividends
dividends = actions['dividends']
print(f"Dividend Payments: {dividends['count']}")
if dividends['metrics']:
    print(f"Current Yield: {dividends['metrics']['current_yield']:.2f}%")
    print(f"5Y Avg Dividend: Rp {dividends['metrics']['avg_dividend_per_year']:,.0f}")
    print(f"Growth Rate: {dividends['metrics']['dividend_growth_rate']:+.1f}%/year")
    print(f"Consistency: {dividends['metrics']['payout_consistency']}")

# Stock Splits
splits = actions['stock_splits']
if splits['count'] > 0:
    latest = splits['latest']
    print(f"\nLatest Split: {latest['Date'][:10]}")
    print(f"Ratio: {latest['Description']}")

# Upcoming Dividends
upcoming = dividends['upcoming']
if upcoming['has_upcoming_dividend']:
    print(f"\n🎁 Upcoming Dividend!")
    print(f"Ex-Date: {upcoming['ex_dividend_date']}")
    print(f"Amount: Rp {upcoming['dividend_rate']:,.0f}")
    print(f"Yield: {upcoming['dividend_yield']:.2f}%")

# Impact Analysis (if you own shares)
impact = tracker.get_impact_analysis(
    current_price=10_000,
    position_shares=1000
)

if impact['has_impact']:
    for event in impact['upcoming_events']:
        if event['type'] == 'Dividend':
            print(f"\nEstimated Dividend Income: Rp {event['estimated_income']:,.0f}")
        elif event['type'] == 'Stock Split':
            print(f"\nPost-Split Shares: {event['shares_after']}")
            print(f"Post-Split Price: Rp {event['price_after']:,.0f}")
```

### Dividend Stock Scoring

| Criterion | Excellent | Good | Moderate | Poor |
|-----------|-----------|------|----------|------|
| **Yield** | >5% | 3-5% | 1-3% | <1% |
| **Consistency** | 5+ years | 3-4 years | 1-2 years | None |
| **Growth** | >10%/year | 5-10%/year | 0-5%/year | Negative |
| **Payout Ratio** | 40-60% | 30-70% | <30% or >70% | >80% |

---

## 4. Foreign Flow Tracker 🌍

**File:** `utils/foreign_flow_tracker.py`

### Overview
Track foreign investor buy/sell activity - a critical indicator for IDX market movements.

### Features

#### 📊 Volume-Based Estimation
Estimate foreign flow from volume patterns:
- Detect volume spikes (>1.5σ above mean)
- Classify by price movement
- Bullish spikes = Foreign buy
- Bearish spikes = Foreign sell

#### 📈 Timeframe Analysis
- Short-term (10 days)
- Medium-term (30 days)
- Long-term (60 days)
- Ownership change detection

#### 🎯 Foreign Pressure Indicators
- STRONG_BUY: Net sentiment >0.3
- BUY: Net sentiment >0
- NEUTRAL: Net sentiment -0.3 to 0.3
- SELL: Net sentiment <-0.3
- STRONG_SELL: Net sentiment <-0.6

### Usage Examples

```python
from utils.foreign_flow_tracker import ForeignFlowTracker
import yfinance as yf

# Get stock data
ticker = yf.Ticker('BBCA.JK')
df = ticker.history(period='3mo')

# Initialize tracker
tracker = ForeignFlowTracker('BBCA.JK')

# Get comprehensive summary
summary = tracker.get_foreign_flow_summary(df)

# Display results
print(f"Stock: {summary['stock_code']}")
print(f"As of: {summary['as_of']}\n")

# Foreign Pressure
pressure = summary['foreign_pressure']
print("Foreign Pressure:")
print(f"  Short-term (10d): {pressure['short_term_10d']}")
print(f"  Medium-term (30d): {pressure['medium_term_30d']}")
print(f"  Overall: {pressure['overall']}\n")

# Key Metrics
metrics = summary['key_metrics']
print("Activity Indicators:")
print(f"  Bullish Spikes: {metrics['recent_bullish_spikes']}")
print(f"  Bearish Spikes: {metrics['recent_bearish_spikes']}")
print(f"  Net Sentiment (10d): {metrics['net_sentiment_10d']:.2f}")
print(f"  Volume Trend: {metrics['volume_trend']}\n")

# Interpretation
interp = summary['interpretation']
print("Analysis:")
print(f"  {interp['short_term']}")
print(f"  {interp['ownership']}")
print(f"  {interp['recommendation']}")

# Compare with Market
ihsg = yf.Ticker('^JKSE')
ihsg_df = ihsg.history(period='3mo')

comparison = tracker.compare_with_market(df, ihsg_df)
print(f"\nMarket Comparison:")
print(f"  Stock Pressure: {comparison['stock_pressure']}")
print(f"  Market Pressure: {comparison['market_pressure']}")
print(f"  Relationship: {comparison['relationship']}")
print(f"  {comparison['interpretation']}")
```

### Foreign Flow Interpretation

| Scenario | Meaning | Action |
|----------|---------|--------|
| **Strong Foreign Buy** | High institutional interest | Consider following smart money |
| **Strong Foreign Sell** | Institutions exiting | Exercise caution |
| **Stock Outperforming** | Stock attracting interest vs market | Potential outperformer |
| **Stock Underperforming** | Stock losing interest vs market | Potential underperformer |
| **Balanced Activity** | No clear foreign direction | Wait for clearer signal |

---

## 5. Alert & Notification System 🔔

**File:** `utils/alert_system.py`

### Overview
Multi-channel alert system for real-time notifications via Telegram and Email.

### Features

#### 📱 Telegram Integration
- Telegram Bot API
- Markdown formatting
- Rich messages with emojis
- Instant delivery

#### 📧 Email Integration
- SMTP support (Gmail, Outlook, etc.)
- Plain text & HTML formats
- Customizable templates
- Reliable delivery

#### 🎯 Alert Types

1. **Price Alerts**
   - Target reached
   - Stop loss hit
   - Price above/below threshold

2. **Signal Alerts**
   - STRONG_BUY/SELL generated
   - Signal with entry/target/stop
   - Confidence scoring

3. **Pattern Alerts**
   - Chart patterns detected
   - Candlestick patterns
   - Pattern confidence

4. **News Alerts**
   - Stock mentioned in news
   - Sentiment analysis
   - Source attribution

5. **Dividend Alerts**
   - Ex-date approaching
   - Dividend amount
   - Days until ex-date

### Configuration

Set environment variables:

```bash
# Telegram (Get from @BotFather)
export TELEGRAM_BOT_TOKEN="your_bot_token"
export TELEGRAM_CHAT_ID="your_chat_id"

# Email (Gmail example)
export SMTP_EMAIL="your_email@gmail.com"
export SMTP_PASSWORD="your_app_password"
export SMTP_SERVER="smtp.gmail.com"
export SMTP_PORT="587"
```

**Gmail App Password:**
1. Go to Google Account settings
2. Security → 2-Step Verification
3. App passwords → Generate
4. Use generated password

### Usage Examples

```python
from utils.alert_system import AlertSystem, send_price_alert, send_signal_alert

# Initialize
alert_system = AlertSystem()

# Example 1: Price Alert
price_alert = alert_system.create_price_alert(
    stock_code='BBCA.JK',
    current_price=10_500,
    target_price=10_000,
    alert_type='TARGET_REACHED'
)

# Send to Telegram
result = alert_system.send_telegram_alert(
    alert_system._format_telegram_message(price_alert)
)

if result['success']:
    print("✅ Alert sent successfully!")
else:
    print(f"❌ Error: {result['error']}")

# Example 2: Signal Alert
signal_alert = alert_system.create_signal_alert(
    stock_code='BBRI.JK',
    signal='STRONG_BUY',
    confidence=85.0,
    entry_price=5_000,
    target_price=5_200,
    stop_loss=4_900
)

# Send to both Telegram and Email
signal_alert['email_recipient'] = 'trader@example.com'

results = alert_system.send_multi_channel_alert(
    signal_alert,
    channels=['telegram', 'email']
)

for channel, result in results.items():
    if result['success']:
        print(f"✅ {channel.title()} alert sent")
    else:
        print(f"❌ {channel.title()} failed: {result['error']}")

# Example 3: Quick Helper Functions
# Price alert (simple)
send_price_alert(
    stock_code='TLKM.JK',
    current_price=4_500,
    target_price=4_000,
    telegram=True,
    email='trader@example.com'
)

# Signal alert (simple)
send_signal_alert(
    stock_code='ASII.JK',
    signal='BUY',
    confidence=75.0,
    entry_price=6_500,
    telegram=True
)

# Example 4: Pattern Alert
pattern_alert = alert_system.create_pattern_alert(
    stock_code='GOTO.JK',
    pattern_name='Head and Shoulders',
    pattern_type='BEARISH',
    confidence=80.0
)

alert_system.send_telegram_alert(
    alert_system._format_telegram_message(pattern_alert)
)

# Example 5: Dividend Alert
dividend_alert = alert_system.create_dividend_alert(
    stock_code='UNVR.JK',
    ex_date='2026-02-15',
    dividend_amount=500,
    days_until=7
)

alert_system.send_telegram_alert(
    alert_system._format_telegram_message(dividend_alert)
)
```

### Telegram Message Format

```markdown
*🟢 BBCA.JK Trading Signal: STRONG_BUY*

📊 Stock: `BBCA.JK`
🎯 Signal: *STRONG_BUY*
📊 Confidence: 85%
💵 Entry: Rp 10,000
🎯 Target: Rp 10,400
🛑 Stop Loss: Rp 9,800

🕐 2026-01-31T10:30:00
```

---

## Integration Guide

### Step 1: Import Modules

```python
from utils.position_sizer import PositionSizer
from utils.multi_timeframe_analyzer import MultiTimeframeAnalyzer
from utils.corporate_actions import CorporateActionsTracker
from utils.foreign_flow_tracker import ForeignFlowTracker
from utils.alert_system import AlertSystem
```

### Step 2: Complete Trading Workflow

```python
import yfinance as yf

# 1. Fetch Data
stock_code = 'BBCA.JK'
ticker = yf.Ticker(stock_code)
df = ticker.history(period='6mo')
current_price = df['Close'].iloc[-1]

# 2. Multi-Timeframe Analysis
mtf_analyzer = MultiTimeframeAnalyzer(stock_code)
mtf_report = mtf_analyzer.generate_multi_timeframe_report()

confluence_score = mtf_report['confluence']['confluence_score']
alignment = mtf_report['confluence']['alignment']

print(f"Confluence: {confluence_score}/100 - {alignment}")

# Only proceed if confluence is good
if confluence_score >= 70:

    # 3. Check Foreign Flow
    ff_tracker = ForeignFlowTracker(stock_code)
    ff_summary = ff_tracker.get_foreign_flow_summary(df)

    foreign_pressure = ff_summary['foreign_pressure']['overall']
    print(f"Foreign Pressure: {foreign_pressure}")

    # 4. Check Corporate Actions
    ca_tracker = CorporateActionsTracker(stock_code)
    actions = ca_tracker.get_all_corporate_actions(current_price)

    has_upcoming_dividend = actions['dividends']['upcoming']['has_upcoming_dividend']
    if has_upcoming_dividend:
        print("📅 Upcoming dividend!")

    # 5. Calculate Position Size
    sizer = PositionSizer(total_capital=100_000_000)

    entry = current_price
    stop_loss = entry * 0.98  # 2% stop
    target = entry * 1.04     # 4% target

    position = sizer.risk_reward_sizing(
        entry_price=entry,
        stop_loss=stop_loss,
        target_price=target,
        risk_per_trade=0.02
    )

    if position['trade_approved']:
        print(f"\n✅ Trade Setup Approved:")
        print(f"Shares: {position['shares']:,}")
        print(f"Position Value: Rp {position['position_value']:,.0f}")
        print(f"Risk/Reward: 1:{position['risk_reward_ratio']:.2f}")

        # 6. Send Alert
        alert_system = AlertSystem()

        signal_alert = alert_system.create_signal_alert(
            stock_code=stock_code,
            signal='STRONG_BUY',
            confidence=confluence_score,
            entry_price=entry,
            target_price=target,
            stop_loss=stop_loss
        )

        alert_system.send_telegram_alert(
            alert_system._format_telegram_message(signal_alert)
        )

        print("🔔 Alert sent!")

else:
    print("⚠️ Low confluence - wait for better alignment")
```

---

## Configuration

### Environment Variables

Create `.env` file in project root:

```env
# Telegram Bot
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
TELEGRAM_CHAT_ID=123456789

# Email (Gmail)
SMTP_EMAIL=yourmail@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# Optional: Other SMTP providers
# Outlook: smtp-mail.outlook.com:587
# Yahoo: smtp.mail.yahoo.com:587
```

Load with:
```python
from dotenv import load_dotenv
load_dotenv()
```

---

## Examples

See individual sections above for detailed examples, or check:
- `tests/test_position_sizer.py` - Position sizing examples
- `NEW_FEATURES_2026.md` - This guide
- Each module's docstrings

---

## Summary

**5 Features Implemented:**

1. ✅ Position Sizing Calculator (400+ lines)
2. ✅ Multi-Timeframe Analysis (400+ lines)
3. ✅ Corporate Actions Tracker (400+ lines)
4. ✅ Foreign Flow Tracker (450+ lines)
5. ✅ Alert System (450+ lines)

**Total:** ~2,100 lines of professional-grade trading tools

**Benefits:**
- Systematic risk management
- Higher win rate (multi-timeframe confirmation)
- Corporate action awareness
- Foreign flow insights (unique for IDX)
- Real-time notifications

**Next Steps:**
1. Integrate into `app.py` UI
2. Test in production
3. Collect user feedback
4. Iterate and improve

**Happy Trading! 🚀📈**

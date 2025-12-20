# 🚀 Deployment Guide - Streamlit Cloud

## Quick Deploy to Streamlit Cloud (FREE)

### Prerequisites
- GitHub account
- Repository pushed to GitHub
- Streamlit Cloud account (sign up at https://streamlit.io/cloud)

### Step 1: Prepare Repository
✅ Already done! Your repository is ready with:
- `app.py` - Main Streamlit application
- `requirements-streamlit.txt` - Dependencies
- `.streamlit/config.toml` - Streamlit configuration

### Step 2: Deploy to Streamlit Cloud

1. **Sign up/Login to Streamlit Cloud**
   - Go to https://share.streamlit.io/
   - Click "Sign up" or "Continue with GitHub"
   - Authorize Streamlit to access your GitHub

2. **Create New App**
   - Click "New app" button
   - Select your repository: `herrylim2001/stock-prediction-indonesia`
   - Branch: `claude/review-repo-files-fdrwt` (or your main branch)
   - Main file path: `app.py`
   - Advanced settings:
     - Python version: 3.11
     - Requirements file: `requirements-streamlit.txt`

3. **Deploy!**
   - Click "Deploy"
   - Wait 2-5 minutes for deployment
   - Your app will be live at: `https://[your-app-name].streamlit.app`

### Step 3: Access Your Dashboard

Once deployed, you'll get a public URL like:
```
https://stock-prediction-indonesia.streamlit.app
```

Share this URL to access your dashboard from anywhere! 🎉

---

## Local Testing (Before Deployment)

### Install Dependencies
```bash
pip install -r requirements-streamlit.txt
```

### Run Locally
```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

---

## Troubleshooting

### Deployment Failed?

1. **Check requirements.txt**
   - Make sure `requirements-streamlit.txt` exists
   - Verify all packages are compatible

2. **GitHub Repository Issues**
   - Ensure repository is public (or Streamlit has access)
   - Check that `app.py` is in the root directory

3. **Runtime Errors**
   - Check Streamlit Cloud logs
   - Look for missing dependencies

### App Running Slow?

- Yahoo Finance API can be slow during market hours
- Data is cached for 1 hour (3600 seconds)
- Try selecting different stocks or timeframes

---

## Features Included in Demo

✅ **Real-time Data Fetching**
- Fetches live data from Yahoo Finance
- Supports 10 Indonesian blue chip stocks
- Multiple timeframes (1mo, 3mo, 6mo, 1y, 2y)

✅ **Technical Analysis**
- Moving Averages (SMA, EMA)
- RSI (Relative Strength Index)
- MACD
- Bollinger Bands
- ATR (Average True Range)

✅ **Mock Predictions**
- 1-hour, 4-hour, 1-day, 3-day forecasts
- Confidence scores
- Trend indicators
- ⚠️ Note: Using mock predictions (LSTM model not trained yet)

✅ **Trading Recommendations**
- Buy/Sell/Hold signals
- Position sizing calculator
- Risk management
- Stop loss & take profit levels

✅ **Interactive Charts**
- Candlestick charts
- Technical indicator overlays
- MACD histogram
- RSI oscillator

---

## Next Steps to Enhance

### Phase 1: Improve Data (Easy)
- [ ] Add more stocks
- [ ] Add intraday data (hourly)
- [ ] Historical data export

### Phase 2: Real ML Model (Medium)
- [ ] Collect historical data (1-2 years)
- [ ] Train LSTM model
- [ ] Replace mock predictions with real predictions
- [ ] Add model performance metrics

### Phase 3: Advanced Features (Advanced)
- [ ] User authentication
- [ ] Portfolio tracking
- [ ] Alert notifications (email/Telegram)
- [ ] Backtesting engine
- [ ] Multi-timeframe analysis

---

## Cost

**Streamlit Cloud Free Tier:**
- ✅ FREE forever
- ✅ Public apps
- ✅ 1 GB resources per app
- ✅ Unlimited viewers
- ⚠️ Apps sleep after inactivity (wake up on visit)

**Upgrade Options:**
- Streamlit Cloud Pro: $20/month (private apps, more resources)

---

## Support & Issues

If you encounter any issues:
1. Check the Streamlit Cloud logs
2. Review this deployment guide
3. Check GitHub Issues
4. Contact Streamlit support

---

## Security Notes

⚠️ **Important:**
- This is a PUBLIC demo app
- Don't input real trading credentials
- Don't store sensitive data
- All data is from public Yahoo Finance API

---

## License

MIT License - See LICENSE file

**DISCLAIMER:**
This system is for educational purposes only. Not financial advice.
Always do your own research before making investment decisions.

---

Created: December 2025

"""
Stock Data Template Generator
Creates Excel templates for Indonesian stock prediction system
"""
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils.dataframe import dataframe_to_rows
from datetime import datetime, timedelta
import numpy as np
import random

# Define 10 popular Indonesian stocks
STOCKS = [
    {"code": "BBCA", "name": "Bank Central Asia", "sector": "Keuangan", "lot_size": 100},
    {"code": "BBRI", "name": "Bank Rakyat Indonesia", "sector": "Keuangan", "lot_size": 100},
    {"code": "TLKM", "name": "Telkom Indonesia", "sector": "Telekomunikasi", "lot_size": 100},
    {"code": "ASII", "name": "Astra International", "sector": "Otomotif", "lot_size": 100},
    {"code": "UNVR", "name": "Unilever Indonesia", "sector": "Consumer Goods", "lot_size": 100},
    {"code": "BMRI", "name": "Bank Mandiri", "sector": "Keuangan", "lot_size": 100},
    {"code": "GOTO", "name": "GoTo Gojek Tokopedia", "sector": "Teknologi", "lot_size": 100},
    {"code": "ACES", "name": "Ace Hardware Indonesia", "sector": "Retail", "lot_size": 100},
    {"code": "ICBP", "name": "Indofood CBP Sukses Makmur", "sector": "Consumer Goods", "lot_size": 100},
    {"code": "EMTK", "name": "Elang Mahkota Teknologi", "sector": "Media & Teknologi", "lot_size": 100},
]

# Base prices (approximate real prices in IDR)
BASE_PRICES = {
    "BBCA": 9500, "BBRI": 5200, "TLKM": 3800, "ASII": 5400, "UNVR": 4200,
    "BMRI": 6100, "GOTO": 85, "ACES": 750, "ICBP": 11500, "EMTK": 480
}

def generate_hourly_data(stock_code, days=60):
    """Generate hourly OHLCV data for a stock"""
    data = []
    base_price = BASE_PRICES[stock_code]
    current_price = base_price
    
    # Trading hours: 9:00 - 16:00 WIB
    trading_hours = list(range(9, 17))  # 9:00 to 16:00
    
    start_date = datetime.now() - timedelta(days=days)
    
    for day_offset in range(days):
        current_date = start_date + timedelta(days=day_offset)
        if current_date.weekday() >= 5:  # Skip weekends
            continue
            
        for hour in trading_hours:
            timestamp = current_date.replace(hour=hour, minute=0, second=0)
            
            # Generate realistic price movement
            volatility = 0.005  # 0.5% volatility per hour
            trend = random.choice([-1, 0, 0, 1])  # Slight bullish bias
            change_pct = random.gauss(0.0001 * trend, volatility)
            
            open_price = current_price
            high_change = abs(random.gauss(0, volatility * 1.5))
            low_change = abs(random.gauss(0, volatility * 1.5))
            close_change = random.gauss(0, volatility)
            
            high_price = open_price * (1 + high_change)
            low_price = open_price * (1 - low_change)
            close_price = open_price * (1 + close_change)
            
            # Ensure OHLC logic
            high_price = max(open_price, close_price, high_price)
            low_price = min(open_price, close_price, low_price)
            
            # Generate volume (higher at open and close)
            base_volume = random.randint(50000, 500000)
            if hour in [9, 10, 15, 16]:
                base_volume *= random.uniform(1.5, 2.5)
            
            data.append({
                "timestamp": timestamp,
                "date": timestamp.strftime("%Y-%m-%d"),
                "hour": hour,
                "open": round(open_price, 0),
                "high": round(high_price, 0),
                "low": round(low_price, 0),
                "close": round(close_price, 0),
                "volume": int(base_volume),
                "value": int(round(close_price * base_volume, 0))
            })
            
            current_price = close_price
    
    return pd.DataFrame(data)

def generate_daily_data(stock_code, days=365):
    """Generate daily OHLCV data for a stock"""
    data = []
    base_price = BASE_PRICES[stock_code]
    current_price = base_price
    
    start_date = datetime.now() - timedelta(days=days)
    
    for day_offset in range(days):
        current_date = start_date + timedelta(days=day_offset)
        if current_date.weekday() >= 5:
            continue
            
        volatility = 0.02  # 2% daily volatility
        trend = random.choice([-1, 0, 0, 0, 1])
        
        open_price = current_price
        high_change = abs(random.gauss(0.01, volatility))
        low_change = abs(random.gauss(0.01, volatility))
        close_change = random.gauss(0.001 * trend, volatility)
        
        high_price = open_price * (1 + high_change)
        low_price = open_price * (1 - low_change)
        close_price = open_price * (1 + close_change)
        
        high_price = max(open_price, close_price, high_price)
        low_price = min(open_price, close_price, low_price)
        
        base_volume = random.randint(5000000, 50000000)
        
        data.append({
            "date": current_date.strftime("%Y-%m-%d"),
            "open": round(open_price, 0),
            "high": round(high_price, 0),
            "low": round(low_price, 0),
            "close": round(close_price, 0),
            "volume": int(base_volume),
            "value": int(round(close_price * base_volume, 0)),
            "change": round((close_price - open_price) / open_price * 100, 2),
            "change_pct": round((close_price - open_price) / open_price * 100, 2)
        })
        
        current_price = close_price
    
    return pd.DataFrame(data)

def style_worksheet(ws, title):
    """Apply professional styling to worksheet"""
    header_fill = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=11)
    border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    
    # Style headers
    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = border
    
    # Auto-adjust column widths
    for column in ws.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        ws.column_dimensions[column_letter].width = min(max_length + 2, 20)

def create_stock_master_template():
    """Create master stock list template"""
    wb = Workbook()
    ws = wb.active
    ws.title = "Stock_Master"
    
    headers = ["Stock_Code", "Stock_Name", "Sector", "Lot_Size", "Last_Price", "Market_Cap", "Is_Active"]
    ws.append(headers)
    
    for stock in STOCKS:
        ws.append([
            stock["code"],
            stock["name"],
            stock["sector"],
            stock["lot_size"],
            BASE_PRICES[stock["code"]],
            BASE_PRICES[stock["code"]] * random.randint(10000000000, 100000000000),
            "YES"
        ])
    
    style_worksheet(ws, "Stock Master")
    wb.save("/home/claude/stock-prediction-system/data/01_stock_master.xlsx")
    print("✓ Created: 01_stock_master.xlsx")

def create_hourly_data_template():
    """Create hourly price data template with sample data"""
    wb = Workbook()
    
    for i, stock in enumerate(STOCKS[:3]):  # Sample for first 3 stocks
        if i == 0:
            ws = wb.active
            ws.title = stock["code"]
        else:
            ws = wb.create_sheet(stock["code"])
        
        df = generate_hourly_data(stock["code"], days=30)
        
        # Add headers
        headers = list(df.columns)
        ws.append(headers)
        
        # Add data
        for _, row in df.iterrows():
            ws.append([
                row["timestamp"].strftime("%Y-%m-%d %H:%M:%S"),
                row["date"],
                row["hour"],
                row["open"],
                row["high"],
                row["low"],
                row["close"],
                row["volume"],
                row["value"]
            ])
        
        style_worksheet(ws, stock["code"])
    
    # Add template sheet
    ws_template = wb.create_sheet("_TEMPLATE")
    ws_template.append(["timestamp", "date", "hour", "open", "high", "low", "close", "volume", "value"])
    ws_template.append(["2025-01-15 09:00:00", "2025-01-15", 9, 9500, 9550, 9480, 9520, 150000, 1428000000])
    style_worksheet(ws_template, "Template")
    
    wb.save("/home/claude/stock-prediction-system/data/02_hourly_prices.xlsx")
    print("✓ Created: 02_hourly_prices.xlsx")

def create_daily_data_template():
    """Create daily price data template with sample data"""
    wb = Workbook()
    
    for i, stock in enumerate(STOCKS[:3]):
        if i == 0:
            ws = wb.active
            ws.title = stock["code"]
        else:
            ws = wb.create_sheet(stock["code"])
        
        df = generate_daily_data(stock["code"], days=365)
        
        headers = list(df.columns)
        ws.append(headers)
        
        for _, row in df.iterrows():
            ws.append(list(row.values))
        
        style_worksheet(ws, stock["code"])
    
    wb.save("/home/claude/stock-prediction-system/data/03_daily_prices.xlsx")
    print("✓ Created: 03_daily_prices.xlsx")

def create_trading_config_template():
    """Create trading configuration template"""
    wb = Workbook()
    
    # Sheet 1: User Config
    ws_config = wb.active
    ws_config.title = "User_Config"
    
    config_data = [
        ["Parameter", "Value", "Description"],
        ["modal_total", 100000000, "Total modal trading (IDR)"],
        ["risk_per_trade", 0.01, "Risk tolerance per trade (1%)"],
        ["max_position_size", 0.1, "Max position size per stock (10%)"],
        ["max_open_positions", 5, "Maximum open positions"],
        ["stop_loss_default", 0.02, "Default stop loss (2%)"],
        ["take_profit_default", 0.04, "Default take profit (4%)"],
        ["trading_fee_buy", 0.0015, "Fee beli (0.15%)"],
        ["trading_fee_sell", 0.0025, "Fee jual (0.25%)"],
    ]
    
    for row in config_data:
        ws_config.append(row)
    style_worksheet(ws_config, "User Config")
    
    # Sheet 2: Trading Hours
    ws_hours = wb.create_sheet("Trading_Hours")
    hours_data = [
        ["Session", "Start_Hour", "End_Hour", "Description"],
        ["Pre-Opening", 8, 9, "Pra-pembukaan"],
        ["Session 1", 9, 12, "Sesi 1 trading"],
        ["Lunch Break", 12, 13, "Istirahat"],
        ["Session 2", 13, 16, "Sesi 2 trading"],
        ["Pre-Closing", 16, 17, "Pra-penutupan"],
    ]
    for row in hours_data:
        ws_hours.append(row)
    style_worksheet(ws_hours, "Trading Hours")
    
    # Sheet 3: Risk Management Rules
    ws_risk = wb.create_sheet("Risk_Rules")
    risk_data = [
        ["Rule_ID", "Rule_Name", "Condition", "Action", "Priority"],
        ["R001", "Daily Loss Limit", "daily_loss > modal * 0.03", "STOP_TRADING", 1],
        ["R002", "Max Drawdown", "drawdown > 0.1", "REDUCE_POSITION", 2],
        ["R003", "Position Concentration", "single_stock > 0.2", "NO_NEW_BUY", 3],
        ["R004", "Volatility Filter", "volatility > 0.05", "SMALLER_LOT", 4],
    ]
    for row in risk_data:
        ws_risk.append(row)
    style_worksheet(ws_risk, "Risk Rules")
    
    wb.save("/home/claude/stock-prediction-system/data/04_trading_config.xlsx")
    print("✓ Created: 04_trading_config.xlsx")

def create_prediction_output_template():
    """Create prediction output template"""
    wb = Workbook()
    
    # Sheet 1: Predictions
    ws_pred = wb.active
    ws_pred.title = "Predictions"
    
    pred_headers = [
        "timestamp", "stock_code", "current_price", "predicted_1h", "predicted_4h",
        "predicted_1d", "predicted_3d", "confidence", "trend", "signal",
        "suggested_action", "suggested_lot", "stop_loss", "take_profit", "notes"
    ]
    ws_pred.append(pred_headers)
    
    # Sample prediction data
    sample_predictions = [
        ["2025-01-15 10:00:00", "BBCA", 9500, 9520, 9580, 9650, 9800, 0.75, "BULLISH", "BUY", "BUY", 10, 9310, 9880, "Strong momentum"],
        ["2025-01-15 10:00:00", "BBRI", 5200, 5180, 5150, 5100, 5050, 0.68, "BEARISH", "SELL", "HOLD", 0, 5096, 5408, "Weak trend"],
        ["2025-01-15 10:00:00", "TLKM", 3800, 3810, 3820, 3850, 3900, 0.72, "BULLISH", "BUY", "BUY", 15, 3724, 3952, "Accumulation phase"],
    ]
    for row in sample_predictions:
        ws_pred.append(row)
    style_worksheet(ws_pred, "Predictions")
    
    # Sheet 2: Daily Summary
    ws_summary = wb.create_sheet("Daily_Summary")
    summary_headers = [
        "date", "total_trades", "winning_trades", "losing_trades", "win_rate",
        "gross_profit", "gross_loss", "net_pnl", "best_trade", "worst_trade"
    ]
    ws_summary.append(summary_headers)
    style_worksheet(ws_summary, "Daily Summary")
    
    # Sheet 3: Portfolio
    ws_portfolio = wb.create_sheet("Portfolio")
    portfolio_headers = [
        "stock_code", "shares", "avg_buy_price", "current_price", "market_value",
        "unrealized_pnl", "unrealized_pnl_pct", "weight"
    ]
    ws_portfolio.append(portfolio_headers)
    style_worksheet(ws_portfolio, "Portfolio")
    
    wb.save("/home/claude/stock-prediction-system/data/05_prediction_output.xlsx")
    print("✓ Created: 05_prediction_output.xlsx")

def create_technical_indicators_template():
    """Create technical indicators reference template"""
    wb = Workbook()
    
    ws = wb.active
    ws.title = "Indicators_Config"
    
    indicators_data = [
        ["Indicator", "Short_Period", "Long_Period", "Signal_Period", "Weight", "Description"],
        ["SMA", 10, 50, "-", 0.1, "Simple Moving Average"],
        ["EMA", 12, 26, "-", 0.15, "Exponential Moving Average"],
        ["RSI", 14, "-", "-", 0.15, "Relative Strength Index"],
        ["MACD", 12, 26, 9, 0.2, "Moving Average Convergence Divergence"],
        ["BB", 20, "-", 2, 0.1, "Bollinger Bands (period, std_dev)"],
        ["ATR", 14, "-", "-", 0.1, "Average True Range"],
        ["VWAP", "-", "-", "-", 0.1, "Volume Weighted Average Price"],
        ["OBV", "-", "-", "-", 0.05, "On Balance Volume"],
        ["STOCH", 14, 3, 3, 0.05, "Stochastic Oscillator (%K, %D, smooth)"],
    ]
    
    for row in indicators_data:
        ws.append(row)
    style_worksheet(ws, "Indicators")
    
    # Sheet 2: Signal Rules
    ws_signals = wb.create_sheet("Signal_Rules")
    signal_data = [
        ["Signal_Type", "Indicator", "Condition", "Action", "Strength"],
        ["BUY", "RSI", "RSI < 30", "Oversold - potential reversal up", "STRONG"],
        ["BUY", "MACD", "MACD crosses above Signal", "Bullish crossover", "MEDIUM"],
        ["BUY", "BB", "Price touches lower band", "Potential bounce", "WEAK"],
        ["SELL", "RSI", "RSI > 70", "Overbought - potential reversal down", "STRONG"],
        ["SELL", "MACD", "MACD crosses below Signal", "Bearish crossover", "MEDIUM"],
        ["SELL", "BB", "Price touches upper band", "Potential pullback", "WEAK"],
        ["HOLD", "SMA", "Price between SMA10 and SMA50", "Consolidation zone", "NEUTRAL"],
    ]
    for row in signal_data:
        ws_signals.append(row)
    style_worksheet(ws_signals, "Signal Rules")
    
    wb.save("/home/claude/stock-prediction-system/data/06_technical_indicators.xlsx")
    print("✓ Created: 06_technical_indicators.xlsx")

def create_csv_templates():
    """Create CSV templates for easy data upload"""
    
    # Hourly CSV template
    hourly_df = pd.DataFrame({
        "timestamp": ["2025-01-15 09:00:00", "2025-01-15 10:00:00"],
        "stock_code": ["BBCA", "BBCA"],
        "open": [9500, 9520],
        "high": [9550, 9580],
        "low": [9480, 9500],
        "close": [9520, 9560],
        "volume": [150000, 180000]
    })
    hourly_df.to_csv("/home/claude/stock-prediction-system/data/template_hourly_prices.csv", index=False)
    print("✓ Created: template_hourly_prices.csv")
    
    # Daily CSV template
    daily_df = pd.DataFrame({
        "date": ["2025-01-15", "2025-01-16"],
        "stock_code": ["BBCA", "BBCA"],
        "open": [9500, 9600],
        "high": [9650, 9700],
        "low": [9450, 9550],
        "close": [9600, 9680],
        "volume": [15000000, 18000000]
    })
    daily_df.to_csv("/home/claude/stock-prediction-system/data/template_daily_prices.csv", index=False)
    print("✓ Created: template_daily_prices.csv")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("📊 STOCK PREDICTION SYSTEM - Template Generator")
    print("="*60 + "\n")
    
    create_stock_master_template()
    create_hourly_data_template()
    create_daily_data_template()
    create_trading_config_template()
    create_prediction_output_template()
    create_technical_indicators_template()
    create_csv_templates()
    
    print("\n" + "="*60)
    print("✅ All templates created successfully!")
    print("="*60)
    print("\n📁 Files location: /home/claude/stock-prediction-system/data/")
    print("\n📝 Template descriptions:")
    print("   1. 01_stock_master.xlsx     - Daftar 10 saham target")
    print("   2. 02_hourly_prices.xlsx    - Data harga per jam (sample)")
    print("   3. 03_daily_prices.xlsx     - Data harga harian (sample)")
    print("   4. 04_trading_config.xlsx   - Konfigurasi trading & risk management")
    print("   5. 05_prediction_output.xlsx- Template output prediksi")
    print("   6. 06_technical_indicators.xlsx - Konfigurasi indikator teknikal")
    print("   7. template_hourly_prices.csv - CSV template untuk upload hourly")
    print("   8. template_daily_prices.csv  - CSV template untuk upload daily")
    print("\n")

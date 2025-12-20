"""
Data Fetcher for Indonesian Stocks
Supports multiple data sources for flexibility
"""
import os

# Stock list with Yahoo Finance tickers
IDX_STOCKS = {
    "BBCA": {"yf_ticker": "BBCA.JK", "name": "Bank Central Asia"},
    "BBRI": {"yf_ticker": "BBRI.JK", "name": "Bank Rakyat Indonesia"},
    "TLKM": {"yf_ticker": "TLKM.JK", "name": "Telkom Indonesia"},
    "ASII": {"yf_ticker": "ASII.JK", "name": "Astra International"},
    "UNVR": {"yf_ticker": "UNVR.JK", "name": "Unilever Indonesia"},
    "BMRI": {"yf_ticker": "BMRI.JK", "name": "Bank Mandiri"},
    "GOTO": {"yf_ticker": "GOTO.JK", "name": "GoTo Gojek Tokopedia"},
    "ACES": {"yf_ticker": "ACES.JK", "name": "Ace Hardware Indonesia"},
    "ICBP": {"yf_ticker": "ICBP.JK", "name": "Indofood CBP"},
    "EMTK": {"yf_ticker": "EMTK.JK", "name": "Elang Mahkota Teknologi"},
}

def check_yfinance():
    """Check if yfinance is installed"""
    try:
        import yfinance
        return True
    except ImportError:
        return False

def install_yfinance():
    """Install yfinance if not available"""
    print("Installing yfinance...")
    os.system("pip install yfinance --break-system-packages -q")
    print("✓ yfinance installed")

def fetch_daily_data_yfinance(stock_code: str, period: str = "1y") -> "pd.DataFrame":
    """
    Fetch daily data from Yahoo Finance
    
    Args:
        stock_code: IDX stock code (e.g., "BBCA")
        period: Data period - 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
    
    Returns:
        DataFrame with OHLCV data
    """
    import yfinance as yf
    import pandas as pd
    
    if stock_code not in IDX_STOCKS:
        raise ValueError(f"Unknown stock code: {stock_code}")
    
    ticker = IDX_STOCKS[stock_code]["yf_ticker"]
    stock = yf.Ticker(ticker)
    
    # Fetch historical data
    df = stock.history(period=period, interval="1d")
    
    if df.empty:
        print(f"⚠️ No data found for {stock_code}")
        return pd.DataFrame()
    
    # Rename columns to match our format
    df = df.reset_index()
    df = df.rename(columns={
        "Date": "date",
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Volume": "volume"
    })
    
    # Add calculated columns
    df["stock_code"] = stock_code
    df["date"] = df["date"].dt.strftime("%Y-%m-%d")
    df["change"] = df["close"] - df["open"]
    df["change_pct"] = (df["change"] / df["open"] * 100).round(2)
    df["value"] = (df["close"] * df["volume"]).astype(int)
    
    # Select and order columns
    columns = ["date", "stock_code", "open", "high", "low", "close", "volume", "value", "change", "change_pct"]
    df = df[columns]
    
    return df

def fetch_hourly_data_yfinance(stock_code: str, period: str = "1mo") -> "pd.DataFrame":
    """
    Fetch hourly data from Yahoo Finance
    
    Args:
        stock_code: IDX stock code (e.g., "BBCA")
        period: Data period - 1d, 5d, 1mo (max for hourly)
    
    Returns:
        DataFrame with OHLCV data
    
    Note: Yahoo Finance has limitations on hourly data availability
    """
    import yfinance as yf
    import pandas as pd
    
    if stock_code not in IDX_STOCKS:
        raise ValueError(f"Unknown stock code: {stock_code}")
    
    ticker = IDX_STOCKS[stock_code]["yf_ticker"]
    stock = yf.Ticker(ticker)
    
    # Fetch hourly data (1h interval)
    df = stock.history(period=period, interval="1h")
    
    if df.empty:
        print(f"⚠️ No hourly data found for {stock_code}")
        return pd.DataFrame()
    
    # Process data
    df = df.reset_index()
    df = df.rename(columns={
        "Datetime": "timestamp",
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Volume": "volume"
    })
    
    # Add calculated columns
    df["stock_code"] = stock_code
    df["date"] = df["timestamp"].dt.strftime("%Y-%m-%d")
    df["hour"] = df["timestamp"].dt.hour
    df["timestamp"] = df["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
    df["value"] = (df["close"] * df["volume"]).astype(int)
    
    # Select and order columns
    columns = ["timestamp", "date", "hour", "stock_code", "open", "high", "low", "close", "volume", "value"]
    df = df[columns]
    
    return df

def fetch_all_stocks_daily(period: str = "1y", save_path: str = None):
    """Fetch daily data for all 10 stocks"""
    import pandas as pd
    
    all_data = []
    
    for code in IDX_STOCKS.keys():
        print(f"Fetching {code}...", end=" ")
        try:
            df = fetch_daily_data_yfinance(code, period)
            if not df.empty:
                all_data.append(df)
                print(f"✓ {len(df)} rows")
            else:
                print("✗ No data")
        except Exception as e:
            print(f"✗ Error: {e}")
    
    if all_data:
        combined = pd.concat(all_data, ignore_index=True)
        
        if save_path:
            combined.to_csv(save_path, index=False)
            print(f"\n✓ Saved to {save_path}")
        
        return combined
    
    return pd.DataFrame()

def fetch_all_stocks_hourly(period: str = "1mo", save_path: str = None):
    """Fetch hourly data for all 10 stocks"""
    import pandas as pd
    
    all_data = []
    
    for code in IDX_STOCKS.keys():
        print(f"Fetching hourly {code}...", end=" ")
        try:
            df = fetch_hourly_data_yfinance(code, period)
            if not df.empty:
                all_data.append(df)
                print(f"✓ {len(df)} rows")
            else:
                print("✗ No data")
        except Exception as e:
            print(f"✗ Error: {e}")
    
    if all_data:
        combined = pd.concat(all_data, ignore_index=True)
        
        if save_path:
            combined.to_csv(save_path, index=False)
            print(f"\n✓ Saved to {save_path}")
        
        return combined
    
    return pd.DataFrame()

def load_csv_data(filepath: str) -> "pd.DataFrame":
    """Load data from CSV file (for manual uploads)"""
    import pandas as pd
    
    df = pd.read_csv(filepath)
    print(f"✓ Loaded {len(df)} rows from {filepath}")
    return df

def validate_data(df: "pd.DataFrame", data_type: str = "daily") -> dict:
    """
    Validate data format and quality
    
    Returns dict with validation results
    """
    results = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "stats": {}
    }
    
    # Check required columns
    if data_type == "daily":
        required = ["date", "open", "high", "low", "close", "volume"]
    else:
        required = ["timestamp", "open", "high", "low", "close", "volume"]
    
    missing = [col for col in required if col not in df.columns]
    if missing:
        results["valid"] = False
        results["errors"].append(f"Missing columns: {missing}")
    
    # Check for null values
    null_counts = df[required].isnull().sum()
    if null_counts.any():
        results["warnings"].append(f"Null values found: {null_counts[null_counts > 0].to_dict()}")
    
    # Check OHLC logic
    if all(col in df.columns for col in ["open", "high", "low", "close"]):
        invalid_ohlc = df[(df["high"] < df["low"]) | 
                         (df["high"] < df["open"]) | 
                         (df["high"] < df["close"]) |
                         (df["low"] > df["open"]) |
                         (df["low"] > df["close"])]
        if len(invalid_ohlc) > 0:
            results["warnings"].append(f"Invalid OHLC logic in {len(invalid_ohlc)} rows")
    
    # Stats
    results["stats"] = {
        "total_rows": len(df),
        "date_range": f"{df['date'].min() if 'date' in df.columns else df['timestamp'].min()} to {df['date'].max() if 'date' in df.columns else df['timestamp'].max()}",
        "stocks": df["stock_code"].nunique() if "stock_code" in df.columns else 1
    }
    
    return results

# Example usage and testing
if __name__ == "__main__":
    print("\n" + "="*60)
    print("📊 STOCK DATA FETCHER - Test Mode")
    print("="*60 + "\n")
    
    # Check/install yfinance
    if not check_yfinance():
        install_yfinance()
    
    import pandas as pd
    
    # Test fetch single stock daily
    print("Testing daily data fetch for BBCA...")
    try:
        df = fetch_daily_data_yfinance("BBCA", "3mo")
        if not df.empty:
            print(f"✓ Fetched {len(df)} rows")
            print(df.head())
            
            # Validate
            validation = validate_data(df, "daily")
            print(f"\nValidation: {'✓ PASSED' if validation['valid'] else '✗ FAILED'}")
            if validation["warnings"]:
                print(f"Warnings: {validation['warnings']}")
            print(f"Stats: {validation['stats']}")
        else:
            print("✗ No data returned")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print("\n" + "-"*60)
    print("To fetch all stocks, run:")
    print("  fetch_all_stocks_daily(period='1y', save_path='data/all_daily.csv')")
    print("  fetch_all_stocks_hourly(period='1mo', save_path='data/all_hourly.csv')")
    print("-"*60 + "\n")

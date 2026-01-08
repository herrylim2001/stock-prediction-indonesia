"""
Market Analyzer - IHSG Correlation, Beta, Market Regime
Specialized for Indonesian Stock Exchange (IDX)
"""
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta


class MarketAnalyzer:
    """Analyze market context for IDX stocks"""

    def __init__(self):
        self.ihsg_data = None
        self.ihsg_ticker = "^JKSE"  # Jakarta Composite Index

    def fetch_ihsg(self, period="6mo"):
        """
        Fetch IHSG (Jakarta Composite Index) data

        Args:
            period: Data period (1mo, 3mo, 6mo, 1y, 2y)

        Returns:
            DataFrame with IHSG data
        """
        try:
            ihsg = yf.Ticker(self.ihsg_ticker)
            df = ihsg.history(period=period)

            if df.empty:
                return None

            df = df.reset_index()
            df.columns = [col.lower() for col in df.columns]
            df['returns'] = df['close'].pct_change()

            self.ihsg_data = df
            return df

        except Exception as e:
            print(f"Error fetching IHSG: {e}")
            return None

    def calculate_beta(self, stock_df, ihsg_df=None):
        """
        Calculate stock beta vs IHSG
        Beta = Cov(Stock, IHSG) / Var(IHSG)

        Args:
            stock_df: Stock dataframe with 'returns' column
            ihsg_df: IHSG dataframe (optional, will fetch if None)

        Returns:
            dict with beta and interpretation
        """
        if ihsg_df is None:
            ihsg_df = self.ihsg_data if self.ihsg_data is not None else self.fetch_ihsg()

        if ihsg_df is None or len(ihsg_df) < 30:
            return {
                'beta': 1.0,
                'interpretation': 'Data insufficient',
                'reliability': 'Low'
            }

        # Align dates
        stock_df = stock_df.copy()
        if 'date' in stock_df.columns:
            stock_df['date'] = pd.to_datetime(stock_df['date']).dt.date
        if 'date' in ihsg_df.columns:
            ihsg_df['date'] = pd.to_datetime(ihsg_df['date']).dt.date

        # Merge on date
        merged = pd.merge(
            stock_df[['date', 'returns']],
            ihsg_df[['date', 'returns']],
            on='date',
            suffixes=('_stock', '_ihsg')
        )

        # Remove NaN
        merged = merged.dropna()

        if len(merged) < 30:
            return {
                'beta': 1.0,
                'interpretation': 'Insufficient overlapping data',
                'reliability': 'Low'
            }

        # Calculate beta
        covariance = merged['returns_stock'].cov(merged['returns_ihsg'])
        variance = merged['returns_ihsg'].var()

        if variance == 0:
            beta = 1.0
        else:
            beta = covariance / variance

        # Calculate correlation
        correlation = merged['returns_stock'].corr(merged['returns_ihsg'])

        # Interpretation
        if beta > 1.5:
            interpretation = "Very High Risk - Bergerak 50%+ lebih volatile dari IHSG"
        elif beta > 1.2:
            interpretation = "High Risk - Lebih volatile dari IHSG"
        elif beta > 0.8:
            interpretation = "Medium Risk - Sejalan dengan IHSG"
        elif beta > 0.5:
            interpretation = "Low Risk - Kurang volatile dari IHSG"
        else:
            interpretation = "Very Low Risk / Defensive - Pergerakan independent dari IHSG"

        # Reliability based on correlation
        if abs(correlation) > 0.7:
            reliability = "High"
        elif abs(correlation) > 0.4:
            reliability = "Medium"
        else:
            reliability = "Low"

        return {
            'beta': round(beta, 3),
            'correlation': round(correlation, 3),
            'interpretation': interpretation,
            'reliability': reliability,
            'data_points': len(merged)
        }

    def detect_market_regime(self, ihsg_df=None):
        """
        Detect current market regime: Bull, Bear, or Sideways

        Args:
            ihsg_df: IHSG dataframe (optional)

        Returns:
            dict with regime and details
        """
        if ihsg_df is None:
            ihsg_df = self.ihsg_data if self.ihsg_data is not None else self.fetch_ihsg()

        if ihsg_df is None or len(ihsg_df) < 50:
            return {
                'regime': 'UNKNOWN',
                'confidence': 0.0,
                'explanation': 'Data insufficient',
                'trend_strength': 0.0
            }

        # Calculate SMAs
        ihsg_df['sma_20'] = ihsg_df['close'].rolling(window=20).mean()
        ihsg_df['sma_50'] = ihsg_df['close'].rolling(window=50).mean()

        latest = ihsg_df.iloc[-1]
        prev_20 = ihsg_df.iloc[-20] if len(ihsg_df) >= 20 else ihsg_df.iloc[0]
        prev_50 = ihsg_df.iloc[-50] if len(ihsg_df) >= 50 else ihsg_df.iloc[0]

        # Calculate returns
        return_20d = ((latest['close'] - prev_20['close']) / prev_20['close']) * 100
        return_50d = ((latest['close'] - prev_50['close']) / prev_50['close']) * 100

        # Trend analysis
        price = latest['close']
        sma_20 = latest['sma_20']
        sma_50 = latest['sma_50']

        # Score calculation
        score = 0

        # Price vs SMAs
        if pd.notna(sma_20) and price > sma_20:
            score += 2
        elif pd.notna(sma_20) and price < sma_20:
            score -= 2

        if pd.notna(sma_50) and price > sma_50:
            score += 3
        elif pd.notna(sma_50) and price < sma_50:
            score -= 3

        # SMA trend
        if pd.notna(sma_20) and pd.notna(sma_50):
            if sma_20 > sma_50:
                score += 2
            elif sma_20 < sma_50:
                score -= 2

        # Returns
        if return_20d > 5:
            score += 2
        elif return_20d < -5:
            score -= 2

        if return_50d > 10:
            score += 2
        elif return_50d < -10:
            score -= 2

        # Determine regime
        if score >= 5:
            regime = "BULL MARKET"
            confidence = min((score / 11) * 100, 100)
            explanation = f"IHSG dalam trend naik kuat. Return 20D: {return_20d:+.1f}%, 50D: {return_50d:+.1f}%"
        elif score >= 2:
            regime = "BULL TRENDING"
            confidence = min((score / 11) * 100, 100)
            explanation = f"IHSG cenderung naik. Return 20D: {return_20d:+.1f}%, 50D: {return_50d:+.1f}%"
        elif score <= -5:
            regime = "BEAR MARKET"
            confidence = min((abs(score) / 11) * 100, 100)
            explanation = f"IHSG dalam trend turun kuat. Return 20D: {return_20d:+.1f}%, 50D: {return_50d:+.1f}%"
        elif score <= -2:
            regime = "BEAR TRENDING"
            confidence = min((abs(score) / 11) * 100, 100)
            explanation = f"IHSG cenderung turun. Return 20D: {return_20d:+.1f}%, 50D: {return_50d:+.1f}%"
        else:
            regime = "SIDEWAYS"
            confidence = 60.0
            explanation = f"IHSG bergerak sideways. Return 20D: {return_20d:+.1f}%, 50D: {return_50d:+.1f}%"

        # Volatility
        volatility = ihsg_df['returns'].tail(20).std() * np.sqrt(252) * 100

        return {
            'regime': regime,
            'confidence': round(confidence, 1),
            'explanation': explanation,
            'score': score,
            'ihsg_price': round(latest['close'], 2),
            'return_20d': round(return_20d, 2),
            'return_50d': round(return_50d, 2),
            'volatility': round(volatility, 2),
            'trend_strength': abs(score)
        }

    def get_market_context(self, stock_df):
        """
        Get complete market context for a stock

        Args:
            stock_df: Stock dataframe

        Returns:
            dict with all market analysis
        """
        # Fetch IHSG if not already cached
        if self.ihsg_data is None:
            self.fetch_ihsg()

        # Calculate beta
        beta_analysis = self.calculate_beta(stock_df)

        # Detect regime
        regime_analysis = self.detect_market_regime()

        # Combined analysis
        return {
            'beta': beta_analysis,
            'regime': regime_analysis,
            'ihsg_data': self.ihsg_data
        }

    def get_sector_classification(self, stock_code):
        """
        Get sector classification for IDX stocks

        Args:
            stock_code: Stock ticker (e.g., 'BBCA')

        Returns:
            dict with sector info
        """
        sectors = {
            # Banking
            'BBCA': {'sector': 'Banking', 'sub_sector': 'Bank', 'category': 'Blue Chip'},
            'BBRI': {'sector': 'Banking', 'sub_sector': 'Bank', 'category': 'Blue Chip'},
            'BMRI': {'sector': 'Banking', 'sub_sector': 'Bank', 'category': 'Blue Chip'},
            'BBNI': {'sector': 'Banking', 'sub_sector': 'Bank', 'category': 'Blue Chip'},

            # Telecommunication
            'TLKM': {'sector': 'Telecommunication', 'sub_sector': 'Telco', 'category': 'Blue Chip'},
            'ISAT': {'sector': 'Telecommunication', 'sub_sector': 'Telco', 'category': 'Second Liner'},
            'EXCL': {'sector': 'Telecommunication', 'sub_sector': 'Telco', 'category': 'Second Liner'},

            # Consumer Goods
            'UNVR': {'sector': 'Consumer Goods', 'sub_sector': 'Consumer Non-Cyclicals', 'category': 'Blue Chip'},
            'ICBP': {'sector': 'Consumer Goods', 'sub_sector': 'Food & Beverage', 'category': 'Blue Chip'},
            'INDF': {'sector': 'Consumer Goods', 'sub_sector': 'Food & Beverage', 'category': 'Blue Chip'},

            # Automotive
            'ASII': {'sector': 'Automotive', 'sub_sector': 'Automotive & Components', 'category': 'Blue Chip'},

            # Technology
            'GOTO': {'sector': 'Technology', 'sub_sector': 'Internet & E-Commerce', 'category': 'Growth'},
            'EMTK': {'sector': 'Media', 'sub_sector': 'Media & Entertainment', 'category': 'Second Liner'},

            # Retail
            'ACES': {'sector': 'Retail', 'sub_sector': 'Retail Trade', 'category': 'Second Liner'},

            # Mining
            'ANTM': {'sector': 'Mining', 'sub_sector': 'Metals & Mining', 'category': 'Commodity'},
            'INCO': {'sector': 'Mining', 'sub_sector': 'Metals & Mining', 'category': 'Commodity'},

            # Energy
            'PGAS': {'sector': 'Energy', 'sub_sector': 'Oil & Gas', 'category': 'State-Owned'},
        }

        return sectors.get(stock_code, {
            'sector': 'Unknown',
            'sub_sector': 'Unknown',
            'category': 'Other'
        })


# Singleton instance
_market_analyzer = None

def get_market_analyzer():
    """Get or create MarketAnalyzer instance"""
    global _market_analyzer
    if _market_analyzer is None:
        _market_analyzer = MarketAnalyzer()
    return _market_analyzer

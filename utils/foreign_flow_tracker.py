"""
Foreign Flow Tracker
====================

Track foreign investor buy/sell activity in Indonesian stocks.
Foreign flow is a critical indicator for IDX market movements.

Data sources:
- IDX daily summary (scraping)
- RTI foreign flow (if available)
- Calculated from volume patterns (estimation)
"""

import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import yfinance as yf


class ForeignFlowTracker:
    """Track foreign investor activity"""

    def __init__(self, stock_code: str):
        """
        Initialize Foreign Flow Tracker

        Args:
            stock_code: Stock ticker (e.g., 'BBCA.JK')
        """
        self.stock_code = stock_code
        self.idx_url = "https://www.idx.co.id"

    def estimate_foreign_flow_from_volume(
        self,
        df: pd.DataFrame,
        lookback_days: int = 20
    ) -> Dict:
        """
        Estimate foreign flow using volume patterns

        Large volume spikes often correlate with foreign activity
        This is an estimation method when direct data not available

        Args:
            df: DataFrame with OHLCV data
            lookback_days: Days to analyze

        Returns:
            Dict with estimated foreign flow metrics
        """
        if len(df) < lookback_days:
            return {'error': 'Insufficient data'}

        recent_data = df.tail(lookback_days).copy()

        # Calculate volume statistics
        avg_volume = recent_data['Volume'].mean()
        std_volume = recent_data['Volume'].std()

        # Detect volume spikes (>1.5 std above mean)
        threshold = avg_volume + (1.5 * std_volume)
        recent_data['volume_spike'] = recent_data['Volume'] > threshold

        # Classify spikes by price movement
        recent_data['price_change'] = recent_data['Close'].pct_change()

        # Bullish spikes (volume + price up) = likely foreign buy
        bullish_spikes = recent_data[
            (recent_data['volume_spike']) &
            (recent_data['price_change'] > 0.01)  # >1% gain
        ]

        # Bearish spikes (volume + price down) = likely foreign sell
        bearish_spikes = recent_data[
            (recent_data['volume_spike']) &
            (recent_data['price_change'] < -0.01)  # >1% loss
        ]

        # Calculate estimated foreign activity score
        foreign_buy_score = len(bullish_spikes)
        foreign_sell_score = len(bearish_spikes)
        total_spikes = foreign_buy_score + foreign_sell_score

        # Net foreign sentiment
        if total_spikes > 0:
            net_sentiment = (foreign_buy_score - foreign_sell_score) / total_spikes
        else:
            net_sentiment = 0

        # Determine foreign pressure
        if net_sentiment > 0.3:
            pressure = 'STRONG_BUY'
            pressure_emoji = '🟢🟢'
        elif net_sentiment > 0:
            pressure = 'BUY'
            pressure_emoji = '🟢'
        elif net_sentiment > -0.3:
            pressure = 'NEUTRAL'
            pressure_emoji = '🟡'
        elif net_sentiment > -0.6:
            pressure = 'SELL'
            pressure_emoji = '🔴'
        else:
            pressure = 'STRONG_SELL'
            pressure_emoji = '🔴🔴'

        return {
            'method': 'Volume Pattern Estimation',
            'lookback_days': lookback_days,
            'bullish_volume_spikes': foreign_buy_score,
            'bearish_volume_spikes': foreign_sell_score,
            'total_spikes': total_spikes,
            'net_sentiment': net_sentiment,
            'foreign_pressure': pressure,
            'pressure_emoji': pressure_emoji,
            'avg_daily_volume': avg_volume,
            'recent_volume_trend': recent_data['Volume'].iloc[-5:].mean() / avg_volume,
            'interpretation': self._interpret_foreign_flow(
                foreign_buy_score,
                foreign_sell_score,
                net_sentiment
            )
        }

    def estimate_foreign_ownership_change(
        self,
        df: pd.DataFrame,
        window: int = 30
    ) -> Dict:
        """
        Estimate foreign ownership change over time

        Uses cumulative volume analysis to infer ownership changes

        Args:
            df: DataFrame with OHLCV data
            window: Rolling window for analysis

        Returns:
            Dict with ownership change estimates
        """
        if len(df) < window * 2:
            return {'error': 'Insufficient data'}

        recent = df.tail(window * 2).copy()

        # Calculate cumulative volume-weighted price changes
        recent['volume_weighted_change'] = (
            recent['Close'].pct_change() * recent['Volume']
        )

        # Split into two periods
        mid_point = len(recent) // 2
        period1 = recent.iloc[:mid_point]
        period2 = recent.iloc[mid_point:]

        # Analyze each period
        period1_net_flow = period1['volume_weighted_change'].sum()
        period2_net_flow = period2['volume_weighted_change'].sum()

        # Detect accumulation or distribution
        flow_change = period2_net_flow - period1_net_flow

        if flow_change > 0:
            trend = 'ACCUMULATION'
            interpretation = 'Foreign investors likely accumulating'
        elif flow_change < 0:
            trend = 'DISTRIBUTION'
            interpretation = 'Foreign investors likely distributing'
        else:
            trend = 'STABLE'
            interpretation = 'No significant ownership change'

        return {
            'method': 'Ownership Change Estimation',
            'window_days': window,
            'period1_flow': period1_net_flow,
            'period2_flow': period2_net_flow,
            'flow_change': flow_change,
            'trend': trend,
            'interpretation': interpretation,
            'confidence': 'MEDIUM (estimated from volume patterns)'
        }

    def get_idx_foreign_summary(self, date: Optional[str] = None) -> Dict:
        """
        Get foreign transaction summary from IDX website

        Note: This requires web scraping and may need maintenance
        when IDX updates their website structure

        Args:
            date: Date string in 'YYYY-MM-DD' format (default: today)

        Returns:
            Dict with foreign transaction data
        """
        # Placeholder - actual implementation requires scraping
        # IDX publishes daily foreign buy/sell at:
        # https://www.idx.co.id/data-pasar/data-saham/transaksi-asing/

        return {
            'method': 'IDX Website Scraping',
            'status': 'NOT_IMPLEMENTED',
            'note': 'Requires web scraping from idx.co.id',
            'alternative': 'Use estimate_foreign_flow_from_volume() for approximation'
        }

    def calculate_foreign_flow_indicators(
        self,
        df: pd.DataFrame
    ) -> Dict:
        """
        Calculate multiple foreign flow indicators

        Args:
            df: DataFrame with OHLCV data

        Returns:
            Dict with comprehensive foreign flow analysis
        """
        # 1. Volume-based estimation (short-term)
        short_term = self.estimate_foreign_flow_from_volume(df, lookback_days=10)

        # 2. Medium-term trend
        medium_term = self.estimate_foreign_flow_from_volume(df, lookback_days=30)

        # 3. Ownership change
        ownership = self.estimate_foreign_ownership_change(df, window=30)

        # 4. Volume momentum
        recent_volume = df['Volume'].tail(5).mean()
        avg_volume = df['Volume'].tail(60).mean()
        volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1

        # Aggregate signals
        short_pressure = short_term.get('foreign_pressure', 'NEUTRAL')
        medium_pressure = medium_term.get('foreign_pressure', 'NEUTRAL')

        # Overall assessment
        if short_pressure in ['STRONG_BUY', 'BUY'] and medium_pressure in ['STRONG_BUY', 'BUY']:
            overall = 'STRONG_FOREIGN_BUY'
            recommendation = '🟢 Strong foreign buying detected across timeframes'
        elif short_pressure in ['STRONG_SELL', 'SELL'] and medium_pressure in ['STRONG_SELL', 'SELL']:
            overall = 'STRONG_FOREIGN_SELL'
            recommendation = '🔴 Strong foreign selling detected across timeframes'
        elif short_pressure == medium_pressure:
            overall = f'CONSISTENT_{short_pressure}'
            recommendation = f'🟡 Consistent {short_pressure.lower()} pressure'
        else:
            overall = 'MIXED_SIGNALS'
            recommendation = '⚠️ Mixed foreign flow signals - wait for clarity'

        return {
            'stock_code': self.stock_code,
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'short_term': short_term,
            'medium_term': medium_term,
            'ownership_change': ownership,
            'volume_metrics': {
                'recent_volume_ratio': volume_ratio,
                'volume_trend': 'Increasing' if volume_ratio > 1.2 else 'Decreasing' if volume_ratio < 0.8 else 'Stable'
            },
            'overall_assessment': {
                'signal': overall,
                'recommendation': recommendation,
                'confidence': 'MEDIUM (volume-based estimation)',
                'note': 'For higher accuracy, use actual foreign transaction data from IDX'
            }
        }

    def get_foreign_flow_summary(self, df: pd.DataFrame) -> Dict:
        """
        Get comprehensive foreign flow summary

        Args:
            df: DataFrame with OHLCV data

        Returns:
            Complete foreign flow analysis
        """
        indicators = self.calculate_foreign_flow_indicators(df)

        # Build easy-to-read summary
        summary = {
            'stock_code': self.stock_code,
            'as_of': datetime.now().strftime('%Y-%m-%d'),
            'foreign_pressure': {
                'short_term_10d': indicators['short_term']['foreign_pressure'],
                'medium_term_30d': indicators['medium_term']['foreign_pressure'],
                'overall': indicators['overall_assessment']['signal']
            },
            'key_metrics': {
                'recent_bullish_spikes': indicators['short_term']['bullish_volume_spikes'],
                'recent_bearish_spikes': indicators['short_term']['bearish_volume_spikes'],
                'net_sentiment_10d': indicators['short_term']['net_sentiment'],
                'net_sentiment_30d': indicators['medium_term']['net_sentiment'],
                'volume_trend': indicators['volume_metrics']['volume_trend']
            },
            'interpretation': {
                'short_term': indicators['short_term']['interpretation'],
                'ownership': indicators['ownership_change']['interpretation'],
                'recommendation': indicators['overall_assessment']['recommendation']
            },
            'detailed_analysis': indicators
        }

        return summary

    def _interpret_foreign_flow(
        self,
        buy_signals: int,
        sell_signals: int,
        net_sentiment: float
    ) -> str:
        """Generate interpretation text"""
        total = buy_signals + sell_signals

        if total == 0:
            return "No significant foreign activity detected"

        if net_sentiment > 0.5:
            return f"Strong foreign buying - {buy_signals} bullish signals vs {sell_signals} bearish"
        elif net_sentiment > 0.2:
            return f"Moderate foreign buying - {buy_signals} bullish signals vs {sell_signals} bearish"
        elif net_sentiment > -0.2:
            return f"Balanced foreign activity - {buy_signals} buys vs {sell_signals} sells"
        elif net_sentiment > -0.5:
            return f"Moderate foreign selling - {sell_signals} bearish signals vs {buy_signals} bullish"
        else:
            return f"Strong foreign selling - {sell_signals} bearish signals vs {buy_signals} bullish"

    def compare_with_market(
        self,
        stock_df: pd.DataFrame,
        ihsg_df: pd.DataFrame
    ) -> Dict:
        """
        Compare stock foreign flow with IHSG market flow

        Args:
            stock_df: Stock OHLCV data
            ihsg_df: IHSG OHLCV data

        Returns:
            Dict with comparative analysis
        """
        # Analyze both
        stock_flow = self.estimate_foreign_flow_from_volume(stock_df, 20)
        ihsg_flow = self.estimate_foreign_flow_from_volume(ihsg_df, 20)

        stock_pressure = stock_flow.get('foreign_pressure', 'NEUTRAL')
        market_pressure = ihsg_flow.get('foreign_pressure', 'NEUTRAL')

        # Compare
        if stock_pressure == market_pressure:
            relationship = 'ALIGNED'
            interpretation = f'Stock following market trend ({stock_pressure})'
        elif stock_pressure in ['STRONG_BUY', 'BUY'] and market_pressure in ['SELL', 'STRONG_SELL']:
            relationship = 'OUTPERFORMING'
            interpretation = 'Stock attracting foreign interest despite market weakness 🌟'
        elif stock_pressure in ['SELL', 'STRONG_SELL'] and market_pressure in ['BUY', 'STRONG_BUY']:
            relationship = 'UNDERPERFORMING'
            interpretation = 'Stock facing foreign selling despite market strength ⚠️'
        else:
            relationship = 'DIVERGING'
            interpretation = 'Stock trend diverging from market'

        return {
            'stock_pressure': stock_pressure,
            'market_pressure': market_pressure,
            'relationship': relationship,
            'interpretation': interpretation,
            'stock_sentiment': stock_flow.get('net_sentiment', 0),
            'market_sentiment': ihsg_flow.get('net_sentiment', 0)
        }


def format_foreign_flow_summary(summary: Dict) -> str:
    """
    Format foreign flow summary for display

    Args:
        summary: Dict from get_foreign_flow_summary()

    Returns:
        Formatted string
    """
    lines = []

    # Header
    lines.append(f"**Foreign Flow Analysis: {summary['stock_code']}**")
    lines.append(f"As of: {summary['as_of']}")
    lines.append("")

    # Foreign Pressure
    pressure = summary['foreign_pressure']
    lines.append("### Foreign Pressure")
    lines.append(f"**Short-term (10d):** {pressure['short_term_10d']}")
    lines.append(f"**Medium-term (30d):** {pressure['medium_term_30d']}")
    lines.append(f"**Overall Signal:** {pressure['overall']}")
    lines.append("")

    # Key Metrics
    metrics = summary['key_metrics']
    lines.append("### Activity Indicators")
    lines.append(f"📈 Bullish Volume Spikes: {metrics['recent_bullish_spikes']}")
    lines.append(f"📉 Bearish Volume Spikes: {metrics['recent_bearish_spikes']}")
    lines.append(f"📊 Net Sentiment (10d): {metrics['net_sentiment_10d']:.2f}")
    lines.append(f"📊 Net Sentiment (30d): {metrics['net_sentiment_30d']:.2f}")
    lines.append(f"📦 Volume Trend: {metrics['volume_trend']}")
    lines.append("")

    # Interpretation
    interp = summary['interpretation']
    lines.append("### Analysis")
    lines.append(f"**Short-term:** {interp['short_term']}")
    lines.append(f"**Ownership:** {interp['ownership']}")
    lines.append(f"**Recommendation:** {interp['recommendation']}")
    lines.append("")

    lines.append("*Note: Analysis based on volume pattern estimation.*")
    lines.append("*For higher accuracy, use actual foreign transaction data.*")

    return "\n".join(lines)

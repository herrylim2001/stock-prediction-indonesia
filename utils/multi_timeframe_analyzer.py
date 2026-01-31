"""
Multi-Timeframe Analysis
=========================

Analyze stock across multiple timeframes (H4, Daily, Weekly) to:
- Detect trend alignment
- Calculate timeframe confluence
- Improve signal quality
- Implement top-down analysis

For Indonesian Stock Market (IDX)
"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple, List


class MultiTimeframeAnalyzer:
    """Analyze stocks across multiple timeframes"""

    def __init__(self, stock_code: str):
        """
        Initialize Multi-Timeframe Analyzer

        Args:
            stock_code: Stock ticker code (e.g., 'BBCA.JK')
        """
        self.stock_code = stock_code
        self.timeframes = {
            '4h': None,     # 4-hour (intraday)
            'daily': None,  # Daily
            'weekly': None  # Weekly
        }

    def fetch_timeframe_data(
        self,
        timeframe: str,
        period: str = '3mo'
    ) -> Optional[pd.DataFrame]:
        """
        Fetch data for specific timeframe

        Args:
            timeframe: '1h', '4h', '1d', '1wk'
            period: Data period (1mo, 3mo, 6mo, 1y)

        Returns:
            DataFrame with OHLCV data
        """
        try:
            ticker = yf.Ticker(self.stock_code)

            # Map timeframe to yfinance interval
            interval_map = {
                '1h': '1h',
                '4h': '1h',  # Download 1h and resample
                'daily': '1d',
                'weekly': '1wk'
            }

            interval = interval_map.get(timeframe, '1d')
            df = ticker.history(period=period, interval=interval)

            if df.empty:
                return None

            # Resample 1h to 4h if needed
            if timeframe == '4h' and interval == '1h':
                df = self._resample_to_4h(df)

            df = df.reset_index()
            df.columns = [col.lower().replace(' ', '_') for col in df.columns]

            # Calculate basic indicators
            df = self._add_timeframe_indicators(df)

            return df

        except Exception as e:
            print(f"Error fetching {timeframe} data: {e}")
            return None

    def _resample_to_4h(self, df: pd.DataFrame) -> pd.DataFrame:
        """Resample 1h data to 4h"""
        # Set index to datetime if not already
        if 'Date' in df.columns or 'Datetime' in df.columns:
            df = df.set_index('Date' if 'Date' in df.columns else 'Datetime')

        # Resample OHLCV
        resampled = pd.DataFrame()
        resampled['Open'] = df['Open'].resample('4H').first()
        resampled['High'] = df['High'].resample('4H').max()
        resampled['Low'] = df['Low'].resample('4H').min()
        resampled['Close'] = df['Close'].resample('4H').last()
        resampled['Volume'] = df['Volume'].resample('4H').sum()

        return resampled.dropna()

    def _add_timeframe_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add technical indicators for timeframe analysis"""
        if len(df) < 50:
            return df

        # Moving Averages
        df['sma_20'] = df['close'].rolling(window=20).mean()
        df['sma_50'] = df['close'].rolling(window=50).mean()
        df['ema_12'] = df['close'].ewm(span=12, adjust=False).mean()
        df['ema_26'] = df['close'].ewm(span=26, adjust=False).mean()

        # MACD
        df['macd'] = df['ema_12'] - df['ema_26']
        df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        df['macd_histogram'] = df['macd'] - df['macd_signal']

        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))

        # Trend determination
        df['trend'] = np.where(df['close'] > df['sma_20'], 'UP', 'DOWN')
        df['trend_strength'] = abs(df['close'] - df['sma_20']) / df['sma_20'] * 100

        return df

    def get_timeframe_trend(self, df: pd.DataFrame) -> Dict:
        """
        Analyze trend for a specific timeframe

        Args:
            df: DataFrame with OHLCV and indicators

        Returns:
            dict with trend analysis
        """
        if df is None or len(df) < 20:
            return {'trend': 'UNKNOWN', 'confidence': 0}

        latest = df.iloc[-1]

        # Trend criteria
        criteria = {
            'price_above_sma20': latest['close'] > latest['sma_20'],
            'price_above_sma50': latest['close'] > latest['sma_50'] if 'sma_50' in df.columns else None,
            'sma20_above_sma50': latest['sma_20'] > latest['sma_50'] if 'sma_50' in df.columns else None,
            'macd_positive': latest['macd'] > 0 if 'macd' in df.columns else None,
            'macd_above_signal': latest['macd'] > latest['macd_signal'] if 'macd' in df.columns else None,
            'rsi_bullish': latest['rsi'] > 50 if 'rsi' in df.columns else None
        }

        # Count bullish signals
        bullish_count = sum(1 for v in criteria.values() if v is True)
        bearish_count = sum(1 for v in criteria.values() if v is False)
        total_criteria = sum(1 for v in criteria.values() if v is not None)

        # Determine trend
        if bullish_count >= total_criteria * 0.7:
            trend = 'UPTREND'
            confidence = (bullish_count / total_criteria) * 100
        elif bearish_count >= total_criteria * 0.7:
            trend = 'DOWNTREND'
            confidence = (bearish_count / total_criteria) * 100
        else:
            trend = 'SIDEWAYS'
            confidence = 50

        return {
            'trend': trend,
            'confidence': confidence,
            'criteria': criteria,
            'bullish_count': bullish_count,
            'bearish_count': bearish_count,
            'current_price': latest['close'],
            'sma_20': latest['sma_20'],
            'rsi': latest['rsi'] if 'rsi' in df.columns else None,
            'macd': latest['macd'] if 'macd' in df.columns else None
        }

    def analyze_all_timeframes(self) -> Dict:
        """
        Analyze all timeframes (4H, Daily, Weekly)

        Returns:
            dict with analysis for each timeframe
        """
        results = {}

        # Define timeframes to analyze
        timeframes_config = {
            # '4h': {'period': '1mo', 'name': '4-Hour'},  # Commented out - might not have intraday
            'daily': {'period': '6mo', 'name': 'Daily'},
            'weekly': {'period': '2y', 'name': 'Weekly'}
        }

        for tf, config in timeframes_config.items():
            df = self.fetch_timeframe_data(tf, period=config['period'])

            if df is not None:
                self.timeframes[tf] = df
                trend_analysis = self.get_timeframe_trend(df)
                trend_analysis['timeframe'] = config['name']
                results[tf] = trend_analysis
            else:
                results[tf] = {
                    'trend': 'NO_DATA',
                    'confidence': 0,
                    'timeframe': config['name']
                }

        return results

    def calculate_timeframe_confluence(
        self,
        timeframe_analysis: Dict
    ) -> Dict:
        """
        Calculate confluence across timeframes

        Strong signals occur when multiple timeframes align

        Args:
            timeframe_analysis: Dict from analyze_all_timeframes()

        Returns:
            dict with confluence analysis
        """
        # Extract trends
        trends = {
            tf: data.get('trend', 'UNKNOWN')
            for tf, data in timeframe_analysis.items()
            if data.get('trend') != 'NO_DATA'
        }

        if not trends:
            return {
                'confluence_score': 0,
                'alignment': 'NO_DATA',
                'recommendation': 'Insufficient data for confluence analysis'
            }

        # Count trend directions
        uptrend_count = sum(1 for t in trends.values() if t == 'UPTREND')
        downtrend_count = sum(1 for t in trends.values() if t == 'DOWNTREND')
        sideways_count = sum(1 for t in trends.values() if t == 'SIDEWAYS')
        total_timeframes = len(trends)

        # Calculate confluence score (0-100)
        if uptrend_count == total_timeframes:
            confluence_score = 100
            alignment = 'STRONG_BULLISH'
            recommendation = '🟢 STRONG BUY - All timeframes aligned bullish'
        elif downtrend_count == total_timeframes:
            confluence_score = 100
            alignment = 'STRONG_BEARISH'
            recommendation = '🔴 STRONG SELL - All timeframes aligned bearish'
        elif uptrend_count > downtrend_count and uptrend_count >= total_timeframes * 0.7:
            confluence_score = 70 + (uptrend_count / total_timeframes * 30)
            alignment = 'BULLISH'
            recommendation = '🟢 BUY - Majority timeframes bullish'
        elif downtrend_count > uptrend_count and downtrend_count >= total_timeframes * 0.7:
            confluence_score = 70 + (downtrend_count / total_timeframes * 30)
            alignment = 'BEARISH'
            recommendation = '🔴 SELL - Majority timeframes bearish'
        else:
            confluence_score = 50 - (sideways_count / total_timeframes * 20)
            alignment = 'NEUTRAL'
            recommendation = '🟡 HOLD - Mixed timeframe signals'

        return {
            'confluence_score': confluence_score,
            'alignment': alignment,
            'uptrend_count': uptrend_count,
            'downtrend_count': downtrend_count,
            'sideways_count': sideways_count,
            'total_timeframes': total_timeframes,
            'recommendation': recommendation,
            'details': trends
        }

    def get_entry_timeframe_recommendation(
        self,
        confluence: Dict
    ) -> Dict:
        """
        Recommend which timeframe to use for entry

        Top-down approach: Use higher timeframe for direction,
        lower timeframe for entry

        Args:
            confluence: Dict from calculate_timeframe_confluence()

        Returns:
            dict with entry recommendations
        """
        alignment = confluence.get('alignment', 'NEUTRAL')

        if alignment in ['STRONG_BULLISH', 'BULLISH']:
            return {
                'direction_timeframe': 'Weekly/Daily',
                'entry_timeframe': 'Daily/4H',
                'strategy': 'Buy on pullbacks in lower timeframe',
                'entry_signal': 'Wait for Daily/4H to pull back to support, then enter on reversal',
                'stop_loss_timeframe': 'Daily',
                'target_timeframe': 'Weekly'
            }
        elif alignment in ['STRONG_BEARISH', 'BEARISH']:
            return {
                'direction_timeframe': 'Weekly/Daily',
                'entry_timeframe': 'Daily/4H',
                'strategy': 'Sell on rallies in lower timeframe',
                'entry_signal': 'Wait for Daily/4H rally to resistance, then enter on reversal',
                'stop_loss_timeframe': 'Daily',
                'target_timeframe': 'Weekly'
            }
        else:
            return {
                'direction_timeframe': 'UNCLEAR',
                'entry_timeframe': 'N/A',
                'strategy': 'Stay out - No clear trend',
                'entry_signal': 'Wait for timeframe alignment',
                'stop_loss_timeframe': 'N/A',
                'target_timeframe': 'N/A'
            }

    def generate_multi_timeframe_report(self) -> Dict:
        """
        Generate comprehensive multi-timeframe analysis report

        Returns:
            Complete analysis with all timeframes
        """
        # Analyze all timeframes
        timeframe_analysis = self.analyze_all_timeframes()

        # Calculate confluence
        confluence = self.calculate_timeframe_confluence(timeframe_analysis)

        # Get entry recommendations
        entry_rec = self.get_entry_timeframe_recommendation(confluence)

        # Build report
        report = {
            'stock_code': self.stock_code,
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'timeframe_analysis': timeframe_analysis,
            'confluence': confluence,
            'entry_recommendation': entry_rec,
            'summary': {
                'confluence_score': confluence['confluence_score'],
                'alignment': confluence['alignment'],
                'primary_trend': self._get_primary_trend(timeframe_analysis),
                'trade_recommendation': confluence['recommendation']
            }
        }

        return report

    def _get_primary_trend(self, timeframe_analysis: Dict) -> str:
        """Determine primary trend (from higher timeframe)"""
        # Priority: Weekly > Daily > 4H
        for tf in ['weekly', 'daily', '4h']:
            if tf in timeframe_analysis and timeframe_analysis[tf].get('trend') != 'NO_DATA':
                return timeframe_analysis[tf]['trend']

        return 'UNKNOWN'


def format_multi_timeframe_report(report: Dict) -> str:
    """
    Format multi-timeframe report for display

    Args:
        report: Dict from generate_multi_timeframe_report()

    Returns:
        Formatted string for display
    """
    lines = []

    # Header
    lines.append(f"**Multi-Timeframe Analysis: {report['stock_code']}**")
    lines.append(f"Analysis Date: {report['analysis_date']}")
    lines.append("")

    # Timeframe Analysis
    lines.append("### Timeframe Trends")
    for tf, data in report['timeframe_analysis'].items():
        if data['trend'] != 'NO_DATA':
            trend_emoji = {
                'UPTREND': '📈',
                'DOWNTREND': '📉',
                'SIDEWAYS': '↔️'
            }.get(data['trend'], '❓')

            lines.append(f"**{data['timeframe']}:** {trend_emoji} {data['trend']} "
                        f"(Confidence: {data['confidence']:.0f}%)")

    lines.append("")

    # Confluence
    conf = report['confluence']
    lines.append("### Timeframe Confluence")
    lines.append(f"**Confluence Score:** {conf['confluence_score']:.0f}/100")
    lines.append(f"**Alignment:** {conf['alignment']}")
    lines.append(f"**Recommendation:** {conf['recommendation']}")
    lines.append("")

    # Entry Strategy
    entry = report['entry_recommendation']
    lines.append("### Entry Strategy")
    lines.append(f"**Direction Timeframe:** {entry['direction_timeframe']}")
    lines.append(f"**Entry Timeframe:** {entry['entry_timeframe']}")
    lines.append(f"**Strategy:** {entry['strategy']}")
    lines.append(f"**Entry Signal:** {entry['entry_signal']}")

    return "\n".join(lines)

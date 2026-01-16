"""
Volume Profile Analysis for Technical Analysis
Analyzes volume distribution at price levels: POC, Value Area, VWAP, etc.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


class VolumeProfileAnalyzer:
    """
    Analyze volume distribution at different price levels
    """

    def __init__(self, df, bins=20):
        """
        Initialize with OHLCV dataframe

        Args:
            df: DataFrame with columns ['Open', 'High', 'Low', 'Close', 'Volume']
            bins: Number of price levels to analyze (default: 20)
        """
        self.df = df.copy()
        self.df = self.df.sort_index()
        self.bins = bins

        # Calculate volume profile
        self._calculate_volume_profile()

    def _calculate_volume_profile(self):
        """Calculate volume distribution across price levels"""
        # Get price range
        self.price_min = self.df['Low'].min()
        self.price_max = self.df['High'].max()
        self.price_range = self.price_max - self.price_min

        # Create price bins
        self.price_levels = np.linspace(self.price_min, self.price_max, self.bins + 1)

        # Initialize volume at each price level
        self.volume_at_price = np.zeros(self.bins)

        # Distribute volume across price levels for each candle
        for idx, row in self.df.iterrows():
            candle_low = row['Low']
            candle_high = row['High']
            candle_volume = row['Volume']

            # Find which bins this candle covers
            for i in range(self.bins):
                bin_low = self.price_levels[i]
                bin_high = self.price_levels[i + 1]
                bin_mid = (bin_low + bin_high) / 2

                # If candle intersects this bin, add volume
                if candle_low <= bin_high and candle_high >= bin_low:
                    # Proportional volume distribution
                    overlap = min(candle_high, bin_high) - max(candle_low, bin_low)
                    candle_range = candle_high - candle_low

                    if candle_range > 0:
                        volume_proportion = overlap / candle_range
                        self.volume_at_price[i] += candle_volume * volume_proportion
                    else:
                        # Single price candle
                        if abs(bin_mid - candle_low) < (bin_high - bin_low) / 2:
                            self.volume_at_price[i] += candle_volume

    def get_point_of_control(self):
        """
        Get Point of Control (POC) - price level with highest volume

        Returns:
            dict: POC information
        """
        poc_idx = np.argmax(self.volume_at_price)
        poc_price = (self.price_levels[poc_idx] + self.price_levels[poc_idx + 1]) / 2
        poc_volume = self.volume_at_price[poc_idx]

        current_price = self.df['Close'].iloc[-1]

        # Determine if POC is support or resistance
        if current_price > poc_price:
            poc_role = 'SUPPORT'
            signal = 'BULLISH' if abs(current_price - poc_price) / poc_price < 0.02 else 'NEUTRAL'
        elif current_price < poc_price:
            poc_role = 'RESISTANCE'
            signal = 'BEARISH' if abs(current_price - poc_price) / poc_price < 0.02 else 'NEUTRAL'
        else:
            poc_role = 'PIVOT'
            signal = 'NEUTRAL'

        return {
            'price': poc_price,
            'volume': poc_volume,
            'role': poc_role,
            'signal': signal,
            'distance_pct': (current_price - poc_price) / poc_price * 100
        }

    def get_value_area(self):
        """
        Get Value Area (VA) - price range containing 70% of volume

        Returns:
            dict: Value area information
        """
        total_volume = np.sum(self.volume_at_price)
        target_volume = total_volume * 0.70

        # Start from POC and expand
        poc_idx = np.argmax(self.volume_at_price)

        # Expand from POC
        accumulated_volume = self.volume_at_price[poc_idx]
        lower_idx = poc_idx
        upper_idx = poc_idx

        while accumulated_volume < target_volume:
            # Check which direction has more volume
            lower_volume = self.volume_at_price[lower_idx - 1] if lower_idx > 0 else 0
            upper_volume = self.volume_at_price[upper_idx + 1] if upper_idx < self.bins - 1 else 0

            if lower_volume > upper_volume and lower_idx > 0:
                lower_idx -= 1
                accumulated_volume += self.volume_at_price[lower_idx]
            elif upper_idx < self.bins - 1:
                upper_idx += 1
                accumulated_volume += self.volume_at_price[upper_idx]
            else:
                break

        va_low = self.price_levels[lower_idx]
        va_high = self.price_levels[upper_idx + 1]

        current_price = self.df['Close'].iloc[-1]

        # Position relative to value area
        if current_price > va_high:
            position = 'ABOVE_VA'
            signal = 'BULLISH'  # Price above value = strong
        elif current_price < va_low:
            position = 'BELOW_VA'
            signal = 'BEARISH'  # Price below value = weak
        else:
            position = 'INSIDE_VA'
            signal = 'NEUTRAL'  # Fair value

        return {
            'low': va_low,
            'high': va_high,
            'width': va_high - va_low,
            'width_pct': (va_high - va_low) / va_low * 100,
            'position': position,
            'signal': signal,
            'volume_pct': accumulated_volume / total_volume * 100
        }

    def get_high_volume_nodes(self, threshold_percentile=75):
        """
        Get High Volume Nodes (HVN) - significant support/resistance levels

        Args:
            threshold_percentile: Percentile threshold for HVN (default: 75)

        Returns:
            list: HVN price levels
        """
        threshold = np.percentile(self.volume_at_price, threshold_percentile)

        hvn_levels = []

        for i in range(self.bins):
            if self.volume_at_price[i] >= threshold:
                price = (self.price_levels[i] + self.price_levels[i + 1]) / 2
                hvn_levels.append({
                    'price': price,
                    'volume': self.volume_at_price[i],
                    'type': 'HVN'
                })

        # Sort by volume
        hvn_levels = sorted(hvn_levels, key=lambda x: x['volume'], reverse=True)

        return hvn_levels

    def get_low_volume_nodes(self, threshold_percentile=25):
        """
        Get Low Volume Nodes (LVN) - potential breakout/breakdown zones

        Args:
            threshold_percentile: Percentile threshold for LVN (default: 25)

        Returns:
            list: LVN price levels
        """
        threshold = np.percentile(self.volume_at_price, threshold_percentile)

        lvn_levels = []

        for i in range(self.bins):
            if self.volume_at_price[i] <= threshold and self.volume_at_price[i] > 0:
                price = (self.price_levels[i] + self.price_levels[i + 1]) / 2
                lvn_levels.append({
                    'price': price,
                    'volume': self.volume_at_price[i],
                    'type': 'LVN'
                })

        # Sort by price
        lvn_levels = sorted(lvn_levels, key=lambda x: x['price'])

        return lvn_levels

    def get_vwap(self, periods=20):
        """
        Calculate Volume Weighted Average Price (VWAP)

        Args:
            periods: Number of periods to calculate (default: 20)

        Returns:
            dict: VWAP information
        """
        recent_data = self.df.tail(periods)

        # Typical price
        recent_data = recent_data.copy()
        recent_data['typical_price'] = (recent_data['High'] + recent_data['Low'] + recent_data['Close']) / 3

        # VWAP calculation
        total_volume = recent_data['Volume'].sum()

        if total_volume > 0:
            vwap = (recent_data['typical_price'] * recent_data['Volume']).sum() / total_volume
        else:
            vwap = recent_data['Close'].mean()

        current_price = self.df['Close'].iloc[-1]
        distance_pct = (current_price - vwap) / vwap * 100

        # Signal based on distance from VWAP
        if distance_pct > 2:
            signal = 'OVERBOUGHT'  # Price significantly above VWAP
            strength = min(abs(distance_pct) * 5, 80)
        elif distance_pct < -2:
            signal = 'OVERSOLD'  # Price significantly below VWAP
            strength = min(abs(distance_pct) * 5, 80)
        else:
            signal = 'NEUTRAL'
            strength = 40

        return {
            'vwap': vwap,
            'current_price': current_price,
            'distance_pct': distance_pct,
            'signal': signal,
            'strength': strength,
            'periods': periods
        }

    def get_volume_trend(self, periods=10):
        """
        Analyze volume trend (increasing/decreasing)

        Args:
            periods: Number of periods to analyze

        Returns:
            dict: Volume trend information
        """
        recent_volumes = self.df['Volume'].tail(periods).values

        if len(recent_volumes) < 5:
            return {'trend': 'INSUFFICIENT_DATA', 'signal': 'NEUTRAL', 'strength': 0}

        # Linear regression on volume
        x = np.arange(len(recent_volumes))
        slope, intercept = np.polyfit(x, recent_volumes, 1)

        avg_volume = np.mean(recent_volumes)
        slope_pct = (slope * len(recent_volumes)) / avg_volume * 100

        # Determine trend
        if slope_pct > 10:
            trend = 'INCREASING'
            signal = 'BULLISH'  # Rising volume = conviction
            strength = min(slope_pct * 2, 80)
        elif slope_pct < -10:
            trend = 'DECREASING'
            signal = 'BEARISH'  # Falling volume = weakening
            strength = min(abs(slope_pct) * 2, 80)
        else:
            trend = 'STABLE'
            signal = 'NEUTRAL'
            strength = 40

        return {
            'trend': trend,
            'slope_pct': slope_pct,
            'avg_volume': avg_volume,
            'latest_volume': recent_volumes[-1],
            'signal': signal,
            'strength': strength
        }

    def get_volume_price_analysis(self):
        """
        Comprehensive volume-price analysis

        Returns:
            dict: Complete analysis
        """
        poc = self.get_point_of_control()
        va = self.get_value_area()
        hvn = self.get_high_volume_nodes()
        lvn = self.get_low_volume_nodes()
        vwap = self.get_vwap()
        volume_trend = self.get_volume_trend()

        current_price = self.df['Close'].iloc[-1]

        # Find nearest support/resistance from HVN
        hvn_support = None
        hvn_resistance = None

        for level in hvn:
            if level['price'] < current_price:
                if hvn_support is None or level['price'] > hvn_support['price']:
                    hvn_support = level
            elif level['price'] > current_price:
                if hvn_resistance is None or level['price'] < hvn_resistance['price']:
                    hvn_resistance = level

        # Aggregate signal
        signals = []
        strengths = []

        if poc['signal'] != 'NEUTRAL':
            signals.append(poc['signal'])
            strengths.append(60)

        if va['signal'] != 'NEUTRAL':
            signals.append(va['signal'])
            strengths.append(70)

        if vwap['signal'] == 'OVERBOUGHT':
            signals.append('BEARISH')
            strengths.append(vwap['strength'])
        elif vwap['signal'] == 'OVERSOLD':
            signals.append('BULLISH')
            strengths.append(vwap['strength'])

        if volume_trend['signal'] != 'NEUTRAL':
            signals.append(volume_trend['signal'])
            strengths.append(volume_trend['strength'])

        # Calculate aggregate
        bullish_count = signals.count('BULLISH')
        bearish_count = signals.count('BEARISH')

        if bullish_count > bearish_count:
            aggregate_signal = 'BULLISH'
            avg_strength = np.mean([strengths[i] for i, s in enumerate(signals) if s == 'BULLISH'])
        elif bearish_count > bullish_count:
            aggregate_signal = 'BEARISH'
            avg_strength = np.mean([strengths[i] for i, s in enumerate(signals) if s == 'BEARISH'])
        else:
            aggregate_signal = 'NEUTRAL'
            avg_strength = 50

        return {
            'poc': poc,
            'value_area': va,
            'vwap': vwap,
            'volume_trend': volume_trend,
            'hvn_support': hvn_support,
            'hvn_resistance': hvn_resistance,
            'hvn_count': len(hvn),
            'lvn_count': len(lvn),
            'aggregate_signal': aggregate_signal,
            'signal_strength': avg_strength,
            'current_price': current_price
        }

    def get_volume_momentum_indicator(self):
        """
        Get volume-based momentum indicator for predictions

        Returns:
            dict: Volume momentum score and signal
        """
        analysis = self.get_volume_price_analysis()

        momentum_score = 0
        confidence_factors = []

        # 1. Value Area position (±30 points)
        va_signal = analysis['value_area']['signal']
        if va_signal == 'BULLISH':
            momentum_score += 30
            confidence_factors.append(0.85)
        elif va_signal == 'BEARISH':
            momentum_score -= 30
            confidence_factors.append(0.85)

        # 2. VWAP position (±25 points)
        vwap_distance = analysis['vwap']['distance_pct']
        if vwap_distance < -2:  # Below VWAP = oversold = bullish
            momentum_score += min(abs(vwap_distance) * 5, 25)
            confidence_factors.append(0.75)
        elif vwap_distance > 2:  # Above VWAP = overbought = bearish
            momentum_score -= min(vwap_distance * 5, 25)
            confidence_factors.append(0.75)

        # 3. Volume trend (±20 points)
        vol_trend = analysis['volume_trend']
        if vol_trend['trend'] == 'INCREASING':
            # Increasing volume confirms trend direction
            if analysis['aggregate_signal'] == 'BULLISH':
                momentum_score += 20
            elif analysis['aggregate_signal'] == 'BEARISH':
                momentum_score -= 20
            confidence_factors.append(0.70)

        # 4. POC distance (±15 points)
        poc_distance = analysis['poc']['distance_pct']
        if abs(poc_distance) > 3:  # Far from POC = potential mean reversion
            if poc_distance > 0:
                momentum_score -= 15  # Above POC, expect pullback
            else:
                momentum_score += 15  # Below POC, expect bounce
            confidence_factors.append(0.60)

        # 5. Support/Resistance proximity (±10 points)
        current_price = analysis['current_price']

        if analysis['hvn_support']:
            support_distance = (current_price - analysis['hvn_support']['price']) / current_price * 100
            if 0 < support_distance < 2:  # Near support
                momentum_score += 10
                confidence_factors.append(0.65)

        if analysis['hvn_resistance']:
            resistance_distance = (analysis['hvn_resistance']['price'] - current_price) / current_price * 100
            if 0 < resistance_distance < 2:  # Near resistance
                momentum_score -= 10
                confidence_factors.append(0.65)

        # Calculate overall confidence
        confidence = np.mean(confidence_factors) if confidence_factors else 0.5

        # Determine signal
        if momentum_score > 20:
            signal = 'BULLISH'
        elif momentum_score < -20:
            signal = 'BEARISH'
        else:
            signal = 'NEUTRAL'

        return {
            'momentum': momentum_score,
            'signal': signal,
            'confidence': confidence,
            'poc_price': analysis['poc']['price'],
            'vwap_price': analysis['vwap']['vwap'],
            'value_area': {
                'low': analysis['value_area']['low'],
                'high': analysis['value_area']['high']
            },
            'analysis': analysis
        }


def get_volume_profile(df, bins=20):
    """
    Convenience function to get volume profile analysis

    Args:
        df: OHLCV DataFrame
        bins: Number of price levels

    Returns:
        dict: Volume profile analysis
    """
    analyzer = VolumeProfileAnalyzer(df, bins)
    return analyzer.get_volume_momentum_indicator()

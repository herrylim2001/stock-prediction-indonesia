"""
Chart Pattern Detection for Technical Analysis
Detects classical chart patterns: Head & Shoulders, Double Top/Bottom, Triangles, etc.
"""
import pandas as pd
import numpy as np
from scipy.signal import argrelextrema
from datetime import datetime, timedelta


class ChartPatternDetector:
    """
    Detect classical chart patterns in price data
    """

    def __init__(self, df):
        """
        Initialize with OHLCV dataframe

        Args:
            df: DataFrame with columns ['Open', 'High', 'Low', 'Close', 'Volume']
        """
        self.df = df.copy()
        self.df = self.df.sort_index()

        # Find local maxima and minima
        self.highs_idx = argrelextrema(self.df['High'].values, np.greater, order=5)[0]
        self.lows_idx = argrelextrema(self.df['Low'].values, np.less, order=5)[0]

    def detect_all_patterns(self):
        """
        Detect all chart patterns

        Returns:
            dict: All detected patterns with signals
        """
        patterns = {
            'head_and_shoulders': self.detect_head_and_shoulders(),
            'inverse_head_and_shoulders': self.detect_inverse_head_and_shoulders(),
            'double_top': self.detect_double_top(),
            'double_bottom': self.detect_double_bottom(),
            'triple_top': self.detect_triple_top(),
            'triple_bottom': self.detect_triple_bottom(),
            'ascending_triangle': self.detect_ascending_triangle(),
            'descending_triangle': self.detect_descending_triangle(),
            'symmetrical_triangle': self.detect_symmetrical_triangle(),
            'cup_and_handle': self.detect_cup_and_handle(),
            'falling_wedge': self.detect_falling_wedge(),
            'rising_wedge': self.detect_rising_wedge(),
            'flag': self.detect_flag(),
            'pennant': self.detect_pennant(),
        }

        # Calculate aggregate signal
        bullish_count = 0
        bearish_count = 0
        total_strength = 0

        for pattern_name, pattern_data in patterns.items():
            if pattern_data['detected']:
                strength = pattern_data.get('strength', 50)
                total_strength += strength

                if pattern_data['signal'] == 'BULLISH':
                    bullish_count += 1
                elif pattern_data['signal'] == 'BEARISH':
                    bearish_count += 1

        # Aggregate signal
        if bullish_count > bearish_count:
            aggregate_signal = 'BULLISH'
            signal_strength = (bullish_count - bearish_count) * (total_strength / max(bullish_count + bearish_count, 1))
        elif bearish_count > bullish_count:
            aggregate_signal = 'BEARISH'
            signal_strength = (bearish_count - bullish_count) * (total_strength / max(bullish_count + bearish_count, 1))
        else:
            aggregate_signal = 'NEUTRAL'
            signal_strength = 0

        patterns['summary'] = {
            'bullish_patterns': bullish_count,
            'bearish_patterns': bearish_count,
            'aggregate_signal': aggregate_signal,
            'signal_strength': min(signal_strength, 100),  # Cap at 100
            'detected_patterns': [name for name, data in patterns.items() if data.get('detected', False)]
        }

        return patterns

    def detect_head_and_shoulders(self):
        """
        Detect Head and Shoulders pattern (bearish reversal)

        Pattern: Left Shoulder - Head - Right Shoulder with neckline
        Signal: BEARISH (price breaks below neckline)
        """
        if len(self.highs_idx) < 3:
            return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

        # Get recent highs (last 60 days)
        recent_highs = self.highs_idx[self.highs_idx >= len(self.df) - 60]

        if len(recent_highs) < 3:
            return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

        # Check last 3 highs
        for i in range(len(recent_highs) - 2):
            left_shoulder_idx = recent_highs[i]
            head_idx = recent_highs[i + 1]
            right_shoulder_idx = recent_highs[i + 2]

            left_shoulder = self.df['High'].iloc[left_shoulder_idx]
            head = self.df['High'].iloc[head_idx]
            right_shoulder = self.df['High'].iloc[right_shoulder_idx]

            # Head should be higher than shoulders
            if head > left_shoulder and head > right_shoulder:
                # Shoulders should be roughly equal (within 3%)
                shoulder_diff_pct = abs(left_shoulder - right_shoulder) / left_shoulder * 100

                if shoulder_diff_pct < 3:
                    # Check if price broke neckline
                    current_price = self.df['Close'].iloc[-1]
                    neckline = min(left_shoulder, right_shoulder)

                    if current_price < neckline:
                        return {
                            'detected': True,
                            'signal': 'BEARISH',
                            'strength': 85,
                            'pattern': 'Head and Shoulders',
                            'neckline': neckline,
                            'target': neckline - (head - neckline)  # Measured move
                        }

        return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

    def detect_inverse_head_and_shoulders(self):
        """
        Detect Inverse Head and Shoulders pattern (bullish reversal)

        Pattern: Left Shoulder - Head - Right Shoulder (inverted)
        Signal: BULLISH (price breaks above neckline)
        """
        if len(self.lows_idx) < 3:
            return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

        # Get recent lows
        recent_lows = self.lows_idx[self.lows_idx >= len(self.df) - 60]

        if len(recent_lows) < 3:
            return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

        # Check last 3 lows
        for i in range(len(recent_lows) - 2):
            left_shoulder_idx = recent_lows[i]
            head_idx = recent_lows[i + 1]
            right_shoulder_idx = recent_lows[i + 2]

            left_shoulder = self.df['Low'].iloc[left_shoulder_idx]
            head = self.df['Low'].iloc[head_idx]
            right_shoulder = self.df['Low'].iloc[right_shoulder_idx]

            # Head should be lower than shoulders
            if head < left_shoulder and head < right_shoulder:
                # Shoulders should be roughly equal
                shoulder_diff_pct = abs(left_shoulder - right_shoulder) / left_shoulder * 100

                if shoulder_diff_pct < 3:
                    # Check if price broke neckline
                    current_price = self.df['Close'].iloc[-1]
                    neckline = max(left_shoulder, right_shoulder)

                    if current_price > neckline:
                        return {
                            'detected': True,
                            'signal': 'BULLISH',
                            'strength': 85,
                            'pattern': 'Inverse Head and Shoulders',
                            'neckline': neckline,
                            'target': neckline + (neckline - head)  # Measured move
                        }

        return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

    def detect_double_top(self):
        """
        Detect Double Top pattern (bearish reversal)

        Pattern: Two peaks at roughly same level
        Signal: BEARISH (price breaks below support)
        """
        if len(self.highs_idx) < 2:
            return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

        recent_highs = self.highs_idx[self.highs_idx >= len(self.df) - 40]

        if len(recent_highs) < 2:
            return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

        # Check last 2 highs
        for i in range(len(recent_highs) - 1):
            first_top_idx = recent_highs[i]
            second_top_idx = recent_highs[i + 1]

            first_top = self.df['High'].iloc[first_top_idx]
            second_top = self.df['High'].iloc[second_top_idx]

            # Tops should be within 2% of each other
            diff_pct = abs(first_top - second_top) / first_top * 100

            if diff_pct < 2:
                # Find support level (lowest low between tops)
                between_lows = self.df['Low'].iloc[first_top_idx:second_top_idx]
                if len(between_lows) > 0:
                    support = between_lows.min()
                    current_price = self.df['Close'].iloc[-1]

                    # Check if price broke support
                    if current_price < support:
                        return {
                            'detected': True,
                            'signal': 'BEARISH',
                            'strength': 75,
                            'pattern': 'Double Top',
                            'resistance': (first_top + second_top) / 2,
                            'support': support,
                            'target': support - (first_top - support)
                        }

        return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

    def detect_double_bottom(self):
        """
        Detect Double Bottom pattern (bullish reversal)

        Pattern: Two troughs at roughly same level
        Signal: BULLISH (price breaks above resistance)
        """
        if len(self.lows_idx) < 2:
            return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

        recent_lows = self.lows_idx[self.lows_idx >= len(self.df) - 40]

        if len(recent_lows) < 2:
            return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

        # Check last 2 lows
        for i in range(len(recent_lows) - 1):
            first_bottom_idx = recent_lows[i]
            second_bottom_idx = recent_lows[i + 1]

            first_bottom = self.df['Low'].iloc[first_bottom_idx]
            second_bottom = self.df['Low'].iloc[second_bottom_idx]

            # Bottoms should be within 2% of each other
            diff_pct = abs(first_bottom - second_bottom) / first_bottom * 100

            if diff_pct < 2:
                # Find resistance level (highest high between bottoms)
                between_highs = self.df['High'].iloc[first_bottom_idx:second_bottom_idx]
                if len(between_highs) > 0:
                    resistance = between_highs.max()
                    current_price = self.df['Close'].iloc[-1]

                    # Check if price broke resistance
                    if current_price > resistance:
                        return {
                            'detected': True,
                            'signal': 'BULLISH',
                            'strength': 75,
                            'pattern': 'Double Bottom',
                            'support': (first_bottom + second_bottom) / 2,
                            'resistance': resistance,
                            'target': resistance + (resistance - first_bottom)
                        }

        return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

    def detect_triple_top(self):
        """Detect Triple Top pattern (strong bearish reversal)"""
        if len(self.highs_idx) < 3:
            return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

        recent_highs = self.highs_idx[self.highs_idx >= len(self.df) - 50]

        if len(recent_highs) < 3:
            return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

        for i in range(len(recent_highs) - 2):
            top1 = self.df['High'].iloc[recent_highs[i]]
            top2 = self.df['High'].iloc[recent_highs[i + 1]]
            top3 = self.df['High'].iloc[recent_highs[i + 2]]

            avg_top = (top1 + top2 + top3) / 3

            # All tops within 2% of average
            if all(abs(top - avg_top) / avg_top * 100 < 2 for top in [top1, top2, top3]):
                support = self.df['Low'].iloc[recent_highs[i]:recent_highs[i + 2]].min()
                current_price = self.df['Close'].iloc[-1]

                if current_price < support:
                    return {
                        'detected': True,
                        'signal': 'BEARISH',
                        'strength': 90,
                        'pattern': 'Triple Top',
                        'resistance': avg_top,
                        'support': support
                    }

        return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

    def detect_triple_bottom(self):
        """Detect Triple Bottom pattern (strong bullish reversal)"""
        if len(self.lows_idx) < 3:
            return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

        recent_lows = self.lows_idx[self.lows_idx >= len(self.df) - 50]

        if len(recent_lows) < 3:
            return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

        for i in range(len(recent_lows) - 2):
            bottom1 = self.df['Low'].iloc[recent_lows[i]]
            bottom2 = self.df['Low'].iloc[recent_lows[i + 1]]
            bottom3 = self.df['Low'].iloc[recent_lows[i + 2]]

            avg_bottom = (bottom1 + bottom2 + bottom3) / 3

            # All bottoms within 2% of average
            if all(abs(bottom - avg_bottom) / avg_bottom * 100 < 2 for bottom in [bottom1, bottom2, bottom3]):
                resistance = self.df['High'].iloc[recent_lows[i]:recent_lows[i + 2]].max()
                current_price = self.df['Close'].iloc[-1]

                if current_price > resistance:
                    return {
                        'detected': True,
                        'signal': 'BULLISH',
                        'strength': 90,
                        'pattern': 'Triple Bottom',
                        'support': avg_bottom,
                        'resistance': resistance
                    }

        return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

    def detect_ascending_triangle(self):
        """
        Detect Ascending Triangle (bullish continuation)

        Pattern: Flat resistance + rising support
        Signal: BULLISH (breakout above resistance)
        """
        if len(self.df) < 30:
            return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

        recent_data = self.df.tail(30)

        # Find resistance (recent highs should be flat)
        recent_highs = recent_data['High'].rolling(5).max()
        resistance = recent_highs.max()

        # Check if highs are forming flat resistance
        high_values = recent_data.nlargest(3, 'High')['High'].values
        if len(high_values) >= 3:
            resistance_flat = np.std(high_values) / np.mean(high_values) < 0.02  # Less than 2% variation

            if resistance_flat:
                # Check if lows are rising
                lows = recent_data['Low'].values
                if len(lows) >= 10:
                    # Linear regression on lows
                    x = np.arange(len(lows))
                    slope, _ = np.polyfit(x, lows, 1)

                    if slope > 0:  # Rising lows
                        current_price = self.df['Close'].iloc[-1]

                        # Breakout above resistance
                        if current_price > resistance:
                            return {
                                'detected': True,
                                'signal': 'BULLISH',
                                'strength': 70,
                                'pattern': 'Ascending Triangle',
                                'resistance': resistance,
                                'target': resistance + (resistance - lows[0]) * 0.5
                            }

        return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

    def detect_descending_triangle(self):
        """
        Detect Descending Triangle (bearish continuation)

        Pattern: Flat support + falling resistance
        Signal: BEARISH (breakdown below support)
        """
        if len(self.df) < 30:
            return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

        recent_data = self.df.tail(30)

        # Find support (recent lows should be flat)
        recent_lows = recent_data['Low'].rolling(5).min()
        support = recent_lows.min()

        # Check if lows are forming flat support
        low_values = recent_data.nsmallest(3, 'Low')['Low'].values
        if len(low_values) >= 3:
            support_flat = np.std(low_values) / np.mean(low_values) < 0.02

            if support_flat:
                # Check if highs are falling
                highs = recent_data['High'].values
                if len(highs) >= 10:
                    x = np.arange(len(highs))
                    slope, _ = np.polyfit(x, highs, 1)

                    if slope < 0:  # Falling highs
                        current_price = self.df['Close'].iloc[-1]

                        # Breakdown below support
                        if current_price < support:
                            return {
                                'detected': True,
                                'signal': 'BEARISH',
                                'strength': 70,
                                'pattern': 'Descending Triangle',
                                'support': support,
                                'target': support - (highs[0] - support) * 0.5
                            }

        return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

    def detect_symmetrical_triangle(self):
        """
        Detect Symmetrical Triangle (consolidation pattern)

        Pattern: Converging trendlines
        Signal: Direction of breakout determines signal
        """
        if len(self.df) < 30:
            return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

        recent_data = self.df.tail(30)

        highs = recent_data['High'].values
        lows = recent_data['Low'].values

        if len(highs) >= 10 and len(lows) >= 10:
            x = np.arange(len(highs))

            # Trendline slopes
            high_slope, _ = np.polyfit(x, highs, 1)
            low_slope, _ = np.polyfit(x, lows, 1)

            # Converging: highs falling, lows rising
            if high_slope < 0 and low_slope > 0:
                current_price = self.df['Close'].iloc[-1]
                upper_trendline = highs[0] + high_slope * len(highs)
                lower_trendline = lows[0] + low_slope * len(lows)

                # Breakout detection
                if current_price > upper_trendline:
                    return {
                        'detected': True,
                        'signal': 'BULLISH',
                        'strength': 65,
                        'pattern': 'Symmetrical Triangle (Bullish Breakout)'
                    }
                elif current_price < lower_trendline:
                    return {
                        'detected': True,
                        'signal': 'BEARISH',
                        'strength': 65,
                        'pattern': 'Symmetrical Triangle (Bearish Breakdown)'
                    }

        return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

    def detect_cup_and_handle(self):
        """
        Detect Cup and Handle pattern (bullish continuation)

        Pattern: U-shaped cup followed by small consolidation (handle)
        Signal: BULLISH (breakout from handle)
        """
        if len(self.df) < 60:
            return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

        data = self.df.tail(60)

        # Divide into cup (first 45 days) and handle (last 15 days)
        cup = data.iloc[:45]
        handle = data.iloc[45:]

        # Cup: should have U-shape (low in middle, high at ends)
        cup_low = cup['Low'].min()
        cup_low_idx = cup['Low'].idxmin()

        # Check if low is in middle third
        low_position = list(cup.index).index(cup_low_idx) / len(cup)

        if 0.3 < low_position < 0.7:
            # Cup rim should be relatively flat
            cup_start_high = cup['High'].iloc[:5].max()
            cup_end_high = cup['High'].iloc[-5:].max()

            if abs(cup_start_high - cup_end_high) / cup_start_high < 0.05:
                # Handle: small consolidation below cup rim
                handle_high = handle['High'].max()

                if handle_high < cup_end_high * 1.02:  # Handle within 2% of cup rim
                    current_price = self.df['Close'].iloc[-1]

                    # Breakout above cup rim
                    if current_price > cup_end_high:
                        return {
                            'detected': True,
                            'signal': 'BULLISH',
                            'strength': 80,
                            'pattern': 'Cup and Handle',
                            'cup_depth': cup_start_high - cup_low,
                            'target': cup_end_high + (cup_start_high - cup_low)
                        }

        return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

    def detect_falling_wedge(self):
        """
        Detect Falling Wedge (bullish reversal)

        Pattern: Converging trendlines sloping down
        Signal: BULLISH (breakout to upside)
        """
        if len(self.df) < 30:
            return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

        recent_data = self.df.tail(30)
        highs = recent_data['High'].values
        lows = recent_data['Low'].values

        if len(highs) >= 10:
            x = np.arange(len(highs))
            high_slope, _ = np.polyfit(x, highs, 1)
            low_slope, _ = np.polyfit(x, lows, 1)

            # Both slopes negative and converging
            if high_slope < 0 and low_slope < 0 and low_slope > high_slope:
                current_price = self.df['Close'].iloc[-1]
                upper_trendline = highs[0] + high_slope * len(highs)

                if current_price > upper_trendline:
                    return {
                        'detected': True,
                        'signal': 'BULLISH',
                        'strength': 70,
                        'pattern': 'Falling Wedge'
                    }

        return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

    def detect_rising_wedge(self):
        """
        Detect Rising Wedge (bearish reversal)

        Pattern: Converging trendlines sloping up
        Signal: BEARISH (breakdown to downside)
        """
        if len(self.df) < 30:
            return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

        recent_data = self.df.tail(30)
        highs = recent_data['High'].values
        lows = recent_data['Low'].values

        if len(highs) >= 10:
            x = np.arange(len(highs))
            high_slope, _ = np.polyfit(x, highs, 1)
            low_slope, _ = np.polyfit(x, lows, 1)

            # Both slopes positive and converging
            if high_slope > 0 and low_slope > 0 and high_slope > low_slope:
                current_price = self.df['Close'].iloc[-1]
                lower_trendline = lows[0] + low_slope * len(lows)

                if current_price < lower_trendline:
                    return {
                        'detected': True,
                        'signal': 'BEARISH',
                        'strength': 70,
                        'pattern': 'Rising Wedge'
                    }

        return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

    def detect_flag(self):
        """
        Detect Flag pattern (continuation pattern)

        Pattern: Sharp move followed by parallel channel consolidation
        Signal: Continues in direction of initial move
        """
        if len(self.df) < 30:
            return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

        # Look for sharp move in last 30 days
        data = self.df.tail(30)

        # Initial move (first 10 days)
        initial_move = data.iloc[:10]
        flag_pole_start = initial_move['Close'].iloc[0]
        flag_pole_end = initial_move['Close'].iloc[-1]
        move_pct = (flag_pole_end - flag_pole_start) / flag_pole_start * 100

        # Sharp move (>5%)
        if abs(move_pct) > 5:
            # Flag (consolidation in parallel channel)
            flag_data = data.iloc[10:]

            if len(flag_data) >= 10:
                highs = flag_data['High'].values
                lows = flag_data['Low'].values
                x = np.arange(len(highs))

                high_slope, _ = np.polyfit(x, highs, 1)
                low_slope, _ = np.polyfit(x, lows, 1)

                # Parallel channel (slopes similar)
                if abs(high_slope - low_slope) / abs(high_slope) < 0.3:
                    current_price = self.df['Close'].iloc[-1]

                    if move_pct > 5:  # Bullish flag
                        upper_channel = highs[0] + high_slope * len(highs)
                        if current_price > upper_channel:
                            return {
                                'detected': True,
                                'signal': 'BULLISH',
                                'strength': 75,
                                'pattern': 'Bull Flag'
                            }
                    elif move_pct < -5:  # Bearish flag
                        lower_channel = lows[0] + low_slope * len(lows)
                        if current_price < lower_channel:
                            return {
                                'detected': True,
                                'signal': 'BEARISH',
                                'strength': 75,
                                'pattern': 'Bear Flag'
                            }

        return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

    def detect_pennant(self):
        """
        Detect Pennant pattern (continuation pattern)

        Pattern: Sharp move followed by symmetrical triangle
        Signal: Continues in direction of initial move
        """
        if len(self.df) < 30:
            return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

        data = self.df.tail(30)

        # Sharp initial move
        initial_move = data.iloc[:10]
        move_pct = (initial_move['Close'].iloc[-1] - initial_move['Close'].iloc[0]) / initial_move['Close'].iloc[0] * 100

        if abs(move_pct) > 5:
            # Pennant (converging trendlines)
            pennant_data = data.iloc[10:]

            if len(pennant_data) >= 10:
                highs = pennant_data['High'].values
                lows = pennant_data['Low'].values
                x = np.arange(len(highs))

                high_slope, _ = np.polyfit(x, highs, 1)
                low_slope, _ = np.polyfit(x, lows, 1)

                # Converging
                if (high_slope < 0 and low_slope > 0) or (high_slope > 0 and low_slope < 0 and abs(low_slope) > abs(high_slope)):
                    current_price = self.df['Close'].iloc[-1]

                    if move_pct > 5:  # Bullish pennant
                        return {
                            'detected': True,
                            'signal': 'BULLISH',
                            'strength': 70,
                            'pattern': 'Bullish Pennant'
                        }
                    elif move_pct < -5:  # Bearish pennant
                        return {
                            'detected': True,
                            'signal': 'BEARISH',
                            'strength': 70,
                            'pattern': 'Bearish Pennant'
                        }

        return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}


def get_chart_patterns(df):
    """
    Convenience function to get all chart patterns

    Args:
        df: OHLCV DataFrame

    Returns:
        dict: All detected patterns
    """
    detector = ChartPatternDetector(df)
    return detector.detect_all_patterns()

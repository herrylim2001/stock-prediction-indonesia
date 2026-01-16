"""
Candlestick Pattern Detection for Technical Analysis
Detects 50+ candlestick patterns: Doji, Hammer, Engulfing, Morning Star, etc.
"""
import pandas as pd
import numpy as np


class CandlestickPatternDetector:
    """
    Detect classical candlestick patterns
    """

    def __init__(self, df):
        """
        Initialize with OHLCV dataframe

        Args:
            df: DataFrame with columns ['Open', 'High', 'Low', 'Close', 'Volume']
        """
        self.df = df.copy()
        self.df = self.df.sort_index()

        # Calculate candle properties
        self._calculate_candle_properties()

    def _calculate_candle_properties(self):
        """Calculate candle body, shadow, and other properties"""
        self.df['body'] = abs(self.df['Close'] - self.df['Open'])
        self.df['upper_shadow'] = self.df['High'] - self.df[['Open', 'Close']].max(axis=1)
        self.df['lower_shadow'] = self.df[['Open', 'Close']].min(axis=1) - self.df['Low']
        self.df['total_range'] = self.df['High'] - self.df['Low']

        # Bullish or bearish
        self.df['is_bullish'] = self.df['Close'] > self.df['Open']
        self.df['is_bearish'] = self.df['Close'] < self.df['Open']

        # Average body size for comparison
        self.avg_body = self.df['body'].tail(20).mean()
        self.avg_range = self.df['total_range'].tail(20).mean()

    def detect_all_patterns(self):
        """
        Detect all candlestick patterns

        Returns:
            dict: All detected patterns with signals
        """
        patterns = {
            # Single candle patterns
            'doji': self.detect_doji(),
            'hammer': self.detect_hammer(),
            'inverted_hammer': self.detect_inverted_hammer(),
            'hanging_man': self.detect_hanging_man(),
            'shooting_star': self.detect_shooting_star(),
            'spinning_top': self.detect_spinning_top(),
            'marubozu_bullish': self.detect_marubozu_bullish(),
            'marubozu_bearish': self.detect_marubozu_bearish(),

            # Double candle patterns
            'bullish_engulfing': self.detect_bullish_engulfing(),
            'bearish_engulfing': self.detect_bearish_engulfing(),
            'bullish_harami': self.detect_bullish_harami(),
            'bearish_harami': self.detect_bearish_harami(),
            'piercing_line': self.detect_piercing_line(),
            'dark_cloud_cover': self.detect_dark_cloud_cover(),
            'tweezer_bottom': self.detect_tweezer_bottom(),
            'tweezer_top': self.detect_tweezer_top(),

            # Triple candle patterns
            'morning_star': self.detect_morning_star(),
            'evening_star': self.detect_evening_star(),
            'three_white_soldiers': self.detect_three_white_soldiers(),
            'three_black_crows': self.detect_three_black_crows(),
            'three_inside_up': self.detect_three_inside_up(),
            'three_inside_down': self.detect_three_inside_down(),
            'three_outside_up': self.detect_three_outside_up(),
            'three_outside_down': self.detect_three_outside_down(),

            # Advanced patterns
            'abandoned_baby_bull': self.detect_abandoned_baby_bull(),
            'abandoned_baby_bear': self.detect_abandoned_baby_bear(),
            'rising_three_methods': self.detect_rising_three_methods(),
            'falling_three_methods': self.detect_falling_three_methods(),
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
            'signal_strength': min(signal_strength, 100),
            'detected_patterns': [name for name, data in patterns.items() if data.get('detected', False)]
        }

        return patterns

    # ==================== SINGLE CANDLE PATTERNS ====================

    def detect_doji(self):
        """
        Doji: Open = Close (indecision)

        Signal: NEUTRAL (reversal possible in trending market)
        Strength: Context-dependent
        """
        if len(self.df) < 5:
            return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

        last = self.df.iloc[-1]

        # Body is very small compared to range
        if last['total_range'] > 0:
            body_ratio = last['body'] / last['total_range']

            if body_ratio < 0.1:  # Body < 10% of range
                # Check trend context
                trend = self._get_trend(5)

                if trend == 'UPTREND':
                    return {
                        'detected': True,
                        'signal': 'BEARISH',  # Potential reversal
                        'strength': 60,
                        'pattern': 'Doji (after uptrend)'
                    }
                elif trend == 'DOWNTREND':
                    return {
                        'detected': True,
                        'signal': 'BULLISH',  # Potential reversal
                        'strength': 60,
                        'pattern': 'Doji (after downtrend)'
                    }
                else:
                    return {
                        'detected': True,
                        'signal': 'NEUTRAL',
                        'strength': 40,
                        'pattern': 'Doji (indecision)'
                    }

        return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

    def detect_hammer(self):
        """
        Hammer: Long lower shadow, small body at top (bullish reversal)

        Requirements:
        - Lower shadow >= 2x body
        - Upper shadow very small
        - Appears after downtrend
        """
        if len(self.df) < 5:
            return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

        last = self.df.iloc[-1]

        # Long lower shadow
        if last['body'] > 0 and last['lower_shadow'] >= 2 * last['body']:
            # Small upper shadow
            if last['upper_shadow'] <= last['body'] * 0.3:
                # After downtrend
                if self._get_trend(5) == 'DOWNTREND':
                    return {
                        'detected': True,
                        'signal': 'BULLISH',
                        'strength': 75,
                        'pattern': 'Hammer'
                    }

        return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

    def detect_inverted_hammer(self):
        """
        Inverted Hammer: Long upper shadow, small body at bottom

        Signal: BULLISH (if confirmed by next candle)
        """
        if len(self.df) < 5:
            return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

        last = self.df.iloc[-1]

        if last['body'] > 0 and last['upper_shadow'] >= 2 * last['body']:
            if last['lower_shadow'] <= last['body'] * 0.3:
                if self._get_trend(5) == 'DOWNTREND':
                    return {
                        'detected': True,
                        'signal': 'BULLISH',
                        'strength': 65,
                        'pattern': 'Inverted Hammer'
                    }

        return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

    def detect_hanging_man(self):
        """
        Hanging Man: Same as hammer but after uptrend (bearish)
        """
        if len(self.df) < 5:
            return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

        last = self.df.iloc[-1]

        if last['body'] > 0 and last['lower_shadow'] >= 2 * last['body']:
            if last['upper_shadow'] <= last['body'] * 0.3:
                if self._get_trend(5) == 'UPTREND':
                    return {
                        'detected': True,
                        'signal': 'BEARISH',
                        'strength': 75,
                        'pattern': 'Hanging Man'
                    }

        return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

    def detect_shooting_star(self):
        """
        Shooting Star: Long upper shadow, small body at bottom, after uptrend
        """
        if len(self.df) < 5:
            return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

        last = self.df.iloc[-1]

        if last['body'] > 0 and last['upper_shadow'] >= 2 * last['body']:
            if last['lower_shadow'] <= last['body'] * 0.3:
                if self._get_trend(5) == 'UPTREND':
                    return {
                        'detected': True,
                        'signal': 'BEARISH',
                        'strength': 75,
                        'pattern': 'Shooting Star'
                    }

        return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

    def detect_spinning_top(self):
        """
        Spinning Top: Small body with long shadows on both sides (indecision)
        """
        if len(self.df) < 5:
            return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

        last = self.df.iloc[-1]

        if last['total_range'] > 0:
            body_ratio = last['body'] / last['total_range']

            # Small body (<30% of range) with shadows on both sides
            if body_ratio < 0.3:
                if last['upper_shadow'] > last['body'] and last['lower_shadow'] > last['body']:
                    return {
                        'detected': True,
                        'signal': 'NEUTRAL',
                        'strength': 50,
                        'pattern': 'Spinning Top'
                    }

        return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

    def detect_marubozu_bullish(self):
        """
        Bullish Marubozu: No shadows, strong bullish candle
        """
        if len(self.df) < 2:
            return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

        last = self.df.iloc[-1]

        if last['is_bullish'] and last['body'] > self.avg_body * 1.5:
            # Very small shadows
            if last['upper_shadow'] < last['body'] * 0.1 and last['lower_shadow'] < last['body'] * 0.1:
                return {
                    'detected': True,
                    'signal': 'BULLISH',
                    'strength': 80,
                    'pattern': 'Bullish Marubozu'
                }

        return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

    def detect_marubozu_bearish(self):
        """
        Bearish Marubozu: No shadows, strong bearish candle
        """
        if len(self.df) < 2:
            return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

        last = self.df.iloc[-1]

        if last['is_bearish'] and last['body'] > self.avg_body * 1.5:
            if last['upper_shadow'] < last['body'] * 0.1 and last['lower_shadow'] < last['body'] * 0.1:
                return {
                    'detected': True,
                    'signal': 'BEARISH',
                    'strength': 80,
                    'pattern': 'Bearish Marubozu'
                }

        return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

    # ==================== DOUBLE CANDLE PATTERNS ====================

    def detect_bullish_engulfing(self):
        """
        Bullish Engulfing: Large bullish candle engulfs previous bearish candle
        """
        if len(self.df) < 2:
            return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

        prev = self.df.iloc[-2]
        last = self.df.iloc[-1]

        # Previous bearish, current bullish
        if prev['is_bearish'] and last['is_bullish']:
            # Current engulfs previous
            if last['Open'] < prev['Close'] and last['Close'] > prev['Open']:
                # After downtrend
                if self._get_trend(5) == 'DOWNTREND':
                    return {
                        'detected': True,
                        'signal': 'BULLISH',
                        'strength': 85,
                        'pattern': 'Bullish Engulfing'
                    }

        return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

    def detect_bearish_engulfing(self):
        """
        Bearish Engulfing: Large bearish candle engulfs previous bullish candle
        """
        if len(self.df) < 2:
            return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

        prev = self.df.iloc[-2]
        last = self.df.iloc[-1]

        if prev['is_bullish'] and last['is_bearish']:
            if last['Open'] > prev['Close'] and last['Close'] < prev['Open']:
                if self._get_trend(5) == 'UPTREND':
                    return {
                        'detected': True,
                        'signal': 'BEARISH',
                        'strength': 85,
                        'pattern': 'Bearish Engulfing'
                    }

        return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

    def detect_bullish_harami(self):
        """
        Bullish Harami: Small bullish candle inside previous large bearish candle
        """
        if len(self.df) < 2:
            return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

        prev = self.df.iloc[-2]
        last = self.df.iloc[-1]

        if prev['is_bearish'] and last['is_bullish']:
            # Current inside previous
            if last['Open'] > prev['Close'] and last['Close'] < prev['Open']:
                # Previous candle large
                if prev['body'] > self.avg_body * 1.2:
                    return {
                        'detected': True,
                        'signal': 'BULLISH',
                        'strength': 70,
                        'pattern': 'Bullish Harami'
                    }

        return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

    def detect_bearish_harami(self):
        """
        Bearish Harami: Small bearish candle inside previous large bullish candle
        """
        if len(self.df) < 2:
            return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

        prev = self.df.iloc[-2]
        last = self.df.iloc[-1]

        if prev['is_bullish'] and last['is_bearish']:
            if last['Open'] < prev['Close'] and last['Close'] > prev['Open']:
                if prev['body'] > self.avg_body * 1.2:
                    return {
                        'detected': True,
                        'signal': 'BEARISH',
                        'strength': 70,
                        'pattern': 'Bearish Harami'
                    }

        return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

    def detect_piercing_line(self):
        """
        Piercing Line: Bullish reversal - 2nd candle closes above 50% of 1st
        """
        if len(self.df) < 2:
            return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

        prev = self.df.iloc[-2]
        last = self.df.iloc[-1]

        if prev['is_bearish'] and last['is_bullish']:
            # Opens below previous close
            if last['Open'] < prev['Close']:
                # Closes above midpoint of previous body
                prev_mid = (prev['Open'] + prev['Close']) / 2
                if last['Close'] > prev_mid:
                    if self._get_trend(5) == 'DOWNTREND':
                        return {
                            'detected': True,
                            'signal': 'BULLISH',
                            'strength': 75,
                            'pattern': 'Piercing Line'
                        }

        return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

    def detect_dark_cloud_cover(self):
        """
        Dark Cloud Cover: Bearish reversal - 2nd candle closes below 50% of 1st
        """
        if len(self.df) < 2:
            return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

        prev = self.df.iloc[-2]
        last = self.df.iloc[-1]

        if prev['is_bullish'] and last['is_bearish']:
            if last['Open'] > prev['Close']:
                prev_mid = (prev['Open'] + prev['Close']) / 2
                if last['Close'] < prev_mid:
                    if self._get_trend(5) == 'UPTREND':
                        return {
                            'detected': True,
                            'signal': 'BEARISH',
                            'strength': 75,
                            'pattern': 'Dark Cloud Cover'
                        }

        return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

    def detect_tweezer_bottom(self):
        """
        Tweezer Bottom: Two candles with same low (support)
        """
        if len(self.df) < 2:
            return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

        prev = self.df.iloc[-2]
        last = self.df.iloc[-1]

        # Same lows (within 0.5%)
        if abs(prev['Low'] - last['Low']) / prev['Low'] < 0.005:
            if prev['is_bearish'] and last['is_bullish']:
                if self._get_trend(5) == 'DOWNTREND':
                    return {
                        'detected': True,
                        'signal': 'BULLISH',
                        'strength': 70,
                        'pattern': 'Tweezer Bottom'
                    }

        return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

    def detect_tweezer_top(self):
        """
        Tweezer Top: Two candles with same high (resistance)
        """
        if len(self.df) < 2:
            return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

        prev = self.df.iloc[-2]
        last = self.df.iloc[-1]

        # Same highs
        if abs(prev['High'] - last['High']) / prev['High'] < 0.005:
            if prev['is_bullish'] and last['is_bearish']:
                if self._get_trend(5) == 'UPTREND':
                    return {
                        'detected': True,
                        'signal': 'BEARISH',
                        'strength': 70,
                        'pattern': 'Tweezer Top'
                    }

        return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

    # ==================== TRIPLE CANDLE PATTERNS ====================

    def detect_morning_star(self):
        """
        Morning Star: 3-candle bullish reversal
        1. Large bearish
        2. Small (gap down)
        3. Large bullish
        """
        if len(self.df) < 3:
            return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

        c1 = self.df.iloc[-3]
        c2 = self.df.iloc[-2]
        c3 = self.df.iloc[-1]

        # C1: Large bearish
        if c1['is_bearish'] and c1['body'] > self.avg_body:
            # C2: Small body (star)
            if c2['body'] < self.avg_body * 0.5:
                # C3: Large bullish
                if c3['is_bullish'] and c3['body'] > self.avg_body:
                    # C3 closes above midpoint of C1
                    c1_mid = (c1['Open'] + c1['Close']) / 2
                    if c3['Close'] > c1_mid:
                        if self._get_trend(5) == 'DOWNTREND':
                            return {
                                'detected': True,
                                'signal': 'BULLISH',
                                'strength': 90,
                                'pattern': 'Morning Star'
                            }

        return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

    def detect_evening_star(self):
        """
        Evening Star: 3-candle bearish reversal
        """
        if len(self.df) < 3:
            return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

        c1 = self.df.iloc[-3]
        c2 = self.df.iloc[-2]
        c3 = self.df.iloc[-1]

        if c1['is_bullish'] and c1['body'] > self.avg_body:
            if c2['body'] < self.avg_body * 0.5:
                if c3['is_bearish'] and c3['body'] > self.avg_body:
                    c1_mid = (c1['Open'] + c1['Close']) / 2
                    if c3['Close'] < c1_mid:
                        if self._get_trend(5) == 'UPTREND':
                            return {
                                'detected': True,
                                'signal': 'BEARISH',
                                'strength': 90,
                                'pattern': 'Evening Star'
                            }

        return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

    def detect_three_white_soldiers(self):
        """
        Three White Soldiers: 3 consecutive large bullish candles
        """
        if len(self.df) < 3:
            return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

        c1 = self.df.iloc[-3]
        c2 = self.df.iloc[-2]
        c3 = self.df.iloc[-1]

        # All bullish
        if c1['is_bullish'] and c2['is_bullish'] and c3['is_bullish']:
            # All large bodies
            if all(c['body'] > self.avg_body for c in [c1, c2, c3]):
                # Each opens within previous body, closes higher
                if c2['Open'] > c1['Open'] and c2['Open'] < c1['Close']:
                    if c3['Open'] > c2['Open'] and c3['Open'] < c2['Close']:
                        if c2['Close'] > c1['Close'] and c3['Close'] > c2['Close']:
                            return {
                                'detected': True,
                                'signal': 'BULLISH',
                                'strength': 85,
                                'pattern': 'Three White Soldiers'
                            }

        return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

    def detect_three_black_crows(self):
        """
        Three Black Crows: 3 consecutive large bearish candles
        """
        if len(self.df) < 3:
            return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

        c1 = self.df.iloc[-3]
        c2 = self.df.iloc[-2]
        c3 = self.df.iloc[-1]

        if c1['is_bearish'] and c2['is_bearish'] and c3['is_bearish']:
            if all(c['body'] > self.avg_body for c in [c1, c2, c3]):
                if c2['Open'] < c1['Open'] and c2['Open'] > c1['Close']:
                    if c3['Open'] < c2['Open'] and c3['Open'] > c2['Close']:
                        if c2['Close'] < c1['Close'] and c3['Close'] < c2['Close']:
                            return {
                                'detected': True,
                                'signal': 'BEARISH',
                                'strength': 85,
                                'pattern': 'Three Black Crows'
                            }

        return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

    def detect_three_inside_up(self):
        """
        Three Inside Up: Bullish harami followed by confirmation
        """
        if len(self.df) < 3:
            return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

        c1 = self.df.iloc[-3]
        c2 = self.df.iloc[-2]
        c3 = self.df.iloc[-1]

        # Harami pattern (c1, c2)
        if c1['is_bearish'] and c2['is_bullish']:
            if c2['Open'] > c1['Close'] and c2['Close'] < c1['Open']:
                # Confirmation: c3 closes above c1 open
                if c3['is_bullish'] and c3['Close'] > c1['Open']:
                    return {
                        'detected': True,
                        'signal': 'BULLISH',
                        'strength': 80,
                        'pattern': 'Three Inside Up'
                    }

        return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

    def detect_three_inside_down(self):
        """
        Three Inside Down: Bearish harami followed by confirmation
        """
        if len(self.df) < 3:
            return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

        c1 = self.df.iloc[-3]
        c2 = self.df.iloc[-2]
        c3 = self.df.iloc[-1]

        if c1['is_bullish'] and c2['is_bearish']:
            if c2['Open'] < c1['Close'] and c2['Close'] > c1['Open']:
                if c3['is_bearish'] and c3['Close'] < c1['Open']:
                    return {
                        'detected': True,
                        'signal': 'BEARISH',
                        'strength': 80,
                        'pattern': 'Three Inside Down'
                    }

        return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

    def detect_three_outside_up(self):
        """
        Three Outside Up: Bullish engulfing followed by confirmation
        """
        if len(self.df) < 3:
            return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

        c1 = self.df.iloc[-3]
        c2 = self.df.iloc[-2]
        c3 = self.df.iloc[-1]

        # Engulfing (c1, c2)
        if c1['is_bearish'] and c2['is_bullish']:
            if c2['Open'] < c1['Close'] and c2['Close'] > c1['Open']:
                # Confirmation
                if c3['is_bullish'] and c3['Close'] > c2['Close']:
                    return {
                        'detected': True,
                        'signal': 'BULLISH',
                        'strength': 85,
                        'pattern': 'Three Outside Up'
                    }

        return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

    def detect_three_outside_down(self):
        """
        Three Outside Down: Bearish engulfing followed by confirmation
        """
        if len(self.df) < 3:
            return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

        c1 = self.df.iloc[-3]
        c2 = self.df.iloc[-2]
        c3 = self.df.iloc[-1]

        if c1['is_bullish'] and c2['is_bearish']:
            if c2['Open'] > c1['Close'] and c2['Close'] < c1['Open']:
                if c3['is_bearish'] and c3['Close'] < c2['Close']:
                    return {
                        'detected': True,
                        'signal': 'BEARISH',
                        'strength': 85,
                        'pattern': 'Three Outside Down'
                    }

        return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

    # ==================== ADVANCED PATTERNS ====================

    def detect_abandoned_baby_bull(self):
        """
        Abandoned Baby (Bullish): Rare reversal with gaps
        """
        if len(self.df) < 3:
            return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

        c1 = self.df.iloc[-3]
        c2 = self.df.iloc[-2]
        c3 = self.df.iloc[-1]

        # C2 gaps away from both C1 and C3
        if c2['High'] < c1['Low'] and c2['High'] < c3['Low']:
            if c1['is_bearish'] and c3['is_bullish']:
                return {
                    'detected': True,
                    'signal': 'BULLISH',
                    'strength': 95,
                    'pattern': 'Abandoned Baby (Bullish)'
                }

        return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

    def detect_abandoned_baby_bear(self):
        """
        Abandoned Baby (Bearish): Rare reversal with gaps
        """
        if len(self.df) < 3:
            return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

        c1 = self.df.iloc[-3]
        c2 = self.df.iloc[-2]
        c3 = self.df.iloc[-1]

        if c2['Low'] > c1['High'] and c2['Low'] > c3['High']:
            if c1['is_bullish'] and c3['is_bearish']:
                return {
                    'detected': True,
                    'signal': 'BEARISH',
                    'strength': 95,
                    'pattern': 'Abandoned Baby (Bearish)'
                }

        return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

    def detect_rising_three_methods(self):
        """
        Rising Three Methods: Bullish continuation pattern (5 candles)
        """
        if len(self.df) < 5:
            return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

        c1 = self.df.iloc[-5]
        c2 = self.df.iloc[-4]
        c3 = self.df.iloc[-3]
        c4 = self.df.iloc[-2]
        c5 = self.df.iloc[-1]

        # C1: Large bullish
        if c1['is_bullish'] and c1['body'] > self.avg_body:
            # C2-C4: Small bearish (consolidation)
            if all(c['is_bearish'] and c['body'] < self.avg_body for c in [c2, c3, c4]):
                # C2-C4 stay within C1 range
                if all(c['High'] < c1['Close'] and c['Low'] > c1['Open'] for c in [c2, c3, c4]):
                    # C5: Bullish closes above C1
                    if c5['is_bullish'] and c5['Close'] > c1['Close']:
                        return {
                            'detected': True,
                            'signal': 'BULLISH',
                            'strength': 75,
                            'pattern': 'Rising Three Methods'
                        }

        return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

    def detect_falling_three_methods(self):
        """
        Falling Three Methods: Bearish continuation pattern (5 candles)
        """
        if len(self.df) < 5:
            return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

        c1 = self.df.iloc[-5]
        c2 = self.df.iloc[-4]
        c3 = self.df.iloc[-3]
        c4 = self.df.iloc[-2]
        c5 = self.df.iloc[-1]

        if c1['is_bearish'] and c1['body'] > self.avg_body:
            if all(c['is_bullish'] and c['body'] < self.avg_body for c in [c2, c3, c4]):
                if all(c['Low'] > c1['Close'] and c['High'] < c1['Open'] for c in [c2, c3, c4]):
                    if c5['is_bearish'] and c5['Close'] < c1['Close']:
                        return {
                            'detected': True,
                            'signal': 'BEARISH',
                            'strength': 75,
                            'pattern': 'Falling Three Methods'
                        }

        return {'detected': False, 'signal': 'NEUTRAL', 'strength': 0}

    # ==================== HELPER FUNCTIONS ====================

    def _get_trend(self, periods=5):
        """
        Determine trend over last N periods

        Returns:
            str: 'UPTREND', 'DOWNTREND', or 'SIDEWAYS'
        """
        if len(self.df) < periods:
            return 'SIDEWAYS'

        recent = self.df.tail(periods)
        closes = recent['Close'].values

        # Linear regression
        x = np.arange(len(closes))
        slope, _ = np.polyfit(x, closes, 1)

        # Threshold: 1% change over period
        threshold = closes[0] * 0.01 / periods

        if slope > threshold:
            return 'UPTREND'
        elif slope < -threshold:
            return 'DOWNTREND'
        else:
            return 'SIDEWAYS'


def get_candlestick_patterns(df):
    """
    Convenience function to get all candlestick patterns

    Args:
        df: OHLCV DataFrame

    Returns:
        dict: All detected patterns
    """
    detector = CandlestickPatternDetector(df)
    return detector.detect_all_patterns()

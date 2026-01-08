"""
Bandar Pattern Detector
Detects market maker / bandar patterns in Indonesian stocks
Specialized for IDX market behavior
"""
import pandas as pd
import numpy as np


class BandarDetector:
    """Detect bandar (market maker) patterns"""

    def __init__(self):
        self.detection_results = {}

    def detect_accumulation(self, df):
        """
        Detect accumulation phase - bandar buying quietly

        Signs:
        - Price stable or slightly down
        - Volume increasing (above average)
        - OBV rising while price flat
        - Support level forming
        - Bollinger Bands narrowing

        Returns:
            dict with accumulation analysis
        """
        if len(df) < 30:
            return {'detected': False, 'confidence': 0.0, 'reasons': []}

        latest = df.iloc[-1]
        last_20 = df.tail(20)

        score = 0
        reasons = []
        signals = []

        # 1. Price movement check - flat or slightly negative
        price_change_20d = ((latest['close'] - df.iloc[-20]['close']) / df.iloc[-20]['close']) * 100

        if -5 < price_change_20d < 2:
            score += 25
            reasons.append(f"✅ Harga relatif stabil ({price_change_20d:+.1f}%) - karakteristik akumulasi")
            signals.append("Price Stability")
        elif price_change_20d < -10:
            score += 10
            reasons.append(f"⚠️ Harga turun {price_change_20d:.1f}% - mungkin akumulasi di level lebih rendah")

        # 2. Volume analysis - increasing volume
        avg_volume = df['volume'].tail(50).mean()
        recent_volume = last_20['volume'].mean()
        volume_ratio = recent_volume / avg_volume

        if volume_ratio > 1.3:
            score += 30
            reasons.append(f"✅ Volume meningkat {volume_ratio:.1f}x dari average - ada akumulasi besar")
            signals.append("High Volume")
        elif volume_ratio > 1.1:
            score += 15
            reasons.append(f"🟡 Volume sedikit naik ({volume_ratio:.1f}x) - akumulasi moderat")

        # 3. OBV vs Price divergence - OBV naik, price flat/turun
        if 'obv' in df.columns:
            obv_change = ((latest['obv'] - df.iloc[-20]['obv']) / abs(df.iloc[-20]['obv'])) * 100

            if obv_change > 10 and price_change_20d < 5:
                score += 35
                reasons.append(f"✅✅ BULLISH DIVERGENCE! OBV naik {obv_change:.1f}% tapi harga hanya {price_change_20d:+.1f}% - STRONG ACCUMULATION")
                signals.append("OBV Divergence")
            elif obv_change > 5 and price_change_20d < 3:
                score += 20
                reasons.append(f"✅ OBV naik {obv_change:.1f}%, harga stabil - ada buying pressure tersembunyi")

        # 4. Bollinger Bands compression - volatility turun
        if 'bb_width' in df.columns:
            avg_bb_width = df['bb_width'].tail(50).mean()
            current_bb_width = latest['bb_width']

            if current_bb_width < avg_bb_width * 0.7:
                score += 20
                reasons.append(f"✅ BB Width menyempit ({current_bb_width:.3f}) - konsolidasi sebelum breakout")
                signals.append("BB Compression")

        # 5. Support level forming - multiple touches at similar price
        low_prices = last_20['low']
        price_range = latest['close'] * 0.02  # 2% range

        support_touches = 0
        min_price = low_prices.min()

        for price in low_prices:
            if abs(price - min_price) < price_range:
                support_touches += 1

        if support_touches >= 3:
            score += 15
            reasons.append(f"✅ Support level terbentuk di Rp {min_price:,.0f} ({support_touches} touches)")
            signals.append("Support Formation")

        # 6. Volume distribution - check if volume concentrated at certain price
        if len(last_20) > 0:
            volume_volatility = last_20['volume'].std() / last_20['volume'].mean()

            if volume_volatility > 0.5:
                score += 10
                reasons.append(f"🟡 Volume tidak merata - bisa jadi bandar sedang akumulasi bertahap")

        # Determine confidence
        confidence = min(score, 100)

        detected = confidence >= 50

        pattern_strength = "VERY STRONG" if confidence >= 80 else "STRONG" if confidence >= 65 else "MODERATE" if confidence >= 50 else "WEAK"

        return {
            'detected': detected,
            'confidence': confidence,
            'strength': pattern_strength,
            'reasons': reasons,
            'signals': signals,
            'score': score,
            'recommendation': self._get_accumulation_recommendation(confidence, price_change_20d)
        }

    def detect_markup(self, df):
        """
        Detect markup phase - bandar pumping price

        Signs:
        - Price rising consistently
        - Volume increasing
        - Higher highs and higher lows
        - Breaking resistance levels
        - Strong momentum indicators

        Returns:
            dict with markup analysis
        """
        if len(df) < 20:
            return {'detected': False, 'confidence': 0.0, 'reasons': []}

        latest = df.iloc[-1]
        last_10 = df.tail(10)
        last_20 = df.tail(20)

        score = 0
        reasons = []
        signals = []

        # 1. Price momentum - strong uptrend
        price_change_10d = ((latest['close'] - df.iloc[-10]['close']) / df.iloc[-10]['close']) * 100
        price_change_20d = ((latest['close'] - df.iloc[-20]['close']) / df.iloc[-20]['close']) * 100

        if price_change_10d > 10:
            score += 35
            reasons.append(f"✅✅ Harga naik {price_change_10d:.1f}% dalam 10 hari - STRONG MARKUP!")
            signals.append("Strong Momentum")
        elif price_change_10d > 5:
            score += 25
            reasons.append(f"✅ Harga naik {price_change_10d:.1f}% - markup phase aktif")

        # 2. Volume surge
        avg_volume = df['volume'].tail(50).mean()
        recent_volume = last_10['volume'].mean()
        volume_ratio = recent_volume / avg_volume

        if volume_ratio > 2.0:
            score += 30
            reasons.append(f"✅✅ Volume SPIKE {volume_ratio:.1f}x - buying frenzy!")
            signals.append("Volume Surge")
        elif volume_ratio > 1.5:
            score += 20
            reasons.append(f"✅ Volume naik {volume_ratio:.1f}x - strong interest")

        # 3. Higher highs and higher lows
        highs = last_10['high'].values
        lows = last_10['low'].values

        higher_highs = sum(1 for i in range(1, len(highs)) if highs[i] > highs[i-1])
        higher_lows = sum(1 for i in range(1, len(lows)) if lows[i] > lows[i-1])

        if higher_highs >= 6 and higher_lows >= 6:
            score += 25
            reasons.append(f"✅ Consistent higher highs & higher lows - perfect uptrend")
            signals.append("Higher H/L")
        elif higher_highs >= 4 and higher_lows >= 4:
            score += 15
            reasons.append(f"🟡 Trend naik terbentuk ({higher_highs} HH, {higher_lows} HL)")

        # 4. RSI momentum
        if 'rsi' in df.columns and pd.notna(latest['rsi']):
            rsi = latest['rsi']

            if 60 < rsi < 80:
                score += 20
                reasons.append(f"✅ RSI {rsi:.1f} - momentum kuat tapi belum overbought")
                signals.append("Strong RSI")
            elif rsi > 80:
                score += 10
                reasons.append(f"⚠️ RSI {rsi:.1f} - sangat overbought, waspadai peak")

        # 5. Break above MA
        if 'sma_20' in df.columns and pd.notna(latest['sma_20']):
            if latest['close'] > latest['sma_20'] * 1.05:
                score += 15
                reasons.append(f"✅ Harga 5%+ di atas SMA20 - strong momentum")
                signals.append("Above MA")

        # 6. MACD momentum
        if 'macd' in df.columns and 'macd_signal' in df.columns:
            if pd.notna(latest['macd']) and pd.notna(latest['macd_signal']):
                if latest['macd'] > latest['macd_signal'] and latest['macd'] > 0:
                    score += 15
                    reasons.append(f"✅ MACD bullish dan positif - trend continuation")
                    signals.append("MACD Bullish")

        confidence = min(score, 100)
        detected = confidence >= 50

        pattern_strength = "VERY STRONG" if confidence >= 80 else "STRONG" if confidence >= 65 else "MODERATE" if confidence >= 50 else "WEAK"

        return {
            'detected': detected,
            'confidence': confidence,
            'strength': pattern_strength,
            'reasons': reasons,
            'signals': signals,
            'score': score,
            'price_momentum': price_change_10d,
            'recommendation': self._get_markup_recommendation(confidence, price_change_10d, latest.get('rsi', 50))
        }

    def detect_distribution(self, df):
        """
        Detect distribution phase - bandar selling/dumping

        Signs:
        - Price topping out or starting to decline
        - Volume high but price not rising
        - Lower highs and lower lows forming
        - OBV divergence (OBV down, price flat)
        - Resistance rejection

        Returns:
            dict with distribution analysis
        """
        if len(df) < 20:
            return {'detected': False, 'confidence': 0.0, 'reasons': []}

        latest = df.iloc[-1]
        last_10 = df.tail(10)
        last_20 = df.tail(20)

        score = 0
        reasons = []
        signals = []

        # 1. Price topping - flat or starting to decline
        price_change_10d = ((latest['close'] - df.iloc[-10]['close']) / df.iloc[-10]['close']) * 100
        price_change_20d = ((latest['close'] - df.iloc[-20]['close']) / df.iloc[-20]['close']) * 100

        if -5 < price_change_10d < 2 and price_change_20d > 5:
            score += 30
            reasons.append(f"✅ Harga mulai flat ({price_change_10d:+.1f}%) setelah naik {price_change_20d:.1f}% - possible topping")
            signals.append("Price Topping")
        elif price_change_10d < -5:
            score += 25
            reasons.append(f"✅ Harga turun {price_change_10d:.1f}% - distribution aktif")

        # 2. Volume high but price not responding
        avg_volume = df['volume'].tail(50).mean()
        recent_volume = last_10['volume'].mean()
        volume_ratio = recent_volume / avg_volume

        if volume_ratio > 1.3 and -3 < price_change_10d < 3:
            score += 35
            reasons.append(f"✅✅ Volume tinggi ({volume_ratio:.1f}x) tapi harga stagnan - DISTRIBUSI BESAR!")
            signals.append("High Volume No Follow")
        elif volume_ratio > 1.5 and price_change_10d < 0:
            score += 30
            reasons.append(f"✅ Volume tinggi dengan harga turun - panic selling atau distribution")

        # 3. OBV vs Price divergence - OBV turun, price flat/naik
        if 'obv' in df.columns:
            obv_change = ((latest['obv'] - df.iloc[-20]['obv']) / abs(df.iloc[-20]['obv'])) * 100

            if obv_change < -10 and price_change_20d > -5:
                score += 35
                reasons.append(f"✅✅ BEARISH DIVERGENCE! OBV turun {obv_change:.1f}% tapi harga masih {price_change_20d:+.1f}% - DISTRIBUTION")
                signals.append("OBV Divergence")
            elif obv_change < -5 and price_change_20d > 0:
                score += 25
                reasons.append(f"✅ OBV turun {obv_change:.1f}% sementara harga naik - selling pressure tersembunyi")

        # 4. Lower highs and lower lows
        highs = last_10['high'].values
        lows = last_10['low'].values

        lower_highs = sum(1 for i in range(1, len(highs)) if highs[i] < highs[i-1])
        lower_lows = sum(1 for i in range(1, len(lows)) if lows[i] < lows[i-1])

        if lower_highs >= 5 and lower_lows >= 5:
            score += 25
            reasons.append(f"✅ Lower highs & lower lows terbentuk - downtrend confirmed")
            signals.append("Lower H/L")

        # 5. RSI divergence or overbought
        if 'rsi' in df.columns and pd.notna(latest['rsi']):
            rsi = latest['rsi']
            prev_rsi = df.iloc[-10]['rsi'] if pd.notna(df.iloc[-10]['rsi']) else 50

            if rsi > 70 and rsi < prev_rsi and price_change_10d > 0:
                score += 25
                reasons.append(f"✅ RSI divergence - RSI turun dari {prev_rsi:.1f} ke {rsi:.1f} tapi harga naik")
                signals.append("RSI Divergence")
            elif rsi > 75:
                score += 15
                reasons.append(f"⚠️ RSI very overbought ({rsi:.1f}) - risiko distribusi tinggi")

        confidence = min(score, 100)
        detected = confidence >= 50

        pattern_strength = "VERY STRONG" if confidence >= 80 else "STRONG" if confidence >= 65 else "MODERATE" if confidence >= 50 else "WEAK"

        return {
            'detected': detected,
            'confidence': confidence,
            'strength': pattern_strength,
            'reasons': reasons,
            'signals': signals,
            'score': score,
            'recommendation': self._get_distribution_recommendation(confidence)
        }

    def analyze_full(self, df):
        """
        Complete bandar pattern analysis

        Returns:
            dict with all pattern detections
        """
        accumulation = self.detect_accumulation(df)
        markup = self.detect_markup(df)
        distribution = self.detect_distribution(df)

        # Determine dominant phase
        scores = {
            'ACCUMULATION': accumulation['confidence'],
            'MARKUP': markup['confidence'],
            'DISTRIBUTION': distribution['confidence']
        }

        dominant_phase = max(scores, key=scores.get)
        dominant_confidence = scores[dominant_phase]

        if dominant_confidence < 40:
            dominant_phase = "UNKNOWN"
            phase_description = "Tidak ada pola bandar yang jelas terdeteksi"
        elif dominant_phase == "ACCUMULATION":
            phase_description = "🟢 Bandar sedang mengumpulkan saham (ACCUMULATION) - Pertimbangkan masuk bertahap"
        elif dominant_phase == "MARKUP":
            phase_description = "🔥 Bandar sedang pump harga (MARKUP) - Ride the trend, tapi waspadai peak"
        elif dominant_phase == "DISTRIBUTION":
            phase_description = "🔴 Bandar sedang jual/dump (DISTRIBUTION) - HATI-HATI, pertimbangkan keluar"
        else:
            phase_description = "Unknown phase"

        return {
            'accumulation': accumulation,
            'markup': markup,
            'distribution': distribution,
            'dominant_phase': dominant_phase,
            'dominant_confidence': dominant_confidence,
            'phase_description': phase_description,
            'all_scores': scores
        }

    def _get_accumulation_recommendation(self, confidence, price_change):
        """Get trading recommendation for accumulation phase"""
        if confidence >= 70:
            if price_change < 0:
                return "🟢 STRONG BUY - Akumulasi kuat terdeteksi dengan harga turun. Peluang entry bagus!"
            else:
                return "🟢 BUY - Akumulasi terdeteksi. Entry sekarang atau tunggu pullback."
        elif confidence >= 50:
            return "🟡 CONSIDER BUY - Ada indikasi akumulasi. Monitor lebih lanjut."
        else:
            return "⚪ WAIT - Pola akumulasi belum jelas."

    def _get_markup_recommendation(self, confidence, price_momentum, rsi):
        """Get trading recommendation for markup phase"""
        if confidence >= 70:
            if rsi > 75:
                return "⚠️ CAUTION - Markup strong tapi RSI overbought. Jangan FOMO, waspadai reversal!"
            elif price_momentum > 15:
                return "🔥 RIDE THE TREND - Markup sangat kuat! Set trailing stop, let profit run."
            else:
                return "🟢 JOIN MOMENTUM - Markup terdeteksi. Entry dengan stop loss ketat."
        elif confidence >= 50:
            return "🟡 MODERATE BUY - Ada momentum, tapi jaga risk management."
        else:
            return "⚪ WAIT - Momentum belum kuat."

    def _get_distribution_recommendation(self, confidence):
        """Get trading recommendation for distribution phase"""
        if confidence >= 70:
            return "🔴 STRONG SELL / EXIT - Distribusi kuat terdeteksi. Protect profit atau cut loss!"
        elif confidence >= 50:
            return "🟡 REDUCE POSITION - Ada indikasi distribusi. Kurangi exposure."
        else:
            return "⚪ MONITOR - Belum ada sinyal distribusi jelas."


# Singleton instance
_bandar_detector = None

def get_bandar_detector():
    """Get or create BandarDetector instance"""
    global _bandar_detector
    if _bandar_detector is None:
        _bandar_detector = BandarDetector()
    return _bandar_detector

"""
Stock Movement Analyzer
Analyzes WHY stocks move up or down based on technical indicators
"""
import pandas as pd
import numpy as np


class StockMovementAnalyzer:
    """Analyze stock movements and provide explanations"""

    def __init__(self):
        self.analysis_results = {}

    def analyze_trend(self, df):
        """Analyze trend indicators"""
        latest = df.iloc[-1]

        reasons = []
        score = 0  # -100 to +100

        # SMA Analysis
        if latest['close'] > latest['sma_50']:
            reasons.append({
                'indicator': 'SMA 50',
                'signal': 'BULLISH',
                'strength': 'Strong',
                'explanation': f"Harga (Rp {latest['close']:,.0f}) berada di ATAS SMA-50 (Rp {latest['sma_50']:,.0f}), menunjukkan trend naik jangka menengah"
            })
            score += 20
        else:
            reasons.append({
                'indicator': 'SMA 50',
                'signal': 'BEARISH',
                'strength': 'Strong',
                'explanation': f"Harga (Rp {latest['close']:,.0f}) berada di BAWAH SMA-50 (Rp {latest['sma_50']:,.0f}), menunjukkan trend turun jangka menengah"
            })
            score -= 20

        # Short term trend
        if latest['close'] > latest['sma_20']:
            reasons.append({
                'indicator': 'SMA 20',
                'signal': 'BULLISH',
                'strength': 'Medium',
                'explanation': f"Harga di atas SMA-20 (Rp {latest['sma_20']:,.0f}), trend jangka pendek positif"
            })
            score += 15
        else:
            reasons.append({
                'indicator': 'SMA 20',
                'signal': 'BEARISH',
                'strength': 'Medium',
                'explanation': f"Harga di bawah SMA-20 (Rp {latest['sma_20']:,.0f}), trend jangka pendek negatif"
            })
            score -= 15

        # Golden/Death Cross
        if latest['sma_20'] > latest['sma_50']:
            if df.iloc[-2]['sma_20'] <= df.iloc[-2]['sma_50']:
                reasons.append({
                    'indicator': 'Golden Cross',
                    'signal': 'BULLISH',
                    'strength': 'Very Strong',
                    'explanation': "GOLDEN CROSS terdeteksi! SMA-20 baru saja memotong SMA-50 ke atas - sinyal beli kuat"
                })
                score += 30
        elif latest['sma_20'] < latest['sma_50']:
            if df.iloc[-2]['sma_20'] >= df.iloc[-2]['sma_50']:
                reasons.append({
                    'indicator': 'Death Cross',
                    'signal': 'BEARISH',
                    'strength': 'Very Strong',
                    'explanation': "DEATH CROSS terdeteksi! SMA-20 baru saja memotong SMA-50 ke bawah - sinyal jual kuat"
                })
                score -= 30

        return reasons, score

    def analyze_momentum(self, df):
        """Analyze momentum indicators"""
        latest = df.iloc[-1]
        prev = df.iloc[-2]

        reasons = []
        score = 0

        # RSI Analysis
        rsi = latest['rsi']
        if rsi > 70:
            reasons.append({
                'indicator': 'RSI',
                'signal': 'OVERBOUGHT',
                'strength': 'Strong',
                'explanation': f"RSI = {rsi:.1f} (>70) menunjukkan kondisi OVERBOUGHT - saham sudah terlalu mahal, potensi koreksi"
            })
            score -= 15
        elif rsi < 30:
            reasons.append({
                'indicator': 'RSI',
                'signal': 'OVERSOLD',
                'strength': 'Strong',
                'explanation': f"RSI = {rsi:.1f} (<30) menunjukkan kondisi OVERSOLD - saham sudah terlalu murah, potensi rebound"
            })
            score += 15
        elif 40 <= rsi <= 60:
            reasons.append({
                'indicator': 'RSI',
                'signal': 'NEUTRAL',
                'strength': 'Medium',
                'explanation': f"RSI = {rsi:.1f} berada di zona netral, belum ada sinyal overbought/oversold"
            })
        elif rsi > 50:
            reasons.append({
                'indicator': 'RSI',
                'signal': 'BULLISH',
                'strength': 'Medium',
                'explanation': f"RSI = {rsi:.1f} di atas 50, momentum positif namun masih wajar"
            })
            score += 10
        else:
            reasons.append({
                'indicator': 'RSI',
                'signal': 'BEARISH',
                'strength': 'Medium',
                'explanation': f"RSI = {rsi:.1f} di bawah 50, momentum negatif"
            })
            score -= 10

        # MACD Analysis
        if latest['macd'] > latest['macd_signal']:
            if prev['macd'] <= prev['macd_signal']:
                reasons.append({
                    'indicator': 'MACD',
                    'signal': 'BULLISH',
                    'strength': 'Very Strong',
                    'explanation': "MACD BULLISH CROSSOVER! MACD line baru memotong signal line ke atas - momentum beli kuat"
                })
                score += 25
            else:
                reasons.append({
                    'indicator': 'MACD',
                    'signal': 'BULLISH',
                    'strength': 'Medium',
                    'explanation': f"MACD ({latest['macd']:.2f}) di atas Signal ({latest['macd_signal']:.2f}) - momentum positif"
                })
                score += 12
        else:
            if prev['macd'] >= prev['macd_signal']:
                reasons.append({
                    'indicator': 'MACD',
                    'signal': 'BEARISH',
                    'strength': 'Very Strong',
                    'explanation': "MACD BEARISH CROSSOVER! MACD line baru memotong signal line ke bawah - momentum jual kuat"
                })
                score -= 25
            else:
                reasons.append({
                    'indicator': 'MACD',
                    'signal': 'BEARISH',
                    'strength': 'Medium',
                    'explanation': f"MACD ({latest['macd']:.2f}) di bawah Signal ({latest['macd_signal']:.2f}) - momentum negatif"
                })
                score -= 12

        # Stochastic Analysis
        stoch_k = latest['stoch_k']
        if stoch_k > 80:
            reasons.append({
                'indicator': 'Stochastic',
                'signal': 'OVERBOUGHT',
                'strength': 'Medium',
                'explanation': f"Stochastic = {stoch_k:.1f} (>80) menunjukkan overbought jangka pendek"
            })
            score -= 8
        elif stoch_k < 20:
            reasons.append({
                'indicator': 'Stochastic',
                'signal': 'OVERSOLD',
                'strength': 'Medium',
                'explanation': f"Stochastic = {stoch_k:.1f} (<20) menunjukkan oversold jangka pendek"
            })
            score += 8

        return reasons, score

    def analyze_volatility(self, df):
        """Analyze volatility indicators"""
        latest = df.iloc[-1]

        reasons = []
        score = 0

        # Bollinger Bands
        price = latest['close']
        bb_upper = latest['bb_upper']
        bb_lower = latest['bb_lower']
        bb_middle = latest['bb_middle']

        if price >= bb_upper:
            reasons.append({
                'indicator': 'Bollinger Bands',
                'signal': 'OVERBOUGHT',
                'strength': 'Strong',
                'explanation': f"Harga menyentuh/melewati BB Upper (Rp {bb_upper:,.0f}) - kemungkinan akan turun kembali ke tengah"
            })
            score -= 12
        elif price <= bb_lower:
            reasons.append({
                'indicator': 'Bollinger Bands',
                'signal': 'OVERSOLD',
                'strength': 'Strong',
                'explanation': f"Harga menyentuh/melewati BB Lower (Rp {bb_lower:,.0f}) - kemungkinan akan naik kembali ke tengah"
            })
            score += 12
        elif price > bb_middle:
            reasons.append({
                'indicator': 'Bollinger Bands',
                'signal': 'BULLISH',
                'strength': 'Medium',
                'explanation': f"Harga di atas BB Middle (Rp {bb_middle:,.0f}) - berada di zona bullish"
            })
            score += 5
        else:
            reasons.append({
                'indicator': 'Bollinger Bands',
                'signal': 'BEARISH',
                'strength': 'Medium',
                'explanation': f"Harga di bawah BB Middle (Rp {bb_middle:,.0f}) - berada di zona bearish"
            })
            score -= 5

        # BB Width Analysis
        bb_width = latest['bb_width']
        avg_bb_width = df['bb_width'].tail(20).mean()

        if bb_width < avg_bb_width * 0.7:
            reasons.append({
                'indicator': 'BB Width',
                'signal': 'CONSOLIDATION',
                'strength': 'Medium',
                'explanation': f"BB Width sempit ({bb_width:.3f}) - saham sedang konsolidasi, akan ada pergerakan besar segera"
            })
        elif bb_width > avg_bb_width * 1.5:
            reasons.append({
                'indicator': 'BB Width',
                'signal': 'HIGH VOLATILITY',
                'strength': 'Medium',
                'explanation': f"BB Width lebar ({bb_width:.3f}) - volatilitas tinggi, trading lebih berisiko"
            })

        # ATR Analysis
        atr = latest['atr']
        avg_atr = df['atr'].tail(20).mean()
        atr_change = ((atr - avg_atr) / avg_atr) * 100

        if atr_change > 20:
            reasons.append({
                'indicator': 'ATR',
                'signal': 'VOLATILITY SPIKE',
                'strength': 'Medium',
                'explanation': f"ATR naik {atr_change:.1f}% - volatilitas meningkat, waspadai pergerakan besar"
            })

        return reasons, score

    def analyze_volume(self, df):
        """Analyze volume patterns"""
        latest = df.iloc[-1]
        prev = df.iloc[-2]

        reasons = []
        score = 0

        volume = latest['volume']
        volume_sma = latest['volume_sma']
        volume_ratio = latest['volume_ratio']

        # Volume spike analysis
        if volume_ratio > 2.0:
            price_change = ((latest['close'] - prev['close']) / prev['close']) * 100

            if price_change > 0:
                reasons.append({
                    'indicator': 'Volume',
                    'signal': 'BULLISH',
                    'strength': 'Very Strong',
                    'explanation': f"Volume SPIKE {volume_ratio:.1f}x dengan harga naik {price_change:.1f}% - buying pressure sangat kuat!"
                })
                score += 20
            else:
                reasons.append({
                    'indicator': 'Volume',
                    'signal': 'BEARISH',
                    'strength': 'Very Strong',
                    'explanation': f"Volume SPIKE {volume_ratio:.1f}x dengan harga turun {price_change:.1f}% - selling pressure sangat kuat!"
                })
                score -= 20
        elif volume_ratio > 1.5:
            reasons.append({
                'indicator': 'Volume',
                'signal': 'ACTIVE',
                'strength': 'Medium',
                'explanation': f"Volume {volume_ratio:.1f}x di atas rata-rata - minat trading meningkat"
            })
            score += 8
        elif volume_ratio < 0.5:
            reasons.append({
                'indicator': 'Volume',
                'signal': 'LOW ACTIVITY',
                'strength': 'Medium',
                'explanation': f"Volume rendah ({volume_ratio:.1f}x) - minat trading lemah, hati-hati dengan pergerakan"
            })

        # OBV Analysis
        obv_change = ((latest['obv'] - df.iloc[-5]['obv']) / abs(df.iloc[-5]['obv'])) * 100
        price_change = ((latest['close'] - df.iloc[-5]['close']) / df.iloc[-5]['close']) * 100

        if obv_change > 10 and price_change < 5:
            reasons.append({
                'indicator': 'OBV',
                'signal': 'ACCUMULATION',
                'strength': 'Strong',
                'explanation': f"OBV naik {obv_change:.1f}% tapi harga hanya naik {price_change:.1f}% - AKUMULASI terdeteksi, harga akan follow"
            })
            score += 15
        elif obv_change < -10 and price_change > -5:
            reasons.append({
                'indicator': 'OBV',
                'signal': 'DISTRIBUTION',
                'strength': 'Strong',
                'explanation': f"OBV turun {obv_change:.1f}% tapi harga hanya turun {price_change:.1f}% - DISTRIBUSI terdeteksi, harga akan follow"
            })
            score -= 15

        return reasons, score

    def analyze_full(self, df):
        """Complete analysis of stock movement"""

        # Analyze all aspects
        trend_reasons, trend_score = self.analyze_trend(df)
        momentum_reasons, momentum_score = self.analyze_momentum(df)
        volatility_reasons, volatility_score = self.analyze_volatility(df)
        volume_reasons, volume_score = self.analyze_volume(df)

        # Combine all reasons
        all_reasons = trend_reasons + momentum_reasons + volatility_reasons + volume_reasons

        # Calculate total score
        total_score = trend_score + momentum_score + volatility_score + volume_score

        # Determine overall signal
        if total_score > 40:
            overall_signal = "STRONG BUY"
            overall_explanation = "Mayoritas indikator menunjukkan sinyal beli yang kuat"
        elif total_score > 15:
            overall_signal = "BUY"
            overall_explanation = "Indikator cenderung positif untuk beli"
        elif total_score > -15:
            overall_signal = "HOLD"
            overall_explanation = "Indikator mixed, lebih baik tunggu sinyal lebih jelas"
        elif total_score > -40:
            overall_signal = "SELL"
            overall_explanation = "Indikator cenderung negatif untuk jual"
        else:
            overall_signal = "STRONG SELL"
            overall_explanation = "Mayoritas indikator menunjukkan sinyal jual yang kuat"

        # Categorize reasons
        bullish_reasons = [r for r in all_reasons if r['signal'] in ['BULLISH', 'OVERSOLD', 'ACCUMULATION']]
        bearish_reasons = [r for r in all_reasons if r['signal'] in ['BEARISH', 'OVERBOUGHT', 'DISTRIBUTION']]
        neutral_reasons = [r for r in all_reasons if r['signal'] in ['NEUTRAL', 'CONSOLIDATION', 'HIGH VOLATILITY', 'LOW ACTIVITY', 'ACTIVE']]

        return {
            'overall_signal': overall_signal,
            'overall_explanation': overall_explanation,
            'total_score': total_score,
            'trend_score': trend_score,
            'momentum_score': momentum_score,
            'volatility_score': volatility_score,
            'volume_score': volume_score,
            'all_reasons': all_reasons,
            'bullish_reasons': bullish_reasons,
            'bearish_reasons': bearish_reasons,
            'neutral_reasons': neutral_reasons,
            'bullish_count': len(bullish_reasons),
            'bearish_count': len(bearish_reasons),
            'neutral_count': len(neutral_reasons)
        }

    def get_summary(self, analysis):
        """Get text summary of analysis"""

        summary = f"""
**Overall Signal: {analysis['overall_signal']}** (Score: {analysis['total_score']}/100)

{analysis['overall_explanation']}

**Breakdown:**
- Trend Score: {analysis['trend_score']}
- Momentum Score: {analysis['momentum_score']}
- Volatility Score: {analysis['volatility_score']}
- Volume Score: {analysis['volume_score']}

**Signals:**
- 🟢 Bullish: {analysis['bullish_count']}
- 🔴 Bearish: {analysis['bearish_count']}
- 🟡 Neutral: {analysis['neutral_count']}
"""
        return summary

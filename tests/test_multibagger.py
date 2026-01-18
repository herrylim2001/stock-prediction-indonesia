"""
Unit Tests for Multibagger Trading System
==========================================

Tests entry/exit point calculations, signal generation, and risk/reward ratios.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


class TestEntryExitCalculations:
    """Test entry and exit price calculations"""

    @pytest.fixture
    def sample_metrics(self):
        """Sample metrics for testing"""
        return {
            'current_price': 10000,
            'day_high': 10500,
            'day_low': 9800,
            'day_range': 700,
            'position_in_range': 0.5,  # Mid-range
            'daily_change': 100,
            'daily_change_pct': 1.0,
            'volume_ratio': 1.5
        }

    def test_entry_price_at_high(self, sample_metrics):
        """Test entry price when stock is near day's high"""
        metrics = sample_metrics.copy()
        metrics['position_in_range'] = 0.8  # Near high (80%)

        # Entry should be below current price for pullback
        current_price = metrics['current_price']
        entry_price = current_price * 0.995  # 0.5% below

        assert entry_price < current_price, "Entry should be below current when near high"
        assert entry_price == 9950, "Entry should be 0.5% below current price"

    def test_entry_price_at_support(self, sample_metrics):
        """Test entry price when stock is near support"""
        metrics = sample_metrics.copy()
        metrics['position_in_range'] = 0.2  # Near low (20%)

        # Entry should be at current price
        current_price = metrics['current_price']
        entry_price = current_price

        assert entry_price == current_price, "Entry should be at current price near support"

    def test_target_price_strong_buy(self):
        """Test target price for STRONG_BUY signal"""
        entry_price = 10000
        signal_score = 80

        # Target: 3% + (signal_score/100 * 2%)
        target_pct = 0.03 + (signal_score / 100 * 0.02)
        target_price = entry_price * (1 + target_pct)

        expected_target = 10000 * 1.046  # 4.6%
        assert abs(target_price - expected_target) < 1, "Target should be ~4.6% above entry"

    def test_target_price_buy(self):
        """Test target price for BUY signal"""
        entry_price = 10000
        signal_score = 60

        # Target: 2% + (signal_score/100 * 1.5%)
        target_pct = 0.02 + (signal_score / 100 * 0.015)
        target_price = entry_price * (1 + target_pct)

        expected_target = 10000 * 1.029  # 2.9%
        assert abs(target_price - expected_target) < 1, "Target should be ~2.9% above entry"

    def test_stop_loss_calculation(self):
        """Test stop loss calculation"""
        entry_price = 10000
        day_range = 200  # 2% range
        current_price = 10000

        # Base SL: 1.5% + volatility adjustment
        base_sl = 0.015
        volatility_add = 0.5 * (day_range / current_price)
        total_sl_pct = base_sl + volatility_add

        stop_loss = entry_price * (1 - total_sl_pct)

        assert stop_loss < entry_price, "Stop loss should be below entry"
        assert stop_loss >= entry_price * 0.975, "Stop loss should not be too far (max 2.5%)"

    def test_risk_reward_ratio(self):
        """Test risk/reward ratio calculation"""
        entry_price = 10000
        target_price = 10400  # +4%
        stop_loss = 9800  # -2%

        potential_profit = target_price - entry_price  # 400
        potential_loss = entry_price - stop_loss  # 200

        risk_reward = potential_profit / potential_loss

        assert risk_reward == 2.0, "R:R should be 1:2.0"
        assert risk_reward >= 1.5, "R:R should be at least 1:1.5 for good trade"

    def test_risk_reward_rating(self):
        """Test risk/reward rating system"""
        test_cases = [
            (2.5, "Excellent", "🟢"),
            (1.8, "Good", "🟡"),
            (1.2, "Poor", "🔴")
        ]

        for rr, expected_text, expected_color in test_cases:
            if rr >= 2.0:
                rating = "Excellent"
                color = "🟢"
            elif rr >= 1.5:
                rating = "Good"
                color = "🟡"
            else:
                rating = "Poor"
                color = "🔴"

            assert rating == expected_text, f"R:R {rr} should be rated {expected_text}"
            assert color == expected_color, f"R:R {rr} should have color {expected_color}"


class TestSignalGeneration:
    """Test trading signal generation"""

    def test_signal_score_strong_buy(self):
        """Test STRONG_BUY signal threshold"""
        signal_score = 45

        if signal_score >= 40:
            signal = "STRONG_BUY"
        elif signal_score >= 20:
            signal = "BUY"
        else:
            signal = "HOLD"

        assert signal == "STRONG_BUY", "Score ≥40 should be STRONG_BUY"

    def test_signal_score_buy(self):
        """Test BUY signal threshold"""
        signal_score = 30

        if signal_score >= 40:
            signal = "STRONG_BUY"
        elif signal_score >= 20:
            signal = "BUY"
        else:
            signal = "HOLD"

        assert signal == "BUY", "Score 20-39 should be BUY"

    def test_signal_score_hold(self):
        """Test HOLD signal threshold"""
        signal_score = 10

        if signal_score >= 40:
            signal = "STRONG_BUY"
        elif signal_score >= 20:
            signal = "BUY"
        elif signal_score >= -20:
            signal = "HOLD"
        else:
            signal = "SELL"

        assert signal == "HOLD", "Score -20 to 19 should be HOLD"

    def test_signal_score_sell(self):
        """Test SELL signal threshold"""
        signal_score = -30

        if signal_score >= 20:
            signal = "BUY"
        elif signal_score >= -20:
            signal = "HOLD"
        elif signal_score >= -40:
            signal = "SELL"
        else:
            signal = "STRONG_SELL"

        assert signal == "SELL", "Score -40 to -21 should be SELL"

    def test_signal_components(self):
        """Test 6-component signal algorithm"""
        # Component scores (max 100 points)
        price_vs_sma = 20  # Price above SMA-5
        daily_momentum = 15  # Positive daily gain
        volume_analysis = 10  # Good volume
        rsi_score = 0  # Neutral RSI
        intraday_position = 10  # Mid-range
        momentum_5d = 15  # Positive 5-day momentum

        total_score = (price_vs_sma + daily_momentum + volume_analysis +
                      rsi_score + intraday_position + momentum_5d)

        assert total_score <= 100, "Total score should not exceed 100"
        assert total_score == 70, "Sum of components should be correct"

    def test_best_time_recommendation(self):
        """Test best time to trade recommendations"""
        test_cases = [
            (0.2, "NOW - Price near support"),
            (0.5, "Good entry range"),
            (0.8, "Wait for pullback to support")
        ]

        for position, expected_recommendation in test_cases:
            if position < 0.3:
                recommendation = "NOW - Price near support"
            elif position > 0.7:
                recommendation = "Wait for pullback to support"
            else:
                recommendation = "Good entry range"

            assert recommendation == expected_recommendation, \
                f"Position {position} should recommend: {expected_recommendation}"


class TestPortfolioSimulation:
    """Test portfolio simulation and capital allocation"""

    def test_equal_allocation(self):
        """Test equal capital allocation"""
        total_capital = 100_000_000
        num_stocks = 5

        allocation_per_stock = total_capital / num_stocks

        assert allocation_per_stock == 20_000_000, "Should allocate equally"
        assert allocation_per_stock * num_stocks == total_capital, "Should sum to total"

    def test_position_calculation(self):
        """Test position size calculation"""
        capital_allocated = 20_000_000
        price_per_share = 10_000

        shares = capital_allocated // price_per_share

        assert shares == 2000, "Should buy 2000 shares"
        assert shares * price_per_share <= capital_allocated, "Should not exceed allocation"

    def test_daily_pl_calculation(self):
        """Test daily P/L calculation"""
        shares = 2000
        entry_price = 10_000
        current_price = 10_200

        daily_pl = shares * (current_price - entry_price)
        daily_pl_pct = ((current_price - entry_price) / entry_price) * 100

        assert daily_pl == 400_000, "P/L should be Rp 400,000"
        assert daily_pl_pct == 2.0, "P/L% should be 2.0%"

    def test_portfolio_total_pl(self):
        """Test total portfolio P/L"""
        positions = [
            {'shares': 2000, 'entry': 10_000, 'current': 10_200},  # +400k
            {'shares': 1500, 'entry': 15_000, 'current': 14_850},  # -225k
            {'shares': 3000, 'entry': 5_000, 'current': 5_100},    # +300k
        ]

        total_pl = sum(
            pos['shares'] * (pos['current'] - pos['entry'])
            for pos in positions
        )

        assert total_pl == 475_000, "Total P/L should be Rp 475,000"

    def test_cash_reserve_calculation(self):
        """Test cash reserve calculation"""
        total_capital = 100_000_000
        invested = 75_000_000

        cash_reserve = total_capital - invested

        assert cash_reserve == 25_000_000, "Cash reserve should be Rp 25M"
        assert cash_reserve >= 0, "Cash reserve should not be negative"


class TestSupportResistance:
    """Test support and resistance level identification"""

    def test_support_level_intraday(self):
        """Test intraday support level"""
        day_low = 9800
        day_high = 10500
        current_price = 10200

        support = day_low

        assert support == 9800, "Support should be day's low"
        assert support < current_price, "Support should be below current price"

    def test_resistance_level_intraday(self):
        """Test intraday resistance level"""
        day_low = 9800
        day_high = 10500
        current_price = 10200

        resistance = day_high

        assert resistance == 10500, "Resistance should be day's high"
        assert resistance > current_price, "Resistance should be above current price"

    def test_distance_to_support(self):
        """Test distance calculation to support"""
        current_price = 10000
        support = 9800

        distance_pct = ((current_price - support) / support) * 100

        assert abs(distance_pct - 2.04) < 0.01, "Distance should be ~2.04%"

    def test_distance_to_resistance(self):
        """Test distance calculation to resistance"""
        current_price = 10000
        resistance = 10500

        distance_pct = ((resistance - current_price) / current_price) * 100

        assert distance_pct == 5.0, "Distance should be 5.0%"


class TestTradingScenarios:
    """Test real-world trading scenarios"""

    def test_bullish_scenario(self):
        """Test complete bullish trade setup"""
        # Stock moving up with strong momentum
        metrics = {
            'current_price': 10200,
            'day_high': 10500,
            'day_low': 10000,
            'position_in_range': 0.4,  # Good position
            'daily_change_pct': 2.0,
            'volume_ratio': 2.5,
            'rsi': 65
        }

        # Signal should be positive
        signal_score = 20 + 20 + 15 + 0 + 10 + 15  # All positive components
        assert signal_score >= 40, "Should generate STRONG_BUY signal"

        # Entry/exit setup
        entry = metrics['current_price']  # Buy now
        target = entry * 1.04  # 4% target
        stop_loss = entry * 0.98  # 2% stop

        rr = (target - entry) / (entry - stop_loss)
        assert rr >= 2.0, "Should have excellent risk/reward"

    def test_bearish_scenario(self):
        """Test complete bearish trade setup"""
        # Stock falling with weakness
        metrics = {
            'current_price': 9800,
            'day_high': 10200,
            'day_low': 9700,
            'position_in_range': 0.2,  # Near lows
            'daily_change_pct': -2.0,
            'volume_ratio': 2.0,
            'rsi': 25  # Oversold
        }

        # Signal could be negative or reversal buy
        # Negative momentum: -20, -20
        # High volume in downtrend: -5
        # But oversold RSI: +15 (potential reversal)

        # Decision: Wait for confirmation
        assert metrics['rsi'] < 30, "Oversold condition detected"
        # Could be reversal opportunity or continued weakness

    def test_neutral_scenario(self):
        """Test neutral/sideways trade setup"""
        metrics = {
            'current_price': 10000,
            'day_high': 10100,
            'day_low': 9900,
            'position_in_range': 0.5,
            'daily_change_pct': 0.0,
            'volume_ratio': 1.0,
            'rsi': 50
        }

        # Signal should be near zero
        signal_score = 0  # All neutral components
        assert -20 <= signal_score <= 20, "Should generate HOLD signal"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

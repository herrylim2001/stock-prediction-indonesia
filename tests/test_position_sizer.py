"""
Unit Tests for Position Sizing Calculator
==========================================

Test all position sizing methods and edge cases.
"""

import pytest
import numpy as np
from utils.position_sizer import PositionSizer, format_position_size_display


class TestKellyCriterion:
    """Test Kelly Criterion calculations"""

    @pytest.fixture
    def sizer(self):
        return PositionSizer(total_capital=100_000_000)

    def test_kelly_basic(self, sizer):
        """Test basic Kelly calculation"""
        result = sizer.kelly_criterion(
            win_rate=0.70,
            avg_win=0.03,
            avg_loss=0.015,
            safety_factor=0.25
        )

        assert 'kelly_percentage' in result
        assert 'safe_kelly_percentage' in result
        assert result['safe_kelly_percentage'] < result['kelly_percentage']
        assert result['position_value'] > 0

    def test_kelly_negative(self, sizer):
        """Test Kelly with losing strategy"""
        result = sizer.kelly_criterion(
            win_rate=0.40,  # 40% win rate
            avg_win=0.02,
            avg_loss=0.03,  # Losses bigger than wins
            safety_factor=0.25
        )

        # Should suggest no position or very small
        assert result['kelly_percentage'] <= 0 or result['safe_kelly_percentage'] <= 5

    def test_kelly_validation(self, sizer):
        """Test Kelly input validation"""
        # Invalid win rate
        result = sizer.kelly_criterion(
            win_rate=1.5,  # Invalid >1
            avg_win=0.03,
            avg_loss=0.015
        )
        assert 'error' in result

    def test_kelly_perfect_strategy(self, sizer):
        """Test Kelly with very good strategy"""
        result = sizer.kelly_criterion(
            win_rate=0.80,  # 80% win rate
            avg_win=0.05,   # 5% avg win
            avg_loss=0.01,  # 1% avg loss
            safety_factor=0.25
        )

        # Should suggest significant position
        assert result['safe_kelly_percentage'] > 5
        assert result['win_loss_ratio'] == 5.0


class TestFixedFractional:
    """Test Fixed Fractional position sizing"""

    @pytest.fixture
    def sizer(self):
        return PositionSizer(total_capital=100_000_000)

    def test_fixed_fractional_basic(self, sizer):
        """Test basic fixed fractional"""
        result = sizer.fixed_fractional(fraction=0.02)

        assert result['risk_percentage'] == 2.0
        assert result['position_value'] == 2_000_000

    def test_fixed_fractional_cap(self, sizer):
        """Test fractional capping at max"""
        result = sizer.fixed_fractional(
            fraction=0.15,  # 15%
            max_fraction=0.10  # Max 10%
        )

        # Should be capped at 10%
        assert result['risk_percentage'] == 10.0

    def test_fixed_fractional_conservative(self, sizer):
        """Test conservative fractional"""
        result = sizer.fixed_fractional(fraction=0.01)

        assert result['risk_percentage'] == 1.0
        assert 'CONSERVATIVE' in result['recommendation']


class TestPercentRisk:
    """Test Percent Risk position sizing"""

    @pytest.fixture
    def sizer(self):
        return PositionSizer(total_capital=100_000_000)

    def test_percent_risk_basic(self, sizer):
        """Test basic percent risk calculation"""
        result = sizer.percent_risk(
            entry_price=10_000,
            stop_loss=9_800,
            risk_per_trade=0.02
        )

        assert result['shares'] > 0
        assert result['lots'] > 0
        assert result['actual_risk_percentage'] > 0

    def test_percent_risk_tight_stop(self, sizer):
        """Test with tight stop loss"""
        result = sizer.percent_risk(
            entry_price=10_000,
            stop_loss=9_950,  # 0.5% stop
            risk_per_trade=0.02
        )

        # Tight stop = larger position
        assert result['shares'] > 10_000

    def test_percent_risk_wide_stop(self, sizer):
        """Test with wide stop loss"""
        result = sizer.percent_risk(
            entry_price=10_000,
            stop_loss=9_500,  # 5% stop
            risk_per_trade=0.02
        )

        # Wide stop = smaller position
        assert result['shares'] < 5_000

    def test_percent_risk_validation(self, sizer):
        """Test input validation"""
        # Stop above entry
        result = sizer.percent_risk(
            entry_price=10_000,
            stop_loss=10_500,  # Above entry!
            risk_per_trade=0.02
        )

        assert 'error' in result


class TestRiskRewardSizing:
    """Test Risk/Reward based sizing"""

    @pytest.fixture
    def sizer(self):
        return PositionSizer(total_capital=100_000_000)

    def test_rr_good_trade(self, sizer):
        """Test trade with good R:R"""
        result = sizer.risk_reward_sizing(
            entry_price=10_000,
            stop_loss=9_800,  # 2% risk
            target_price=10_400,  # 4% reward
            risk_per_trade=0.02,
            min_risk_reward=1.5
        )

        assert result['risk_reward_ratio'] == 2.0
        assert result['trade_approved'] is True
        assert 'GOOD' in result['recommendation'] or 'EXCELLENT' in result['recommendation']

    def test_rr_poor_trade(self, sizer):
        """Test trade with poor R:R"""
        result = sizer.risk_reward_sizing(
            entry_price=10_000,
            stop_loss=9_800,  # 2% risk
            target_price=10_100,  # 1% reward
            risk_per_trade=0.02,
            min_risk_reward=1.5
        )

        assert result['risk_reward_ratio'] == 0.5
        assert result['trade_approved'] is False
        assert 'SKIP' in result['recommendation']

    def test_rr_minimum_threshold(self, sizer):
        """Test R:R at minimum threshold"""
        result = sizer.risk_reward_sizing(
            entry_price=10_000,
            stop_loss=9_800,  # 2% risk
            target_price=10_300,  # 3% reward = 1.5 R:R
            risk_per_trade=0.02,
            min_risk_reward=1.5
        )

        assert result['risk_reward_ratio'] == 1.5
        assert result['trade_approved'] is True


class TestPortfolioHeat:
    """Test portfolio heat calculations"""

    @pytest.fixture
    def sizer(self):
        return PositionSizer(total_capital=100_000_000)

    def test_portfolio_heat_empty(self, sizer):
        """Test with no open positions"""
        result = sizer.portfolio_heat(open_positions=[])

        assert result['portfolio_heat'] == 0
        assert result['can_take_new_trade'] is True

    def test_portfolio_heat_single_position(self, sizer):
        """Test with one position"""
        positions = [
            {'shares': 2000, 'entry': 10_000, 'stop_loss': 9_800}
        ]

        result = sizer.portfolio_heat(positions, max_heat=0.06)

        # Risk = 2000 × (10_000 - 9_800) = 400,000
        # Heat = 400,000 / 100,000,000 = 0.4%
        assert abs(result['portfolio_heat'] - 0.4) < 0.01
        assert result['can_take_new_trade'] is True

    def test_portfolio_heat_multiple_positions(self, sizer):
        """Test with multiple positions"""
        positions = [
            {'shares': 2000, 'entry': 10_000, 'stop_loss': 9_800},  # 400k risk
            {'shares': 3000, 'entry': 5_000, 'stop_loss': 4_900},   # 300k risk
            {'shares': 1000, 'entry': 15_000, 'stop_loss': 14_700}  # 300k risk
        ]

        result = sizer.portfolio_heat(positions, max_heat=0.06)

        # Total risk = 1,000,000 = 1%
        assert abs(result['portfolio_heat'] - 1.0) < 0.1

    def test_portfolio_heat_at_max(self, sizer):
        """Test portfolio at maximum heat"""
        # Create positions totaling 6% heat
        positions = [
            {'shares': 10000, 'entry': 10_000, 'stop_loss': 9_400}  # 6M risk = 6%
        ]

        result = sizer.portfolio_heat(positions, max_heat=0.06)

        assert result['portfolio_heat'] >= 6.0
        assert result['can_take_new_trade'] is False
        assert 'MAXIMUM' in result['recommendation']


class TestCorrelationAdjustment:
    """Test correlation-based position adjustments"""

    @pytest.fixture
    def sizer(self):
        return PositionSizer(total_capital=100_000_000)

    def test_low_correlation(self, sizer):
        """Test with low correlation"""
        result = sizer.correlation_adjusted_sizing(
            base_position_size=10_000_000,
            correlation=0.3,
            max_correlation=0.7
        )

        # Should not reduce size
        assert result['adjustment_factor'] == 1.0
        assert result['adjusted_position_size'] == 10_000_000

    def test_high_correlation(self, sizer):
        """Test with high correlation"""
        result = sizer.correlation_adjusted_sizing(
            base_position_size=10_000_000,
            correlation=0.9,
            max_correlation=0.7
        )

        # Should reduce size
        assert result['adjustment_factor'] < 1.0
        assert result['adjusted_position_size'] < 10_000_000
        assert result['size_reduction'] > 0

    def test_negative_correlation(self, sizer):
        """Test with negative correlation"""
        result = sizer.correlation_adjusted_sizing(
            base_position_size=10_000_000,
            correlation=-0.9,  # Negative but high absolute
            max_correlation=0.7
        )

        # Should reduce size (uses absolute correlation)
        assert result['adjustment_factor'] < 1.0


class TestComprehensiveRecommendation:
    """Test comprehensive position recommendation"""

    @pytest.fixture
    def sizer(self):
        return PositionSizer(total_capital=100_000_000)

    def test_recommendation_without_kelly(self, sizer):
        """Test recommendation without historical data"""
        result = sizer.get_position_recommendation(
            entry_price=10_000,
            stop_loss=9_800,
            target_price=10_400,
            risk_per_trade=0.02
        )

        assert 'primary_method' in result
        assert 'summary' in result
        assert result['summary']['trade_approved'] is True
        assert 'R:R sizing' in result['recommendation_basis']

    def test_recommendation_with_kelly(self, sizer):
        """Test recommendation with historical data"""
        result = sizer.get_position_recommendation(
            entry_price=10_000,
            stop_loss=9_800,
            target_price=10_400,
            risk_per_trade=0.02,
            win_rate=0.70,
            avg_win=0.03,
            avg_loss=0.015
        )

        assert 'kelly_criterion' in result
        assert 'recommended_position_value' in result

    def test_recommendation_summary(self, sizer):
        """Test recommendation summary contents"""
        result = sizer.get_position_recommendation(
            entry_price=10_000,
            stop_loss=9_800,
            target_price=10_400,
            risk_per_trade=0.02
        )

        summary = result['summary']
        assert 'entry_price' in summary
        assert 'stop_loss' in summary
        assert 'target_price' in summary
        assert 'risk_reward_ratio' in summary
        assert 'recommended_shares' in summary
        assert 'position_value' in summary


class TestFormatting:
    """Test display formatting"""

    def test_format_basic(self):
        """Test basic formatting"""
        data = {
            'method': 'Test Method',
            'shares': 2000,
            'lots': 20,
            'position_value': 20_000_000,
            'actual_risk': 400_000,
            'actual_risk_percentage': 0.4,
            'recommendation': '🟢 Test recommendation'
        }

        output = format_position_size_display(data)

        assert 'Test Method' in output
        assert '2,000 shares' in output or '2.000 shares' in output
        assert '20,000,000' in output or '20.000.000' in output
        assert 'Test recommendation' in output

    def test_format_error(self):
        """Test error formatting"""
        data = {'error': 'Test error message'}

        output = format_position_size_display(data)

        assert '❌' in output
        assert 'Test error' in output


class TestRealWorldScenarios:
    """Test realistic trading scenarios"""

    @pytest.fixture
    def sizer(self):
        return PositionSizer(total_capital=100_000_000)

    def test_conservative_trader(self, sizer):
        """Test conservative trader (1% risk)"""
        result = sizer.percent_risk(
            entry_price=10_000,
            stop_loss=9_900,  # 1% stop
            risk_per_trade=0.01  # 1% risk
        )

        # 1% of 100M = 1M risk
        # 1M / 100 per share = 10,000 shares
        assert result['shares'] == 10_000
        assert result['actual_risk_percentage'] <= 1.1  # Allow small deviation

    def test_aggressive_trader(self, sizer):
        """Test aggressive trader (5% risk)"""
        result = sizer.percent_risk(
            entry_price=10_000,
            stop_loss=9_800,  # 2% stop
            risk_per_trade=0.05  # 5% risk
        )

        # Should have larger position
        assert result['actual_risk_percentage'] >= 4.5

    def test_swing_trader(self, sizer):
        """Test swing trader (wider stops, bigger targets)"""
        result = sizer.risk_reward_sizing(
            entry_price=10_000,
            stop_loss=9_500,  # 5% stop
            target_price=11_000,  # 10% target
            risk_per_trade=0.02
        )

        assert result['risk_reward_ratio'] == 2.0
        assert result['trade_approved'] is True

    def test_scalper(self, sizer):
        """Test scalper (tight stops, small targets)"""
        result = sizer.risk_reward_sizing(
            entry_price=10_000,
            stop_loss=9_950,  # 0.5% stop
            target_price=10_100,  # 1% target
            risk_per_trade=0.01
        )

        assert result['risk_reward_ratio'] == 2.0
        assert result['shares'] > 20_000  # Large position due to tight stop


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

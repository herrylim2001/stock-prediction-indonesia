"""
Position Sizing Calculator
==========================

Calculate optimal position sizes using various methods:
- Kelly Criterion
- Fixed Fractional
- Percent Risk
- Portfolio Heat
- Risk-adjusted sizing

For Indonesian Stock Market (IDX)
"""

import numpy as np
import pandas as pd
from typing import Dict, Optional, Tuple


class PositionSizer:
    """Calculate optimal position sizes for trading"""

    def __init__(self, total_capital: float = 100_000_000):
        """
        Initialize Position Sizer

        Args:
            total_capital: Total trading capital in Rupiah (default: 100 juta)
        """
        self.total_capital = total_capital
        self.min_lot_size = 100  # IDX minimum lot size

    def kelly_criterion(
        self,
        win_rate: float,
        avg_win: float,
        avg_loss: float,
        safety_factor: float = 0.25
    ) -> Dict:
        """
        Calculate position size using Kelly Criterion

        Formula: f = (p * b - q) / b
        Where:
        - f = fraction of capital to bet
        - p = probability of win (win rate)
        - q = probability of loss (1 - win rate)
        - b = win/loss ratio (avg_win / avg_loss)

        Args:
            win_rate: Historical win rate (0-1, e.g., 0.70 for 70%)
            avg_win: Average winning trade percentage (e.g., 0.03 for 3%)
            avg_loss: Average losing trade percentage (e.g., 0.015 for 1.5%)
            safety_factor: Fractional Kelly (default: 0.25 = Quarter Kelly)

        Returns:
            dict with position sizing details
        """
        # Validate inputs
        if not 0 < win_rate < 1:
            return {'error': 'Win rate must be between 0 and 1'}

        if avg_win <= 0 or avg_loss <= 0:
            return {'error': 'Avg win and avg loss must be positive'}

        # Calculate Kelly percentage
        p = win_rate
        q = 1 - win_rate
        b = avg_win / avg_loss  # Win/loss ratio

        kelly_pct = (p * b - q) / b

        # Apply safety factor (fractional Kelly)
        safe_kelly_pct = kelly_pct * safety_factor

        # Ensure positive and cap at 100%
        safe_kelly_pct = max(0, min(safe_kelly_pct, 1.0))

        # Calculate position size
        position_value = self.total_capital * safe_kelly_pct

        return {
            'method': 'Kelly Criterion',
            'kelly_percentage': kelly_pct * 100,
            'safe_kelly_percentage': safe_kelly_pct * 100,
            'position_value': position_value,
            'win_rate': win_rate * 100,
            'win_loss_ratio': b,
            'safety_factor': safety_factor,
            'recommendation': self._get_kelly_recommendation(safe_kelly_pct)
        }

    def fixed_fractional(
        self,
        fraction: float = 0.02,
        max_fraction: float = 0.10
    ) -> Dict:
        """
        Fixed Fractional position sizing

        Risk a fixed percentage of capital per trade

        Args:
            fraction: Fraction of capital to risk (default: 0.02 = 2%)
            max_fraction: Maximum allowed fraction (default: 0.10 = 10%)

        Returns:
            dict with position sizing details
        """
        # Validate and cap fraction
        fraction = max(0.001, min(fraction, max_fraction))

        position_value = self.total_capital * fraction

        return {
            'method': 'Fixed Fractional',
            'risk_percentage': fraction * 100,
            'position_value': position_value,
            'max_percentage': max_fraction * 100,
            'recommendation': self._get_fixed_fractional_recommendation(fraction)
        }

    def percent_risk(
        self,
        entry_price: float,
        stop_loss: float,
        risk_per_trade: float = 0.02,
        lot_size: int = 100
    ) -> Dict:
        """
        Calculate position size based on percent risk

        Formula: Position Size = (Capital × Risk%) / (Entry - Stop Loss)

        Args:
            entry_price: Entry price per share
            stop_loss: Stop loss price per share
            risk_per_trade: Risk per trade as decimal (default: 0.02 = 2%)
            lot_size: Lot size (default: 100 shares for IDX)

        Returns:
            dict with position sizing details
        """
        # Validate inputs
        if entry_price <= 0 or stop_loss <= 0:
            return {'error': 'Prices must be positive'}

        if entry_price <= stop_loss:
            return {'error': 'Entry price must be above stop loss'}

        # Calculate risk per share
        risk_per_share = entry_price - stop_loss

        # Calculate capital at risk
        capital_at_risk = self.total_capital * risk_per_trade

        # Calculate number of shares
        shares = capital_at_risk / risk_per_share

        # Round to lot size
        lots = int(shares / lot_size)
        actual_shares = lots * lot_size

        # Recalculate actual values
        position_value = actual_shares * entry_price
        actual_risk = actual_shares * risk_per_share
        actual_risk_pct = (actual_risk / self.total_capital) * 100

        return {
            'method': 'Percent Risk',
            'entry_price': entry_price,
            'stop_loss': stop_loss,
            'risk_per_share': risk_per_share,
            'target_risk_percentage': risk_per_trade * 100,
            'shares': actual_shares,
            'lots': lots,
            'position_value': position_value,
            'actual_risk': actual_risk,
            'actual_risk_percentage': actual_risk_pct,
            'recommendation': self._get_percent_risk_recommendation(actual_risk_pct, risk_per_trade * 100)
        }

    def risk_reward_sizing(
        self,
        entry_price: float,
        stop_loss: float,
        target_price: float,
        risk_per_trade: float = 0.02,
        min_risk_reward: float = 1.5
    ) -> Dict:
        """
        Position sizing with risk/reward validation

        Only take trade if R:R meets minimum threshold

        Args:
            entry_price: Entry price per share
            stop_loss: Stop loss price per share
            target_price: Target/take profit price per share
            risk_per_trade: Risk per trade (default: 0.02 = 2%)
            min_risk_reward: Minimum R:R ratio (default: 1.5)

        Returns:
            dict with position sizing and R:R analysis
        """
        # Calculate R:R ratio
        risk_per_share = entry_price - stop_loss
        reward_per_share = target_price - entry_price

        if risk_per_share <= 0:
            return {'error': 'Invalid stop loss (must be below entry)'}

        if reward_per_share <= 0:
            return {'error': 'Invalid target (must be above entry)'}

        risk_reward_ratio = reward_per_share / risk_per_share

        # Check if R:R meets threshold
        trade_approved = risk_reward_ratio >= min_risk_reward

        # Calculate position size using percent risk method
        position = self.percent_risk(entry_price, stop_loss, risk_per_trade)

        if 'error' in position:
            return position

        # Add R:R analysis
        position.update({
            'method': 'Risk/Reward Sizing',
            'target_price': target_price,
            'risk_reward_ratio': risk_reward_ratio,
            'min_risk_reward': min_risk_reward,
            'trade_approved': trade_approved,
            'potential_profit': position['shares'] * reward_per_share,
            'potential_loss': position['shares'] * risk_per_share,
            'recommendation': self._get_rr_recommendation(risk_reward_ratio, trade_approved)
        })

        return position

    def portfolio_heat(
        self,
        open_positions: list,
        max_heat: float = 0.06
    ) -> Dict:
        """
        Calculate portfolio heat (total risk across all positions)

        Portfolio heat = sum of all position risks / total capital

        Args:
            open_positions: List of dicts with 'shares', 'entry', 'stop_loss'
            max_heat: Maximum portfolio heat allowed (default: 0.06 = 6%)

        Returns:
            dict with portfolio heat analysis
        """
        total_risk = 0

        for pos in open_positions:
            shares = pos.get('shares', 0)
            entry = pos.get('entry', 0)
            stop_loss = pos.get('stop_loss', 0)

            if entry > stop_loss > 0:
                risk_per_share = entry - stop_loss
                position_risk = shares * risk_per_share
                total_risk += position_risk

        # Calculate heat percentage
        heat_pct = (total_risk / self.total_capital) if self.total_capital > 0 else 0

        # Calculate remaining heat capacity
        remaining_heat = max_heat - heat_pct
        remaining_capital = remaining_heat * self.total_capital if remaining_heat > 0 else 0

        return {
            'total_risk': total_risk,
            'portfolio_heat': heat_pct * 100,
            'max_heat': max_heat * 100,
            'remaining_heat': remaining_heat * 100 if remaining_heat > 0 else 0,
            'remaining_capital': remaining_capital,
            'can_take_new_trade': heat_pct < max_heat,
            'num_positions': len(open_positions),
            'recommendation': self._get_heat_recommendation(heat_pct, max_heat)
        }

    def correlation_adjusted_sizing(
        self,
        base_position_size: float,
        correlation: float,
        max_correlation: float = 0.7
    ) -> Dict:
        """
        Adjust position size based on correlation with existing positions

        Reduce size if highly correlated to avoid concentration risk

        Args:
            base_position_size: Base position size before adjustment
            correlation: Correlation coefficient (-1 to 1)
            max_correlation: Correlation threshold (default: 0.7)

        Returns:
            dict with adjusted position size
        """
        # Absolute correlation
        abs_correlation = abs(correlation)

        # Adjustment factor: reduce size for high correlation
        if abs_correlation > max_correlation:
            adjustment_factor = 1 - ((abs_correlation - max_correlation) / (1 - max_correlation)) * 0.5
        else:
            adjustment_factor = 1.0

        adjusted_size = base_position_size * adjustment_factor

        return {
            'base_position_size': base_position_size,
            'correlation': correlation,
            'adjustment_factor': adjustment_factor,
            'adjusted_position_size': adjusted_size,
            'size_reduction': (base_position_size - adjusted_size),
            'reduction_percentage': (1 - adjustment_factor) * 100,
            'recommendation': self._get_correlation_recommendation(abs_correlation, max_correlation)
        }

    # Helper methods for recommendations
    def _get_kelly_recommendation(self, kelly_pct: float) -> str:
        """Get recommendation based on Kelly percentage"""
        if kelly_pct <= 0:
            return "⚠️ SKIP TRADE - Negative Kelly suggests unfavorable odds"
        elif kelly_pct < 0.05:
            return "🟡 SMALL POSITION - Low Kelly suggests limited edge"
        elif kelly_pct < 0.15:
            return "🟢 MODERATE POSITION - Reasonable Kelly percentage"
        elif kelly_pct < 0.25:
            return "🟢 GOOD POSITION - Strong Kelly percentage"
        else:
            return "⚠️ HIGH RISK - Consider reducing position size"

    def _get_fixed_fractional_recommendation(self, fraction: float) -> str:
        """Get recommendation for fixed fractional sizing"""
        if fraction <= 0.01:
            return "🟢 CONSERVATIVE - Low risk per trade"
        elif fraction <= 0.02:
            return "🟢 MODERATE - Balanced risk approach"
        elif fraction <= 0.05:
            return "🟡 AGGRESSIVE - Higher risk per trade"
        else:
            return "🔴 VERY AGGRESSIVE - Consider reducing risk"

    def _get_percent_risk_recommendation(self, actual_risk: float, target_risk: float) -> str:
        """Get recommendation for percent risk sizing"""
        diff = abs(actual_risk - target_risk)
        if diff < 0.5:
            return f"✅ OPTIMAL - Actual risk ({actual_risk:.1f}%) matches target ({target_risk:.1f}%)"
        elif diff < 1.0:
            return f"🟢 ACCEPTABLE - Actual risk ({actual_risk:.1f}%) close to target ({target_risk:.1f}%)"
        else:
            return f"⚠️ DEVIATION - Actual risk ({actual_risk:.1f}%) differs from target ({target_risk:.1f}%)"

    def _get_rr_recommendation(self, rr: float, approved: bool) -> str:
        """Get recommendation based on risk/reward ratio"""
        if not approved:
            return f"❌ SKIP TRADE - R:R ({rr:.2f}) below minimum threshold"
        elif rr >= 3.0:
            return f"🟢 EXCELLENT - R:R ({rr:.2f}) is very favorable"
        elif rr >= 2.0:
            return f"🟢 GOOD - R:R ({rr:.2f}) is favorable"
        else:
            return f"🟡 ACCEPTABLE - R:R ({rr:.2f}) meets minimum"

    def _get_heat_recommendation(self, heat: float, max_heat: float) -> str:
        """Get recommendation based on portfolio heat"""
        heat_pct = heat * 100
        max_pct = max_heat * 100

        if heat >= max_heat:
            return f"🔴 MAXIMUM HEAT - Portfolio at {heat_pct:.1f}% (max: {max_pct:.1f}%). DO NOT add positions!"
        elif heat >= max_heat * 0.8:
            return f"🟡 HIGH HEAT - Portfolio at {heat_pct:.1f}% (max: {max_pct:.1f}%). Limited room for new trades"
        elif heat >= max_heat * 0.5:
            return f"🟢 MODERATE HEAT - Portfolio at {heat_pct:.1f}% (max: {max_pct:.1f}%). Can add selective trades"
        else:
            return f"🟢 LOW HEAT - Portfolio at {heat_pct:.1f}% (max: {max_pct:.1f}%). Good capacity for new trades"

    def _get_correlation_recommendation(self, correlation: float, max_corr: float) -> str:
        """Get recommendation based on correlation"""
        if correlation > max_corr:
            return f"⚠️ HIGH CORRELATION ({correlation:.2f}) - Position size reduced to manage concentration risk"
        elif correlation > 0.5:
            return f"🟡 MODERATE CORRELATION ({correlation:.2f}) - Some overlap with existing positions"
        else:
            return f"🟢 LOW CORRELATION ({correlation:.2f}) - Good diversification"

    def get_position_recommendation(
        self,
        entry_price: float,
        stop_loss: float,
        target_price: float,
        risk_per_trade: float = 0.02,
        win_rate: Optional[float] = None,
        avg_win: Optional[float] = None,
        avg_loss: Optional[float] = None
    ) -> Dict:
        """
        Get comprehensive position sizing recommendation

        Combines multiple methods for best recommendation

        Args:
            entry_price: Entry price per share
            stop_loss: Stop loss price
            target_price: Target price
            risk_per_trade: Risk per trade (default: 2%)
            win_rate: Historical win rate (optional, for Kelly)
            avg_win: Avg winning % (optional, for Kelly)
            avg_loss: Avg losing % (optional, for Kelly)

        Returns:
            dict with comprehensive recommendation
        """
        results = {}

        # 1. Risk/Reward sizing (primary method)
        rr_sizing = self.risk_reward_sizing(
            entry_price, stop_loss, target_price, risk_per_trade
        )
        results['primary_method'] = rr_sizing

        # 2. Kelly Criterion (if historical data provided)
        if all([win_rate, avg_win, avg_loss]):
            kelly = self.kelly_criterion(win_rate, avg_win, avg_loss)
            results['kelly_criterion'] = kelly

            # Compare with R:R sizing
            kelly_value = kelly.get('position_value', 0)
            rr_value = rr_sizing.get('position_value', 0)

            if kelly_value > 0 and rr_value > 0:
                # Use more conservative of the two
                recommended_value = min(kelly_value, rr_value)
                results['recommended_position_value'] = recommended_value
                results['recommendation_basis'] = 'More conservative of R:R and Kelly'
            else:
                results['recommended_position_value'] = rr_value
                results['recommendation_basis'] = 'R:R sizing only'
        else:
            results['recommended_position_value'] = rr_sizing.get('position_value', 0)
            results['recommendation_basis'] = 'R:R sizing (no historical data for Kelly)'

        # 3. Summary
        results['summary'] = {
            'entry_price': entry_price,
            'stop_loss': stop_loss,
            'target_price': target_price,
            'risk_reward_ratio': rr_sizing.get('risk_reward_ratio', 0),
            'trade_approved': rr_sizing.get('trade_approved', False),
            'recommended_shares': rr_sizing.get('shares', 0),
            'recommended_lots': rr_sizing.get('lots', 0),
            'position_value': results['recommended_position_value'],
            'potential_profit': rr_sizing.get('potential_profit', 0),
            'potential_loss': rr_sizing.get('potential_loss', 0),
        }

        return results


def format_position_size_display(position_data: Dict) -> str:
    """
    Format position sizing data for display

    Args:
        position_data: Dictionary from position sizer methods

    Returns:
        Formatted string for display
    """
    if 'error' in position_data:
        return f"❌ Error: {position_data['error']}"

    method = position_data.get('method', 'Unknown')
    output = [f"**{method}**", ""]

    # Common fields
    if 'shares' in position_data:
        shares = position_data['shares']
        lots = position_data.get('lots', shares // 100)
        output.append(f"📊 **Position Size:** {shares:,.0f} shares ({lots:,.0f} lots)")

    if 'position_value' in position_data:
        value = position_data['position_value']
        output.append(f"💰 **Position Value:** Rp {value:,.0f}")

    if 'actual_risk' in position_data:
        risk = position_data['actual_risk']
        risk_pct = position_data.get('actual_risk_percentage', 0)
        output.append(f"⚠️ **Capital at Risk:** Rp {risk:,.0f} ({risk_pct:.2f}%)")

    if 'risk_reward_ratio' in position_data:
        rr = position_data['risk_reward_ratio']
        output.append(f"📈 **Risk/Reward:** 1:{rr:.2f}")

    if 'potential_profit' in position_data and 'potential_loss' in position_data:
        profit = position_data['potential_profit']
        loss = position_data['potential_loss']
        output.append(f"💵 **Potential Profit:** Rp {profit:,.0f}")
        output.append(f"💸 **Potential Loss:** Rp {loss:,.0f}")

    # Recommendation
    if 'recommendation' in position_data:
        output.append("")
        output.append(position_data['recommendation'])

    return "\n".join(output)

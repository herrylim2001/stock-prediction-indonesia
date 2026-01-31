"""
Corporate Actions Tracker
=========================

Track and analyze corporate actions for Indonesian stocks:
- Dividend announcements & payments
- Stock splits
- Rights issues
- Bonus shares
- Share buybacks

Data sources:
- Yahoo Finance API
- IDX announcements (scraping)
"""

import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import requests
from bs4 import BeautifulSoup


class CorporateActionsTracker:
    """Track corporate actions for stocks"""

    def __init__(self, stock_code: str):
        """
        Initialize Corporate Actions Tracker

        Args:
            stock_code: Stock ticker (e.g., 'BBCA.JK')
        """
        self.stock_code = stock_code
        self.ticker = yf.Ticker(stock_code)

    def get_dividends(self, period: str = '5y') -> pd.DataFrame:
        """
        Get dividend history

        Args:
            period: Historical period (1y, 2y, 5y, 10y, max)

        Returns:
            DataFrame with dividend dates and amounts
        """
        try:
            dividends = self.ticker.dividends

            if dividends.empty:
                return pd.DataFrame(columns=['Date', 'Dividend'])

            df = dividends.reset_index()
            df.columns = ['Date', 'Dividend']
            df['Date'] = pd.to_datetime(df['Date'])

            # Filter by period
            cutoff_date = self._get_cutoff_date(period)
            df = df[df['Date'] >= cutoff_date]

            return df.sort_values('Date', ascending=False)

        except Exception as e:
            print(f"Error fetching dividends: {e}")
            return pd.DataFrame(columns=['Date', 'Dividend'])

    def get_stock_splits(self, period: str = '5y') -> pd.DataFrame:
        """
        Get stock split history

        Args:
            period: Historical period

        Returns:
            DataFrame with split dates and ratios
        """
        try:
            splits = self.ticker.splits

            if splits.empty:
                return pd.DataFrame(columns=['Date', 'Split_Ratio'])

            df = splits.reset_index()
            df.columns = ['Date', 'Split_Ratio']
            df['Date'] = pd.to_datetime(df['Date'])

            # Filter by period
            cutoff_date = self._get_cutoff_date(period)
            df = df[df['Date'] >= cutoff_date]

            # Add split description
            df['Description'] = df['Split_Ratio'].apply(self._format_split_ratio)

            return df.sort_values('Date', ascending=False)

        except Exception as e:
            print(f"Error fetching splits: {e}")
            return pd.DataFrame(columns=['Date', 'Split_Ratio', 'Description'])

    def get_upcoming_dividends(self) -> Dict:
        """
        Get upcoming dividend information

        Returns:
            Dict with upcoming dividend details
        """
        try:
            info = self.ticker.info

            dividend_data = {
                'has_upcoming_dividend': False,
                'ex_dividend_date': None,
                'dividend_rate': info.get('dividendRate', 0),
                'dividend_yield': info.get('dividendYield', 0) * 100 if info.get('dividendYield') else 0,
                'payout_ratio': info.get('payoutRatio', 0) * 100 if info.get('payoutRatio') else 0,
                'five_year_avg_yield': info.get('fiveYearAvgDividendYield', 0),
                'last_dividend_value': info.get('lastDividendValue', 0),
                'last_dividend_date': info.get('lastDividendDate', None)
            }

            # Check if ex-dividend date exists and is in the future
            ex_div_date = info.get('exDividendDate')
            if ex_div_date:
                ex_div_datetime = datetime.fromtimestamp(ex_div_date)
                if ex_div_datetime > datetime.now():
                    dividend_data['has_upcoming_dividend'] = True
                    dividend_data['ex_dividend_date'] = ex_div_datetime.strftime('%Y-%m-%d')

            return dividend_data

        except Exception as e:
            print(f"Error fetching upcoming dividends: {e}")
            return {'has_upcoming_dividend': False}

    def calculate_dividend_metrics(self, current_price: float) -> Dict:
        """
        Calculate dividend-related metrics

        Args:
            current_price: Current stock price

        Returns:
            Dict with dividend metrics
        """
        dividends_df = self.get_dividends(period='5y')

        if dividends_df.empty:
            return {
                'total_dividends_5y': 0,
                'avg_dividend_per_year': 0,
                'dividend_growth_rate': 0,
                'current_yield': 0,
                'payout_consistency': 'No dividend history'
            }

        # Calculate metrics
        total_dividends = dividends_df['Dividend'].sum()
        years = (dividends_df['Date'].max() - dividends_df['Date'].min()).days / 365.25
        avg_dividend = total_dividends / max(years, 1)

        # Calculate growth rate
        dividends_by_year = dividends_df.copy()
        dividends_by_year['Year'] = dividends_by_year['Date'].dt.year
        yearly_dividends = dividends_by_year.groupby('Year')['Dividend'].sum()

        if len(yearly_dividends) >= 2:
            growth_rate = ((yearly_dividends.iloc[-1] / yearly_dividends.iloc[0]) ** (1 / (len(yearly_dividends) - 1)) - 1) * 100
        else:
            growth_rate = 0

        # Current yield
        last_year_dividend = yearly_dividends.iloc[-1] if len(yearly_dividends) > 0 else 0
        current_yield = (last_year_dividend / current_price) * 100 if current_price > 0 else 0

        # Consistency
        years_with_dividends = len(yearly_dividends)
        if years_with_dividends >= 5:
            consistency = 'Excellent (5+ years consecutive)'
        elif years_with_dividends >= 3:
            consistency = 'Good (3+ years consecutive)'
        elif years_with_dividends >= 1:
            consistency = 'Moderate (1-2 years)'
        else:
            consistency = 'No recent dividends'

        return {
            'total_dividends_5y': total_dividends,
            'avg_dividend_per_year': avg_dividend,
            'dividend_growth_rate': growth_rate,
            'current_yield': current_yield,
            'payout_consistency': consistency,
            'years_with_dividends': years_with_dividends
        }

    def get_rights_issues(self) -> List[Dict]:
        """
        Get rights issues information

        Note: This requires scraping from IDX or company announcements
        Yahoo Finance doesn't provide this data directly

        Returns:
            List of rights issues (empty for now, requires scraping)
        """
        # Placeholder for rights issues
        # Would need to scrape from idx.co.id or company IR pages
        return []

    def get_bonus_shares(self) -> List[Dict]:
        """
        Get bonus shares information

        Returns:
            List of bonus shares (inferred from splits where ratio > 1)
        """
        splits_df = self.get_stock_splits()

        if splits_df.empty:
            return []

        # Bonus shares typically show as splits > 1
        # e.g., 2:1 split could be 1:1 bonus
        bonus_shares = []

        for _, row in splits_df.iterrows():
            ratio = row['Split_Ratio']
            if ratio > 1:
                bonus_shares.append({
                    'date': row['Date'].strftime('%Y-%m-%d'),
                    'ratio': ratio,
                    'description': row['Description'],
                    'type': 'Bonus Share (inferred)'
                })

        return bonus_shares

    def get_all_corporate_actions(self, current_price: Optional[float] = None) -> Dict:
        """
        Get comprehensive corporate actions summary

        Args:
            current_price: Current stock price (optional)

        Returns:
            Dict with all corporate actions
        """
        # Fetch all data
        dividends = self.get_dividends()
        splits = self.get_stock_splits()
        upcoming_div = self.get_upcoming_dividends()
        bonus = self.get_bonus_shares()
        rights = self.get_rights_issues()

        # Calculate metrics if price provided
        div_metrics = {}
        if current_price:
            div_metrics = self.calculate_dividend_metrics(current_price)

        # Build summary
        summary = {
            'stock_code': self.stock_code,
            'as_of_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'dividends': {
                'history': dividends.to_dict('records') if not dividends.empty else [],
                'count': len(dividends),
                'latest': dividends.iloc[0].to_dict() if not dividends.empty else None,
                'upcoming': upcoming_div,
                'metrics': div_metrics
            },
            'stock_splits': {
                'history': splits.to_dict('records') if not splits.empty else [],
                'count': len(splits),
                'latest': splits.iloc[0].to_dict() if not splits.empty else None
            },
            'bonus_shares': {
                'history': bonus,
                'count': len(bonus)
            },
            'rights_issues': {
                'history': rights,
                'count': len(rights),
                'note': 'Requires IDX scraping for complete data'
            },
            'summary': {
                'total_actions': len(dividends) + len(splits) + len(bonus) + len(rights),
                'has_dividends': len(dividends) > 0,
                'has_splits': len(splits) > 0,
                'has_upcoming_dividend': upcoming_div.get('has_upcoming_dividend', False),
                'dividend_stock': len(dividends) >= 3  # Paid dividends 3+ times
            }
        }

        return summary

    def _get_cutoff_date(self, period: str) -> datetime:
        """Get cutoff date for period"""
        now = datetime.now()

        period_map = {
            '1y': 365,
            '2y': 730,
            '5y': 1825,
            '10y': 3650,
            'max': 36500  # 100 years
        }

        days = period_map.get(period, 1825)
        return now - timedelta(days=days)

    def _format_split_ratio(self, ratio: float) -> str:
        """Format split ratio for display"""
        if ratio > 1:
            return f"{ratio}:1 Split (Stock increased {ratio}x)"
        elif ratio < 1:
            return f"1:{int(1/ratio)} Reverse Split (Stock consolidated)"
        else:
            return "No split"

    def get_impact_analysis(self, current_price: float, position_shares: int = 0) -> Dict:
        """
        Analyze impact of upcoming corporate actions on holdings

        Args:
            current_price: Current stock price
            position_shares: Number of shares held (optional)

        Returns:
            Dict with impact analysis
        """
        upcoming_div = self.get_upcoming_dividends()
        splits = self.get_stock_splits(period='1y')

        impact = {
            'has_impact': False,
            'upcoming_events': [],
            'estimated_dividend_income': 0,
            'post_split_shares': position_shares,
            'post_split_price': current_price
        }

        # Dividend impact
        if upcoming_div.get('has_upcoming_dividend'):
            div_per_share = upcoming_div.get('dividend_rate', 0)
            estimated_income = div_per_share * position_shares if position_shares > 0 else 0

            impact['has_impact'] = True
            impact['upcoming_events'].append({
                'type': 'Dividend',
                'ex_date': upcoming_div.get('ex_dividend_date'),
                'amount_per_share': div_per_share,
                'estimated_income': estimated_income,
                'yield': upcoming_div.get('dividend_yield', 0)
            })
            impact['estimated_dividend_income'] = estimated_income

        # Recent splits (check last year)
        if not splits.empty and position_shares > 0:
            latest_split = splits.iloc[0]
            split_ratio = latest_split['Split_Ratio']

            impact['has_impact'] = True
            impact['post_split_shares'] = int(position_shares * split_ratio)
            impact['post_split_price'] = current_price / split_ratio
            impact['upcoming_events'].append({
                'type': 'Stock Split',
                'date': latest_split['Date'].strftime('%Y-%m-%d'),
                'ratio': split_ratio,
                'description': latest_split['Description'],
                'shares_before': position_shares,
                'shares_after': impact['post_split_shares'],
                'price_before': current_price,
                'price_after': impact['post_split_price']
            })

        return impact


def format_corporate_actions_summary(actions: Dict) -> str:
    """
    Format corporate actions for display

    Args:
        actions: Dict from get_all_corporate_actions()

    Returns:
        Formatted string
    """
    lines = []

    # Header
    lines.append(f"**Corporate Actions: {actions['stock_code']}**")
    lines.append(f"As of: {actions['as_of_date']}")
    lines.append("")

    # Summary
    summary = actions['summary']
    lines.append("### Summary")
    lines.append(f"📊 Total Actions: {summary['total_actions']}")
    lines.append(f"💰 Dividend Stock: {'Yes ✅' if summary['dividend_stock'] else 'No ❌'}")
    lines.append(f"📈 Has Upcoming Dividend: {'Yes 🎁' if summary['has_upcoming_dividend'] else 'No'}")
    lines.append("")

    # Dividends
    div_data = actions['dividends']
    if div_data['count'] > 0:
        lines.append("### Dividend History")
        lines.append(f"Total Payments: {div_data['count']}")

        if div_data['latest']:
            latest = div_data['latest']
            lines.append(f"Latest: {latest['Date'][:10]} - Rp {latest['Dividend']:,.0f}")

        if div_data['metrics']:
            metrics = div_data['metrics']
            lines.append(f"Current Yield: {metrics['current_yield']:.2f}%")
            lines.append(f"5Y Avg Dividend: Rp {metrics['avg_dividend_per_year']:,.0f}/year")
            lines.append(f"Growth Rate: {metrics['dividend_growth_rate']:+.1f}%/year")
            lines.append(f"Consistency: {metrics['payout_consistency']}")

        lines.append("")

    # Splits
    split_data = actions['stock_splits']
    if split_data['count'] > 0:
        lines.append("### Stock Splits")
        lines.append(f"Total Splits: {split_data['count']}")

        if split_data['latest']:
            latest = split_data['latest']
            lines.append(f"Latest: {latest['Date'][:10]} - {latest['Description']}")

        lines.append("")

    return "\n".join(lines)

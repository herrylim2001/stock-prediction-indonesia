"""
Multibagger Stock Tracker for Daily Trading
Tracks favorite stocks for daily basis trading with quick signals and comparisons
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf


class MultibaggerTracker:
    """
    Track and analyze favorite stocks for daily trading
    """

    def __init__(self, stock_codes, stock_info):
        """
        Initialize multibagger tracker

        Args:
            stock_codes: List of stock codes (e.g., ['BBCA', 'BBRI'])
            stock_info: Dict of stock information from STOCKS
        """
        self.stock_codes = stock_codes
        self.stock_info = stock_info
        self.data = {}
        self.signals = {}

    def fetch_all_data(self, period='5d'):
        """
        Fetch data for all multibagger stocks

        Args:
            period: Period for historical data (default: 5d for daily trading)

        Returns:
            dict: Data for all stocks
        """
        for code in self.stock_codes:
            ticker = f"{code}.JK"
            try:
                df = yf.download(ticker, period=period, progress=False)
                if not df.empty:
                    df.columns = [col.lower() for col in df.columns]
                    df = df.rename(columns={'adj close': 'adj_close'})
                    self.data[code] = df
            except Exception as e:
                print(f"Error fetching {code}: {e}")
                self.data[code] = None

        return self.data

    def calculate_daily_metrics(self, code):
        """
        Calculate key metrics for daily trading

        Args:
            code: Stock code

        Returns:
            dict: Daily trading metrics
        """
        df = self.data.get(code)

        if df is None or df.empty:
            return None

        # Get today's and yesterday's data
        today = df.iloc[-1] if len(df) > 0 else None
        yesterday = df.iloc[-2] if len(df) > 1 else None

        if today is None:
            return None

        # Calculate metrics
        current_price = today['close']
        prev_close = yesterday['close'] if yesterday is not None else current_price

        # Daily change
        daily_change = current_price - prev_close
        daily_change_pct = (daily_change / prev_close * 100) if prev_close > 0 else 0

        # Volume analysis
        current_volume = today['volume']
        avg_volume = df['volume'].tail(5).mean() if len(df) >= 5 else current_volume
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1

        # Intraday metrics
        day_high = today['high']
        day_low = today['low']
        day_open = today['open']
        day_range = day_high - day_low
        day_range_pct = (day_range / day_low * 100) if day_low > 0 else 0

        # Position in day's range
        if day_range > 0:
            position_in_range = (current_price - day_low) / day_range
        else:
            position_in_range = 0.5

        # Momentum (5-day)
        if len(df) >= 5:
            five_days_ago = df['close'].iloc[-5]
            momentum_5d = (current_price - five_days_ago) / five_days_ago * 100
        else:
            momentum_5d = 0

        return {
            'code': code,
            'name': self.stock_info[code]['name'],
            'sector': self.stock_info[code]['sector'],
            'current_price': current_price,
            'prev_close': prev_close,
            'daily_change': daily_change,
            'daily_change_pct': daily_change_pct,
            'day_open': day_open,
            'day_high': day_high,
            'day_low': day_low,
            'day_range': day_range,
            'day_range_pct': day_range_pct,
            'position_in_range': position_in_range,
            'current_volume': current_volume,
            'avg_volume': avg_volume,
            'volume_ratio': volume_ratio,
            'momentum_5d': momentum_5d,
            'timestamp': datetime.now()
        }

    def generate_trading_signal(self, code):
        """
        Generate trading signal for daily trading

        Args:
            code: Stock code

        Returns:
            dict: Trading signal and reasoning
        """
        df = self.data.get(code)
        metrics = self.calculate_daily_metrics(code)

        if df is None or metrics is None:
            return {
                'signal': 'NO_DATA',
                'strength': 0,
                'reasons': ['Insufficient data']
            }

        # Calculate technical indicators
        close_prices = df['close'].values
        volumes = df['volume'].values

        # Simple moving averages
        if len(close_prices) >= 5:
            sma_5 = np.mean(close_prices[-5:])
            current_price = close_prices[-1]

            # RSI-like momentum indicator
            gains = []
            losses = []
            for i in range(1, min(14, len(close_prices))):
                change = close_prices[i] - close_prices[i-1]
                if change > 0:
                    gains.append(change)
                else:
                    losses.append(abs(change))

            avg_gain = np.mean(gains) if gains else 0
            avg_loss = np.mean(losses) if losses else 0
            rs = avg_gain / avg_loss if avg_loss > 0 else 100
            rsi = 100 - (100 / (1 + rs))

        else:
            sma_5 = metrics['current_price']
            current_price = metrics['current_price']
            rsi = 50

        # Signal generation logic
        signal_score = 0
        reasons = []

        # 1. Price vs SMA (20 points)
        if current_price > sma_5:
            signal_score += 20
            reasons.append("Price above 5-day average (Bullish)")
        else:
            signal_score -= 20
            reasons.append("Price below 5-day average (Bearish)")

        # 2. Daily momentum (20 points)
        if metrics['daily_change_pct'] > 1:
            signal_score += 20
            reasons.append(f"Strong daily gain (+{metrics['daily_change_pct']:.1f}%)")
        elif metrics['daily_change_pct'] > 0:
            signal_score += 10
            reasons.append(f"Positive daily change (+{metrics['daily_change_pct']:.1f}%)")
        elif metrics['daily_change_pct'] < -1:
            signal_score -= 20
            reasons.append(f"Strong daily loss ({metrics['daily_change_pct']:.1f}%)")
        else:
            signal_score -= 10
            reasons.append(f"Negative daily change ({metrics['daily_change_pct']:.1f}%)")

        # 3. Volume analysis (15 points)
        if metrics['volume_ratio'] > 1.5:
            signal_score += 15
            reasons.append(f"High volume ({metrics['volume_ratio']:.1f}x avg)")
        elif metrics['volume_ratio'] > 1.2:
            signal_score += 10
            reasons.append(f"Above average volume ({metrics['volume_ratio']:.1f}x)")
        elif metrics['volume_ratio'] < 0.8:
            signal_score -= 5
            reasons.append(f"Low volume ({metrics['volume_ratio']:.1f}x avg)")

        # 4. RSI (15 points)
        if rsi < 30:
            signal_score += 15
            reasons.append(f"Oversold (RSI: {rsi:.0f})")
        elif rsi > 70:
            signal_score -= 15
            reasons.append(f"Overbought (RSI: {rsi:.0f})")

        # 5. Position in day's range (15 points)
        if metrics['position_in_range'] > 0.8:
            signal_score += 15
            reasons.append("Trading near day's high")
        elif metrics['position_in_range'] < 0.2:
            signal_score -= 15
            reasons.append("Trading near day's low")

        # 6. 5-day momentum (15 points)
        if metrics['momentum_5d'] > 3:
            signal_score += 15
            reasons.append(f"Strong 5-day momentum (+{metrics['momentum_5d']:.1f}%)")
        elif metrics['momentum_5d'] < -3:
            signal_score -= 15
            reasons.append(f"Weak 5-day momentum ({metrics['momentum_5d']:.1f}%)")

        # Determine signal
        if signal_score >= 40:
            signal = 'STRONG_BUY'
            color = 'success'
        elif signal_score >= 20:
            signal = 'BUY'
            color = 'success'
        elif signal_score >= -20:
            signal = 'HOLD'
            color = 'warning'
        elif signal_score >= -40:
            signal = 'SELL'
            color = 'error'
        else:
            signal = 'STRONG_SELL'
            color = 'error'

        return {
            'signal': signal,
            'strength': abs(signal_score),
            'score': signal_score,
            'color': color,
            'reasons': reasons,
            'rsi': rsi,
            'metrics': metrics
        }

    def get_all_signals(self):
        """
        Get trading signals for all multibagger stocks

        Returns:
            dict: Signals for all stocks
        """
        for code in self.stock_codes:
            self.signals[code] = self.generate_trading_signal(code)

        return self.signals

    def get_comparison_table(self):
        """
        Get comparison table for all multibagger stocks

        Returns:
            pd.DataFrame: Comparison table
        """
        comparison_data = []

        for code in self.stock_codes:
            metrics = self.calculate_daily_metrics(code)
            signal = self.signals.get(code, self.generate_trading_signal(code))

            if metrics:
                comparison_data.append({
                    'Code': code,
                    'Name': metrics['name'],
                    'Sector': metrics['sector'],
                    'Price': metrics['current_price'],
                    'Change': metrics['daily_change'],
                    'Change %': metrics['daily_change_pct'],
                    '5D Momentum %': metrics['momentum_5d'],
                    'Volume Ratio': metrics['volume_ratio'],
                    'Signal': signal['signal'],
                    'Strength': signal['strength'],
                    'RSI': signal['rsi']
                })

        if comparison_data:
            df = pd.DataFrame(comparison_data)
            # Sort by signal strength (descending)
            df = df.sort_values('Strength', ascending=False)
            return df
        else:
            return pd.DataFrame()

    def get_top_opportunities(self, top_n=3):
        """
        Get top trading opportunities

        Args:
            top_n: Number of top stocks to return

        Returns:
            list: Top opportunities
        """
        # Get all signals
        all_signals = self.get_all_signals()

        # Filter for buy signals only
        buy_signals = {
            code: sig for code, sig in all_signals.items()
            if sig['signal'] in ['BUY', 'STRONG_BUY']
        }

        # Sort by strength
        sorted_signals = sorted(
            buy_signals.items(),
            key=lambda x: x[1]['strength'],
            reverse=True
        )

        return sorted_signals[:top_n]

    def simulate_portfolio(self, capital=100000000, allocation='equal'):
        """
        Simulate portfolio with multibagger stocks

        Args:
            capital: Total capital (default: 100 juta)
            allocation: 'equal' or 'weighted'

        Returns:
            dict: Portfolio simulation
        """
        if allocation == 'equal':
            # Equal allocation
            per_stock = capital / len(self.stock_codes)
            allocations = {code: per_stock for code in self.stock_codes}

        else:
            # Weighted by signal strength
            signals = self.get_all_signals()
            total_strength = sum(sig['strength'] for sig in signals.values())

            if total_strength > 0:
                allocations = {
                    code: capital * (sig['strength'] / total_strength)
                    for code, sig in signals.items()
                }
            else:
                # Fallback to equal
                per_stock = capital / len(self.stock_codes)
                allocations = {code: per_stock for code in self.stock_codes}

        # Calculate shares and positions
        portfolio = []
        total_value = 0

        for code in self.stock_codes:
            metrics = self.calculate_daily_metrics(code)
            if metrics:
                allocation = allocations[code]
                shares = int(allocation / (metrics['current_price'] * 100)) * 100  # Round to lot (100 shares)
                position_value = shares * metrics['current_price']

                total_value += position_value

                portfolio.append({
                    'code': code,
                    'name': metrics['name'],
                    'allocation': allocation,
                    'shares': shares,
                    'price': metrics['current_price'],
                    'position_value': position_value,
                    'daily_pl': shares * metrics['daily_change'],
                    'daily_pl_pct': metrics['daily_change_pct']
                })

        return {
            'capital': capital,
            'invested': total_value,
            'cash': capital - total_value,
            'positions': portfolio,
            'total_daily_pl': sum(p['daily_pl'] for p in portfolio),
            'total_daily_pl_pct': (sum(p['daily_pl'] for p in portfolio) / total_value * 100) if total_value > 0 else 0
        }


def get_multibagger_analysis(stock_codes, stock_info, capital=100000000):
    """
    Convenience function to get complete multibagger analysis

    Args:
        stock_codes: List of stock codes
        stock_info: Stock information dict
        capital: Portfolio capital

    Returns:
        dict: Complete analysis
    """
    tracker = MultibaggerTracker(stock_codes, stock_info)

    # Fetch data
    tracker.fetch_all_data(period='10d')

    # Get signals
    signals = tracker.get_all_signals()

    # Get comparison
    comparison = tracker.get_comparison_table()

    # Get top opportunities
    opportunities = tracker.get_top_opportunities(top_n=3)

    # Simulate portfolio
    portfolio = tracker.simulate_portfolio(capital=capital, allocation='equal')

    return {
        'signals': signals,
        'comparison': comparison,
        'opportunities': opportunities,
        'portfolio': portfolio,
        'tracker': tracker
    }

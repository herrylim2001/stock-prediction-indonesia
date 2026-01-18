"""
Backtesting Framework
=====================

Test prediction system against historical data to measure actual performance.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf


class BacktestEngine:
    """Engine for backtesting trading strategies"""

    def __init__(self, initial_capital=100_000_000):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.positions = {}
        self.trade_history = []
        self.equity_curve = []

    def execute_trade(self, stock_code, action, price, shares, date):
        """Execute a buy or sell trade"""
        if action == "BUY":
            cost = price * shares
            if cost <= self.capital:
                self.capital -= cost
                self.positions[stock_code] = {
                    'shares': shares,
                    'entry_price': price,
                    'entry_date': date
                }
                self.trade_history.append({
                    'date': date,
                    'stock': stock_code,
                    'action': 'BUY',
                    'price': price,
                    'shares': shares,
                    'cost': cost
                })
                return True
        elif action == "SELL":
            if stock_code in self.positions:
                position = self.positions[stock_code]
                proceeds = price * position['shares']
                profit = proceeds - (position['entry_price'] * position['shares'])

                self.capital += proceeds
                self.trade_history.append({
                    'date': date,
                    'stock': stock_code,
                    'action': 'SELL',
                    'price': price,
                    'shares': position['shares'],
                    'proceeds': proceeds,
                    'profit': profit,
                    'profit_pct': (profit / (position['entry_price'] * position['shares'])) * 100
                })
                del self.positions[stock_code]
                return True
        return False

    def get_portfolio_value(self, current_prices):
        """Calculate current portfolio value"""
        cash = self.capital
        stock_value = sum(
            pos['shares'] * current_prices.get(stock, pos['entry_price'])
            for stock, pos in self.positions.items()
        )
        return cash + stock_value

    def calculate_metrics(self):
        """Calculate performance metrics"""
        if not self.trade_history:
            return {}

        trades_df = pd.DataFrame(self.trade_history)
        sell_trades = trades_df[trades_df['action'] == 'SELL']

        if len(sell_trades) == 0:
            return {'total_trades': 0}

        metrics = {
            'total_trades': len(sell_trades),
            'winning_trades': len(sell_trades[sell_trades['profit'] > 0]),
            'losing_trades': len(sell_trades[sell_trades['profit'] < 0]),
            'total_profit': sell_trades['profit'].sum(),
            'avg_profit': sell_trades['profit'].mean(),
            'avg_profit_pct': sell_trades['profit_pct'].mean(),
            'win_rate': len(sell_trades[sell_trades['profit'] > 0]) / len(sell_trades) * 100,
            'max_profit': sell_trades['profit'].max(),
            'max_loss': sell_trades['profit'].min(),
            'final_capital': self.capital,
            'total_return': ((self.capital - self.initial_capital) / self.initial_capital) * 100
        }

        return metrics


class TestBacktesting:
    """Test backtesting functionality"""

    @pytest.fixture
    def backtest_engine(self):
        """Create backtest engine"""
        return BacktestEngine(initial_capital=100_000_000)

    def test_engine_initialization(self, backtest_engine):
        """Test backtest engine initialization"""
        assert backtest_engine.initial_capital == 100_000_000
        assert backtest_engine.capital == 100_000_000
        assert len(backtest_engine.positions) == 0
        assert len(backtest_engine.trade_history) == 0

    def test_buy_trade(self, backtest_engine):
        """Test buying stock"""
        success = backtest_engine.execute_trade(
            stock_code='BBCA',
            action='BUY',
            price=10_000,
            shares=1000,
            date=datetime(2024, 1, 1)
        )

        assert success is True, "Buy trade should succeed"
        assert backtest_engine.capital == 90_000_000, "Capital should decrease"
        assert 'BBCA' in backtest_engine.positions, "Position should be created"
        assert backtest_engine.positions['BBCA']['shares'] == 1000

    def test_sell_trade(self, backtest_engine):
        """Test selling stock"""
        # First buy
        backtest_engine.execute_trade('BBCA', 'BUY', 10_000, 1000, datetime(2024, 1, 1))

        # Then sell at profit
        success = backtest_engine.execute_trade(
            stock_code='BBCA',
            action='SELL',
            price=10_500,
            shares=1000,
            date=datetime(2024, 1, 10)
        )

        assert success is True, "Sell trade should succeed"
        assert backtest_engine.capital == 100_500_000, "Capital should increase with profit"
        assert 'BBCA' not in backtest_engine.positions, "Position should be closed"

    def test_insufficient_capital(self, backtest_engine):
        """Test trade rejection due to insufficient capital"""
        success = backtest_engine.execute_trade(
            stock_code='BBCA',
            action='BUY',
            price=10_000,
            shares=20_000,  # Requires 200M but only have 100M
            date=datetime(2024, 1, 1)
        )

        assert success is False, "Trade should fail due to insufficient capital"
        assert backtest_engine.capital == 100_000_000, "Capital should remain unchanged"

    def test_portfolio_value(self, backtest_engine):
        """Test portfolio value calculation"""
        # Buy 2 stocks
        backtest_engine.execute_trade('BBCA', 'BUY', 10_000, 1000, datetime(2024, 1, 1))
        backtest_engine.execute_trade('BBRI', 'BUY', 5_000, 2000, datetime(2024, 1, 1))

        # Calculate portfolio value with current prices
        current_prices = {'BBCA': 10_500, 'BBRI': 5_200}
        portfolio_value = backtest_engine.get_portfolio_value(current_prices)

        # Cash: 100M - 10M - 10M = 80M
        # Stocks: (1000 * 10,500) + (2000 * 5,200) = 10.5M + 10.4M = 20.9M
        # Total: 100.9M
        expected_value = 80_000_000 + 10_500_000 + 10_400_000

        assert portfolio_value == expected_value, "Portfolio value should be calculated correctly"

    def test_performance_metrics(self, backtest_engine):
        """Test performance metrics calculation"""
        # Execute some trades
        backtest_engine.execute_trade('BBCA', 'BUY', 10_000, 1000, datetime(2024, 1, 1))
        backtest_engine.execute_trade('BBCA', 'SELL', 10_500, 1000, datetime(2024, 1, 10))

        backtest_engine.execute_trade('BBRI', 'BUY', 5_000, 2000, datetime(2024, 1, 15))
        backtest_engine.execute_trade('BBRI', 'SELL', 4_900, 2000, datetime(2024, 1, 20))

        metrics = backtest_engine.calculate_metrics()

        assert metrics['total_trades'] == 2, "Should have 2 completed trades"
        assert metrics['winning_trades'] == 1, "Should have 1 winning trade"
        assert metrics['losing_trades'] == 1, "Should have 1 losing trade"
        assert metrics['win_rate'] == 50.0, "Win rate should be 50%"


class TestBacktestScenarios:
    """Test various backtesting scenarios"""

    def test_simple_momentum_strategy(self):
        """Test simple momentum buy and hold strategy"""
        engine = BacktestEngine(initial_capital=50_000_000)

        # Simulate 5-day trading
        prices = [10_000, 10_100, 10_300, 10_200, 10_500]
        dates = [datetime(2024, 1, i) for i in range(1, 6)]

        # Buy on day 1
        engine.execute_trade('TEST', 'BUY', prices[0], 1000, dates[0])

        # Sell on day 5
        engine.execute_trade('TEST', 'SELL', prices[4], 1000, dates[4])

        metrics = engine.calculate_metrics()

        assert metrics['total_trades'] == 1
        assert metrics['total_profit'] == 500_000, "Profit should be 500k"
        assert metrics['avg_profit_pct'] == 5.0, "Return should be 5%"

    def test_stop_loss_scenario(self):
        """Test stop loss execution"""
        engine = BacktestEngine(initial_capital=50_000_000)

        entry_price = 10_000
        stop_loss = 9_800  # -2%

        # Buy
        engine.execute_trade('TEST', 'BUY', entry_price, 1000, datetime(2024, 1, 1))

        # Price drops to stop loss
        engine.execute_trade('TEST', 'SELL', stop_loss, 1000, datetime(2024, 1, 2))

        metrics = engine.calculate_metrics()

        assert metrics['total_profit'] == -200_000, "Loss should be 200k"
        assert metrics['avg_profit_pct'] == -2.0, "Loss should be -2%"

    def test_take_profit_scenario(self):
        """Test take profit execution"""
        engine = BacktestEngine(initial_capital=50_000_000)

        entry_price = 10_000
        target = 10_400  # +4%

        # Buy
        engine.execute_trade('TEST', 'BUY', entry_price, 1000, datetime(2024, 1, 1))

        # Price reaches target
        engine.execute_trade('TEST', 'SELL', target, 1000, datetime(2024, 1, 5))

        metrics = engine.calculate_metrics()

        assert metrics['total_profit'] == 400_000, "Profit should be 400k"
        assert metrics['avg_profit_pct'] == 4.0, "Return should be 4%"

    def test_multiple_stocks_portfolio(self):
        """Test portfolio with multiple stocks"""
        engine = BacktestEngine(initial_capital=100_000_000)

        # Buy 3 different stocks
        stocks = [
            ('BBCA', 10_000, 1000),
            ('BBRI', 5_000, 2000),
            ('TLKM', 4_000, 2500)
        ]

        for stock, price, shares in stocks:
            engine.execute_trade(stock, 'BUY', price, shares, datetime(2024, 1, 1))

        # Check diversification
        assert len(engine.positions) == 3, "Should have 3 positions"

        # Sell all with different outcomes
        engine.execute_trade('BBCA', 'SELL', 10_500, 1000, datetime(2024, 1, 10))  # +5%
        engine.execute_trade('BBRI', 'SELL', 4_900, 2000, datetime(2024, 1, 10))   # -2%
        engine.execute_trade('TLKM', 'SELL', 4_100, 2500, datetime(2024, 1, 10))   # +2.5%

        metrics = engine.calculate_metrics()

        assert metrics['total_trades'] == 3
        assert metrics['winning_trades'] == 2
        assert metrics['win_rate'] > 50.0, "Win rate should be > 50%"


class TestRealDataBacktest:
    """Test backtesting with real market data"""

    @pytest.mark.skipif(True, reason="Requires live data connection")
    def test_backtest_with_yfinance(self):
        """Test backtesting with real Yahoo Finance data"""
        # This test requires internet connection
        # Download historical data
        ticker = yf.Ticker("BBCA.JK")
        df = ticker.history(period="1mo")

        assert len(df) > 0, "Should fetch historical data"

        # Simple strategy: Buy if daily gain > 1%, sell next day
        engine = BacktestEngine(initial_capital=100_000_000)

        for i in range(len(df) - 1):
            current_price = df['Close'].iloc[i]
            next_price = df['Close'].iloc[i + 1]
            date = df.index[i]

            daily_change = ((current_price - df['Close'].iloc[i-1]) / df['Close'].iloc[i-1] * 100) if i > 0 else 0

            # Buy signal: daily gain > 1%
            if daily_change > 1 and 'BBCA' not in engine.positions:
                shares = (engine.capital * 0.2) // current_price  # Use 20% of capital
                if shares > 0:
                    engine.execute_trade('BBCA', 'BUY', current_price, int(shares), date)

            # Sell next day
            elif 'BBCA' in engine.positions:
                shares = engine.positions['BBCA']['shares']
                engine.execute_trade('BBCA', 'SELL', current_price, shares, date)

        metrics = engine.calculate_metrics()

        # Strategy should have executed some trades
        assert metrics.get('total_trades', 0) > 0, "Should execute at least one trade"


class TestPerformanceAnalysis:
    """Test performance analysis functions"""

    def test_sharpe_ratio_calculation(self):
        """Test Sharpe ratio calculation"""
        # Sample returns
        returns = np.array([0.02, -0.01, 0.03, 0.01, -0.005, 0.025, 0.015])

        # Sharpe = (mean_return - risk_free_rate) / std_return
        risk_free_rate = 0.05 / 252  # 5% annual, daily
        mean_return = returns.mean()
        std_return = returns.std()

        sharpe = (mean_return - risk_free_rate) / std_return if std_return > 0 else 0

        assert sharpe != 0, "Sharpe ratio should be calculated"

    def test_max_drawdown_calculation(self):
        """Test maximum drawdown calculation"""
        # Sample equity curve
        equity = np.array([100, 105, 103, 110, 108, 95, 98, 105])

        # Calculate drawdown
        running_max = np.maximum.accumulate(equity)
        drawdown = (equity - running_max) / running_max * 100

        max_drawdown = drawdown.min()

        assert max_drawdown < 0, "Max drawdown should be negative"
        assert max_drawdown >= -100, "Max drawdown should be >= -100%"

    def test_profit_factor(self):
        """Test profit factor calculation"""
        profits = [500, 300, 200, -100, -150, 400, -50]

        gross_profit = sum(p for p in profits if p > 0)
        gross_loss = abs(sum(p for p in profits if p < 0))

        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')

        assert profit_factor > 0, "Profit factor should be positive"
        # Profit factor > 1 means profitable strategy
        assert profit_factor == 1400 / 300, "Should calculate correct profit factor"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

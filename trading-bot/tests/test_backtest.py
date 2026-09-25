import pandas as pd
import pytest

from tradingbot.backtest import run_backtest
from tradingbot.risk import RiskManager
from tradingbot.strategies import SMACrossover
from tradingbot.strategies.base import Strategy


class AlwaysLong(Strategy):
    name = "always_long"

    def generate_signals(self, df):
        return pd.Series(1, index=df.index)


class NeverTrade(Strategy):
    name = "never"

    def generate_signals(self, df):
        return pd.Series(0, index=df.index)


def test_no_trades_keeps_capital(random_walk):
    result = run_backtest(random_walk, NeverTrade(), initial_capital=1000)
    assert (result.equity == 1000).all()
    assert result.metrics()["trades"] == 0


def test_always_long_tracks_price_minus_fees(uptrend):
    result = run_backtest(uptrend, AlwaysLong(), initial_capital=1000, fee_rate=0.0)
    # entra en la apertura de la vela 1 y valora al cierre de la última
    expected = 1000 * uptrend["close"].iloc[-1] / uptrend["open"].iloc[1]
    assert result.equity.iloc[-1] == pytest.approx(expected)


def test_fees_reduce_equity(uptrend):
    free = run_backtest(uptrend, AlwaysLong(), fee_rate=0.0).equity.iloc[-1]
    paid = run_backtest(uptrend, AlwaysLong(), fee_rate=0.01).equity.iloc[-1]
    assert paid < free


def test_stop_loss_limits_loss():
    import numpy as np
    from conftest import make_ohlcv

    df = make_ohlcv(np.linspace(100, 50, 100))  # caída continua
    risk = RiskManager(stop_loss_pct=0.05)
    result = run_backtest(df, AlwaysLong(), fee_rate=0.0, risk=risk)
    assert result.metrics()["total_return_pct"] == pytest.approx(-5, abs=0.5)
    assert result.metrics()["trades"] == 1  # no reentra tras el stop


def test_metrics_keys(random_walk):
    m = run_backtest(random_walk, SMACrossover(5, 20)).metrics()
    assert {"final_equity", "total_return_pct", "max_drawdown_pct", "sharpe", "trades",
            "win_rate_pct"} <= m.keys()
    assert m["max_drawdown_pct"] <= 0

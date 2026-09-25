"""Motor de backtesting (solo posiciones largas)."""

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from .risk import RiskManager
from .strategies.base import Strategy


@dataclass
class Trade:
    entry_time: pd.Timestamp
    entry_price: float
    exit_time: pd.Timestamp | None = None
    exit_price: float | None = None
    qty: float = 0.0
    pnl: float = 0.0


@dataclass
class BacktestResult:
    equity: pd.Series
    trades: list[Trade] = field(default_factory=list)

    def metrics(self, periods_per_year: int = 24 * 365) -> dict[str, float]:
        eq = self.equity
        returns = eq.pct_change().dropna()
        total_return = eq.iloc[-1] / eq.iloc[0] - 1
        drawdown = eq / eq.cummax() - 1
        std = returns.std()
        sharpe = float(np.sqrt(periods_per_year) * returns.mean() / std) if std > 0 else 0.0
        closed = [t for t in self.trades if t.exit_price is not None]
        wins = [t for t in closed if t.pnl > 0]
        return {
            "final_equity": float(eq.iloc[-1]),
            "total_return_pct": float(total_return * 100),
            "max_drawdown_pct": float(drawdown.min() * 100),
            "sharpe": sharpe,
            "trades": len(closed),
            "win_rate_pct": float(len(wins) / len(closed) * 100) if closed else 0.0,
        }


def run_backtest(
    df: pd.DataFrame,
    strategy: Strategy,
    initial_capital: float = 1000.0,
    fee_rate: float = 0.001,
    risk: RiskManager | None = None,
) -> BacktestResult:
    """Simula la estrategia vela a vela.

    La señal calculada al cierre de la vela i se ejecuta al precio de apertura de la vela i+1,
    para evitar sesgo de anticipación (look-ahead bias).
    """
    risk = risk or RiskManager()
    signals = strategy.generate_signals(df).reindex(df.index).fillna(0).astype(int)

    cash = initial_capital
    trade: Trade | None = None
    trades: list[Trade] = []
    equity = []
    stopped_out = False  # tras un stop, no reentrar hasta que la señal vuelva a 0

    opens, highs, lows, closes = (df[c].to_numpy() for c in ("open", "high", "low", "close"))
    index = df.index

    for i in range(len(df)):
        prev_signal = signals.iloc[i - 1] if i > 0 else 0
        if prev_signal == 0:
            stopped_out = False

        # Ejecutar la señal de la vela anterior en la apertura de ésta
        if trade is None and prev_signal == 1 and not stopped_out:
            price = opens[i]
            qty = risk.position_size(cash, price) / (1 + fee_rate)
            cash -= qty * price * (1 + fee_rate)
            trade = Trade(entry_time=index[i], entry_price=price, qty=qty)
        elif trade is not None and prev_signal == 0:
            cash += _close(trade, index[i], opens[i], fee_rate)
            trades.append(trade)
            trade = None

        # Stop-loss / take-profit intravela
        if trade is not None:
            exit_price = risk.should_exit(trade.entry_price, lows[i], highs[i])
            if exit_price is not None:
                cash += _close(trade, index[i], exit_price, fee_rate)
                trades.append(trade)
                trade = None
                stopped_out = True

        position_value = trade.qty * closes[i] if trade else 0.0
        equity.append(cash + position_value)

    if trade is not None:  # posición abierta al final: se valora pero queda abierta
        trades.append(trade)

    return BacktestResult(equity=pd.Series(equity, index=index, name="equity"), trades=trades)


def _close(trade: Trade, time: pd.Timestamp, price: float, fee_rate: float) -> float:
    proceeds = trade.qty * price * (1 - fee_rate)
    trade.exit_time = time
    trade.exit_price = price
    trade.pnl = proceeds - trade.qty * trade.entry_price * (1 + fee_rate)
    return proceeds

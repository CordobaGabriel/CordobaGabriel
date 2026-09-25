import pandas as pd

from .base import Strategy


def rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / period, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1 / period, adjust=False).mean()
    rs = gain / loss
    return 100 - 100 / (1 + rs)


class RSIStrategy(Strategy):
    """Compra cuando el RSI cae por debajo de `oversold` y vende al superar `overbought`."""

    name = "rsi"

    def __init__(self, period: int = 14, oversold: float = 30, overbought: float = 70):
        self.period = period
        self.oversold = oversold
        self.overbought = overbought

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        values = rsi(df["close"], self.period)
        signal = pd.Series(pd.NA, index=df.index, dtype="Int64")
        signal[values < self.oversold] = 1
        signal[values > self.overbought] = 0
        return signal.ffill().fillna(0).astype(int)

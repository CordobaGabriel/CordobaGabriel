import pandas as pd

from .base import Strategy


class SMACrossover(Strategy):
    """Comprado mientras la media rápida esté por encima de la lenta."""

    name = "sma_crossover"

    def __init__(self, fast: int = 20, slow: int = 50):
        if fast >= slow:
            raise ValueError("fast debe ser menor que slow")
        self.fast = fast
        self.slow = slow

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        fast = df["close"].rolling(self.fast).mean()
        slow = df["close"].rolling(self.slow).mean()
        return (fast > slow).astype(int)

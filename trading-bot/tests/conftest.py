import numpy as np
import pandas as pd
import pytest


def make_ohlcv(close: np.ndarray) -> pd.DataFrame:
    index = pd.date_range("2024-01-01", periods=len(close), freq="h", tz="UTC")
    close = pd.Series(close, index=index, dtype=float)
    open_ = close.shift(1).fillna(close.iloc[0])
    return pd.DataFrame(
        {
            "open": open_,
            "high": np.maximum(open_, close) * 1.001,
            "low": np.minimum(open_, close) * 0.999,
            "close": close,
            "volume": 1.0,
        }
    )


@pytest.fixture
def uptrend() -> pd.DataFrame:
    return make_ohlcv(np.linspace(100, 200, 300))


@pytest.fixture
def random_walk() -> pd.DataFrame:
    rng = np.random.default_rng(42)
    return make_ohlcv(100 * np.exp(np.cumsum(rng.normal(0, 0.01, 1000))))

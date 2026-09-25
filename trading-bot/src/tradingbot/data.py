"""Descarga y carga de velas OHLCV."""

from pathlib import Path

import pandas as pd

COLUMNS = ["timestamp", "open", "high", "low", "close", "volume"]


def fetch_ohlcv(exchange: str, symbol: str, timeframe: str = "1h", limit: int = 1000) -> pd.DataFrame:
    """Descarga velas públicas de un exchange usando ccxt (no requiere API key)."""
    import ccxt

    client = getattr(ccxt, exchange)({"enableRateLimit": True})
    rows = client.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    return _to_frame(rows)


def load_csv(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    missing = set(COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"Faltan columnas en el CSV: {sorted(missing)}")
    return _to_frame(df[COLUMNS].values.tolist())


def _to_frame(rows) -> pd.DataFrame:
    df = pd.DataFrame(rows, columns=COLUMNS)
    if pd.api.types.is_numeric_dtype(df["timestamp"]):
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
    else:
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df = df.set_index("timestamp").astype(float)
    return df.sort_index()

from abc import ABC, abstractmethod

import pandas as pd


class Strategy(ABC):
    """Una estrategia recibe velas OHLCV y devuelve la posición deseada por vela.

    1 = estar comprado, 0 = estar fuera del mercado.
    La señal de la vela i solo puede usar datos hasta el cierre de la vela i.
    """

    name: str = "base"

    @abstractmethod
    def generate_signals(self, df: pd.DataFrame) -> pd.Series: ...

    def __repr__(self) -> str:
        params = ", ".join(f"{k}={v}" for k, v in vars(self).items())
        return f"{self.name}({params})"

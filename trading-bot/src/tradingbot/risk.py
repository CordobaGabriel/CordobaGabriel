"""Reglas de gestión de riesgo."""

from dataclasses import dataclass


@dataclass
class RiskManager:
    position_pct: float = 1.0
    stop_loss_pct: float | None = None
    take_profit_pct: float | None = None

    def __post_init__(self) -> None:
        if not 0 < self.position_pct <= 1:
            raise ValueError("position_pct debe estar entre 0 y 1")

    def position_size(self, capital: float, price: float) -> float:
        """Cantidad de activo a comprar con el capital disponible."""
        return capital * self.position_pct / price

    def should_exit(self, entry_price: float, low: float, high: float) -> float | None:
        """Devuelve el precio de salida si se toca stop-loss o take-profit, o None.

        Si en la misma vela se tocan ambos, se asume lo peor (stop-loss).
        """
        if self.stop_loss_pct is not None:
            stop = entry_price * (1 - self.stop_loss_pct)
            if low <= stop:
                return stop
        if self.take_profit_pct is not None:
            target = entry_price * (1 + self.take_profit_pct)
            if high >= target:
                return target
        return None

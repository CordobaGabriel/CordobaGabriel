"""Broker simulado para paper trading."""

import logging
from dataclasses import dataclass

log = logging.getLogger(__name__)


@dataclass
class PaperBroker:
    cash: float
    fee_rate: float = 0.001
    qty: float = 0.0
    entry_price: float | None = None

    @property
    def in_position(self) -> bool:
        return self.qty > 0

    def buy(self, price: float, fraction: float = 1.0) -> None:
        spend = self.cash * fraction
        qty = spend / (price * (1 + self.fee_rate))
        self.cash -= qty * price * (1 + self.fee_rate)
        self.qty += qty
        self.entry_price = price
        log.info("COMPRA %.6f @ %.2f | cash=%.2f", qty, price, self.cash)

    def sell(self, price: float) -> None:
        proceeds = self.qty * price * (1 - self.fee_rate)
        log.info("VENTA %.6f @ %.2f | +%.2f", self.qty, price, proceeds)
        self.cash += proceeds
        self.qty = 0.0
        self.entry_price = None

    def equity(self, price: float) -> float:
        return self.cash + self.qty * price

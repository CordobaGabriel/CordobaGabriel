from .base import Strategy
from .rsi import RSIStrategy
from .sma_crossover import SMACrossover

STRATEGIES: dict[str, type[Strategy]] = {
    SMACrossover.name: SMACrossover,
    RSIStrategy.name: RSIStrategy,
}


def build_strategy(cfg: dict) -> Strategy:
    name = cfg["name"]
    if name not in STRATEGIES:
        raise ValueError(f"Estrategia desconocida: {name}. Disponibles: {list(STRATEGIES)}")
    return STRATEGIES[name](**cfg.get("params", {}))


__all__ = ["STRATEGIES", "RSIStrategy", "SMACrossover", "Strategy", "build_strategy"]

import pytest

from tradingbot.strategies import RSIStrategy, SMACrossover, build_strategy


def test_sma_crossover_long_in_uptrend(uptrend):
    signals = SMACrossover(fast=5, slow=20).generate_signals(uptrend)
    assert signals.iloc[:19].sum() == 0  # sin datos suficientes para la media lenta
    assert (signals.iloc[20:] == 1).all()


def test_sma_crossover_rejects_bad_params():
    with pytest.raises(ValueError):
        SMACrossover(fast=50, slow=20)


def test_rsi_signals_are_binary(random_walk):
    signals = RSIStrategy().generate_signals(random_walk)
    assert set(signals.unique()) <= {0, 1}
    assert len(signals) == len(random_walk)


def test_build_strategy_from_config():
    s = build_strategy({"name": "sma_crossover", "params": {"fast": 3, "slow": 7}})
    assert isinstance(s, SMACrossover) and s.fast == 3


def test_build_strategy_unknown():
    with pytest.raises(ValueError):
        build_strategy({"name": "nope"})

import pytest

from tradingbot.broker import PaperBroker
from tradingbot.risk import RiskManager


def test_position_size():
    assert RiskManager(position_pct=0.5).position_size(1000, 100) == 5


def test_invalid_position_pct():
    with pytest.raises(ValueError):
        RiskManager(position_pct=1.5)


def test_should_exit():
    r = RiskManager(stop_loss_pct=0.1, take_profit_pct=0.2)
    assert r.should_exit(100, low=95, high=105) is None
    assert r.should_exit(100, low=89, high=105) == pytest.approx(90)
    assert r.should_exit(100, low=95, high=121) == pytest.approx(120)


def test_paper_broker_round_trip():
    b = PaperBroker(cash=1000, fee_rate=0.0)
    b.buy(100)
    assert b.in_position and b.cash == pytest.approx(0)
    b.sell(110)
    assert not b.in_position and b.cash == pytest.approx(1100)

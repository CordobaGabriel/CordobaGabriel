"""Punto de entrada de línea de comandos."""

import argparse
import logging
import time

from .backtest import run_backtest
from .broker import PaperBroker
from .config import load_config
from .data import fetch_ohlcv, load_csv
from .risk import RiskManager
from .strategies import build_strategy

log = logging.getLogger("tradingbot")


def _risk(cfg: dict) -> RiskManager:
    r = cfg.get("risk", {})
    return RiskManager(
        position_pct=r.get("position_pct", 1.0),
        stop_loss_pct=r.get("stop_loss_pct"),
        take_profit_pct=r.get("take_profit_pct"),
    )


def cmd_backtest(cfg: dict, csv: str | None) -> None:
    df = load_csv(csv) if csv else fetch_ohlcv(
        cfg["exchange"], cfg["symbol"], cfg["timeframe"], cfg.get("limit", 1000)
    )
    strategy = build_strategy(cfg["strategy"])
    bt = cfg.get("backtest", {})
    result = run_backtest(
        df,
        strategy,
        initial_capital=bt.get("initial_capital", 1000.0),
        fee_rate=bt.get("fee_rate", 0.001),
        risk=_risk(cfg),
    )
    print(f"\nBacktest {cfg.get('symbol', csv)} | {strategy}")
    print(f"Velas: {len(df)} ({df.index[0]} -> {df.index[-1]})\n")
    for k, v in result.metrics().items():
        print(f"  {k:<18} {v:,.2f}")


def cmd_paper(cfg: dict) -> None:
    strategy = build_strategy(cfg["strategy"])
    risk = _risk(cfg)
    bt = cfg.get("backtest", {})
    broker = PaperBroker(cash=bt.get("initial_capital", 1000.0), fee_rate=bt.get("fee_rate", 0.001))
    poll = cfg.get("paper", {}).get("poll_seconds", 60)

    log.info("Paper trading %s con %s. Ctrl+C para salir.", cfg["symbol"], strategy)
    while True:
        df = fetch_ohlcv(cfg["exchange"], cfg["symbol"], cfg["timeframe"], limit=500)
        closed = df.iloc[:-1]  # la última vela aún no ha cerrado
        signal = int(strategy.generate_signals(closed).iloc[-1])
        last = df.iloc[-1]
        price = last["close"]

        if broker.in_position and risk.should_exit(broker.entry_price, last["low"], last["high"]):
            broker.sell(price)
        elif not broker.in_position and signal == 1:
            broker.buy(price, risk.position_pct)
        elif broker.in_position and signal == 0:
            broker.sell(price)

        log.info("precio=%.2f señal=%d equity=%.2f", price, signal, broker.equity(price))
        time.sleep(poll)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="tradingbot")
    sub = parser.add_subparsers(dest="command", required=True)

    p_bt = sub.add_parser("backtest", help="Ejecuta un backtest")
    p_bt.add_argument("--config", default="config/config.yaml")
    p_bt.add_argument("--csv", help="CSV OHLCV local en lugar de descargar datos")

    p_paper = sub.add_parser("paper", help="Paper trading en vivo (simulado)")
    p_paper.add_argument("--config", default="config/config.yaml")

    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    cfg = load_config(args.config)

    if args.command == "backtest":
        cmd_backtest(cfg, args.csv)
    else:
        try:
            cmd_paper(cfg)
        except KeyboardInterrupt:
            log.info("Detenido.")


if __name__ == "__main__":
    main()

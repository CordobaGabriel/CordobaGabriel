# Trading Bot

Proyecto base de un bot de trading algorítmico en Python. Incluye:

- **Datos**: descarga de velas OHLCV desde exchanges vía [ccxt](https://github.com/ccxt/ccxt) o carga desde CSV.
- **Estrategias**: interfaz común + ejemplo de cruce de medias móviles (SMA crossover) y RSI.
- **Backtesting**: simulador vectorizado con comisiones y métricas (retorno, drawdown, Sharpe, win rate).
- **Gestión de riesgo**: tamaño de posición por % de capital, stop-loss y take-profit.
- **Paper trading**: loop en vivo que simula órdenes sin dinero real.
- **Tests** con pytest.

> ⚠️ **Aviso**: esto es un proyecto educativo. El trading conlleva riesgo de pérdida de capital.
> No uses dinero real sin haber probado a fondo la estrategia en backtesting y paper trading.

## Estructura

```
trading-bot/
├── config/config.example.yaml   # Configuración (copiar a config.yaml)
├── src/tradingbot/
│   ├── cli.py                   # Punto de entrada: backtest / paper
│   ├── config.py                # Carga de configuración
│   ├── data.py                  # Descarga y carga de datos OHLCV
│   ├── backtest.py              # Motor de backtesting y métricas
│   ├── risk.py                  # Gestión de riesgo
│   ├── broker.py                # Broker simulado (paper trading)
│   └── strategies/
│       ├── base.py              # Clase base de estrategias
│       ├── sma_crossover.py
│       └── rsi.py
└── tests/
```

## Instalación

```bash
cd trading-bot
python -m venv .venv
source .venv/bin/activate        # En Windows: .venv\Scripts\activate
pip install -e ".[dev]"
cp config/config.example.yaml config/config.yaml
```

## Uso

Backtest con datos de Binance (datos públicos, no requiere API key):

```bash
tradingbot backtest --config config/config.yaml
```

Backtest desde un CSV propio (columnas: `timestamp,open,high,low,close,volume`):

```bash
tradingbot backtest --config config/config.yaml --csv data/BTCUSDT_1h.csv
```

Paper trading (simulado, sin dinero real):

```bash
tradingbot paper --config config/config.yaml
```

Tests:

```bash
pytest
```

## Crear una estrategia nueva

1. Crea un archivo en `src/tradingbot/strategies/`.
2. Hereda de `Strategy` e implementa `generate_signals(df)`, que devuelve una serie con
   `1` (comprado) o `0` (fuera del mercado) para cada vela.
3. Regístrala en `STRATEGIES` dentro de `strategies/__init__.py`.

## API keys

Para operar en real hace falta configurar las claves del exchange como variables de entorno
(`EXCHANGE_API_KEY`, `EXCHANGE_API_SECRET`). **Nunca** las subas al repositorio: `.env` y
`config/config.yaml` están en `.gitignore`.

## Próximos pasos sugeridos

- [ ] Más estrategias (Bollinger, MACD, breakout).
- [ ] Optimización de parámetros (grid search / walk-forward).
- [ ] Ejecución real de órdenes vía ccxt con modo `live`.
- [ ] Notificaciones por Telegram.
- [ ] Dashboard de resultados.

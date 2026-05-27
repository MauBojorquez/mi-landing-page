"""
Bot principal multi-par con límite de pérdida diaria.

FLUJO EN CADA CICLO:
  1. Verifica si se alcanzó el límite de pérdida diaria (-3%)
  2. Para cada par configurado en SYMBOLS:
     a. Si ya hay MAX_OPEN_TRADES_TOTAL posiciones abiertas → para
     b. Si ya hay 1 posición abierta en ese par → salta al siguiente
     c. Calcula indicadores y busca señal
     d. Si hay señal → calcula lotes y ejecuta orden
  3. Espera 60 segundos y repite
"""

import time
import sys
import datetime

import mt5_connector as mt5c
from strategy import calculate_indicators, generate_signal
from risk_manager import calculate_lot_size
from logger import log
from config import (
    SYMBOLS, CHECK_INTERVAL_SECONDS,
    MAX_OPEN_TRADES_TOTAL, MAX_DAILY_LOSS_PCT
)

_daily_start_balance = None
_daily_start_date    = None


def get_daily_start_balance() -> float:
    global _daily_start_balance, _daily_start_date
    today = datetime.date.today()
    if _daily_start_date != today:
        _daily_start_balance = mt5c.get_account_balance()
        _daily_start_date    = today
        log(f"--- Nuevo día | Balance inicial del día: {_daily_start_balance:.2f} ---")
    return _daily_start_balance


def daily_loss_exceeded() -> bool:
    start   = get_daily_start_balance()
    equity  = mt5c.get_account_equity()
    pct     = (equity - start) / start * 100
    if pct <= -MAX_DAILY_LOSS_PCT:
        log(f"LIMITE DIARIO ALCANZADO | Pérdida del día: {pct:.2f}% | Límite: -{MAX_DAILY_LOSS_PCT}% | Sin más operaciones hoy.")
        return True
    return False


def run_cycle():
    if daily_loss_exceeded():
        return

    total_open = mt5c.count_all_open_positions()
    if total_open >= MAX_OPEN_TRADES_TOTAL:
        log(f"Posiciones abiertas: {total_open}/{MAX_OPEN_TRADES_TOTAL}. Esperando cierre.")
        return

    balance = mt5c.get_account_balance()

    for symbol in SYMBOLS:
        total_open = mt5c.count_all_open_positions()
        if total_open >= MAX_OPEN_TRADES_TOTAL:
            log(f"Límite de posiciones alcanzado ({total_open}/{MAX_OPEN_TRADES_TOTAL}). Pausando nuevas entradas.")
            break

        if mt5c.count_open_positions(symbol) >= 1:
            log(f"{symbol}: ya tiene posición abierta, saltando.")
            continue

        df = mt5c.get_candles(symbol, bars=300)
        if df.empty:
            continue

        df = calculate_indicators(df)
        if df.empty:
            continue

        last  = df.iloc[-1]
        log(f"{symbol} | Precio: {last['close']:.5f} | EMA50: {last['ema_fast']:.5f} | EMA200: {last['ema_slow']:.5f} | RSI: {last['rsi']:.1f}")

        signal = generate_signal(df)
        if signal is None:
            log(f"{symbol}: Sin señal.")
            continue

        log(f"*** SEÑAL {symbol}: {signal['signal']} | RSI={signal['rsi']:.1f} | ATR={signal['atr']:.5f} ***")

        sl_distance = abs(last["close"] - signal["sl"])
        lots        = calculate_lot_size(symbol, balance, sl_distance)

        if lots <= 0:
            log(f"ERROR: Lote inválido para {symbol}. Saltando.")
            continue

        mt5c.send_order(
            symbol=symbol,
            order_type=signal["signal"],
            volume=lots,
            sl_price=signal["sl"],
            tp_price=signal["tp"],
        )


def main():
    log("=" * 55)
    log(f"  AutoBot iniciado | {len(SYMBOLS)} pares | H1")
    log(f"  Pares: {', '.join(SYMBOLS)}")
    log(f"  Riesgo: 1% por trade | Límite diario: -{MAX_DAILY_LOSS_PCT}%")
    log(f"  Máx posiciones simultáneas: {MAX_OPEN_TRADES_TOTAL}")
    log("=" * 55)

    if not mt5c.connect():
        log("No se pudo conectar a MT5. Verifica que MT5 esté abierto.")
        sys.exit(1)

    try:
        while True:
            try:
                run_cycle()
            except Exception as e:
                log(f"ERROR en ciclo: {e}")

            log(f"Próximo análisis en {CHECK_INTERVAL_SECONDS}s...\n")
            time.sleep(CHECK_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        log("Bot detenido por el usuario.")
    finally:
        mt5c.disconnect()


if __name__ == "__main__":
    main()

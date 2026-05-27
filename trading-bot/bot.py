"""
Bot principal. Ejecuta el ciclo de análisis y trading de forma automática.

USO:
  python bot.py

FLUJO EN CADA CICLO:
  1. Obtiene las últimas velas de MT5
  2. Calcula indicadores (EMA, RSI, MACD, ATR)
  3. Evalúa si hay señal de compra o venta
  4. Si hay señal y no hay posición abierta, calcula lotes y ejecuta la orden
  5. Espera el intervalo configurado y repite
"""

import time
import sys
from datetime import datetime

import mt5_connector as mt5c
from strategy import calculate_indicators, generate_signal
from risk_manager import calculate_lot_size
from logger import log
from config import CHECK_INTERVAL_SECONDS, MAX_OPEN_TRADES, SYMBOL, TIMEFRAME


def run_cycle():
    df = mt5c.get_candles(bars=300)
    if df.empty:
        log("Sin datos de mercado, reintentando...")
        return

    df = calculate_indicators(df)
    if df.empty:
        return

    last    = df.iloc[-1]
    price   = last["close"]
    rsi_val = last["rsi"]
    ema_f   = last["ema_fast"]
    ema_s   = last["ema_slow"]

    log(f"Análisis {SYMBOL} {TIMEFRAME} | Precio: {price:.5f} | EMA{50}: {ema_f:.5f} | EMA{200}: {ema_s:.5f} | RSI: {rsi_val:.1f}")

    signal = generate_signal(df)

    open_trades = mt5c.count_open_positions()
    if open_trades >= MAX_OPEN_TRADES:
        log(f"Posiciones abiertas: {open_trades}/{MAX_OPEN_TRADES}. Esperando cierre.")
        return

    if signal is None:
        log("Sin señal. Esperando confluencia...")
        return

    log(f"*** SEÑAL DETECTADA: {signal['signal']} | RSI={signal['rsi']:.1f} | ATR={signal['atr']:.5f} ***")

    balance      = mt5c.get_account_balance()
    sl_distance  = abs(price - signal["sl"])
    lots         = calculate_lot_size(balance, sl_distance)

    if lots <= 0:
        log("ERROR: Tamaño de lote inválido. Operación cancelada.")
        return

    mt5c.send_order(
        order_type=signal["signal"],
        volume=lots,
        sl_price=signal["sl"],
        tp_price=signal["tp"],
    )


def main():
    log("=" * 55)
    log(f"  AutoBot iniciado | {SYMBOL} | {TIMEFRAME}")
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

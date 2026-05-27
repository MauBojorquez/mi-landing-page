"""
Calcula el tamaño de posición óptimo basado en el % de riesgo configurado.
Nunca arriesga más del RISK_PERCENT del balance por operación.
"""

import MetaTrader5 as mt5
from config import SYMBOL, RISK_PERCENT
from logger import log


def calculate_lot_size(balance: float, sl_distance_price: float) -> float:
    """
    balance          : saldo de la cuenta en la divisa base
    sl_distance_price: distancia en precio hasta el stop loss (ej: 0.0050 para 50 pips en EURUSD)

    Fórmula:
      capital_en_riesgo = balance * (RISK_PERCENT / 100)
      pip_value_por_lote = depende del símbolo (MT5 lo calcula)
      lotes = capital_en_riesgo / (sl_pips * pip_value_por_lote)
    """
    if sl_distance_price <= 0:
        log("ERROR risk_manager: sl_distance_price debe ser > 0")
        return 0.01

    sym = mt5.symbol_info(SYMBOL)
    if sym is None:
        log(f"ERROR risk_manager: símbolo {SYMBOL} no encontrado")
        return 0.01

    capital_risk    = balance * (RISK_PERCENT / 100.0)
    tick_size       = sym.trade_tick_size
    tick_value      = sym.trade_tick_value
    sl_in_ticks     = sl_distance_price / tick_size
    value_per_lot   = sl_in_ticks * tick_value

    if value_per_lot <= 0:
        return 0.01

    lots = capital_risk / value_per_lot
    lots = max(sym.volume_min, min(sym.volume_max, lots))
    lots = round(lots / sym.volume_step) * sym.volume_step
    lots = round(lots, 2)

    log(f"Risk Manager | Balance: {balance:.2f} | Riesgo: {capital_risk:.2f} | SL dist: {sl_distance_price:.5f} | Lotes calculados: {lots}")
    return lots

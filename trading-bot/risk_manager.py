"""
Calcula el tamaño de posición óptimo. Nunca arriesga más del RISK_PERCENT por operación.
"""

import MetaTrader5 as mt5
from config import RISK_PERCENT
from logger import log


def calculate_lot_size(symbol: str, balance: float, sl_distance_price: float) -> float:
    if sl_distance_price <= 0:
        log(f"ERROR risk_manager [{symbol}]: sl_distance debe ser > 0")
        return 0.01

    sym = mt5.symbol_info(symbol)
    if sym is None:
        log(f"ERROR risk_manager: símbolo {symbol} no encontrado")
        return 0.01

    capital_risk  = balance * (RISK_PERCENT / 100.0)
    tick_size     = sym.trade_tick_size
    tick_value    = sym.trade_tick_value
    sl_in_ticks   = sl_distance_price / tick_size
    value_per_lot = sl_in_ticks * tick_value

    if value_per_lot <= 0:
        return 0.01

    lots = capital_risk / value_per_lot
    lots = max(sym.volume_min, min(sym.volume_max, lots))
    lots = round(lots / sym.volume_step) * sym.volume_step
    lots = round(lots, 2)

    log(f"Risk [{symbol}] | Balance: {balance:.2f} | Riesgo: {capital_risk:.2f} | Lotes: {lots}")
    return lots

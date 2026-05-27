"""
Maneja la conexión con MetaTrader 5 y la ejecución de órdenes.
"""

import MetaTrader5 as mt5
import pandas as pd
from config import MT5_LOGIN, MT5_PASSWORD, MT5_SERVER, TIMEFRAME
from logger import log

_TF_MAP = {
    "M1":  mt5.TIMEFRAME_M1,
    "M5":  mt5.TIMEFRAME_M5,
    "M15": mt5.TIMEFRAME_M15,
    "M30": mt5.TIMEFRAME_M30,
    "H1":  mt5.TIMEFRAME_H1,
    "H4":  mt5.TIMEFRAME_H4,
    "D1":  mt5.TIMEFRAME_D1,
}


def connect():
    if not mt5.initialize():
        log(f"ERROR: No se pudo inicializar MT5: {mt5.last_error()}")
        return False

    if MT5_LOGIN and MT5_PASSWORD and MT5_SERVER:
        ok = mt5.login(MT5_LOGIN, password=MT5_PASSWORD, server=MT5_SERVER)
        if not ok:
            log(f"ERROR: Login fallido: {mt5.last_error()}")
            mt5.shutdown()
            return False

    info = mt5.account_info()
    log(f"Conectado | Cuenta: {info.login} | Balance: {info.balance:.2f} {info.currency} | Servidor: {info.server}")
    return True


def disconnect():
    mt5.shutdown()
    log("Desconectado de MT5.")


def get_candles(symbol: str, bars: int = 300) -> pd.DataFrame:
    tf = _TF_MAP.get(TIMEFRAME, mt5.TIMEFRAME_H1)
    rates = mt5.copy_rates_from_pos(symbol, tf, 0, bars)
    if rates is None or len(rates) == 0:
        log(f"ERROR: Sin datos para {symbol}")
        return pd.DataFrame()
    df = pd.DataFrame(rates)
    df["time"] = pd.to_datetime(df["time"], unit="s")
    return df


def get_account_balance() -> float:
    info = mt5.account_info()
    return info.balance if info else 0.0


def get_account_equity() -> float:
    info = mt5.account_info()
    return info.equity if info else 0.0


def count_open_positions(symbol: str) -> int:
    positions = mt5.positions_get(symbol=symbol)
    return len(positions) if positions else 0


def count_all_open_positions() -> int:
    positions = mt5.positions_get()
    return len(positions) if positions else 0


def get_symbol_info(symbol: str):
    info = mt5.symbol_info(symbol)
    if info is None:
        log(f"ERROR: Símbolo {symbol} no encontrado.")
    return info


def send_order(symbol: str, order_type: str, volume: float, sl_price: float, tp_price: float) -> bool:
    sym_info = get_symbol_info(symbol)
    if sym_info is None:
        return False

    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        log(f"ERROR: No se pudo obtener precio de {symbol}.")
        return False

    if order_type == "BUY":
        price    = tick.ask
        mt5_type = mt5.ORDER_TYPE_BUY
    else:
        price    = tick.bid
        mt5_type = mt5.ORDER_TYPE_SELL

    digits = sym_info.digits
    sl     = round(sl_price, digits)
    tp     = round(tp_price, digits)
    volume = round(volume, 2)

    request = {
        "action":       mt5.TRADE_ACTION_DEAL,
        "symbol":       symbol,
        "volume":       volume,
        "type":         mt5_type,
        "price":        price,
        "sl":           sl,
        "tp":           tp,
        "deviation":    10,
        "magic":        20250101,
        "comment":      "AutoBot",
        "type_time":    mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        log(f"ERROR orden {symbol} {order_type}: retcode={result.retcode} | {result.comment}")
        return False

    log(f"ORDEN EJECUTADA | {symbol} {order_type} {volume} lotes @ {price} | SL={sl} | TP={tp} | Ticket={result.order}")
    return True

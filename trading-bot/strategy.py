"""
Estrategia multi-indicador por confluencia:
  EMA 50/200  → define la tendencia principal
  RSI 14      → detecta momentum y zonas de sobrecompra/sobreventa
  MACD 12/26/9 → confirma el cruce de señal
  ATR 14      → calibra stop loss y take profit dinámicamente

Señal de COMPRA:  precio > EMA50 > EMA200  AND  RSI < RSI_BUY  AND  MACD cruza arriba
Señal de VENTA:   precio < EMA50 < EMA200  AND  RSI > RSI_SELL  AND  MACD cruza abajo
"""

import pandas as pd
import pandas_ta as ta
from config import (
    EMA_FAST, EMA_SLOW,
    RSI_PERIOD, RSI_BUY, RSI_SELL,
    MACD_FAST, MACD_SLOW, MACD_SIG,
    ATR_PERIOD, ATR_SL_MULT, ATR_TP_MULT
)


def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["ema_fast"] = ta.ema(df["close"], length=EMA_FAST)
    df["ema_slow"] = ta.ema(df["close"], length=EMA_SLOW)
    df["rsi"]      = ta.rsi(df["close"], length=RSI_PERIOD)
    df["atr"]      = ta.atr(df["high"], df["low"], df["close"], length=ATR_PERIOD)

    macd_df = ta.macd(df["close"], fast=MACD_FAST, slow=MACD_SLOW, signal=MACD_SIG)
    df["macd"]      = macd_df[f"MACD_{MACD_FAST}_{MACD_SLOW}_{MACD_SIG}"]
    df["macd_sig"]  = macd_df[f"MACDs_{MACD_FAST}_{MACD_SLOW}_{MACD_SIG}"]
    df["macd_hist"] = macd_df[f"MACDh_{MACD_FAST}_{MACD_SLOW}_{MACD_SIG}"]

    return df.dropna()


def _macd_crossed_up(df: pd.DataFrame) -> bool:
    """MACD cruzó por encima de la señal en la última vela cerrada."""
    prev = df.iloc[-2]
    last = df.iloc[-1]
    return (prev["macd"] < prev["macd_sig"]) and (last["macd"] > last["macd_sig"])


def _macd_crossed_down(df: pd.DataFrame) -> bool:
    """MACD cruzó por debajo de la señal en la última vela cerrada."""
    prev = df.iloc[-2]
    last = df.iloc[-1]
    return (prev["macd"] > prev["macd_sig"]) and (last["macd"] < last["macd_sig"])


def generate_signal(df: pd.DataFrame):
    """
    Retorna un dict con la señal o None si no hay señal.
    Estructura: {"signal": "BUY"|"SELL", "sl": float, "tp": float}
    """
    if len(df) < 3:
        return None

    last  = df.iloc[-1]
    price = last["close"]
    atr   = last["atr"]

    uptrend   = price > last["ema_fast"] and last["ema_fast"] > last["ema_slow"]
    downtrend = price < last["ema_fast"] and last["ema_fast"] < last["ema_slow"]

    rsi_buy_zone  = last["rsi"] < RSI_BUY
    rsi_sell_zone = last["rsi"] > RSI_SELL

    macd_up   = _macd_crossed_up(df)
    macd_down = _macd_crossed_down(df)

    if uptrend and rsi_buy_zone and macd_up:
        sl = price - (atr * ATR_SL_MULT)
        tp = price + (atr * ATR_TP_MULT)
        return {"signal": "BUY", "sl": sl, "tp": tp, "atr": atr, "rsi": last["rsi"]}

    if downtrend and rsi_sell_zone and macd_down:
        sl = price + (atr * ATR_SL_MULT)
        tp = price - (atr * ATR_TP_MULT)
        return {"signal": "SELL", "sl": sl, "tp": tp, "atr": atr, "rsi": last["rsi"]}

    return None

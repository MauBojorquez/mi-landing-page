"""
Estrategia multi-indicador (versión agresiva):
  EMA 50/200   → define la tendencia principal
  RSI 14       → confirma momentum (zonas más amplias: 40/60)
  MACD 12/26/9 → dirección del MACD vs señal (no espera cruce exacto)
  ATR 14       → calibra stop loss y take profit dinámicamente

Señal de COMPRA:  precio > EMA50 > EMA200  AND  RSI < 40  AND  MACD > señal
Señal de VENTA:   precio < EMA50 < EMA200  AND  RSI > 60  AND  MACD < señal
"""

import pandas as pd
import ta
from config import (
    EMA_FAST, EMA_SLOW,
    RSI_PERIOD, RSI_BUY, RSI_SELL,
    MACD_FAST, MACD_SLOW, MACD_SIG,
    ATR_PERIOD, ATR_SL_MULT, ATR_TP_MULT
)


def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["ema_fast"] = ta.trend.ema_indicator(df["close"], window=EMA_FAST)
    df["ema_slow"] = ta.trend.ema_indicator(df["close"], window=EMA_SLOW)
    df["rsi"]      = ta.momentum.rsi(df["close"], window=RSI_PERIOD)
    df["atr"]      = ta.volatility.average_true_range(df["high"], df["low"], df["close"], window=ATR_PERIOD)
    df["macd"]     = ta.trend.macd(df["close"], window_fast=MACD_FAST, window_slow=MACD_SLOW)
    df["macd_sig"] = ta.trend.macd_signal(df["close"], window_fast=MACD_FAST, window_slow=MACD_SLOW, window_sign=MACD_SIG)
    return df.dropna()


def generate_signal(df: pd.DataFrame):
    if len(df) < 3:
        return None

    last  = df.iloc[-1]
    price = last["close"]
    atr   = last["atr"]

    uptrend   = price > last["ema_fast"] and last["ema_fast"] > last["ema_slow"]
    downtrend = price < last["ema_fast"] and last["ema_fast"] < last["ema_slow"]

    rsi_buy_zone  = last["rsi"] < RSI_BUY
    rsi_sell_zone = last["rsi"] > RSI_SELL

    macd_bullish = last["macd"] > last["macd_sig"]
    macd_bearish = last["macd"] < last["macd_sig"]

    if uptrend and rsi_buy_zone and macd_bullish:
        sl = price - (atr * ATR_SL_MULT)
        tp = price + (atr * ATR_TP_MULT)
        return {"signal": "BUY", "sl": sl, "tp": tp, "atr": atr, "rsi": last["rsi"]}

    if downtrend and rsi_sell_zone and macd_bearish:
        sl = price + (atr * ATR_SL_MULT)
        tp = price - (atr * ATR_TP_MULT)
        return {"signal": "SELL", "sl": sl, "tp": tp, "atr": atr, "rsi": last["rsi"]}

    return None

"""
Configuración central del bot.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# --- Conexión MT5 ---
MT5_LOGIN    = int(os.getenv("MT5_LOGIN", "0"))
MT5_PASSWORD = os.getenv("MT5_PASSWORD", "")
MT5_SERVER   = os.getenv("MT5_SERVER", "")

# --- Pares a operar ---
SYMBOLS   = ["EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD"]
TIMEFRAME = "H1"

# --- Gestión de riesgo ---
RISK_PERCENT          = 1.0   # % del balance arriesgado por operación
ATR_SL_MULT           = 1.5   # Multiplicador ATR para stop loss
ATR_TP_MULT           = 2.5   # Multiplicador ATR para take profit
MAX_OPEN_TRADES_TOTAL = 2     # Máximo de posiciones abiertas en total (todos los pares)
MAX_DAILY_LOSS_PCT    = 3.0   # Para el bot si pierde este % del balance en el día

# --- Parámetros de indicadores ---
EMA_FAST   = 50
EMA_SLOW   = 200
RSI_PERIOD = 14
RSI_BUY    = 45
RSI_SELL   = 55
MACD_FAST  = 12
MACD_SLOW  = 26
MACD_SIG   = 9
ATR_PERIOD = 14

# --- Control del bot ---
CHECK_INTERVAL_SECONDS = 60
LOG_FILE = "bot_log.txt"

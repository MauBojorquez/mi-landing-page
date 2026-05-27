"""
Configuración central del bot. Las credenciales se leen del archivo .env (nunca va a GitHub).
"""

import os
from dotenv import load_dotenv

load_dotenv()

# --- Conexión MT5 (se leen de .env) ---
MT5_LOGIN    = int(os.getenv("MT5_LOGIN", "0"))
MT5_PASSWORD = os.getenv("MT5_PASSWORD", "")
MT5_SERVER   = os.getenv("MT5_SERVER", "")

# --- Activo a operar ---
SYMBOL    = "EURUSD"
TIMEFRAME = "H1"          # M1, M5, M15, M30, H1, H4, D1

# --- Gestión de riesgo ---
RISK_PERCENT   = 1.0      # % del capital arriesgado por operación (1% = conservador)
ATR_SL_MULT    = 1.5      # Multiplicador ATR para stop loss
ATR_TP_MULT    = 2.5      # Multiplicador ATR para take profit (ratio 2.5:1)
MAX_OPEN_TRADES = 1       # Máximo de operaciones abiertas simultáneas

# --- Parámetros de indicadores ---
EMA_FAST   = 50           # EMA rápida (tendencia corta)
EMA_SLOW   = 200          # EMA lenta (tendencia principal)
RSI_PERIOD = 14
RSI_BUY    = 45           # RSI por debajo de este valor = zona de compra
RSI_SELL   = 55           # RSI por encima de este valor = zona de venta
MACD_FAST  = 12
MACD_SLOW  = 26
MACD_SIG   = 9
ATR_PERIOD = 14

# --- Control del bot ---
CHECK_INTERVAL_SECONDS = 60   # Cada cuántos segundos revisa el mercado
LOG_FILE = "bot_log.txt"

"""
Configuración central del bot. Ajusta estos valores según tu cuenta demo.
"""

# --- Conexión MT5 ---
MT5_LOGIN    = 0          # Tu número de cuenta demo (ej: 123456789)
MT5_PASSWORD = ""         # Tu contraseña de cuenta demo
MT5_SERVER   = ""         # Servidor del broker (ej: "ICMarkets-Demo")

# --- Activo a operar ---
SYMBOL    = "EURUSD"
TIMEFRAME = "M15"         # M1, M5, M15, M30, H1, H4, D1

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

"""
Script de prueba — coloca UNA operación mínima en EURUSD para verificar
que el bot está correctamente conectado a MT5.

USO:
  python test_trade.py
"""

import MetaTrader5 as mt5
from dotenv import load_dotenv
import os

load_dotenv()

MT5_LOGIN    = int(os.getenv("MT5_LOGIN", "0"))
MT5_PASSWORD = os.getenv("MT5_PASSWORD", "")
MT5_SERVER   = os.getenv("MT5_SERVER", "")

SYMBOL = "EURUSD"
VOLUME = 0.01   # lote mínimo (~$1 de riesgo)

print("Conectando a MT5...")
if not mt5.initialize():
    print(f"ERROR: No se pudo inicializar MT5: {mt5.last_error()}")
    exit(1)

if MT5_LOGIN and MT5_PASSWORD and MT5_SERVER:
    if not mt5.login(MT5_LOGIN, password=MT5_PASSWORD, server=MT5_SERVER):
        print(f"ERROR: Login fallido: {mt5.last_error()}")
        mt5.shutdown()
        exit(1)

info = mt5.account_info()
print(f"Conectado | Cuenta: {info.login} | Balance: {info.balance:.2f} {info.currency}")

tick = mt5.symbol_info_tick(SYMBOL)
price = tick.ask
sl    = round(price - 0.0010, 5)   # 10 pips de SL
tp    = round(price + 0.0020, 5)   # 20 pips de TP

request = {
    "action":       mt5.TRADE_ACTION_DEAL,
    "symbol":       SYMBOL,
    "volume":       VOLUME,
    "type":         mt5.ORDER_TYPE_BUY,
    "price":        price,
    "sl":           sl,
    "tp":           tp,
    "deviation":    10,
    "magic":        99999,
    "comment":      "Test conexion",
    "type_time":    mt5.ORDER_TIME_GTC,
    "type_filling": mt5.ORDER_FILLING_IOC,
}

print(f"Enviando orden de prueba: BUY {VOLUME} {SYMBOL} @ {price} | SL={sl} | TP={tp}")
result = mt5.order_send(request)

if result.retcode == mt5.TRADE_RETCODE_DONE:
    print(f"\n EXITO — Orden ejecutada correctamente")
    print(f"   Ticket: {result.order}")
    print(f"   Precio: {result.price}")
    print(f"\nEl bot esta correctamente conectado a MT5.")
    print(f"Puedes ver la operacion en MT5 pestaña 'Operaciones'.")
else:
    print(f"\n ERROR — retcode={result.retcode} | {result.comment}")
    print("Revisa que MT5 este abierto y con trading algoritmico activado.")

mt5.shutdown()

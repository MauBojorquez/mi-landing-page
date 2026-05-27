# AutoBot MT5 — Guía de instalación y uso

## Requisitos previos

- MetaTrader 5 instalado y abierto (con cuenta demo activa)
- Python 3.9 o superior → https://www.python.org/downloads/
  - Durante la instalación: **marca la casilla "Add Python to PATH"**

---

## Instalación paso a paso

### 1. Instalar dependencias

Abre una terminal (CMD o PowerShell) en la carpeta `trading-bot` y ejecuta:

```bash
pip install -r requirements.txt
```

### 2. Configurar tu cuenta

Abre `config.py` y llena tus datos de cuenta demo:

```python
MT5_LOGIN    = 123456789     # Tu número de cuenta (lo ves en MT5, esquina superior)
MT5_PASSWORD = "tuContraseña"
MT5_SERVER   = "NombreDelBroker-Demo"  # Ej: "ICMarkets-Demo", "Exness-Demo"
```

> El servidor lo encuentras en MT5 → Archivo → Abrir Cuenta → busca tu broker.

### 3. Verificar que MT5 permita trading algorítmico

En MetaTrader 5:
- **Herramientas → Opciones → Expert Advisors**
- Activa: ✅ "Permitir trading algorítmico"

### 4. Iniciar el bot

```bash
python bot.py
```

Verás logs en tiempo real. También se guarda todo en `bot_log.txt`.

---

## Cómo funciona la estrategia

| Condición | BUY | SELL |
|-----------|-----|------|
| Tendencia | Precio > EMA50 > EMA200 | Precio < EMA50 < EMA200 |
| Momentum  | RSI < 45 | RSI > 55 |
| Confirmación | MACD cruza hacia arriba | MACD cruza hacia abajo |

**Las 3 condiciones deben cumplirse simultáneamente** para ejecutar una orden.

- **Stop Loss**: 1.5× ATR (automático, basado en volatilidad real)
- **Take Profit**: 2.5× ATR (ratio riesgo/recompensa de 1:2.5)
- **Tamaño de posición**: 1% del balance arriesgado por operación

---

## Parámetros ajustables (config.py)

| Parámetro | Default | Descripción |
|-----------|---------|-------------|
| `RISK_PERCENT` | 1.0 | % del balance por trade. No subir de 2% en demo |
| `TIMEFRAME` | M15 | Marco temporal. H1 = menos señales pero más precisas |
| `ATR_SL_MULT` | 1.5 | Multiplicador para stop loss |
| `ATR_TP_MULT` | 2.5 | Multiplicador para take profit |
| `CHECK_INTERVAL_SECONDS` | 60 | Frecuencia de análisis (en segundos) |
| `MAX_OPEN_TRADES` | 1 | Máximo de posiciones abiertas a la vez |

---

## Detener el bot

Presiona `Ctrl + C` en la terminal.

---

## Estructura del proyecto

```
trading-bot/
├── bot.py           # Punto de entrada principal
├── config.py        # Toda la configuración aquí
├── strategy.py      # Lógica de señales (EMA + RSI + MACD)
├── risk_manager.py  # Cálculo de tamaño de posición
├── mt5_connector.py # Conexión y ejecución de órdenes en MT5
├── logger.py        # Sistema de logs
└── bot_log.txt      # Log generado automáticamente
```

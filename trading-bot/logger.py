"""
Sistema de logging: imprime en consola y guarda en archivo.
"""

import sys
from datetime import datetime
from config import LOG_FILE


def log(message: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}"
    print(line, flush=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

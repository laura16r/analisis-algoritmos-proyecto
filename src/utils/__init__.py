"""
utils/io.py
===========
Funciones de lectura y escritura JSON reutilizables.

Antes estas funciones estaban copiadas en market_processor.py
y en market_cleaner.py. Al centralizarlas aqui, cualquier cambio
(encoding, formato, manejo de errores) se aplica a todo el proyecto
desde un solo lugar.
"""

import json
import os
from typing import Any


def load_json(path: str) -> list[dict[str, Any]]:
    """
    Lee un archivo JSON y devuelve su contenido como lista de diccionarios.
    Lanza FileNotFoundError si el archivo no existe para que el llamador
    pueda manejarlo con un mensaje descriptivo.
    """
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def save_json(path: str, data: Any) -> None:
    """
    Guarda cualquier estructura serializable como JSON con indentacion.
    Crea las carpetas intermedias si no existen.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
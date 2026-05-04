"""
utils/io.py
===========
Funciones centralizadas de lectura y escritura JSON.

Todos los modulos del proyecto usan FileUtils para leer y guardar
archivos. Si cambia el formato o encoding, se modifica aqui y
aplica a todo el proyecto.
"""

import json
import os
from typing import Any


class FileUtils:

    @staticmethod
    def load_json(file_path: str) -> list[dict[str, Any]]:
        """
        Lee un archivo JSON y retorna su contenido.
        Lanza FileNotFoundError si el archivo no existe.
        """
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)

    @staticmethod
    def save_json(file_path: str, data: Any) -> None:
        """
        Guarda cualquier estructura serializable como JSON con indentacion.
        Crea las carpetas intermedias si no existen.
        """
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
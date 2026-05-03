import json
import os
from typing import Any


class FileUtils:
    """
    Utilidades generales para lectura y escritura de archivos.

    Esta clase centraliza operaciones repetidas de I/O para evitar duplicar
    json.load, json.dump, os.makedirs y manejo básico de errores en extractors,
    processors, cleaners y analytics.
    """

    @staticmethod
    def ensure_directory_exists(file_path: str) -> None:
        """
        Crea el directorio padre de un archivo si no existe.

        Args:
            file_path: Ruta completa del archivo.
        """

        directory = os.path.dirname(file_path)

        if directory:
            os.makedirs(directory, exist_ok=True)

    @staticmethod
    def save_json(
        file_path: str,
        data: Any,
        indent: int = 4,
        ensure_ascii: bool = False,
    ) -> None:
        """
        Guarda datos serializables en formato JSON.

        Args:
            data: Datos serializables a JSON.
            file_path: Ruta destino del archivo.
            indent: Nivel de indentación del JSON.
            ensure_ascii: Si False, conserva caracteres UTF-8.
        """

        try:
            FileUtils.ensure_directory_exists(file_path)

            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(
                    data,
                    file,
                    indent=indent,
                    ensure_ascii=ensure_ascii,
                )

        except TypeError as error:
            raise TypeError(
                f"[FileUtils] Los datos no son serializables a JSON: {error}"
            )

        except OSError as error:
            raise OSError(
                f"[FileUtils] No se pudo guardar el archivo '{file_path}': {error}"
            )

    @staticmethod
    def load_json(file_path: str) -> Any:
        """
        Carga un archivo JSON.

        Args:
            file_path: Ruta del archivo JSON.

        Returns:
            Contenido del archivo JSON.
        """

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return json.load(file)

        except FileNotFoundError:
            raise FileNotFoundError(
                f"[FileUtils] El archivo no existe: '{file_path}'"
            )

        except json.JSONDecodeError as error:
            raise ValueError(
                f"[FileUtils] El archivo no contiene JSON válido: '{file_path}'. "
                f"Detalle: {error}"
            )

        except OSError as error:
            raise OSError(
                f"[FileUtils] No se pudo leer el archivo '{file_path}': {error}"
            )
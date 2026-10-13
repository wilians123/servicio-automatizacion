"""Lectura tolerante del JSON DUCA-T congelado."""

import json
from decimal import Decimal
from pathlib import Path
from typing import Any


def cargar_contrato(ruta: str | Path) -> dict[str, Any]:
    with Path(ruta).open("r", encoding="utf-8") as archivo:
        datos = json.load(archivo, parse_float=Decimal)
    if not isinstance(datos, dict):
        raise ValueError("El contrato JSON debe contener un objeto en la raíz.")
    return datos


def paso_datos(datos: dict[str, Any], nombre: str) -> dict[str, Any]:
    paso = datos.get(nombre)
    return paso if isinstance(paso, dict) else {}

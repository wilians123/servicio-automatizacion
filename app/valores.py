"""Helpers for contract values and literal option matching."""

import re
import unicodedata
from decimal import Decimal


def a_texto(valor) -> str:
    if isinstance(valor, Decimal):
        return format(valor, "f")
    if isinstance(valor, float):
        return format(Decimal(str(valor)), "f")
    if isinstance(valor, bool):
        return "true" if valor else "false"
    return str(valor)


def es_vacio(valor) -> bool:
    return valor is None or (isinstance(valor, str) and not valor.strip())


def normalizar(texto: str) -> str:
    sin_acentos = "".join(
        letra
        for letra in unicodedata.normalize("NFKD", texto)
        if not unicodedata.combining(letra)
    )
    return " ".join(sin_acentos.casefold().split())


def construir_regex_opcion(texto: str) -> re.Pattern[str]:
    return re.compile(r"^\s*" + re.escape(texto) + r"\s*$", re.IGNORECASE)

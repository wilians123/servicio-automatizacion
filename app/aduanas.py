"""Búsqueda y coincidencia literal de nombres de aduana."""

import re

from app.valores import normalizar


_GENERICOS = {"ADUANA", "TERRESTRE"}


def extraer_codigo_numerico_aduana(valor: str) -> str | None:
    """Devuelve el código numérico del segmento central de una aduana."""
    segmentos = re.split(r"\s*[-–—]\s*", valor.strip())
    if len(segmentos) < 3:
        return None
    codigo = segmentos[1].strip()
    return codigo if codigo.isdigit() else None


def terminos_busqueda_aduana(valor: str) -> list[str]:
    segmentos = re.split(r"\s*[-–—]\s*", valor.strip())
    terminos: list[str] = []
    if len(segmentos) >= 3:
        codigo = segmentos[1].strip()
        if codigo:
            terminos.append(codigo)

    nombre = segmentos[0] if segmentos else valor
    palabras = [parte for parte in re.split(r"\s+", nombre.strip()) if parte]
    distintiva = next(
        (palabra for palabra in palabras if normalizar(palabra).upper() not in _GENERICOS),
        palabras[0] if palabras else "",
    )
    if distintiva and distintiva.casefold() not in {x.casefold() for x in terminos}:
        terminos.append(distintiva)
    return terminos


def indice_coincidencia_exacta(valor: str, opciones: list[str]) -> int | None:
    objetivo = normalizar(valor)
    indices = [indice for indice, texto in enumerate(opciones) if normalizar(texto) == objetivo]
    return indices[0] if len(indices) == 1 else None

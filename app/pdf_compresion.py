"""Compresión agresiva de PDF antes de almacenarlos en una ejecución."""

from __future__ import annotations

from io import BytesIO
import logging
from pathlib import PurePath

import pymupdf

logger = logging.getLogger(__name__)
LIMITE_PDF_BYTES = 999 * 1024

# Se empieza con calidad razonable y se baja gradualmente. Los dos últimos
# niveles son extremos; se conservan texto y gráficos vectoriales del PDF.
_NIVELES_COMPRESION = (
    (180, 120, 55),
    (150, 96, 40),
    (120, 72, 25),
    (96, 50, 15),
    (72, 36, 10),
)


class PDFNoComprimibleError(ValueError):
    """El PDF no pudo reducirse al límite requerido."""


def comprimir_si_es_necesario(nombre: str, contenido: bytes) -> bytes:
    """Comprime PDFs mayores a 999 KiB; deja intactos los demás archivos."""
    if PurePath(nombre.replace("\\", "/")).suffix.lower() != ".pdf":
        return contenido
    if len(contenido) <= LIMITE_PDF_BYTES:
        return contenido

    logger.info(
        "PDF pesado recibido: %s (%.1f KiB; límite %.1f KiB). Iniciando compresión.",
        nombre,
        len(contenido) / 1024,
        LIMITE_PDF_BYTES / 1024,
    )

    try:
        for dpi_umbral, dpi_objetivo, calidad in _NIVELES_COMPRESION:
            with pymupdf.open(stream=contenido, filetype="pdf") as documento:
                if documento.needs_pass:
                    raise PDFNoComprimibleError(
                        "El PDF está protegido con contraseña y no se puede comprimir."
                    )
                sigflags = documento.get_sigflags()
                if sigflags is not None and sigflags >= 3:
                    raise PDFNoComprimibleError(
                        "El PDF contiene firmas digitales que no se pueden conservar al comprimirlo."
                    )

                documento.rewrite_images(
                    dpi_threshold=dpi_umbral,
                    dpi_target=dpi_objetivo,
                    quality=calidad,
                )
                buffer = BytesIO()
                documento.save(
                    buffer,
                    garbage=4,
                    deflate=1,
                    use_objstms=True,
                )
                comprimido = buffer.getvalue()

            if len(comprimido) <= LIMITE_PDF_BYTES:
                logger.info(
                    "Compresión PDF exitosa: %s (%.1f KiB -> %.1f KiB; %d dpi, calidad %d).",
                    nombre,
                    len(contenido) / 1024,
                    len(comprimido) / 1024,
                    dpi_objetivo,
                    calidad,
                )
                return comprimido
    except PDFNoComprimibleError:
        raise
    except Exception as exc:
        raise PDFNoComprimibleError(
            "El PDF no se pudo procesar para compresión."
        ) from exc

    raise PDFNoComprimibleError(
        "El PDF sigue excediendo 999 KiB después de aplicar compresión extrema."
    )

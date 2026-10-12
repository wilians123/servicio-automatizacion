"""Wrapper que permite recuperar un paso fallido manualmente."""

import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Callable

from app.config import Settings, get_settings
from app.pausa import Pausador, pausar_para_usuario

logger = logging.getLogger(__name__)


def paso(
    page,
    nombre: str,
    accion: Callable[[], None],
    *,
    settings: Settings | None = None,
    pausador: Pausador | None = None,
) -> None:
    try:
        logger.info("▶ %s", nombre)
        accion()
    except Exception as error:
        if page.is_closed():
            raise

        mensaje = str(error).splitlines()[0] if str(error) else type(error).__name__
        logger.exception("Falló el paso %s: %s", nombre, mensaje)
        config = settings or get_settings()
        carpeta = config.data_dir / "capturas"
        carpeta.mkdir(parents=True, exist_ok=True)
        slug = re.sub(r"[^A-Za-z0-9]+", "_", nombre).strip("_") or "paso"
        captura = carpeta / f"{datetime.now():%Y%m%d_%H%M%S}_{slug}.png"
        try:
            page.screenshot(path=str(captura), full_page=True)
            logger.error("Captura guardada: %s", captura)
        except Exception:
            logger.exception("No se pudo guardar la captura de %s", nombre)
            if page.is_closed():
                raise

        try:
            pausar_para_usuario(
                page,
                f'Falló el paso "{nombre}". Complétalo manualmente.',
                pausador,
            )
        except Exception:
            if page.is_closed():
                raise error
            raise

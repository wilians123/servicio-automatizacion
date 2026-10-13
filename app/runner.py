"""Wrapper que permite recuperar un paso fallido manualmente."""

import logging
import re
from contextvars import ContextVar
from datetime import datetime
from pathlib import Path
from typing import Callable

from app.config import Settings, get_settings
from app.errors import NavegadorCerradoError
from app.pausa import Pausador, pausar_para_usuario

logger = logging.getLogger(__name__)
_reporter_actual: ContextVar[Callable | None] = ContextVar("reporter_actual", default=None)
_pausador_actual: ContextVar[Pausador | None] = ContextVar("pausador_actual", default=None)


def reporter_context(reporter, pausador=None):
    """Asocia el reporter al flujo actual sin cambiar las firmas de los pasos."""
    return _reporter_actual.set(reporter), _pausador_actual.set(pausador)


def restaurar_reporter(token) -> None:
    reporter_token, pausador_token = token
    _reporter_actual.reset(reporter_token)
    _pausador_actual.reset(pausador_token)


def _notificar(reporter, evento: str, **datos) -> None:
    if reporter is not None:
        reporter(evento, **datos)


def paso(
    page,
    nombre: str,
    accion: Callable[[], None],
    *,
    settings: Settings | None = None,
    pausador: Pausador | None = None,
    reporter=None,
) -> None:
    reporter = reporter or _reporter_actual.get()
    pausador = pausador or _pausador_actual.get()
    if reporter is not None:
        reporter("comprobar_cancelacion")
    try:
        logger.info("▶ %s", nombre)
        _notificar(reporter, "paso_inicio", nombre=nombre)
        accion()
        _notificar(reporter, "paso_ok", nombre=nombre)
    except Exception as error:
        _notificar(reporter, "paso_fallo", nombre=nombre)
        if page.is_closed():
            raise

        # No registrar texto de excepciones: algunos mensajes de validación pueden
        # incluir valores del formulario que pertenecen al embarque.
        logger.error("Falló el paso %s (%s)", nombre, type(error).__name__)
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
            _notificar(reporter, "pausa_inicio", motivo=f'Falló el paso "{nombre}". Complétalo manualmente.')
            pausar_para_usuario(
                page,
                f'Falló el paso "{nombre}". Complétalo manualmente.',
                pausador,
            )
            _notificar(reporter, "pausa_fin", motivo=f'Falló el paso "{nombre}". Complétalo manualmente.')
            _notificar(reporter, "paso_ok", nombre=nombre)
        except Exception as pausa_error:
            if reporter is not None and isinstance(pausa_error, NavegadorCerradoError):
                raise
            if page.is_closed():
                raise error
            raise

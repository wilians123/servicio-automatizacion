"""Flujo completo de captura DUCA-T; se detiene antes de guardar la declaración."""

from pathlib import Path

from app.pasos import crear_duca, paso1, paso2, paso3, paso4, paso5, paso6, paso7, paso8, paso9
from app.pausa import pausar_para_usuario
from app.runner import reporter_context, restaurar_reporter


def ejecutar_duca(page, datos: dict, ruta_archivos: str | Path, settings, reporter=None, pausador=None) -> None:
    token = reporter_context(reporter, pausador)
    try:
        crear_duca.ejecutar(page, datos, settings)
        paso1.ejecutar(page, datos.get("paso1") or {}, settings)
        paso2.ejecutar(page, datos.get("paso2") or {}, settings)
        paso3.ejecutar(page, datos.get("paso3") or {}, settings)
        paso4.ejecutar(page, datos.get("paso4") or {}, settings)
        paso5.ejecutar(page, datos.get("paso5") or {}, settings)
        paso6.ejecutar(page, datos.get("paso6") or {}, settings)
        paso7.ejecutar(page, datos.get("paso7") or {}, settings)
        paso8.ejecutar(page, datos.get("paso8") or {}, Path(ruta_archivos), settings)
        paso9.ejecutar(page, datos.get("paso9") or {}, settings)
        page.wait_for_timeout(200)
        pausar_para_usuario(
            page,
            "Revisa y guarda la DUCA manualmente",
            pausador,
        )
    finally:
        restaurar_reporter(token)

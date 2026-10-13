"""Paso 1: aduanas, país de destino y observaciones."""

import logging
import re

from app.pasos.comunes import (
    campo,
    fijo,
    pausa_operador,
    seleccionar_aduana,
    seleccionar_select2,
    esperar_selectores_paso1_listos,
)
from app.pausa import pausar_para_usuario
from app.valores import es_vacio

logger = logging.getLogger(__name__)


def ejecutar(page, datos: dict, settings) -> None:
    campo_inicio = datos.get("AduanaInicio")

    def elegir_inicio(valor: str) -> None:
        page.locator('span[data-valmsg-for="P1_AduanaInicio"]').filter(
            has_text="Seleccione una aduana de inicio"
        ).wait_for(state="visible", timeout=30_000)
        if not seleccionar_aduana(page, "#s2id_P1_AduanaInicio", valor):
            logger.warning("No se encontró coincidencia única para AduanaInicio")
            pausar_para_usuario(
                page,
                "No se encontró una coincidencia única para AduanaInicio en el paso 1: complétala manualmente",
            )

    campo(page, "1", "AduanaInicio", campo_inicio, elegir_inicio)
    page.wait_for_timeout(5000)

    def destino_fijo() -> None:
        seleccionar_select2(
            page, "#s2id_P1_PaisDestino", "Salvador", "El Salvador"
        )

    fijo(page, "1", "País de destino", destino_fijo)
    page.wait_for_timeout(5000)

    campo_destino = datos.get("AduanaDestino")

    def elegir_destino(valor: str) -> None:
        esperar_selectores_paso1_listos(page)
        page.locator('span[data-valmsg-for="P1_AduanaDestino"]').filter(
            has_text="Seleccione una aduana de destino"
        ).wait_for(state="visible", timeout=30_000)
        page.wait_for_timeout(1000)
        if not seleccionar_aduana(page, "#s2id_P1_AduanaDestino", valor):
            logger.warning("No se encontró coincidencia única para AduanaDestino")
            pausar_para_usuario(
                page,
                "No se encontró una coincidencia única para AduanaDestino en el paso 1: complétala manualmente",
            )

    campo(page, "1", "AduanaDestino", campo_destino, elegir_destino)
    campo(
        page,
        "1",
        "Observaciones",
        datos.get("Observaciones"),
        lambda texto: page.get_by_role("textbox", name=re.compile("Observaciones")).fill(texto),
    )
    fijo(
        page,
        "1",
        "Siguiente",
        lambda: page.locator("#step1").get_by_text("Siguiente").click(),
    )

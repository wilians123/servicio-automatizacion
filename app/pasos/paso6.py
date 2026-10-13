"""Paso 6: licencia del conductor."""

import logging
import re

from app.pasos.comunes import fijo
from app.pausa import pausar_para_usuario
from app.valores import a_texto, es_vacio

logger = logging.getLogger(__name__)


def ejecutar(page, datos: dict, settings) -> None:
    page.wait_for_timeout(200)

    def tipo_documento() -> None:
        contenedor = page.locator("#s2id_cmbTipoDocumentoConductor")
        contenedor.click()
        entrada = contenedor.locator("input")
        entrada.press_sequentially("LIC", delay=200)
        page.locator(".select2-results li").filter(has_text="Licencia").click()

    fijo(page, "6", "Tipo de documento conductor", tipo_documento)

    licencia = datos.get("LicenciaConductor")

    def llenar_licencia_y_buscar() -> None:
        campo_licencia = page.get_by_role("textbox", name="Ingrese el número de")
        if es_vacio(licencia):
            logger.warning("Falta LicenciaConductor en el paso 6")
            pausar_para_usuario(
                page,
                "Falta LicenciaConductor en el paso 6: complétala manualmente",
            )
        else:
            campo_licencia.click()
            campo_licencia.fill(a_texto(licencia))
        page.wait_for_timeout(500)
        page.locator("#btnBusquedaConductor").click()

    fijo(page, "6", "Licencia conductor", llenar_licencia_y_buscar)

    fijo(
        page,
        "6",
        "Esperar datos del conductor",
        lambda: page.get_by_text(
            re.compile("Debe ingresar el primer nombre del conductor", re.I)
        ).filter(visible=True).first.wait_for(state="hidden", timeout=20_000),
    )
    page.wait_for_timeout(500)
    fijo(page, "6", "Siguiente", lambda: page.locator("#step6").get_by_text("Siguiente").click())

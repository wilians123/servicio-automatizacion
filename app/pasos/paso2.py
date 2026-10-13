"""Paso 2: exportador."""

import re

from app.pasos.comunes import campo, fijo, valor_pais, seleccionar_pais_select2_directo, esperar_mensaje_rojo
from app.runner import paso


def ejecutar(page, datos: dict, settings) -> None:
    fijo(
        page,
        "2",
        "Esperar formulario",
        lambda: esperar_mensaje_rojo(
            page, re.compile(r"Debe ingresar el nombre o raz[oó]n social del exportador", re.I)
        ),
    )
    campo(page, "2", "NombreExportador", datos.get("NombreExportador"), lambda v: (page.locator("#P2_NombreExportador_I").click(), page.locator("#P2_NombreExportador_I").fill(v)))
    campo(page, "2", "DomicilioExportador", datos.get("DomicilioExportador"), lambda v: (page.locator("#P2_DireccionExportador_I").click(), page.locator("#P2_DireccionExportador_I").fill(v)))

    def tipo_identificacion() -> None:
        contenedor = page.locator("#s2id_P2_TipoDocumentoIdentificacion")
        contenedor.click()
        entrada = contenedor.locator("input")
        entrada.press_sequentially("Tributa", delay=200)
        page.locator(".select2-results li").filter(
            has_text="Número de Identificacion Tributaria"
        ).click()

    fijo(page, "2", "Tipo de identificación exportador", tipo_identificacion)
    campo(
        page,
        "2",
        "NumeroIdentificacionExportador",
        "S/N",
        lambda v: (page.locator("#P2_NumeroDocumento_I").click(), page.locator("#P2_NumeroDocumento_I").fill(v)),
    )

    def pais_exportador() -> None:
        pais = valor_pais(page, "2", "PaisExportador", datos.get("PaisExportador"))
        if pais is not None:
            seleccionar_pais_select2_directo(page, "#s2id_P2_PaisEmisionDocumento", pais)

    paso(page, "Paso 2 - País exportador", pais_exportador)
    fijo(page, "2", "Siguiente", lambda: page.locator("#step2").get_by_text("Siguiente").click())

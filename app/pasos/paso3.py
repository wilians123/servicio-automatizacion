"""Paso 3: importador."""

import re

from app.pasos.comunes import campo, fijo, valor_pais, seleccionar_pais_select2_directo, esperar_mensaje_rojo
from app.runner import paso


def ejecutar(page, datos: dict, settings) -> None:
    fijo(
        page,
        "3",
        "Esperar formulario",
        lambda: esperar_mensaje_rojo(
            page, re.compile(r"Debe ingresar el nombre o raz[oó]n social del importador", re.I)
        ),
    )
    campo(page, "3", "NombreImportador", datos.get("NombreImportador"), lambda v: (page.locator("#P3_NombreConsignatario_I").click(), page.locator("#P3_NombreConsignatario_I").fill(v)))
    campo(page, "3", "DomicilioImportador", datos.get("DomicilioImportador"), lambda v: (page.locator("#P3_DireccionConsignatario_I").click(), page.locator("#P3_DireccionConsignatario_I").fill(v)))

    def tipo_identificacion() -> None:
        contenedor = page.locator("#s2id_P3_TipoDocumentoIdentificacion")
        contenedor.click()
        entrada = contenedor.locator("input")
        entrada.press_sequentially("Tributa", delay=200)
        page.locator(".select2-results li").filter(
            has_text="Número de Identificacion Tributaria"
        ).click()

    fijo(page, "3", "Tipo de identificación importador", tipo_identificacion)
    campo(page, "3", "NumeroIdentificacionImportador", datos.get("NumeroIdentificacionImportador"), lambda v: (page.locator("#P3_NumeroDocumento_I").click(), page.locator("#P3_NumeroDocumento_I").fill(v)))

    def pais_importador() -> None:
        pais = valor_pais(page, "3", "PaisImportador", datos.get("PaisImportador"))
        if pais is not None:
            seleccionar_pais_select2_directo(page, "#s2id_P3_PaisEmisionDocumento", pais)

    paso(page, "Paso 3 - País importador", pais_importador)
    fijo(page, "3", "Siguiente", lambda: page.locator("#step3").get_by_text("Siguiente").click())

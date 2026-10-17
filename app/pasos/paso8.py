"""Paso 8: carga y clasificación de documentos."""

import logging
from pathlib import Path

from app.duca_numero import reportar_numero_duca
from app.pasos.comunes import (
    adjuntar_archivo,
    campo,
    completar_tipo_documento,
    fijo,
    seleccionar_carpeta,
    subir_y_esperar_ventana,
)
from app.pausa import pausar_para_usuario
from app.runner import paso
from app.valores import a_texto, es_vacio, normalizar

logger = logging.getLogger(__name__)


def _documento(page, ruta_archivos: Path, numero: int, categoria: str, doc: dict, campos: tuple[str, str, str], carpeta: str, exigir_exact: bool = False) -> None:
    nombre_campo, tipo_campo, numero_campo = campos
    nombre_paso = f"8 {categoria} {numero}"

    def carpeta_y_archivo() -> None:
        seleccionar_carpeta(page, carpeta)
        nombre = doc.get(nombre_campo)
        if es_vacio(nombre):
            logger.warning("Falta %s en el paso 8", nombre_campo)
            pausar_para_usuario(
                page, f"Falta {nombre_campo} en el paso 8: selecciona el archivo manualmente"
            )
            return
        ruta = ruta_archivos / a_texto(nombre)
        if not ruta.is_file():
            logger.warning("No se encuentra el archivo requerido por %s", nombre_campo)
            pausar_para_usuario(
                page,
                f"No se encuentra el archivo de {nombre_campo} en el paso 8: selecciona el archivo manualmente",
            )
            return
        adjuntar_archivo(page, ruta)

    fijo(page, nombre_paso, f"{carpeta}: carpeta y archivo", carpeta_y_archivo)
    fijo(page, nombre_paso, f"{carpeta}: subir", lambda: subir_y_esperar_ventana(page))
    def completar_tipo(tipo: str) -> None:
        texto = tipo
        if exigir_exact and normalizar(tipo) == "manifiesto de carga":
            texto = "Manifiesto de carga"
        completar_tipo_documento(page, texto, exigir_exact)

    campo(
        page,
        nombre_paso,
        tipo_campo,
        doc.get(tipo_campo),
        completar_tipo,
    )

    def llenar_numero() -> None:
        entrada = page.locator("#P8_InfoDocumentosAUX_DXPEForm_DXEFL_DXEditor7_I")
        entrada.wait_for(state="visible", timeout=10_000)
        numero_doc = doc.get(numero_campo)
        if es_vacio(numero_doc):
            logger.warning("Falta %s en el paso 8", numero_campo)
            pausar_para_usuario(
                page, f"Falta {numero_campo} en el paso 8: complétalo manualmente"
            )
        else:
            entrada.click()
            entrada.fill(a_texto(numero_doc))
        entrada.press("Tab")
        if not es_vacio(numero_doc):
            from playwright.sync_api import expect

            expect(entrada).to_have_value(a_texto(numero_doc), timeout=3_000)

    fijo(page, nombre_paso, f"{carpeta}: número de documento", llenar_numero)

    def guardar() -> None:
        entrada = page.locator("#P8_InfoDocumentosAUX_DXPEForm_DXEFL_DXEditor7_I")
        page.get_by_role("link", name="Guardar", exact=True).click()
        entrada.wait_for(state="hidden", timeout=30_000)

    fijo(page, nombre_paso, f"{carpeta}: guardar", guardar)


def ejecutar(page, datos: dict, ruta_archivos: Path, settings, reporter=None) -> None:
    fijo(
        page,
        "8",
        "Esperar administrador de archivos",
        lambda: page.locator("#fileManager").wait_for(state="visible", timeout=30_000),
    )
    reportar_numero_duca(page, reporter)
    p8 = datos if isinstance(datos, dict) else {}
    for categoria, carpeta, campos, exact in (
        (
            "facturas",
            "Facturas",
            ("NombreDocumentoFactura", "TipoDocumentoFactura", "NumeroDocumentoFactura"),
            False,
        ),
        (
            "manifiestos",
            "Manifiestos",
            ("NombreDocumentoManifiesto", "TipoDocumentoManifiesto", "NumeroDocumentoManifiesto"),
            True,
        ),
        (
            "otros",
            "Otros",
            ("NombreDocumentoBL", "TipoDocumentoManifiestoBL", "NumeroDocumentoManifiestoBL"),
            False,
        ),
    ):
        documentos = p8.get(categoria)
        if not isinstance(documentos, list):
            continue
        for indice, documento in enumerate(documentos, 1):
            _documento(
                page,
                ruta_archivos,
                indice,
                categoria.capitalize(),
                documento if isinstance(documento, dict) else {},
                campos,
                carpeta,
                exact,
            )

    fijo(
        page,
        "8",
        "Siguiente",
        lambda: page.locator("#step8 > .text-right > .btn.btn-success").click(),
    )

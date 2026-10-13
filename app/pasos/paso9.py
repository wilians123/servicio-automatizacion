"""Paso 9: equipamiento."""

import logging
import re

from app.pasos.comunes import campo, fijo, valor_pais
from app.pausa import pausar_para_usuario
from app.runner import paso

logger = logging.getLogger(__name__)


def ejecutar(page, datos: dict, settings) -> None:
    def nuevo_equipamiento() -> None:
        nuevo = page.locator("#P10_Equipamiento_DXCBtn0")
        nuevo.wait_for(state="visible", timeout=15_000)
        from playwright.sync_api import expect

        expect(nuevo).to_be_enabled()
        nuevo.click()
        page.locator("#P10_Equipamiento_DXPEForm_DXEFL_DXEditor3_CC").wait_for(
            state="visible", timeout=30_000
        )
        page.locator("#P10_Equipamiento_DXPEForm_DXEFL_DXEditor3_I").wait_for(
            state="visible", timeout=30_000
        )

    fijo(page, "9", "Nuevo equipamiento", nuevo_equipamiento)

    def tipo_equipamiento() -> None:
        entrada = page.locator("#P10_Equipamiento_DXPEForm_DXEFL_DXEditor3_I")
        entrada.wait_for(state="visible", timeout=30_000)
        entrada.click()
        entrada.press_sequentially("Contenedor", delay=200)
        page.locator("#P10_Equipamiento_DXPEForm_DXEFL_DXEditor3_CC").click()
        opcion = page.get_by_role("cell", name="Contenedor", exact=True).get_by_role("emphasis")
        opcion.wait_for(state="visible", timeout=15_000)
        opcion.click()
        from playwright.sync_api import expect

        expect(entrada).to_have_value(re.compile("^Contenedor$", re.I))

    fijo(page, "9", "Tipo de equipamiento", tipo_equipamiento)

    def tipo_carga() -> None:
        entrada = page.locator("#P10_Equipamiento_DXPEForm_DXEFL_DXEditor5_I")
        entrada.wait_for(state="visible", timeout=30_000)
        entrada.click()
        entrada.press_sequentially("Contenerizada", delay=200)
        page.locator("#P10_Equipamiento_DXPEForm_DXEFL_DXEditor5_CC").click()
        opcion = page.get_by_text("Contenerizada", exact=True)
        opcion.wait_for(state="visible", timeout=15_000)
        opcion.click()
        from playwright.sync_api import expect

        expect(entrada).to_have_value(re.compile("^Contenerizada$", re.I))

    fijo(page, "9", "Tipo de carga", tipo_carga)

    def placa_chasis(valor: str) -> None:
        selector = "#P10_Equipamiento_DXPEForm_DXEFL_DXEditor6_I"
        entrada = page.locator(selector)
        from app.pasos.comunes import esperar_campo_listo

        esperar_campo_listo(page, selector)
        entrada.fill(valor)
        from playwright.sync_api import expect

        expect(entrada).to_have_value(valor)

    campo(page, "9", "PlacaChasis", datos.get("PlacaChasis"), placa_chasis)

    def marchamo(valor: str) -> None:
        selector = "#P10_Equipamiento_DXPEForm_DXEFL_DXEditor7_I"
        entrada = page.locator(selector)
        from app.pasos.comunes import esperar_campo_listo

        esperar_campo_listo(page, selector)
        entrada.fill(valor)
        from playwright.sync_api import expect

        expect(entrada).to_have_value(valor)

    campo(page, "9", "MarchamoSat", datos.get("MarchamoSat"), marchamo)

    def tipo_contenedor() -> None:
        abrir = page.locator("#P10_Equipamiento_DXPEForm_DXEFL_DXEditor8_B-1Img")
        abrir.wait_for(state="visible", timeout=30_000)
        abrir.click()
        page.wait_for_timeout(500)
        opcion = page.locator("#P10_Equipamiento_DXPEForm_DXEFL_DXEditor8_DDD_L_LBI0T0")
        opcion.wait_for(state="visible", timeout=30_000)
        opcion.click()
        page.wait_for_timeout(500)
        eliminar = page.locator("#P10_Equipamiento_DXPEForm_DXEFL_DXEditor8_B-100")
        eliminar.wait_for(state="visible", timeout=30_000)
        from playwright.sync_api import expect

        expect(eliminar).to_be_enabled()
        eliminar.click()
        page.wait_for_timeout(600)
        expect(page.locator("#P10_Equipamiento_DXPEForm_DXEFL_DXEditor8_I")).to_have_value("")
        tamano = page.get_by_role(
            "cell", name="Tamaño del equipamiento:  *", exact=True
        ).last
        tamano.wait_for(state="visible", timeout=30_000)
        page.wait_for_timeout(200)
        tamano.click()

    fijo(page, "9", "Tipo de contenedor", tipo_contenedor)

    def tamano(valor: str) -> None:
        entrada = page.locator("#P10_Equipamiento_DXPEForm_DXEFL_DXEditor9_I")
        entrada.wait_for(state="visible", timeout=30_000)
        entrada.click()
        entrada.fill(valor)
        from playwright.sync_api import expect

        expect(entrada).to_have_value(valor)

    campo(page, "9", "TamañoContenedor", datos.get("TamañoContenedor"), tamano)

    def numero_contenedor(valor: str) -> None:
        selector = "#P10_Equipamiento_DXPEForm_DXEFL_DXEditor11_I"
        entrada = page.locator(selector)
        from app.pasos.comunes import esperar_campo_listo

        esperar_campo_listo(page, selector)
        entrada.fill(valor)
        from playwright.sync_api import expect

        expect(entrada).to_have_value(valor)

    campo(page, "9", "NumeroContenedor", datos.get("NumeroContenedor"), numero_contenedor)
    page.wait_for_timeout(200)

    def nacionalidad() -> None:
        lista_clase = page.locator("#Clase_Bultos_DDD_L_LBT")
        try:
            if lista_clase.is_visible():
                page.locator("#Descripcion_Mercaderia").click()
        except Exception:
            pass
        pais = valor_pais(page, "9", "PaisChasis", datos.get("PaisChasis"))
        if pais is None:
            return
        entrada = page.locator("#P10_Equipamiento_DXPEForm_DXEFL_DXEditor12_I")
        entrada.wait_for(state="visible", timeout=15_000)
        entrada.click()
        entrada.press_sequentially(pais.devexpress_busqueda, delay=200)
        opcion = page.get_by_role("cell", name=pais.devexpress_opcion, exact=True).filter(
            visible=True
        ).last
        opcion.wait_for(state="visible", timeout=15_000)
        opcion.scroll_into_view_if_needed()
        opcion.click()
        from playwright.sync_api import expect

        expect(entrada).to_have_value(
            re.compile(r"^" + re.escape(pais.devexpress_opcion) + r"$", re.I),
            timeout=15_000,
        )

    paso(page, "Paso 9 - Nacionalidad del remolque", nacionalidad)

    def guardar_equipamiento() -> None:
        guardar = page.locator("#P10_Equipamiento_DXPEForm_DXEFL_DXCBtn0")
        guardar.wait_for(state="visible", timeout=15_000)
        guardar.click()
        from playwright.sync_api import expect

        expect(
            page.locator("#P10_Equipamiento_DXPEForm_DXEFL_DXEditor3_I")
        ).to_be_hidden(timeout=30_000)

    fijo(page, "9", "Guardar equipamiento", guardar_equipamiento)
    fijo(
        page,
        "9",
        "Finalizar",
        lambda: page.locator("#step9 > .text-right > .btn.btn-success").click(),
    )

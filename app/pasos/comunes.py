"""Helpers de interacción portados del spec original."""

import logging
import re
from pathlib import Path

from playwright.sync_api import expect

from app.aduanas import indice_coincidencia_exacta, terminos_busqueda_aduana
from app.paises import Pais, buscar_pais
from app.pausa import pausar_para_usuario
from app.runner import paso
from app.valores import a_texto, construir_regex_opcion, es_vacio

logger = logging.getLogger(__name__)


def campo(page, numero: str, nombre: str, valor, accion) -> None:
    def ejecutar() -> None:
        if es_vacio(valor):
            logger.warning("Falta %s en el paso %s", nombre, numero)
            pausar_para_usuario(
                page,
                f"Falta {nombre} en el paso {numero}: complétalo manualmente",
            )
            return
        accion(a_texto(valor))

    paso(page, f"Paso {numero} - {nombre}", ejecutar)


def fijo(page, numero: str, nombre: str, accion) -> None:
    paso(page, f"Paso {numero} - {nombre}", accion)


def pausa_operador(page, numero: str, nombre: str, motivo: str) -> None:
    def ejecutar() -> None:
        logger.warning("Revisión manual requerida: %s en el paso %s", nombre, numero)
        pausar_para_usuario(page, motivo)

    paso(page, f"Paso {numero} - {nombre}", ejecutar)


def valor_pais(page, numero: str, nombre: str, valor) -> Pais | None:
    if es_vacio(valor):
        logger.warning("Falta %s en el paso %s", nombre, numero)
        pausar_para_usuario(
            page, f"Falta {nombre} en el paso {numero}: complétalo manualmente"
        )
        return None
    pais = buscar_pais(valor)
    if pais is None:
        logger.warning("País sin mapeo para %s en el paso %s", nombre, numero)
        pausar_para_usuario(
            page,
            f"No se reconoce el país de {nombre} en el paso {numero}: complétalo manualmente",
        )
    return pais


def esperar_mensaje_rojo(page, texto: re.Pattern, timeout: int = 30_000) -> None:
    page.get_by_text(texto).filter(visible=True).first.wait_for(
        state="visible", timeout=timeout
    )


def esperar_selectores_paso1_listos(page) -> None:
    selectores = ["#s2id_P1_DepositoDestino", "#s2id_P1_LugarDesembarque"]
    page.wait_for_function(
        """ids => ids.every(id => {
          const elemento = document.querySelector(id);
          if (!elemento || !document.body.contains(elemento)) return false;
          const estilo = getComputedStyle(elemento);
          const rect = elemento.getBoundingClientRect();
          return estilo.display !== 'none' && estilo.visibility !== 'hidden' &&
            rect.width > 0 && rect.height > 0;
        })""",
        arg=selectores,
        timeout=30_000,
    )
    page.wait_for_function(
        """ids => ids.every(id => {
          const contenedor = document.querySelector(id);
          if (!contenedor || !document.body.contains(contenedor)) return false;
          if ((contenedor.textContent ?? '').match(/por favor espere/i)) return false;
          const control = contenedor.querySelector('input, select, button');
          return !control || !control.disabled;
        })""",
        arg=selectores,
        timeout=30_000,
    )


def esperar_campo_listo(page, selector: str, timeout: int = 20_000) -> None:
    campo_locator = page.locator(selector)
    campo_locator.wait_for(state="visible", timeout=timeout)
    expect(campo_locator).not_to_have_value(re.compile("por favor espere", re.I), timeout=timeout)
    expect(campo_locator).to_be_editable(timeout=timeout)


def esperar_select2_listo(page, selector: str, timeout: int = 30_000):
    contenedor = page.locator(selector)
    contenedor.wait_for(state="visible", timeout=timeout)
    page.wait_for_function(
        """id => {
          const elemento = document.querySelector(id);
          if (!elemento || !document.body.contains(elemento)) return false;
          if (/por favor espere/i.test(elemento.textContent ?? '')) return false;
          return true;
        }""",
        arg=selector,
        timeout=timeout,
    )
    return contenedor


def seleccionar_select2(page, selector: str, texto: str, opcion: str, timeout: int = 30_000) -> None:
    contenedor = esperar_select2_listo(page, selector, timeout)
    contenedor.click()
    entrada = page.locator(".select2-drop:visible input.select2-input").last
    entrada.wait_for(state="visible", timeout=timeout)
    expect(entrada).to_be_editable(timeout=timeout)
    entrada.fill("")
    entrada.press_sequentially(texto, delay=200)
    resultado = page.locator(".select2-results li:visible").filter(
        has_text=construir_regex_opcion(opcion)
    ).first
    resultado.wait_for(state="visible", timeout=timeout)
    resultado.click()


def seleccionar_pais_select2_directo(page, selector: str, pais: Pais) -> None:
    contenedor = page.locator(selector)
    contenedor.click()
    entrada = contenedor.locator("input")
    entrada.press_sequentially(pais.select2_busqueda, delay=200)
    page.locator(".select2-results li").filter(
        has_text=construir_regex_opcion(pais.select2_opcion)
    ).click()


def seleccionar_aduana(page, selector: str, valor: str) -> bool:
    # Paso 1 ya espera el mensaje rojo de validación y su pausa de estabilización;
    # abrir el control visible inmediatamente evita bloquear antes del clic por
    # texto transitorio que puede permanecer en el contenedor Select2.
    contenedor = page.locator(selector)
    contenedor.wait_for(state="visible", timeout=30_000)
    terminos = terminos_busqueda_aduana(valor)
    segmentos = re.split(r"\s*[-–—]\s*", valor.strip())
    codigo = segmentos[1].strip() if len(segmentos) >= 3 else ""
    # Para códigos alfabéticos (p. ej. ST), comienza por el nombre distintivo.
    # Los códigos numéricos conservan prioridad para la aduana de destino.
    if codigo and not codigo.isdigit():
        terminos = [termino for termino in terminos if termino != codigo] + [codigo]
    contenedor.click()
    entrada = page.locator(".select2-drop:visible input.select2-input").last
    entrada.wait_for(state="visible", timeout=30_000)
    expect(entrada).to_be_editable(timeout=30_000)
    for indice_termino, termino in enumerate(terminos):
        entrada.fill("")
        entrada.press_sequentially(termino, delay=200)
        resultados = page.locator(".select2-results li:visible")
        patron_termino = re.compile(
            r"(?<!\w)" + re.escape(termino) + r"(?!\w)", re.IGNORECASE
        )
        try:
            resultados.filter(has_text=patron_termino).first.wait_for(
                state="visible", timeout=30_000
            )
        except Exception:
            if indice_termino < len(terminos) - 1:
                continue
            return False
        textos = resultados.all_text_contents()
        encontrado = indice_coincidencia_exacta(valor, textos)
        if encontrado is None:
            if codigo:
                patron_codigo = re.compile(
                    r"(?<!\w)" + re.escape(codigo) + r"(?!\w)", re.IGNORECASE
                )
                coincidencias = [
                    indice
                    for indice, texto in enumerate(textos)
                    if patron_codigo.search(texto)
                ]
                if len(coincidencias) == 1:
                    encontrado = coincidencias[0]
        if encontrado is not None:
            resultados.nth(encontrado).click()
            return True
    return False


def seleccionar_aduana_por_codigo(page, selector: str, codigo: str) -> bool:
    """Busca por el código numérico y elige una única opción que lo contenga."""
    contenedor = esperar_select2_listo(page, selector)
    contenedor.click()
    entrada = page.locator(".select2-drop:visible input.select2-input").last
    entrada.wait_for(state="visible", timeout=30_000)
    expect(entrada).to_be_editable(timeout=30_000)
    entrada.fill("")
    entrada.press_sequentially(codigo, delay=200)
    resultados = page.locator(".select2-results li:visible")
    patron_codigo = re.compile(r"(?<!\d)" + re.escape(codigo) + r"(?!\d)")
    try:
        resultados.filter(has_text=patron_codigo).first.wait_for(
            state="visible", timeout=30_000
        )
    except Exception:
        return False

    coincidencias = [
        indice
        for indice, texto in enumerate(resultados.all_text_contents())
        if patron_codigo.search(texto)
    ]
    if len(coincidencias) != 1:
        return False
    resultados.nth(coincidencias[0]).click()
    return True


def seleccionar_combo_paso9(page, input_selector: str, lista_selector: str, texto: str) -> None:
    entrada = page.locator(input_selector)
    esperar_campo_listo(page, input_selector)
    entrada.click()
    entrada.fill(texto)
    opcion = page.locator(lista_selector).filter(
        has_text=construir_regex_opcion(texto)
    ).first
    opcion.wait_for(state="visible", timeout=15_000)
    opcion.click()
    expect(entrada).to_have_value(construir_regex_opcion(texto))


def seleccionar_carpeta(page, nombre: str) -> None:
    patron = re.compile(r"^\s*" + re.escape(nombre) + r"\s*$")
    texto = page.locator(
        'div[id^="fileManager_Splitter_Folders_N0_"] span.dxtv-ndTxt'
    ).filter(has_text=patron).first
    texto.wait_for(state="visible", timeout=30_000)
    texto.click()
    expect(page.locator("#fileManager_BreadCrumbs .dxfm-bcLastItem")).to_have_text(
        patron, timeout=15_000
    )


def adjuntar_archivo(page, ruta: Path) -> None:
    input_archivo = page.locator("#fileManager_Splitter_Upload_TextBox0_Input")
    examinar = page.locator("#fileManager_Splitter_Upload_Browse0")
    examinar.wait_for(state="visible", timeout=15_000)
    input_archivo.set_input_files(str(ruta))
    expect(page.locator("#fileManager_Splitter_UploadButton")).not_to_have_class(
        re.compile("dxfm-uploadDisable"), timeout=15_000
    )


def subir_y_esperar_ventana(page) -> None:
    subir = page.locator("#fileManager_Splitter_UploadButton")
    subir.wait_for(state="visible", timeout=10_000)
    expect(subir).not_to_have_class(re.compile("dxfm-uploadDisable"), timeout=15_000)
    subir.click()
    page.locator("#P8_InfoDocumentosAUX_DXPEForm_DXEFL_DXEditor7_I").wait_for(
        state="visible", timeout=60_000
    )


def completar_tipo_documento(page, tipo: str, exigir_texto_exact: bool = False) -> None:
    selector_tipo = "#P8_InfoDocumentosAUX_DXPEForm_DXEFL_DXEditor6_I"
    selector_lista = '[id^="P8_InfoDocumentosAUX_DXPEForm_DXEFL_DXEditor6_DDD_L_LBI"]'
    entrada = page.locator(selector_tipo)
    entrada.wait_for(state="visible", timeout=10_000)
    actual = entrada.input_value()
    patron = re.compile(re.escape(tipo), re.I)
    coincide = (
        actual.strip().casefold() == tipo.strip().casefold()
        if exigir_texto_exact
        else patron.search(actual) is not None
    )
    if coincide:
        return

    entrada.click()
    patron_opcion_exacta = re.compile(r"^\s*" + re.escape(tipo) + r"\s*$", re.I)
    opcion = page.locator(selector_lista).filter(
        has_text=patron_opcion_exacta if exigir_texto_exact else patron
    ).first
    try:
        opcion.wait_for(state="visible", timeout=4_000)
        visible = True
    except Exception:
        visible = False
    if not visible:
        entrada.fill(tipo)
        opcion.wait_for(state="visible", timeout=8_000)
    opcion.click()
    expect(entrada).to_have_value(
        tipo if exigir_texto_exact else patron, timeout=5_000
    )


def completar_numero_y_guardar(page, numero) -> None:
    entrada = page.locator("#P8_InfoDocumentosAUX_DXPEForm_DXEFL_DXEditor7_I")
    entrada.wait_for(state="visible", timeout=10_000)
    if not es_vacio(numero):
        entrada.click()
        entrada.fill(a_texto(numero))
    entrada.press("Tab")
    if not es_vacio(numero):
        expect(entrada).to_have_value(a_texto(numero), timeout=3_000)
    page.get_by_role("link", name="Guardar", exact=True).click()
    entrada.wait_for(state="hidden", timeout=30_000)

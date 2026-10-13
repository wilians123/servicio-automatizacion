"""Paso 7: mercancías, países y gastos."""

import logging
import re
from decimal import Decimal, InvalidOperation

from app.pasos.comunes import campo, fijo, valor_pais
from app.pausa import pausar_para_usuario
from app.plan import resolver_otros_gastos
from app.runner import paso
from app.valores import a_texto, construir_regex_opcion, es_vacio

logger = logging.getLogger(__name__)


def _es_cero(valor) -> bool:
    try:
        return Decimal(a_texto(valor).strip()) == 0
    except InvalidOperation:
        return False


def _agregar_mercancia(page, *, hay_mas: bool) -> None:
    valor_transaccion = page.locator("#VALOR_TRANSACCION_TOTAL_I")
    try:
        page.locator("#cover-spin").wait_for(state="hidden", timeout=30_000)
    except Exception:
        pass
    try:
        page.locator("#p7-btagregarmercancia").click()
        if not hay_mas:
            valor_transaccion.wait_for(state="visible", timeout=60_000)
        else:
            page.locator("#cover-spin").wait_for(state="hidden", timeout=30_000)
    except Exception as error:
        if page.is_closed():
            raise
        logger.error("Agregar mercancía requiere revisión manual")
        pausar_para_usuario(
            page,
            "Paso 7 detenido: agrega la mercancía manualmente y presiona Resume cuando aparezca el valor transaccional.",
        )
        if not hay_mas:
            valor_transaccion.wait_for(state="visible", timeout=60_000)


def _mercancia(page, mercancia: dict, indice: int, *, hay_mas: bool) -> None:
    numero = f"7 mercancía {indice}"
    partida = mercancia.get("PartidaArancelaria")

    def elegir_partida(valor: str) -> None:
        partida_limpia = re.sub(r"[^0-9]", "", valor)[:10]
        entrada = page.locator("#Clasificacion_Arancelaria_I")
        entrada.click()
        entrada.fill("")
        entrada.press_sequentially(partida_limpia, delay=200)
        patron_partida = re.compile(
            r"(?<!\d)" + re.escape(partida_limpia) + r"(?!\d)"
        )
        opciones = page.locator(
            "#Clasificacion_Arancelaria_DDD_L_LBT tr:visible"
        ).filter(has_text=patron_partida)
        opciones.first.wait_for(state="visible", timeout=30_000)
        if opciones.count() != 1:
            raise ValueError("La partida arancelaria no tiene una opción única")
        opciones.first.click()

    campo(page, numero, "PartidaArancelaria", partida, elegir_partida)
    page.wait_for_timeout(200)

    def descripcion(valor: str) -> None:
        page.get_by_text("Agregar Mercancía").click()
        entrada = page.locator("#Descripcion_Mercaderia")
        entrada.click()
        entrada.fill(valor)

    campo(page, numero, "DescripcionMercancia", mercancia.get("DescripcionMercancia"), descripcion)
    page.wait_for_timeout(200)

    def cantidad(valor: str) -> None:
        entrada = page.locator("#Numero_Bultos_I")
        entrada.click()
        entrada.fill(valor)
        page.wait_for_function(
            "valor => { const input = document.querySelector('#Numero_Bultos_I'); return input && input.value === valor; }",
            arg=valor,
            timeout=3000,
        )

    campo(page, numero, "CantidadMercancia", mercancia.get("CantidadMercancia"), cantidad)
    page.wait_for_timeout(200)

    def clase(valor: str) -> None:
        entrada = page.locator("#Clase_Bultos_I")
        entrada.click()
        entrada.press_sequentially(valor, delay=200)
        fila = page.locator("#Clase_Bultos_DDD_L_LBT tr").filter(has_text=valor).first
        fila.wait_for(state="visible", timeout=5000)
        fila.click()
        page.wait_for_function(
            "valor => { const hidden = document.querySelector('#Clase_Bultos_DDD_L_VI'); return hidden && hidden.value.includes(valor); }",
            arg=valor,
            timeout=5000,
        )

    campo(page, numero, "ClaseMercancia", mercancia.get("ClaseMercancia"), clase)
    page.wait_for_timeout(200)

    def pais_origen() -> None:
        lista_clase = page.locator("#Clase_Bultos_DDD_L_LBT")
        try:
            if lista_clase.is_visible():
                page.locator("#Descripcion_Mercaderia").click()
        except Exception:
            pass
        pais = valor_pais(page, numero, "PaisMercancia", mercancia.get("PaisMercancia"))
        if pais is None:
            return
        contenedor = page.locator("#s2id_Pais_Origen")
        contenedor.scroll_into_view_if_needed()
        contenedor.wait_for(state="visible", timeout=5000)
        contenedor.click()
        entrada = contenedor.locator("input")
        entrada.press_sequentially(pais.select2_busqueda, delay=200)
        page.locator(".select2-results li").filter(
            has_text=construir_regex_opcion(pais.select2_opcion)
        ).click()
        page.wait_for_function(
            "codigo => { const select = document.querySelector('#Pais_Origen'); return select && select.value === codigo; }",
            arg=pais.iso2,
            timeout=5000,
        )

    paso(page, f"Paso {numero} - País de origen", pais_origen)
    page.wait_for_timeout(200)

    def peso(valor: str) -> None:
        peso_limpio = format(Decimal(valor).quantize(Decimal("0.01")), "f")
        entrada = page.locator("#Peso_Bruto_I")
        entrada.click()
        entrada.fill(peso_limpio)
        page.wait_for_function(
            "valor => { const input = document.querySelector('#Peso_Bruto_I'); return input && input.value === valor; }",
            arg=peso_limpio,
            timeout=3000,
        )
        entrada.press("Tab")

    campo(page, numero, "PesoMercancia", mercancia.get("PesoMercancia"), peso)
    fijo(
        page,
        numero,
        "Agregar mercancía",
        lambda: _agregar_mercancia(page, hay_mas=hay_mas),
    )


def ejecutar(page, datos: dict, settings) -> None:
    mercancias = datos.get("mercancias")
    if not isinstance(mercancias, list) or not mercancias:
        logger.warning("Falta mercancias en el paso 7")
        pausar_para_usuario(page, "Falta mercancias en el paso 7: complétalas manualmente")
    else:
        total_mercancias = len(mercancias)
        for indice, mercancia in enumerate(mercancias, 1):
            _mercancia(
                page,
                mercancia if isinstance(mercancia, dict) else {},
                indice,
                hay_mas=indice < total_mercancias,
            )

    # Los gastos se rellenan únicamente después de recorrer la lista completa.
    page.locator("#VALOR_TRANSACCION_TOTAL_I").wait_for(state="visible", timeout=60_000)

    gastos = datos.get("gastos") if isinstance(datos.get("gastos"), dict) else {}
    transporte = gastos.get("GastosTransporte")
    if es_vacio(transporte) or _es_cero(transporte):
        transporte = "0.01"
    seguro = gastos.get("GastosSeguro")
    if es_vacio(seguro):
        seguro = 0
    otros = resolver_otros_gastos(gastos)
    if es_vacio(otros):
        otros = 0

    campo(page, "7", "ValorFOB", gastos.get("ValorFOB"), lambda v: (page.locator("#VALOR_TRANSACCION_TOTAL_I").click(), page.locator("#VALOR_TRANSACCION_TOTAL_I").fill(v)))
    campo(page, "7", "GastosTransporte", transporte, lambda v: (page.locator("#VALOR_GASTO_TRANSPORTE_TOTAL_I").click(), page.locator("#VALOR_GASTO_TRANSPORTE_TOTAL_I").fill(v)))
    campo(page, "7", "GastosSeguro", seguro, lambda v: (page.locator("#VALOR_GASTO_SEGURO_TOTAL_I").click(), page.locator("#VALOR_GASTO_SEGURO_TOTAL_I").fill(v)))
    campo(page, "7", "OtrosGastos", otros, lambda v: (page.locator("#VALOR_GASTO_OTROS_TOTAL_I").click(), page.locator("#VALOR_GASTO_OTROS_TOTAL_I").fill(v)))
    page.wait_for_timeout(500)
    fijo(page, "7", "Siguiente", lambda: page.locator("#btnNext7").get_by_text("Siguiente").click())

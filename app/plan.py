"""Plan offline de pausas previsibles; no incluye valores del embarque."""

from pathlib import Path

from app.aduanas import terminos_busqueda_aduana
from app.contrato import paso_datos
from app.paises import buscar_pais
from app.valores import es_vacio


def resolver_otros_gastos(gastos: dict):
    valor = gastos.get("OtrosGastos")
    if es_vacio(valor) and not es_vacio(gastos.get("GastosTransporte")) and not es_vacio(gastos.get("GastosSeguro")):
        return 0
    return valor


def planificar_pausas(datos: dict, ruta_archivos: str | Path | None = None) -> dict:
    pausas: list[str] = []
    aduanas: list[dict[str, object]] = []

    def requerido(paso: str, campo: str, valor) -> None:
        if es_vacio(valor):
            pausas.append(f"Paso {paso}: {campo}")

    p1 = paso_datos(datos, "paso1")
    for campo in ("AduanaInicio", "AduanaDestino", "Observaciones"):
        requerido("1", campo, p1.get(campo))
    for campo in ("AduanaInicio", "AduanaDestino"):
        valor = p1.get(campo)
        if not es_vacio(valor):
            aduanas.append({"campo": campo, "terminos": terminos_busqueda_aduana(str(valor))})

    for numero, nombre, campos, paises in (
        ("2", "paso2", ("NombreExportador", "DomicilioExportador"), ("PaisExportador",)),
        ("3", "paso3", ("NombreImportador", "DomicilioImportador", "NumeroIdentificacionImportador"), ("PaisImportador",)),
    ):
        paso = paso_datos(datos, nombre)
        for campo in campos:
            requerido(numero, campo, paso.get(campo))
        for campo in paises:
            valor = paso.get(campo)
            requerido(numero, campo, valor)
            if not es_vacio(valor) and buscar_pais(valor) is None:
                pausas.append(f"Paso {numero}: {campo} (país sin mapeo)")

    for numero, nombre, campos in (
        ("5", "paso5", ("CodigoTransportista", "PlacaTransporte")),
        ("6", "paso6", ("LicenciaConductor",)),
    ):
        paso = paso_datos(datos, nombre)
        for campo in campos:
            requerido(numero, campo, paso.get(campo))

    p7 = paso_datos(datos, "paso7")
    mercancias = p7.get("mercancias")
    if isinstance(mercancias, list):
        for indice, mercancia in enumerate(mercancias, 1):
            fila = mercancia if isinstance(mercancia, dict) else {}
            for campo in (
                "PartidaArancelaria",
                "DescripcionMercancia",
                "CantidadMercancia",
                "ClaseMercancia",
                "PaisMercancia",
                "PesoMercancia",
            ):
                requerido(f"7 mercancía {indice}", campo, fila.get(campo))
            pais = fila.get("PaisMercancia")
            if not es_vacio(pais) and buscar_pais(pais) is None:
                pausas.append(f"Paso 7 mercancía {indice}: PaisMercancia (país sin mapeo)")

    gastos = p7.get("gastos") if isinstance(p7.get("gastos"), dict) else {}
    for campo in ("ValorFOB", "GastosTransporte", "GastosSeguro"):
        requerido("7", campo, gastos.get(campo))
    if es_vacio(resolver_otros_gastos(gastos)):
        requerido("7", "OtrosGastos", None)

    if ruta_archivos is not None:
        raiz_archivos = Path(ruta_archivos)
    else:
        raiz_archivos = None
    p8 = paso_datos(datos, "paso8")
    for categoria, campos in (
        ("facturas", ("NombreDocumentoFactura", "TipoDocumentoFactura", "NumeroDocumentoFactura")),
        ("manifiestos", ("NombreDocumentoManifiesto", "TipoDocumentoManifiesto", "NumeroDocumentoManifiesto")),
        ("otros", ("NombreDocumentoBL", "TipoDocumentoManifiestoBL", "NumeroDocumentoManifiestoBL")),
    ):
        documentos = p8.get(categoria)
        if not isinstance(documentos, list):
            continue
        for indice, documento in enumerate(documentos, 1):
            fila = documento if isinstance(documento, dict) else {}
            for campo in campos:
                requerido(f"8 {categoria} {indice}", campo, fila.get(campo))
            nombre_archivo = fila.get(campos[0])
            if raiz_archivos is not None and not es_vacio(nombre_archivo):
                if not (raiz_archivos / str(nombre_archivo)).is_file():
                    pausas.append(f"Paso 8 {categoria} {indice}: archivo {campos[0]} no encontrado")

    p9 = paso_datos(datos, "paso9")
    for campo in ("PlacaChasis", "MarchamoSat", "TamañoContenedor", "NumeroContenedor", "PaisChasis"):
        requerido("9", campo, p9.get(campo))
    pais_chasis = p9.get("PaisChasis")
    if not es_vacio(pais_chasis) and buscar_pais(pais_chasis) is None:
        pausas.append("Paso 9: PaisChasis (país sin mapeo)")

    return {"pausas": pausas, "aduanas": aduanas}

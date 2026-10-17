from pathlib import Path

from app.contrato import cargar_contrato
from app.paises import buscar_pais


def test_mapeo_por_nombre_iso_y_alias_salvador():
    assert buscar_pais("Estados Unidos").iso2 == "US"
    assert buscar_pais("US").select2_opcion == "Estados Unidos"
    assert buscar_pais("CO").nombre == "Colombia"
    assert buscar_pais("SALVADOR").devexpress_opcion == "El Salvador"
    assert buscar_pais("país inventado") is None


def test_aliases_espanoles_se_escriben_con_la_opcion_literal_de_sieca():
    opciones = {
        "Turquía": "Turkey",
        "Reino Unido": "United Kingdom",
        "Brasil": "Brazil",
        "República Checa": "czech republic",
        "Chipre": "cyprus",
        "Dinamarca": "denmark",
        "República Dominicana": "Dominican Republic",
        "Francia": "France",
        "Alemania": "Germany",
        "Irlanda": "ireland",
        "Italia": "Italy",
        "Ucrania": "Ukraine",
        "Korea": "Korea, Republic of",
        "Estados Unidos": "Estados Unidos",
    }
    for entrada, opcion in opciones.items():
        pais = buscar_pais(entrada)
        assert pais is not None
        assert pais.select2_opcion == opcion
        assert pais.devexpress_opcion == opcion


def test_paises_adicionales_tambien_tienen_opcion_en_ingles():
    opciones = {
        "Canadá": "Canada",
        "Japón": "Japan",
        "Países Bajos": "Netherlands",
        "España": "Spain",
        "Bélgica": "Belgium",
        "India": "India",
        "Argentina": "Argentina",
        "Chile": "Chile",
        "Portugal": "Portugal",
        "Australia": "Australia",
    }
    for entrada, opcion in opciones.items():
        pais = buscar_pais(entrada)
        assert pais is not None
        assert pais.select2_opcion == opcion


def test_paises_de_los_tres_fixtures_estan_en_la_tabla():
    root = Path(__file__).resolve().parents[1]
    for indice in range(1, 4):
        datos = cargar_contrato(root / "contrato" / "fixtures" / f"embarque_{indice}.json")
        paso2 = datos.get("paso2", {})
        paso3 = datos.get("paso3", {})
        assert buscar_pais(paso2.get("PaisExportador")) is not None
        assert buscar_pais(paso3.get("PaisImportador")) is not None
        for mercancia in datos.get("paso7", {}).get("mercancias", []):
            assert buscar_pais(mercancia.get("PaisMercancia")) is not None

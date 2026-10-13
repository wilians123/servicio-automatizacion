from pathlib import Path

from app.contrato import cargar_contrato
from app.paises import buscar_pais


def test_mapeo_por_nombre_iso_y_alias_salvador():
    assert buscar_pais("Estados Unidos").iso2 == "US"
    assert buscar_pais("US").select2_opcion == "Estados Unidos"
    assert buscar_pais("CO").nombre == "Colombia"
    assert buscar_pais("SALVADOR").devexpress_opcion == "El Salvador"
    assert buscar_pais("país inventado") is None


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

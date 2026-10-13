from decimal import Decimal

from app.valores import a_texto, construir_regex_opcion, es_vacio, normalizar


def test_a_texto_preserva_valores_y_decimales():
    assert a_texto("0012.30") == "0012.30"
    assert a_texto(Decimal("19428.595")) == "19428.595"
    assert a_texto(Decimal("1.2300E+3")) == "1230.0"
    assert a_texto(21) == "21"


def test_vacio_y_normalizacion():
    assert es_vacio(None)
    assert es_vacio("  ")
    assert not es_vacio(0)
    assert normalizar("  Aduana   ANGUIATÚ ") == "aduana anguiatu"


def test_regex_opcion_conserva_espacios_internos_del_original():
    patron = construir_regex_opcion("El Salvador")
    assert patron.fullmatch(" El Salvador ")
    assert not patron.fullmatch("El   Salvador")

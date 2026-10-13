from app.aduanas import indice_coincidencia_exacta, terminos_busqueda_aduana


def test_busqueda_aduana_prioriza_codigo_y_usa_nombre_distintivo():
    assert terminos_busqueda_aduana(
        "TERRESTRE ANGUIATÚ - 08 - ADUANA PORTUARIA"
    ) == ["08", "ANGUIATÚ"]
    assert terminos_busqueda_aduana(
        "ADUANA SANTO TOMAS DE CASTILLA - ST - ADUANA PORTUARIA"
    ) == ["ST", "SANTO"]


def test_coincidencia_ignora_acentos_mayusculas_y_espacios():
    assert indice_coincidencia_exacta(
        "TERRESTRE ANGUIATÚ - 08 - ADUANA PORTUARIA",
        ["otra", " terrestre  Anguiatu - 08 - aduana portuaria "],
    ) == 1
    assert indice_coincidencia_exacta("Aduana X", ["ADUANA X", "aduana x"]) is None

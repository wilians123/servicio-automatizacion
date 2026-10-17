"""Alias de entrada y opciones literales de país reconocidas por SIECA."""

from dataclasses import dataclass

from app.valores import normalizar


@dataclass(frozen=True)
class Pais:
    nombre: str
    iso2: str
    alias: tuple[str, ...]
    select2_busqueda: str
    select2_opcion: str
    devexpress_busqueda: str
    devexpress_opcion: str


def _pais(nombre: str, iso2: str, *alias: str) -> Pais:
    """Construye un mapeo usando la opción literal del portal para ambos controles."""
    return Pais(nombre, iso2, (nombre, iso2, *alias), nombre, nombre, nombre, nombre)


PAISES = (
    _pais("Guatemala", "GT"),
    _pais("El Salvador", "SV", "SALVADOR"),
    _pais("Honduras", "HN"),
    _pais("Nicaragua", "NI"),
    _pais("Costa Rica", "CR"),
    _pais("Panama", "PA", "Panamá"),
    # SIECA presenta esta opción en español; conservarla es una excepción requerida.
    Pais("Estados Unidos", "US", ("Estados Unidos", "United States", "USA", "US"), "Estados", "Estados Unidos", "Estados", "Estados Unidos"),
    _pais("Mexico", "MX", "México"),
    _pais("Colombia", "CO"),
    _pais("China", "CN"),
    _pais("Turkey", "TR", "Turquia", "Turquía", "Türkiye"),
    _pais("United Kingdom", "GB", "Reino Unido", "UK", "Great Britain", "Britain"),
    _pais("Brazil", "BR", "Brasil"),
    _pais("czech republic", "CZ", "Czech Republic", "República Checa", "Republica Checa", "Czechia"),
    _pais("cyprus", "CY", "Cyprus", "Chipre"),
    _pais("denmark", "DK", "Denmark", "Dinamarca"),
    _pais("Dominican Republic", "DO", "República Dominicana", "Republica Dominicana"),
    _pais("France", "FR", "Francia"),
    _pais("Germany", "DE", "Alemania"),
    _pais("ireland", "IE", "Irlanda", "Ireland"),
    _pais("Italy", "IT", "Italia"),
    _pais("Korea, Republic of", "KR", "Korea", "South Korea", "Republic of Korea", "Corea del Sur", "Corea"),
    _pais("Ukraine", "UA", "Ucrania"),
    # Diez países adicionales frecuentes en el comercio internacional.
    _pais("Canada", "CA", "Canadá"),
    _pais("Japan", "JP", "Japón"),
    _pais("Netherlands", "NL", "Países Bajos", "Paises Bajos", "Holland"),
    _pais("Spain", "ES", "España"),
    _pais("Belgium", "BE", "Bélgica", "Belgica"),
    _pais("India", "IN"),
    _pais("Argentina", "AR"),
    _pais("Chile", "CL"),
    _pais("Portugal", "PT"),
    _pais("Australia", "AU"),
)

_POR_ALIAS = {
    normalizar(alias): pais
    for pais in PAISES
    for alias in pais.alias
}


def buscar_pais(valor) -> Pais | None:
    if valor is None:
        return None
    return _POR_ALIAS.get(normalizar(str(valor)))

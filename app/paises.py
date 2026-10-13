"""Alias observados y opciones literales para los controles de países."""

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


PAISES = (
    Pais("Guatemala", "GT", ("Guatemala", "GT"), "Guatemala", "Guatemala", "Guatemala", "Guatemala"),
    Pais("El Salvador", "SV", ("El Salvador", "SV", "SALVADOR"), "Salva", "El Salvador", "Salvador", "El Salvador"),
    Pais("Honduras", "HN", ("Honduras", "HN"), "Honduras", "Honduras", "Honduras", "Honduras"),
    Pais("Nicaragua", "NI", ("Nicaragua", "NI"), "Nicaragua", "Nicaragua", "Nicaragua", "Nicaragua"),
    Pais("Costa Rica", "CR", ("Costa Rica", "CR"), "Costa", "Costa Rica", "Costa Rica", "Costa Rica"),
    Pais("Panamá", "PA", ("Panamá", "Panama", "PA"), "Panam", "Panamá", "Panamá", "Panamá"),
    Pais("Estados Unidos", "US", ("Estados Unidos", "United States", "USA", "US"), "Estados", "Estados Unidos", "Estados", "Estados Unidos"),
    Pais("México", "MX", ("México", "Mexico", "MX"), "Méxic", "México", "México", "México"),
    Pais("Colombia", "CO", ("Colombia", "CO"), "Colombia", "Colombia", "Colombia", "Colombia"),
    Pais("China", "CN", ("China", "CN"), "China", "China", "China", "China"),
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

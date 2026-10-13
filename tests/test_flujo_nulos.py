from pathlib import Path

from app.contrato import cargar_contrato, paso_datos
from app.pasos.comunes import campo
from app.plan import planificar_pausas, resolver_otros_gastos


class FakePage:
    def __init__(self):
        self.pauses = 0

    def is_closed(self):
        return False

    def evaluate(self, *args, **kwargs):
        return None

    def pause(self):
        self.pauses += 1


def test_campo_null_pausa_con_nombre_de_campo_sin_dato_de_embarque():
    page = FakePage()
    campo(page, "3", "NumeroIdentificacionImportador", None, lambda _: None)
    assert page.pauses == 1


def test_otros_gastos_null_solo_se_convierte_en_cero_con_ambos_gastos():
    assert resolver_otros_gastos(
        {"OtrosGastos": None, "GastosTransporte": 0, "GastosSeguro": 0}
    ) == 0
    assert resolver_otros_gastos(
        {"OtrosGastos": None, "GastosTransporte": None, "GastosSeguro": 0}
    ) is None
    assert resolver_otros_gastos(
        {"OtrosGastos": "12.30", "GastosTransporte": None, "GastosSeguro": None}
    ) == "12.30"


def test_tres_fixtures_cargan_y_generan_plan_sin_error():
    root = Path(__file__).resolve().parents[1]
    for indice in range(1, 4):
        datos = cargar_contrato(root / "contrato" / "fixtures" / f"embarque_{indice}.json")
        archivos = root / "test_data" / f"embarque_{indice}"
        plan = planificar_pausas(datos, archivos)
        assert isinstance(plan["pausas"], list)
        assert isinstance(plan["aduanas"], list)
        assert plan["aduanas"]
    assert paso_datos({}, "paso1") == {}

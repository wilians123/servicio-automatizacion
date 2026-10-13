import json
import threading
import time

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.ejecucion import GestorEjecuciones, MENSAJE_PAUSA_FINAL
from app.api import main as api


class FakePage:
    def __init__(self):
        self.closed = False
        self.notices = []

    def is_closed(self):
        return self.closed

    def evaluate(self, script, value=None):
        self.notices.append(value)


class FakeContext:
    def __init__(self):
        self.pages = [FakePage()]
        self.closed = False

    def close(self):
        self.closed = True


def wait_for(predicate, timeout=2):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return
        time.sleep(0.01)
    assert predicate()


def manager_at(tmp_path, flow):
    context = FakeContext()
    manager = GestorEjecuciones(
        Settings(sieca_user="", sieca_password="", data_dir=tmp_path),
        flow_runner=flow,
        browser_factory=lambda settings: context,
        login_runner=lambda page, settings: None,
    )
    return manager, context


def test_start_valido_y_segundo_run_ocupado(tmp_path):
    entered = threading.Event()
    release = threading.Event()

    def flow(page, datos, carpeta, settings, reporter, pausador):
        entered.set()
        release.wait(2)

    manager, _ = manager_at(tmp_path, flow)
    api.gestor = manager
    client = TestClient(api.app)
    response = client.post("/automation/start", data={"datos": '{"paso1":{}}'})
    assert response.status_code == 202
    assert response.json()["ok"] is True
    run_id = response.json()["id"]
    assert entered.wait(1)
    assert client.get(f"/automation/{run_id}").status_code == 200
    second = client.post("/automation/start", data={"datos": "{}"})
    assert second.status_code == 409
    release.set()
    wait_for(lambda: manager.obtener(run_id)["estado"] == "finalizado")


def test_datos_invalidos_responden_400(tmp_path):
    api.gestor = manager_at(tmp_path, lambda *args: None)[0]
    response = TestClient(api.app).post("/automation/start", data={"datos": "[]"})
    assert response.status_code == 400
    assert response.json()["error"]["codigo"] == "DATOS_INVALIDOS_ERR"


def test_pausa_resume_revision_final_y_finalizado(tmp_path):
    def flow(page, datos, carpeta, settings, reporter, pausador):
        reporter("paso_inicio", nombre="Paso 1 - prueba")
        pausador.pausar(page, "dato manual")
        reporter("paso_ok", nombre="Paso 1 - prueba")
        pausador.pausar(page, MENSAJE_PAUSA_FINAL)

    manager, context = manager_at(tmp_path, flow)
    run_id = manager.iniciar({})
    wait_for(lambda: manager.obtener(run_id)["estado"] == "pausado")
    assert manager.reanudar(run_id) is True
    wait_for(lambda: manager.obtener(run_id)["estado"] == "revision_final")
    assert manager.reanudar(run_id) is True
    wait_for(lambda: manager.obtener(run_id)["estado"] == "finalizado")
    assert context.closed


def test_cancelar_durante_pausa(tmp_path):
    def flow(page, datos, carpeta, settings, reporter, pausador):
        pausador.pausar(page, "espera")

    manager, context = manager_at(tmp_path, flow)
    run_id = manager.iniciar({})
    wait_for(lambda: manager.obtener(run_id)["estado"] == "pausado")
    assert manager.cancelar_run(run_id) is True
    wait_for(lambda: manager.obtener(run_id)["estado"] == "cancelado")
    assert context.closed


def test_error_del_hilo_es_generico(tmp_path):
    def flow(*args):
        raise RuntimeError("valor embarque secreto")

    manager, _ = manager_at(tmp_path, flow)
    run_id = manager.iniciar({"confidencial": "valor embarque secreto"})
    wait_for(lambda: manager.obtener(run_id)["estado"] == "error")
    resultado = manager.obtener(run_id)
    assert resultado["error"]["codigo"] == "AUTOMATION_CRASH_ERR"
    assert "valor embarque secreto" not in json.dumps(resultado)


def test_archivo_con_ruta_peligrosa_y_datos_no_se_registran(tmp_path):
    bloqueado = threading.Event()
    seguir = threading.Event()

    def flow(page, datos, carpeta, settings, reporter, pausador):
        bloqueado.set()
        seguir.wait(2)

    manager, _ = manager_at(tmp_path, flow)
    secreto = "VALOR_PRIVADO_987"
    run_id = manager.iniciar({"campo": secreto}, [(r"C:\\fake\\..\\secreto.pdf", b"pdf")])
    assert bloqueado.wait(1)
    guardado = list((tmp_path / "ejecuciones" / run_id / "archivos").iterdir())
    assert len(guardado) == 1
    assert guardado[0].parent.resolve() == (tmp_path / "ejecuciones" / run_id / "archivos").resolve()
    assert ".." not in guardado[0].name and ":" not in guardado[0].name
    assert secreto not in json.dumps(manager.obtener(run_id)["eventos"])
    seguir.set()
    wait_for(lambda: manager.obtener(run_id)["estado"] == "finalizado")

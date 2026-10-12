from pathlib import Path

import pytest

from app.config import Settings
from app.runner import paso


class FakePage:
    def __init__(self):
        self.closed = False
        self.captures = []

    def is_closed(self):
        return self.closed

    def screenshot(self, *, path, full_page):
        self.captures.append((path, full_page))
        Path(path).write_bytes(b"fake screenshot")


class FakePausador:
    def __init__(self):
        self.motivos = []

    def pausar(self, page, motivo):
        self.motivos.append(motivo)


def settings_at(tmp_path):
    return Settings(
        sieca_user="", sieca_password="", data_dir=tmp_path
    )


def test_paso_exitoso_no_pausa_ni_captura(tmp_path):
    page = FakePage()
    pausador = FakePausador()
    llamado = []
    paso(page, "paso", lambda: llamado.append(True), settings=settings_at(tmp_path), pausador=pausador)
    assert llamado == [True]
    assert page.captures == []
    assert pausador.motivos == []


def test_fallo_guarda_captura_pausa_y_continua(tmp_path):
    page = FakePage()
    pausador = FakePausador()

    def fallo():
        raise RuntimeError("fallo simulado")

    paso(page, "Paso 1 - prueba", fallo, settings=settings_at(tmp_path), pausador=pausador)
    assert len(page.captures) == 1
    ruta, full_page = page.captures[0]
    assert Path(ruta).exists()
    assert Path(ruta).name.startswith("20")
    assert Path(ruta).name.endswith("_Paso_1_prueba.png")
    assert full_page is True
    assert len(pausador.motivos) == 1


def test_navegador_cerrado_relanzando_error(tmp_path):
    page = FakePage()
    pausador = FakePausador()

    def fallo_y_cierre():
        page.closed = True
        raise RuntimeError("error original")

    with pytest.raises(RuntimeError, match="error original"):
        paso(page, "paso", fallo_y_cierre, settings=settings_at(tmp_path), pausador=pausador)
    assert page.captures == []
    assert pausador.motivos == []

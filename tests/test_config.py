from pathlib import Path

import pytest

from app.config import Settings, get_settings


def test_faltan_credenciales_da_error_claro(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("SIECA_USER", raising=False)
    monkeypatch.delenv("SIECA_PASSWORD", raising=False)
    with pytest.raises(ValueError, match="SIECA_USER.*SIECA_PASSWORD"):
        get_settings()


def test_rutas_por_defecto(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    config = Settings(sieca_user="", sieca_password="")
    assert config.data_dir == Path("data")
    assert config.sieca_user_data_dir == Path("data/chrome_profile")
    assert config.debug_port == 9222


def test_variables_env_son_obligatorias_y_env_file_funciona(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("SIECA_USER", "")
    monkeypatch.setenv("SIECA_PASSWORD", "")
    (tmp_path / ".env").write_text("SIECA_USER=\nSIECA_PASSWORD=\n", encoding="utf-8")
    config = get_settings()
    assert config.sieca_user == ""
    assert config.sieca_password == ""

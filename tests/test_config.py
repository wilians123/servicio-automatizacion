from pathlib import Path

import pytest

import app.config as config_module
from app.config import Settings, get_settings


def test_falta_usuario_da_error_claro(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("SIECA_USER", raising=False)
    monkeypatch.delenv("SIECA_PASSWORD", raising=False)
    settings_file = tmp_path / "settings.json"
    settings_file.write_text('{"PASSWORD": "clave-de-prueba"}', encoding="utf-8")
    monkeypatch.setattr(config_module, "SETTINGS_FILE", settings_file)
    with pytest.raises(ValueError, match="SIECA_USER"):
        get_settings()


def test_rutas_por_defecto(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    config = Settings(sieca_user="", sieca_password="")
    assert config.data_dir == Path("data")
    assert config.sieca_user_data_dir == Path("data/chrome_profile")
    assert config.debug_port == 9222


def test_password_se_lee_de_settings_json_y_prioriza_sobre_entorno(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("SIECA_USER", "usuario-prueba")
    monkeypatch.setenv("SIECA_PASSWORD", "valor-viejo")
    settings_file = tmp_path / "settings.json"
    settings_file.write_text('{"PASSWORD": "clave-json#prueba"}', encoding="utf-8")
    monkeypatch.setattr(config_module, "SETTINGS_FILE", settings_file)
    (tmp_path / ".env").write_text(
        "SIECA_LOGIN_URL=https://example.invalid/login\nSIECA_PASSWORD=valor-env\n",
        encoding="utf-8",
    )
    config = get_settings()
    assert config.sieca_user == "usuario-prueba"
    assert config.sieca_password == "clave-json#prueba"
    assert config.sieca_login_url == "https://example.invalid/login"

import pytest

from app.config import Settings
from app.errors import LoginTimeoutError
from app import sieca_login


class FakeClock:
    def __init__(self):
        self.ms = 0

    def monotonic(self):
        return self.ms / 1000


class FakeLocator:
    def __init__(self, page, kind):
        self.page = page
        self.kind = kind

    def fill(self, value):
        self.page.fills.append((self.kind, value))
        self.page.values[self.kind] = value

    def evaluate(self, _script, value):
        self.page.fills.append((self.kind, value))
        self.page.values[self.kind] = value

    def input_value(self):
        return self.page.values.get(self.kind, "")

    def or_(self, other):
        return self

    @property
    def first(self):
        return self

    def click(self, timeout=None):
        self.page.click_times.append(self.page.clock.ms)
        self.page.current_url = "https://example.invalid/Inicio"

    def count(self):
        return 1 if self.page.has_captcha else 0


class FakePage:
    def __init__(self, clock, has_captcha=True):
        self.clock = clock
        self.current_url = "https://example.invalid/Account/Login"
        self.has_captcha = has_captcha
        self.closed = False
        self.fills = []
        self.values = {}
        self.click_times = []

    def goto(self, url, wait_until):
        self.current_url = url

    def wait_for_load_state(self, state):
        pass

    @property
    def url(self):
        return self.current_url

    def get_by_role(self, role, name):
        return FakeLocator(self, f"{role}:{name}")

    def locator(self, selector):
        return FakeLocator(self, selector)

    def frame_locator(self, selector):
        return FakeLocator(self, selector)

    def is_closed(self):
        return self.closed

    def wait_for_timeout(self, ms):
        self.clock.ms += ms

    def evaluate(self, script, arg=None):
        pass


def config():
    return Settings(sieca_user="", sieca_password="", sieca_login_url="https://example.invalid/Account/Login")


def install_clock(monkeypatch, clock):
    monkeypatch.setattr(sieca_login.time, "monotonic", clock.monotonic)


def test_llenado_contrasena_completa_si_input_declara_maxlength():
    class CampoConLongitudMaxima:
        def __init__(self):
            self.maxlength = 8
            self.value = ""

        def fill(self, value):
            self.value = value[: self.maxlength] if self.maxlength is not None else value

        def input_value(self):
            return self.value

        def evaluate(self, _script, value):
            self.maxlength = None
            self.value = value

    campo = CampoConLongitudMaxima()
    contrasena = "demo/123#tail"

    sieca_login._llenar_contrasena_completa(campo, contrasena)

    assert campo.value == contrasena


def test_captcha_resuelto_pulsa_ingresar(monkeypatch):
    clock = FakeClock()
    install_clock(monkeypatch, clock)
    monkeypatch.setattr(sieca_login, "captcha_resuelto", lambda page: True)
    page = FakePage(clock)
    sieca_login.iniciar_sesion_sieca(page, config())
    assert page.click_times == [0]
    assert [kind for kind, _ in page.fills] == ["textbox:Usuario", "textbox:Contraseña"]


def test_sin_captcha_espera_mas_de_tres_segundos(monkeypatch):
    clock = FakeClock()
    install_clock(monkeypatch, clock)
    page = FakePage(clock, has_captcha=False)
    sieca_login.iniciar_sesion_sieca(page, config())
    assert page.click_times == [3500]


def test_timeout_de_cinco_minutos_con_tiempo_simulado(monkeypatch):
    clock = FakeClock()
    install_clock(monkeypatch, clock)
    page = FakePage(clock, has_captcha=True)
    monkeypatch.setattr(sieca_login, "captcha_resuelto", lambda page: False)
    with pytest.raises(LoginTimeoutError, match="5 min"):
        sieca_login.iniciar_sesion_sieca(page, config())
    assert clock.ms == 300_000

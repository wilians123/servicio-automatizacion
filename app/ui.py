"""Avisos visuales temporales dentro de la página."""

AVISO_ID = "__sieca_aviso__"


def mostrar_aviso(page, texto: str) -> None:
    try:
        page.evaluate(
            """({id, t}) => {
              document.getElementById(id)?.remove();
              const div = document.createElement('div');
              div.id = id;
              div.textContent = t;
              div.style.cssText = 'position:fixed;top:0;left:0;right:0;z-index:2147483647;background:#b45309;color:#fff;font:14px/1.4 sans-serif;padding:8px 12px;text-align:center;';
              document.body.appendChild(div);
            }""",
            {"id": AVISO_ID, "t": texto},
        )
    except Exception:
        pass


def quitar_aviso(page) -> None:
    try:
        page.evaluate(
            "(id) => document.getElementById(id)?.remove()", AVISO_ID
        )
    except Exception:
        pass

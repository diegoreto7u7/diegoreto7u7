"""Logros desbloqueados (achievements.svg): siete notificaciones al estilo Steam/Xbox.

Entran deslizándose desde la derecha una sola vez, cada 0,35 s; la primera ya está en su sitio en
t = 0. Después los trofeos destellan en bucle. El estado base es el final (todas visibles y quietas).
"""

from gen.content import COPY, fmt_int
from gen.live import LiveStats, streak_badge
from gen.pixel import rects
from gen.scenes.common import BLINK_CSS, header
from gen.sprites.misc import TROPHY
from gen.svg import document, text

W = 840
BG, FRAME, PANEL, ICON_BG = "#0d1117", "#30363d", "#161b22", "#0d1117"
GREY, LIGHT = "#8b949e", "#e6edf3"
TOAST_X, TOAST_Y0, TOAST_W, TOAST_H, TOAST_GAP = 12, 64, 816, 60, 8
TROPHY_SCALE = 4
TEXT_X = 76                  # tras la casilla del trofeo (56) y el separador
STAGGER, SLIDE = 0.35, 0.3   # una notificación nueva cada 0,35 s; cada una tarda 0,3 s en entrar
FLASH_EVERY = 2.8


def streak_text(lang: str, live: LiveStats) -> str:
    """Logro de racha: la actual si es de 3 días o más; si no, la más larga."""
    kind, n = streak_badge(live)
    return COPY[lang][f"ach.streak_{kind}"].format(n=fmt_int(n, lang))


def _texts(lang: str, live: LiveStats) -> list[str]:
    c = COPY[lang]
    return ([c["ach.best_day"].format(n=fmt_int(live.best_day, lang))]
            + [c[f"ach.{k}"] for k in ("langs", "gpu", "rag", "rust", "go")]
            + [streak_text(lang, live)])


def _r(x, y, w, h, fill) -> str:
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"/>'


def _toast(i: int, label: str, toast: str) -> str:
    x, y, w, h = TOAST_X, TOAST_Y0 + i * (TOAST_H + TOAST_GAP), TOAST_W, TOAST_H
    rows, pal = TROPHY
    tx, ty = x + 6, y + 6
    silhouette = ["".join("." if ch == "." else "A" for ch in row) for row in rows]
    shine = rects(silhouette, {"A": "#fffbe6"}, tx, ty, TROPHY_SCALE)   # destello: trofeo en blanco
    # esquinas recortadas de 2 px para que el marco se lea pixelado
    corners = "".join(_r(cx, cy, 2, 2, BG) for cx in (x, x + w - 2) for cy in (y, y + h - 2))
    cls = "toast" if i == 0 else f"toast slide s{i}"
    return (
        f'<g class="{cls}">'
        + _r(x, y, w, h, FRAME) + _r(x + 2, y + 2, w - 4, h - 4, PANEL)
        + _r(x + 2, y + 2, 56, h - 4, ICON_BG) + _r(x + 58, y + 2, 2, h - 4, FRAME)
        + corners
        + rects(rows, pal, tx, ty, TROPHY_SCALE)
        + f'<g class="shine h{i}">{shine}</g>'
        + text(x + TEXT_X, y + 25, toast, "vt323", 22, GREY, max_width=w - TEXT_X - 16)
        + text(x + TEXT_X, y + 50, label, "vt323", 26, LIGHT, max_width=w - TEXT_X - 16)
        + "</g>"
    )


def _css(n: int) -> str:
    arrived = (n - 1) * STAGGER
    rules = [
        f".slide{{animation:slide {SLIDE:g}s steps(6) both}}"
        f"@keyframes slide{{from{{transform:translateX({W}px)}}}}",
        f".shine{{opacity:0;animation:shine {FLASH_EVERY:g}s steps(1) infinite}}"
        "@keyframes shine{0%{opacity:0}4%{opacity:.8}8%{opacity:.35}12%{opacity:0}}",
    ]
    rules += [f".s{i}{{animation-delay:{i * STAGGER - SLIDE:.2f}s}}" for i in range(1, n)]
    rules += [f".h{i}{{animation-delay:{arrived + 0.4 + i * 0.15:.2f}s}}" for i in range(n)]
    return "".join(rules)


def render(lang: str, live: LiveStats) -> dict[str, str]:
    c = COPY[lang]
    labels = _texts(lang, live)
    body = header(c["ach.title"]) + "".join(
        _toast(i, label, c["ach.toast"]) for i, label in enumerate(labels))
    h = TOAST_Y0 + len(labels) * (TOAST_H + TOAST_GAP) - TOAST_GAP + 8
    streak = streak_text(lang, live)
    title = c["alt.achievements"].format(best=fmt_int(live.best_day, lang),
                                         streak=streak[0].lower() + streak[1:])
    svg = document(W, h, title, body, css=BLINK_CSS + _css(len(labels)),
                   fonts=("ps2p", "vt323"), bg=BG)
    return {"achievements.svg": svg}

"""Logros desbloqueados (achievements.svg): siete notificaciones al estilo Steam/Xbox.

Entran deslizándose desde la derecha una sola vez, cada 0,35 s; la primera ya está en su sitio en
t = 0. Después los trofeos destellan en bucle. El estado base es el final (todas visibles y quietas).

Dos maquetaciones con el mismo dibujo (`Layout`): notificaciones de 816 en escritorio
(achievements.svg, 840 de ancho) y de 400 en el móvil (m-achievements.svg, 420 de ancho). Si el
logro no cabe en una línea, se parte en líneas parejas (hoy, dos como mucho) y la notificación
crece.
"""

from dataclasses import dataclass

from gen.content import COPY, fmt_int
from gen.live import LiveStats, streak_badge
from gen.pixel import rects
from gen.scenes.common import BLINK_CSS, MOBILE_W, header
from gen.sprites.misc import TROPHY
from gen.svg import balanced_wrap, document, rect, text

BG, FRAME, PANEL, ICON_BG = "#0d1117", "#30363d", "#161b22", "#0d1117"
GREY, LIGHT = "#8b949e", "#e6edf3"
TOAST_Y0, TOAST_H, TOAST_GAP = 64, 60, 8    # TOAST_H: alto con el logro en una línea
LINE_H = 28                  # cada línea más del logro alarga la notificación
TROPHY_SCALE = 4
TEXT_X = 76                  # tras la casilla del trofeo (56) y el separador
STAGGER, SLIDE = 0.35, 0.3   # una notificación nueva cada 0,35 s; cada una tarda 0,3 s en entrar
FLASH_EVERY = 2.8


def streak_text(lang: str, live: LiveStats) -> str:
    """Logro de racha: la actual si es de 3 días o más; si no, la más larga."""
    kind, n = streak_badge(live)
    return COPY[lang][f"ach.streak_{kind}"].format(n=fmt_int(n, lang))


def alt_text(lang: str, live: LiveStats) -> str:
    """Texto alternativo del bloque: el <title> del SVG y el alt del README son este mismo texto.

    La racha va a mitad de frase, así que empieza en minúscula («…; racha récord: 16 días seguidos.»).
    """
    streak = streak_text(lang, live)
    return COPY[lang]["alt.achievements"].format(best=fmt_int(live.best_day, lang),
                                                 streak=streak[0].lower() + streak[1:])


@dataclass(frozen=True)
class Layout:
    """Lienzo de `w` de ancho con las notificaciones de `toast_w` a partir de `toast_x`."""
    w: int
    toast_x: int
    toast_w: int


DESKTOP = Layout(w=840, toast_x=12, toast_w=816)
MOBILE = Layout(w=MOBILE_W, toast_x=10, toast_w=400)


def _texts(lang: str, live: LiveStats) -> list[str]:
    c = COPY[lang]
    return ([c["ach.best_day"].format(n=fmt_int(live.best_day, lang))]
            + [c[f"ach.{k}"] for k in ("langs", "gpu", "rag", "rust", "go")]
            + [streak_text(lang, live)])


def _toast(i: int, y: int, label: str, toast: str, lay: Layout) -> tuple[str, int]:
    """Notificación `i` con su borde superior en `y`; devuelve el svg y su alto."""
    x, w = lay.toast_x, lay.toast_w
    lines = balanced_wrap(label, "vt323", 26, w - TEXT_X - 16)
    h = TOAST_H + (len(lines) - 1) * LINE_H
    rows, pal = TROPHY
    tx, ty = x + 6, y + (h - len(rows) * TROPHY_SCALE) // 2   # trofeo centrado en su casilla
    silhouette = ["".join("." if ch == "." else "A" for ch in row) for row in rows]
    shine = rects(silhouette, {"A": "#fffbe6"}, tx, ty, TROPHY_SCALE)   # destello: trofeo en blanco
    # esquinas recortadas de 2 px para que el marco se lea pixelado
    corners = "".join(rect(cx, cy, 2, 2, BG) for cx in (x, x + w - 2) for cy in (y, y + h - 2))
    cls = "toast" if i == 0 else f"toast slide s{i}"
    return (
        f'<g class="{cls}">'
        + rect(x, y, w, h, FRAME) + rect(x + 2, y + 2, w - 4, h - 4, PANEL)
        + rect(x + 2, y + 2, 56, h - 4, ICON_BG) + rect(x + 58, y + 2, 2, h - 4, FRAME)
        + corners
        + rects(rows, pal, tx, ty, TROPHY_SCALE)
        + f'<g class="shine h{i}">{shine}</g>'
        + text(x + TEXT_X, y + 25, toast, "vt323", 22, GREY, max_width=w - TEXT_X - 16)
        + "".join(text(x + TEXT_X, y + 50 + k * LINE_H, line, "vt323", 26, LIGHT,
                       max_width=w - TEXT_X - 16) for k, line in enumerate(lines))
        + "</g>"
    ), h


def _css(n: int, width: int) -> str:
    arrived = (n - 1) * STAGGER
    rules = [
        f".slide{{animation:slide {SLIDE:g}s steps(6) both}}"
        f"@keyframes slide{{from{{transform:translateX({width}px)}}}}",
        f".shine{{opacity:0;animation:shine {FLASH_EVERY:g}s steps(1) infinite}}"
        "@keyframes shine{0%{opacity:0}4%{opacity:.8}8%{opacity:.35}12%{opacity:0}}",
    ]
    rules += [f".s{i}{{animation-delay:{i * STAGGER - SLIDE:.2f}s}}" for i in range(1, n)]
    rules += [f".h{i}{{animation-delay:{arrived + 0.4 + i * 0.15:.2f}s}}" for i in range(n)]
    return "".join(rules)


def _achievements(lang: str, live: LiveStats, lay: Layout) -> str:
    c = COPY[lang]
    labels = _texts(lang, live)
    parts, y = [header(c["ach.title"], lay.w)], TOAST_Y0
    for i, label in enumerate(labels):
        toast, toast_h = _toast(i, y, label, c["ach.toast"], lay)
        parts.append(toast)
        y += toast_h + TOAST_GAP
    h = y - TOAST_GAP + 8
    return document(lay.w, h, alt_text(lang, live), "".join(parts),
                    css=BLINK_CSS + _css(len(labels), lay.w), fonts=("ps2p", "vt323"), bg=BG)


def render(lang: str, live: LiveStats) -> dict[str, str]:
    return {"achievements.svg": _achievements(lang, live, DESKTOP),
            "m-achievements.svg": _achievements(lang, live, MOBILE)}

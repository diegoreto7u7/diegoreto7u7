"""Cabecera animada (hero.svg): nombre y rol fijos, un terminal que escribe solo y una cámara
pixel que se enciende a los 2 s y detecta a cuatro personas que cruzan.

Ciclo de 14 s. El estilo base de cada elemento es su estado final (cámara encendida, todas las
líneas visibles, personas quietas): con movimiento reducido se ve la escena completa.

Dos maquetaciones con el mismo dibujo (`Layout`): en escritorio (hero.svg, 840 de ancho) el
terminal y la cámara van lado a lado; en el móvil (m-hero.svg, 420 de ancho) el terminal va a
todo el ancho y la cámara, también a todo el ancho, debajo. Lo de dentro de cada panel se coloca
relativo a su caja (`Box`).
"""

import random
from dataclasses import dataclass

from gen.content import COPY
from gen.live import LiveStats
from gen.pixel import rects, two_frames
from gen.scenes.common import BLINK_CSS, MOBILE_W
from gen.sprites.misc import CAT, DOT, PLANT
from gen.sprites.people import PEOPLE
from gen.svg import document, escape, pct, rect, text, text_width

CYCLE, RESET, CAM_ON = 14.0, 13.5, 2.0


@dataclass(frozen=True)
class Box:
    """Un panel de la ventana (terminal o cámara), en coordenadas del lienzo."""
    x0: int
    y0: int
    x1: int
    y1: int

    @property
    def w(self) -> int:
        return self.x1 - self.x0

    @property
    def h(self) -> int:
        return self.y1 - self.y0


@dataclass(frozen=True)
class Layout:
    """Ventana con marco de 4 px: barra de título de top + 4 a top + 36 y debajo los paneles."""
    w: int
    h: int
    top: int                         # borde superior (exterior) del marco de la ventana
    win_bottom: int                  # borde inferior (exterior) del marco de la ventana
    term: Box
    cam: Box
    sep: tuple[int, int, int, int]   # marco entre los dos paneles: x, y, ancho, alto
    cat_x: int                       # el gato duerme sobre el borde superior, a la derecha


# terminal a la izquierda y cámara a la derecha
DESKTOP = Layout(w=840, h=400, top=100, win_bottom=392, term=Box(8, 136, 404, 388),
                 cam=Box(412, 136, 832, 388), sep=(404, 136, 8, 252), cat_x=752)
# terminal arriba y cámara debajo, las dos a todo el ancho y con el alto del escritorio. La
# ventana baja 10 px: en 420 el gato queda bajo el final del rol («Bilbao») y así no lo toca.
MOBILE = Layout(w=MOBILE_W, h=666, top=110, win_bottom=658, term=Box(8, 146, 412, 398),
                cam=Box(8, 402, 412, 654), sep=(8, 398, 404, 4), cat_x=332)

# dentro de la cámara, relativo a su esquina superior izquierda
FLOOR_DY = 114                         # línea del suelo
DOOR_DX, DOOR_DY, DOOR_W = 174, 36, 60  # marco de la puerta; acaba en el zócalo

FRAME, BAR, TERM_BG, CAM_BG = "#30363d", "#161b22", "#010409", "#0b1118"
INK, PAPER, GREEN, BLUE = "#0d1117", "#f0f6fc", "#3fb950", "#79c0ff"
YELLOW, GREY, LIGHT = "#e3b341", "#8b949e", "#c9d1d9"

TERM_DX, TERM_DY, TERM_LH = 12, 30, 34   # primera línea del terminal, relativa al panel
VT323_REAL_ADVANCE = 0.4   # medido en el TTF; solo para colocar el cursor tras el texto
# (clave, color del texto, segundo en que aparece; None = visible desde el fotograma 0)
LINES = [("t1", BLUE, None), ("t2", LIGHT, None), ("t3", BLUE, 0.6), ("t4", YELLOW, 1.0),
         ("t5", BLUE, 1.4), ("t6", GREY, 2.0), ("t7", GREY, 2.4)]

# (persona, escala, pies_y, x en reposo, sentido, segundos por cruce, color de la caja,
# confianza de la detección), de la más lejana a la más cercana para que se solapen bien.
# pies_y y x son relativos a la esquina de la cámara.
# Cada persona lleva su propia confianza, más baja cuanto más lejos está, como un detector real.
WALKERS = [
    (2, 3, 162, 122, -1, 17, "#d2a8ff", "0.71"),
    (3, 4, 190, 280, -1, 13, "#58a6ff", "0.83"),
    (1, 4, 210, 166, 1, 11, YELLOW, "0.88"),
    (0, 5, 248, 8, 1, 9, GREEN, "0.94"),
]
POSE_AT = 2.5  # segundo en que cada persona pasa por su posición de reposo


def _defs(cam: Box) -> str:
    # ruido de televisión: losa de 25×18 píxeles de 4, con semilla fija para que el SVG no cambie
    rng = random.Random(3)
    noise_rows = ["".join(rng.choice("..abcd") for _ in range(25)) for _ in range(18)]
    noise = rects(noise_rows, {"a": "#21262d", "b": "#484f58", "c": "#6e7681", "d": "#8b949e"},
                  0, 0, 4)
    scan = rect(0, 0, 4, 1, "#000", ' opacity=".28"')
    return (
        "<defs>"
        f'<clipPath id="cam"><rect x="{cam.x0}" y="{cam.y0}" width="{cam.w}" '
        f'height="{cam.h}"/></clipPath>'
        '<pattern id="wall" width="32" height="8" patternUnits="userSpaceOnUse">'
        f'{rect(0, 0, 16, 8, "#0f1720")}{rect(16, 0, 16, 8, "#111b25")}</pattern>'
        f'<pattern id="floor" x="{cam.x0}" y="{cam.y0 + FLOOR_DY}" width="48" height="24" '
        'patternUnits="userSpaceOnUse">'
        f'{rect(0, 0, 48, 24, "#141e29")}{rect(24, 0, 24, 12, "#1a2533")}'
        f'{rect(0, 12, 24, 12, "#1a2533")}</pattern>'
        '<pattern id="noise" width="100" height="72" patternUnits="userSpaceOnUse">'
        f'{rect(0, 0, 100, 72, INK)}{noise}</pattern>'
        f'<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse">{scan}</pattern>'
        "</defs>"
    )


def _band(lang: str, width: int) -> str:
    return (text(8, 42, "DIEGO ORUE", "ps2p", 28, PAPER, max_width=width - 16)
            + text(8, 76, COPY[lang]["hero.role"], "vt323", 26, GREY, max_width=width - 16))


def _title_bar(lay: Layout) -> str:
    top = lay.top
    dots = "".join(rect(20 + i * 18, top + 14, 12, 12, c)
                   for i, c in enumerate(("#ff5f56", "#ffbd2e", "#27c93f")))
    return (rect(8, top + 4, lay.w - 16, 32, BAR) + dots
            + text(80, top + 27, "diego@bilbao", "vt323", 22, "#7d8590"))


def _frame(lay: Layout) -> str:
    """Marco de 4 px con esquinas escalonadas, dibujado encima de los paneles."""
    w, top, bottom = lay.w, lay.top, lay.win_bottom
    side = bottom - top - 16
    parts = [
        rect(12, top, w - 24, 4, FRAME), rect(12, bottom - 4, w - 24, 4, FRAME),
        rect(4, top + 8, 4, side, FRAME), rect(w - 8, top + 8, 4, side, FRAME),
        rect(*lay.sep, FRAME),
    ]
    parts += [rect(x, y, 4, 4, FRAME) for x in (8, w - 12) for y in (top + 4, bottom - 8)]
    return "".join(parts)


def _line(x: int, y: int, s: str, color: str, max_width: int) -> tuple[str, float]:
    """Una línea del terminal y la x donde acaba (con el avance real de la fuente).

    Va en un solo <text>; el prompt «$»/«>» y el «OK» final son <tspan> en verde. Así el
    navegador los coloca con el avance real de VT323 y no queda un hueco de más antes del «OK»
    (ADVANCE lleva margen para comprobar que nada desborda, no para colocar).
    """
    el = text(x, y, s, "vt323", 26, color, max_width=max_width)
    head, body, tail = "", s, ""
    if body[:2] in ("$ ", "> "):
        head, body = f'<tspan fill="{GREEN}">{escape(body[0])}</tspan> ', body[2:]
    if body.endswith(" OK"):
        body, tail = body.removesuffix(" OK"), f' <tspan fill="{GREEN}">OK</tspan>'
    open_tag = el[:el.index(">") + 1]
    return (f"{open_tag}{head}{escape(body)}{tail}</text>",
            x + len(s) * VT323_REAL_ADVANCE * 26)


def _terminal(lang: str, term: Box) -> tuple[str, str]:
    body = [rect(term.x0, term.y0, term.w, term.h, TERM_BG)]
    css = []
    x = term.x0 + TERM_DX
    for i, (key, color, at) in enumerate(LINES):
        y = term.y0 + TERM_DY + i * TERM_LH
        svg, end = _line(x, y, COPY[lang][f"hero.{key}"], color, term.x1 - 8 - x)
        if key == "t7":  # cursor █, un espacio después del texto
            svg += rect(round(end + VT323_REAL_ADVANCE * 26), y - 19, 12, 22, GREEN,
                        ' class="blink"')
        if at is None:
            body.append(svg)
            continue
        body.append(f'<g class="{key}">{svg}</g>')
        css.append(f".{key}{{animation:{key}k {CYCLE:g}s steps(1) infinite both}}"
                   f"@keyframes {key}k{{0%{{opacity:0}}{pct(at, CYCLE)}%{{opacity:1}}"
                   f"{pct(RESET, CYCLE)}%,100%{{opacity:0}}}}")
    return "".join(body), "".join(css)


def _walker(cam: Box, i: int, person: int, scale: int, feet_dy: int, x_dx: int, sense: int,
            secs: int, color: str, confidence: str, kind: str) -> tuple[str, str]:
    """Persona en su caja de detección; cruza la cámara entera y pasa por x en POSE_AT."""
    label = f"{kind} {confidence}"   # «persona 0.94»
    a, b, pal = PEOPLE[person]
    if sense < 0:
        a, b = [r[::-1] for r in a], [r[::-1] for r in b]
    x = cam.x0 + x_dx
    w, h = len(a[0]) * scale, len(a) * scale
    top = cam.y0 + feet_dy - h
    bx, by, bw, bh = x - 4, top - 4, w + 8, h + 6
    tw = round(text_width(label, "vt323", 22)) + 8
    svg = (
        f'<g class="walker w{i}">'
        f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" fill="none" '
        f'stroke="{color}" stroke-width="2"/>'
        + rect(bx - 1, by - 23, tw, 22, color)
        + text(bx + 3, by - 7, label, "vt323", 22, INK)
        + two_frames(a, b, pal, x, top, scale)
        + "</g>"
    )
    left, right = bx - 1, max(bx + bw + 1, bx - 1 + tw)
    start, end = cam.x0 - right, cam.x1 - left       # fuera de plano a un lado y al otro
    if sense < 0:
        start, end = end, start
    rest = -start / (end - start)                   # fracción del cruce en la posición de reposo
    delay = (POSE_AT - rest * secs) % secs - secs
    css = (f".w{i}{{animation:wk{i} {secs}s linear {delay:.2f}s infinite both}}"
           f"@keyframes wk{i}{{from{{transform:translateX({start}px)}}"
           f"to{{transform:translateX({end}px)}}}}")
    return svg, css


def _door(cam: Box, label: str) -> str:
    """Puerta al fondo, sobre el zócalo, con el cartel verde de salida encima."""
    x, door_top = cam.x0 + DOOR_DX, cam.y0 + DOOR_DY
    mid, bottom = x + DOOR_W // 2, cam.y0 + FLOOR_DY - 6
    sign_w = round(text_width(label, "vt323", 22)) + 10
    return (rect(x, door_top, DOOR_W, bottom - door_top, "#1f2a36")
            + rect(x + 4, door_top + 4, DOOR_W - 8, bottom - door_top - 4, "#070b10")
            + rect(x + DOOR_W - 14, door_top + 40, 4, 4, "#484f58")
            + rect(mid - sign_w // 2, door_top - 26, sign_w, 22, "#0d2a17")
            + text(mid, door_top - 9, label, "vt323", 22, GREEN, anchor="middle"))


def _camera(lang: str, cam: Box) -> tuple[str, str]:
    c = COPY[lang]
    x0, y0, x1, y1, cw, ch = cam.x0, cam.y0, cam.x1, cam.y1, cam.w, cam.h
    floor = y0 + FLOOR_DY
    cx, cy = x0 + cw // 2, y0 + ch // 2
    count = f'{c["hero.count"]} {len(WALKERS)}/40'
    count_w = round(text_width(count, "vt323", 22)) + 12
    sign_w = round(text_width(c["hero.nosignal"], "ps2p", 20)) + 40
    kind = c["hero.person"]

    walkers, css = [], []
    for i, spec in enumerate(WALKERS):
        svg, rule = _walker(cam, i, *spec, kind)
        walkers.append(svg)
        css.append(rule)

    svg = (
        '<g clip-path="url(#cam)">'
        + rect(x0, y0, cw, ch, CAM_BG)
        + rect(x0, y0, cw, floor - y0, "url(#wall)")
        + rect(x0, floor, cw, y1 - floor, "url(#floor)")
        + rect(x0, floor - 6, cw, 6, "#1f2a36")
        + _door(cam, c["hero.exit"])
        + rects(PLANT[0], PLANT[1], x0 + 14, floor - 44, 4)
        + "".join(walkers)
        # HUD
        + f'<g class="blink">{rects(DOT[0], {"A": "#f85149"}, x0 + 12, y0 + 11, 3)}</g>'
        + text(x0 + 34, y0 + 25, "REC cam_03", "vt323", 22, "#ff7b72")
        + rect(x1 - 8 - count_w, y0 + 8, count_w, 24, INK)
        + text(x1 - 14, y0 + 26, count, "vt323", 22, LIGHT, anchor="end")
        + text(x1 - 14, y1 - 12, "30 FPS", "vt323", 22, GREY, anchor="end")
        # sin señal: ruido que tiembla y cartel; oculto en el estado base (cámara encendida)
        + '<g class="nosig">'
        + rect(x0 - 48, y0 - 48, cw + 96, ch + 96, "url(#noise)", ' class="noise"')
        + rect(cx - sign_w // 2, cy - 26, sign_w, 52, INK)
        + rect(cx - sign_w // 2 + 4, cy - 22, sign_w - 8, 44, "#21262d")
        + rect(cx - sign_w // 2 + 8, cy - 18, sign_w - 16, 36, INK)
        + text(cx, cy + 10, c["hero.nosignal"], "ps2p", 20, PAPER, anchor="middle")
        + "</g>"
        + rect(x0, y0, cw, ch, "url(#scan)")
        + rect(x0, y0, cw, ch, PAPER, ' class="flash"')
        + "</g>"
    )
    on = pct(CAM_ON, CYCLE) + "%"
    css.append(
        f".nosig{{opacity:0;animation:nosig {CYCLE:g}s steps(1) infinite both}}"
        f"@keyframes nosig{{0%{{opacity:1}}{on}{{opacity:0}}{pct(RESET, CYCLE)}%,100%{{opacity:1}}}}"
        ".noise{animation:noise .4s steps(1) infinite}"
        "@keyframes noise{25%{transform:translate(-20px,12px)}"
        "50%{transform:translate(12px,-16px)}75%{transform:translate(-8px,-28px)}}"
        f".flash{{opacity:0;animation:flash {CYCLE:g}s linear infinite both}}"
        f"@keyframes flash{{0%,{pct(CAM_ON - 0.01, CYCLE)}%{{opacity:0}}{on}{{opacity:.85}}"
        f"{pct(CAM_ON + 0.5, CYCLE)}%,100%{{opacity:0}}}}"
    )
    return svg, "".join(css)


def _cat(x: int, win_top: int) -> str:
    """Gato dormido sobre el borde superior derecho de la ventana, con dos «z» que suben."""
    y = win_top - len(CAT[0]) * 3
    zs = "".join(
        f'<g class="z z{i}">{text(x + 58 + i * 12, y - 2 - i * 16, "z", "vt323", 22, GREY)}</g>'
        for i in range(2))
    return rects(CAT[0], CAT[1], x, y, 3) + zs


CSS = BLINK_CSS + (
    ".z{animation:zz 3s linear infinite}.z1{animation-delay:-1.5s}"
    "@keyframes zz{0%{opacity:0;transform:translate(-4px,10px)}30%{opacity:1}"
    "100%{opacity:0;transform:translate(6px,-12px)}}"
)


def _hero(lang: str, lay: Layout) -> str:
    term, term_css = _terminal(lang, lay.term)
    cam, cam_css = _camera(lang, lay.cam)
    body = (_defs(lay.cam) + _band(lang, lay.w) + _title_bar(lay) + term + cam + _frame(lay)
            + _cat(lay.cat_x, lay.top))
    return document(lay.w, lay.h, COPY[lang]["alt.hero"], body, css=CSS + term_css + cam_css,
                    fonts=("ps2p", "vt323"))


def render(lang: str, live: LiveStats) -> dict[str, str]:
    return {"hero.svg": _hero(lang, DESKTOP), "m-hero.svg": _hero(lang, MOBILE)}

"""Cabecera animada (hero.svg): nombre y rol fijos, un terminal que escribe solo y una cámara
pixel que se enciende a los 2 s y detecta a cuatro personas que cruzan.

Ciclo de 14 s. El estilo base de cada elemento es su estado final (cámara encendida, todas las
líneas visibles, personas quietas): con movimiento reducido se ve la escena completa.
"""

import random

from gen.content import COPY
from gen.live import LiveStats
from gen.pixel import rects, two_frames
from gen.scenes.common import BLINK_CSS
from gen.sprites.misc import CAT, DOT, PLANT
from gen.sprites.people import PEOPLE
from gen.svg import document, escape, pct, rect, text, text_width

W, H = 840, 400
CYCLE, RESET, CAM_ON = 14.0, 13.5, 2.0

WIN_TOP, WIN_BOTTOM = 100, 392
BAR_TOP, BODY_TOP, BODY_BOTTOM = 104, 136, 388
TERM_X0, TERM_X1 = 8, 404
CAM_X0, CAM_X1 = 412, 832
FLOOR_Y = 250
DOOR_X, DOOR_TOP, DOOR_W = 586, 172, 60  # marco de la puerta; acaba en el zócalo

FRAME, BAR, TERM_BG, CAM_BG = "#30363d", "#161b22", "#010409", "#0b1118"
INK, PAPER, GREEN, BLUE = "#0d1117", "#f0f6fc", "#3fb950", "#79c0ff"
YELLOW, GREY, LIGHT = "#e3b341", "#8b949e", "#c9d1d9"

TERM_X, TERM_Y0, TERM_LH = 20, 166, 34
VT323_REAL_ADVANCE = 0.4   # medido en el TTF; solo para colocar el cursor tras el texto
# (clave, color del texto, segundo en que aparece; None = visible desde el fotograma 0)
LINES = [("t1", BLUE, None), ("t2", LIGHT, None), ("t3", BLUE, 0.6), ("t4", YELLOW, 1.0),
         ("t5", BLUE, 1.4), ("t6", GREY, 2.0), ("t7", GREY, 2.4)]

# (persona, escala, pies_y, x en reposo, sentido, segundos por cruce, color de la caja,
# confianza de la detección), de la más lejana a la más cercana para que se solapen bien.
# Cada persona lleva su propia confianza, más baja cuanto más lejos está, como un detector real.
WALKERS = [
    (2, 3, 298, 534, -1, 17, "#d2a8ff", "0.71"),
    (3, 4, 326, 692, -1, 13, "#58a6ff", "0.83"),
    (1, 4, 346, 578, 1, 11, YELLOW, "0.88"),
    (0, 5, 384, 420, 1, 9, GREEN, "0.94"),
]
POSE_AT = 2.5  # segundo en que cada persona pasa por su posición de reposo


def _defs() -> str:
    # ruido de televisión: losa de 25×18 píxeles de 4, con semilla fija para que el SVG no cambie
    rng = random.Random(3)
    noise_rows = ["".join(rng.choice("..abcd") for _ in range(25)) for _ in range(18)]
    noise = rects(noise_rows, {"a": "#21262d", "b": "#484f58", "c": "#6e7681", "d": "#8b949e"},
                  0, 0, 4)
    scan = rect(0, 0, 4, 1, "#000", ' opacity=".28"')
    return (
        "<defs>"
        f'<clipPath id="cam"><rect x="{CAM_X0}" y="{BODY_TOP}" width="{CAM_X1 - CAM_X0}" '
        f'height="{BODY_BOTTOM - BODY_TOP}"/></clipPath>'
        '<pattern id="wall" width="32" height="8" patternUnits="userSpaceOnUse">'
        f'{rect(0, 0, 16, 8, "#0f1720")}{rect(16, 0, 16, 8, "#111b25")}</pattern>'
        f'<pattern id="floor" x="{CAM_X0}" y="{FLOOR_Y}" width="48" height="24" '
        'patternUnits="userSpaceOnUse">'
        f'{rect(0, 0, 48, 24, "#141e29")}{rect(24, 0, 24, 12, "#1a2533")}'
        f'{rect(0, 12, 24, 12, "#1a2533")}</pattern>'
        '<pattern id="noise" width="100" height="72" patternUnits="userSpaceOnUse">'
        f'{rect(0, 0, 100, 72, INK)}{noise}</pattern>'
        f'<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse">{scan}</pattern>'
        "</defs>"
    )


def _band(lang: str) -> str:
    return (text(TERM_X0, 42, "DIEGO ORUE", "ps2p", 28, PAPER)
            + text(TERM_X0, 76, COPY[lang]["hero.role"], "vt323", 26, GREY))


def _title_bar() -> str:
    dots = "".join(rect(20 + i * 18, 114, 12, 12, c)
                   for i, c in enumerate(("#ff5f56", "#ffbd2e", "#27c93f")))
    return (rect(8, BAR_TOP, 824, BODY_TOP - BAR_TOP, BAR) + dots
            + text(80, 127, "diego@bilbao", "vt323", 22, "#7d8590"))


def _frame() -> str:
    """Marco de 4 px con esquinas escalonadas, dibujado encima de los paneles."""
    parts = [
        rect(12, WIN_TOP, 816, 4, FRAME), rect(12, WIN_BOTTOM - 4, 816, 4, FRAME),
        rect(4, 108, 4, 276, FRAME), rect(832, 108, 4, 276, FRAME),
        rect(TERM_X1, BODY_TOP, CAM_X0 - TERM_X1, BODY_BOTTOM - BODY_TOP, FRAME),
    ]
    parts += [rect(x, y, 4, 4, FRAME) for x in (8, 828) for y in (104, 384)]
    return "".join(parts)


def _line(y: int, s: str, color: str) -> tuple[str, float]:
    """Una línea del terminal y la x donde acaba (con el avance real de la fuente).

    Va en un solo <text>; el prompt «$»/«>» y el «OK» final son <tspan> en verde. Así el
    navegador los coloca con el avance real de VT323 y no queda un hueco de más antes del «OK»
    (ADVANCE lleva margen para comprobar que nada desborda, no para colocar).
    """
    el = text(TERM_X, y, s, "vt323", 26, color, max_width=TERM_X1 - 8 - TERM_X)
    head, body, tail = "", s, ""
    if body[:2] in ("$ ", "> "):
        head, body = f'<tspan fill="{GREEN}">{escape(body[0])}</tspan> ', body[2:]
    if body.endswith(" OK"):
        body, tail = body.removesuffix(" OK"), f' <tspan fill="{GREEN}">OK</tspan>'
    open_tag = el[:el.index(">") + 1]
    return (f"{open_tag}{head}{escape(body)}{tail}</text>",
            TERM_X + len(s) * VT323_REAL_ADVANCE * 26)


def _terminal(lang: str) -> tuple[str, str]:
    body = [rect(TERM_X0, BODY_TOP, TERM_X1 - TERM_X0, BODY_BOTTOM - BODY_TOP, TERM_BG)]
    css = []
    for i, (key, color, at) in enumerate(LINES):
        y = TERM_Y0 + i * TERM_LH
        svg, end = _line(y, COPY[lang][f"hero.{key}"], color)
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


def _walker(i: int, person: int, scale: int, feet: int, x: int, sense: int,
            secs: int, color: str, confidence: str, kind: str) -> tuple[str, str]:
    """Persona en su caja de detección; cruza la cámara entera y pasa por x en POSE_AT."""
    label = f"{kind} {confidence}"   # «persona 0.94»
    a, b, pal = PEOPLE[person]
    if sense < 0:
        a, b = [r[::-1] for r in a], [r[::-1] for r in b]
    w, h = len(a[0]) * scale, len(a) * scale
    top = feet - h
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
    start, end = CAM_X0 - right, CAM_X1 - left       # fuera de plano a un lado y al otro
    if sense < 0:
        start, end = end, start
    rest = -start / (end - start)                   # fracción del cruce en la posición de reposo
    delay = (POSE_AT - rest * secs) % secs - secs
    css = (f".w{i}{{animation:wk{i} {secs}s linear {delay:.2f}s infinite both}}"
           f"@keyframes wk{i}{{from{{transform:translateX({start}px)}}"
           f"to{{transform:translateX({end}px)}}}}")
    return svg, css


def _door(label: str) -> str:
    """Puerta al fondo, sobre el zócalo, con el cartel verde de salida encima."""
    mid, bottom = DOOR_X + DOOR_W // 2, FLOOR_Y - 6
    sign_w = round(text_width(label, "vt323", 22)) + 10
    return (rect(DOOR_X, DOOR_TOP, DOOR_W, bottom - DOOR_TOP, "#1f2a36")
            + rect(DOOR_X + 4, DOOR_TOP + 4, DOOR_W - 8, bottom - DOOR_TOP - 4, "#070b10")
            + rect(DOOR_X + DOOR_W - 14, DOOR_TOP + 40, 4, 4, "#484f58")
            + rect(mid - sign_w // 2, DOOR_TOP - 26, sign_w, 22, "#0d2a17")
            + text(mid, DOOR_TOP - 9, label, "vt323", 22, GREEN, anchor="middle"))


def _camera(lang: str) -> tuple[str, str]:
    c = COPY[lang]
    cw, ch = CAM_X1 - CAM_X0, BODY_BOTTOM - BODY_TOP
    cx, cy = CAM_X0 + cw // 2, BODY_TOP + ch // 2
    count = f'{c["hero.count"]} {len(WALKERS)}/40'
    count_w = round(text_width(count, "vt323", 22)) + 12
    sign_w = round(text_width(c["hero.nosignal"], "ps2p", 20)) + 40
    kind = c["hero.person"]

    walkers, css = [], []
    for i, spec in enumerate(WALKERS):
        svg, rule = _walker(i, *spec, kind)
        walkers.append(svg)
        css.append(rule)

    svg = (
        '<g clip-path="url(#cam)">'
        + rect(CAM_X0, BODY_TOP, cw, ch, CAM_BG)
        + rect(CAM_X0, BODY_TOP, cw, FLOOR_Y - BODY_TOP, "url(#wall)")
        + rect(CAM_X0, FLOOR_Y, cw, BODY_BOTTOM - FLOOR_Y, "url(#floor)")
        + rect(CAM_X0, FLOOR_Y - 6, cw, 6, "#1f2a36")
        + _door(c["hero.exit"])
        + rects(PLANT[0], PLANT[1], CAM_X0 + 14, FLOOR_Y - 44, 4)
        + "".join(walkers)
        # HUD
        + f'<g class="blink">{rects(DOT[0], {"A": "#f85149"}, CAM_X0 + 12, 147, 3)}</g>'
        + text(CAM_X0 + 34, 161, "REC cam_03", "vt323", 22, "#ff7b72")
        + rect(CAM_X1 - 8 - count_w, 144, count_w, 24, INK)
        + text(CAM_X1 - 14, 162, count, "vt323", 22, LIGHT, anchor="end")
        + text(CAM_X1 - 14, BODY_BOTTOM - 12, "30 FPS", "vt323", 22, GREY, anchor="end")
        # sin señal: ruido que tiembla y cartel; oculto en el estado base (cámara encendida)
        + '<g class="nosig">'
        + rect(CAM_X0 - 48, BODY_TOP - 48, cw + 96, ch + 96, "url(#noise)", ' class="noise"')
        + rect(cx - sign_w // 2, cy - 26, sign_w, 52, INK)
        + rect(cx - sign_w // 2 + 4, cy - 22, sign_w - 8, 44, "#21262d")
        + rect(cx - sign_w // 2 + 8, cy - 18, sign_w - 16, 36, INK)
        + text(cx, cy + 10, c["hero.nosignal"], "ps2p", 20, PAPER, anchor="middle")
        + "</g>"
        + rect(CAM_X0, BODY_TOP, cw, ch, "url(#scan)")
        + rect(CAM_X0, BODY_TOP, cw, ch, PAPER, ' class="flash"')
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


def _cat() -> str:
    """Gato dormido sobre el borde superior derecho de la ventana, con dos «z» que suben."""
    x, y = 752, WIN_TOP - len(CAT[0]) * 3
    zs = "".join(
        f'<g class="z z{i}">{text(x + 58 + i * 12, y - 2 - i * 16, "z", "vt323", 22, GREY)}</g>'
        for i in range(2))
    return rects(CAT[0], CAT[1], x, y, 3) + zs


CSS = BLINK_CSS + (
    ".z{animation:zz 3s linear infinite}.z1{animation-delay:-1.5s}"
    "@keyframes zz{0%{opacity:0;transform:translate(-4px,10px)}30%{opacity:1}"
    "100%{opacity:0;transform:translate(6px,-12px)}}"
)


def render(lang: str, live: LiveStats) -> dict[str, str]:
    term, term_css = _terminal(lang)
    cam, cam_css = _camera(lang)
    body = _defs() + _band(lang) + _title_bar() + term + cam + _frame() + _cat()
    svg = document(W, H, COPY[lang]["alt.hero"], body, css=CSS + term_css + cam_css,
                   fonts=("ps2p", "vt323"))
    return {"hero.svg": svg}

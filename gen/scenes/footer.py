"""Pie del README: Bilbao de noche en pixel art (bilbao.svg) y «pulsa start» (start.svg).

bilbao.svg: rejilla de 168 x 46 a escala 5 (840 x 230), procedural y reproducible (Random(7)
local). Capas animadas: estrellas, ventanas, reflejos del agua y una estrella fugaz cada 9 s.
Estado base (movimiento reducido): estrellas y ventanas visibles, sin estrella fugaz.
"""

import math
import random

from gen.content import COPY
from gen.live import LiveStats
from gen.pixel import rects, sprite
from gen.scenes.common import BLINK_CSS
from gen.sprites.misc import ARROW
from gen.svg import document, text, text_width

W, H, SCALE = 168, 46, 5
QUAY = 34                      # primera fila del muelle; la ría empieza en QUAY + 2
START_W, START_H = 840, 88

PAL = {
    "a": "#0a0f1f", "b": "#0d1530", "c": "#111c3d", "d": "#16234a",
    # montes de Artxanda: verde oscuro, más claro que el cielo para que se lean como monte
    "h": "#3a6358", "i": "#28463f",
    "s": "#9aa7b4", "S": "#c9d1d9", "t": "#6e7b88", "T": "#4d5964",
    "w": "#0c2236", "x": "#123049",
    "q": "#30363d", "Q": "#21262d",
    "k": "#1b2433", "K": "#243042",
    "r": "#da3633", "R": "#8e2523", "Z": "#e6edf3", "m": "#f0e6c8", "n": "#d4c8a4",
    "1": "#ff7b72", "2": "#d2a8ff", "3": "#3fb950", "4": "#e3b341", "5": "#58a6ff",
}
# (x0, ancho, cima) de los edificios genéricos; los que llevan ventanas van en WINDOWED
BUILDINGS = [(2, 7, 24), (10, 5, 21), (16, 3, 27), (122, 7, 22), (131, 5, 26), (160, 8, 23)]
WINDOWED = [(2, 7, 24), (10, 5, 21), (122, 7, 22), (160, 8, 23)]
IBERDROLA = (106, 9)           # x0, ancho
GUGG = (29, 45)                # x0, ancho
BRIDGE = (75, 29)              # x0, ancho
ZUBI = (133, 27)               # x0, ancho

CSS = (
    BLINK_CSS
    + ".tw{animation:tw 3s steps(1) infinite}.tw1{animation-delay:-.7s}"
    ".tw2{animation-delay:-1.4s}.tw3{animation-delay:-2.1s}"
    "@keyframes tw{50%{opacity:.15}}"
    ".win{animation:win 7s steps(1) infinite}.win1{animation-delay:-2s}"
    ".win2{animation-delay:-4s}.win3{animation-delay:-5.5s}"
    "@keyframes win{0%,60%{opacity:1}61%,100%{opacity:.1}}"
    ".sh{animation:sh 1.6s steps(2) infinite}.sh1{animation-delay:-.5s}.sh2{animation-delay:-1s}"
    "@keyframes sh{50%{opacity:0}}"
    ".shoot{opacity:0;animation:shoot 9s linear infinite}"
    "@keyframes shoot{0%,80%{transform:translate(20px,2px);opacity:0}"
    "81%{opacity:1}90%{transform:translate(60px,14px);opacity:1}91%,100%{opacity:0}}"
)


def _grid() -> list[list[str]]:
    rng = random.Random(7)
    g = [["." for _ in range(W)] for _ in range(H)]

    # cielo con bandas y tramado
    bands = "abcd"
    for y in range(QUAY):
        bi = min(3, y * 4 // QUAY)
        for x in range(W):
            ch = bands[bi]
            if bi < 3 and (y * 4 % QUAY) > 26 and (x + y) % 2 == 0:
                ch = bands[bi + 1]
            g[y][x] = ch

    # luna creciente
    for y in range(3, 12):
        for x in range(141, 150):
            if (x - 145) ** 2 + (y - 7) ** 2 <= 14 and not (x - 147) ** 2 + (y - 6) ** 2 <= 9:
                g[y][x] = "m" if (x + y) % 5 else "n"

    # montes de Artxanda
    for x in range(W):
        top = int(22 + 3 * math.sin(x / 13) + 2 * math.sin(x / 5.5))
        for y in range(top, QUAY):
            g[y][x] = "h" if y < top + 2 else "i"

    def block(x0, w, top, col):
        for y in range(top, QUAY):
            for x in range(x0, min(W, x0 + w)):
                g[y][x] = col

    for x0, w, top in BUILDINGS:
        block(x0, w, top, rng.choice("kK"))

    # torre Iberdrola: fuste, remate escalonado y base ancha
    x0, w = IBERDROLA
    block(x0, w, 7, "K")
    block(x0 + 2, w - 4, 4, "K")
    block(x0 + 3, w - 6, 2, "K")
    for y in range(7, QUAY):
        g[y][x0] = "k"
    block(x0 - 1, w + 2, 30, "K")

    # Guggenheim: lóbulos de titanio superpuestos y torre de la fachada
    x0, w = GUGG
    lobes = [(0.00, 0.34, 8), (0.18, 0.55, 11), (0.40, 0.80, 9), (0.62, 1.00, 6)]
    tops = []
    for x in range(x0, x0 + w):
        u = (x - x0) / (w - 1)
        h = 3.0
        for a, b, amp in lobes:
            if a <= u <= b:
                h = max(h, 3 + amp * math.sin((u - a) / (b - a) * math.pi) ** 0.8)
        tops.append(QUAY - int(h))
    for i, x in enumerate(range(x0, x0 + w)):
        for y in range(tops[i], QUAY):
            depth = y - tops[i]
            wave = int(2 * math.sin(x / 2.6 + y / 2.2))
            m = (y + wave) % 5
            ch = "S" if m == 0 else ("s" if m < 3 else ("t" if m == 3 else "T"))
            if depth == 0:
                ch = "S"
            g[y][x] = ch
    # torre de la fachada (a la derecha) y cristalera del atrio
    for y in range(15, QUAY):
        for x in range(x0 + w, x0 + w + 3):
            g[y][x] = "s" if y % 3 else "S"
    for y in range(29, QUAY):
        for x in range(x0 + 14, x0 + 20):
            g[y][x] = "5" if (x - x0) % 2 else "c"

    # Puppy: perro de flores
    for y in range(27, QUAY):
        for x in range(19, 27):
            if (x - 22.5) ** 2 / 14 + (y - 30.5) ** 2 / 14 <= 1.1:
                g[y][x] = rng.choice("12345")
    for y in range(24, 27):
        for x in range(21, 25):
            if (x - 22.5) ** 2 / 4 + (y - 26) ** 2 / 4 <= 1.1:
                g[y][x] = rng.choice("12345")

    # muelle y ría
    for x in range(W):
        g[QUAY][x] = "q"
        g[QUAY + 1][x] = "Q"
    for y in range(QUAY + 2, H):
        for x in range(W):
            g[y][x] = "w" if (x // 3 + y) % 5 else "x"

    # puente de La Salve con el arco rojo y su tablero
    bx, bw = BRIDGE
    for x in range(bx, bx + bw):
        g[QUAY - 1][x] = "q"
        g[QUAY][x] = "q"
    cx = bx + bw / 2
    for x in range(bx + 3, bx + bw - 2):
        yy = 22 + int(((x - cx) ** 2) / 8)
        g[min(yy, QUAY - 2)][x] = "r"
        g[min(yy + 1, QUAY - 2)][x] = "R"
        if (x - bx) % 3 == 0:
            for y in range(yy + 2, QUAY - 1):
                g[y][x] = "R"

    # Zubizuri: arco blanco y péndolas
    zx, zw = ZUBI
    for x in range(zx, zx + zw):
        g[QUAY + 1][x] = "Z"
        yy = QUAY + 1 - int(11 * math.sin((x - zx) / (zw - 1) * math.pi))
        g[yy][x] = "Z"
        g[min(yy + 1, QUAY)][x] = "Z"
        if (x - zx) % 3 == 0:
            for y in range(yy + 2, QUAY + 1):
                g[y][x] = "t"
    return g


def _bilbao() -> tuple[str, str]:
    rng = random.Random(7)
    rng.random()  # separado del de _grid: solo decide capas animadas
    g = _grid()
    rows = ["".join(r) for r in g]
    over = []
    for i in range(32):
        x, y = rng.randint(0, W - 1), rng.randint(0, 18)
        if rows[y][x] in "abcd" and not (140 <= x <= 150 and 2 <= y <= 12):
            over.append(f'<rect class="tw tw{i % 4}" x="{x}" y="{y}" width="1" height="1" fill="#f0f6fc"/>')
    ibx, ibw = IBERDROLA
    for x in range(ibx + 2, ibx + ibw - 1, 2):
        for y in range(8, 30, 3):
            if rng.random() < .55:
                over.append(f'<rect class="win win{rng.randint(0, 3)}" x="{x}" y="{y}" width="1" height="1" fill="#e3b341"/>')
    for x0, w, top in WINDOWED:
        for x in range(x0 + 1, x0 + w - 1, 2):
            for y in range(top + 2, QUAY - 1, 3):
                if rng.random() < .4:
                    over.append(f'<rect class="win win{rng.randint(0, 3)}" x="{x}" y="{y}" width="1" height="1" fill="#e3b341"/>')
    for i in range(16):
        x, y = rng.randint(0, W - 3), rng.randint(QUAY + 3, H - 2)
        over.append(f'<rect class="sh sh{i % 3}" x="{x}" y="{y}" width="2" height="1" fill="#e3b34188"/>')
    over.append('<g class="shoot"><rect x="0" y="0" width="1" height="1" fill="#fff"/>'
                '<rect x="-1" y="-1" width="1" height="1" fill="#ffffffaa"/>'
                '<rect x="-2" y="-2" width="1" height="1" fill="#ffffff55"/></g>')
    return rects(rows, PAL), "".join(over)


def _bilbao_svg(lang: str) -> str:
    base, over = _bilbao()
    body = f'<g transform="scale({SCALE})">{base}{over}</g>'
    title = {"es": "Bilbao de noche en pixel art", "en": "Bilbao at night in pixel art"}[lang]
    return document(W * SCALE, H * SCALE, title, body, css=CSS)


def _start_svg(lang: str) -> str:
    label = COPY[lang]["footer.start"]
    mail = "orueret@gmail.com"
    arrow_w, gap = len(ARROW[0][0]) * 3, 12
    total = arrow_w + gap + text_width(label, "ps2p", 16)
    x0 = (START_W - total) / 2
    pal = dict(ARROW[1], A="#3fb950")
    body = (sprite(ARROW[0], pal, x0, 14, 3, "blink")
            + text(x0 + arrow_w + gap, 30, label, "ps2p", 16, "#e6edf3", max_width=START_W - 2 * x0)
            + text(START_W / 2, 70, mail, "vt323", 26, "#58a6ff", anchor="middle", max_width=START_W))
    title = COPY[lang]["footer.start"]
    return document(START_W, START_H, title, body, css=BLINK_CSS, fonts=("ps2p", "vt323"))


def render(lang: str, live: LiveStats) -> dict[str, str]:
    return {"bilbao.svg": _bilbao_svg(lang), "start.svg": _start_svg(lang)}

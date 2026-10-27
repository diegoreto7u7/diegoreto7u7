"""Inventario (inventory.svg): el stack como objetos pixel en 2 filas de 5 casillas biseladas.

Un cursor amarillo (marco + ▼) salta de casilla en casilla cada 1,2 s. El estado base es el
cursor sobre la primera casilla, que es lo que queda con movimiento reducido.

Dos rejillas con el mismo dibujo (`Layout`): 5 columnas en escritorio (inventory.svg, 840 de
ancho) y 3 en el móvil (m-inventory.svg, 420 de ancho; la última fila queda incompleta).
"""

from dataclasses import dataclass

from gen.content import COPY, INVENTORY
from gen.live import LiveStats
from gen.pixel import sprite
from gen.scenes.common import BLINK_CSS, MOBILE_W, header
from gen.sprites.items import ITEMS
from gen.sprites.misc import DOWN
from gen.svg import document, rect, text

BG, BORDER, WELL, SHADOW, LIT = "#0d1117", "#21262d", "#161b22", "#0a0d12", "#30363d"
LABEL, YELLOW = "#c9d1d9", "#e3b341"

SLOT_H, GAP_Y = 104, 20
ROW0_Y = 74                 # deja sitio sobre la primera fila para el ▼
EDGE = 3                    # grosor del borde, de la sombra interior y del marco del cursor
ITEM_SCALE, ITEM_TOP = 4, 16
LABEL_BASE = 90             # línea base de la etiqueta, desde el borde superior de la casilla
ARROW_SCALE = 3
STEP = 1.2                  # segundos que el cursor pasa en cada casilla


@dataclass(frozen=True)
class Layout:
    """Rejilla de `cols` columnas de casillas de `slot_w` de ancho, separadas `gap_x`."""
    w: int
    cols: int
    slot_w: int
    gap_x: int


DESKTOP = Layout(w=840, cols=5, slot_w=160, gap_x=10)        # 5 × 160 + 4 × 10 = 840
MOBILE = Layout(w=MOBILE_W, cols=3, slot_w=132, gap_x=12)    # 3 × 132 + 2 × 12 = 420


def _origin(i: int, lay: Layout) -> tuple[int, int]:
    row, col = divmod(i, lay.cols)
    return col * (lay.slot_w + lay.gap_x), ROW0_Y + row * (SLOT_H + GAP_Y)


def _slot(i: int, name: str, lay: Layout) -> str:
    """Casilla hundida (sombra arriba y a la izquierda, luz abajo y a la derecha) con el objeto
    centrado y su nombre."""
    x, y = _origin(i, lay)
    slot_w = lay.slot_w
    rows, pal = ITEMS[name]
    item_w, item_h = len(rows[0]) * ITEM_SCALE, len(rows) * ITEM_SCALE
    box = 12 * ITEM_SCALE                       # los objetos miden 12 de ancho y hasta 12 de alto
    inner_w, inner_h = slot_w - 2 * EDGE, SLOT_H - 2 * EDGE
    return (rect(x, y, slot_w, SLOT_H, BORDER)
            + rect(x + EDGE, y + EDGE, inner_w, inner_h, WELL)
            + rect(x + EDGE, y + SLOT_H - 2 * EDGE, inner_w, EDGE, LIT)
            + rect(x + slot_w - 2 * EDGE, y + EDGE, EDGE, inner_h, LIT)
            + rect(x + EDGE, y + EDGE, inner_w, EDGE, SHADOW)
            + rect(x + EDGE, y + EDGE, EDGE, inner_h, SHADOW)
            + sprite(rows, pal, x + (slot_w - item_w) // 2,
                     y + ITEM_TOP + (box - item_h) // 2, ITEM_SCALE)
            + text(x + slot_w // 2, y + LABEL_BASE, name, "vt323", 22, LABEL, anchor="middle",
                   max_width=slot_w - 4 * EDGE))


def _cursor(lay: Layout) -> tuple[str, str]:
    """Marco amarillo y ▼ dibujados sobre la casilla 0; el @keyframes los lleva a las demás."""
    x, y = _origin(0, lay)
    slot_w = lay.slot_w
    rows, pal = DOWN[0], {**DOWN[1], "A": YELLOW}
    arrow_w, arrow_h = len(rows[0]) * ARROW_SCALE, len(rows) * ARROW_SCALE
    svg = (
        '<g class="cur">'
        + rect(x, y, slot_w, EDGE, YELLOW) + rect(x, y + SLOT_H - EDGE, slot_w, EDGE, YELLOW)
        + rect(x, y, EDGE, SLOT_H, YELLOW) + rect(x + slot_w - EDGE, y, EDGE, SLOT_H, YELLOW)
        + sprite(rows, pal, x + (slot_w - arrow_w) // 2, y - arrow_h - 3, ARROW_SCALE)
        + "</g>"
    )
    n = len(INVENTORY)
    stops = "".join(
        f"{i * 100 / n:g}%{{transform:translate({dx}px,{dy - y}px)}}"
        for i in range(1, n) for dx, dy in [_origin(i, lay)])
    css = f".cur{{animation:cur {STEP * n:g}s steps(1) infinite}}@keyframes cur{{{stops}}}"
    return svg, css


def _inventory(lang: str, lay: Layout) -> str:
    c = COPY[lang]
    cursor, cursor_css = _cursor(lay)
    body = (header(c["inv.title"], lay.w)
            + "".join(_slot(i, name, lay) for i, name in enumerate(INVENTORY))
            + cursor)
    h = _origin(len(INVENTORY) - 1, lay)[1] + SLOT_H + 8
    return document(lay.w, h, c["alt.inventory"], body, css=BLINK_CSS + cursor_css,
                    fonts=("ps2p", "vt323"), bg=BG)


def render(lang: str, live: LiveStats) -> dict[str, str]:
    return {"inventory.svg": _inventory(lang, DESKTOP),
            "m-inventory.svg": _inventory(lang, MOBILE)}

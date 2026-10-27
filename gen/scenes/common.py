"""Piezas compartidas por las escenas: el parpadeo y la cabecera de sección «▶ TÍTULO»."""

from gen.content import COPY
from gen.pixel import sprite
from gen.sprites.misc import ARROW
from gen.svg import text, text_width

BLINK_CSS = ".blink{animation:blink 1s steps(1) infinite}@keyframes blink{50%{opacity:0}}"
HEADER_W, HEADER_H = 840, 56
MOBILE_W = 420  # lienzo de las variantes m-*.svg: en el móvil se ven a ≈ 276 px (escala ≈ 0,66)
# Títulos de las cabeceras de sección: en un mismo ancho van todas al mismo tamaño.
SECTION_TITLES = ("sheet.title", "ach.title", "inv.title", "quests.title", "hs.title")


def header_size(width: int) -> int:
    """El mayor tamaño (20, 18 o 16) al que caben en `width` todas las cabeceras de los dos idiomas.

    En escritorio (840) es 20. En el móvil (420), 18: «LOGROS DESBLOQUEADOS» mide 400 a 20 y no
    cabe en 392; las demás bajan con ella para que todas las cabeceras móviles sean iguales.
    """
    room = width - 28
    labels = [COPY[lang][key] for lang in COPY for key in SECTION_TITLES]
    return next((s for s in (20, 18)
                 if all(text_width(label, "ps2p", s) <= room for label in labels)), 16)


def header(label: str, width: int = HEADER_W) -> str:
    """Cabecera de sección: «▶» verde parpadeando, título en ps2p y una línea debajo.

    Ocupa la franja superior de `width` × 56 de su lienzo (840 en escritorio, MOBILE_W en las
    variantes móviles); necesita BLINK_CSS y la fuente ps2p. El tamaño es `header_size(width)`.
    """
    room = width - 28
    return (sprite(ARROW[0], ARROW[1], 0, 15, 3, "blink")
            + text(28, 34, label, "ps2p", header_size(width), "#f0f6fc", max_width=room)
            + f'<rect x="0" y="46" width="{width}" height="2" fill="#30363d"/>')

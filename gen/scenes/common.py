"""Piezas compartidas por las escenas: el parpadeo y la cabecera de sección «▶ TÍTULO»."""

from gen.pixel import sprite
from gen.sprites.misc import ARROW
from gen.svg import text, text_width

BLINK_CSS = ".blink{animation:blink 1s steps(1) infinite}@keyframes blink{50%{opacity:0}}"
HEADER_W, HEADER_H = 840, 56
MOBILE_W = 420  # lienzo de las variantes m-*.svg: en el móvil se ven a ≈ 276 px (escala ≈ 0,66)


def header(label: str, width: int = HEADER_W) -> str:
    """Cabecera de sección: «▶» verde parpadeando, título en ps2p 20 y una línea debajo.

    Ocupa la franja superior de `width` × 56 de su lienzo (840 en escritorio, MOBILE_W en las
    variantes móviles); necesita BLINK_CSS y la fuente ps2p. Si el título no cabe a 20 (solo
    pasa en el móvil: «LOGROS DESBLOQUEADOS» mide 400), baja a 18 y, si hace falta, a 16.
    """
    room = width - 28
    size = next((s for s in (20, 18) if text_width(label, "ps2p", s) <= room), 16)
    return (sprite(ARROW[0], ARROW[1], 0, 15, 3, "blink")
            + text(28, 34, label, "ps2p", size, "#f0f6fc", max_width=room)
            + f'<rect x="0" y="46" width="{width}" height="2" fill="#30363d"/>')

"""Piezas compartidas por las escenas: el parpadeo y la cabecera de sección «▶ TÍTULO»."""

from gen.pixel import sprite
from gen.sprites.misc import ARROW
from gen.svg import text

BLINK_CSS = ".blink{animation:blink 1s steps(1) infinite}@keyframes blink{50%{opacity:0}}"
HEADER_W, HEADER_H = 840, 56


def header(label: str) -> str:
    """Cabecera de sección: «▶» verde parpadeando, título en ps2p 20 y una línea debajo.

    Ocupa la franja superior de 840 × 56 de su lienzo; necesita BLINK_CSS y la fuente ps2p.
    """
    return (sprite(ARROW[0], ARROW[1], 0, 15, 3, "blink")
            + text(28, 34, label, "ps2p", 20, "#f0f6fc", max_width=HEADER_W - 28)
            + f'<rect x="0" y="46" width="{HEADER_W}" height="2" fill="#30363d"/>')

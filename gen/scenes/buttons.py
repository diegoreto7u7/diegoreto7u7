"""Botones pixel enlazables: relieve con luz arriba-izquierda y sombra abajo-derecha."""

from gen.content import COPY
from gen.live import LiveStats
from gen.pixel import sprite
from gen.sprites.misc import ARROW, DOWNLOAD, ENVELOPE, GLOBE, LINKEDIN_IN
from gen.svg import document, text, text_width

W, H, BEVEL, SCALE, GAP = 216, 56, 4, 3, 12
INK = "#0d1117"
BLINK_CSS = ".blink{animation:blink 1s steps(1) infinite}@keyframes blink{50%{opacity:0}}"


def _light(hex_color: str) -> str:
    """Mezcla un 45 % de blanco para el borde iluminado."""
    c = [int(hex_color[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(v + (255 - v) * 0.45):02x}" for v in c)


# nombre, clave de texto, color, sombra, sprite, parpadea
BUTTONS = [
    ("btn-portfolio", "btn.portfolio", "#3fb950", "#238636", (ARROW[0], {"A": INK}), True),
    ("btn-linkedin", "btn.linkedin", "#58a6ff", "#1f6feb", LINKEDIN_IN, False),
    ("btn-email", "btn.email", "#e3b341", "#9e6a03", ENVELOPE, False),
    ("btn-cv", "btn.cv", "#d2a8ff", "#8957e5", DOWNLOAD, False),
    ("btn-lang", "btn.lang", "#c9d1d9", "#6e7681", GLOBE, False),
]


def _button(label: str, face: str, shade: str, icon, blink: bool) -> str:
    rows, pal = icon
    iw, ih = len(rows[0]) * SCALE, len(rows) * SCALE
    tw = text_width(label, "ps2p", 16)
    x0 = (W - (iw + GAP + tw)) / 2
    body = (
        f'<rect x="0" y="0" width="{W}" height="{H}" fill="{shade}"/>'
        f'<rect x="0" y="0" width="{W - BEVEL}" height="{H - BEVEL}" fill="{_light(face)}"/>'
        f'<rect x="{BEVEL}" y="{BEVEL}" width="{W - 2 * BEVEL}" height="{H - 2 * BEVEL}" fill="{face}"/>'
        + sprite(rows, pal, x0, (H - ih) / 2, SCALE, "blink" if blink else "")
        + text(x0 + iw + GAP, 34, label, "ps2p", 16, INK, max_width=W - 2 * BEVEL - iw - GAP)
    )
    return body


def render(lang: str, live: LiveStats) -> dict[str, str]:
    out = {}
    for name, key, face, shade, icon, blink in BUTTONS:
        label = COPY[lang][key]
        svg = document(W, H, label, _button(label, face, shade, icon, blink),
                       css=BLINK_CSS if blink else "", fonts=("ps2p",))
        out[f"{name}.svg"] = svg
    return out

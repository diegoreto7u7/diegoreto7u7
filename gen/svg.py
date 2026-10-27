"""Documento SVG, texto medido y ajuste de líneas."""

from typing import Iterable

from gen.fonts import ADVANCE, CHARSET, MIN_SIZE, font_face_css
from gen.pixel import FRAME_CSS, num

REDUCED_MOTION = "@media (prefers-reduced-motion: reduce){*{animation:none!important}}"


def escape(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def rect(x, y, w, h, fill, extra="") -> str:
    """Un <rect> con los valores tal cual; `extra` añade atributos (p. ej. ' class="blink"')."""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"{extra}/>'


def pct(t: float, cycle: float, trim: bool = False) -> str:
    """Momento `t` (s) de un ciclo de `cycle` s como porcentaje de @keyframes, sin el «%».

    Con dos decimales («12.50»); con `trim`, sin ceros sobrantes («12.5», «10»).
    """
    s = f"{t * 100 / cycle:.2f}"
    return s.rstrip("0").rstrip(".") if trim else s


def text_width(s: str, font: str, size: float) -> float:
    return len(s) * ADVANCE[font] * size


def text(x, y, s, font, size, fill, cls="", anchor="start", max_width=None) -> str:
    if size < MIN_SIZE[font]:
        raise ValueError(f"tamaño {size} menor que el mínimo {MIN_SIZE[font]} de {font}")
    bad = sorted({c for c in s if c not in CHARSET})
    if bad:
        raise ValueError(f"caracteres fuera del recorte de fuente: {''.join(bad)!r}")
    if max_width is not None and text_width(s, font, size) > max_width:
        raise ValueError(f"el texto {s!r} no cabe en {max_width}")
    c = f' class="{cls}"' if cls else ""
    return (f'<text x="{num(x)}" y="{num(y)}" font-family="{font}" '
            f'font-size="{num(size)}" fill="{fill}" text-anchor="{anchor}"{c}>'
            f'{escape(s)}</text>')


def wrap(s, font, size, max_width) -> list[str]:
    lines: list[str] = []
    cur = ""
    for word in s.split():
        trial = f"{cur} {word}" if cur else word
        if cur and text_width(trial, font, size) > max_width:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


def document(width: int, height: int, title: str, body: str, css: str = "",
             fonts: Iterable[str] = (), bg: str = "#0d1117") -> str:
    style = font_face_css(fonts)
    if 'class="f1"' in body:
        style += FRAME_CSS
    style += css
    if "@keyframes" in style:
        style += REDUCED_MOTION
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}" role="img" shape-rendering="crispEdges">'
        f'<title>{escape(title)}</title><style>{style}</style>'
        f'<rect width="{width}" height="{height}" fill="{bg}"/>{body}</svg>'
    )

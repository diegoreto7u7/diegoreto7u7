"""Documento SVG, texto medido y ajuste de líneas."""

from itertools import combinations
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


def balanced_wrap(s, font, size, max_width) -> list[str]:
    """Las mismas líneas que `wrap`, repartidas para que la más larga sea lo más corta posible.

    Evita la última línea con una palabra suelta («PULSA START PARA HABLAR» / «CONMIGO»). Prueba
    todos los cortes, así que es para rótulos cortos, no para párrafos.
    """
    greedy = wrap(s, font, size, max_width)
    words = s.split()
    if not words:
        return greedy
    best, best_w = greedy, max((text_width(line, font, size) for line in greedy), default=0)
    for cuts in combinations(range(1, len(words)), len(greedy) - 1):
        bounds = (0, *cuts, len(words))
        lines = [" ".join(words[a:b]) for a, b in zip(bounds, bounds[1:])]
        widest = max(text_width(line, font, size) for line in lines)
        if widest < best_w:
            best, best_w = lines, widest
    return best


def wrap_keep(s, font, size, max_width, wrapper=wrap) -> list[str]:
    """Como `wrap` (o `wrapper`), pero sin partir lo que va entre paréntesis («(300 h)» queda en
    una línea) y sin empezar una línea con «·»: el separador se queda al final de la anterior."""
    out, depth = [], 0
    for ch in s.replace(" · ", "\0· "):
        depth += (ch == "(") - (ch == ")")
        out.append("\0" if ch == " " and depth > 0 else ch)
    return [line.replace("\0", " ") for line in wrapper("".join(out), font, size, max_width)]


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

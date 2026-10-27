"""Convierte sprites ASCII en elementos <rect> de SVG."""

from typing import Mapping, Sequence

FRAME_CSS = (
    ".f2{opacity:0}"
    ".f1{animation:f1k 1s steps(1) infinite}"
    ".f2{animation:f2k 1s steps(1) infinite}"
    "@keyframes f1k{0%{opacity:1}50%{opacity:0}}"
    "@keyframes f2k{0%{opacity:0}50%{opacity:1}}"
)


def _num(v: float) -> str:
    return str(int(v)) if float(v).is_integer() else f"{v:g}"


def validate(rows: Sequence[str], palette: Mapping[str, str]) -> None:
    if not rows:
        raise ValueError("el sprite está vacío")
    width = len(rows[0])
    for r in rows:
        if len(r) != width:
            raise ValueError("las filas del sprite tienen distinto largo")
        for ch in r:
            if ch != "." and ch not in palette:
                raise ValueError(f"carácter {ch!r} sin color en la paleta")


def rects(rows: Sequence[str], palette: Mapping[str, str],
          x: float = 0, y: float = 0, scale: float = 1) -> str:
    validate(rows, palette)
    out = []
    for row_i, row in enumerate(rows):
        col = 0
        while col < len(row):
            ch = row[col]
            run = col
            while run < len(row) and row[run] == ch:
                run += 1
            if ch != ".":
                out.append(
                    f'<rect x="{_num(x + col * scale)}" y="{_num(y + row_i * scale)}" '
                    f'width="{_num((run - col) * scale)}" height="{_num(scale)}" '
                    f'fill="{palette[ch]}"/>'
                )
            col = run
    return "".join(out)


def _cls(cls: str) -> str:
    return f' class="{cls}"' if cls else ""


def sprite(rows: Sequence[str], palette: Mapping[str, str],
           x: float, y: float, scale: float, cls: str = "") -> str:
    return f"<g{_cls(cls)}>{rects(rows, palette, x, y, scale)}</g>"


def two_frames(a: Sequence[str], b: Sequence[str], palette: Mapping[str, str],
               x: float, y: float, scale: float, cls: str = "") -> str:
    f1 = rects(a, palette, x, y, scale)
    f2 = rects(b, palette, x, y, scale)
    return f'<g{_cls(cls)}><g class="f1">{f1}</g><g class="f2">{f2}</g></g>'

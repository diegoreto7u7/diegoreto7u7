"""Recorta una TTF a CHARSET y la guarda como WOFF (uso único).

Uso: PYTHONPATH=<wheel de fontTools>:. python3 tools/subset_fonts.py <ttf> <salida.woff>
"""

import sys
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from gen.fonts import CHARSET  # noqa: E402


def main(src: str, dst: str) -> None:
    cmap = TTFont(src).getBestCmap()
    missing = [c for c in CHARSET if ord(c) not in cmap]
    if missing:
        raise SystemExit(f"a la fuente le faltan: {''.join(missing)!r}")
    opts = subset.Options(flavor="woff", hinting=False)
    opts.recalc_timestamp = False
    font = subset.load_font(src, opts)
    sub = subset.Subsetter(opts)
    sub.populate(text=CHARSET)
    sub.subset(font)
    subset.save_font(font, dst, opts)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    main(sys.argv[1], sys.argv[2])

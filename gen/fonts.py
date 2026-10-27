"""Recorte de caracteres, métricas y @font-face de las fuentes pixel."""

import base64
from pathlib import Path
from typing import Iterable

CHARSET = (
    "".join(chr(c) for c in range(0x20, 0x7F))
    + "áéíóúñüÁÉÍÓÚÑÜ·¿¡«»—–"
)
MIN_SIZE = {"ps2p": 16, "vt323": 22}
ADVANCE = {"ps2p": 1.0, "vt323": 0.4}

_FONTS_DIR = Path(__file__).resolve().parent.parent / "fonts"
_FILES = {"ps2p": "press-start-2p.woff", "vt323": "vt323.woff"}


def font_face_css(families: Iterable[str]) -> str:
    out = []
    for fam in families:
        if fam not in _FILES:
            raise ValueError(f"fuente desconocida: {fam!r}")
        data = base64.b64encode((_FONTS_DIR / _FILES[fam]).read_bytes()).decode("ascii")
        out.append(
            f'@font-face{{font-family:"{fam}";src:url(data:font/woff;base64,{data})}}'
        )
    return "".join(out)

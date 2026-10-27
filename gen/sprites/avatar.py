"""Avatar de Diego tecleando: pelo castaño corto, sudadera, reloj y pulsera de plata.

La cámara es la pantalla: se le ve de frente, con las dos manos sobre el teclado.
Pulsera en la muñeca derecha (izquierda del sprite) y reloj en la izquierda.
"""

from gen.sprites import shade

# Rasgos sin confirmar: se cambian en una línea y las sombras se recalculan solas.
HAIR = "#6b4423"     # castaño
SKIN = "#e8b48a"     # clara-media
HOODIE = "#2ea043"

PALETTE = {
    "H": HAIR, "h": shade(HAIR, 0.2), "d": shade(HAIR, -0.35),
    "S": SKIN, "s": shade(SKIN, -0.14), "m": shade(SKIN, -0.42),
    "K": "#2b1d16", "e": "#ffffff",
    "G": HOODIE, "g": shade(HOODIE, -0.35), "L": shade(HOODIE, 0.25), "c": shade(HOODIE, -0.18),
    "D": "#e6edf3", "a": "#afb8c1",
    "W": "#1c2128", "w": "#56d4dd",
    "B": "#c0c7d0", "b": "#eef2f6",
    "k": "#30363d", "j": "#161b22", "n": "#6e7681", "N": "#8b949e", "y": "#3fb950",
}

_BASE = [
    "........................",
    "........dHHHHHHd........",
    "......dHHhhhHHHHHd......",
    ".....dHHhHHHHHHHHHd.....",
    ".....dHHHHHHdHHHHHd.....",
    ".....dHSSSSSHHHHHHd.....",
    ".....dSSSSSSSSSHHSd.....",
    ".....dSSddSSSSddSSd.....",
    "....SSSSeKSSSSeKSSSS....",
    "....sSSSKKSSSSKKSSSs....",
    "....SSSSSSSsSSSSSSSS....",
    ".....SSSSSSmmSSSSSS.....",
    "......SSSSSSSSSSSS......",
    ".....LLsSSSSSSSSsLL.....",
    "....gLLLLssssssLLLLg....",
    "..gGGLLLLLssssLLLLLGGg..",
    ".gGGGGgLLLLssLLLLgGGGGg.",
    "gGGGgGGGGLDLLDLGGGGgGGGg",
    "gGGGgGGGGGDGGDGGGGGgGGGg",
    "gGGGgGGGGGDGGDGGGGGgGGGg",
    "gGGGgGGGGGaGGaGGGGGgGGGg",
    "gGGGgGggggggggggggGgGGGg",
    "gGGGgcgccccccccccgcgGGGg",
    "gGGGgcgccccccccccgcgGGGg",
    "gGGGgcgccccccccccgcgGGGg",
    "..NNNNNNNNNNNNNNNNNNNN..",
    ".knnknnknnknnknnknnknnk.",
    "kkknnknnknnknnknnknnkyyk",
    "kknnknnnnnnnnnnnknnknnkk",
    "jjjjjjjjjjjjjjjjjjjjjjjj",
]

# Antebrazo, puño acanalado, muñeca y mano (el pulgar hacia dentro); «.» deja ver la base.
_HAND_BRACELET = [
    "gGGGg...",
    "gLGGGg..",
    ".gLGGGg.",
    "..gLGGGg",
    "..cgcgc.",
    "..BbBBB.",
    "..SSSSSS",
    "..sSSSSs",
    "..SsSsS.",
]
_HAND_WATCH = [
    "...gGGGg",
    "..gGGGLg",
    ".gGGGLg.",
    "gGGGLg..",
    ".cgcgc..",
    ".WwwwW..",
    "SSSSSS..",
    "sSSSSs..",
    ".SsSsS..",
]


def _paste(grid: list[list[str]], piece: list[str], x: int, y: int) -> None:
    for dy, row in enumerate(piece):
        for dx, ch in enumerate(row):
            if ch != ".":
                grid[y + dy][x + dx] = ch


def _frame(left_up: bool) -> list[str]:
    grid = [list(r) for r in _BASE]
    _paste(grid, _HAND_BRACELET, 0, 18 if left_up else 19)
    _paste(grid, _HAND_WATCH, 16, 19 if left_up else 18)
    return ["".join(r) for r in grid]


def _close_eyes(rows: list[str]) -> list[str]:
    out = list(rows)
    eye_rows = [i for i, r in enumerate(rows) if "K" in r]
    out[eye_rows[0]] = rows[eye_rows[0]].replace("e", "S").replace("K", "S")
    for i in eye_rows[1:]:
        out[i] = rows[i].replace("K", "d")
    return out


AVATAR_A = _frame(left_up=True)
AVATAR_B = _frame(left_up=False)
AVATAR_BLINK = _close_eyes(AVATAR_A)

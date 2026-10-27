"""Detalles sueltos: gato, planta, trofeo, glifos (▶ ▼ ● ★ ♥), iconos de botones y misiones,
taza humeante, Pac-Man y fantasmas.

Los glifos de un solo color (ARROW, DOWN, DOT) usan solo la clave «A», para que la escena
pueda recolorearlos (p. ej. la flecha en tinta sobre el botón del portfolio).
Los iconos de los botones van en tinta oscura para leerse sobre el color del botón.
"""

from gen.sprites.items import CRAB

INK = "#0d1117"
PAPER = "#f0f6fc"

CAT = ([
    ".o....o...........",
    ".Op..pO..OoOOoOO..",
    "OOOOOOOOOOOOoOOOO.",
    "OkkOOkkOOOOOOOOOOO",
    "OOwppwOOOoOOOoOOOO",
    ".OwwwwOOOOOOOOOOoO",
    ".wWwwWwOOOOOOOOOoO",
    "..oooooooooooooOo.",
], {"O": "#e3a03b", "o": "#b8761f", "k": "#3b2a1e", "w": "#f6e7cf", "W": "#d9c4a5",
    "p": "#f2a3a3"})

PLANT = ([
    "....L.....",
    "..L.GL..L.",
    ".LGLGGLLG.",
    "LGGGLGGGGL",
    ".GGgGGgGG.",
    "..gGGgGg..",
    "...g.g....",
    ".rrrrrrrr.",
    "..oooooo..",
    "..oOoooo..",
    "...oooo...",
], {"L": "#56d364", "G": "#2ea043", "g": "#196c2e", "r": "#d9895b", "o": "#b4653f",
    "O": "#8a4a2c"})

TROPHY = ([
    "..wYYYYYYY..",
    "YYYwYYYYYoYY",
    "Y.YwYYYYYo.Y",
    "Y.YYYYYYYo.Y",
    ".YYYYYYYYoY.",
    "...YYYYYo...",
    "....YYYo....",
    ".....Yo.....",
    ".....Yo.....",
    "...oYYYYo...",
    "..bbbbbbbb..",
    "..bbbbbbbb..",
], {"Y": "#e3b341", "w": "#fff2b3", "o": "#9e6a03", "b": "#6e4b2a"})

_HEART = [
    ".RR.RR.",
    "RwRRRRR",
    "RRRRRRR",
    ".RRRRR.",
    "..RRR..",
    "...R...",
]
HEART_ON = (_HEART, {"R": "#f85149", "w": "#ffc1bd"})
HEART_OFF = ([
    ".OO.OO.",
    "ORROROO",
    "ORRRRRO",
    ".ORRRO.",
    "..ORO..",
    "...O...",
], {"O": "#484f58", "R": "#21262d"})

STAR = ([
    "....Y....",
    "....Y....",
    "...YwY...",
    "YYYYwYYYY",
    ".YYYYYYY.",
    "..YYYYY..",
    "..YYoYY..",
    ".YYo.oYY.",
    ".Yo...oY.",
], {"Y": "#e3b341", "w": "#fff2b3", "o": "#9e6a03"})

ARROW = ([
    "A...",
    "AA..",
    "AAA.",
    "AAAA",
    "AAA.",
    "AA..",
    "A...",
], {"A": "#3fb950"})

DOWN = ([
    "AAAAAAA",
    ".AAAAA.",
    "..AAA..",
    "...A...",
], {"A": "#e6edf3"})

DOT = ([
    ".AAA.",
    "AAAAA",
    "AAAAA",
    "AAAAA",
    ".AAA.",
], {"A": "#3fb950"})

ENVELOPE = ([
    "kkkkkkkkk",
    "kkwwwwwkk",
    "kwkwwwkwk",
    "kwwkwkwwk",
    "kwwwkwwwk",
    "kwwwwwwwk",
    "kkkkkkkkk",
], {"k": INK, "w": PAPER})

LINKEDIN_IN = ([
    ".kkkkkk.",
    "kkwkkkkk",
    "kkkkkkkk",
    "kkwkwwkk",
    "kkwkwkwk",
    "kkwkwkwk",
    "kkwkwkwk",
    ".kkkkkk.",
], {"k": INK, "w": PAPER})

DOWNLOAD = ([
    "...kk...",
    "...kk...",
    "...kk...",
    ".kkkkkk.",
    "..kkkk..",
    "...kk...",
    "k......k",
    "kkkkkkkk",
], {"k": INK})

GLOBE = ([
    "..kkkkk..",
    ".k.k.k.k.",
    "k..k.k..k",
    "kkkkkkkkk",
    "k..k.k..k",
    "kkkkkkkkk",
    "k..k.k..k",
    ".k.k.k.k.",
    "..kkkkk..",
], {"k": INK})

CAMERA = ([
    "..ssssssss..",
    ".sWWWWWWWWs.",
    ".WWWWWWWWWkk",
    ".WWWWWWWWWkL",
    ".wwwwwwwRWkk",
    "..wwwwwwww..",
    ".....gg.....",
    ".....gg.....",
    "...gggggg...",
], {"s": "#6e7681", "W": "#c9d1d9", "w": "#8b949e", "k": "#21262d", "L": "#58a6ff",
    "R": "#f85149", "g": "#484f58"})

DOCUMENT = ([
    "WWWWWWWf....",
    "WkkkkWWff...",
    "WWWWWWWWW...",
    "WkkkkkkWW...",
    "WWWWWWWWW...",
    "WkkkkkWWW...",
    "WWWWWWbbbb..",
    "WkkkkbLLLLb.",
    "WWWWWbLLLLb.",
    ".....bLLLLb.",
    "......bbbbmm",
    "...........m",
], {"W": PAPER, "f": "#c9d1d9", "k": "#8b949e", "b": "#58a6ff", "L": "#a5d6ff", "m": "#9e6a03"})

CITY = ([
    ".......Y.Y..",
    "........Y...",
    "........A...",
    ".......BBB..",
    "..CC...BYB..",
    "..CC.D.BBB..",
    ".CYC.DDBYB.C",
    ".CCCDDDBBBCC",
    ".CYCDYDBYBCY",
    "CCCCDDDBBBCC",
    "CYCCDYDBYBCY",
    "CCCCDDDBBBCC",
], {"B": "#3fb950", "C": "#2ea043", "D": "#39c5bb", "Y": "#e3b341", "A": "#8b949e"})

ICONS: dict[str, tuple[list[str], dict[str, str]]] = {
    "camera": CAMERA,
    "document": DOCUMENT,
    "crab": CRAB,
    "city": CITY,
}

MUG = ([
    "...s....",
    "..s..s..",
    "...s.s..",
    "..s..s..",
    "MmmmmmM.",
    "MMMMMMMM",
    "MMMMMM.M",
    "RRRRRR.M",
    "MMMMMMMM",
    ".MMMMM..",
], [
    "..s..s..",
    "...s..s.",
    "..s..s..",
    "...s....",
    "MmmmmmM.",
    "MMMMMMMM",
    "MMMMMM.M",
    "RRRRRR.M",
    "MMMMMMMM",
    ".MMMMM..",
], {"s": "#8b949e", "M": "#f0f6fc", "m": "#6e4b2a", "R": "#f85149"})

PAC = ([
    "..YYY..",
    ".YYYYY.",
    "YYYY...",
    "YYY....",
    "YYYY...",
    ".YYYYY.",
    "..YYY..",
], [
    "..YYY..",
    ".YYYYY.",
    "YYYYYYY",
    "YYYYYYY",
    "YYYYYYY",
    ".YYYYY.",
    "..YYY..",
], {"Y": "#e3b341"})

_GHOST = [
    "..GGG..",
    ".GGGGG.",
    "GwwGwwG",
    "GwpGwpG",
    "GGGGGGG",
    "GGGGGGG",
    "G.G.G.G",
]


def ghost(color: str) -> tuple[list[str], dict[str, str]]:
    """Fantasma del color dado, mirando a la derecha."""
    return _GHOST, {"G": color, "w": PAPER, "p": "#1f6feb"}

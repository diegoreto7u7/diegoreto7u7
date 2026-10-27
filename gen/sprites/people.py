"""Cuatro personas de 10×16 que cruzan la cámara de la cabecera, de perfil y mirando a la derecha.

Fotograma A: zancada, con los brazos balanceándose. Fotograma B: piernas juntas y brazo caído.
Las extremidades del lado lejano van en un tono más oscuro (c, p, z) para que se lea el paso.
"""

# Cabezas (filas 0-4) y cuello (fila 5).
_SHORT = [
    "...HHHH...",
    "..HHHHHH..",
    "..HHHSKS..",
    "..HHSSSSS.",
    "...HSSSS..",
    "....sSS...",
]
_PONYTAIL = [
    "...HHHH...",
    "..HHHHHH..",
    ".HHHHSKS..",
    "HH.HSSSSS.",
    "H..HSSSS..",
    "....sSS...",
]
_CURLY = [
    "..HhHhH...",
    ".HhHHhHH..",
    ".HHhHSKS..",
    "..HHSSSSS.",
    "...HSSSS..",
    "....sSS...",
]
_BOB = [
    "...HHHH...",
    "..HHHHHHH.",
    "..HHHSKSH.",
    "..HHHSSSS.",
    "..HHSSSS..",
    "..H.sSS...",
]

_TORSO_A = [
    "...cCCC...",
    "..ccCCCC..",
    ".cc.CCCCC.",
    ".S..CCC.S.",
    "...CCCC...",
]
_TORSO_B = [
    "...CCCC...",
    "...CCCC...",
    "...CCCCC..",
    "...CCCSC..",
    "...CCCC...",
]
_BAG_A = [
    ".BBbCCC...",
    ".BBbCCCC..",
    ".BBbCCCCC.",
    ".BB.CCC.S.",
    "...CCCC...",
]
_BAG_B = [
    ".BBbCCC...",
    ".BBbCCC...",
    ".BBbCCCC..",
    ".BB.CCSC..",
    "...CCCC...",
]
_LEGS_A = [
    "...PPPP...",
    "..pPP.PP..",
    "..pp...PP.",
    ".pp....PP.",
    ".zz....ZZZ",
]
_LEGS_B = [
    "...PPPP...",
    "...PPPp...",
    "...PP.p...",
    "...PP.pp..",
    "...ZZZ.zz.",
]


def _person(head: list[str], palette: dict[str, str],
            bag: bool = False) -> tuple[list[str], list[str], dict[str, str]]:
    torso_a, torso_b = (_BAG_A, _BAG_B) if bag else (_TORSO_A, _TORSO_B)
    return head + torso_a + _LEGS_A, head + torso_b + _LEGS_B, palette


def _pal(hair, skin, skin_shade, shirt, shirt_back, pants, pants_back, shoes, shoes_back, **extra):
    return {"H": hair, "S": skin, "s": skin_shade, "K": "#0d1117", "C": shirt, "c": shirt_back,
            "P": pants, "p": pants_back, "Z": shoes, "z": shoes_back, **extra}


PEOPLE = [
    _person(_SHORT, _pal("#4a3020", "#f0c8a0", "#d4a37c", "#2f81f7", "#1f5fbf",
                         "#b08d5b", "#86683f", "#e6edf3", "#a8b1bb")),
    _person(_PONYTAIL, _pal("#d29922", "#c69472", "#a87655", "#da3633", "#a32422",
                            "#1f6feb", "#164fae", "#f0883e", "#bd561d",
                            B="#6e4b2a", b="#4a3020"), bag=True),
    _person(_CURLY, _pal("#2f2a29", "#8d5524", "#6e3f18", "#3fb950", "#23863a",
                         "#6e7681", "#484f58", "#e6edf3", "#a8b1bb", h="#55504e")),
    _person(_BOB, _pal("#8957e5", "#f0c8a0", "#d4a37c", "#e6edf3", "#a8b1bb",
                       "#1b7c83", "#125a5f", "#da3633", "#a32422")),
]

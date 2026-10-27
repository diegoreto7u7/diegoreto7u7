"""Objetos del inventario: interpretaciones pixel propias de cada tecnología, no logos oficiales."""

PYTHON = ([
    "...BBBBBB...",
    "..BwBBBBBB..",
    "..BBBBBBBB..",
    "..BBB.......",
    "BBBBBBBBbbY.",
    "BBBBBBBbbYYY",
    "BBBbyYYYYYYY",
    ".BByYYYYYYYY",
    ".......YYY..",
    "..YYYYYYYY..",
    "..YYYYYYwY..",
    "...YYYYYY...",
], {"B": "#3572a5", "b": "#24507a", "Y": "#ffd43b", "y": "#c9a227", "w": "#f0f6fc"})

GOPHER = ([
    ".bB......Bb.",
    ".BBBBBBBBBB.",
    "BwwwBBBBwwwB",
    "BwKwBBBBwKwB",
    "BwwwBBBBwwwB",
    "BBBBcnncBBBB",
    "BBBBccccBBBB",
    "BBBBBwwBBBBB",
    "cBBBBBBBBBBc",
    ".BBBBBBBBBB.",
    "..bBBBBBBb..",
    ".cc......cc.",
], {"B": "#00add8", "b": "#007d9c", "w": "#f0f6fc", "K": "#0d1117",
    "c": "#e0b48a", "n": "#3b2a1e"})

CRAB = ([
    "O.O......O.O",
    "OOO......OOO",
    ".O..OOOO..O.",
    ".OOOOOOOOOO.",
    "..OOwKOwKOO.",
    "OOOOOOOOOOOO",
    ".OOOOooOOOO.",
    ".OoOOOOOOoO.",
    ".O.o....o.O.",
    "O..O....O..O",
], {"O": "#f74c00", "o": "#a33500", "w": "#f0f6fc", "K": "#0d1117"})

PENGUIN = ([
    "...kKKKKK...",
    "..kKKKKKKK..",
    "..kwpKKwpK..",
    "..kwwKKwwK..",
    "..KKYYYYKK..",
    ".kKKwYYwKKK.",
    ".kKwwwwwwKK.",
    "kKwwwwwwwwKK",
    "kKwwwwwwwwKK",
    "kKwwwwwwwwKK",
    ".kKwwwwwwKK.",
    ".YYYK..KYYY.",
], {"K": "#343a42", "k": "#57606a", "w": "#f0f6fc", "p": "#0d1117", "Y": "#e3b341"})

WHALE = ([
    "....Cc.Cc...",
    "....cc.cc...",
    "............",
    ".Cc.Cc.Cc..B",
    ".cc.cc.cc.BB",
    "BBBBBBBBBBBB",
    "BBBBBBBBBBB.",
    "BwBBBBBBBBB.",
    "BBBBBBBBBB..",
    ".BBBBBBBBb..",
    "..bbbbbbb...",
], {"B": "#2496ed", "b": "#1a6fb5", "C": "#c5e6ff", "c": "#7cc4f5", "w": "#f0f6fc"})

HELM = ([
    ".....BB.....",
    "...BBBBBB...",
    ".BBBBwwBBBB.",
    ".BBwBwwBwBB.",
    "BBBBwwwwBBBB",
    "BBwwwBBwwwBB",
    "BBwwwBBwwwBB",
    "BBBBwwwwBBBB",
    ".BBwBwwBwBB.",
    ".BBBBwwBBBB.",
    "..BBBBBBBB..",
    "....BBBB....",
], {"B": "#326ce5", "w": "#f0f6fc"})

ELEPHANT = ([
    ".bbb....bbb.",
    "bbbbBBBBbbbb",
    "bbbBBBBBBbbb",
    "bbbBKBBKBbbb",
    "bbbBBBBBBbbb",
    ".bbBBBBBBbb.",
    "..bwBBBBwb..",
    "....BBBB....",
    "....BBB.....",
    ".....BB.....",
    "......BB....",
    ".......B....",
], {"B": "#336791", "b": "#6b9bd1", "K": "#0d1117", "w": "#f0f6fc"})

ATOM = ([
    "..CC....CC..",
    "..C.C..C.C..",
    "...C.CC.C...",
    ".CCCCCCCCCC.",
    "C..C.CC.C..C",
    "C...CwwC...C",
    "C...CwwC...C",
    "C..C.CC.C..C",
    ".CCCCCCCCCC.",
    "...C.CC.C...",
    "..C.C..C.C..",
    "..CC....CC..",
], {"C": "#61dafb", "w": "#f0f6fc"})

GPU = ([
    "kkkkkkkkkkks",
    "k.FF.k.FF.ks",
    "kFhhFkFhhFks",
    "kFhhFkFhhFks",
    "k.FF.k.FF.ks",
    "kGGGGGGGGGks",
    "pppppppppp.s",
    ".yyyy.yyy..s",
], {"k": "#484f58", "F": "#8b949e", "h": "#21262d", "G": "#76b900", "p": "#1a7f37",
    "y": "#e3b341", "s": "#c9d1d9"})

VIDEO = ([
    "kkkkkkkkkkkk",
    "kddddddddRdk",
    "kdgggggddddk",
    "kdgdSdgddddk",
    "kdgdCdgdddDk",
    "kdgCCCgddDDk",
    "kdgdPdgdDDDk",
    "kdgggggDDDDk",
    "kkkkkkkkkkkk",
    "....kkkk....",
    "...kkkkkk...",
], {"k": "#484f58", "d": "#0b1a2a", "R": "#f85149", "g": "#3fb950", "S": "#f0c8a0",
    "C": "#58a6ff", "P": "#30363d", "D": "#123049"})

ITEMS: dict[str, tuple[list[str], dict[str, str]]] = {
    "Python": PYTHON,
    "Go": GOPHER,
    "Rust": CRAB,
    "Linux": PENGUIN,
    "Docker": WHALE,
    "Kubernetes": HELM,
    "PostgreSQL": ELEPHANT,
    "React": ATOM,
    "CUDA": GPU,
    "DeepStream": VIDEO,
}

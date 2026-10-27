"""Ficha de personaje (sheet.svg): avatar tecleando, datos clave, idiomas, barra EXP y habilidades.

El estado base de cada elemento es su estado final (barras encendidas, EXP llena, ojos abiertos):
con movimiento reducido se ve la ficha completa.
"""

from gen.content import COPY, SKILLS, fmt_int, fmt_pct
from gen.live import LiveStats
from gen.pixel import rects, sprite, two_frames
from gen.scenes.common import BLINK_CSS, header
from gen.sprites.avatar import AVATAR_A, AVATAR_B, AVATAR_BLINK, PALETTE
from gen.sprites.misc import HEART_OFF, HEART_ON, MUG
from gen.svg import document, rect, text, text_width, wrap

W = 840
BG, FRAME, TRACK = "#0d1117", "#30363d", "#21262d"
PAPER, LIGHT, KEY = "#f0f6fc", "#c9d1d9", "#7d8590"
GREEN, DARK_GREEN = "#3fb950", "#2ea043"

PANEL_Y, PAD = 56, 28
TOP = PANEL_Y + 24           # primera línea de contenido dentro del marco
AV_SCALE, AV_X = 6, PAD
MUG_SCALE = 4
RX = 232                    # columna derecha: nombre, filas clave/valor e idiomas
KEY_W = 128                 # ancho de la columna de claves («LANGUAGES» ocupa 99)
VALUE_W = W - PAD - RX - KEY_W
ROW_H, ORIGIN_LINES = 30, 3

# código, corazones llenos (de 3): ES nativo, EN B2, EU B2
SPOKEN = [("ES", 3), ("EN", 2), ("EU", 2)]
HEART_SCALE = 3

EXP_CELL, EXP_CELLS, EXP_H = 10, 78, 16   # 78 celdas de 8 px + separador de 2: todo el ancho
SKILL_COLORS = {
    "PYTHON": "#3572a5", "TYPESCRIPT": "#3178c6", "C / C++": "#f34b7d",
    "GO": "#00add8", "PHP": "#7a86b8", "RUST": "#dea584",
}
SEGMENTS, SEG_W, SEG_GAP, SEG_H = 20, 26, 2, 14
NAME_W, PCT_W, SKILL_H = 140, 84, 28
SEG_STEP = 0.06             # segundos entre segmento y segmento al encenderse
SKILL_TOP = max(p for _, p in SKILLS)   # el lenguaje más usado llena la barra


def segments(pct: float) -> int:
    """Segmentos encendidos (de 1 a 20) para un lenguaje; el más usado de SKILLS llena la barra."""
    return min(SEGMENTS, max(1, round(pct / SKILL_TOP * SEGMENTS)))


def _panel(h: int) -> str:
    # borde doble oscuro: 4 px fuera, hueco de 4 px y línea de 2 px dentro
    y = PANEL_Y
    return (rect(0, y, W, h, FRAME) + rect(4, y + 4, W - 8, h - 8, BG)
            + rect(8, y + 8, W - 16, h - 16, FRAME) + rect(10, y + 10, W - 20, h - 20, BG))


def _avatar(y: float) -> tuple[str, str]:
    """Diego tecleando, con parpadeo, brillo de la pantalla en la cara y la taza humeando."""
    s = AV_SCALE
    av_w, av_h = len(AVATAR_A[0]) * s, len(AVATAR_A) * s
    mug_a, mug_b, mug_pal = MUG
    mug_x = AV_X + av_w + 6
    desk_y = y + av_h
    # el parpadeo solo cambia las filas de los ojos: así las manos no saltan si se ve el fotograma B
    eyes = [i for i, (a, b) in enumerate(zip(AVATAR_A, AVATAR_BLINK)) if a != b]
    blink = rects(AVATAR_BLINK[eyes[0]:eyes[-1] + 1], PALETTE, AV_X, y + eyes[0] * s, s)
    # el brillo de la pantalla cae sobre la piel y el blanco de los ojos de la cabeza (filas 0–12)
    face = ["".join("A" if c in "Ssme" else "." for c in row) for row in AVATAR_A[:13]]
    svg = (
        rect(AV_X - 12, desk_y, mug_x + len(mug_a[0]) * MUG_SCALE + 12 - (AV_X - 12), 6, FRAME)
        + two_frames(AVATAR_A, AVATAR_B, PALETTE, AV_X, y, s)
        + f'<g class="eyes">{blink}</g>'
        + sprite(face, {"A": "#79c0ff"}, AV_X, y, s, "glow")
        + two_frames(mug_a, mug_b, mug_pal, mug_x, desk_y - len(mug_a) * MUG_SCALE, MUG_SCALE)
    )
    css = (".eyes{opacity:0;animation:eyes 4s steps(1) infinite}"
           "@keyframes eyes{0%{opacity:0}95%{opacity:1}}"
           ".glow{opacity:.1;animation:glow 2.2s steps(3) infinite}"
           "@keyframes glow{50%{opacity:.22}}")
    return svg, css


def _wrap_keep_parens(s: str, max_width: float) -> list[str]:
    """Como wrap(), pero sin partir lo que va entre paréntesis («(300 h)» queda en una línea)."""
    out, depth = [], 0
    for ch in s:
        depth += (ch == "(") - (ch == ")")
        out.append("\0" if ch == " " and depth > 0 else ch)
    return [line.replace("\0", " ") for line in wrap("".join(out), "vt323", 26, max_width)]


def _kv(y: float, key: str, value: str) -> str:
    return (text(RX, y, key, "vt323", 26, KEY, max_width=KEY_W)
            + text(RX + KEY_W, y, value, "vt323", 26, LIGHT, max_width=VALUE_W))


def _identity(lang: str) -> tuple[str, float]:
    """Nombre, filas clave/valor e idiomas con corazones; devuelve el svg y la y donde acaba."""
    c = COPY[lang]
    out = [text(RX, TOP + 22, "DIEGO ORUE", "ps2p", 24, PAPER)]
    y = TOP + 60
    for key in ("class", "guild", "base"):
        out.append(_kv(y, c[f"sheet.{key}"], c[f"sheet.{key}_v"]))
        y += ROW_H
    origin = _wrap_keep_parens(c["sheet.origin_v"], VALUE_W)
    if len(origin) > ORIGIN_LINES:
        raise ValueError(f"el origen ocupa {len(origin)} líneas (máximo {ORIGIN_LINES})")
    out.append(text(RX, y, c["sheet.origin"], "vt323", 26, KEY, max_width=KEY_W))
    for line in origin:
        out.append(text(RX + KEY_W, y, line, "vt323", 26, LIGHT, max_width=VALUE_W))
        y += ROW_H - 2
    y += 2
    out.append(text(RX, y, c["sheet.langs"], "vt323", 26, KEY, max_width=KEY_W))
    x = RX + KEY_W
    heart_w = len(HEART_ON[0][0]) * HEART_SCALE
    for code, full in SPOKEN:
        out.append(text(x, y, code, "vt323", 26, LIGHT))
        x += text_width(code, "vt323", 26) + 8
        for i in range(3):
            rows, pal = HEART_ON if i < full else HEART_OFF
            out.append(sprite(rows, pal, round(x), y - 17, HEART_SCALE))
            x += heart_w + 3
        x += 21
    if x - 24 > W - PAD:
        raise ValueError("los idiomas no caben en la fila")
    return "".join(out), y


def _exp(lang: str, live: LiveStats, y: float) -> tuple[str, str, float]:
    """Barra EXP (días activos / días de la ventana) que se llena una vez, y su texto."""
    ratio = live.active_days / live.window_days if live.window_days else 0.0
    fill_w = round(ratio * EXP_CELLS) * EXP_CELL
    x0, inner_w = PAD + 2, EXP_CELLS * EXP_CELL
    svg = (
        "<defs>"
        f'<clipPath id="xpclip"><rect x="{x0}" y="{y + 2}" width="{inner_w}" '
        f'height="{EXP_H}"/></clipPath>'
        f'<pattern id="xpcell" x="{x0}" y="0" width="{EXP_CELL}" height="{EXP_H}" '
        'patternUnits="userSpaceOnUse">'
        f'{rect(0, 0, EXP_CELL - 2, EXP_H, GREEN)}{rect(EXP_CELL - 2, 0, 2, EXP_H, DARK_GREEN)}</pattern>'
        "</defs>"
        + rect(PAD, y, inner_w + 4, EXP_H + 4, FRAME) + rect(x0, y + 2, inner_w, EXP_H, TRACK)
    )
    css = ""
    if fill_w:
        # el relleno entra desde la izquierda dentro del recorte: parece que la barra crece
        svg += (f'<g clip-path="url(#xpclip)"><g class="xp">'
                f'{rect(x0, y + 2, fill_w, EXP_H, "url(#xpcell)")}</g></g>')
        css = (".xp{animation:xp 1.2s steps(12) .2s both}"
               f"@keyframes xp{{from{{transform:translateX(-{fill_w}px)}}}}")
    label = COPY[lang]["sheet.exp"].format(
        total=fmt_int(live.total, lang), active=fmt_int(live.active_days, lang),
        window=fmt_int(live.window_days, lang))
    tag, rest = label.split(" ", 1)          # «EXP» en verde y el resto en claro
    rest_x = PAD + text_width(tag + " ", "vt323", 26)
    y += EXP_H + 32
    svg += (text(PAD, y, tag, "vt323", 26, GREEN)
            + text(rest_x, y, rest, "vt323", 26, LIGHT, max_width=W - PAD - rest_x))
    return svg, css, y


def _skills(lang: str, y: float) -> tuple[str, str, float]:
    """Seis barras de 20 segmentos que se encienden en secuencia una sola vez."""
    out = [text(PAD, y, COPY[lang]["sheet.skills"], "ps2p", 16, KEY, max_width=W - 2 * PAD)]
    bar_x = PAD + NAME_W
    for name, p in SKILLS:
        y += SKILL_H
        out.append(text(PAD, y, name, "vt323", 26, LIGHT, max_width=NAME_W - 8))
        top = y - 15
        for i in range(SEGMENTS):
            out.append(rect(bar_x + i * (SEG_W + SEG_GAP), top, SEG_W, SEG_H, TRACK))
        for i in range(segments(p)):
            out.append(rect(bar_x + i * (SEG_W + SEG_GAP), top, SEG_W, SEG_H, SKILL_COLORS[name],
                            f' class="sg d{i}"'))
        out.append(text(W - PAD, y, fmt_pct(p, lang), "vt323", 26, LIGHT, anchor="end",
                        max_width=PCT_W))
    css = (".sg{animation:sg .06s steps(1) both}@keyframes sg{from{opacity:0}}"
           + "".join(f".d{i}{{animation-delay:{0.4 + i * SEG_STEP:.2f}s}}"
                     for i in range(SEGMENTS)))
    return "".join(out), css, y


def render(lang: str, live: LiveStats) -> dict[str, str]:
    c = COPY[lang]
    identity, y = _identity(lang)
    # el avatar queda centrado en vertical junto al bloque de datos (de TOP a la fila de idiomas)
    avatar, avatar_css = _avatar(round((TOP + y - len(AVATAR_A) * AV_SCALE) / 2))
    exp, exp_css, y = _exp(lang, live, y + 24)
    skills, skills_css, y = _skills(lang, y + 40)
    h = round(y + 10 + PAD)
    body = (header(c["sheet.title"]) + _panel(h - PANEL_Y)
            + avatar + identity + exp + skills)
    title = c["alt.sheet"].format(total=fmt_int(live.total, lang),
                                  active=fmt_int(live.active_days, lang),
                                  window=fmt_int(live.window_days, lang))
    svg = document(W, h, title, body, css=BLINK_CSS + avatar_css + exp_css + skills_css,
                   fonts=("ps2p", "vt323"), bg=BG)
    return {"sheet.svg": svg}

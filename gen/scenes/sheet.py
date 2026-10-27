"""Ficha de personaje (sheet.svg): avatar tecleando, datos clave, idiomas, barra EXP y habilidades.

El estado base de cada elemento es su estado final (barras encendidas, EXP llena, ojos abiertos):
con movimiento reducido se ve la ficha completa.

Dos maquetaciones con el mismo dibujo (`Layout`): en escritorio (sheet.svg, 840 de ancho) el avatar
va a la izquierda y los datos a su derecha, con cada clave y su valor en la misma línea; en el
móvil (m-sheet.svg, 420 de ancho) todo se apila: avatar más grande y centrado arriba, nombre,
cada clave encima de su valor y cada barra de habilidad a todo el ancho, debajo de su nombre.
"""

from dataclasses import dataclass

from gen.content import COPY, SKILLS, fmt_int, fmt_pct
from gen.live import LiveStats
from gen.pixel import rects, sprite, two_frames
from gen.scenes.common import BLINK_CSS, MOBILE_W, header
from gen.sprites.avatar import AVATAR_A, AVATAR_B, AVATAR_BLINK, PALETTE
from gen.sprites.misc import HEART_OFF, HEART_ON, MUG
from gen.svg import balanced_wrap, document, rect, text, text_width, wrap

BG, FRAME, TRACK = "#0d1117", "#30363d", "#21262d"
PAPER, LIGHT, KEY = "#f0f6fc", "#c9d1d9", "#7d8590"
GREEN, DARK_GREEN = "#3fb950", "#2ea043"

PANEL_Y = 56
TOP = PANEL_Y + 24           # primera línea de contenido dentro del marco
LINE_H, ORIGIN_LINES = 28, 3  # de una línea de un valor a la siguiente; máximo de líneas del origen

# código, corazones llenos (de 3): ES nativo, EN B2, EU B2
SPOKEN = [("ES", 3), ("EN", 2), ("EU", 2)]
HEART_SCALE = 3

EXP_CELL, EXP_H = 10, 16    # celdas de 8 px + separador de 2, tantas como quepan a todo el ancho
SKILL_COLORS = {
    "PYTHON": "#3572a5", "TYPESCRIPT": "#3178c6", "C / C++": "#f34b7d",
    "GO": "#00add8", "PHP": "#7a86b8", "RUST": "#dea584",
}
SEGMENTS, SEG_GAP, SEG_H = 20, 2, 14
PCT_W, SKILL_H = 84, 28     # SKILL_H: del título HABILIDADES al nombre del primer lenguaje
SEG_STEP = 0.06             # segundos entre segmento y segmento al encenderse
SKILL_TOP = max(p for _, p in SKILLS)   # el lenguaje más usado llena la barra


@dataclass(frozen=True)
class Layout:
    """Dónde va cada parte de la ficha en un lienzo de `w` de ancho."""
    w: int
    pad: int                 # margen del contenido dentro del marco
    av_scale: int            # tamaño del píxel del avatar
    mug_scale: int
    av_x: int
    av_y: int | None         # None: centrado en vertical junto al bloque de datos
    id_x: int                # columna del nombre, las claves y los idiomas
    id_top: int              # el nombre va 22 por debajo y la primera clave, 60
    name_x: int
    name_anchor: str
    key_size: int            # tamaño de las claves (CLASE, GREMIO…)
    key_w: int               # el valor va `key_w` a la derecha de su clave (0: debajo, con todo
    value_dy: int            # el ancho) y `value_dy` más abajo (0: en la misma línea)
    row_gap: int             # de la última línea de un valor a la clave siguiente, sobre LINE_H
    skill_name_w: int        # columna del nombre del lenguaje (PYTHON, TYPESCRIPT…)
    bar_dx: int              # la barra de habilidad empieza `bar_dx` a la derecha del margen…
    bar_dy: int              # …y su borde de arriba queda `bar_dy` bajo la línea base del nombre
    skill_h: int             # de una barra de habilidad a la siguiente
    seg_w: int               # ancho de cada uno de los 20 segmentos
    foot: int                # de la última línea base al borde inferior del lienzo


# avatar a la izquierda; a su derecha, en la columna 232, nombre y claves (columna de 128:
# «LANGUAGES» ocupa 99) con el valor en la misma línea; barras de 20 × 26 tras el nombre
DESKTOP = Layout(w=840, pad=28, av_scale=6, mug_scale=4, av_x=28, av_y=None, id_x=232,
                 id_top=TOP, name_x=232, name_anchor="start", key_size=26, key_w=128,
                 value_dy=0, row_gap=2, skill_name_w=140, bar_dx=140, bar_dy=-15, skill_h=28,
                 seg_w=26, foot=38)
# avatar a escala 8 (≈ 5,3 px CSS por píxel en el móvil: se ven el reloj y la pulsera) centrado
# con la taza; debajo, todo apilado a todo el ancho (420 - 2 × 18 = 384)
_M_AV, _M_MUG = 8, 5
_M_GROUP = len(AVATAR_A[0]) * _M_AV + 6 + len(MUG[0][0]) * _M_MUG   # avatar, hueco y taza
MOBILE = Layout(w=MOBILE_W, pad=18, av_scale=_M_AV, mug_scale=_M_MUG,
                av_x=(MOBILE_W - _M_GROUP) // 2, av_y=TOP, id_x=18,
                id_top=TOP + len(AVATAR_A) * _M_AV + 24, name_x=MOBILE_W // 2,
                name_anchor="middle", key_size=22, key_w=0, value_dy=26, row_gap=8,
                skill_name_w=MOBILE_W - 2 * 18 - PCT_W, bar_dx=0, bar_dy=8, skill_h=46, seg_w=17,
                foot=50)


def segments(pct: float) -> int:
    """Segmentos encendidos (de 1 a 20) para un lenguaje; el más usado de SKILLS llena la barra."""
    return min(SEGMENTS, max(1, round(pct / SKILL_TOP * SEGMENTS)))


def _panel(h: int, w: int) -> str:
    # borde doble oscuro: 4 px fuera, hueco de 4 px y línea de 2 px dentro
    y = PANEL_Y
    return (rect(0, y, w, h, FRAME) + rect(4, y + 4, w - 8, h - 8, BG)
            + rect(8, y + 8, w - 16, h - 16, FRAME) + rect(10, y + 10, w - 20, h - 20, BG))


def _avatar(y: float, lay: Layout) -> tuple[str, str]:
    """Diego tecleando, con parpadeo, brillo de la pantalla en la cara y la taza humeando."""
    s, x, mug_s = lay.av_scale, lay.av_x, lay.mug_scale
    av_w, av_h = len(AVATAR_A[0]) * s, len(AVATAR_A) * s
    mug_a, mug_b, mug_pal = MUG
    mug_x = x + av_w + 6
    desk_y = y + av_h
    # el parpadeo solo cambia las filas de los ojos: así las manos no saltan si se ve el fotograma B
    eyes = [i for i, (a, b) in enumerate(zip(AVATAR_A, AVATAR_BLINK)) if a != b]
    blink = rects(AVATAR_BLINK[eyes[0]:eyes[-1] + 1], PALETTE, x, y + eyes[0] * s, s)
    # el brillo de la pantalla cae sobre la piel y el blanco de los ojos de la cabeza (filas 0–12)
    face = ["".join("A" if c in "Ssme" else "." for c in row) for row in AVATAR_A[:13]]
    svg = (
        rect(x - 12, desk_y, mug_x + len(mug_a[0]) * mug_s + 12 - (x - 12), 6, FRAME)
        + two_frames(AVATAR_A, AVATAR_B, PALETTE, x, y, s)
        + f'<g class="eyes">{blink}</g>'
        + sprite(face, {"A": "#79c0ff"}, x, y, s, "glow")
        + two_frames(mug_a, mug_b, mug_pal, mug_x, desk_y - len(mug_a) * mug_s, mug_s)
    )
    css = (".eyes{opacity:0;animation:eyes 4s steps(1) infinite}"
           "@keyframes eyes{0%{opacity:0}95%{opacity:1}}"
           ".glow{opacity:.1;animation:glow 2.2s steps(3) infinite}"
           "@keyframes glow{50%{opacity:.22}}")
    return svg, css


def _wrap_keep(s: str, max_width: float, wrapper=wrap) -> list[str]:
    """Como wrap() (o `wrapper`), pero sin partir lo que va entre paréntesis («(300 h)» queda en
    una línea) y sin empezar una línea con «·»: el separador se queda al final de la anterior."""
    out, depth = [], 0
    for ch in s.replace(" · ", "\0· "):
        depth += (ch == "(") - (ch == ")")
        out.append("\0" if ch == " " and depth > 0 else ch)
    return [line.replace("\0", " ") for line in wrapper("".join(out), "vt323", 26, max_width)]


def _key(lay: Layout, y: float, key: str) -> str:
    # con el valor debajo (key_w = 0), la clave tiene todo el ancho
    room = lay.key_w or lay.w - lay.pad - lay.id_x
    return text(lay.id_x, y, key, "vt323", lay.key_size, KEY, max_width=room)


def _identity(lang: str, lay: Layout) -> tuple[str, float]:
    """Nombre, filas clave/valor e idiomas con corazones; devuelve el svg y la línea base de los
    corazones, que es donde acaba."""
    c = COPY[lang]
    value_x, value_w = lay.id_x + lay.key_w, lay.w - lay.pad - lay.id_x - lay.key_w
    out = [text(lay.name_x, lay.id_top + 22, "DIEGO ORUE", "ps2p", 24, PAPER,
                anchor=lay.name_anchor, max_width=lay.w - 2 * lay.pad)]
    y = lay.id_top + 60
    for key in ("class", "guild", "base", "origin"):
        lines = _wrap_keep(c[f"sheet.{key}_v"], value_w)
        if key == "origin" and len(lines) > ORIGIN_LINES:
            raise ValueError(f"el origen ocupa {len(lines)} líneas (máximo {ORIGIN_LINES})")
        out.append(_key(lay, y, c[f"sheet.{key}"]))
        out += [text(value_x, y + lay.value_dy + i * LINE_H, line, "vt323", 26, LIGHT,
                     max_width=value_w) for i, line in enumerate(lines)]
        y += lay.value_dy + len(lines) * LINE_H + lay.row_gap
    out.append(_key(lay, y, c["sheet.langs"]))
    x, y = value_x, y + lay.value_dy
    heart_w = len(HEART_ON[0][0]) * HEART_SCALE
    for code, full in SPOKEN:
        out.append(text(x, y, code, "vt323", 26, LIGHT))
        x += text_width(code, "vt323", 26) + 8
        for i in range(3):
            rows, pal = HEART_ON if i < full else HEART_OFF
            out.append(sprite(rows, pal, round(x), y - 17, HEART_SCALE))
            x += heart_w + 3
        x += 21
    if x - 24 > lay.w - lay.pad:
        raise ValueError("los idiomas no caben en la fila")
    return "".join(out), y


def _exp(lang: str, live: LiveStats, y: float, lay: Layout) -> tuple[str, str, float]:
    """Barra EXP (días activos / días de la ventana) que se llena una vez, y su texto; devuelve
    también la línea base de la última línea del texto."""
    pad = lay.pad
    cells = (lay.w - 2 * pad - 4) // EXP_CELL       # 78 en escritorio, 38 en el móvil
    ratio = live.active_days / live.window_days if live.window_days else 0.0
    fill_w = round(ratio * cells) * EXP_CELL
    x0, inner_w = pad + 2, cells * EXP_CELL
    svg = (
        "<defs>"
        f'<clipPath id="xpclip"><rect x="{x0}" y="{y + 2}" width="{inner_w}" '
        f'height="{EXP_H}"/></clipPath>'
        f'<pattern id="xpcell" x="{x0}" y="0" width="{EXP_CELL}" height="{EXP_H}" '
        'patternUnits="userSpaceOnUse">'
        f'{rect(0, 0, EXP_CELL - 2, EXP_H, GREEN)}{rect(EXP_CELL - 2, 0, 2, EXP_H, DARK_GREEN)}</pattern>'
        "</defs>"
        + rect(pad, y, inner_w + 4, EXP_H + 4, FRAME) + rect(x0, y + 2, inner_w, EXP_H, TRACK)
    )
    css = ""
    if fill_w:
        # el relleno entra desde la izquierda dentro del recorte: parece que la barra crece
        svg += (f'<g clip-path="url(#xpclip)"><g class="xp">'
                f'{rect(x0, y + 2, fill_w, EXP_H, "url(#xpcell)")}</g></g>')
        css = (".xp{animation:xp 1.2s steps(12) .2s both}"
               f"@keyframes xp{{from{{transform:translateX(-{fill_w}px)}}}}")
    label = COPY[lang]["sheet.exp"].format(
        total=fmt_int(live.total, lang), active=fmt_int(live.active_days, lang))
    tag, rest = label.split(" ", 1)          # «EXP» en verde y el resto en claro
    rest_x = pad + text_width(tag + " ", "vt323", 26)
    room = lay.w - pad - rest_x
    y += EXP_H + 32
    svg += text(pad, y, tag, "vt323", 26, GREEN)
    # si no cabe en una línea (en el móvil), el resto se parte en líneas parejas bajo el texto
    lines = _wrap_keep(rest, room, balanced_wrap)
    svg += "".join(text(rest_x, y + i * LINE_H, line, "vt323", 26, LIGHT, max_width=room)
                   for i, line in enumerate(lines))
    return svg, css, y + (len(lines) - 1) * LINE_H


def _skills(lang: str, y: float, lay: Layout) -> tuple[str, str, float]:
    """Seis barras de 20 segmentos que se encienden en secuencia una sola vez."""
    pad, step = lay.pad, lay.seg_w + SEG_GAP
    out = [text(pad, y, COPY[lang]["sheet.skills"], "ps2p", 16, KEY,
                max_width=lay.w - 2 * pad)]
    bar_x = pad + lay.bar_dx
    for k, (name, p) in enumerate(SKILLS):
        row = y + SKILL_H + k * lay.skill_h          # línea base del nombre del lenguaje
        out.append(text(pad, row, name, "vt323", 26, LIGHT, max_width=lay.skill_name_w - 8))
        top = row + lay.bar_dy
        for i in range(SEGMENTS):
            out.append(rect(bar_x + i * step, top, lay.seg_w, SEG_H, TRACK))
        for i in range(segments(p)):
            out.append(rect(bar_x + i * step, top, lay.seg_w, SEG_H, SKILL_COLORS[name],
                            f' class="sg d{i}"'))
        out.append(text(lay.w - pad, row, fmt_pct(p, lang), "vt323", 26, LIGHT, anchor="end",
                        max_width=PCT_W))
    css = (".sg{animation:sg .06s steps(1) both}@keyframes sg{from{opacity:0}}"
           + "".join(f".d{i}{{animation-delay:{0.4 + i * SEG_STEP:.2f}s}}"
                     for i in range(SEGMENTS)))
    return "".join(out), css, row


def _sheet(lang: str, live: LiveStats, lay: Layout) -> str:
    c = COPY[lang]
    identity, y = _identity(lang, lay)
    # en escritorio el avatar queda centrado en vertical junto al bloque de datos (de TOP a la
    # fila de idiomas); en el móvil va arriba, encima del nombre
    av_y = lay.av_y if lay.av_y is not None else round((TOP + y - len(AVATAR_A) * lay.av_scale) / 2)
    avatar, avatar_css = _avatar(av_y, lay)
    exp, exp_css, y = _exp(lang, live, y + 24, lay)
    skills, skills_css, y = _skills(lang, y + 40, lay)
    h = round(y + lay.foot)
    body = (header(c["sheet.title"], lay.w) + _panel(h - PANEL_Y, lay.w)
            + avatar + identity + exp + skills)
    title = c["alt.sheet"].format(total=fmt_int(live.total, lang),
                                  active=fmt_int(live.active_days, lang))
    return document(lay.w, h, title, body, css=BLINK_CSS + avatar_css + exp_css + skills_css,
                    fonts=("ps2p", "vt323"), bg=BG)


def render(lang: str, live: LiveStats) -> dict[str, str]:
    return {"sheet.svg": _sheet(lang, live, DESKTOP), "m-sheet.svg": _sheet(lang, live, MOBILE)}

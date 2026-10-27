"""Misiones: tarjetas como cuadros de diálogo RPG, título y enlace «más».

Cada tarjeta tiene dos versiones con las mismas piezas (marco, icono, estrella, etiqueta de estado
y ▼): en escritorio (quest-*.svg, 416 × 196) el título va junto al icono y cada texto en su sitio
fijo; en el móvil (m-quest-*.svg, 200 de ancho) todo se apila. En el README las tarjetas van al
49 %, así que en el móvil se ven a ≈ 135 px (escala ≈ 0,675): 168 de ancho útil.
"""

from gen.content import COPY, PROJECT_TOTAL, QUESTS, Quest, quest_stack
from gen.live import LiveStats
from gen.pixel import sprite
from gen.scenes.common import BLINK_CSS, HEADER_H, HEADER_W, MOBILE_W, header
from gen.sprites.misc import ARROW, DOT, DOWN, ICONS, STAR
from gen.svg import balanced_wrap, document, rect, text, text_width, wrap, wrap_keep

W, H = 416, 196
PAD = 24
SUMMARY_W = 352  # ancho del resumen; con avance 0.42 em caben 38 caracteres y sobran 30 px hasta el marco
BG, LINE, INK = "#0d1117", "#f0f6fc", "#c9d1d9"
GREY, GREEN, YELLOW, BLUE = "#8b949e", "#3fb950", "#e3b341", "#58a6ff"
CHIP, DOT_W = "#21262d", len(DOT[0][0]) * 3

# Tarjeta móvil
M_W, M_PAD = 200, 16
M_ROOM = M_W - 2 * M_PAD                  # 168
ICON_BOX = 12 * 3                         # los iconos miden 12 de ancho y hasta 12 de alto, a escala 3
M_TITLE = M_PAD + ICON_BOX + 26           # línea base del título, bajo el icono
M_LINE = 26
M_CHIP_PAD, M_CHIP_GAP = 8, 6              # etiqueta algo más ceñida: «In development» cabe en una línea
DOWN_W, DOWN_H = len(DOWN[0][0]) * 3, len(DOWN[0]) * 3


def _frame(w: int = W, h: int = H) -> str:
    # borde doble claro: 4 px fuera, hueco oscuro de 4 px y línea de 2 px dentro
    return (rect(0, 0, w, h, LINE) + rect(4, 4, w - 8, h - 8, BG)
            + rect(8, 8, w - 16, h - 16, LINE) + rect(10, 10, w - 20, h - 20, BG))


def _dot(q: Quest) -> str:
    return YELLOW if q.in_progress else GREEN


def _chip(x, top, lines: list[str], dot: str, pad: int = 10, gap: int = 8) -> tuple[str, int]:
    """Etiqueta de estado: fondo gris, punto de color y el texto en una o más líneas; y su alto.

    `pad` es el margen a cada lado y `gap`, el hueco entre el punto y el texto.
    """
    text_x = pad + DOT_W + gap
    tw = max(text_width(line, "vt323", 22) for line in lines)
    w = text_x + tw + pad
    h = 28 + M_LINE * (len(lines) - 1)
    return (rect(x, top, w, h, CHIP) + sprite(DOT[0], {"A": dot}, x + pad, top + 7, 3)
            + "".join(text(x + text_x, top + 21 + i * M_LINE, line, "vt323", 22, INK, max_width=tw)
                      for i, line in enumerate(lines))), h


def _down(x, y) -> str:
    return sprite(DOWN[0], {"A": "#e6edf3"}, x, y, 3, "blink")


def _card(q: Quest, lang: str) -> str:
    rows, pal = ICONS[q.icon]
    title = q.title[lang]
    body = _frame() + sprite(rows, pal, PAD, 24, 3)
    tx = PAD + 12 * 3 + 12
    body += text(tx, 48, title, "ps2p", 16, BLUE, max_width=W - tx - PAD - 26)
    if q.starred:
        body += sprite(STAR[0], STAR[1], tx + text_width(title, "ps2p", 16) + 8, 32, 2)
    inner = SUMMARY_W
    for i, line in enumerate(wrap(q.summary[lang], "vt323", 22, inner)):
        body += text(PAD, 88 + i * 26, line, "vt323", 22, INK, max_width=inner)
    body += text(PAD, 142, quest_stack(q, lang), "vt323", 22, GREY, max_width=W - 2 * PAD)
    body += _chip(PAD, 152, [q.status[lang]], _dot(q))[0]
    body += _down(W - PAD - DOWN_W, 160)
    return document(W, H, f"{title}: {q.summary[lang]}", body, css=BLINK_CSS,
                    fonts=("ps2p", "vt323"), bg=BG)


def _m_title_font(title: str) -> tuple[str, int]:
    """ps2p 16 como en escritorio; si no cabe en M_ROOM, vt323 a 28 o a 26 (más estrecha)."""
    if text_width(title, "ps2p", 16) <= M_ROOM:
        return "ps2p", 16
    for size in (28, 26):
        if text_width(title, "vt323", size) <= M_ROOM:
            return "vt323", size
    raise ValueError(f"el título {title!r} no cabe en la tarjeta móvil")


def _m_lines(q: Quest, lang: str) -> tuple[list[str], list[str], list[str]]:
    """Resumen, stack y estado de la tarjeta móvil, partidos en líneas de M_ROOM como mucho.

    La stack no empieza ninguna línea con «·»; la stack y el estado van en líneas parejas.
    """
    return (balanced_wrap(q.summary[lang], "vt323", 22, M_ROOM),
            wrap_keep(quest_stack(q, lang), "vt323", 22, M_ROOM, balanced_wrap),
            balanced_wrap(q.status[lang], "vt323", 22,
                          M_ROOM - 2 * M_CHIP_PAD - DOT_W - M_CHIP_GAP))


def _m_foot(stack: list[str], status: list[str]) -> int:
    """Alto del pie (stack, etiqueta y ▼), de la línea base de la primera línea de la stack al
    borde inferior del lienzo."""
    return (M_LINE * (len(stack) - 1) + 10 + 28 + M_LINE * (len(status) - 1)
            + 8 + DOWN_H + M_PAD)


def _m_height(lang: str) -> int:
    """Alto común de las tarjetas móviles de un idioma: el de la que más ocupa. En el móvil van de
    dos en dos, y con el mismo alto las filas cuadran."""
    return max(M_TITLE + 32 + M_LINE * (len(summary) - 1) + 30 + _m_foot(stack, status)
               for summary, stack, status in (_m_lines(q, lang) for q in QUESTS))


def _m_card(q: Quest, lang: str, h: int) -> str:
    """Tarjeta móvil: icono (y estrella) arriba, título debajo y el resumen; la stack, la etiqueta
    y el ▼ van abajo del todo, así quedan a la misma altura en todas las tarjetas."""
    summary, stack, status = _m_lines(q, lang)
    rows, pal = ICONS[q.icon]
    title = q.title[lang]
    body = _frame(M_W, h) + sprite(rows, pal, M_PAD, M_PAD + (ICON_BOX - len(rows) * 3) // 2, 3)
    if q.starred:
        star = len(STAR[0]) * 2
        body += sprite(STAR[0], STAR[1], M_PAD + ICON_BOX + 10, M_PAD + (ICON_BOX - star) // 2, 2)
    font, size = _m_title_font(title)
    body += text(M_PAD, M_TITLE, title, font, size, BLUE, max_width=M_ROOM)
    body += "".join(text(M_PAD, M_TITLE + 32 + i * M_LINE, line, "vt323", 22, INK, max_width=M_ROOM)
                    for i, line in enumerate(summary))
    y = h - _m_foot(stack, status)
    body += "".join(text(M_PAD, y + i * M_LINE, line, "vt323", 22, GREY, max_width=M_ROOM)
                    for i, line in enumerate(stack))
    top = y + M_LINE * (len(stack) - 1) + 10
    chip, chip_h = _chip(M_PAD, top, status, _dot(q), M_CHIP_PAD, M_CHIP_GAP)
    body += chip + _down(M_W - M_PAD - DOWN_W, top + chip_h + 8)
    fonts = ("ps2p", "vt323") if font == "ps2p" else ("vt323",)
    return document(M_W, h, f"{title}: {q.summary[lang]}", body, css=BLINK_CSS, fonts=fonts, bg=BG)


def _title(lang: str, width: int = HEADER_W) -> str:
    label = COPY[lang]["quests.title"]
    return document(width, HEADER_H, label, header(label, width), css=BLINK_CSS,
                    fonts=("ps2p",))


def _more(lang: str, width: int = 840) -> str:
    """«▶ +N misiones más…» centrado; si no cabe en `width`, en líneas equilibradas bajo la flecha."""
    label = COPY[lang]["quests.more"].format(n=PROJECT_TOTAL - len(QUESTS))
    room = width - 2 * 20 - 24                       # 20 de margen a cada lado y la flecha
    lines = balanced_wrap(label, "vt323", 22, room)
    w = 24 + max(text_width(line, "vt323", 22) for line in lines)
    x0 = (width - w) / 2
    body = sprite(ARROW[0], ARROW[1], x0, 16, 3) + "".join(
        text(x0 + 24, 36 + i * 26, line, "vt323", 22, "#58a6ff", max_width=room)
        for i, line in enumerate(lines))
    return document(width, 56 + (len(lines) - 1) * 26, label, body, fonts=("vt323",))


def render(lang: str, live: LiveStats) -> dict[str, str]:
    out = {f"quest-{q.slug}.svg": _card(q, lang) for q in QUESTS}
    h = _m_height(lang)
    out.update({f"m-quest-{q.slug}.svg": _m_card(q, lang, h) for q in QUESTS})
    out["quests-title.svg"] = _title(lang)
    out["quests-more.svg"] = _more(lang)
    out["m-quests-title.svg"] = _title(lang, MOBILE_W)
    out["m-quests-more.svg"] = _more(lang, MOBILE_W)
    return out

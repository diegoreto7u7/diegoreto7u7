"""Misiones: tarjetas como cuadros de diálogo RPG, título y enlace «más»."""

from gen.content import COPY, PROJECT_TOTAL, QUESTS, Quest, quest_stack
from gen.live import LiveStats
from gen.pixel import sprite
from gen.scenes.common import BLINK_CSS, HEADER_H, HEADER_W, MOBILE_W, header
from gen.sprites.misc import ARROW, DOT, DOWN, ICONS, STAR
from gen.svg import balanced_wrap, document, rect, text, text_width, wrap

W, H = 416, 196
PAD = 24
SUMMARY_W = 352  # ancho del resumen; con avance 0.42 em caben 38 caracteres y sobran 30 px hasta el marco
BG, LINE, INK = "#0d1117", "#f0f6fc", "#c9d1d9"
GREY, GREEN, YELLOW = "#8b949e", "#3fb950", "#e3b341"


def _frame() -> str:
    # borde doble claro: 4 px fuera, hueco oscuro de 4 px y línea de 2 px dentro
    return (rect(0, 0, W, H, LINE) + rect(4, 4, W - 8, H - 8, BG)
            + rect(8, 8, W - 16, H - 16, LINE) + rect(10, 10, W - 20, H - 20, BG))


def _card(q: Quest, lang: str) -> str:
    rows, pal = ICONS[q.icon]
    title = q.title[lang]
    body = _frame() + sprite(rows, pal, PAD, 24, 3)
    tx = PAD + 12 * 3 + 12
    body += text(tx, 48, title, "ps2p", 16, "#58a6ff", max_width=W - tx - PAD - 26)
    if q.starred:
        body += sprite(STAR[0], STAR[1], tx + text_width(title, "ps2p", 16) + 8, 32, 2)
    inner = SUMMARY_W
    for i, line in enumerate(wrap(q.summary[lang], "vt323", 22, inner)):
        body += text(PAD, 88 + i * 26, line, "vt323", 22, INK, max_width=inner)
    body += text(PAD, 142, quest_stack(q, lang), "vt323", 22, GREY, max_width=W - 2 * PAD)
    status = q.status[lang]
    dot = YELLOW if q.in_progress else GREEN
    chip_w = 10 + 15 + 8 + text_width(status, "vt323", 22) + 10
    body += rect(PAD, 152, chip_w, 28, "#21262d")
    body += sprite(DOT[0], {"A": dot}, PAD + 10, 159, 3)
    body += text(PAD + 33, 173, status, "vt323", 22, INK, max_width=chip_w - 33 - 10)
    body += sprite(DOWN[0], {"A": "#e6edf3"}, W - PAD - 21, 160, 3, "blink")
    return document(W, H, f"{title}: {q.summary[lang]}", body, css=BLINK_CSS,
                    fonts=("ps2p", "vt323"), bg=BG)


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
    out["quests-title.svg"] = _title(lang)
    out["quests-more.svg"] = _more(lang)
    out["m-quests-title.svg"] = _title(lang, MOBILE_W)
    out["m-quests-more.svg"] = _more(lang, MOBILE_W)
    return out

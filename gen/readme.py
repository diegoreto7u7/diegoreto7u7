"""Markdown de los dos README."""

from html import escape
from pathlib import Path

from .content import COPY, PROJECT_TOTAL, QUESTS, URLS, fmt_int
from .live import LiveStats, load_live
from .scenes.achievements import streak_text

DEFAULT_LIVE = Path(__file__).resolve().parent.parent / "data" / "live.json"


def _a(s: str) -> str:
    return escape(s, quote=True)


def _quest_alt(q, lang: str) -> str:
    return f"{q.title[lang]} — {q.summary[lang]} ({q.status[lang]})"


def render_readme(lang: str, live: LiveStats | None = None) -> str:
    """Markdown del README; los llamadores de producción pasan `live`."""
    if live is None:
        live = load_live(DEFAULT_LIVE, refresh=False, token=None)
    c, u = COPY[lang], URLS[lang]
    n = lambda v: fmt_int(v, lang)  # noqa: E731
    alt = {
        "lang": c["alt.lang"],
        "hero": c["alt.hero"],
        "sheet": c["alt.sheet"].format(
            total=n(live.total), active=n(live.active_days), window=n(live.window_days)),
        "achievements": c["alt.achievements"].format(
            best=n(live.best_day), streak=streak_text(lang, live)),
        "inventory": c["alt.inventory"],
        "highscore": c["alt.highscore"].format(total=n(live.total), best=n(live.best_day)),
        "bilbao": c["alt.bilbao"],
        "more": c["quests.more"].format(n=PROJECT_TOTAL - len(QUESTS)),
    }
    img = f"assets/{lang}"
    quests = "\n".join(
        f'  <a href="{u["quest." + q.slug]}"><img src="{img}/quest-{q.slug}.svg" '
        f'width="49%" alt="{_a(_quest_alt(q, lang))}"></a>'
        for q in QUESTS
    )
    return f"""<!-- Generado con `python3 -m gen build`. No editar a mano. -->
<p align="right"><a href="{u["lang"]}"><img src="{img}/btn-lang.svg" height="40" alt="{_a(alt["lang"])}"></a></p>

{c["intro"]}

<p align="center"><img src="{img}/hero.svg" width="100%" alt="{_a(alt["hero"])}"></p>
<p align="center">
  <a href="{u["portfolio"]}"><img src="{img}/btn-portfolio.svg" height="48" alt="Portfolio"></a>
  <a href="{u["linkedin"]}"><img src="{img}/btn-linkedin.svg" height="48" alt="LinkedIn"></a>
  <a href="{u["email"]}"><img src="{img}/btn-email.svg" height="48" alt="{_a(c["btn.email"])}"></a>
  <a href="{u["cv"]}"><img src="{img}/btn-cv.svg" height="48" alt="CV"></a>
</p>
<p align="center"><img src="{img}/sheet.svg" width="100%" alt="{_a(alt["sheet"])}"></p>
<p align="center"><img src="{img}/achievements.svg" width="100%" alt="{_a(alt["achievements"])}"></p>
<p align="center"><img src="{img}/inventory.svg" width="100%" alt="{_a(alt["inventory"])}"></p>
<p align="center"><img src="{img}/quests-title.svg" width="100%" alt="{_a(c["quests.title"])}"></p>
<p align="center">
{quests}
</p>
<p align="center"><a href="{u["portfolio"]}"><img src="{img}/quests-more.svg" width="100%" alt="{_a(alt["more"])}"></a></p>
<p align="center"><img src="{img}/highscore.svg" width="100%" alt="{_a(alt["highscore"])}"></p>
<p align="center"><img src="{img}/bilbao.svg" width="100%" alt="{_a(alt["bilbao"])}"></p>
<p align="center"><a href="{u["email"]}"><img src="{img}/start.svg" width="100%" alt="{_a(c["footer.start"])}: orueret@gmail.com"></a></p>
"""

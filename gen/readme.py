"""Markdown de los dos README."""

from html import escape
from pathlib import Path

from .content import COPY, PROJECT_TOTAL, QUESTS, URLS, fmt_int
from .live import LiveStats, load_live
from .scenes import achievements

DEFAULT_LIVE = Path(__file__).resolve().parent.parent / "data" / "live.json"
# Las imágenes con variante móvil (m-<nombre>.svg) van en un <picture>: con la pantalla a 600 px o
# menos, el <source> elige la variante. El srcset es absoluto porque GitHub reescribe el src
# relativo de un <img>, pero no hay garantía de que haga lo mismo con el de un <source>.
MOBILE_MEDIA = "(max-width: 600px)"
RAW_BASE = "https://github.com/diegoreto7u7/diegoreto7u7/raw/main/"


def _a(s: str) -> str:
    return escape(s, quote=True)


def _pic(lang: str, name: str, width: str, alt: str) -> str:
    """El <img> de `assets/<lang>/<name>` dentro de un <picture> con su variante móvil."""
    return (f'<picture><source media="{MOBILE_MEDIA}" srcset="{RAW_BASE}assets/{lang}/m-{name}">'
            f'<img src="assets/{lang}/{name}" width="{width}" alt="{_a(alt)}"></picture>')


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
        "sheet": c["alt.sheet"].format(total=n(live.total), active=n(live.active_days)),
        "achievements": achievements.alt_text(lang, live),
        "inventory": c["alt.inventory"],
        "highscore": c["alt.highscore"].format(total=n(live.total), best=n(live.best_day)),
        "bilbao": c["alt.bilbao"],
        "more": c["quests.more"].format(n=PROJECT_TOTAL - len(QUESTS)),
    }
    img = f"assets/{lang}"
    pic = lambda name, alt, width="100%": _pic(lang, name, width, alt)  # noqa: E731
    quests = "\n".join(
        f'  <a href="{u["quest." + q.slug]}">'
        f'{pic(f"quest-{q.slug}.svg", _quest_alt(q, lang), "49%")}</a>'
        for q in QUESTS
    )
    return f"""<!-- Generado con `python3 -m gen build`. No editar a mano. -->
<p align="right"><a href="{u["lang"]}"><img src="{img}/btn-lang.svg" height="40" alt="{_a(alt["lang"])}"></a></p>

{c["intro"]}

<p align="center">{pic("hero.svg", alt["hero"])}</p>
<p align="center">
  <a href="{u["portfolio"]}"><img src="{img}/btn-portfolio.svg" height="48" alt="Portfolio"></a>
  <a href="{u["linkedin"]}"><img src="{img}/btn-linkedin.svg" height="48" alt="LinkedIn"></a>
  <a href="{u["email"]}"><img src="{img}/btn-email.svg" height="48" alt="{_a(c["btn.email"])}"></a>
  <a href="{u["cv"]}"><img src="{img}/btn-cv.svg" height="48" alt="CV"></a>
</p>
<p align="center">{pic("sheet.svg", alt["sheet"])}</p>
<p align="center">{pic("achievements.svg", alt["achievements"])}</p>
<p align="center">{pic("inventory.svg", alt["inventory"])}</p>
<p align="center">{pic("quests-title.svg", c["quests.title"])}</p>
<p align="center">
{quests}
</p>
<p align="center"><a href="{u["portfolio"]}">{pic("quests-more.svg", alt["more"])}</a></p>
<p align="center">{pic("highscore.svg", alt["highscore"])}</p>
<p align="center"><img src="{img}/bilbao.svg" width="100%" alt="{_a(alt["bilbao"])}"></p>
<p align="center"><a href="{u["email"]}">{pic("start.svg", f"{c["footer.start"]}: orueret@gmail.com")}</a></p>
"""

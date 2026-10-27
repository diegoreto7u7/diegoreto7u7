"""Orquesta las escenas y escribe README y assets."""

from pathlib import Path

from .content import LANGS
from .live import LiveStats, load_live
from .readme import render_readme
from .scenes import achievements, buttons, footer, hero, highscore, inventory, quests, sheet
from .svgcheck import check_svg

SCENES = (hero, buttons, quests, sheet, achievements, inventory, highscore, footer)
README = {"es": "README.md", "en": "README.en.md"}


def render_all(lang: str, live: LiveStats) -> dict[str, str]:
    files: dict[str, str] = {}
    for scene in SCENES:
        files.update(scene.render(lang, live))
    return files


def build(out: Path, refresh: bool, token: str | None) -> list[Path]:
    out = Path(out)
    live = load_live(out / "data" / "live.json", refresh=refresh, token=token)
    rendered = {lang: render_all(lang, live) for lang in LANGS}
    problems = [f"{lang}/{name}: {p}"
                for lang, files in rendered.items()
                for name, svg in sorted(files.items())
                for p in check_svg(svg)]
    if problems:
        raise SystemExit("SVG con problemas:\n" + "\n".join(problems))
    written: list[Path] = []
    for lang in LANGS:
        folder = out / "assets" / lang
        folder.mkdir(parents=True, exist_ok=True)
        for name, svg in sorted(rendered[lang].items()):
            path = folder / name
            path.write_text(svg, encoding="utf-8", newline="\n")
            written.append(path)
        readme = out / README[lang]
        readme.write_text(render_readme(lang, live), encoding="utf-8", newline="\n")
        written.append(readme)
    return written

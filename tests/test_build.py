import re
import shutil
import tempfile
import unittest
import xml.etree.ElementTree as ET
from html import escape
from html.parser import HTMLParser
from unittest import mock
from pathlib import Path

from gen.build import build, render_all
from gen.content import LANGS, fmt_int
from gen.scenes.achievements import streak_text
from gen.live import load_live
from gen.readme import render_readme


def _copy_data(out: Path) -> None:
    shutil.copytree("data", out / "data")


class _Imgs(HTMLParser):
    def __init__(self):
        super().__init__()
        self.imgs = []

    def handle_starttag(self, tag, attrs):
        if tag == "img":
            self.imgs.append(attrs)


class BuildTests(unittest.TestCase):
    def test_build_writes_everything(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d)
            _copy_data(out)
            paths = build(out, refresh=False, token=None)
            self.assertTrue(paths)
            for lang in LANGS:
                self.assertTrue((out / "assets" / lang / "hero.svg").exists())
                names = {p.name for p in (out / "assets" / lang).glob("*.svg")}
                desktop = {n for n in names if not n.startswith("m-")}
                self.assertEqual(len(desktop), 18)
                self.assertTrue(names - desktop)                  # hay variantes móviles
                for n in names - desktop:
                    self.assertIn(n[2:], desktop)                 # m-<nombre de escritorio>
                total = sum(p.stat().st_size for p in (out / "assets" / lang).glob("*.svg"))
                self.assertLess(total, 3_000_000)
            self.assertTrue((out / "README.md").exists() and (out / "README.en.md").exists())

    def test_build_is_reproducible(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            snaps = []
            for d in (a, b):
                out = Path(d)
                _copy_data(out)
                build(out, refresh=False, token=None)
                snaps.append({p.relative_to(out): p.read_bytes()
                              for p in out.rglob("*") if p.is_file() and "data" not in p.parts})
            self.assertEqual(snaps[0], snaps[1])
            self.assertGreater(len(snaps[0]), 36)

    def test_readme_links(self):
        es, en = render_readme("es"), render_readme("en")
        self.assertIn("blob/main/README.en.md", es)
        self.assertIn('href="https://github.com/diegoreto7u7"', en)
        self.assertIn("https://diegoret.pages.dev/proyectos/conteobk/", es)
        self.assertIn("https://diegoret.pages.dev/en/projects/conteobk/", en)
        for md in (es, en):
            for src in re.findall(r'src="([^"]+)"', md):
                self.assertTrue(src.startswith("assets/"))

    def test_every_referenced_asset_is_rendered(self):
        live = load_live(Path("data/live.json"), refresh=False, token=None)
        for lang in LANGS:
            md = render_readme(lang)
            rendered = set(render_all(lang, live))
            for src in re.findall(r'src="assets/([^/]+)/([^"]+)"', md):
                self.assertEqual(src[0], lang)
                self.assertIn(src[1], rendered)

    def test_alts_are_escaped_and_filled(self):
        live = load_live(Path("data/live.json"), refresh=False, token=None)
        for lang in LANGS:
            md = render_readme(lang)
            self.assertNotRegex(md, r"\{[a-z]+\}")
            alts = re.findall(r'alt="([^"]*)"', md)
            for alt in alts:
                self.assertTrue(alt)
                self.assertNotIn("<", alt)
                self.assertNotRegex(alt, r"&(?!(?:amp|lt|gt|quot|#\d+|#x[0-9a-f]+);)")
            joined = "\n".join(alts)
            self.assertIn(fmt_int(live.total, lang), joined)
            self.assertIn(fmt_int(live.best_day, lang), joined)
            ach = [a for a in alts if "ogros" in a or "chievements" in a]
            self.assertTrue(ach)
            streak = streak_text(lang, live)            # a mitad de frase, en minúscula
            self.assertIn(escape(streak[0].lower() + streak[1:], quote=True), ach[0])
        self.assertIn(fmt_int(live.total, "es"), render_readme("es"))
        self.assertIn(fmt_int(live.total, "en"), render_readme("en"))

    def test_readme_alts_match_svg_titles(self):
        live = load_live(Path("data/live.json"), refresh=False, token=None)
        for lang in LANGS:
            p = _Imgs()
            p.feed(render_readme(lang, live))
            alts = {Path(dict(a)["src"]).name: dict(a)["alt"] for a in p.imgs}
            svgs = render_all(lang, live)
            for name in ("hero.svg", "sheet.svg", "achievements.svg", "inventory.svg",
                         "highscore.svg", "bilbao.svg"):
                title = ET.fromstring(svgs[name]).find("{*}title").text
                self.assertEqual(alts[name], title, (lang, name))

    def test_img_attributes_parse_cleanly(self):
        for lang in LANGS:
            md = render_readme(lang)
            p = _Imgs()
            p.feed(md)
            self.assertEqual(len(p.imgs), md.count("<img"))
            for attrs in p.imgs:
                names = [k for k, _ in attrs]
                self.assertLessEqual(set(names), {"src", "alt", "width", "height"})
                self.assertEqual(len(names), len(set(names)))
                self.assertTrue(dict(attrs).get("alt"))

    def test_build_fails_on_invalid_svg_and_writes_nothing(self):
        from gen.scenes import hero
        with tempfile.TemporaryDirectory() as d:
            out = Path(d)
            _copy_data(out)
            bad = lambda lang, live: {"hero.svg": "<svg><script>x</script></svg>"}  # noqa: E731
            with mock.patch.object(hero, "render", bad):
                with self.assertRaises(SystemExit):
                    build(out, refresh=False, token=None)
            self.assertFalse((out / "README.md").exists())
            self.assertFalse((out / "README.en.md").exists())
            self.assertFalse((out / "assets").exists())


if __name__ == "__main__":
    unittest.main()

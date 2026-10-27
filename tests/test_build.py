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
from gen.readme import MOBILE_MEDIA, RAW_BASE, render_readme


def _copy_data(out: Path) -> None:
    shutil.copytree("data", out / "data")


class _Imgs(HTMLParser):
    """Los <img> y los <source> del README; cada <picture> con los suyos."""

    def __init__(self):
        super().__init__()
        self.imgs, self.sources, self.pictures = [], [], []
        self._open = None                       # el <picture> abierto, si lo hay

    def handle_starttag(self, tag, attrs):
        if tag == "picture":
            self._open = {"sources": [], "imgs": []}
            self.pictures.append(self._open)
        elif tag in ("img", "source"):
            (self.imgs if tag == "img" else self.sources).append(attrs)
            if self._open is not None:
                self._open[tag + "s"].append(dict(attrs))

    def handle_endtag(self, tag):
        if tag == "picture":
            self._open = None


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
            # las variantes móviles de los <source>, con su URL absoluta
            srcsets = re.findall(r'srcset="([^"]*)"', md)
            self.assertTrue(srcsets, lang)
            for srcset in srcsets:
                m = re.fullmatch(re.escape(RAW_BASE) + r"assets/([^/]+)/(m-[^/]+\.svg)", srcset)
                self.assertTrue(m, srcset)
                self.assertEqual(m.group(1), lang)
                self.assertIn(m.group(2), rendered)

    def test_picture_sources_absolute(self):
        # GitHub reescribe el src relativo de un <img>, pero no hay garantía de que lo haga con
        # el srcset de un <source>: va absoluto
        self.assertEqual(RAW_BASE, "https://github.com/diegoreto7u7/diegoreto7u7/raw/main/")
        self.assertEqual(MOBILE_MEDIA, "(max-width: 600px)")
        live = load_live(Path("data/live.json"), refresh=False, token=None)
        for lang in LANGS:
            rendered = set(render_all(lang, live))
            p = _Imgs()
            p.feed(render_readme(lang, live))
            self.assertTrue(p.pictures, lang)
            self.assertEqual(len(p.sources), sum(len(pic["sources"]) for pic in p.pictures))
            used = set()
            for pic in p.pictures:
                self.assertEqual((len(pic["sources"]), len(pic["imgs"])), (1, 1), (lang, pic))
                source, img = pic["sources"][0], pic["imgs"][0]
                self.assertEqual(source["media"], MOBILE_MEDIA)
                desktop = Path(img["src"]).name
                self.assertEqual(img["src"], f"assets/{lang}/{desktop}")
                self.assertEqual(source["srcset"], f"{RAW_BASE}assets/{lang}/m-{desktop}")
                self.assertIn(f"m-{desktop}", rendered)
                used.add(f"m-{desktop}")
            # cada variante móvil sale en el README y solo se quedan sin ella los botones y Bilbao
            self.assertEqual(used, {n for n in rendered if n.startswith("m-")}, lang)
            plain = {Path(dict(a)["src"]).name for a in p.imgs} - {n[2:] for n in used}
            self.assertEqual({n for n in plain if not n.startswith("btn-")}, {"bilbao.svg"})

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
            self.assertEqual(len(p.sources), md.count("<source"))
            self.assertEqual(len(p.pictures), md.count("<picture>"))
            self.assertEqual(md.count("<picture"), md.count("</picture>"))
            for attrs in p.sources:
                names = [k for k, _ in attrs]
                self.assertLessEqual(set(names), {"media", "srcset"})
                self.assertEqual(len(names), len(set(names)))
                self.assertTrue(all(v for _, v in attrs))

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

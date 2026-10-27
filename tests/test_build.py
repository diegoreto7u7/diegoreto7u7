import re
import shutil
import tempfile
import unittest
from pathlib import Path

from gen.build import build, render_all
from gen.content import LANGS
from gen.live import load_live
from gen.readme import render_readme


def _copy_data(out: Path) -> None:
    shutil.copytree("data", out / "data")


class BuildTests(unittest.TestCase):
    def test_build_writes_everything(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d)
            _copy_data(out)
            paths = build(out, refresh=False, token=None)
            self.assertTrue(paths)
            for lang in LANGS:
                self.assertTrue((out / "assets" / lang / "hero.svg").exists())
                self.assertEqual(len(list((out / "assets" / lang).glob("*.svg"))), 18)
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
        for lang in LANGS:
            md = render_readme(lang)
            self.assertNotRegex(md, r"\{[a-z]+\}")
            for alt in re.findall(r'alt="([^"]*)"', md):
                self.assertNotIn("<", alt)
                self.assertTrue(alt)


if __name__ == "__main__":
    unittest.main()

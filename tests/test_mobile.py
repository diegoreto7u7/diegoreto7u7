"""Variantes móviles (m-*.svg): lienzo de 420, mismo contenido y escritorio intacto."""

import hashlib
import json
import unittest
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

from gen.build import render_all
from gen.content import COPY, LANGS
from gen.live import LiveStats
from gen.svg import balanced_wrap, text_width, wrap
from gen.svgcheck import check_svg
from tests.helpers import LIVE

SNAPSHOT = Path(__file__).parent / "fixtures" / "desktop_snapshot.json"
MOBILE = ("m-hero.svg", "m-quests-title.svg", "m-quests-more.svg", "m-start.svg")
M_W = 420


def desktop_hashes() -> dict[str, str]:
    """sha256 de cada SVG de escritorio (no m-*) de los dos idiomas, renderizado con LIVE.

    Con LIVE y no con data/live.json, que el bot reescribe cada día.
    """
    return {f"{lang}/{name}": hashlib.sha256(svg.encode("utf-8")).hexdigest()
            for lang in LANGS for name, svg in sorted(render_all(lang, LIVE).items())
            if not name.startswith("m-")}


def write_snapshot() -> None:
    """Regenera el fixture tras un cambio de escritorio hecho a propósito (p. ej. en content.py):

        python3 -c "import tests.test_mobile as t; t.write_snapshot()"
    """
    SNAPSHOT.write_text(json.dumps(desktop_hashes(), indent=2, sort_keys=True) + "\n",
                        encoding="utf-8", newline="\n")


def _texts(svg: str) -> list[str]:
    root = ET.fromstring(svg)
    return ["".join(t.itertext()) for t in root.findall(".//{*}text")]


def _words(svg: str) -> list[str]:
    return " ".join(_texts(svg)).split()


class MobileTests(unittest.TestCase):
    def setUp(self):
        self.out = {lang: render_all(lang, LIVE) for lang in LANGS}

    def test_mobile_variants_exist_and_valid(self):
        for lang in LANGS:
            for name in MOBILE:
                self.assertIn(name, sorted(self.out[lang]), lang)
                svg = self.out[lang][name]
                self.assertEqual(check_svg(svg), [], (lang, name))
                vb = ET.fromstring(svg).get("viewBox")
                self.assertTrue(vb.startswith(f"0 0 {M_W} "), (lang, name, vb))

    def test_every_mobile_file_has_a_desktop_twin(self):
        for lang in LANGS:
            for name in self.out[lang]:
                if name.startswith("m-"):
                    self.assertIn(name[2:], sorted(self.out[lang]), lang)

    def test_desktop_unchanged_vs_snapshot(self):
        # el fixture se generó con el código anterior a las variantes móviles: un retoque móvil
        # no puede cambiar ni un byte del escritorio
        snap = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
        got = desktop_hashes()
        self.assertEqual(sorted(got), sorted(snap))
        for key in sorted(snap):
            self.assertEqual(got[key], snap[key], key)

    def test_mobile_large_numbers_fit(self):
        big = LiveStats(days=LIVE.days, total=1_234_567, best_day=9_999, active_days=366,
                        window_days=366, current_streak=365, longest_streak=366)
        for lang in LANGS:
            out = render_all(lang, big)
            self.assertLessEqual(set(MOBILE), set(out), lang)
            for name in out:
                if name.startswith("m-"):
                    self.assertEqual(check_svg(out[name]), [], (lang, name))

    def test_mobile_text_stays_inside_canvas(self):
        anchors = {"start": 0, "middle": 0.5, "end": 1}
        for lang in LANGS:
            for name in MOBILE:
                root = ET.fromstring(self.out[lang][name])
                for t in root.findall(".//{*}text"):
                    s = "".join(t.itertext())
                    w = text_width(s, t.get("font-family"), float(t.get("font-size")))
                    left = float(t.get("x")) - w * anchors[t.get("text-anchor")]
                    self.assertGreaterEqual(left, 0, (lang, name, s))
                    self.assertLessEqual(left + w, M_W, (lang, name, s))

    def test_mobile_hero_same_content(self):
        # mismo contenido que el escritorio: solo cambia la maquetación
        for lang in LANGS:
            self.assertEqual(Counter(_words(self.out[lang]["m-hero.svg"])),
                             Counter(_words(self.out[lang]["hero.svg"])), lang)
            m = self.out[lang]["m-hero.svg"]
            self.assertEqual(m.count('class="walker'), 4)
            for cls in ("nosig", "flash", "blink", "z z0", "z z1"):
                self.assertIn(f'class="{cls}"', m, (lang, cls))

    def test_mobile_hero_stacks_terminal_over_full_width_camera(self):
        root = ET.fromstring(self.out["es"]["m-hero.svg"])
        clip = root.find(".//{*}clipPath[@id='cam']/{*}rect")
        cam_x, cam_y, cam_w = (float(clip.get(k)) for k in ("x", "y", "width"))
        self.assertGreaterEqual(cam_w, M_W - 16)                 # a todo el ancho
        self.assertLessEqual(cam_x + cam_w, M_W)
        term_ys = [float(t.get("y")) for t in root.findall(".//{*}text")
                   if "".join(t.itertext()) in {COPY["es"][f"hero.t{i}"] for i in range(1, 8)}]
        self.assertEqual(len(term_ys), 7)
        self.assertLess(max(term_ys), cam_y)                    # el terminal va encima

    def test_mobile_title_same_text(self):
        for lang in LANGS:
            self.assertEqual(_texts(self.out[lang]["m-quests-title.svg"]),
                             _texts(self.out[lang]["quests-title.svg"]), lang)

    def test_mobile_more_and_start_same_words(self):
        for lang in LANGS:
            for name in ("quests-more.svg", "start.svg"):
                self.assertEqual(_words(self.out[lang]["m-" + name]),
                                 _words(self.out[lang][name]), (lang, name))

    def test_mobile_start_splits_into_balanced_lines(self):
        texts = _texts(self.out["es"]["m-start.svg"])
        self.assertEqual(texts[:2], ["PULSA START PARA", "HABLAR CONMIGO"])
        texts = _texts(self.out["en"]["m-start.svg"])
        self.assertEqual(texts[:2], ["PRESS START TO", "GET IN TOUCH"])


class BalancedWrapTests(unittest.TestCase):
    def test_same_line_count_as_wrap_and_lines_fit(self):
        s = "PULSA START PARA HABLAR CONMIGO"
        for width in (200, 260, 374, 500):
            lines = balanced_wrap(s, "ps2p", 16, width)
            self.assertEqual(len(lines), len(wrap(s, "ps2p", 16, width)), width)
            self.assertEqual(" ".join(lines), s)
            self.assertTrue(all(text_width(l, "ps2p", 16) <= width for l in lines), width)

    def test_balances_the_longest_line(self):
        # wrap deja «CONMIGO» sola; balanced_wrap reparte
        self.assertEqual(wrap("PULSA START PARA HABLAR CONMIGO", "ps2p", 16, 374),
                         ["PULSA START PARA HABLAR", "CONMIGO"])
        self.assertEqual(balanced_wrap("PULSA START PARA HABLAR CONMIGO", "ps2p", 16, 374),
                         ["PULSA START PARA", "HABLAR CONMIGO"])

    def test_single_line_when_it_fits(self):
        self.assertEqual(balanced_wrap("uno dos", "vt323", 22, 400), ["uno dos"])


if __name__ == "__main__":
    unittest.main()

import unittest

from gen.content import LANGS
from gen.scenes import footer
from gen.svgcheck import check_svg
from tests.helpers import LIVE


class FooterTests(unittest.TestCase):
    def test_footer_valid(self):
        for lang in LANGS:
            out = footer.render(lang, LIVE)
            self.assertEqual(set(out), {"bilbao.svg", "start.svg", "m-start.svg"})
            for svg in out.values():
                self.assertEqual(check_svg(svg), [])

    def test_bilbao_deterministic(self):
        self.assertEqual(footer.render("es", LIVE)["bilbao.svg"],
                         footer.render("es", LIVE)["bilbao.svg"])

    def test_bilbao_size_and_layers(self):
        svg = footer.render("es", LIVE)["bilbao.svg"]
        self.assertIn('viewBox="0 0 840 230"', svg)
        self.assertNotIn("<text", svg)
        for cls in ("tw", "win", "sh", "shoot"):
            self.assertIn(f'class="{cls}', svg)

    def test_shooting_star_hidden_in_base_state(self):
        svg = footer.render("es", LIVE)["bilbao.svg"]
        self.assertIn(".shoot{opacity:0;", svg)

    def test_hills_lighter_than_sky(self):
        def lum(c):
            return sum(int(c[i:i + 2], 16) * w for i, w in ((1, .2126), (3, .7152), (5, .0722)))
        sky = max(lum(footer.PAL[k]) for k in "abcd")
        self.assertGreater(lum(footer.PAL["i"]), sky * 1.3)      # Artxanda se lee como monte
        self.assertGreater(lum(footer.PAL["h"]), lum(footer.PAL["i"]))   # cresta iluminada

    def test_start_text(self):
        self.assertIn("PRESS START TO GET IN TOUCH", footer.render("en", LIVE)["start.svg"])
        self.assertIn("PULSA START PARA HABLAR CONMIGO", footer.render("es", LIVE)["start.svg"])

    def test_start_has_email_and_size(self):
        svg = footer.render("es", LIVE)["start.svg"]
        self.assertIn("orueret@gmail.com", svg)
        self.assertIn('viewBox="0 0 840 88"', svg)


if __name__ == "__main__":
    unittest.main()

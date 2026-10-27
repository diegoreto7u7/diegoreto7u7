import unittest

from gen.content import LANGS, QUESTS
from gen.scenes import buttons, quests
from gen.svg import wrap
from gen.svgcheck import check_svg
from tests.helpers import LIVE


class TestSceneLinks(unittest.TestCase):
    def test_buttons_valid_and_sized(self):
        for lang in LANGS:
            out = buttons.render(lang, LIVE)
            self.assertEqual(set(out), {"btn-portfolio.svg", "btn-linkedin.svg", "btn-email.svg",
                                        "btn-cv.svg", "btn-lang.svg"})
            for svg in out.values():
                self.assertEqual(check_svg(svg), [])
                self.assertIn('viewBox="0 0 216 56"', svg)
        self.assertIn("ESPAÑOL", buttons.render("en", LIVE)["btn-lang.svg"])

    def test_only_portfolio_button_blinks(self):
        out = buttons.render("es", LIVE)
        for name, svg in out.items():
            self.assertEqual("blink" in svg, name == "btn-portfolio.svg", name)

    def test_quest_cards(self):
        out = quests.render("es", LIVE)
        self.assertIn("quest-smart-city-platform.svg", out)
        self.assertIn("Sistema desplegado", out["quest-conteobk.svg"])
        self.assertIn("+9 misiones más", out["quests-more.svg"])
        self.assertIn('viewBox="0 0 416 196"', out["quest-nectum.svg"])
        self.assertIn('viewBox="0 0 840 56"', out["quests-title.svg"])
        for svg in out.values():
            self.assertEqual(check_svg(svg), [])

    def test_english_quests_use_ai(self):
        out = quests.render("en", LIVE)
        self.assertIn("AI", out["quest-licitaciones.svg"])
        self.assertIn("+9 more quests", out["quests-more.svg"])

    def test_summary_fits_two_lines(self):
        for lang in LANGS:
            for q in QUESTS:
                self.assertLessEqual(len(wrap(q.summary[lang], "vt323", 22, quests.SUMMARY_W)), 2)

    def test_status_dot_colour_follows_in_progress(self):
        out = quests.render("es", LIVE)
        for slug, colour, other in [("nectum", "#e3b341", "#3fb950"),
                                    ("smart-city-platform", "#e3b341", "#3fb950"),
                                    ("conteobk", "#3fb950", "#e3b341"),
                                    ("licitaciones", "#3fb950", "#e3b341")]:
            svg = out[f"quest-{slug}.svg"]
            self.assertIn(f'<rect x="37" y="159" width="9" height="3" fill="{colour}"/>', svg, slug)
            self.assertNotIn(f'<rect x="37" y="159" width="9" height="3" fill="{other}"/>', svg, slug)

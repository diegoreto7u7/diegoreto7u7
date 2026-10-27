import unittest
import xml.etree.ElementTree as ET

from gen.content import COPY, LANGS, SKILLS, fmt_int
from gen.live import LiveStats, compute_stats
from gen.scenes import achievements, quests, sheet
from gen.scenes.common import header
from gen.scenes.sheet import segments
from gen.svg import escape
from gen.svgcheck import check_svg
from tests.helpers import LIVE, days_with_current_streak


class TestSceneSheet(unittest.TestCase):
    def test_segments(self):
        self.assertEqual([segments(p) for _, p in SKILLS], [20, 20, 14, 4, 2, 2])

    def test_sheet_valid_and_live(self):
        svg = sheet.render("es", LIVE)["sheet.svg"]
        self.assertEqual(check_svg(svg), [])
        self.assertIn(fmt_int(LIVE.total, "es"), svg)

    def test_sheet_english(self):
        svg = sheet.render("en", LIVE)["sheet.svg"]
        self.assertEqual(check_svg(svg), [])
        self.assertIn("CHARACTER SHEET", svg)
        self.assertIn(f"{LIVE.active_days}/{LIVE.window_days} active days", svg)

    def test_achievements_streak_rule(self):
        low = compute_stats(days_with_current_streak(2, longest=16))
        self.assertIn("Racha récord: 16", achievements.render("es", low)["achievements.svg"])
        hi = compute_stats(days_with_current_streak(5, longest=5))
        self.assertIn("Current streak: 5", achievements.render("en", hi)["achievements.svg"])

    def test_achievements_has_all_seven(self):
        svg = achievements.render("es", LIVE)["achievements.svg"]
        for k in ("ach.langs", "ach.gpu", "ach.rag", "ach.rust", "ach.go"):
            self.assertIn(escape(COPY["es"][k]), svg)

    def test_achievements_order_and_first_visible(self):
        for lang in LANGS:
            svg = achievements.render(lang, LIVE)["achievements.svg"]
            self.assertEqual(check_svg(svg), [])
            c = COPY[lang]
            texts = [c["ach.best_day"].format(n=fmt_int(LIVE.best_day, lang))]
            texts += [c[f"ach.{k}"] for k in ("langs", "gpu", "rag", "rust", "go")]
            texts.append(c["ach.streak_current"].format(n=LIVE.current_streak))
            root = ET.fromstring(svg)
            toasts = [g for g in root.findall(".//{*}g")
                      if "toast" in (g.get("class") or "").split()]
            self.assertEqual(len(toasts), 7)
            for g, t in zip(toasts, texts):
                self.assertIn(t, [e.text for e in g.findall(".//{*}text")])
            # la primera ya está en su sitio en t = 0; las demás entran deslizándose
            self.assertEqual(toasts[0].get("class"), "toast")
            self.assertTrue(all("slide" in g.get("class") for g in toasts[1:]))

    def test_section_headers_share_one_style(self):
        for lang in LANGS:
            c = COPY[lang]
            for svg, key in ((quests.render(lang, LIVE)["quests-title.svg"], "quests.title"),
                             (sheet.render(lang, LIVE)["sheet.svg"], "sheet.title"),
                             (achievements.render(lang, LIVE)["achievements.svg"], "ach.title")):
                self.assertIn(header(c[key]), svg, key)

    def test_large_numbers_fit(self):
        big = LiveStats(days=LIVE.days, total=123456, best_day=9999, active_days=366,
                        window_days=366, current_streak=366, longest_streak=366)
        for lang in LANGS:
            sheet.render(lang, big)
            achievements.render(lang, big)   # no lanza ValueError por desbordamiento


if __name__ == "__main__":
    unittest.main()

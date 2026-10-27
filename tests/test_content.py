import unittest

from gen.content import (COPY, INVENTORY, LANGS, PROJECT_TOTAL, QUESTS, SKILLS,
                         URLS, fmt_int)
from gen.fonts import CHARSET


class ContentTest(unittest.TestCase):
    def test_same_keys_in_both_languages(self):
        self.assertEqual(set(COPY["es"]), set(COPY["en"]))

    def test_all_copy_within_charset(self):
        for lang in LANGS:
            for k, v in COPY[lang].items():
                if k == "intro":
                    v = v.replace("*", "")
                self.assertTrue(set(v) <= set(CHARSET), (lang, k, set(v) - set(CHARSET)))

    def test_alt_keys_and_placeholders(self):
        for lang in LANGS:
            for k in ("lang", "hero", "sheet", "achievements", "inventory", "highscore", "bilbao"):
                self.assertIn("alt." + k, COPY[lang])
            self.assertIn("{window}", COPY[lang]["alt.sheet"])
            self.assertIn("{streak}", COPY[lang]["alt.achievements"])
            self.assertIn("{best}", COPY[lang]["alt.highscore"])

    def test_fmt_int(self):
        self.assertEqual(fmt_int(4452, "es"), "4.452")
        self.assertEqual(fmt_int(4452, "en"), "4,452")
        self.assertEqual(fmt_int(143, "es"), "143")

    def test_quests(self):
        self.assertEqual([q.slug for q in QUESTS], ["conteobk", "licitaciones", "nectum", "smart-city-platform"])
        self.assertEqual([q.starred for q in QUESTS], [True, True, False, False])
        self.assertEqual(PROJECT_TOTAL - len(QUESTS), 9)
        for q in QUESTS:
            for text in (q.stack, *q.title.values(), *q.summary.values(), *q.status.values()):
                self.assertTrue(set(text) <= set(CHARSET), (q.slug, text))

    def test_skills_inventory_urls(self):
        self.assertEqual(len(SKILLS), 6)
        self.assertEqual(len(INVENTORY), 10)
        self.assertEqual(URLS["en"]["quest.nectum"], "https://diegoret.pages.dev/en/projects/nectum/")
        self.assertEqual(URLS["es"]["quest.nectum"], "https://diegoret.pages.dev/proyectos/nectum/")
        self.assertTrue(URLS["es"]["lang"].endswith("README.en.md"))


if __name__ == "__main__":
    unittest.main()

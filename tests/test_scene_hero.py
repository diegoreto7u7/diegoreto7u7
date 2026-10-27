import unittest
import xml.etree.ElementTree as ET

from gen.content import COPY, LANGS
from gen.scenes.hero import render
from gen.svg import escape
from gen.svgcheck import check_svg
from tests.helpers import LIVE


class TestSceneHero(unittest.TestCase):
    def test_hero_valid_both_langs(self):
        for lang in LANGS:
            svg = render(lang, LIVE)["hero.svg"]
            self.assertEqual(check_svg(svg), [])

    def test_name_and_role_static(self):
        root = ET.fromstring(render("es", LIVE)["hero.svg"])
        # iter() no admite el comodín {*}; findall sí
        name = [t for t in root.findall(".//{*}text") if t.text == "DIEGO ORUE"][0]
        self.assertFalse(name.get("class"))          # sin clase de animación
        self.assertIn("Desarrollador de software", ET.tostring(root, encoding="unicode"))

    def test_four_detection_boxes(self):
        self.assertEqual(render("en", LIVE)["hero.svg"].count('class="walker'), 4)

    def test_translated(self):
        self.assertIn("NO SIGNAL", render("en", LIVE)["hero.svg"])
        self.assertIn("SIN SEÑAL", render("es", LIVE)["hero.svg"])

    def test_terminal_shows_every_line(self):
        for lang in LANGS:
            svg = render(lang, LIVE)["hero.svg"]
            for i in range(1, 8):
                # el prompt («$ » o «> ») va en su propio color, así que basta con el resto
                line = COPY[lang][f"hero.t{i}"]
                body = line[2:] if line[:2] in ("$ ", "> ") else line
                self.assertIn(escape(body.removesuffix(" OK")), svg)


if __name__ == "__main__":
    unittest.main()

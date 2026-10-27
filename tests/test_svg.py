import unittest
import xml.etree.ElementTree as ET

from gen.svg import document, pct, rect, text, text_width, wrap


class TestSvg(unittest.TestCase):
    def test_text_escapes_xml(self):
        doc = document(840, 100, "t", text(0, 50, "vision & <data>", "vt323", 26, "#fff"))
        ET.fromstring(doc)

    def test_text_rejects_small_size(self):
        with self.assertRaises(ValueError):
            text(0, 0, "a", "ps2p", 12, "#fff")

    def test_text_rejects_char_outside_charset(self):
        with self.assertRaises(ValueError):
            text(0, 0, "10 €", "vt323", 26, "#fff")

    def test_text_rejects_overflow(self):
        with self.assertRaises(ValueError):
            text(0, 0, "ABCDEFGHIJ", "ps2p", 20, "#fff", max_width=150)

    def test_text_omits_empty_class(self):
        self.assertNotIn("class", text(0, 0, "a", "vt323", 26, "#fff"))
        self.assertIn('class="x"', text(0, 0, "a", "vt323", 26, "#fff", cls="x"))

    def test_wrap_respects_width(self):
        lines = wrap("uno dos tres cuatro cinco", "vt323", 25, 100)
        self.assertTrue(all(text_width(l, "vt323", 25) <= 100 for l in lines))
        self.assertEqual(" ".join(lines), "uno dos tres cuatro cinco")

    def test_document_shape(self):
        root = ET.fromstring(document(840, 120, "Hola", "", css="@keyframes a{}", fonts=["ps2p"]))
        self.assertEqual(root.get("viewBox"), "0 0 840 120")
        self.assertIn("prefers-reduced-motion", ET.tostring(root, encoding="unicode"))

    def test_frame_css_only_with_two_frames(self):
        self.assertNotIn("@keyframes", document(840, 100, "t", ""))
        doc = document(840, 100, "t", '<g class="f1"></g>')
        self.assertIn("@keyframes", doc)
        self.assertIn("prefers-reduced-motion", doc)

    def test_font_face_embedded(self):
        doc = document(840, 100, "t", "", fonts=["ps2p", "vt323"])
        self.assertEqual(doc.count("@font-face"), 2)
        self.assertIn("data:font/woff;base64,", doc)

    def test_shared_rect_and_pct(self):
        self.assertEqual(rect(0, 4, 8, 2, "#fff"), '<rect x="0" y="4" width="8" height="2" fill="#fff"/>')
        self.assertEqual(rect(1, 2, 3, 4, "#000", ' class="blink"'),
                         '<rect x="1" y="2" width="3" height="4" fill="#000" class="blink"/>')
        self.assertEqual(pct(7, 14), "50.00")
        self.assertEqual(pct(7, 14, trim=True), "50")
        self.assertEqual(pct(3, 24, trim=True), "12.5")

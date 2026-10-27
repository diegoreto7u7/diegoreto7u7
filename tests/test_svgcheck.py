import unittest

from gen.svg import document
from gen.svgcheck import check_svg

HEAD = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 50" width="100" height="50">'
BG = '<rect width="100" height="50" fill="#000"/>'


def mini(body=BG, title="<title>t</title>", style=""):
    return f"{HEAD}{title}{style}{body}</svg>"


class TestSvgCheck(unittest.TestCase):
    def has(self, svg, word):
        self.assertTrue(any(word in p for p in check_svg(svg)), check_svg(svg))

    def test_clean_document_passes(self):
        self.assertEqual(check_svg(document(840, 100, "ok", "")), [])

    def test_clean_minimal_passes(self):
        self.assertEqual(check_svg(mini()), [])

    def test_detects_external_url(self):
        bad = document(840, 100, "x", '<image href="https://x.y/a.png"/>')
        self.assertTrue(any("externa" in p for p in check_svg(bad)))

    def test_external_url_in_css(self):
        self.has(mini(style="<style>a{background:url(http://x.y/a.png)}</style>"), "externa")
        self.has(mini(style='<style>@import "https://x.y/a.css";</style>'), "externa")

    def test_data_url_and_xmlns_not_flagged(self):
        css = "<style>@font-face{font-family:a;src:url(data:font/woff;base64,AAAA)}</style>"
        self.assertEqual(check_svg(mini(style=css)), [])

    def test_detects_script(self):
        self.has(mini(body=BG + "<script>1</script>"), "script")

    def test_detects_missing_title(self):
        self.has(mini(title=""), "title")

    def test_detects_missing_bg(self):
        self.has(mini(body='<rect width="10" height="10"/>'), "fondo")
        self.has(mini(body="<g/>"), "fondo")

    def test_detects_small_font(self):
        self.has(mini(body=BG + '<text font-family="ps2p" font-size="12">a</text>'), "tamaño")

    def test_detects_keyframes_without_reduced_motion(self):
        self.has(mini(style="<style>@keyframes a{}</style>"), "movimiento")

    def test_detects_unparseable(self):
        self.has("<svg", "XML")

    def test_detects_no_viewbox_and_wrong_root(self):
        self.has('<svg xmlns="http://www.w3.org/2000/svg"><title>t</title></svg>', "viewBox")
        self.has("<html/>", "svg")

    def test_detects_oversize(self):
        self.has(mini(body=BG + "<!--" + "a" * 500001 + "-->"), "bytes")

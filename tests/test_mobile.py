"""Variantes móviles (m-*.svg): 420 de ancho (tarjetas, 200), mismo contenido y escritorio intacto."""

import hashlib
import json
import re
import unittest
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

from gen.build import render_all
from gen.content import COPY, INVENTORY, LANGS, QUESTS, SKILLS, fmt_int, quest_stack
from gen.live import LiveStats, compute_stats
from gen.scenes.sheet import segments
from gen.svg import balanced_wrap, text_width, wrap
from gen.svgcheck import check_svg
from tests.helpers import LIVE, days_with_current_streak

SNAPSHOT = Path(__file__).parent / "fixtures" / "desktop_snapshot.json"
MOBILE = ("m-hero.svg", "m-quests-title.svg", "m-quests-more.svg", "m-start.svg",
          "m-sheet.svg", "m-achievements.svg", "m-inventory.svg", "m-highscore.svg")
CARDS = tuple(f"m-quest-{q.slug}.svg" for q in QUESTS)   # tarjetas: 200 de ancho, se ven al 49 %
M_W = 420
CARD_W = 200
PHONE = 276          # ancho real de la columna del README en el móvil, en px CSS
SVG_NS = "{http://www.w3.org/2000/svg}"


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


def _width(svg: str) -> float:
    return float(ET.fromstring(svg).get("viewBox").split()[2])


def _height(svg: str) -> float:
    return float(ET.fromstring(svg).get("viewBox").split()[3])


def _texts(svg: str) -> list[str]:
    root = ET.fromstring(svg)
    return ["".join(t.itertext()) for t in root.findall(".//{*}text")]


def _words(svg: str) -> list[str]:
    return " ".join(_texts(svg)).split()


ANCHORS = {"start": 0, "middle": 0.5, "end": 1}


def _text_spans(svg: str) -> list[tuple[str, float, float]]:
    """(texto, x izquierda, x derecha) de cada <text>, con el ancho estimado de ADVANCE."""
    out = []
    for t in ET.fromstring(svg).findall(".//{*}text"):
        s = "".join(t.itertext())
        w = text_width(s, t.get("font-family"), float(t.get("font-size")))
        left = float(t.get("x")) - w * ANCHORS[t.get("text-anchor")]
        out.append((s, left, left + w))
    return out


def _classed(root: ET.Element, tag: str, cls: str) -> list[ET.Element]:
    return [e for e in root.iter()
            if e.tag == SVG_NS + tag and cls in (e.get("class") or "").split()]


def _rects(el: ET.Element) -> list[ET.Element]:
    return list(el.iter(SVG_NS + "rect"))


def _toast_label(g: ET.Element) -> str:
    """El logro de una notificación (sin «¡Logro desbloqueado!»), con sus líneas unidas."""
    lines = ["".join(t.itertext()) for t in g.iter(SVG_NS + "text")]
    return " ".join(lines[1:])


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
                    for text, left, right in _text_spans(out[name]):
                        self.assertGreaterEqual(left, 0, (lang, name, text))
                        self.assertLessEqual(right, _width(out[name]), (lang, name, text))
            # las cifras grandes salen enteras (partidas en líneas si hace falta)
            words = (_words(out["m-sheet.svg"]) + _words(out["m-achievements.svg"])
                     + _words(out["m-highscore.svg"]))
            self.assertIn(fmt_int(1_234_567, lang), words, lang)
            self.assertIn(fmt_int(9_999, lang), words, lang)

    def test_mobile_text_stays_inside_canvas(self):
        for lang in LANGS:
            for name in MOBILE + CARDS:
                svg = self.out[lang][name]
                for text, left, right in _text_spans(svg):
                    self.assertGreaterEqual(left, 0, (lang, name, text))
                    self.assertLessEqual(right, _width(svg), (lang, name, text))

    def test_mobile_titles_match_desktop(self):
        # el README lleva un solo alt para las dos versiones: el <title> tiene que ser el mismo
        for lang in LANGS:
            for name, svg in self.out[lang].items():
                if name.startswith("m-"):
                    self.assertEqual(ET.fromstring(svg).find("{*}title").text,
                                     ET.fromstring(self.out[lang][name[2:]]).find("{*}title").text,
                                     (lang, name))

    def test_mobile_headers_same_size(self):
        # todas las cabeceras móviles al mismo tamaño: el mayor al que caben todos los títulos
        # (18, por «LOGROS DESBLOQUEADOS»); las de escritorio siguen a 20
        def sizes(mobile: bool) -> set[tuple[str, str]]:
            out = set()
            for lang in LANGS:
                for name, svg in self.out[lang].items():
                    if name.startswith("m-") != mobile:
                        continue
                    for t in ET.fromstring(svg).iter(SVG_NS + "text"):
                        if (t.get("x"), t.get("y"), t.get("font-family")) == ("28", "34", "ps2p"):
                            out.add((name, t.get("font-size")))
            return out

        mobile, desktop = sizes(True), sizes(False)
        self.assertEqual({n for n, _ in mobile},
                         {"m-quests-title.svg", "m-sheet.svg", "m-achievements.svg",
                          "m-inventory.svg", "m-highscore.svg"})
        self.assertEqual({s for _, s in mobile}, {"18"})
        self.assertEqual(len(desktop), 5)
        self.assertEqual({s for _, s in desktop}, {"20"})

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

    # --- ficha ---

    def test_mobile_sheet_same_content(self):
        for lang in LANGS:
            self.assertEqual(Counter(_words(self.out[lang]["m-sheet.svg"])),
                             Counter(_words(self.out[lang]["sheet.svg"])), lang)
            # al partir una línea, el «·» se queda al final de la anterior
            self.assertFalse([t for t in _texts(self.out[lang]["m-sheet.svg"])
                              if t.startswith("·")], lang)
            # el texto queda dentro del marco del panel (borde interior en 10 y en 410)
            for text, left, right in _text_spans(self.out[lang]["m-sheet.svg"])[1:]:
                self.assertGreaterEqual(left, 10, (lang, text))
                self.assertLessEqual(right, M_W - 10, (lang, text))

    def test_mobile_sheet_avatar_centered_on_top_and_big(self):
        root = ET.fromstring(self.out["es"]["m-sheet.svg"])
        # el avatar y la taza (fotograma A) van centrados, encima del nombre
        frames = [r for g in _classed(root, "g", "f1") for r in _rects(g)]
        x0 = min(float(r.get("x")) for r in frames)
        x1 = max(float(r.get("x")) + float(r.get("width")) for r in frames)
        self.assertAlmostEqual((x0 + x1) / 2, M_W / 2, delta=2)
        bottom = max(float(r.get("y")) + float(r.get("height")) for r in frames)
        name = next(t for t in root.iter(SVG_NS + "text") if t.text == "DIEGO ORUE")
        self.assertLess(bottom, float(name.get("y")) - 24)
        # reloj (esfera #56d4dd) y pulsera (#c0c7d0) a 4,5 px CSS o más por píxel en el móvil
        for color in ("#56d4dd", "#c0c7d0"):
            px = {float(r.get("height")) for r in frames if r.get("fill") == color}
            self.assertTrue(px, color)
            self.assertGreaterEqual(min(px) * PHONE / M_W, 4.5, color)

    def test_mobile_sheet_keeps_blink_mug_and_hearts(self):
        for lang in LANGS:
            m = ET.fromstring(self.out[lang]["m-sheet.svg"])
            d = ET.fromstring(self.out[lang]["sheet.svg"])
            for cls in ("eyes", "glow"):
                # el parpadeo solo tapa las filas de los ojos, igual que en escritorio
                self.assertEqual(len(_rects(_classed(m, "g", cls)[0])),
                                 len(_rects(_classed(d, "g", cls)[0])), (lang, cls))
            self.assertEqual(len(_classed(m, "g", "f1")), 2, lang)     # avatar y taza
            # corazones: ES 3/3, EN 2/3, EU 2/3, como en escritorio
            for color in ("#f85149", "#484f58"):
                self.assertEqual(sum(r.get("fill") == color for r in _rects(m)),
                                 sum(r.get("fill") == color for r in _rects(d)), (lang, color))

    def test_mobile_sheet_exp_bar_full_width(self):
        for lang in LANGS:
            svg = self.out[lang]["m-sheet.svg"]
            root = ET.fromstring(svg)
            clip = root.find(".//{*}clipPath[@id='xpclip']/{*}rect")
            fill = next(r for r in _rects(root) if r.get("fill") == "url(#xpcell)")
            inner = float(clip.get("width"))
            self.assertGreaterEqual(inner, M_W - 2 * 22)
            self.assertAlmostEqual(float(fill.get("width")) / inner,
                                   LIVE.active_days / LIVE.window_days, delta=10 / inner)
            self.assertNotIn(f"{LIVE.active_days}/{LIVE.window_days}", svg)

    def test_mobile_sheet_skill_bars_full_width(self):
        root = ET.fromstring(self.out["es"]["m-sheet.svg"])
        lit = _classed(root, "rect", "sg")
        self.assertEqual(len(lit), sum(segments(p) for _, p in SKILLS))
        x0 = min(float(r.get("x")) for r in lit)
        x1 = max(float(r.get("x")) + float(r.get("width")) for r in lit)
        self.assertGreaterEqual(x1 - x0, M_W - 2 * 24)          # la barra llena va de lado a lado
        names = [t for t in root.iter(SVG_NS + "text") if t.text in {n for n, _ in SKILLS}]
        self.assertEqual([t.text for t in names], [n for n, _ in SKILLS])

    # --- logros ---

    def test_mobile_achievements_same_toasts_in_order(self):
        for lang in LANGS:
            m = ET.fromstring(self.out[lang]["m-achievements.svg"])
            d = ET.fromstring(self.out[lang]["achievements.svg"])
            mt, dt = _classed(m, "g", "toast"), _classed(d, "g", "toast")
            self.assertEqual(len(mt), 7)
            self.assertEqual([_toast_label(g) for g in mt], [_toast_label(g) for g in dt], lang)
            self.assertEqual(mt[0].get("class"), "toast")       # la primera ya está en t = 0
            self.assertTrue(all("slide" in g.get("class") for g in mt[1:]))
            for g in mt:
                frame = _rects(g)[0]
                self.assertEqual(float(frame.get("width")), 400)
                self.assertLessEqual(len(list(g.iter(SVG_NS + "text"))), 3)   # aviso + 2 líneas
            self.assertIn(f"translateX({M_W}px)", self.out[lang]["m-achievements.svg"])

    def test_mobile_achievements_streak_rule(self):
        def last_label(live, lang):
            svg = render_all(lang, live)["m-achievements.svg"]
            return _toast_label(_classed(ET.fromstring(svg), "g", "toast")[-1])

        low = compute_stats(days_with_current_streak(2, longest=16))
        self.assertEqual(last_label(low, "es"), "Racha récord: 16 días seguidos")
        hi = compute_stats(days_with_current_streak(5, longest=5))
        self.assertEqual(last_label(hi, "en"), "Current streak: 5 days in a row")

    # --- inventario ---

    def test_mobile_inventory_three_columns_in_order(self):
        for lang in LANGS:
            root = ET.fromstring(self.out[lang]["m-inventory.svg"])
            labels = [t for t in root.iter(SVG_NS + "text") if t.text in INVENTORY]
            self.assertEqual([t.text for t in labels], INVENTORY)
            xs = sorted({float(t.get("x")) for t in labels})
            ys = sorted({float(t.get("y")) for t in labels})
            self.assertEqual((len(xs), len(ys)), (3, 4))
            order = sorted(labels, key=lambda t: (float(t.get("y")), float(t.get("x"))))
            self.assertEqual([t.text for t in order], INVENTORY)

    def test_mobile_inventory_cursor_steps_over_every_slot(self):
        svg = self.out["es"]["m-inventory.svg"]
        root = ET.fromstring(svg)
        cur = _classed(root, "g", "cur")
        self.assertEqual(len(cur), 1)
        self.assertIsNone(cur[0].get("transform"))               # base: sobre la casilla 0
        rule = re.search(r"\.cur\{animation:cur ([\d.]+)s steps\(1\)", svg)
        self.assertAlmostEqual(float(rule.group(1)), 1.2 * len(INVENTORY))
        frames = re.search(r"@keyframes cur\{(.*?)\}\}", svg).group(1)
        moves = re.findall(r"translate\((-?[\d.]+)px,(-?[\d.]+)px\)", frames)
        self.assertEqual(len(moves), len(INVENTORY) - 1)
        frame = _rects(cur[0])
        right = max(float(r.get("x")) + float(r.get("width")) for r in frame)
        for dx, _ in moves:                                      # el marco no se sale del lienzo
            self.assertLessEqual(right + float(dx), M_W)

    # --- tarjetas de misión ---

    def test_mobile_quest_cards(self):
        for lang in LANGS:
            heights = set()
            for q in QUESTS:
                name = f"m-quest-{q.slug}.svg"
                svg = self.out[lang][name]
                self.assertEqual(check_svg(svg), [], (lang, name))
                vb = ET.fromstring(svg).get("viewBox")
                self.assertTrue(vb.startswith(f"0 0 {CARD_W} "), (lang, name, vb))
                heights.add(_height(svg))
                # mismas palabras que la tarjeta de escritorio
                self.assertEqual(Counter(_words(svg)),
                                 Counter(_words(self.out[lang][f"quest-{q.slug}.svg"])),
                                 (lang, name))
                # el texto queda dentro del marco (borde interior en 10 y en 190)
                for text, left, right in _text_spans(svg):
                    self.assertGreaterEqual(left, 10, (lang, name, text))
                    self.assertLessEqual(right, CARD_W - 10, (lang, name, text))
                self.assertIn('class="blink"', svg)                       # el ▼
                self.assertEqual('fill="#fff2b3"' in svg, q.starred, (lang, name))   # la estrella
            # las cuatro igual de altas: en el móvil van de dos en dos y las filas cuadran
            self.assertEqual(len(heights), 1, (lang, heights))

    def test_mobile_quest_card_stacks_title_summary_stack_status(self):
        for lang in LANGS:
            for q in QUESTS:
                root = ET.fromstring(self.out[lang][f"m-quest-{q.slug}.svg"])
                texts = list(root.iter(SVG_NS + "text"))
                title = texts[0]
                self.assertEqual(title.text, q.title[lang])
                # ps2p 16 si cabe en 168; si no, vt323 de 26 o más
                if text_width(q.title[lang], "ps2p", 16) <= CARD_W - 32:
                    self.assertEqual((title.get("font-family"), title.get("font-size")),
                                     ("ps2p", "16"), (lang, q.slug))
                else:
                    self.assertEqual(title.get("font-family"), "vt323", (lang, q.slug))
                    self.assertGreaterEqual(float(title.get("font-size")), 26, (lang, q.slug))
                # el icono va encima del título
                icon = root.find(SVG_NS + "g")
                icon_bottom = max(float(r.get("y")) + float(r.get("height")) for r in _rects(icon))
                self.assertLess(icon_bottom, float(title.get("y")) - 16, (lang, q.slug))
                # de arriba abajo: título, resumen, stack y estado
                ys = [float(t.get("y")) for t in texts]
                self.assertEqual(ys, sorted(ys), (lang, q.slug))
                words = " ".join(t.text for t in texts[1:]).split()
                summary, stack = q.summary[lang].split(), quest_stack(q, lang).split()
                self.assertEqual(words, summary + stack + q.status[lang].split(), (lang, q.slug))
                # al partir la stack, el «·» se queda al final de la línea
                self.assertFalse([t.text for t in texts if t.text.startswith("·")], (lang, q.slug))

    # --- high score ---

    def test_mobile_highscore_26_weeks(self):
        days = _days(400)
        year = compute_stats(days)
        for live in (LIVE, year):
            for lang in LANGS:
                out = render_all(lang, live)
                svg = out["m-highscore.svg"]
                cells = svg.count('class="cell')
                self.assertGreater(cells, 0)
                self.assertLessEqual(cells, 26 * 7, lang)
                # los mismos días con el mismo color que en escritorio (los últimos)
                lv = lambda s: re.findall(r'class="cell (l\d)', s)  # noqa: E731
                self.assertEqual(lv(svg), lv(out["highscore.svg"])[-cells:], lang)
        svg = render_all("es", year)["m-highscore.svg"]
        self.assertEqual(svg.count('class="cell'), 7 * 25 + _row_of(days[-1][0]) + 1)
        xs = {float(x) for x in re.findall(r'class="cell[^"]*" x="([\d.]+)"', svg)}
        self.assertEqual(len(xs), 26)
        self.assertGreaterEqual(min(xs), 8)                             # dentro del marco
        self.assertLessEqual(max(xs) + 12, M_W - 8)

    def test_mobile_highscore_same_pacman_logic(self):
        for lang in LANGS:
            m, d = self.out[lang]["m-highscore.svg"], self.out[lang]["highscore.svg"]
            self.assertEqual(m.count('class="run'), 4)                  # Pac-Man y 3 fantasmas
            self.assertEqual(m.count('class="run'), d.count('class="run'))
            for rule in (".run{animation:run 24s linear infinite}",
                         ".face{animation:face 24s step-end infinite}",
                         "@keyframes run{", "@keyframes face{"):
                self.assertIn(rule, m, (lang, rule))
            # cada celda con contribuciones lleva su @keyframes, como en escritorio
            self.assertEqual(len(re.findall(r'class="cell l\d e\d+"', m)),
                             len(re.findall(r"@keyframes e\d+\{", m)))
            # serpentina: 7 filas, una parada al principio y otra al final de cada una
            run = re.search(r"@keyframes run\{(.*?)\}\}", m).group(1)
            self.assertEqual(len(re.findall(r"translate\(", run)), 2 * 7 + 1)

    def test_mobile_highscore_scores_stacked(self):
        for lang in LANGS:
            svg = self.out[lang]["m-highscore.svg"]
            c = COPY[lang]
            score = c["hs.score"].format(total=fmt_int(LIVE.total, lang))
            best = c["hs.best"].format(n=fmt_int(LIVE.best_day, lang))
            texts = {t.text: t for t in ET.fromstring(svg).iter(SVG_NS + "text")}
            self.assertLess(float(texts[score].get("y")), float(texts[best].get("y")))
            self.assertEqual((texts[best].get("font-family"), texts[best].get("font-size")),
                             ("vt323", "32"))
            # la rejilla empieza bajo el récord
            first = min(float(y) for y in re.findall(r'class="cell[^"]*" x="[\d.]+" y="([\d.]+)"', svg))
            self.assertGreater(first, float(texts[best].get("y")))

    def test_mobile_start_splits_into_balanced_lines(self):
        texts = _texts(self.out["es"]["m-start.svg"])
        self.assertEqual(texts[:2], ["PULSA START PARA", "HABLAR CONMIGO"])
        texts = _texts(self.out["en"]["m-start.svg"])
        self.assertEqual(texts[:2], ["PRESS START TO", "GET IN TOUCH"])


def _days(n: int) -> list[tuple[str, int]]:
    """`n` días seguidos con contribuciones variadas (y algún cero)."""
    start = date(2025, 9, 1)
    return [((start + timedelta(days=i)).isoformat(), (i * 7) % 5 * (i % 3)) for i in range(n)]


def _row_of(iso: str) -> int:
    return (date.fromisoformat(iso).weekday() + 1) % 7          # domingo = 0, arriba


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

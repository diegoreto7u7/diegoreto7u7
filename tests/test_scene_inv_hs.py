import re
import unittest
import xml.etree.ElementTree as ET
from datetime import date, timedelta

from gen.content import COPY, INVENTORY, LANGS, fmt_int
from gen.live import LiveStats, compute_stats
from gen.scenes import highscore, inventory
from gen.scenes.common import header
from gen.svgcheck import check_svg
from tests.helpers import LIVE


def _year(last: date, n_days: int, count=lambda i: 1 + i % 9) -> list[tuple[str, int]]:
    """Calendario de n_days días que acaba en `last`, con contribuciones todos los días."""
    first = last - timedelta(days=n_days - 1)
    return [((first + timedelta(days=i)).isoformat(), count(i)) for i in range(n_days)]


def _cells(svg: str) -> list[ET.Element]:
    root = ET.fromstring(svg)
    return [e for e in root.findall(".//{*}rect") if "cell" in (e.get("class") or "").split()]


def _eat_pct(svg: str) -> dict[str, float]:
    """Porcentaje del ciclo en que se come cada celda, por nombre de @keyframes."""
    return {name: float(p) for name, p in re.findall(r"@keyframes (e\d+)\{([\d.]+)%", svg)}


class TestSceneInventory(unittest.TestCase):
    def test_inventory_items(self):
        svg = inventory.render("en", LIVE)["inventory.svg"]
        for name in INVENTORY:
            self.assertIn(f">{name}<", svg)
        self.assertEqual(check_svg(svg), [])

    def test_inventory_both_langs(self):
        for lang in LANGS:
            svg = inventory.render(lang, LIVE)["inventory.svg"]
            self.assertEqual(check_svg(svg), [])
            self.assertIn(header(COPY[lang]["inv.title"]), svg)
            self.assertIn('width="840"', svg)

    def test_cursor_jumps_with_steps_and_rests_on_slot_0(self):
        svg = inventory.render("es", LIVE)["inventory.svg"]
        root = ET.fromstring(svg)
        cur = [g for g in root.findall(".//{*}g") if g.get("class") == "cur"]
        self.assertEqual(len(cur), 1)
        self.assertIsNone(cur[0].get("transform"))       # en la base, sobre la casilla 0
        rule = re.search(r"\.cur\{animation:cur ([\d.]+)s steps\(1\)", svg)
        self.assertIsNotNone(rule)
        self.assertAlmostEqual(float(rule.group(1)), 1.2 * len(INVENTORY))
        # una parada por casilla: la 0 es la base y las otras nueve van en el @keyframes
        frames = re.search(r"@keyframes cur\{(.*?)\}\}", svg).group(1)
        self.assertEqual(frames.count("transform:translate("), len(INVENTORY) - 1)


class TestSceneHighscore(unittest.TestCase):
    def test_highscore_grid_and_scores(self):
        svg = highscore.render("es", LIVE)["highscore.svg"]
        self.assertEqual(check_svg(svg), [])
        self.assertIn("1UP " + fmt_int(LIVE.total, "es"), svg)
        self.assertIn(f"RÉCORD {LIVE.best_day}/DÍA", svg)
        self.assertEqual(svg.count('class="cell'), min(len(LIVE.days), 53 * 7))

    def test_scoreboard_in_vt323_for_accented_capitals(self):
        # Press Start 2P dibuja É/Í con altura de minúscula; VT323 tiene mayúsculas acentuadas de verdad
        for lang in LANGS:
            root = ET.fromstring(highscore.render(lang, LIVE)["highscore.svg"])
            labels = {"1UP": None, "RÉCORD" if lang == "es" else "BEST": None}
            for t in root.findall(".//{*}text"):
                for k in labels:
                    if t.text.startswith(k):
                        labels[k] = t
            for k, t in labels.items():
                self.assertIsNotNone(t, (lang, k))
                self.assertEqual(t.get("font-family"), "vt323", (lang, k))
                self.assertGreaterEqual(float(t.get("font-size")), 26, (lang, k))

    def test_highscore_large_numbers_fit(self):
        big = LiveStats(days=LIVE.days, total=123456, best_day=9999, active_days=1,
                        window_days=1, current_streak=0, longest_streak=0)
        highscore.render("en", big)  # no lanza

    def test_highscore_both_langs(self):
        for lang in LANGS:
            svg = highscore.render(lang, LIVE)["highscore.svg"]
            self.assertEqual(check_svg(svg), [])
            self.assertIn(header(COPY[lang]["hs.title"]), svg)
        self.assertIn(f"BEST {LIVE.best_day}/DAY", highscore.render("en", LIVE)["highscore.svg"])

    def test_levels_use_quartiles_of_active_days(self):
        self.assertEqual(highscore.levels([0, 1, 2, 3, 4, 5, 6, 7, 8]),
                         [0, 1, 1, 1, 2, 2, 3, 3, 4])
        self.assertEqual(highscore.levels([0, 0, 0]), [0, 0, 0])

    def test_last_53_weeks_sunday_on_top(self):
        last = date(2026, 10, 27)                       # martes
        live = compute_stats(_year(last, 400))
        cells = _cells(highscore.render("es", live)["highscore.svg"])
        # 52 semanas completas más domingo, lunes y martes de la semana en curso
        self.assertEqual(len(cells), 52 * 7 + 3)
        xs = sorted({float(c.get("x")) for c in cells})
        ys = sorted({float(c.get("y")) for c in cells})
        self.assertEqual((len(xs), len(ys)), (53, 7))
        self.assertEqual(xs[1] - xs[0], 15)              # celda de 12 + separación de 3
        self.assertEqual(ys[1] - ys[0], 15)
        # la primera celda es un domingo (fila de arriba) y la última, el martes (tercera fila)
        self.assertEqual((float(cells[0].get("x")), float(cells[0].get("y"))), (xs[0], ys[0]))
        self.assertEqual((float(cells[-1].get("x")), float(cells[-1].get("y"))), (xs[-1], ys[2]))

    def test_eat_order_follows_serpentine(self):
        live = compute_stats(_year(date(2026, 10, 24), 371))   # 53 semanas completas
        svg = highscore.render("en", live)["highscore.svg"]
        pct = _eat_pct(svg)
        grid: dict[tuple[float, float], float] = {}
        for c in _cells(svg):
            name = next(k for k in c.get("class").split() if re.fullmatch(r"e\d+", k))
            grid[(float(c.get("y")), float(c.get("x")))] = pct[name]
        ys = sorted({y for y, _ in grid})
        order = []
        for r, y in enumerate(ys):
            row = [grid[k] for k in sorted(k for k in grid if k[0] == y)]
            order += row if r % 2 == 0 else row[::-1]    # fila par →, fila impar ←
        self.assertEqual(order, sorted(order))
        self.assertEqual(len(set(order)), len(order))
        self.assertLess(order[-1], 100)

    def test_only_cells_with_contributions_are_eaten(self):
        svg = highscore.render("es", LIVE)["highscore.svg"]
        eaten = len(_eat_pct(svg))
        self.assertEqual(eaten, LIVE.active_days)
        self.assertIn("opacity:.06", svg)

    def test_full_year_fits_and_is_deterministic(self):
        live = compute_stats(_year(date(2026, 10, 27), 400, count=lambda i: 1 + i * 7 % 150))
        for lang in LANGS:
            svg = highscore.render(lang, live)["highscore.svg"]
            self.assertEqual(check_svg(svg), [])
            self.assertLess(len(svg.encode()), 500_000)
            self.assertEqual(svg, highscore.render(lang, live)["highscore.svg"])

    def test_pacman_and_three_ghosts(self):
        svg = highscore.render("es", LIVE)["highscore.svg"]
        for color in ("#f85149", "#ff9bce", "#56d4dd"):
            self.assertIn(f'fill="{color}"', svg)
        self.assertIn("@keyframes run{", svg)
        self.assertIn("scale(-1,1)", svg)               # mira a la izquierda en las filas de vuelta
        lags = sorted(float(d) for d in re.findall(r"\.g\d,\.g\d \.face\{animation-delay:(-[\d.]+)s", svg))
        self.assertEqual(lags, [-23.2, -22.4, -21.6])   # 0,8 s de retraso entre uno y otro


if __name__ == "__main__":
    unittest.main()

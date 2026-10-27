import contextlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import urllib.error
from datetime import date, timedelta
from pathlib import Path
from unittest import mock

from gen.build import build
from gen.live import compute_stats, fetch_calendar, load_live, streak_badge

FIXTURE = Path(__file__).parent / "fixtures" / "graphql_calendar.json"
ROOT = Path(__file__).resolve().parent.parent


def days(counts, start=date(2026, 1, 1)):
    return [((start + timedelta(i)).isoformat(), n) for i, n in enumerate(counts)]


class FakeResponse:
    def __init__(self, body):
        self.body = body

    def read(self):
        return self.body

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def fake_opener(body):
    seen = []

    def opener(req, timeout=None):
        seen.append(req)
        return FakeResponse(body)

    opener.seen = seen
    return opener


def failing_opener(req, timeout=None):
    raise urllib.error.URLError("sin red")


def drop_body(n=25):
    """Respuesta de GraphQL con un solo día de `n` contribuciones."""
    return json.dumps({"data": {"user": {"contributionsCollection": {"contributionCalendar": {
        "weeks": [{"contributionDays": [{"date": "2026-01-02", "contributionCount": n}]}]}}}}}).encode()


class StatsTest(unittest.TestCase):
    def test_stats_basic(self):
        s = compute_stats(days([3, 0, 5, 5, 0, 2, 7]))
        self.assertEqual((s.total, s.best_day, s.active_days, s.window_days, s.longest_streak), (22, 7, 5, 7, 2))

    def test_current_streak_ignores_empty_today(self):
        self.assertEqual(compute_stats(days([2, 0, 1, 1, 1, 0])).current_streak, 3)

    def test_current_streak_counts_today(self):
        self.assertEqual(compute_stats(days([2, 0, 1, 1, 1, 1])).current_streak, 4)

    def test_streak_badge_threshold(self):
        two = compute_stats(days([1] * 16 + [0, 1, 1]))
        self.assertEqual((two.current_streak, two.longest_streak), (2, 16))
        self.assertEqual(streak_badge(two), ("longest", 16))
        three = compute_stats(days([1] * 16 + [0, 1, 1, 1]))
        self.assertEqual(streak_badge(three), ("current", 3))


class FetchTest(unittest.TestCase):
    def test_fetch_parses_graphql(self):
        op = fake_opener(FIXTURE.read_bytes())
        got = fetch_calendar("u", "t", opener=op)
        self.assertEqual(got[:2], [("2025-10-26", 0), ("2025-10-27", 4)])
        self.assertEqual(len(got), 5)
        req = op.seen[0]
        self.assertEqual(req.full_url, "https://api.github.com/graphql")
        self.assertEqual(req.get_header("Authorization"), "bearer t")
        self.assertEqual(json.loads(req.data)["variables"], {"login": "u"})

    def test_graphql_errors_raise(self):
        with self.assertRaises(ValueError):
            fetch_calendar("u", "t", opener=fake_opener(b'{"errors":[{"message":"x"}]}'))


class LoadTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "live.json"

    def write_cache(self, counts):
        self.path.write_text(json.dumps({"login": "u", "days": [list(d) for d in days(counts)]}))

    def test_load_live_uses_cache_without_refresh(self):
        self.write_cache([1, 2, 3])
        s = load_live(self.path, False, None, opener=failing_opener)
        self.assertEqual(s.total, 6)

    def test_load_live_keeps_cache_on_network_error(self):
        self.write_cache([1, 2, 3])
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            s = load_live(self.path, True, "t", opener=failing_opener)
        self.assertEqual(s.total, 6)
        self.assertIn("caché", err.getvalue())

    def test_refresh_writes_deterministic_cache(self):
        s = load_live(self.path, True, "t", login="u", opener=fake_opener(FIXTURE.read_bytes()))
        self.assertEqual(s.total, 12)
        data = json.loads(self.path.read_text())
        self.assertEqual(set(data), {"login", "days"})
        self.assertEqual(data["days"][1], ["2025-10-27", 4])

    def test_refresh_refuses_big_drop(self):
        self.write_cache([4000])
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            s = load_live(self.path, True, "t", opener=fake_opener(drop_body()))
        self.assertEqual(s.total, 4000)
        self.assertEqual(json.loads(self.path.read_text())["days"][0][1], 4000)
        self.assertIn("caché", err.getvalue())

    def test_load_live_without_cache_and_error_exits(self):
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                load_live(self.path, True, "t", opener=failing_opener)
            with self.assertRaises(SystemExit):
                load_live(self.path, False, None)

    def test_lenient_refresh_without_token_warns_and_uses_cache(self):
        self.write_cache([1, 2, 3])
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            s = load_live(self.path, True, None, opener=failing_opener)
        self.assertEqual(s.total, 6)
        self.assertIn("GITHUB_TOKEN", err.getvalue())


class StrictLoadTest(unittest.TestCase):
    """Modo de `gen build --refresh` (la Action): si no se puede refrescar, falla en rojo."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "live.json"
        self.path.write_text(json.dumps({"login": "u", "days": [list(d) for d in days([4000, 1, 2])]}))
        self.before = self.path.read_bytes()

    def strict_exit(self, token, opener) -> str:
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            with self.assertRaises(SystemExit) as cm:
                load_live(self.path, True, token, opener=opener, strict=True)
        self.assertEqual(cm.exception.code, 1)
        self.assertEqual(self.path.read_bytes(), self.before)   # la caché queda intacta
        return err.getvalue()

    def test_strict_network_error_exits_and_keeps_cache(self):
        self.assertIn("no se pudo descargar", self.strict_exit("t", failing_opener))

    def test_strict_graphql_error_exits(self):
        self.assertIn("GraphQL", self.strict_exit("t", fake_opener(b'{"errors":[{"message":"x"}]}')))

    def test_strict_refused_drop_exits(self):
        self.assertIn("menos de la mitad", self.strict_exit("t", fake_opener(drop_body())))

    def test_strict_missing_token_exits_without_fetching(self):
        op = fake_opener(FIXTURE.read_bytes())
        self.assertIn("GITHUB_TOKEN", self.strict_exit(None, op))
        self.assertEqual(op.seen, [])

    def test_strict_success_writes_cache(self):
        self.path.write_text(json.dumps({"login": "u", "days": [list(d) for d in days([1, 2, 3])]}))
        s = load_live(self.path, True, "t", login="u", opener=fake_opener(FIXTURE.read_bytes()),
                      strict=True)
        self.assertEqual(s.total, 12)
        self.assertEqual(json.loads(self.path.read_text())["days"][1], ["2025-10-27", 4])

    def test_strict_build_writes_nothing_on_failed_fetch(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d)
            shutil.copytree(ROOT / "data", out / "data")
            cache = (out / "data" / "live.json").read_bytes()
            with mock.patch("gen.live.fetch_calendar", side_effect=urllib.error.URLError("sin red")):
                with contextlib.redirect_stderr(io.StringIO()):
                    with self.assertRaises(SystemExit) as cm:
                        build(out, refresh=True, token="t", strict=True)
            self.assertEqual(cm.exception.code, 1)
            self.assertEqual((out / "data" / "live.json").read_bytes(), cache)
            self.assertFalse((out / "README.md").exists())
            self.assertFalse((out / "assets").exists())

    def test_cli_refresh_without_token_exits_nonzero(self):
        env = {k: v for k, v in os.environ.items() if k != "GITHUB_TOKEN"}
        with tempfile.TemporaryDirectory() as d:
            out = Path(d)
            shutil.copytree(ROOT / "data", out / "data")
            cache = (out / "data" / "live.json").read_bytes()
            res = subprocess.run([sys.executable, "-m", "gen", "build", "--refresh", "--out", d],
                                 cwd=ROOT, env=env, capture_output=True, text=True, timeout=120)
            self.assertNotEqual(res.returncode, 0)
            self.assertIn("GITHUB_TOKEN", res.stderr)
            self.assertEqual((out / "data" / "live.json").read_bytes(), cache)
            self.assertFalse((out / "README.md").exists())


if __name__ == "__main__":
    unittest.main()

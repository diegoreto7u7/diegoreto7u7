import contextlib
import io
import json
import tempfile
import unittest
import urllib.error
from datetime import date, timedelta
from pathlib import Path

from gen.live import compute_stats, fetch_calendar, load_live, streak_badge

FIXTURE = Path(__file__).parent / "fixtures" / "graphql_calendar.json"


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
        body = json.dumps({"data": {"user": {"contributionsCollection": {"contributionCalendar": {
            "weeks": [{"contributionDays": [{"date": "2026-01-02", "contributionCount": 25}]}]}}}}}).encode()
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            s = load_live(self.path, True, "t", opener=fake_opener(body))
        self.assertEqual(s.total, 4000)
        self.assertEqual(json.loads(self.path.read_text())["days"][0][1], 4000)
        self.assertIn("caché", err.getvalue())

    def test_load_live_without_cache_and_error_exits(self):
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                load_live(self.path, True, "t", opener=failing_opener)
            with self.assertRaises(SystemExit):
                load_live(self.path, False, None)


if __name__ == "__main__":
    unittest.main()

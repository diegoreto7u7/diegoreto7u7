"""Calendario de contribuciones: descarga, caché y estadísticas."""

import json
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

API = "https://api.github.com/graphql"
QUERY = (
    "query($login:String!){user(login:$login){contributionsCollection{"
    "contributionCalendar{weeks{contributionDays{date contributionCount}}}}}}"
)
MIN_KEEP_RATIO = 0.5


@dataclass(frozen=True)
class LiveStats:
    days: tuple[tuple[str, int], ...]
    total: int
    best_day: int
    active_days: int
    window_days: int
    current_streak: int
    longest_streak: int


def compute_stats(days: list[tuple[str, int]]) -> LiveStats:
    counts = [n for _, n in days]
    longest = run = 0
    for n in counts:
        run = run + 1 if n > 0 else 0
        longest = max(longest, run)
    trimmed = counts[:-1] if counts and counts[-1] == 0 else counts  # hoy aún sin actividad
    current = 0
    for n in reversed(trimmed):
        if n <= 0:
            break
        current += 1
    return LiveStats(
        days=tuple((d, n) for d, n in days),
        total=sum(counts),
        best_day=max(counts, default=0),
        active_days=sum(1 for n in counts if n > 0),
        window_days=len(counts),
        current_streak=current,
        longest_streak=longest,
    )


def streak_badge(s: LiveStats) -> tuple[str, int]:
    if s.current_streak >= 3:
        return ("current", s.current_streak)
    return ("longest", s.longest_streak)


def fetch_calendar(login: str, token: str, opener=urllib.request.urlopen) -> list[tuple[str, int]]:
    body = json.dumps({"query": QUERY, "variables": {"login": login}}).encode()
    req = urllib.request.Request(
        API,
        data=body,
        method="POST",
        headers={
            "Authorization": f"bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "diegoreto7u7-profile-generator",
        },
    )
    with opener(req, timeout=30) as resp:
        payload = json.loads(resp.read())
    if payload.get("errors"):
        raise ValueError(f"error de GraphQL: {payload['errors']}")
    try:
        weeks = payload["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
        days = [
            (d["date"], int(d["contributionCount"]))
            for w in weeks
            for d in w["contributionDays"]
        ]
    except (KeyError, TypeError) as e:
        raise ValueError(f"respuesta inesperada: {e!r}") from e
    if not days:
        raise ValueError("calendario vacío")
    return days


def _read_cache(path: Path) -> list[tuple[str, int]] | None:
    if not path.exists():
        return None
    return [(d, int(n)) for d, n in json.loads(path.read_text())["days"]]


def load_live(
    path: Path,
    refresh: bool,
    token: str | None,
    login: str = "diegoreto7u7",
    opener=urllib.request.urlopen,
) -> LiveStats:
    cached = _read_cache(path)
    if refresh and token:
        try:
            fresh = fetch_calendar(login, token, opener=opener)
        except (urllib.error.URLError, OSError, ValueError) as e:
            if cached is None:
                print(f"no se pudo descargar el calendario y no hay caché: {e}", file=sys.stderr)
                raise SystemExit(1)
            print(f"aviso: descarga fallida ({e}); se usa la caché", file=sys.stderr)
        else:
            fresh_total = sum(n for _, n in fresh)
            if cached is not None and fresh_total < MIN_KEEP_RATIO * sum(n for _, n in cached):
                print(
                    f"aviso: la descarga suma {fresh_total}, muy por debajo de la caché; se conserva la caché",
                    file=sys.stderr,
                )
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                rows = ",\n".join(f"  {json.dumps([d, n])}" for d, n in fresh)
                path.write_text(f'{{"login": {json.dumps(login)},\n "days": [\n{rows}\n ]}}\n')
                cached = fresh
    if cached is None:
        print(f"no hay caché en {path}; ejecuta con --refresh y GITHUB_TOKEN", file=sys.stderr)
        raise SystemExit(1)
    return compute_stats(cached)

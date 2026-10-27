"""Datos fijos y deterministas para los tests de las escenas."""

from datetime import date, timedelta

from gen.live import compute_stats

_START = date(2026, 9, 27)
_COUNTS = [3, 0, 12, 7, 0, 0, 25, 143, 9, 4, 0, 18, 6, 2, 0,
           31, 11, 0, 8, 5, 14, 0, 0, 22, 3, 7, 16, 1, 9, 4]

DAYS = [((_START + timedelta(days=i)).isoformat(), n) for i, n in enumerate(_COUNTS)]
LIVE = compute_stats(DAYS)

# Un año largo (400 días) fijo, sin fechas relativas a hoy: ejercita los recortes anuales
# (rejilla del high score, marcadores del año) que los 30 días de LIVE no alcanzan.
_YEAR_START = date(2025, 3, 3)
YEAR_DAYS = [((_YEAR_START + timedelta(days=i)).isoformat(),
              0 if i % 7 in (2, 5) or i % 29 == 0 else (i * 7) % 23 + (140 if i == 250 else 0))
             for i in range(400)]
YEAR_LIVE = compute_stats(YEAR_DAYS)


def days_with_current_streak(current: int, longest: int) -> list[tuple[str, int]]:
    """Calendario cuya racha más larga es `longest` y cuya racha actual (hasta hoy) es `current`."""
    counts = [2] * longest + [0] * 3 + [1] * current
    start = date(2026, 1, 1)
    return [((start + timedelta(days=i)).isoformat(), n) for i, n in enumerate(counts)]

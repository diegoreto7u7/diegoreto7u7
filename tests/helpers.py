"""Datos fijos y deterministas para los tests de las escenas."""

from datetime import date, timedelta

from gen.live import compute_stats

_START = date(2026, 9, 27)
_COUNTS = [3, 0, 12, 7, 0, 0, 25, 143, 9, 4, 0, 18, 6, 2, 0,
           31, 11, 0, 8, 5, 14, 0, 0, 22, 3, 7, 16, 1, 9, 4]

DAYS = [((_START + timedelta(days=i)).isoformat(), n) for i, n in enumerate(_COUNTS)]
LIVE = compute_stats(DAYS)

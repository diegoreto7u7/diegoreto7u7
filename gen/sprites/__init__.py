"""Sprites pixel en ASCII: cada uno es (filas, paleta); los animados, (fotograma_a, fotograma_b, paleta).

En las filas, «.» es transparente y cada otro carácter es una clave de la paleta.
"""


def shade(color: str, amount: float) -> str:
    """Aclara (amount > 0, hacia blanco) u oscurece (amount < 0, hacia negro) un color #rrggbb."""
    rgb = [int(color[i:i + 2], 16) for i in (1, 3, 5)]
    target = 255 if amount > 0 else 0
    mixed = [round(c + (target - c) * abs(amount)) for c in rgb]
    return "#" + "".join(f"{c:02x}" for c in mixed)

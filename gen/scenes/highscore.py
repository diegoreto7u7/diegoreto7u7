"""High score (highscore.svg): Pac-Man y tres fantasmas se comen el calendario de contribuciones.

Rejilla: las últimas 53 semanas en columnas de 7 días, con el domingo arriba como en GitHub.
Pac-Man la recorre en serpentina (fila 0 →, fila 1 ←, …) en un ciclo de 24 s, mirando hacia
donde va; cada celda con contribuciones se apaga al pasar él y vuelve al empezar el ciclo.
Los fantasmas siguen el mismo camino, 0,8 s detrás uno de otro.

Estado base (lo que queda con movimiento reducido): rejilla entera, Pac-Man esperando en la
primera casilla y los fantasmas en fila en el centro del marcador.

Dos maquetaciones con el mismo dibujo (`Layout`): en escritorio (highscore.svg, 840 de ancho) las
53 semanas y el marcador en una línea, con los fantasmas en medio; en el móvil (m-highscore.svg,
420 de ancho) las últimas 26 semanas, con el récord en una segunda línea y los fantasmas esperando
a su izquierda. Los marcadores son siempre los del año.
"""

from dataclasses import dataclass
from datetime import date, timedelta

from gen.content import COPY, fmt_int
from gen.live import LiveStats
from gen.pixel import sprite, two_frames
from gen.scenes.common import BLINK_CSS, MOBILE_W, header
from gen.sprites.misc import PAC, ghost
from gen.svg import document, pct, rect, text

W = 840
BG, NAVY, WALL, VOID = "#0d1117", "#1f2a6b", "#2f3fb0", "#010409"
SCORE, BEST = "#f0f6fc", "#f85149"
LEVELS = ("#161b22", "#0e4429", "#006d32", "#26a641", "#39d353")
GHOSTS = ("#f85149", "#ff9bce", "#56d4dd")

WEEKS, DAYS = 53, 7
CELL, GAP = 12, 3
PITCH = CELL + GAP
FRAME_Y = 56
PAD = 24                    # del borde del lienzo al marcador (8 de marco + 16 de margen)
SCORE_BASE = FRAME_Y + 40   # línea base del marcador
# El marcador va en VT323: Press Start 2P dibuja É/Í con altura de minúscula («RéCORD 143/DíA»).
SCORE_FONT, SCORE_SIZE = "vt323", 32
SCORE_CAP = 0.56 * SCORE_SIZE   # altura de las mayúsculas (capHeight 560/1000 en el TTF)
SCORE_LINE = 36             # de la línea del marcador a la del récord, si van apiladas
BOTTOM = 16 + 8             # bajo la rejilla: margen y marco
SPRITE_SCALE = 2            # Pac-Man y fantasmas: 7 × 7 a escala 2 = 14, algo más que una celda
HALF = len(PAC[0][0]) * SPRITE_SCALE // 2
GHOST_SPACING = 20          # fantasmas en fila en el centro del marcador (estado base)
LINEUP_HALF = GHOST_SPACING * (len(GHOSTS) - 1) // 2 + HALF

CYCLE = 24.0                # segundos por vuelta
RUN = 21.0                  # Pac-Man recorre la rejilla en 21 s; el último fantasma acaba a los 23,4
LAG = 0.8                   # retraso de cada fantasma respecto al anterior
EATEN = ".06"


@dataclass(frozen=True)
class Layout:
    """Lienzo de `w` de ancho con la rejilla de las últimas `weeks` semanas.

    El marcador (1UP) va a la izquierda de la primera línea y el récord, alineado a la derecha,
    `best_dy` más abajo (0: en la misma línea). Los fantasmas esperan en fila con el centro en
    `lineup_cx`, `lineup_dy` por debajo de la primera línea. La rejilla empieza bajo el récord.
    """
    w: int
    weeks: int
    best_dy: int
    lineup_cx: int
    lineup_dy: int

    @property
    def grid_y(self) -> int:
        return SCORE_BASE + self.best_dy + 14

    @property
    def score_w(self) -> int:
        """Ancho del marcador: hasta la fila de fantasmas si va en su línea; si no, todo."""
        end = self.lineup_cx - LINEUP_HALF - 16 if self.lineup_dy == 0 else self.w - PAD
        return end - PAD

    @property
    def best_w(self) -> int:
        """Ancho del récord: desde la fila de fantasmas si va en su línea; si no, todo."""
        start = self.lineup_cx + LINEUP_HALF + 16 if self.lineup_dy == self.best_dy else PAD
        return self.w - PAD - start


DESKTOP = Layout(w=W, weeks=WEEKS, best_dy=0, lineup_cx=W // 2, lineup_dy=0)
MOBILE = Layout(w=MOBILE_W, weeks=26, best_dy=SCORE_LINE, lineup_cx=PAD + LINEUP_HALF,
                lineup_dy=SCORE_LINE)


def levels(counts: list[int]) -> list[int]:
    """Nivel 0–4 de cada día: 0 sin contribuciones; 1–4 según los cuartiles de los días activos."""
    active = sorted(n for n in counts if n > 0)
    if not active:
        return [0] * len(counts)
    q = [active[int(len(active) * f)] for f in (0.25, 0.5, 0.75)]
    return [0 if n == 0 else 1 + sum(n > t for t in q) for n in counts]


def _row(d: date) -> int:
    return (d.weekday() + 1) % 7            # domingo = 0, arriba


def _layout(days, weeks: int) -> tuple[list[tuple[int, int, int, int]], int]:
    """(columna, fila, contribuciones, nivel) de cada día de las últimas `weeks` semanas y nº de
    columnas.

    El nivel sale siempre de las 53 semanas (el año, como en GitHub): así un día tiene el mismo
    color en las dos rejillas.
    """
    dated = [(date.fromisoformat(d), n) for d, n in days]
    last = dated[-1][0]

    def first_sunday(w: int) -> date:
        return last - timedelta(days=_row(last) + 7 * (w - 1))

    year = [(d, n) for d, n in dated if d >= first_sunday(WEEKS)]
    kept = [(d, n, lv) for (d, n), lv in zip(year, levels([n for _, n in year]))
            if d >= first_sunday(weeks)]
    start = kept[0][0] - timedelta(days=_row(kept[0][0]))
    cells = [((d - start).days // 7, _row(d), n, lv) for d, n, lv in kept]
    return cells, cells[-1][0] + 1


class _Path:
    """Serpentina sobre 7 filas × `cols` columnas, medida en pasos de celda."""

    def __init__(self, cols: int, x0: int, grid_y: int):
        self.cols, self.x0, self.grid_y = cols, x0, grid_y
        self.length = DAYS * cols - 1           # 7 filas de cols − 1 pasos y 6 bajadas

    def distance(self, col: int, row: int) -> int:
        along = col if row % 2 == 0 else self.cols - 1 - col
        return row * self.cols + along

    def time(self, dist: int) -> float:
        return dist / self.length * RUN

    def center(self, col: int, row: int) -> tuple[int, int]:
        return self.x0 + col * PITCH + CELL // 2, self.grid_y + row * PITCH + CELL // 2


def _grid(cells, path: _Path) -> tuple[str, str]:
    """Celdas coloreadas por nivel; las que tienen contribuciones llevan su propio @keyframes."""
    out, css = [], []
    for col, row, n, level in cells:
        x, y = path.x0 + col * PITCH, path.grid_y + row * PITCH
        cls = f"cell l{level}"
        if n > 0:
            i = path.distance(col, row)
            cls += f" e{i}"
            at = pct(path.time(i), CYCLE, trim=True)
            css.append(f".e{i}{{animation-name:e{i}}}@keyframes e{i}{{{at}%{{opacity:{EATEN}}}}}")
        out.append(f'<rect class="{cls}" x="{x}" y="{y}" width="{CELL}" height="{CELL}"/>')
    base = (f".cell{{animation:{CYCLE:g}s step-end infinite}}"
            + "".join(f".l{i}{{fill:{c}}}" for i, c in enumerate(LEVELS)))
    return "".join(out), base + "".join(css)


def _runners(path: _Path, lay: Layout) -> tuple[str, str]:
    """Pac-Man y los fantasmas: grupo exterior que se desplaza y grupo interior que se da la vuelta o se oculta.

    Los sprites se dibujan centrados en el origen, así el giro scale(-1,1) es sobre sí mismos.
    """
    start = path.center(0, 0)
    open_, shut, pal = PAC
    pac = two_frames(open_, shut, pal, -HALF, -HALF, SPRITE_SCALE)
    svg = [f'<g class="run" transform="translate({start[0]} {start[1]})">'
           f'<g class="face">{pac}</g></g>']
    lineup_x = lay.lineup_cx - LINEUP_HALF + HALF
    delays = []
    for k, color in enumerate(GHOSTS, 1):
        rows, gpal = ghost(color)
        # a media altura de las mayúsculas del marcador
        gx = lineup_x + (k - 1) * GHOST_SPACING
        gy = SCORE_BASE + lay.lineup_dy - round(SCORE_CAP / 2)
        svg.insert(0, f'<g class="run g{k}" transform="translate({gx} {gy})">'
                      f'<g class="face">{sprite(rows, gpal, -HALF, -HALF, SPRITE_SCALE)}</g></g>')
        # retraso negativo: en t = 0 cada fantasma está en el tramo final (oculto) de su vuelta
        delays.append(f".g{k},.g{k} .face{{animation-delay:-{CYCLE - k * LAG:g}s}}")

    stops, faces = [], []
    for row in range(DAYS):
        first, last = (0, path.cols - 1) if row % 2 == 0 else (path.cols - 1, 0)
        for col in (first, last):
            x, y = path.center(col, row)
            at = pct(path.time(path.distance(col, row)), CYCLE, trim=True)
            stops.append(f"{at}%{{transform:translate({x}px,{y}px)}}")
        if row:
            flip = "scale(-1,1)" if row % 2 else "none"
            at = pct(path.time(path.distance(first, row)), CYCLE, trim=True)
            faces.append(f"{at}%{{transform:{flip}}}")
    end = path.center(path.cols - 1, DAYS - 1)
    stops.append(f"to{{transform:translate({end[0]}px,{end[1]}px)}}")
    faces.append(f"{pct(RUN, CYCLE, trim=True)}%{{opacity:0}}")
    css = ([f".run{{animation:run {CYCLE:g}s linear infinite}}",
            f".face{{animation:face {CYCLE:g}s step-end infinite}}"]
           + delays
           + ["@keyframes run{" + "".join(stops) + "}",
              "@keyframes face{" + "".join(faces) + "}"])
    return "".join(svg), "".join(css)


def _frame(h: int, w: int) -> str:
    """Marco de laberinto: azul marino por fuera, hueco negro y línea azul viva por dentro."""
    y = FRAME_Y
    return (rect(0, y, w, h, NAVY) + rect(4, y + 4, w - 8, h - 8, VOID)
            + rect(6, y + 6, w - 12, h - 12, WALL) + rect(8, y + 8, w - 16, h - 16, VOID))


def _highscore(lang: str, live: LiveStats, lay: Layout) -> str:
    c = COPY[lang]
    cells, cols = _layout(live.days, lay.weeks)
    path = _Path(cols, (lay.w - (cols * PITCH - GAP)) // 2, lay.grid_y)
    grid, grid_css = _grid(cells, path)
    runners, runners_css = _runners(path, lay)
    h = lay.grid_y + DAYS * PITCH - GAP + BOTTOM
    score = (text(PAD, SCORE_BASE, c["hs.score"].format(total=fmt_int(live.total, lang)),
                  SCORE_FONT, SCORE_SIZE, SCORE, max_width=lay.score_w)
             + text(lay.w - PAD, SCORE_BASE + lay.best_dy,
                    c["hs.best"].format(n=fmt_int(live.best_day, lang)),
                    SCORE_FONT, SCORE_SIZE, BEST, anchor="end", max_width=lay.best_w))
    body = header(c["hs.title"], lay.w) + _frame(h - FRAME_Y, lay.w) + score + grid + runners
    title = c["alt.highscore"].format(total=fmt_int(live.total, lang),
                                      best=fmt_int(live.best_day, lang))
    return document(lay.w, h, title, body, css=BLINK_CSS + grid_css + runners_css,
                    fonts=("ps2p", "vt323"), bg=BG)


def render(lang: str, live: LiveStats) -> dict[str, str]:
    return {"highscore.svg": _highscore(lang, live, DESKTOP),
            "m-highscore.svg": _highscore(lang, live, MOBILE)}

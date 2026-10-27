# Generador del perfil

`gen/` genera `README.md`, `README.en.md` y los SVG de `assets/es/` y `assets/en/` a partir de los
textos de `gen/content.py` y del calendario de contribuciones guardado en `data/live.json`.
Python 3.12, solo biblioteca estándar.

**No edites a mano** `README.md`, `README.en.md` ni nada de `assets/`: son generados y el próximo
build (o la Action diaria) pisa cualquier cambio. `data/live.json` lo escribe `--refresh`.

## Dónde se cambia cada cosa

Todo el contenido está en `gen/content.py`:

- `COPY["es"]` y `COPY["en"]`: todos los textos, incluidos los textos alternativos (`alt.*`).
  Las llaves `{total}`, `{active}`, `{best}` y `{streak}` se rellenan con los datos vivos. Los dos
  idiomas tienen que tener las mismas claves (lo comprueba un test).
- `QUESTS`: las cuatro misiones. `title`, `summary` y `status` van por idioma (`status` es el texto
  de la etiqueta, p. ej. «En desarrollo»); `starred` pone la estrella; `icon` elige el sprite
  (`ICONS` en `gen/sprites/misc.py`); `in_progress=True` pinta el punto amarillo en vez de verde.
  Si la stack en inglés cambia, va en `_STACK_EN`.
- `SKILLS`: los porcentajes de lenguajes. El mayor llena su barra y el resto se escala con él.
- `INVENTORY`: los objetos del inventario. Cada nombre necesita su sprite en `ITEMS`
  (`gen/sprites/items.py`).
- `PROJECT_TOTAL`: proyectos del portfolio. «+N misiones más» es `PROJECT_TOTAL - len(QUESTS)`.
- `URLS`: enlaces por idioma (`portfolio`, `cv`, `linkedin`, `email`, `lang` y `quest.<slug>`).

Colores del avatar: `HAIR`, `SKIN` y `HOODIE` al principio de `gen/sprites/avatar.py`. Las sombras
se recalculan solas. El largo del pelo y el tono de piel son valores por defecto aún sin confirmar.

Cada bloque del README es una escena en `gen/scenes/` (hero, buttons, quests, sheet, achievements,
inventory, highscore, footer).

Variantes móviles: las escenas generan también `m-<nombre>.svg` (de momento hero, quests-title,
quests-more y start) con 420 de ancho (`MOBILE_W` en `gen/scenes/common.py`) y la misma
información, apilada o partida en líneas.
En la cabecera, las dos maquetaciones son los `Layout` `DESKTOP` y `MOBILE` de `gen/scenes/hero.py`.
`tests/fixtures/desktop_snapshot.json` guarda el sha256 de cada SVG de escritorio, así que un
retoque móvil no puede cambiar el escritorio sin que falle un test. Si cambias el escritorio a
propósito (un texto de `content.py`, por ejemplo), regenera el fixture y revisa el diff:
`python3 -c "import tests.test_mobile as t; t.write_snapshot()"`.

## Comandos

Todos se lanzan desde la raíz del repo.

```sh
python3 -m gen build                                         # regenera desde la caché, sin red
GITHUB_TOKEN=$(gh auth token) python3 -m gen build --refresh  # descarga el calendario y regenera
python3 -m unittest discover -s tests -t .                   # tests
```

- `--out DIR` escribe en otra carpeta y **lee la caché de `DIR/data/live.json`**. Copia antes
  `data/` allí: `mkdir -p /tmp/x && cp -r data /tmp/x/ && python3 -m gen build --out /tmp/x`.
- `--refresh` es estricto. Si falta el token, si falla la descarga o si la descarga suma menos de
  la mitad que la caché, termina con código 1 sin tocar la caché ni escribir nada. Si la caída es
  real, borra `data/live.json` y vuelve a ejecutar con `--refresh`.

Vista previa con el renderizador de GitHub: hace falta `gh` con sesión iniciada y Chromium sin
interfaz de Playwright (la ruta está en `CHROME`, en `tools/preview.py`, o se pasa con `--chrome`).
Las capturas quedan en `preview/`, que no se commitea.

```sh
python3 tools/preview.py page                          # es/en × claro/oscuro × 830, 358 y 276 px
python3 tools/preview.py page --lang es --width 276 --theme dark
python3 tools/preview.py frames assets/es/hero.svg 0 1 2.5 rm   # fotogramas; rm = movimiento reducido
python3 tools/preview.py frames assets/es/highscore.svg 0 --crop 0 60 840 50 --scale 2   # zoom
```

276 px es el ancho real de la columna del README en el móvil.

## Caracteres y fuentes

Las fuentes de `fonts/` están recortadas a `CHARSET` (`gen/fonts.py`). Si escribes un carácter que
no está ahí (p. ej. «€» o «ç»), fallan el build (si va en un SVG) o los tests (si va en cualquier
texto de `COPY`). Para añadirlo:

1. Añádelo a `CHARSET`.
2. Descarga los TTF originales de Google Fonts (`ofl/pressstart2p/PressStart2P-Regular.ttf` y
   `ofl/vt323/VT323-Regular.ttf`) y el wheel `fonttools-4.67.0-py3-none-any.whl` de PyPI. En esta
   máquina no hay pip; el wheel se carga por `PYTHONPATH`.
3. Recorta las dos fuentes:
   ```sh
   PYTHONPATH=<ruta>/fonttools-4.67.0-py3-none-any.whl:. python3 tools/subset_fonts.py PressStart2P-Regular.ttf fonts/press-start-2p.woff
   PYTHONPATH=<ruta>/fonttools-4.67.0-py3-none-any.whl:. python3 tools/subset_fonts.py VT323-Regular.ttf fonts/vt323.woff
   ```
4. `python3 -m gen build` y los tests.

Los símbolos ▶ █ ♥ ● ✉ ▼ ★ y el trofeo son sprites (`gen/sprites/misc.py`), no texto. Press Start 2P
dibuja las mayúsculas acentuadas (É, Í…) con altura de minúscula, así que en los rótulos grandes
con tildes va mejor VT323 (como en el marcador del high score).

Los tests y el build vigilan los límites: texto de al menos 16 en `ps2p` y 22 en `vt323` (unidades
de lienzo), ningún texto fuera de su caja, cada SVG por debajo de 500 000 bytes, sin `<script>` ni
URLs `http(s)` dentro y un build determinista.

## La Action diaria

`.github/workflows/update.yml` se ejecuta cada día a las 04:23 UTC, con cada push a `main` que toque
`gen/**` o `fonts/**`, y a mano desde Actions → «Actualizar datos vivos» → Run workflow. Pasa los
tests, ejecuta `python -m gen build --refresh` y, si algo cambia, commitea como
`github-actions[bot]` («chore: actualizar datos vivos»).

- **Una ejecución en rojo en «Regenerar con datos vivos» significa que el refresco falló** (red,
  GraphQL, token o una caída de más de la mitad). No se ha commiteado nada y el perfil sigue con los
  números del último refresco bueno. El motivo está en el log de ese paso. Si el rojo está en
  «Tests», es que falla un test.
- **Haz pull antes de editar** (`git pull --ff-only`): el bot commitea casi todos los días. Si hay
  conflicto en archivos generados (`README*.md`, `assets/`, `data/live.json`), quédate con
  cualquiera de los dos lados (`git checkout --theirs -- <archivos>`), ejecuta
  `python3 -m gen build`, haz `git add` y sigue. El siguiente refresco pone los datos al día.
- **Regla de los 60 días**: en un repo público, GitHub desactiva los workflows programados cuando el
  repo pasa 60 días sin actividad. No cuentes con que los commits del bot basten. Si en Actions
  aparece el workflow desactivado, actívalo con «Enable workflow» o con
  `gh workflow enable update.yml -R diegoreto7u7/diegoreto7u7`.

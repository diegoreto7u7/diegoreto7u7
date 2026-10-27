"""Vista previa local del README con el renderizador real de GitHub y Chromium sin interfaz.

    python3 tools/preview.py page [--lang es|en] [--width 830 358 276] [--theme light dark]
    python3 tools/preview.py frames assets/es/hero.svg 0 1 2.5 6 [--width 358] [--name hero]
                                   [--crop X Y W H] [--scale 2]

`page` pasa README.md y README.en.md por `gh api markdown` (GFM con el contexto del repo), lo mete
en una página con github-markdown-css y `<base href>` en la raíz del repo, y la captura entera en
`preview/<lang>-<tema>-<ancho>.png`. Las imágenes son `<img>`: se ven en su primer fotograma.
Anchos por defecto: 830 (escritorio), 358 y 276 (la columna real del README en la app y la web
móvil de GitHub).

`frames` mete el SVG en línea en un HTML, pausa todas sus animaciones en cada segundo pedido y
captura `preview/<x>@<t>.png`. El tiempo `rm` captura el estado con movimiento reducido.

Solo biblioteca estándar. El CSS de GitHub se carga de jsdelivr (versión fija); es solo para la
vista previa local, nunca va dentro de los SVG.
"""

import argparse
import math
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "preview"
CHROME = (Path.home() / ".cache/ms-playwright/chromium_headless_shell-1248"
          / "chrome-headless-shell-linux64/chrome-headless-shell")
MARKDOWN_CSS = "https://cdn.jsdelivr.net/npm/github-markdown-css@5.8.1/github-markdown-{theme}.css"
READMES = {"es": "README.md", "en": "README.en.md"}
PAGE_BG = {"light": "#ffffff", "dark": "#0d1117"}
GUTTER = 16                 # margen de la página alrededor del cuadro del README
BUDGET_MS = 3000            # tiempo virtual para que carguen el CSS y las imágenes


def chrome(binary: Path, *args: str) -> str:
    cmd = [str(binary), "--headless", "--no-sandbox", "--hide-scrollbars", *args]
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if res.returncode != 0:
        raise SystemExit(f"chrome falló ({res.returncode}): {res.stderr[-2000:]}")
    return res.stdout


def gfm(readme: Path) -> str:
    res = subprocess.run(
        ["gh", "api", "markdown", "-f", "mode=gfm", "-f", "context=diegoreto7u7/diegoreto7u7",
         "-F", f"text=@{readme}"],
        capture_output=True, text=True, check=True)
    return res.stdout


def page_html(fragment: str, theme: str, width: int) -> str:
    # el script deja la altura de la página en <body data-h> para la pasada de --dump-dom
    return (
        '<!doctype html><html><head><meta charset="utf-8">'
        f'<base href="{ROOT.as_uri()}/">'
        f'<link rel="stylesheet" href="{MARKDOWN_CSS.format(theme=theme)}">'
        f"<style>html,body{{margin:0;background:{PAGE_BG[theme]}}}"
        f".wrap{{padding:{GUTTER}px}}"
        f".markdown-body{{box-sizing:border-box;width:{width}px}}</style>"
        "</head><body><div class=\"wrap\"><article class=\"markdown-body\">"
        f"{fragment}</article></div>"
        "<script>addEventListener('load',()=>{document.body.dataset.h="
        "Math.ceil(document.documentElement.scrollHeight)})</script>"
        "</body></html>"
    )


def page(args) -> list[Path]:
    OUT.mkdir(exist_ok=True)
    shots = []
    for lang in args.lang:
        fragment = gfm(ROOT / READMES[lang])
        for theme in args.theme:
            for width in args.width:
                name = f"{lang}-{theme}-{width}"
                html = OUT / f"{name}.html"
                html.write_text(page_html(fragment, theme, width), encoding="utf-8")
                win_w = width + 2 * GUTTER
                dom = chrome(args.chrome, f"--window-size={win_w},800",
                             f"--virtual-time-budget={BUDGET_MS}", "--dump-dom", html.as_uri())
                m = re.search(r'data-h="(\d+)"', dom)
                if not m:
                    raise SystemExit(f"{name}: no se pudo medir la altura de la página")
                png = OUT / f"{name}.png"
                chrome(args.chrome, f"--window-size={win_w},{m.group(1)}",
                       f"--force-device-scale-factor={args.scale:g}",
                       f"--virtual-time-budget={BUDGET_MS}", f"--screenshot={png}", html.as_uri())
                print(png.relative_to(ROOT), f"{win_w}×{m.group(1)}")
                shots.append(png)
    return shots


def _svg_size(svg: str) -> tuple[float, float]:
    m = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg)
    if not m:
        raise SystemExit("el SVG no tiene viewBox")
    return float(m.group(1)), float(m.group(2))


def frames(args) -> list[Path]:
    OUT.mkdir(exist_ok=True)
    src = Path(args.svg)
    svg = (src if src.is_absolute() else ROOT / src).read_text(encoding="utf-8")
    vw, vh = _svg_size(svg)
    if args.crop:
        # zoom sin bibliotecas de imagen: el viewBox se reduce a la región pedida
        cx, cy, vw, vh = args.crop
        svg = re.sub(r'viewBox="[^"]*"', f'viewBox="{cx:g} {cy:g} {vw:g} {vh:g}"', svg, count=1)
    width = args.width or vw
    height = round(vh * width / vw)
    # el SVG se muestra al ancho pedido (por defecto, su tamaño de lienzo)
    svg = re.sub(r'width="[\d.]+" height="[\d.]+"', f'width="{width:g}" height="{height}"',
                 svg, count=1)
    stem = args.name or src.stem
    shots = []
    for t in args.times:
        label = t if t == "rm" else f"{float(t):g}"
        script = "" if t == "rm" else (
            "<script>addEventListener('load',()=>document.getAnimations().forEach(a=>"
            f"{{a.pause();a.currentTime={float(t) * 1000:g}}}))</script>")
        html = OUT / f"{stem}@{label}.html"
        html.write_text(
            '<!doctype html><meta charset="utf-8">'
            "<style>html,body{margin:0;background:#fff}svg{display:block}</style>"
            f"{svg}{script}", encoding="utf-8")
        png = OUT / f"{stem}@{label}.png"
        extra = ["--force-prefers-reduced-motion"] if t == "rm" else []
        chrome(args.chrome, *extra, f"--window-size={math.ceil(width)},{height}",
               f"--force-device-scale-factor={args.scale:g}",
               f"--virtual-time-budget={BUDGET_MS}", f"--screenshot={png}", html.as_uri())
        print(png.relative_to(ROOT))
        shots.append(png)
    return shots


def main(argv=None) -> None:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--chrome", type=Path, default=CHROME,
                        help="binario de Chromium sin interfaz")
    common.add_argument("--scale", type=float, default=1, help="factor de escala del dispositivo")
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("page", parents=[common], help="README entero con el renderizador de GitHub")
    p.add_argument("--lang", nargs="+", choices=sorted(READMES), default=["es", "en"])
    p.add_argument("--theme", nargs="+", choices=sorted(PAGE_BG), default=["light", "dark"])
    p.add_argument("--width", nargs="+", type=int, default=[830, 358, 276],
                   help="anchos del cuadro del README en px (276 = columna de GitHub en el móvil)")
    p.set_defaults(run=page)

    f = sub.add_parser("frames", parents=[common], help="fotogramas de un SVG en los segundos pedidos")
    f.add_argument("svg", help="ruta del SVG, p. ej. assets/es/hero.svg")
    f.add_argument("times", nargs="+", help="segundos (p. ej. 0 1 2.5) o «rm»")
    f.add_argument("--width", type=float, help="ancho de presentación en px (por defecto, el del lienzo)")
    f.add_argument("--name", help="nombre base de las capturas (por defecto, el del SVG)")
    f.add_argument("--crop", nargs=4, type=float, metavar=("X", "Y", "W", "H"),
                   help="solo esta región del lienzo (para ampliar detalles)")
    f.set_defaults(run=frames)

    args = ap.parse_args(argv)
    if not args.chrome.exists():
        sys.exit(f"no encuentro Chromium en {args.chrome}; pásalo con --chrome")
    args.run(args)


if __name__ == "__main__":
    main()

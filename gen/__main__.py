"""CLI: python3 -m gen build [--refresh] [--out DIR]"""

import argparse
import os
from pathlib import Path

from .build import build


def main() -> None:
    p = argparse.ArgumentParser(prog="gen")
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="genera README y assets")
    b.add_argument("--refresh", action="store_true",
                   help="descarga el calendario con GITHUB_TOKEN; si falla (sin token, error de red "
                        "o caída de más de la mitad) sale con código 1 y deja la caché como estaba")
    b.add_argument("--out", type=Path, default=Path("."), metavar="DIR",
                   help="directorio de salida; la caché del calendario se lee (y con --refresh "
                        "se escribe) en DIR/data/live.json (por defecto, el directorio actual)")
    args = p.parse_args()
    paths = build(args.out, refresh=args.refresh, token=os.environ.get("GITHUB_TOKEN"),
                  strict=args.refresh)
    print(f"{len(paths)} archivos escritos en {args.out}")


if __name__ == "__main__":
    main()

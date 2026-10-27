"""CLI: python3 -m gen build [--refresh] [--out DIR]"""

import argparse
import os
from pathlib import Path

from .build import build


def main() -> None:
    p = argparse.ArgumentParser(prog="gen")
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="genera README y assets")
    b.add_argument("--refresh", action="store_true", help="descarga el calendario (usa GITHUB_TOKEN)")
    b.add_argument("--out", type=Path, default=Path("."), help="directorio de salida")
    args = p.parse_args()
    paths = build(args.out, refresh=args.refresh, token=os.environ.get("GITHUB_TOKEN"))
    print(f"{len(paths)} archivos escritos en {args.out}")


main()

"""Validador de los SVG generados: devuelve la lista de problemas."""

import re
import xml.etree.ElementTree as ET

from gen.fonts import MIN_SIZE

MAX_BYTES = 500_000
_EXTERNAL = re.compile(
    r"""(?:xlink:)?href\s*=\s*["']\s*https?://"""
    r"""|url\(\s*["']?\s*https?://"""
    r"""|@import\s+(?:url\(\s*)?["']?\s*https?://""",
    re.I,
)


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def check_svg(svg: str) -> list[str]:
    problems: list[str] = []
    size = len(svg.encode("utf-8"))
    if size > MAX_BYTES:
        problems.append(f"pesa demasiado: {size} bytes (máximo {MAX_BYTES})")
    try:
        root = ET.fromstring(svg)
    except ET.ParseError as e:
        return problems + [f"XML no válido: {e}"]
    if _local(root.tag) != "svg":
        return problems + ["la raíz no es svg"]
    if not root.get("viewBox"):
        problems.append("falta el viewBox en la raíz")
    if not any(_local(e.tag) == "title" for e in root.iter()):
        problems.append("falta el elemento title")
    if any(_local(e.tag) == "script" for e in root.iter()) or "<script" in svg.lower():
        problems.append("contiene un script")
    if _EXTERNAL.search(svg):
        problems.append("contiene una URL externa (http o https)")
    if "@keyframes" in svg and "prefers-reduced-motion" not in svg:
        problems.append("hay animaciones sin bloque de movimiento reducido")

    first = next((e for e in root if _local(e.tag) not in ("title", "style", "defs")), None)
    vb = (root.get("viewBox") or "").split()
    if (first is None or _local(first.tag) != "rect"
            or len(vb) != 4
            or first.get("width") != vb[2] or first.get("height") != vb[3]):
        problems.append("el primer elemento de contenido no es un rect de fondo del lienzo")

    for e in root.iter():
        if _local(e.tag) != "text":
            continue
        fam, fs = e.get("font-family"), e.get("font-size")
        if fam in MIN_SIZE and fs:
            try:
                if float(fs) < MIN_SIZE[fam]:
                    problems.append(f"tamaño de fuente {fs} menor que {MIN_SIZE[fam]} en {fam}")
            except ValueError:
                problems.append(f"tamaño de fuente no numérico: {fs}")
    return problems

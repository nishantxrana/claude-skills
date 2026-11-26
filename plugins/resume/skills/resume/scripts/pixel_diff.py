#!/usr/bin/env python3
"""pixel_diff.py A.tex B.tex : compile both and report whether page 1 renders pixel-identical.
Use it to PROVE that an invisible ATS change (glyphtounicode, pdftitle) did not alter the look.
Also accepts two PDFs. Exit 0 = IDENTICAL."""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import compile_tex  # noqa: E402

try:
    import pymupdf as fitz
except ImportError:
    import fitz  # type: ignore
from PIL import Image, ImageChops


def render(src: str) -> Image.Image:
    p = Path(src)
    if p.suffix.lower() == ".tex":
        pdf, _, errs = compile_tex(p, Path(tempfile.mkdtemp(prefix="pxdiff_")))
        if not pdf:
            sys.exit(f"compile failed for {src}: {' | '.join(errs)}")
        p = pdf
    pix = fitz.open(str(p))[0].get_pixmap(dpi=150)
    return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)


a, b = render(sys.argv[1]), render(sys.argv[2])
bb = ImageChops.difference(a, b).getbbox() if a.size == b.size else "size differs"
print("IDENTICAL" if bb is None else f"DIFFERENT: {bb}")
sys.exit(0 if bb is None else 1)

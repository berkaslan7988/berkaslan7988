#!/usr/bin/env python3
"""Make the static font instances that tools/build.py embeds in the SVGs.

Downloads the variable fonts from the google/fonts repository and pins the
weights the art uses. Run it once; the results are committed in tools/fonts.

    python tools/build_fonts.py
"""
from __future__ import annotations

import io
import urllib.request
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

FONTS = Path(__file__).resolve().parent / "fonts"
BASE = "https://raw.githubusercontent.com/google/fonts/main/ofl/"

# output name -> (source path in google/fonts, weight or None for static fonts)
INSTANCES = {
    "SofiaSansCondensed-ExtraBold.ttf": ("sofiasanscondensed/SofiaSansCondensed%5Bwght%5D.ttf", 800),
    "SofiaSansCondensed-SemiBold.ttf": ("sofiasanscondensed/SofiaSansCondensed%5Bwght%5D.ttf", 600),
    "SofiaSans-Regular.ttf": ("sofiasans/SofiaSans%5Bwght%5D.ttf", 400),
    "SofiaSans-SemiBold.ttf": ("sofiasans/SofiaSans%5Bwght%5D.ttf", 600),
    "FragmentMono-Regular.ttf": ("fragmentmono/FragmentMono-Regular.ttf", None),
}
# Basic Latin, Latin-1, Latin Extended-A (Turkish), punctuation and arrows.
UNICODES = "U+0020-007E,U+00A0-017F,U+2010-2027,U+2030-205E,U+2190-21FF,U+2212"

LICENCES = {
    "OFL-SofiaSans.txt": "sofiasans/OFL.txt",
    "OFL-FragmentMono.txt": "fragmentmono/OFL.txt",
}


def fetch(path: str) -> bytes:
    with urllib.request.urlopen(BASE + path, timeout=60) as r:
        return r.read()


def main() -> None:
    FONTS.mkdir(exist_ok=True)
    cache: dict[str, bytes] = {}
    for name, (src, weight) in INSTANCES.items():
        data = cache.setdefault(src, fetch(src))
        font = TTFont(io.BytesIO(data))
        if weight is not None:
            font = instancer.instantiateVariableFont(font, {"wght": weight}, updateFontNames=True)
        options = subset.Options()
        options.layout_features = ["kern", "liga", "calt", "ccmp", "locl", "mark", "mkmk"]
        options.name_IDs = ["*"]
        sub = subset.Subsetter(options)
        sub.populate(unicodes=subset.parse_unicodes(UNICODES))
        sub.subset(font)
        font.save(FONTS / name)
        print(f"{name:36} {(FONTS / name).stat().st_size // 1024} KB")
    for name, src in LICENCES.items():
        (FONTS / name).write_bytes(fetch(src))


if __name__ == "__main__":
    main()

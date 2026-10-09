#!/usr/bin/env python3
"""Build web-sized images from the original media/ folder.

The originals in media/ are large (several MB each) and are NOT committed.
Run this script whenever you add or change photos:

    python3 tools/optimize_media.py

It writes, for every project:
    assets/img/<slug>/<n>.jpg        full size (max 2000px on the long side)
    assets/img/<slug>/<n>-thumb.jpg  thumbnail (max 900px)
and a manifest at assets/img/manifest.json with each image's dimensions.
Uses macOS `sips` (built in), so no extra installs are needed.
"""
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "media"
OUT = ROOT / "assets" / "img"

# slug -> {section name: source folder or single file (relative to media/)}
PROJECTS = {
    "echec-et-mat": {"gallery": "PROGETTO OLANDA"},
    "anime-giovani": {
        "gallery": "STILL ANIME GIOVANI",
        "backstage": "STILL ANIME GIOVANI/Backstage",
    },
    "the-end": {
        "gallery": "THE END STILL/PORTFOLIO THE END",
        "backstage": "THE END STILL/BACKSTAGE",
    },
    "fashion-graduate-italia": {"gallery": "fashion graduate italia"},
    # Images used outside project galleries.
    "site": {"about": "fashion graduate italia/copertina.jpg"},
}

# Files that should appear first in a section (e.g. title cards).
FIRST = {"TITOLO TESTA ANIME GIOVANI 250221_3.1.1(1).jpg"}
# Files to leave out of galleries.
SKIP = {
    "copertina.jpg",    # too small for a gallery; used on the About page instead
    "Olanda-0010.jpg",  # contact details page of the book
}

# Film stills exported with black pillarbox bars: crop to the 4:3 frame.
CROP_4X3 = {f"Still 2025-02-20 180847_1.{n}.jpg"
            for n in ("10.1", "28.2", "30.1", "4.1", "5.1", "74.1")}

EXTS = {".jpg", ".jpeg", ".png"}


def sips_resize(src: Path, dst: Path, size: int, quality: int) -> None:
    size = min(size, max(dims(src)))  # never upscale
    subprocess.run(
        ["sips", "-Z", str(size), "-s", "format", "jpeg",
         "-s", "formatOptions", str(quality), str(src), "--out", str(dst)],
        check=True, capture_output=True,
    )


def crop_4x3(src: Path, tmpdir: str) -> Path:
    w, h = dims(src)
    out = Path(tmpdir) / (src.stem + ".png")
    subprocess.run(["sips", "-s", "format", "png", "-c", str(h), str(round(h * 4 / 3)),
                    str(src), "--out", str(out)], check=True, capture_output=True)
    return out


def dims(path: Path) -> tuple[int, int]:
    out = subprocess.run(
        ["sips", "-g", "pixelWidth", "-g", "pixelHeight", str(path)],
        check=True, capture_output=True, text=True,
    ).stdout
    vals = {}
    for line in out.splitlines():
        line = line.strip()
        if line.startswith("pixel"):
            k, v = line.split(":")
            vals[k] = int(v)
    return vals["pixelWidth"], vals["pixelHeight"]


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    manifest = {}
    tmp = tempfile.mkdtemp()
    for slug, sections in PROJECTS.items():
        dest = OUT / slug
        dest.mkdir(parents=True)
        manifest[slug] = {}
        for section, folder in sections.items():
            if (SRC / folder).is_file():
                files = [SRC / folder]
            else:
                files = sorted(
                    (p for p in (SRC / folder).iterdir()
                     if p.is_file() and p.suffix.lower() in EXTS and p.name not in SKIP),
                    key=lambda p: (p.name not in FIRST, p.name.lower()),
                )
            items = []
            for i, f in enumerate(files, 1):
                name = f"{section}-{i:02d}"
                full, thumb = dest / f"{name}.jpg", dest / f"{name}-thumb.jpg"
                src = crop_4x3(f, tmp) if f.name in CROP_4X3 else f
                sips_resize(src, full, 2000, 80)
                sips_resize(src, thumb, 900, 75)
                w, h = dims(full)
                items.append({"src": f"{slug}/{name}.jpg",
                              "thumb": f"{slug}/{name}-thumb.jpg",
                              "w": w, "h": h, "source": f.name})
                print(f"{slug}/{name}.jpg  {w}x{h}  <- {f.name}")
            manifest[slug][section] = items
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2))
    shutil.rmtree(tmp)


if __name__ == "__main__":
    main()

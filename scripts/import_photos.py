#!/usr/bin/env python3
"""Fetch three rights-cleared photos, turn them into compact WebP assets and retain audit provenance."""
import io
import json
import pathlib
import urllib.request
from PIL import Image, ImageOps

ROOT = pathlib.Path(__file__).resolve().parents[1]
manifest = json.loads((ROOT / "photo-sources.json").read_text("utf-8"))
assert manifest["schemaVersion"] == 1
out_dir = ROOT / "images"
out_dir.mkdir(parents=True, exist_ok=True)
for photo in manifest["photos"]:
    slug = photo["slug"]
    assert slug.replace("-", "").isalnum() and len(slug) <= 100
    url = photo["url"]
    assert url.startswith("https://upload.wikimedia.org/wikipedia/commons/")
    req = urllib.request.Request(url, headers={"User-Agent": "Yosurf-Editorial-Photo-Importer/1.0 (CC license attribution in pierreneuville/LineUpSurf)"})
    with urllib.request.urlopen(req, timeout=40) as response:
        payload = response.read(10 * 1024 * 1024 + 1)
    if len(payload) > 10 * 1024 * 1024:
        raise ValueError(f"Image too large: {slug}")
    with Image.open(io.BytesIO(payload)) as src:
        src.load()
        if src.format not in ("JPEG", "PNG", "WEBP"):
            raise ValueError(f"Unsupported format: {src.format}")
        if src.width < 800:
            raise ValueError(f"Not enough horizontal pixels: {slug}")
        photo_img = ImageOps.exif_transpose(src).convert("RGB")
        # Preserve whole archive photographs: no misleading crops or altering image claims.
        photo_img.thumbnail((1600, 1600), Image.Resampling.LANCZOS)
        dest = out_dir / (slug + "-licensed-archive.webp")
        photo_img.save(dest, "WEBP", quality=80, method=6)
        print(f"{dest.relative_to(ROOT)}: {photo_img.width}x{photo_img.height}, {dest.stat().st_size} bytes")

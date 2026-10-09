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
    # Wikimedia blocks shared CI runner IP ranges with 429; do not publish
    # anything until a real raster file can be downloaded and decoded.
    # A temporary third-party image proxy is permitted for IMPORT ONLY:
    # once imported, website images are served from our public GitHub repo.
    from urllib.parse import quote
    attempts = [
        url,
        "https://wsrv.nl/?url=" + quote(url, safe=""),
        "https://images.weserv.nl/?url=" + quote(url, safe=""),
    ]
    payload = None
    for candidate in attempts:
        try:
            req = urllib.request.Request(candidate, headers={
                "User-Agent": "Mozilla/5.0 YosurfEditorialBot/1.0 (https://github.com/pierreneuville/LineUpSurf)",
                "Accept": "image/avif,image/webp,image/*,*/*;q=0.8",
            })
            with urllib.request.urlopen(req, timeout=40) as response:
                payload = response.read(10 * 1024 * 1024 + 1)
            if payload:
                print(f"Fetched {slug} from {candidate.split('/')[2]}")
                break
        except Exception as err:
            print(f"Image fetch failed from {candidate.split('/')[2]} for {slug}: {err}")
    if payload is None:
        raise RuntimeError(f"All photo fetch sources unavailable: {slug}")
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

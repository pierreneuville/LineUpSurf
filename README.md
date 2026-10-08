# LineUpSurf — Yosurf editorial content

Public, Git-backed content repository for the **The Lineup** section on [Yosurf](https://yosurf.app/lineup).

## Structure

- `manifest.json` — explicit order/allowlist of public article slugs
- `articles/<slug>.json` — one complete EN / FR / ES / PT story per file
- `images/<slug>.svg` (or approved .jpg/.webp/.png) — editorial assets kept in this same repository

The website reads JSON via `raw.githubusercontent.com` using 300-second Next.js ISR. Images are served from the repository through `cdn.jsdelivr.net` (needed for reliable SVG MIME types); asset URLs may remain cached for up to 12 hours, so give any updated image a NEW filename. **Adding an article, changing a translation or uploading an image does not need a Yosurf build.**

## Branches

- `staging` — read by `staging.yosurf.app`; editorial validation
- `main` — read by `yosurf.app`; production

To publish: verify sources and rights → add `articles/<slug>.json` and approved image → update `manifest.json` LAST → PR to `staging`; validate; promote the same content to `main` by PR. No changes to Yosurf code for content-only updates.

**A story is not public unless its slug is listed in the manifest, its status is `published`, its score is >=65, the four languages exist and sources are valid.**

## Photography and rights

Images **can live in this public GitHub repository**. Only upload original images, images under licenses allowing republication (respecting restrictions/attribution), or assets with explicit authorization. Never copy a news outlet's copyrighted photograph simply because it appears in search results. The three initial images are **original SVG illustrations**, not purported photographs of the actual events. For real photography, use a properly licensed JPEG/WebP and preserve proof of permission.

Use an `image` object:
```json
{
  "path": "images/my-story.webp",
  "alt": {"en":"...", "fr":"...", "es":"...", "pt":"..."},
  "credit": "Photographer Name / License",
  "license": "CC BY 4.0",
  "sourceUrl": "https://the-authoritative-original-source"
}
```

Files should be reasonably compressed: aim for <= 400 kB per WebP/JPEG at 1600px wide. Do not add secrets, drafts with embargoes, internal notes, or API keys to this public repository. Validate that image paths resolve before advertising a story.

## Data contract

Each article must use `schemaVersion: 1`, `slug`, `status`, `publishedAt`, `category`, `editorialScore`, `sources`, and `translations` in `en/fr/es/pt`. `image` is optional for compatibility; **new editorial publication should include a rights-cleared hero image**. Native-language original writing required. An empty week is a valid `NO_PUBLISH` with no commits.

Canonical domain and SEO signals remain on `yosurf.app`, not GitHub.

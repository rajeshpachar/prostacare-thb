# ProstaCare Spec Viewer — build & deploy

One-command tooling to bundle the spec docs into a single shareable HTML and publish it to S3 + CloudFront.

## Deploy (refresh the shared link)
```bash
scripts/spec-viewer/deploy.sh
```
Regenerates the viewer, uploads to S3, and invalidates CloudFront. Requires the `hippa` AWS profile.

**Shared link:** https://d29eh5rcaoayqi.cloudfront.net/prostacare/spec-viewer.html

## What each piece does
- `gen_viewer.py` — bundles `docs/*.md` (Functional spec, Alignment review, Build spec, Field dictionary, Flow clarity) into `docs/prostacare-spec-viewer.html` (self-contained; renders Markdown + Mermaid client-side).
- `gen_fielddict.py` — regenerates `docs/FIELD_DICTIONARY.md` from the V2 workbook. Skips gracefully if the workbook or `openpyxl` is missing (keeps the committed file). Override the workbook path: `WORKBOOK=/path/to.xlsx`. Needs `pip install openpyxl`.
- `viewer_template.html` — the HTML shell (ProstaCare palette, tabs, Print/PDF).
- `deploy.sh` — regen → `aws s3 cp` → `aws cloudfront create-invalidation`.

## Config (edit in `deploy.sh`)
| Var | Value |
|---|---|
| Bucket | `zygo-media-dev-991046336932` |
| Key | `media/prostacare/spec-viewer.html` (CloudFront origin path is `/media`) |
| Distribution | `E25YK1CQ9XN80Z` |
| Profile | `hippa` |

## Add a new doc as a tab
Add `("Tab Title", "FILENAME.md")` to the `ORDER` list in `gen_viewer.py`, then run `deploy.sh`.

> The viewer loads `marked` + `mermaid` from the jsdelivr CDN, so rendering needs internet in the viewer's browser.

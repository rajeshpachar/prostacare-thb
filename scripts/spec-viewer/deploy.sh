#!/usr/bin/env bash
# Regenerate the ProstaCare spec viewer and publish it to S3 + CloudFront.
# Usage:  scripts/spec-viewer/deploy.sh
# Requires: aws CLI logged in via the 'hippa' profile, python3 (+ openpyxl for
# Field Dictionary regen; skipped gracefully if the workbook/openpyxl is absent).
set -euo pipefail

ROOT="$(git -C "$(dirname "$0")" rev-parse --show-toplevel)"
cd "$ROOT"

# --- config ---------------------------------------------------------------
BUCKET="zygo-media-dev-991046336932"
KEY="media/prostacare/spec-viewer.html"      # CloudFront origin path is /media
DIST_ID="E25YK1CQ9XN80Z"
PROFILE="hippa"
CF_PATH="/prostacare/spec-viewer.html"
URL="https://d29eh5rcaoayqi.cloudfront.net${CF_PATH}"
DIR="scripts/spec-viewer"
# --------------------------------------------------------------------------

echo "==> 1/4  Regenerate Field Dictionary from workbook (optional)"
python3 "$DIR/gen_fielddict.py"

echo "==> 2/4  Rebuild self-contained viewer"
python3 "$DIR/gen_viewer.py"

echo "==> 3/4  Upload to s3://$BUCKET/$KEY"
aws s3 cp docs/prostacare-spec-viewer.html "s3://$BUCKET/$KEY" \
  --profile "$PROFILE" \
  --content-type "text/html; charset=utf-8" \
  --cache-control "no-cache, max-age=60"

echo "==> 4/4  Invalidate CloudFront $CF_PATH"
aws cloudfront create-invalidation \
  --distribution-id "$DIST_ID" \
  --paths "$CF_PATH" \
  --profile "$PROFILE" \
  --query "Invalidation.[Id,Status]" --output text

echo ""
echo "✅ Live: $URL"

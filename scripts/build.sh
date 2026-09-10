#!/usr/bin/env bash
# Assemble dist/ — exactly what gets deployed, and nothing else.
#
# The site has no compile step, so "building" is copying the served files into
# a clean directory. That directory is the deploy boundary: wix.config.json
# points outputDirectory at ./dist so a release can never pick up .env,
# scripts/, or host configs sitting in the repo root.
set -euo pipefail
cd "$(dirname "$0")/.."

rm -rf dist
mkdir -p dist/client dist/server

# Everything the browser needs, and only that.
rsync -a \
  --exclude='.git' \
  --exclude='.wix' \
  --exclude='.env*' \
  --exclude='dist' \
  --exclude='scripts' \
  --exclude='node_modules' \
  --exclude='.DS_Store' \
  --exclude='.gitignore' \
  --exclude='*.md' \
  --exclude='netlify.toml' \
  --exclude='vercel.json' \
  --exclude='wix.config.json' \
  --exclude='worker' \
  --exclude='package*.json' \
  ./ dist/client/

# The worker gives us clean URLs. Wix serves a matching static file directly
# and hands anything else to this, so /about.html is served by the CDN and
# /about falls through to the worker, which fetches it. Entry MUST be named
# entry.mjs — Wix looks for /user-code/entry.mjs and 500s otherwise.
cp worker/entry.mjs dist/server/entry.mjs

# Fail loudly rather than ship a secret.
if find dist/client -name '.env*' -o -name '*.key' -o -name '*.pem' | grep -q .; then
  echo "ABORT: secret-shaped file found in dist/" >&2
  exit 1
fi
if grep -rlq "CLOUDINARY_API_SECRET" dist/ 2>/dev/null; then
  echo "ABORT: CLOUDINARY_API_SECRET appears in dist/" >&2
  exit 1
fi
if [ ! -f dist/client/index.html ]; then
  echo "ABORT: dist/client/index.html missing — Wix requires an entry HTML file at the top level" >&2
  exit 1
fi

if [ ! -f dist/server/entry.mjs ]; then
  echo "ABORT: dist/server/entry.mjs missing — Wix requires this exact filename" >&2
  exit 1
fi

FILES=$(find dist/client -type f | wc -l | tr -d ' ')
# awk, not bc — this now runs in Netlify CI, and bc is not guaranteed to be
# installed there. Under `set -e` a missing bc would fail the whole build.
SIZE=$(find dist/client -type f -exec ls -l {} \; | awk '{s+=$5} END {printf "%.0f", s/1024}')
printf 'dist/ built: %s client files, %sKB + worker\n' "$FILES" "$SIZE"

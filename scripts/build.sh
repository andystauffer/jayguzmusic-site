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
mkdir -p dist

# Everything the browser needs, and only that.
rsync -a \
  --exclude='.git' \
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
  --exclude='package*.json' \
  ./ dist/

# Fail loudly rather than ship a secret.
if find dist -name '.env*' -o -name '*.key' -o -name '*.pem' | grep -q .; then
  echo "ABORT: secret-shaped file found in dist/" >&2
  exit 1
fi
if grep -rlq "CLOUDINARY_API_SECRET" dist/ 2>/dev/null; then
  echo "ABORT: CLOUDINARY_API_SECRET appears in dist/" >&2
  exit 1
fi
if [ ! -f dist/index.html ]; then
  echo "ABORT: dist/index.html missing — Wix requires an entry HTML file at the top level" >&2
  exit 1
fi

FILES=$(find dist -type f | wc -l | tr -d ' ')
BYTES=$(find dist -type f -exec ls -l {} \; | awk '{s+=$5} END {print s}')
printf 'dist/ built: %s files, %.0fKB\n' "$FILES" "$(echo "$BYTES/1024" | bc -l)"

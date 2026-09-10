#!/usr/bin/env bash
# Read form schemas from a Wix site. Read-only: only ever queries.
#
#   ./read-forms.sh <SITE_ID>                  # list every form
#   ./read-forms.sh <SITE_ID> "Form Name"      # dump one form's fields
#
# Run this BEFORE deciding whether to extend an existing form or
# create a new one. What matters is each field's `target`, because
# that is the key a submission must use — Wix accepts only keys that
# match a target, so a mismatch loses the value with no error worth
# the name.
#
# Reads WIX_API_KEY and WIX_ACCOUNT_ID from .env, like create-form.sh.

set -euo pipefail

ENV_FILE="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)/.env"
if [[ -f "$ENV_FILE" ]]; then
  # shellcheck disable=SC1090
  set -a; source "$ENV_FILE"; set +a
fi

SITE_ID="${1:-}"
WANT="${2:-}"

if [[ -z "$SITE_ID" ]]; then
  echo "usage: $0 <SITE_ID> [\"Form Name\"]" >&2
  exit 2
fi
if [[ -z "${WIX_API_KEY:-}" ]]; then
  echo "set WIX_API_KEY in $ENV_FILE" >&2
  exit 2
fi

# Capture rather than pipe: the heredoc below occupies python's stdin, so a
# pipe here would be silently discarded (curl: "Failure writing output").
RESPONSE="$(curl -sS -X POST "https://www.wixapis.com/form-schema-service/v4/forms/query" \
  -H "Authorization: $WIX_API_KEY" \
  -H "wix-site-id: $SITE_ID" \
  -H "Content-Type: application/json" \
  -d '{"query":{"filter":{"namespace":"wix.form_app.form"}}}')"

FORMS_JSON="$RESPONSE" python3 - "$WANT" <<'PY'
import json, os, sys

want = sys.argv[1] if len(sys.argv) > 1 else ""
raw = os.environ["FORMS_JSON"]
try:
    forms = json.loads(raw).get("forms", [])
except Exception:
    print("could not parse response:", raw[:400]); sys.exit(1)

if not want:
    print(f"{len(forms)} form(s)\n")
    for f in forms:
        fields = [x for x in f.get("formFields", [])
                  if x.get("identifier") != "SUBMIT_BUTTON"]
        print(f"  {f.get('name','(unnamed)')}")
        print(f"    id     {f.get('id')}")
        print(f"    fields {len(fields)}")
    sys.exit(0)

match = [f for f in forms if f.get("name") == want]
if not match:
    print(f'no form named "{want}". Names present:')
    for f in forms:
        print("  -", f.get("name"))
    sys.exit(1)

for f in match:
    print(f'{f.get("name")}   id={f.get("id")}   revision={f.get("revision")}')
    print(f'{"TARGET":<32} {"IDENTIFIER":<24} REQ  LABEL')
    for x in f.get("formFields", []):
        if x.get("identifier") == "SUBMIT_BUTTON":
            continue
        opts = x.get("inputOptions", {}) or {}
        target = opts.get("target", "?")
        req = "yes" if opts.get("required") else "-"
        so = opts.get("stringOptions", {}) or {}
        label = ""
        for k, v in so.items():
            if isinstance(v, dict) and "label" in v:
                label = v["label"]; break
        print(f'{target:<32} {x.get("identifier",""):<24} {req:<4} {label}')
    print()
PY

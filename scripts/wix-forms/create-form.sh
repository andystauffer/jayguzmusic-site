#!/usr/bin/env bash
# Create the Event Consultation form on a Wix site.
#
#   ./create-form.sh <SITE_ID> <PAYLOAD.json>
#
# Needs an account API key with forms:v4:form:create_form. The Wix
# CLI token does NOT work: it is an app-instance token with empty
# permissions and no MetaSite context, so it 401s regardless of the
# caller's account role.
#
# Reads WIX_API_KEY and WIX_ACCOUNT_ID from .env (gitignored,
# chmod 600), same as the Cloudinary scripts, so the key never has
# to be pasted anywhere it might be captured.
#
# The key must belong to the account that OWNS the target site —
# Wix rejects site-level calls made with another account's key.
#
# Creates one form and stops. It does not update or delete, so a
# second run makes a duplicate — check the dashboard before re-running.

set -euo pipefail

ENV_FILE="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)/.env"
if [[ -f "$ENV_FILE" ]]; then
  # shellcheck disable=SC1090
  set -a; source "$ENV_FILE"; set +a
fi

SITE_ID="${1:-}"
PAYLOAD="${2:-}"

if [[ -z "$SITE_ID" || -z "$PAYLOAD" ]]; then
  echo "usage: $0 <SITE_ID> <PAYLOAD.json>" >&2
  exit 2
fi
if [[ ! -f "$PAYLOAD" ]]; then
  echo "no such payload: $PAYLOAD" >&2
  exit 2
fi
if [[ -z "${WIX_API_KEY:-}" || -z "${WIX_ACCOUNT_ID:-}" ]]; then
  echo "set WIX_API_KEY and WIX_ACCOUNT_ID in $ENV_FILE" >&2
  exit 2
fi

# The site id decides whose dashboard these leads land in. Two known
# sites, easy to confuse — name the target out loud before writing.
case "$SITE_ID" in
  e935d47e-9867-4df5-bd31-9abdb3df3534)
    echo "target: OUR headless project (jayguzmusic-site-…wix-site-host.com)" ;;
  c6da36f6-95ac-4db1-9286-c690672a61a0)
    echo "target: JAY'S LIVE PREMIUM SITE — leads and test entries hit his real dashboard" ;;
  *)
    echo "target: unrecognised site $SITE_ID" ;;
esac
FORM_NAME="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["form"]["name"])' "$PAYLOAD")"
echo "form:   $FORM_NAME"

# Jay's site already carries seven near-duplicate forms on a plan
# capped at ten, and one of them holds a real lead. Refuse to add
# another form with a name that is already taken — a second
# "Event Lead Capture Form" would split enquiries between two
# identically named rows with no way to tell them apart.
EXISTING="$(curl -sS -X POST "https://www.wixapis.com/form-schema-service/v4/forms/query" \
  -H "Authorization: $WIX_API_KEY" \
  -H "wix-account-id: $WIX_ACCOUNT_ID" \
  -H "wix-site-id: $SITE_ID" \
  -H "Content-Type: application/json" \
  -d '{"query":{}}' || true)"

if python3 - "$FORM_NAME" <<PY
import json, sys
name = sys.argv[1]
try:
    forms = json.loads('''$EXISTING''').get('forms', [])
except Exception:
    sys.exit(1)          # could not read the list; fall through to the prompt
sys.exit(0 if any(f.get('name') == name for f in forms) else 1)
PY
then
  echo
  echo "REFUSING: a form named \"$FORM_NAME\" already exists on this site."
  echo "Creating another would duplicate it. Update the existing form instead,"
  echo "or rename this payload if a separate form is genuinely wanted."
  exit 1
fi

read -r -p "create it? [y/N] " reply
[[ "$reply" == "y" ]] || { echo "aborted"; exit 1; }

curl -sS -X POST "https://www.wixapis.com/form-schema-service/v4/forms" \
  -H "Authorization: $WIX_API_KEY" \
  -H "wix-account-id: $WIX_ACCOUNT_ID" \
  -H "wix-site-id: $SITE_ID" \
  -H "Content-Type: application/json" \
  --data-binary "@$PAYLOAD" \
  -w '\nHTTP %{http_code}\n'

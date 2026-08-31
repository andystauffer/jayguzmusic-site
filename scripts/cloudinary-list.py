#!/usr/bin/env python3
"""List Cloudinary assets. Reads CLOUDINARY_URL from .env (never committed).

Usage:
  python3 scripts/cloudinary-list.py              # newest 100 images
  python3 scripts/cloudinary-list.py video        # videos instead
  python3 scripts/cloudinary-list.py image 500    # more results

Read-only: only ever issues GET to the Admin API's resources endpoint.
"""
import base64, json, os, sys, urllib.parse, urllib.request, re, pathlib

def load_env():
    p = pathlib.Path(__file__).resolve().parent.parent / ".env"
    if p.exists():
        for line in p.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

def creds():
    load_env()
    url = os.environ.get("CLOUDINARY_URL", "")
    m = re.match(r"cloudinary://(\d+):([^@]+)@([\w-]+)", url)
    if m:
        return m.group(1), m.group(2), m.group(3)
    # or the three parts separately
    key    = os.environ.get("CLOUDINARY_API_KEY", "").strip()
    secret = os.environ.get("CLOUDINARY_API_SECRET", "").strip()
    cloud  = os.environ.get("CLOUDINARY_CLOUD_NAME", "").strip()
    missing = [n for n, v in
               (("CLOUDINARY_API_KEY", key), ("CLOUDINARY_API_SECRET", secret),
                ("CLOUDINARY_CLOUD_NAME", cloud)) if not v]
    if missing:
        sys.exit("Missing in .env: " + ", ".join(missing))
    if not key.isdigit():
        sys.exit(f"CLOUDINARY_API_KEY should be all digits; got {len(key)} chars "
                 f"starting '{key[:4]}'. That looks like the API *secret* — "
                 f"the key is the numeric one next to it in the console.")
    return key, secret, cloud

def main():
    kind = sys.argv[1] if len(sys.argv) > 1 else "image"
    n    = sys.argv[2] if len(sys.argv) > 2 else "100"
    key, secret, cloud = creds()
    qs  = urllib.parse.urlencode({"max_results": n, "direction": "desc"})
    req = urllib.request.Request(
        f"https://api.cloudinary.com/v1_1/{cloud}/resources/{kind}?{qs}")
    req.add_header("Authorization",
        "Basic " + base64.b64encode(f"{key}:{secret}".encode()).decode())
    try:
        data = json.load(urllib.request.urlopen(req, timeout=30))
    except urllib.error.HTTPError as e:
        sys.exit(f"Cloudinary returned {e.code}: {e.read().decode()[:300]}")

    rows = data.get("resources", [])
    print(f"{len(rows)} {kind}(s) in cloud '{cloud}', newest first\n")
    for r in rows:
        dims = f"{r.get('width','?')}x{r.get('height','?')}"
        size = f"{r.get('bytes',0)/1_048_576:.1f}MB"
        print(f"  {r['created_at'][:10]}  {dims:>11}  {size:>8}  {r['public_id']}.{r['format']}")
        print(f"      {r['secure_url']}")

if __name__ == "__main__":
    main()

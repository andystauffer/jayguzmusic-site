#!/usr/bin/env python3
"""Upload local images to Cloudinary. Reads credentials from .env (never committed).

Usage:  python3 scripts/cloudinary-upload.py <file>:<public_id> [...]

Signed upload: signature is sha1 of the sorted params plus the API secret.
Prints the resulting public_id so the delivery URLs can be wired up.
"""
import hashlib, json, os, pathlib, re, subprocess, sys, time

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
    key    = os.environ.get("CLOUDINARY_API_KEY", "").strip()
    secret = os.environ.get("CLOUDINARY_API_SECRET", "").strip()
    cloud  = os.environ.get("CLOUDINARY_CLOUD_NAME", "").strip()
    if not (key and secret and cloud):
        sys.exit("Missing Cloudinary credentials in .env")
    return key, secret, cloud

def upload(path, public_id, key, secret, cloud):
    ts = str(int(time.time()))
    # signed params must be sorted by key, joined k=v with &, then the secret appended
    params = {"public_id": public_id, "timestamp": ts}
    to_sign = "&".join(f"{k}={params[k]}" for k in sorted(params))
    sig = hashlib.sha1((to_sign + secret).encode()).hexdigest()

    out = subprocess.run([
        "curl", "-s", "-X", "POST",
        f"https://api.cloudinary.com/v1_1/{cloud}/image/upload",
        "-F", f"file=@{path}",
        "-F", f"public_id={public_id}",
        "-F", f"timestamp={ts}",
        "-F", f"api_key={key}",
        "-F", f"signature={sig}",
    ], capture_output=True, text=True).stdout

    try:
        data = json.loads(out)
    except json.JSONDecodeError:
        return None, out[:300]
    if "error" in data:
        return None, data["error"].get("message", str(data["error"]))
    return data, None

def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    key, secret, cloud = creds()
    for arg in sys.argv[1:]:
        path, _, pid = arg.partition(":")
        if not pid:
            pid = re.sub(r"\.\w+$", "", os.path.basename(path))
        mb = os.path.getsize(path) / 1048576
        data, err = upload(path, pid, key, secret, cloud)
        if err:
            print(f"  ✗ {os.path.basename(path):<40} ({mb:.1f}MB)  {err}")
            continue
        print(f"  ✓ {os.path.basename(path):<40} ({mb:.1f}MB) -> "
              f"{data['public_id']}.{data['format']}  {data['width']}x{data['height']}")

if __name__ == "__main__":
    main()

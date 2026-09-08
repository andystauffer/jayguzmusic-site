# Wix migration — state and runbook

**Updated:** 2026-09-08
**Supersedes:** `HANDOFF_SOP.md` (that documents a Netlify hosting transfer we are no longer doing).

---

## 1. Where things are

| | |
|---|---|
| Repo | `/Users/andystauffer/jayguzmusic-site`, `main`, pushed to `github.com/andystauffer/jayguzmusic-site` |
| Live on Wix | https://jayguzmusic-site-andystauffer-100c.wix-site-host.com |
| Live on Netlify | https://jayguzmusic.netlify.app (`noindex`, kept as a working reference) |
| Target domain | `jayguzmanmusicandevents.com` — **currently serves Jay's own Wix Editor site, not ours** |
| Old domain | `jayguzmusic.com` — a different Wix account entirely, "HOME \| My Site" |

**Phases 0–2 are done.** Remaining: Wix Forms, then the domain.

---

## 2. Wix project

```
appId    2d235353-205d-45c9-a51b-b53c7bc5ff42
siteId   e935d47e-9867-4df5-bd31-9abdb3df3534
```

Created with `npm create @wix/new@latest init`, which also printed **"Business created"** — the project landed under a **new business**, not alongside Jay's existing site. It does not appear in a `site-list/v2/sites/query` against the default account context.

**This matters for the domain.** `jayguzmanmusicandevents.com` is attached to Jay's business (owner account `f549d57e-…`, on which Andy is a contributor, `c1670433-…`). Moving the domain onto this project may mean moving it between businesses, or moving the project. Confirm before promising a cutover date.

Jay's existing site, for reference: `c6da36f6-95ac-4db1-9286-c690672a61a0`, `ODEDITOR`, premium, domain connected.

---

## 3. Build and deploy

```bash
./scripts/build.sh          # assembles dist/client + dist/server
npx @wix/cli@latest release # uploads and publishes
```

`scripts/build.sh` is the deploy boundary and **aborts** rather than ship if it finds a secret-shaped file, if `CLOUDINARY_API_SECRET` appears in the output, or if either `dist/client/index.html` or `dist/server/entry.mjs` is missing.

Never point `outputDirectory` at `.` — the repo root contains `.env`.

---

## 4. How Wix static hosting actually behaves

Established by testing. **Not documented, and Wix's own support agent got it wrong twice** — it diagnosed a SPA routing problem and recommended `/* → /index.html`, which for a non-SPA would serve the homepage at all ten URLs.

**Routing model:** a matching static file is served by the CDN. Anything with no match is handed to the server worker.

| Path | Result |
|---|---|
| `/about.html` | 200, served by the CDN |
| `/about` | no static match → worker → fetches `about.html` → 200 |
| `/about/` | 301 → `/about` |
| `/sitemap.xml` | **404 even when present.** Wix reserves it. Ours is `sitemap-index.xml` |
| extensionless file | serves, but as `application/octet-stream` — unusable for pages |

**Worker constraints, all found the hard way:**
- entry **must** be `worker/entry.mjs` → `dist/server/entry.mjs`. `index.js` gives 500 `ERR_MODULE_NOT_FOUND`
- no `ASSETS` binding; `env.DEPLOYMENT_URL` is how the worker fetches the underlying file
- `outputDirectory` must resolve **inside** the project folder
- `.wix/` is written to the repo root by the CLI. It must be excluded from the build — including it caused two releases to fail with an S3 403

The flat `.html` files remain the real paths, so the worker is an enhancement, not a single point of failure. The same build serves clean URLs natively on Netlify.

---

## 5. Credentials

`.env` (gitignored, `chmod 600`) holds Cloudinary. Wix uses the CLI's OAuth session — `npx @wix/cli@latest login`, no stored secret.

> **Outstanding:** the Cloudinary API secret was pasted into a chat transcript and **should be rotated** — Cloudinary → Settings → API Keys.

`scripts/cloudinary-list.py` (read) and `scripts/cloudinary-upload.py` (signed upload) both read from `.env`.

---

## 6. Remaining work

**Phase 4 — Wix Forms.** Three forms (`consultation`, `coordinator-inquiry`, `song-request`) still carry `data-netlify`. On Wix they fall back to a prefilled `mailto` via `buildEnquiryMailto()` in `assets/js/main.js` — a safety net, not the destination. Wire them to Wix Forms so leads reach Jay's dashboard. **This is the main reason the migration is worth doing.**

**Phase 5 — the domain.** Needs Jay's decision: pointing it here replaces the site he built. Ask whether anything on his version, the ShowReel especially, should come across first. Note his current site already shows **1 form submission** — check Inbox before it is replaced.

**At cutover:** delete the staging-guard block from `netlify.toml`, and confirm the Wix deployment isn't serving `noindex`.

---

## 7. Known-open, smaller

- **No full-band photograph.** The band callout uses a solo show photo as a stand-in.
- **No city-specific photography.** Dallas, Houston and San Antonio share generic performing shots.
- **Four unused reel videos** in Cloudinary: `taylor_Blank_space`, `Morgan_Wallen_Last_night`, `Smashmouth`, `Yeah-_luda_verse`.
- **Trustpilot shows 4.0** despite three 5-star reviews — worth Jay checking his dashboard for one not displaying. His Trustpilot profile is also still registered under `jayguzmusic.com`.
- **Video testimonials and the About video** are commented out in the HTML with restore notes, awaiting real footage.
- **About page says "well over a few hundred songs"**; the catalog holds 162. Jay's own wording, so left alone.

---

## 8. Verification habits that caught real bugs

Check rendered output, not the diff. Specifically:

- Fetch live pages and **strip HTML comments before asserting** — `grep` counts commented-out markup and will tell you something renders when it doesn't.
- Test **individual URLs**, never just the homepage. The Wix 404s were invisible from `/`.
- Headless Chrome **clamps windows to 500px minimum**, so a "390px" screenshot is a squeezed 500px layout. Measure mobile through an iframe.
- For contrast, render with the text hidden and sample the background — sampling with text present hits the glyphs and reports 1:1.

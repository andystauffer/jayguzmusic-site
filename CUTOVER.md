# Cutover plan — Netlify site, Wix as registrar only

**Rewritten:** 2026-09-17, replacing the Netlify-frontend/Wix-backend plan.
**Status:** Site is built and live on Netlify. Nothing on the public domain yet.
**Companion:** `WIX_MIGRATION.md` (project history, established Wix behaviour)

---

## 1. The decision

**This is a Netlify site.** Wix's only remaining role is **DNS for the domain Jay
bought there**. No Wix hosting, no Wix Forms, no Wix backend.

```
  jayguzmanmusicandevents.com
        │  DNS zone hosted at Wix (ns8/ns9.wixdns.net)
        │  A + CNAME  ──────────────────────────────┐
        │                                            ▼
        │                                         Netlify
        │                                    (static site, this repo)
        │                                         │
        │                                    Netlify Forms
        │                                    → email notification to Jay
        │
        └─ MX / SPF / TXT stay pointed at Google Workspace. UNTOUCHED.
```

**What this replaces.** The previous plan used Jay's Wix site as a forms backend.
That was built and tested end to end (three forms on site `c6da36f6`), but it tied
lead capture to a Wix Premium plan we no longer want to depend on — if that plan
ever lapses, submissions stop silently.

**The trade-off we are re-accepting, deliberately.** Netlify Forms was rejected in
the old B2 because *"a lead sitting in a dashboard nobody opens is barely better
than a lost one."* That objection is still valid and is **only** answered by
configuring notification emails (Phase 2). Without that step this is a
regression, not a migration.

---

## 2. Current state

| | |
|---|---|
| Repo | `main`, clean, pushed to `github.com/andystauffer/jayguzmusic-site` |
| Live | `jayguzmusic.netlify.app` — built by `scripts/build.sh`, publishes `dist/client` |
| Domain | `jayguzmanmusicandevents.com` → still Jay's Wix Editor site |
| Netlify account | Andy's. Domain never lives in Netlify, so rollback is a DNS change |
| Staging guard | `X-Robots-Tag: noindex` still on — **must come off at cutover** |
| Clean URLs | Work natively on Netlify. The Wix fall-through worker is now dead weight |

Forms markup is **already correct for Netlify Forms** on all three pages —
matching `form-name` hidden input, honeypot, `data-netlify`. Netlify has already
detected and registered them (proven: it strips `data-netlify` from the served
HTML).

---

## 3. Ground rules

- **Nothing is irreversible until Phase 5.** The site keeps serving throughout.
- **Prefer APIs over clicking.** Auditable, scriptable, and verifiable before and after.
- **Verify rendered output, not the repo.** A host can rewrite your markup after
  deploy — see the trap in §8. Check the live URL.
- **Secrets never go through chat.** `.env` only, gitignored, `chmod 600`.

`[YOU]` = browser or credential.  `[CLAUDE]` = I run it.

---

## 4. Phase 1 — Netlify Forms `[CLAUDE]`

Only `assets/js/main.js` changes. The markup is already right.

Replace the `window.submitWixForm(...)` call with a Netlify Forms POST, keeping
the handler shape and the mailto fallback:

```js
const res = await fetch('/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: new URLSearchParams(data).toString(),   // includes form-name
});
if (!res.ok) throw new Error('HTTP ' + res.status);
```

**Rename the binding attribute.** The handler selects `form[data-wix-form]`,
which is now misleading. Rename to `data-enquiry-form` across the three pages and
`main.js`. **Do not** switch the selector back to `data-netlify` — Netlify strips
that attribute at deploy time and the selector would match nothing in production
(§8). A custom attribute is load-bearing here, not cosmetic.

**Retire the Wix integration.** Remove the `wix-forms.js` script tags from
`index.html`, `event-coordinators.html`, `setlist.html`, and delete
`assets/js/wix-forms.js`. Leave `scripts/wix-forms/` and the three forms on
`c6da36f6` alone for now — harmless, and a working reference until cutover is
proven.

**Test on `jayguzmusic.netlify.app` before going further.** Submit all three
forms; confirm each appears in Netlify → Forms.

---

## 5. Phase 2 — notifications `[YOU]` or `[CLAUDE]` with a token

**Do not skip this.** Netlify → Project → Forms → Notifications → add an outgoing
email notification to Jay for each of the three forms.

Verify by submitting once more and confirming the email actually arrives. A form
that captures silently is the failure this whole phase exists to prevent.

---

## 6. Phase 3 — credentials `[YOU]`

**Netlify personal access token** — User settings → Applications → Personal
access tokens. Put it in `.env` as `NETLIFY_AUTH_TOKEN`. Lets Claude add the
domain, set notifications, check SSL, and read submissions.

**Wix API key with domain permissions** — *optional.* The existing key returns
`403 DOMAINS.READ_DNS_ZONES`; it was scoped to Forms/CRM. Re-scope it only if you
want the DNS records changed by API. Doing those four records by hand, with
Claude verifying by `dig` before and after, is an equally good answer and keeps
the irreversible step under your finger.

---

## 7. Phase 4 — lower the TTL `[YOU]`, a day ahead

In Wix DNS, set TTL to **300s** on the apex `A` records and the `www` `CNAME`.

Highest-value preparatory step in the plan: propagation is TTL-bound, so this
shrinks both the switch window and the rollback window from hours to minutes.

---

## 8. Phase 5 — the switch

**5a `[CLAUDE]` Capture DNS before touching anything.**
`docs/dns-before-cutover.md` holds the 2026-09-10 snapshot. Re-capture it — it is
the rollback reference and must be current.

**5b `[YOU]` or `[CLAUDE]` Add the domain in Netlify.**
Add both apex and `www`. **Copy the exact records Netlify returns** — don't reuse
values from this file or any older runbook; Netlify's addresses change.

**5c `[YOU]` Disconnect the domain from the Editor site in Wix.**
Wix manages A/CNAME automatically while a domain is connected to a site, so the
records aren't editable until this is done. This does **not** delete Jay's site —
it keeps its plan and `wixsite.com` address. Confirm you can still reach it.

**5d Change only `A` and `CNAME`.**

> ⚠️ **Jay runs Google Workspace email on this domain.** Five `MX` records, an SPF
> `TXT`, and two `google-site-verification` `TXT` records are live. Delete or edit
> any of them and **his mail stops.**
>
> If done by API, this is structurally safe: `PATCH /domains/v1/dns-zones/{domain}`
> takes explicit `additions` and `deletions` arrays and is **not** a whole-zone
> replace — records you don't name are untouched. Note the API allows only one
> record object per type per hostname, so changing the apex `A` means deleting the
> existing `A` object and adding a new one carrying Netlify's value(s). That is a
> delete-and-add of the `A` record only; `MX` is never referenced.

**5e `[CLAUDE]` Remove the staging guard.**
Delete the fenced `X-Robots-Tag = "noindex, nofollow"` block from `netlify.toml`
and redeploy. Until this goes, the live domain tells Google not to index it.

**5f `[YOU]` Wait for HTTPS.**
Netlify provisions Let's Encrypt after DNS resolves. Expect a brief certificate
warning. Don't intervene, and don't announce launch until the padlock is clean on
both apex and `www`.

**Expected downtime: none.** The Netlify site is fully live before 5d. During
propagation some visitors resolve to the old site and some to the new, and both
work. A split-audience window, not an outage.

---

## 9. Phase 6 — verify `[CLAUDE]`

Against `https://www.jayguzmanmusicandevents.com`:

| Check | Expect |
|---|---|
| All 10 pages | 200 |
| `/about` clean URL | 200 (native on Netlify) |
| `/about.html` | 200 |
| apex → `www` | 301 |
| `/sitemap-index.xml` | 200 (**not** `/sitemap.xml` — robots.txt points here) |
| `/nonexistent` | 404, not the homepage |
| `X-Robots-Tag` | **absent** |
| `<meta robots>` | `index, follow` |
| Live form submission | appears in Netlify Forms **and** emails Jay |
| `dig MX` | identical to the pre-cutover snapshot |

Then `[YOU]`: Google Search Console — add the domain, submit `sitemap-index.xml`,
request indexing on the homepage.

---

## 10. Phase 7 — cleanup, only after Phase 6 passes

- Delete `worker/` and `wix.config.json`. Remove the worker copy step and the
  `dist/server/entry.mjs` assertion from `scripts/build.sh`.
- Delete `scripts/wix-forms/` and the three forms on `c6da36f6` if Jay wants them
  gone; otherwise leave them.
- Mark the Wix-hosting sections of `WIX_MIGRATION.md` superseded.
- **Rotate the Cloudinary API secret** — outstanding since it was pasted into a
  chat transcript.
- Consider transferring the Netlify project to Jay: Project configuration →
  General → Transfer project. Transfer is free; *adding a member* can require a
  paid seat. A project transfers only to a team where you are an Owner or
  Developer, so the order is: Jay creates his team, adds Andy, Andy transfers,
  Andy steps out.

---

## 11. Rollback

Before 5c there is nothing to roll back — Jay's site is still serving.

After 5d: restore the `A` and `CNAME` records from `docs/dns-before-cutover.md`
and reconnect the domain to the Editor site in Wix. Recovery is bounded by the
TTL, which is why Phase 4 comes a day early.

Nothing in this plan deletes Jay's Editor site, cancels his plan, or touches his
existing form submissions.

---

## 12. Traps already paid for — don't rediscover these

- **Netlify strips `data-netlify` from served HTML.** It detects the form at
  deploy time and removes the attribute. A selector on it matches nothing in
  production — silently, with the visitor still seeing a success page. Bind to a
  custom attribute.
- **Wix reserves `/sitemap.xml`** and 404s it even when the file is present.
  Ours is `sitemap-index.xml`; `robots.txt` points there. Harmless on Netlify,
  but don't "fix" the name back.
- **`bc` isn't guaranteed in Netlify CI.** `build.sh` uses `awk`. Under `set -e` a
  missing binary fails the whole build.
- **`publish` must never be `.`** — the repo root holds `.env`. `build.sh` is the
  deploy boundary and aborts on secret-shaped files.
- **Strip HTML comments before asserting on live output.** `grep` counts
  commented-out markup and will report something renders when it doesn't.
- **Test individual URLs, never just `/`.** The Wix 404s were invisible from the
  homepage.
- **Headless Chrome clamps windows to 500px minimum.** A "390px" screenshot is a
  squeezed 500px layout. Measure mobile through an iframe.

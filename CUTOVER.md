# Cutover plan — Netlify frontend, Wix backend

**Created:** 2026-09-10
**Status:** Phases A and B complete. Phase C (the domain) not started.
**Companion:** `WIX_MIGRATION.md` (project state, established Wix behaviour)

---

## 1. The decision

Host the frontend on **Netlify**. Use **Jay's existing premium Wix site as the backend**
for forms, contacts and inbox. This is Wix's documented *self-managed headless*
migration path, not a workaround.

```
  jayguzmanmusicandevents.com
        │  A / CNAME
        ▼
  Netlify  ──── static site (this repo)
        │
        │  headless client (clientID + anonymous visitor token)
        ▼
  Wix site c6da36f6  ──── Forms · Contacts · Inbox
        └─ Jay's existing Premium plan, unchanged
```

**Why this and not Wix hosting.** Wix's migration doc lists the Premium plan
under *what stays the same*: *"Your Premium plan, which is still required for a
custom domain and for payments."* Jay's existing plan keeps covering the domain,
so this path adds **no new subscription**, needs **no site transfer**, and never
raises the plan-eligibility question. Wix-managed hosting would have required its
own project with its own plan.

It also deletes work: Netlify serves clean URLs natively, so the fall-through
worker — and the four undocumented Wix static-hosting quirks behind it — stop
mattering.

**Consequences**
- Wix headless project `e935d47e` becomes redundant. Leave it (free, harmless); stop deploying to it.
- Jay's Editor site keeps its Premium plan and stays reachable at its `wixsite.com` address as a fallback.
- `worker/` and `wix.config.json` become dead weight. Remove **after** cutover is proven, not before (§7).

---

## 2. Ground rules

- **Nothing is irreversible until §5.** Phases 3 and 4 run while Jay's site keeps serving.
- **Test the frontend at its Netlify address first.** Per Wix: *"This connection
  doesn't depend on domains… which is why you can build and test it against your
  project before you migrate."*
- **Verify rendered output, not the diff.** Strip HTML comments before asserting
  (see `WIX_MIGRATION.md` §8 — this caught real bugs).
- **Secrets never go through chat.** `.env` only, gitignored, `chmod 600`.

`[MANUAL]` = you, in a browser.  `[CLAUDE]` = I run it.

---

## 3. Phase A — Wix backend (no user-visible change)

**A1 `[MANUAL]` ~~Create the headless client.~~ DONE 2026-09-10.**
Dashboard → site `c6da36f6` → Settings → Headless Settings → **Create New Client**.
Copy the **clientID**. This is a public value — it ships in client-side JS.

> Allowed redirect domains are *not* required for form submissions: a submission
> is a direct API call with a visitor token, not a redirect. Only add them if we
> later use Wix-hosted login or checkout pages.

**A2 `[MANUAL]` ~~Create an API key.~~ DONE 2026-09-10.**
Same page → **Manage API Key**. Scope to Forms/CRM if offered. Put it in `.env`:

```
WIX_API_KEY=…
WIX_ACCOUNT_ID=f549d57e-…
```

The key must be generated from `f549d57e` — Wix rejects site-level calls made
with another account's key.

**A3 `[CLAUDE]` ~~Read the existing forms.~~ DONE 2026-09-10.**
```bash
./scripts/wix-forms/read-forms.sh c6da36f6-95ac-4db1-9286-c690672a61a0
```
Confirms the seven experiments and that nothing claims our names.

**A4 `[CLAUDE]` ~~Create the forms.~~ DONE 2026-09-10.**
```bash
./scripts/wix-forms/create-form.sh c6da36f6-95ac-4db1-9286-c690672a61a0 \
  scripts/wix-forms/website-event-consultation.form.json
```
Three forms created on `c6da36f6`, all verified end to end:

| Form | ID | Fields |
|---|---|---|
| Website - Event Consultation | `f3eeeeec-4ab0-4f49-bb73-87075198c48f` | 6 |
| Website - Coordinator Inquiry | `c3eb2afe-4c5e-4c25-88b3-85d97e61d642` | 10 |
| Website - Song Request | `69563c61-5e8a-48c8-8e19-208310e55a71` | 5 |

The script refuses to create a name that already exists.

**A5 `[MANUAL]` ~~Open each form in the dashboard.~~ DONE 2026-09-10.**
Confirm every field renders. **This is the check that matters** — a form whose
fields carry unrecognised `identifier` values is accepted by the API, takes
submissions, and opens *empty* in the editor. Thirty seconds here is worth it.

**A6 `[CLAUDE]` ~~Wire the frontend.~~ DONE 2026-09-10.**
clientID + form IDs into `WIX_FORMS_CONFIG` in `assets/js/wix-forms.js`, rebuild.

---

## 4. Phase B — Netlify becomes the real host

**B1 `[CLAUDE]` ~~Stop publishing the repo root.~~ DONE 2026-09-10.**
`netlify.toml` published `.` — the repo root, which holds `.env`. Now builds
via `./scripts/build.sh` and publishes `dist/client`, putting Netlify behind
the same deploy boundary as Wix, including the secret-shaped-file and
`CLOUDINARY_API_SECRET` aborts.

`build.sh` also had a `bc` dependency in its final size calculation. Harmless
locally, but `bc` isn't guaranteed in Netlify CI and under `set -e` a missing
binary fails the whole build. Switched to `awk`.

**B2 `[CLAUDE]` ~~Keep the Netlify Forms fallback.~~ DROPPED 2026-09-10.**
Wix is the sole capture path. The chain is **Wix → mailto**.

A second capture service meant leads could land in a Netlify dashboard Jay
never opens, which is barely better than losing them — and it needed its own
notification setup to be useful at all. The mailto fallback reaches his actual
inbox, so it is the better failure mode for this business.

`data-netlify` stays on the forms for one narrow case: with JS disabled the
handler never runs, and the native POST is caught by Netlify instead of being
answered by the static `/thank-you` page, which would show a success screen
and drop the enquiry.

Trade-off, stated plainly: if Wix is unreachable the visitor has to actually
complete the mailto, and some won't. Netlify Forms would have caught those
silently — in a place nobody checks.

**B3 `[CLAUDE]` Netlify strips `data-netlify` from the served HTML. DONE 2026-09-10.**
Found only by fetching the deployed page. Netlify detects a form at deploy time
and then removes `data-netlify` and `netlify-honeypot` from the HTML it serves:

```
local  <form id="consult-form" ... data-netlify="true" netlify-honeypot="bot-field">
live   <form action='/thank-you' id='consult-form' method='POST' name='consultation'>
```

`main.js` selected `form[data-netlify]`, so in production **the selector matched
nothing**, no handler bound, and every enquiry would have native-POSTed into
Netlify Forms instead of Wix — silently, with the visitor still seeing the
success page. The handler now binds to `data-wix-form`, our own attribute,
which survives post-processing.

> The general lesson, and the reason `WIX_MIGRATION.md` §8 says to check
> rendered output: **a host can rewrite your markup after you deploy it.**
> Anything the JS depends on in the HTML has to be verified on the live URL,
> not in the repo.

**B4 `[CLAUDE] + [MANUAL]` ~~End-to-end form test.~~ DONE 2026-09-10.**
All three forms submitted over the real path — anonymous visitor token, then
`POST /form-submission-service/v4/submissions` keyed by field target. Every
field stored (6, 10, 5), every submission reached Submissions, and one merged
Contact was created from the shared email. Test rows and the test contact
deleted afterwards; Jay's own 2026-08-29 lead verified untouched.

> **A 200 can come back `PENDING`, not `CONFIRMED`.** Wix confirms
> asynchronously within seconds, with no further call from us. A `PENDING`
> submission is not yet queryable and **404s on GET** — which looks exactly
> like a failed submission and isn't. Per the docs: *"read it from the
> response rather than assuming."* Verify a test submission a minute later,
> never immediately.

> Two other traps found here: the submissions query ignores a `formId` filter
> and needs `filter.namespace` instead (a `formId` filter silently returns 0,
> not an error); and the id returned by the POST is not always the id the
> confirmed row ends up with.

**B5 `[MANUAL]` ~~Decide the Netlify account owner.~~ DECIDED 2026-09-10.**
Ship from Andy's Netlify account. Hand it over later if and when it matters.

Safe because **the domain never lives in Netlify.** DNS stays in Jay's Wix
account and merely points at Netlify, so the worst case is repointing an `A`
record — minutes, not a recovery operation.

When handing over, the mechanism is **transfer the project**, not "add Jay as
an owner": per Netlify's docs *"depending on your team plan, you may need to
upgrade in order to add new members"*, so adding a member can mean paying for
a seat. Transfer is free — Project configuration > General > Transfer project.

One constraint to plan around: a project transfers only *"to any team where you
are an Owner or Developer"*, and transfers *"between teams with no shared Owners
or Developers"* need a support ticket. So the order is: Jay creates his team,
adds Andy to it, Andy transfers the project, Andy steps out.

---

## 5. Phase C — the domain (the only risky step)

**C1 `[MANUAL]` Lower the DNS TTL first — do this a day ahead.**
In Wix's DNS panel for `jayguzmanmusicandevents.com`, drop the TTL on the `A`
and `CNAME` records to 300s. Propagation is TTL-bound; this shrinks the switch
window from hours to minutes and is the single highest-value preparatory step.

**C2 `[MANUAL]` Add the custom domain in Netlify.**
Netlify → Domain management → add `jayguzmanmusicandevents.com` and
`www.jayguzmanmusicandevents.com`. **Copy the exact records Netlify shows you** —
apex `A` and `www` `CNAME`. Do not reuse values from memory or an old runbook;
Netlify's addresses change.

**C3 `[MANUAL]` Disconnect the domain from the Editor site.**
Wix manages A/CNAME automatically while a domain is connected to a site, so those
records aren't editable until it's disconnected. In Wix: Domains → the domain →
disconnect from site / point to an external site.

Per Wix, this **does not delete the Editor site** — it keeps its plan and its
`wixsite.com` address. Confirm you can still reach it before proceeding.

**C4 `[MANUAL]` Set the records to Netlify's values.**

> **Change only `A` and `CNAME`.** Wix's migration doc is explicit: email keeps
> working *"as long as you change only the `A` and `CNAME` records that route
> visitors to your project, not the separate `MX`, `SPF`, `DKIM`, and `DMARC`
> records that route email."* Touch those and **Jay's email breaks.**

**C5 `[CLAUDE]` Remove the staging guard.**
Delete the `X-Robots-Tag = "noindex, nofollow"` block from `netlify.toml`
(it's fenced and labelled). Until this goes, the live domain tells Google not
to index it. Redeploy.

**C6 `[MANUAL]` Wait for HTTPS.**
Netlify provisions a Let's Encrypt certificate after DNS resolves. The site may
show a certificate warning for a few minutes. Don't intervene; don't announce
launch until the padlock is clean on both apex and `www`.

### Expected downtime: none

The Netlify site is fully live and tested before C4. During propagation some
visitors resolve to the old site and some to the new — **both work**. It is a
split-audience window, not an outage. With TTL at 300s it should be minutes.

---

## 6. Phase D — verify the live domain

`[CLAUDE]` Run against `https://www.jayguzmanmusicandevents.com`:

| Check | Expect |
|---|---|
| `/` and all 9 pages | 200 |
| `/about` (clean URL) | 200 — native on Netlify, no worker |
| `/about.html` | 200 |
| `/about/` | 301 → `/about` |
| apex → `www` | 301 |
| `/sitemap-index.xml` | 200 (**not** `/sitemap.xml` — Wix reserved it; Netlify doesn't, but our sitemap is named this and robots.txt points here) |
| `/nonexistent` | 404, not the homepage |
| `X-Robots-Tag` header | **absent** |
| Page `<meta robots>` | `index, follow` |
| Live form submission | lands in Wix Submissions + Contacts |
| `dig MX` | unchanged from before cutover |

`[MANUAL]` Then: Google Search Console — add the domain, submit
`sitemap-index.xml`, request indexing on the homepage.

---

## 7. Phase E — cleanup (only after D passes)

- Delete `worker/`, and the `dist/server/entry.mjs` requirement plus the worker
  copy step from `scripts/build.sh`.
- Delete `wix.config.json`.
- Fold this file's outcome into `WIX_MIGRATION.md`; mark the Wix-hosting
  sections superseded.
- Leave `e935d47e` alone — free, and a working reference.
- **Rotate the Cloudinary API secret** (outstanding from `WIX_MIGRATION.md` §5 —
  it was pasted into a chat transcript).

---

## 8. Rollback

Before C3, there is nothing to roll back — Jay's site is still serving.

After C4, if something is wrong: **restore the original A/CNAME records in Wix
and reconnect the domain to the Editor site.** Recovery is bounded by the TTL,
which is why C1 matters. Screenshot the original DNS records before changing
them — that screenshot *is* the rollback plan.

Nothing in this plan deletes Jay's Editor site, cancels his plan, or touches his
existing form submissions.

---

## 9. Open questions

*(Both earlier questions are now closed: `song-request` is wired to Wix with the
setlist carried in its own `selected_songs` field, and four experiment forms
were deleted, so the site sits at 6/10 with room to spare.)*

Nothing outstanding. Phases A and B are complete; Phase C is the remaining work.

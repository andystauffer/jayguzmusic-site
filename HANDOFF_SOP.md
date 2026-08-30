# SOP — Transfer hosting to Jason's Netlify account

**Written:** 2026-08-30
**Goal:** Move hosting and billing for jayguzmusic.com off the Proofmap Netlify team and onto Jason's own Netlify account, at no cost to him.
**Client-facing companion doc:** the plain-language version for Jason lives at the artifact URL in the 2026-08-30 session notes. This file is the operator runbook — it is not for Jason.

---

## 1. State at time of writing

| Thing | Value |
|---|---|
| Repo | `andystauffer/jayguzmusic-site` — **public**, **user-owned**, default branch `main` |
| Netlify project | `jayguzmusic` under the **Proofmap** team (Free plan) |
| Staging URL | https://jayguzmusic.netlify.app |
| Link method | Netlify GitHub App (no deploy key or classic webhook on the repo) |
| Custom domain | **Not attached.** Jason owns the registrar. |
| Search indexing | Blocked site-wide by `X-Robots-Tag` in `netlify.toml` |
| Forms | `consultation`, `coordinator-inquiry`, `song-request` — registered, no notification email set |
| Build | None. Static. Publish directory `.` |

Netlify plan facts that drive this SOP (verified 2026-08-30, pricing is credit-based now — older advice about Starter tiers and a 100/month form cap is stale):

- Free plan includes custom domains with SSL.
- Form submissions are free and **unlimited** on all credit-based plans.
- Free plan **cannot add team member seats**. Reviewer role is free/unlimited but only sees Deploy Previews and branch deploys, not production.
- A project transfer needs Owner on the source team **and** Owner/Developer on the destination team. Two Free teams therefore cannot transfer to each other self-serve — it needs a Netlify support ticket.

**Because of that last point, this SOP rebuilds the site under Jason's account rather than transferring it.** Nothing is lost: no domain attached, no real form submissions, trivial deploy history.

---

## 2. Inputs to collect before starting

Do not begin until all three are in hand:

- [ ] Jason's **GitHub username** (or confirmation he needs to create an account)
- [ ] Jason's **email** for form notifications
- [ ] Jason available for a ~20 min screen share, or willing to follow the client-facing doc

---

## 3. The repo-access decision

This is the one genuinely uncertain step. Resolve it early — it changes everything downstream.

**The problem:** Netlify support states that linking a repo requires *administrative* permissions, because linking installs a webhook and deploy key. On a **user-owned** repo, collaborators can only be granted write — admin is owner-only. The granular admin role exists only on organization repos.

**The ambiguity:** the current link uses the modern GitHub App, which creates no deploy key or webhook, so the old constraint may not apply. Netlify's docs hedge ("may need administrative privileges"). The definitive support answer predates the App.

**Do not try to resolve this by reading. Test it — it is cheap and non-destructive:**

> Have Jason create his Netlify account, start **Add new site → Import an existing project → GitHub**, and authorize the Netlify GitHub App. If `jayguzmusic-site` appears in his repo list, path A works. If it does not appear — even after "Configure Netlify on GitHub" — fall back to path B.

### Path A — repo stays with Andy (preferred if the test passes)
Jason is a write collaborator. Andy keeps ownership of the code.

### Path B — transfer the repo to Jason (fallback, and the more consistent end state)
Jason already owns the domain, hosting, and form data. Owning the code is consistent with that, and it removes the permission problem entirely because he becomes repo admin. Andy is added back as a collaborator and keeps working exactly as now — write access is all that's needed to push.

A third option, moving the repo into a GitHub org where Jason gets repo admin, is available but is more setup than this project warrants. Use it only if Andy must retain ownership for a reason that emerges later.

---

## 4. Procedure

### Step 1 — Grant Jason repo access *(Andy)*

```bash
gh api -X PUT repos/andystauffer/jayguzmusic-site/collaborators/JASON_USERNAME \
  -f permission=push
```

Verify the invite is pending:

```bash
gh api repos/andystauffer/jayguzmusic-site/invitations \
  --jq '.[] | {invitee:.invitee.login, permission:.permissions}'
```

### Step 2 — Jason accepts *(Jason)*
GitHub emails the invitation. Confirm it landed:

```bash
gh api repos/andystauffer/jayguzmusic-site/collaborators --jq '.[].login'
# expect: andystauffer, JASON_USERNAME
```

### Step 3 — Jason creates his Netlify account *(Jason)*
Sign up at netlify.com **using GitHub login** — it makes step 4 smoother. Free plan. No card.

### Step 4 — Run the repo-access test from §3 *(Jason, Andy watching)*
If the repo does not appear, stop and execute Path B:

```bash
# Path B — transfer repo ownership to Jason, then re-add Andy
gh api -X POST repos/andystauffer/jayguzmusic-site/transfer \
  -f new_owner=JASON_USERNAME
# After Jason accepts, he runs (or does via UI):
#   gh api -X PUT repos/JASON_USERNAME/jayguzmusic-site/collaborators/andystauffer -f permission=push
# Then update the local remote:
git remote set-url origin https://github.com/JASON_USERNAME/jayguzmusic-site.git
git remote -v
```

### Step 5 — Create the site *(Jason)*
**Add new site → Import an existing project → GitHub → `jayguzmusic-site`**

- Build command: **empty**
- Publish directory: `.`
- Branch: `main`

Everything else (redirects, headers, noindex guard) comes from `netlify.toml` automatically. Do **not** hand-configure redirects in the UI.

### Step 6 — Verification gate *(Andy)*

Set `NEW` to Jason's new site URL, then run all of it. **Every check must pass before step 7.**

```bash
NEW=https://JASONS-SITE.netlify.app

# a) noindex still active on every page (must print noindex 10x)
for u in / /about /setlist /event-coordinators /wedding-band-austin \
         /corporate-events-austin /private-parties-austin \
         /wedding-band-dallas /wedding-band-houston /wedding-band-san-antonio; do
  printf "%-28s %s\n" "$u" "$(curl -sI $NEW$u | grep -i x-robots-tag | tr -d '\r')"
done

# b) redirects firing (all must be 301)
for u in /index.html /about.html /setlist.html /events/weddings /events/weddings.html; do
  printf "%-28s %s\n" "$u" "$(curl -s -o /dev/null -w '%{http_code}' $NEW$u)"
done

# c) forms registered — data-netlify must be CONSUMED (served count = 0)
for u in / /setlist /event-coordinators; do
  printf "%-22s served-data-netlify=%s\n" "$u" "$(curl -s $NEW$u | grep -c 'data-netlify')"
done

# d) 404 works
curl -s -o /dev/null -w '%{http_code}\n' $NEW/does-not-exist   # expect 404
```

Expected: (a) ten `noindex, nofollow`; (b) all `301`; (c) all `0`; (d) `404`.

Then Jason sets **Forms → Settings → notification email** and Andy submits one test enquiry per form to confirm delivery and the `/thank-you` redirect. Delete the three test submissions afterward.

### Step 7 — Retire the Proofmap site *(Andy)*

> **Gate: only after every check in step 6 passes.**
>
> Until this is done, **two Netlify sites deploy from the same repo on every push.** Both stay live, both register the same three forms, and submissions split unpredictably between two dashboards — an enquiry can land in an inbox nobody is watching.

Proofmap team → `jayguzmusic` → **Project configuration → General → Delete project**.

Confirm it is gone:

```bash
curl -s -o /dev/null -w '%{http_code}\n' https://jayguzmusic.netlify.app/   # expect 404
```

---

## 5. Rollback

Before step 7, rollback is free — delete Jason's site, the Proofmap one is untouched.

After step 7, the Proofmap site is gone but **nothing is lost**: the repo is the source of truth and `netlify.toml` carries every setting. Re-import it to any Netlify account in about five minutes.

Irreversible actions in this SOP: deleting the Proofmap project (step 7) and transferring the GitHub repo (step 4, Path B — reversible only by Jason transferring it back).

---

## 6. Launch day — separate, later

Do **not** fold these into the handoff. They happen only when the outstanding assets land.

1. Delete the `STAGING GUARD` block at the top of `netlify.toml` (removes `X-Robots-Tag`).
2. Jason attaches `jayguzmusic.com` in his Netlify → **Domain management**, and updates DNS at his registrar.
3. Confirm apex → www redirect works and SSL is issued.
4. Verify `X-Robots-Tag` is **gone** and `robots.txt` still reads `Allow: /`.
5. Submit `https://www.jayguzmusic.com/sitemap.xml` to Google Search Console.

Blocking launch as of 2026-08-30: **7 missing hero images** and **2 placeholder YouTube IDs** (`YOUTUBE_VIDEO_ID_1` / `_2` in `index.html`). See `PRE_LAUNCH.md`.

---

## 7. Assets left on Proofmap accounts

Flag to Jason; not part of this transfer.

- **Cloudinary** (cloud `dja4ppkvq`) serves all 9 reel videos plus poster frames, referenced from `index.html` and `setlist.html`. It stays on Andy's account. If the relationship ends, the site loses its video. Moving it means re-uploading and rewriting 25 URLs.

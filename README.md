# jayguzmanmusicandevents.com

Marketing site for Jason "Jay" Guzman — Austin-based event pianist, vocalist, and
live entertainer.

**Production URL:** https://www.jayguzmanmusicandevents.com/ *(cutover pending — see `CUTOVER.md`)*
**Staging:** https://jayguzmusic.netlify.app (carries `X-Robots-Tag: noindex` until cutover)

## Architecture

Static HTML / CSS / vanilla JS — no framework. **Netlify** serves the frontend;
**Wix** is the backend for forms, contacts and inbox, reached from the browser
over a headless client. Jay's existing Wix Premium plan covers the custom domain.

```
  jayguzmanmusicandevents.com → Netlify (static)
                                    │ headless client
                                    ▼
                          Wix site c6da36f6 — Forms · Contacts · Inbox
```

Every page is a flat `.html` file at the repo root, so the file path *is* the
URL. Netlify serves `/about` from `about.html` natively and 301s `/about/` →
`/about`; no rewrite rules are needed, and the same build works on any static
host.

## Folder structure

```
jayguzmusic-site/
├── index.html                    # Home
├── about.html
├── setlist.html                  # Interactive song catalog
├── event-coordinators.html       # B2B page for planners
├── wedding-band-{austin,dallas,houston,san-antonio}.html
├── corporate-events-austin.html
├── private-parties-austin.html
├── thank-you.html                # Form confirmation
├── 404.html
├── robots.txt
├── sitemap-index.xml             # NOT sitemap.xml — see WIX_MIGRATION.md §4
├── netlify.toml                  # headers, redirects, caching, build config
├── assets/
│   ├── css/styles.css
│   └── js/
│       ├── main.js               # nav, carousels, form submit handler
│       └── wix-forms.js          # Wix Forms submission layer
├── scripts/
│   ├── build.sh                  # assembles dist/ — the deploy boundary
│   ├── cloudinary-*.py           # media helpers (read .env)
│   └── wix-forms/                # form schema + create/read scripts
├── worker/                       # Wix-hosting only; redundant on Netlify
└── dist/                         # build output, gitignored
```

Images and video are served from Cloudinary, not the repo.

## Build

There **is** a build step. `scripts/build.sh` assembles `dist/client` from the
served files only and is the deploy boundary: it aborts rather than ship a
secret-shaped file, or if `CLOUDINARY_API_SECRET` appears in the output.

```bash
./scripts/build.sh
```

Never point a host's publish directory at `.` — the repo root contains `.env`.

## Deploy

Netlify builds from the repo: `command = "./scripts/build.sh"`,
`publish = "dist/client"` (see `netlify.toml`).

```bash
npx netlify deploy --prod        # manual deploy
```

## Forms

Three forms — `consultation`, `coordinator-inquiry`, `song-request`.

All three post to **Wix Forms** on Jay's premium site, which is the single
capture path — submissions reach his dashboard and create a contact. If Wix
can't be reached the enquiry falls back to `mailto:`, which lands in an inbox
he actually reads. There is deliberately no second capture service.

`data-netlify` remains on the forms only so that a JS-disabled native POST is
caught by Netlify rather than answered by the static `/thank-you` page.

`song-request` carries one extra field: the set list the visitor built on the
page lives in a JS array, so a capture-phase submit listener copies it into a
hidden input before `main.js` reads FormData. Capture matters — `main.js` binds
in the bubble phase and would otherwise send an empty set list.

## Local preview

```bash
python3 -m http.server 8000      # then visit http://localhost:8000
```

Clean URLs won't resolve locally — `python3 -m http.server` serves literal paths.
Test `/about.html`, or run `npx netlify dev` to match production routing.

## Docs

| File | What it is |
|---|---|
| `CUTOVER.md` | **Current** — the Netlify cutover runbook |
| `WIX_MIGRATION.md` | Project state; Wix behaviour established by testing |
| `HANDOFF_SOP.md` | Superseded |
| `PRE_LAUNCH.md` | Superseded |

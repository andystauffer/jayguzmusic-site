# jayguzmusic.com

Marketing site for Jason "Jay" Guzman — Austin-based event pianist, vocalist, and live entertainer.

**Production URL:** https://www.jayguzmusic.com/

## Stack

Static HTML / CSS / vanilla JS. No build step. No framework. Drop the folder onto any static host.

## Folder structure

```
jayguzmusic-site/
├── index.html               # Home
├── about.html               # About / bio
├── setlist.html             # Interactive song catalog
├── event-coordinators.html  # B2B page for planners
├── thank-you.html           # Form confirmation
├── 404.html                 # Not-found page
├── robots.txt
├── sitemap.xml
├── netlify.toml             # Netlify config (headers, redirects, caching)
├── vercel.json              # Vercel config (headers, redirects, clean URLs)
├── PRE_LAUNCH.md            # Pre-launch checklist
├── events/
│   ├── weddings.html
│   ├── corporate.html
│   ├── rehearsal-dinners.html
│   └── private-parties.html
└── assets/
    ├── css/styles.css
    ├── js/main.js
    └── images/              # Replace placeholders before launch — see PRE_LAUNCH.md
```

## Deploy

### Netlify (drag-and-drop)
1. Log in at https://app.netlify.com
2. Drag the `jayguzmusic-site/` folder onto the Sites dashboard
3. Connect custom domain `www.jayguzmusic.com` under Domain Settings
4. Forms (consultation, coordinator-inquiry, song-request) work automatically — view submissions under Forms tab

### Netlify (CLI)
```bash
npm i -g netlify-cli
cd jayguzmusic-site
netlify deploy --prod
```

### Vercel (CLI)
```bash
npm i -g vercel
cd jayguzmusic-site
vercel --prod
```

Forms are wired for Netlify (`data-netlify="true"`). If deploying to Vercel, replace the form `action` with a third-party form handler (Formspree, Basin, etc.) or a Vercel serverless function.

## Local preview

```bash
cd jayguzmusic-site
python3 -m http.server 8000
# Visit http://localhost:8000
```

## Before going live

See [PRE_LAUNCH.md](./PRE_LAUNCH.md) for the full checklist (real photos, real video URLs, real testimonials, analytics, form notifications).

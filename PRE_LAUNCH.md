# Pre-Launch Checklist

> **SUPERSEDED (2026-09-10).** This describes a launch on `www.jayguzmusic.com`
> — a different domain on a different Wix account — and a repo whose images were
> local placeholders. Images moved to Cloudinary in `e83d525`; the target domain
> is now `jayguzmanmusicandevents.com`. Kept for the photography and copy notes
> only. For current state see `WIX_MIGRATION.md`; for the launch steps see
> `CUTOVER.md`.

Domain locked in: **www.jayguzmusic.com** ✅

## 1. Confirm contact email

The site uses `jayguzmusic@gmail.com` as the public contact email. If a different address is preferred, search-and-replace across:
- All `*.html` files
- `robots.txt`, `sitemap.xml`, `netlify.toml`
- `PRE_LAUNCH.md`

Also update the footer agency credit in `index.html` (`<a href="#">Your Agency</a>`).

## 2. Image Placeholders
All in `assets/images/` — currently background colors stand in. Replace with real photography (recommend ~1600×900 hero, ~1000×1200 portrait, ~800×800 detail shots, all <300KB optimized JPGs).

| File | Used in | Notes |
|---|---|---|
| `og-image.jpg` | Open Graph share image | 1200×630 |
| `about-hero-placeholder.jpg` | about.html hero | Wide, atmospheric performance shot |
| `about-portrait-placeholder.jpg` | about.html | Vertical portrait, 4:5 |
| `event-wedding-placeholder.jpg` | index.html event card | Wedding scene |
| `event-corporate-placeholder.jpg` | index.html event card | Corporate scene |
| `event-rehearsal-placeholder.jpg` | index.html event card | Rehearsal/intimate dinner |
| `event-party-placeholder.jpg` | index.html event card | Party scene |
| `wedding-hero-placeholder.jpg` | events/weddings.html hero | |
| `wedding-detail-placeholder.jpg` | events/weddings.html | Square 1:1 |
| `corporate-hero-placeholder.jpg` | events/corporate.html hero | |
| `rehearsal-hero-placeholder.jpg` | events/rehearsal-dinners.html hero | |
| `rehearsal-detail-placeholder.jpg` | events/rehearsal-dinners.html | 4:5 |
| `party-hero-placeholder.jpg` | events/private-parties.html hero | |
| `party-detail-placeholder.jpg` | events/private-parties.html | Square |
| `ec-hero-placeholder.jpg` | event-coordinators.html hero | |
| `full-band-placeholder.jpg` | index.html band callout | |

## 3. Video Content
**Performance clips** (`index.html`, six tiles in `#clips` section):
- Currently `data-video-src="#"`. Replace with Cloudinary URLs (or direct MP4 URLs).
- Recommended: 30-second MP4s, 720p, ~3-5MB each.
- Update the `aria-label` and visible label per clip to match each clip's content.

**YouTube testimonial videos** (`index.html` `.yt-grid` section):
- Replace `YOUTUBE_VIDEO_ID_1` and `YOUTUBE_VIDEO_ID_2` with real YouTube video IDs.

## 4. Testimonials
Current testimonial copy (Sarah M., Diane T., Patricia G., Emily & Marcus R., Amanda K., etc.) is placeholder text designed for tone. Replace with real client quotes before launch.

## 5. Forms (Netlify)
Three forms wired with `data-netlify="true"`:
- `consultation` (index.html)
- `coordinator-inquiry` (event-coordinators.html)
- `song-request` (setlist.html)

After first Netlify deploy:
1. Confirm all three forms appear in the Netlify dashboard under **Forms**.
2. Add an email notification → `jayguzmusic@gmail.com`.
3. Enable spam protection (reCAPTCHA or Akismet) under Form Settings.

If deploying to Vercel instead, swap each form `action` for a third-party endpoint (Formspree, Basin) or a Vercel serverless function — Netlify Forms only work on Netlify.

## 6. Analytics & SEO
- [ ] Add Google Analytics / Plausible / Fathom snippet to `<head>` of all pages.
- [ ] Verify DNS: `www.jayguzmusic.com` → Netlify/Vercel; apex `jayguzmusic.com` → 301 to www (already configured in `netlify.toml`).
- [ ] Submit `https://www.jayguzmusic.com/sitemap.xml` to Google Search Console.
- [ ] Test Open Graph previews via opengraph.xyz once `og-image.jpg` is in place.

## 7. Final QA
- [ ] Test all 3 forms end-to-end (submit → thank-you page → email received).
- [ ] Verify mobile nav hamburger works on all 8 pages.
- [ ] Verify song catalog drag-to-reorder, search, send-to-email, and copy-to-clipboard.
- [ ] Lighthouse audit (target 90+ on Performance, Accessibility, SEO).
- [ ] Cross-browser test: Safari, Chrome, Firefox, mobile Safari, mobile Chrome.
- [ ] Confirm SSL certificate is active (auto on Netlify/Vercel).

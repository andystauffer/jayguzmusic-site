# Site updates from Jay — implementation plan

**Source:** Jay's email "Updates for Website", 2026-10-15 (jayguzmusic@gmail.com)
**Written:** 2026-10-19
**Status:** All four items done.
- 3.2 (Instagram + `sameAs`) and 3.4 (Guitar): PR #1, live as `b6fa315` on 2026-10-19 21:16Z.
- 3.3 (About copy plus the homepage line): approved by Andy as Jay's proxy; PR #2, live as
  `707e2bd` on 2026-10-19 21:24Z.
- 3.1 (showreel): Jay uploaded the reel to his new channel `@JayGuzmanMusicEvents` as
  `lFoXYmqQmTI` (public, embeddable, 5:00). The embed is swapped on branch
  `claude/new-showreel`. The copy changed from "Two minutes" / "a Couple of Minutes" to
  "Five minutes" / "a Few Minutes", and the channel is added to `sameAs`.
- Follow-up from Jay (text, 2026-10-20): the city pages overstated his Spanish. San Antonio said he
  "grew up performing in Spanish as much as English", and Dallas/Houston claimed "extensive Latin
  repertoire". Andy, as Jay's proxy, set the line: Puerto Rican roots and a handful of Spanish-language
  songs he plays well, but not a fully bilingual act. Rewritten on branch `claude/spanish-claims`.

---

## 1. Deployment review (as of 2026-10-19)

| Check | Result |
|---|---|
| Production URL | `https://www.jayguzmanmusicandevents.com/` — 200 on `/`, `/about`, `/setlist`, `/event-coordinators`, `/wedding-band-austin` |
| Apex → `www` | 301 (Netlify-managed, as intended) |
| Live deploy | `664503f`, deployed 2026-09-17 18:27Z, state `ready`, branch `main` |
| Repo vs live | `origin/main` = `664503f` = live. Nothing undeployed, no drift |
| Deploys since cutover | None. These updates will be the first post-launch content change |

The site is healthy. Things from `CUTOVER.md` §13 that are still open, outside
the scope of Jay's email:

- **GA4:** not wired up. No page has a `googletagmanager` tag. Still waiting on
  the Measurement ID from Jay (§13.3).
- **Phase 7 cleanup:** `worker/` and `wix.config.json` are still in the repo, and
  `scripts/build.sh` still copies the worker and asserts `dist/server/entry.mjs`.
- **Cloudinary API secret:** still not rotated.
- **Netlify transfer to Jay, Wix wind-down, Search Console:** waiting on Jay (§13.1, 13.2, 13.4).

---

## 2. What Jay asked for

1. **Showreel:** replace the old JayGuzMusic reel everywhere it appears with
   the new "Jay Guzman Music & Events" one.
2. **Instagram:** point every link on the site at the new business account,
   `https://www.instagram.com/jayguzmanmusicandevents/`.
3. **About page:** replace the "full band" line with something more honest
   about a solo performer.
4. **About page, Guitar section:** remove "electric". He plays acoustic only.

---

## 3. Work items

### 3.1 Showreel `[JAY or ANDY]` then `[CLAUDE]`

**Where the reel appears:** only once, the "01 — The Highlight Reel" block on
the homepage (`index.html:283–288`). It's a YouTube embed of `g79shq0yjY0` (the old
reel). No other page embeds it or links to it, and there's no `VideoObject` or
`og:video` metadata to update. "Across the site" means this one embed.

**The new video:** `JG Music & Events Showreel.mp4`, in Jay's shared Drive
folder "Andy Project". Drive file id `1QABgUyOOlJ17aQjoLlXDUpHU0-2NAzp7`,
**450 MB**, last modified 2026-08-11.

**Hosting decision — YouTube, not Cloudinary.**
- The current embed is already YouTube (`youtube-nocookie.com`), so the
  markup, CSS (`.perf-hero__embed`) and lazy-loading stay exactly as they are.
- 450 MB is over Cloudinary's 100 MB per-video limit on the free plan. Hosting
  it there would mean transcoding first and paying for bandwidth on every play.
- YouTube gives adaptive streaming and mobile playback, and a reel on Jay's own
  channel helps people find him.

**Step A `[JAY]` (preferred):** Jay uploads the file to his YouTube channel
as Public or Unlisted, titled "Jay Guzman Music & Events — Showreel", and
sends the URL. *Alternative `[ANDY]`:* Andy uploads it, but then the
video belongs to Andy's account. Avoid that: it's the same ownership problem as
the Netlify project.

**Step B `[CLAUDE]`:** in `index.html`:
- Replace the video id `g79shq0yjY0` with the new id in the iframe `src` (keep
  `youtube-nocookie.com/embed/<id>?rel=0`).
- Change the iframe `title` to `Jay Guzman Music & Events — Showreel`.
- **Check the copy against the new cut.** The heading "Watch a Couple of
  Minutes." and the sub "Two minutes cut together from real weddings, corporate
  events and private parties. It's all live, nothing re-recorded." both assume
  a 2-minute, all-live reel. Watch the new video and update the length or
  description if they no longer match.

### 3.2 Instagram `[CLAUDE]`

**Where:** one footer link per page, in **10 files**: `index.html`,
`about.html`, `setlist.html`, `event-coordinators.html`,
`corporate-events-austin.html`, `private-parties-austin.html`,
`wedding-band-{austin,dallas,houston,san-antonio}.html`. All are the same
string, `https://www.instagram.com/jayguzmusic/`, with no other variants.
`thank-you.html` and `404.html` have no Instagram link.

**Change:** replace it everywhere with
`https://www.instagram.com/jayguzmanmusicandevents/`.

```bash
grep -rl 'instagram.com/jayguzmusic/' --include='*.html' . \
  | xargs sed -i '' 's#instagram.com/jayguzmusic/#instagram.com/jayguzmanmusicandevents/#g'
```

**Extra, recommended:** add the Instagram URL to the structured data so Google
ties the account to the business. `about.html:31` has
`"sameAs": ["https://www.jayguzmanmusicandevents.com/"]`; add the Instagram URL
to that array. The homepage's business JSON-LD has no `sameAs` for the business
itself (the only `sameAs` at `index.html:35` is the Austin Wikipedia link), so
add one there too.

**Leave alone:** the Trustpilot links (`trustpilot.com/review/jayguzmusic.com`,
8 occurrences). That's where the reviews actually live, and changing the URL
breaks them. Jay didn't ask for that change.

### 3.3 About page: the "full band" line `[CLAUDE drafts, JAY approves]`

Jay remembered it as "designed to feel like a full band". The actual copy is
`about.html:166`, the sub-line under "One Performer. A Full Sound.":

> My setup is engineered to sound like a full band — because it basically is.
> Here's what I bring to every show.

The same claim appears again in the Light Percussion item (`about.html:197`):

> The rhythmic backbone that gives every song its full-band feel. …

**Proposed copy (for Jay to approve):**

- `about.html:166` →
  *"It's just me up there — piano, vocals, acoustic guitar and a little
  percussion, all played live and shaped to the room. Here's what I bring to
  every show."*
- `about.html:197` →
  *"The rhythmic backbone that keeps a song moving. Subtle enough for a dinner
  setting, strong enough to get a reception going — layered in live alongside
  everything else."*

Keep the heading "One Performer. A Full Sound." It's honest about being one
person and doesn't promise a band. Keep the "Full Band (Upgrade)" card. That's
a real offer (he puts a band together through his network), not a claim about the
solo setup.

**Question for Jay, not in his email:** the homepage makes the same claim
more strongly. `index.html:171` says *"Clients consistently say it sounds like
a full band. Because it does."* Ask whether he wants that toned down to match.
Don't change it without a yes. It's framed as client feedback, and he only
mentioned the About page.

### 3.4 About page: Guitar is acoustic only `[CLAUDE]`

`about.html:188` currently reads:

> Acoustic and electric. The guitar adds texture, warmth, and range that the
> keys alone can't provide — …

→ *"Acoustic. The guitar adds texture, warmth, and range that the keys alone
can't provide — perfect for intimate moments or adding a different sonic color
to the room."*

I checked the whole site: no other page mentions electric guitar. Every other
guitar mention is plain "guitar", "acoustic guitar", "classical guitar" or
"Latin guitar", which are all fine.

---

## 4. Execution order

| # | Step | Owner | Blocked on |
|---|---|---|---|
| 1 | Send Jay the proposed About copy (3.3) and the homepage question; ask him to upload the reel to YouTube (3.1 A) | Andy | — |
| 2 | Instagram swap + `sameAs` (3.2) — **done** | Claude | — |
| 3 | Guitar fix (3.4) — **done** | Claude | — |
| 4 | About "full band" copy + homepage line (3.3) — **done**, approved by Andy as proxy | Claude | — |
| 5 | Showreel embed + copy check (3.1 B) — **done** | Claude | — |
| 6 | Verify locally, PR to `main`, merge → Netlify deploys | Claude / Andy | 2–5 |
| 7 | Verify on the live domain (§5) and reply to Jay | Claude / Andy | 6 |

Steps 2–3 don't need anything from Jay and can ship right away. If the reel
upload takes a while, ship 2–4 first and do 5 as a second, one-line deploy.
Don't hold the easy fixes for the video.

---

## 5. Verification

Follow the `CUTOVER.md` §12 rules: check the live URL, not the repo, and strip
HTML comments before grepping.

**Local, before merge**
- `./scripts/build.sh` succeeds.
- `python3 -m http.server 8000` → load `/index.html` and `/about.html`; the reel
  plays, and the About copy reads correctly at desktop and phone widths.
- `grep -rc 'instagram.com/jayguzmusic/' --include='*.html' .` → all zero.
- JSON-LD on `about.html` and `index.html` still parses (paste into
  validator.schema.org or `python3 -c 'import json; …'`).

**Live, after Netlify deploys**
- The deploy for the merge commit is `ready` in Netlify.
- For each of the 10 pages: the comment-stripped HTML contains
  `instagram.com/jayguzmanmusicandevents/` once and `instagram.com/jayguzmusic/`
  zero times.
- The homepage HTML contains the new YouTube id and not `g79shq0yjY0`.
- `/about` contains "Acoustic." and does not contain "electric" or "sound like
  a full band".
- Click the Instagram link in a real browser and confirm it opens the business
  profile. Instagram returns 200 even for handles that don't exist, so `curl`
  can't prove this.
- Play the reel on the live homepage on desktop and on a phone.

**Close out**
- Reply to Jay with what changed and the homepage question if it's still open.
- Add a short entry under `CUTOVER.md` §13, or in this file, recording the
  deploy commit.

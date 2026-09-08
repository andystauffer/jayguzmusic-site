#!/usr/bin/env python3
"""Trim titles to <=60 and descriptions to <=160 so search doesn't truncate them.

Also fixes two content bugs found while auditing:
  - the About description still cited "the Caribbean", a leftover from the
    cruise-ship claim Jay asked us to remove
  - it opened lowercase, because the tenure sweep replaced "Twenty years"
    with "over a decade" mid-sentence

Where a page's og:description or twitter:description duplicated the meta
description, they are updated together so the three never drift apart.
"""
import re, sys, pathlib

TITLES = {
 "index.html":                            "Jay Guzman | Austin Event Pianist & Live Music",
 "event-coordinators/index.html":         "For Event Coordinators | Jay Guzman, Austin Pianist",
 "wedding-band-dallas/index.html":        "Wedding Band in Dallas | Jay Guzman, Austin-Based",
 "wedding-band-houston/index.html":       "Wedding Band in Houston | Jay Guzman, Austin-Based",
 "wedding-band-san-antonio/index.html":   "Wedding Band San Antonio | Jay Guzman, Bilingual",
}

DESCRIPTIONS = {
 "index.html":
   "Live piano, vocals and guitar for Austin weddings, corporate events and "
   "private parties. Over a decade of experience. You set the vibe, Jay brings it.",
 "about/index.html":
   "Over a decade of live performance across New York, Puerto Rico, Spain and "
   "London. Jay Guzman brings range, flexibility and a vendor's mindset to Austin events.",
 "corporate-events-austin/index.html":
   "Live piano and vocals for Austin corporate events, galas, client dinners and "
   "product launches. Corporate experience with BetMGM, SandsRx and more.",
 "event-coordinators/index.html":
   "A musician your clients will love and you'll enjoy working with. Jay Guzman "
   "knows timelines, run-of-show and vendor communication.",
 "private-parties-austin/index.html":
   "Live piano, vocals and guitar for Austin private parties. Birthdays, "
   "anniversaries, holiday gatherings — the energy your celebration deserves.",
 "setlist/index.html":
   "Browse Jay Guzman's full song catalog across Pop, Jazz, Latin, Country and "
   "R&B. Build a custom set list for your Austin event and send it over.",
 "wedding-band-dallas/index.html":
   "Austin-based wedding pianist and vocalist, regularly in Dallas. Solo piano, "
   "layered trio or full live band — one vendor across the whole night.",
 "wedding-band-houston/index.html":
   "Austin-based wedding pianist and vocalist, regularly in Houston. Solo piano "
   "to full live band, bilingual repertoire available.",
 "wedding-band-san-antonio/index.html":
   "Austin-based wedding pianist and vocalist, regularly in San Antonio. "
   "Bilingual sets, Latin repertoire, solo to full band.",
}

def esc(t):
    return t.replace("&", "&amp;")

def main():
    dry = "--dry-run" in sys.argv
    root = pathlib.Path(__file__).resolve().parent.parent
    for f in sorted(set(TITLES) | set(DESCRIPTIONS)):
        p = root / f
        s = orig = p.read_text()
        notes = []

        if f in TITLES:
            new = TITLES[f]
            assert len(new) <= 60, f"title too long for {f}: {len(new)}"
            s, n = re.subn(r"<title>.*?</title>", f"<title>{esc(new)}</title>", s, count=1, flags=re.S)
            assert n, f"no <title> in {f}"
            notes.append(f"title -> {len(new)}")
            # og:title / twitter:title carry the same text on these pages
            for prop in ('property="og:title"', 'name="twitter:title"'):
                s = re.sub(rf'({prop} content=")[^"]*(")', lambda m: m.group(1)+esc(new)+m.group(2), s)

        if f in DESCRIPTIONS:
            new = DESCRIPTIONS[f]
            assert len(new) <= 160, f"description too long for {f}: {len(new)}"
            old_m = re.search(r'name="description" content="([^"]*)"', s)
            old = old_m.group(1) if old_m else None
            s, n = re.subn(r'(name="description" content=")[^"]*(")',
                           lambda m: m.group(1)+esc(new)+m.group(2), s, count=1)
            assert n, f"no meta description in {f}"
            notes.append(f"desc -> {len(new)}")
            # only touch social copies that duplicated the meta description
            if old:
                for prop in ('property="og:description"', 'name="twitter:description"'):
                    s = re.sub(rf'({prop} content=")' + re.escape(esc(old)) + r'(")',
                               lambda m: m.group(1)+esc(new)+m.group(2), s)

        if s != orig and not dry:
            p.write_text(s)
        print(f"  {f:<38} {', '.join(notes)}")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Point every image slot on the site at its Cloudinary asset.

Mapping is by asset title. Every URL is delivered through f_auto,q_auto so
Cloudinary serves WebP/AVIF at an appropriate size — the raw PNGs and JPGs
are 2.5-6.7MB each, which is not shippable as-is.

Run from the repo root:  python3 scripts/apply-images.py [--dry-run]
"""
import re, sys, pathlib

CLOUD = "dja4ppkvq"

def url(public_id, w, extra=""):
    t = f"f_auto,q_auto,w_{w}" + (("," + extra) if extra else "")
    return f"https://res.cloudinary.com/{CLOUD}/image/upload/{t}/{public_id}"

# slot (file, old path) -> (cloudinary public id, delivered width)
MAPPING = [
    # ---- home ----
    ("index.html", "hero_musician_austin_wedding_events.png",
     "home_hero_wedding_event_piano_player_ocd7l4.png", 1600),
    ("index.html", "assets/images/full-band-placeholder.jpg",
     "Performing_Chelsea_Piers_show_acxidh.jpg", 1400),

    # ---- about ----
    ("about.html", "assets/images/about-hero-placeholder.jpg",
     "Performing_Hero_Cabo_xzgad1.png", 2000),
    ("about.html", "assets/images/jason-portrait.jpg",
     "Suit_Photo_e3rvbx.jpg", 1000),

    # ---- event coordinators ----
    ("event-coordinators.html", "assets/images/ec-hero-placeholder.jpg",
     "Guitar_Bar_NY_Photo_njcoej.png", 2000),

    # ---- weddings ----
    ("events/weddings.html", "../assets/images/wedding-hero-placeholder.jpg",
     "Hero_Cabo_Wedding_b9irs0.jpg", 2000),
    ("events/weddings.html", "../assets/images/wedding-detail-placeholder.jpg",
     "performing_wedding_Palm_Springs_bhbhht.png", 1200),

    # ---- corporate ----
    ("events/corporate.html", "../assets/images/corporate-hero-placeholder.jpg",
     "Performing_Chelsea_Piers_show_acxidh.jpg", 2000),

    # ---- private parties ----
    ("events/private-parties.html", "../assets/images/party-hero-placeholder.jpg",
     "Performing_Boat_NYC_stnxx2.png", 1400),
    ("events/private-parties.html", "../assets/images/party-detail-placeholder.jpg",
     "Performing_Austin_Piano_zsomxf.png", 1200),

    # ---- city pages: no city-specific photography exists, so these reuse the
    #      generic performing shots. None of them are labelled with a city, so
    #      nothing is claimed that isn't true. ----
    ("wedding-band-dallas.html", "assets/images/dallas-wedding-hero.jpg",
     "Hero_Cabo_Wedding_b9irs0.jpg", 2000),
    ("wedding-band-dallas.html", "assets/images/dallas-wedding-detail.jpg",
     "performing_wedding_Palm_Springs_bhbhht.png", 1200),
    ("wedding-band-dallas.html", "assets/images/dallas-venue-wide.jpg",
     "Performing_Hero_Cabo_xzgad1.png", 1600),

    ("wedding-band-houston.html", "assets/images/houston-wedding-hero.jpg",
     "performing_wedding_Palm_Springs_bhbhht.png", 2000),
    ("wedding-band-houston.html", "assets/images/houston-wedding-detail.jpg",
     "Performing_Chelsea_Piers_show_acxidh.jpg", 1200),
    ("wedding-band-houston.html", "assets/images/houston-venue-wide.jpg",
     "Performing_Hero_Cabo_xzgad1.png", 1600),

    ("wedding-band-san-antonio.html", "assets/images/san-antonio-wedding-hero.jpg",
     "Performing_Chelsea_Piers_show_acxidh.jpg", 2000),
    ("wedding-band-san-antonio.html", "assets/images/san-antonio-wedding-detail.jpg",
     "Hero_Cabo_Wedding_b9irs0.jpg", 1200),
    ("wedding-band-san-antonio.html", "assets/images/san-antonio-venue-wide.jpg",
     "Performing_Austin_Piano_zsomxf.png", 1600),
]

# Social cards are absolute URLs that CONTAIN the asset path, so they must be
# replaced whole and BEFORE the relative paths — otherwise the substring match
# rewrites the tail and yields https://site/https://res.cloudinary.com/...
SITE = "https://www.jayguzmanmusicandevents.com"
SOCIAL = [
    ("wedding-band-dallas.html",      "assets/images/dallas-wedding-hero.jpg",
     "Hero_Cabo_Wedding_b9irs0.jpg"),
    ("wedding-band-houston.html",     "assets/images/houston-wedding-hero.jpg",
     "performing_wedding_Palm_Springs_bhbhht.png"),
    ("wedding-band-san-antonio.html", "assets/images/san-antonio-wedding-hero.jpg",
     "Performing_Chelsea_Piers_show_acxidh.jpg"),
]

def social_url(pid):
    # 1200x630 is the canonical OG card size; g_auto keeps the subject centred
    return (f"https://res.cloudinary.com/{CLOUD}/image/upload/"
            f"f_auto,q_auto,w_1200,h_630,c_fill,g_auto/{pid}")

def main():
    dry = "--dry-run" in sys.argv
    root = pathlib.Path(__file__).resolve().parent.parent
    touched, applied, misses = {}, 0, []

    for f, path, pid in SOCIAL:
        p = root / f
        s = touched.get(f, p.read_text())
        absolute = f"{SITE}/{path}"
        if absolute not in s:
            misses.append((f, absolute)); continue
        n = s.count(absolute)
        touched[f] = s.replace(absolute, social_url(pid))
        applied += n
        print(f"  {f:<30} og:image {path.split('/')[-1]:<27} -> {pid}  ({n}x, 1200x630)")

    for f, old, pid, w in MAPPING:
        p = root / f
        s = touched.get(f, p.read_text())
        if old not in s:
            misses.append((f, old)); continue
        n = s.count(old)
        touched[f] = s.replace(old, url(pid, w))
        applied += n
        print(f"  {f:<30} {old.split('/')[-1]:<36} -> {pid}  ({n}x, w_{w})")
    if misses:
        print("\n  NOT FOUND:")
        for f, old in misses:
            print(f"    {f}: {old}")
    if not dry:
        for f, s in touched.items():
            (root / f).write_text(s)
    print(f"\n  {applied} references {'would be' if dry else ''} updated "
          f"across {len(touched)} files")

if __name__ == "__main__":
    main()

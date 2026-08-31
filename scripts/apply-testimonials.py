#!/usr/bin/env python3
"""Replace the invented testimonials with the three real Trustpilot reviews.

Source: https://www.trustpilot.com/review/jayguzmusic.com  (retrieved 2026-08-31)

Every excerpt below is asserted to be a literal substring of the full review
text before anything is written. These are real, named people — their wording
is never altered, only trimmed at sentence boundaries with an ellipsis.
"""
import re, sys, pathlib

TRUSTPILOT = "https://www.trustpilot.com/review/jayguzmusic.com"

# Full review bodies, verbatim.
FULL = {
"matt": """Jay is absolutely incredible. There are not enough ways to describe how great he is. We hired him to play our wedding and in addition to being a genuinely nice guy he is unbelievably talented. Where to begin? Leading up to the wedding he engaged with us to find out what music / specific songs we wanted. We even told him we wanted our first dance to be a piano version of our favorite EDM song and he created a version that was absolute perfection. He also learned a bunch of songs that we wanted him to play throughout the night. The layout of our venue required him to play in 3 different rooms for cocktail hour, dinner and after dinner dancing and he pulled this off flawlessly. The vibe for each part was on point, so on point that he had people dancing during dinner. He has a song repertoire that works for every generation. He took impromptu requests from our guests without missing a beat, played some mashups and had everyone on the dance floor. All of our guests were raving about him during and for weeks after our wedding. Jay can definitely carry any kind of party on his own with his keyboard and guitar. We would hire him for literally anything.""",

"vinnie": """Jay is AMAZING!!! I just hired Jay to play my wife's surprise birthday party and he was FABULOUS!!! Not only is Jay a great musician, he is an amazing person. Extremely friendly and over the top nice and professional. A true pleasure to work with from the very beginning of the planning process for the event all the way up and through the event itself. If you want someone who can make your party special and amazing, with zero drama and who is nothing but polite, professional, super nice, and super talented - then Jay is your choice!!! 5 Stars only because I can't give him 10 stars. Thanks!!!""",

"jesse": """I've known Jason for years and hired him to play many different kinds events. He's a singer/songwriter one man band, mainly playing piano, but also guitar and some percussion. He always makes it fun. I've had him play intimate private parties, in corporate settings and all the way up to large showcases on a big stage. It doesn't matter, he always delivers and is very reliable and self contained. I work with a LOT of musicians and I've always been impressed with how long he can play and entertain a crowd. He's capable of playing standards, modern and classic covers, on the spot requests and he's also got original songs. Jason is guaranteed to read the room and give any kind of crowd, regardless of setting, exactly what they want.""",
}

# Excerpt = ordered list of verbatim fragments, joined by an ellipsis.
REVIEWS = {
"matt": dict(
    name="Matt Yee", event="Wedding · via Trustpilot", avatar="#E8D9CE",
    parts=["We hired him to play our wedding and in addition to being a genuinely nice guy he is unbelievably talented.",
           "We even told him we wanted our first dance to be a piano version of our favorite EDM song and he created a version that was absolute perfection.",
           "All of our guests were raving about him during and for weeks after our wedding."]),
"vinnie": dict(
    name="Vinnie", event="Surprise Birthday Party · via Trustpilot", avatar="#CFE0DC",
    parts=["I just hired Jay to play my wife's surprise birthday party and he was FABULOUS!!! Not only is Jay a great musician, he is an amazing person.",
           "If you want someone who can make your party special and amazing, with zero drama and who is nothing but polite, professional, super nice, and super talented - then Jay is your choice!!!"]),
"jesse": dict(
    name="Jesse Rothman", event="Private, Corporate & Showcase · via Trustpilot", avatar="#E4C9BC",
    parts=["I've had him play intimate private parties, in corporate settings and all the way up to large showcases on a big stage. It doesn't matter, he always delivers and is very reliable and self contained.",
           "Jason is guaranteed to read the room and give any kind of crowd, regardless of setting, exactly what they want."]),
}

def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def verify():
    """Every fragment must appear verbatim in the source review."""
    for key, r in REVIEWS.items():
        for p in r["parts"]:
            if p not in FULL[key]:
                sys.exit(f"NOT VERBATIM in {key}:\n  {p}")
    print("  ✅ all excerpt fragments verified verbatim against the source reviews")

def card(key, indent="        "):
    r = REVIEWS[key]
    quote = esc(" … ".join(r["parts"]))
    i = indent
    return (f'{i}<div class="testimonial-card fade-in">\n'
            f'{i}  <p class="testimonial-card__quote">{quote}</p>\n'
            f'{i}  <div class="testimonial-card__author">\n'
            f'{i}    <div class="testimonial-card__avatar" style="background: {r["avatar"]};" aria-hidden="true"></div>\n'
            f'{i}    <div>\n'
            f'{i}      <p class="testimonial-card__name">{esc(r["name"])}</p>\n'
            f'{i}      <p class="testimonial-card__event">{esc(r["event"])}</p>\n'
            f'{i}    </div>\n'
            f'{i}  </div>\n'
            f'{i}</div>')

# which real reviews belong on which page, by what each review actually describes
PLACEMENT = {
    "index.html":                    ["matt", "vinnie", "jesse"],
    "events/weddings.html":          ["matt"],
    "events/private-parties.html":   ["vinnie"],
    "events/corporate.html":         ["jesse"],
    "event-coordinators.html":       ["jesse"],
    "wedding-band-dallas.html":      ["matt"],
}

def find_cards(s):
    """Locate each .testimonial-card block by matching div nesting properly.
    A non-greedy regex stops at the first </div> of the nested author block
    and leaves orphaned closers behind."""
    out = []
    for m in re.finditer(r'[ \t]*<div class="testimonial-card fade-in"[^>]*>', s):
        i, depth = m.end(), 1
        while depth:
            nxt = re.search(r'<div\b|</div>', s[i:])
            if not nxt: return out
            depth += -1 if nxt.group(0) == '</div>' else 1
            i += nxt.end()
        while i < len(s) and s[i] == '\n':
            i += 1
        out.append((m.start(), i))
    return out

def main():
    dry = "--dry-run" in sys.argv
    verify()
    root = pathlib.Path(__file__).resolve().parent.parent
    for f, keys in PLACEMENT.items():
        p = root / f
        s = p.read_text()
        found = find_cards(s)
        if not found:
            print(f"  ⚠ {f}: no cards matched"); continue
        indent = re.match(r'[ \t]*', s[found[0][0]:]).group(0)
        new = "\n".join(card(k, indent) for k in keys) + "\n"
        s2 = s[:found[0][0]] + new + s[found[-1][1]:]
        # the replacement must not change the document's div balance beyond
        # the cards actually removed
        assert s2.count("</div>") - len(re.findall(r"<div[ >]", s2)) == 0, \
            f"div balance broken in {f}"
        if not dry:
            p.write_text(s2)
        print(f"  {f:<32} {len(found)} invented -> {len(keys)} real ({', '.join(REVIEWS[k]['name'] for k in keys)})")

if __name__ == "__main__":
    main()

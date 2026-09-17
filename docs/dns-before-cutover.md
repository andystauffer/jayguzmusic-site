# DNS snapshot — jayguzmanmusicandevents.com

**Captured:** 2026-09-17T15:26:33Z, from the authoritative nameserver `ns8.wixdns.net`, after
the Phase 4 TTL reduction and before any cutover change.
**This is the rollback reference.** To undo the cutover, restore the A and
CNAME records below exactly as listed.

Zone is hosted by Wix (`ns8.wixdns.net`, `ns9.wixdns.net`).

## Records that CHANGE at cutover

```
A      jayguzmanmusicandevents.com         1800  185.230.63.107
A      jayguzmanmusicandevents.com         1800  185.230.63.171
A      jayguzmanmusicandevents.com         1800  185.230.63.186
CNAME  www.jayguzmanmusicandevents.com     1800  cdn1.wixdns.net.
```

Those three A records and the `www` CNAME point at Wix. They are the only
records the cutover touches. TTL was lowered from 3600 to 1800 on
2026-09-17 — 30 minutes is the floor Wix's DNS panel allows.

## Records that MUST NOT be touched

Jay runs **Google Workspace email on this domain**. Deleting or editing any of
the following stops his mail.

```
MX     jayguzmanmusicandevents.com         3600  10 aspmx.l.google.com.
MX     jayguzmanmusicandevents.com         3600  20 alt1.aspmx.l.google.com.
MX     jayguzmanmusicandevents.com         3600  30 alt2.aspmx.l.google.com.
MX     jayguzmanmusicandevents.com         3600  40 alt3.aspmx.l.google.com.
MX     jayguzmanmusicandevents.com         3600  50 alt4.aspmx.l.google.com.
TXT    jayguzmanmusicandevents.com         3600  "google-site-verification=Lx34EnTBVuHcgYfJ1XCUYP-y0jsK1zQ9s-OWb0xm1WM"
TXT    jayguzmanmusicandevents.com         3600  "google-site-verification=_UB8hZDVI5uD4QvJ3HPEdXxWeRjHxYUqxZaKpz7fZ2Q"
TXT    jayguzmanmusicandevents.com         3600  "v=spf1 include:_spf.google.com ~all"
```

No `_dmarc` record exists. Not required, and not our business here — noted only
so its absence isn't mistaken later for something the cutover removed.

## Verify after cutover

```bash
dig @ns8.wixdns.net +noall +answer MX  jayguzmanmusicandevents.com   # identical to above
dig @ns8.wixdns.net +noall +answer TXT jayguzmanmusicandevents.com   # identical to above
dig @ns8.wixdns.net +noall +answer A   jayguzmanmusicandevents.com   # Netlify's value(s)
dig @ns8.wixdns.net +noall +answer CNAME www.jayguzmanmusicandevents.com  # jayguzmusic.netlify.app
```

## Previous snapshot

2026-09-10T22:01:28Z: identical records, all at TTL 3600.

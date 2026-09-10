# DNS snapshot — jayguzmanmusicandevents.com

**Captured:** 2026-09-10T22:01:28Z, before any cutover change.
**This is the rollback reference.** To undo the cutover, restore the A and
CNAME records below exactly as listed.

Zone is hosted by Wix (`ns8.wixdns.net`, `ns9.wixdns.net`).

## Records that CHANGE at cutover

```
A      jayguzmanmusicandevents.com       3600   185.230.63.171
A      jayguzmanmusicandevents.com       3600   185.230.63.186
A      jayguzmanmusicandevents.com       3600   185.230.63.107
CNAME  www.jayguzmanmusicandevents.com   3600   cdn1.wixdns.net.
```

Those three A records and the `www` CNAME point at Wix. They are the only
records the cutover touches.

## Records that MUST NOT be touched

Jay runs **Google Workspace email on this domain**. Deleting or editing any of
the following stops his mail.

```
MX   10  aspmx.l.google.com.
MX   20  alt1.aspmx.l.google.com.
MX   30  alt2.aspmx.l.google.com.
MX   40  alt3.aspmx.l.google.com.
MX   50  alt4.aspmx.l.google.com.
TXT  "v=spf1 include:_spf.google.com ~all"
TXT  "google-site-verification=Lx34EnTBVuHcgYfJ1XCUYP-y0jsK1zQ9s-OWb0xm1WM"
TXT  "google-site-verification=_UB8hZDVI5uD4QvJ3HPEdXxWeRjHxYUqxZaKpz7fZ2Q"
```

No `_dmarc` record exists. Not required, and not our business here — noted only
so its absence isn't mistaken later for something the cutover removed.

## Verify after cutover

```bash
dig +short MX jayguzmanmusicandevents.com     # must be unchanged from above
dig +short TXT jayguzmanmusicandevents.com    # must still contain the SPF record
```

If either differs, restore from this file immediately — email outages are
silent, and mail sent meanwhile bounces rather than queuing.

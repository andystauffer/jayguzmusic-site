/* Clean URLs on Wix.
   Wix serves a static file when one matches the path, and hands anything
   else to this worker. So /about.html is served directly, and /about
   arrives here — we fetch the real file and return it. Fetching a path
   that IS a static file can't recurse back into the worker. */
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname.replace(/\/+$/, '');   // tolerate a trailing slash

    if (path && !path.includes('.')) {
      const res = await fetch(`${env.DEPLOYMENT_URL}${path}.html`);
      if (res.ok) {
        return new Response(res.body, {
          status: 200,
          headers: { 'content-type': 'text/html; charset=utf-8' },
        });
      }
    }
    const nf = await fetch(`${env.DEPLOYMENT_URL}/404.html`);
    return new Response(nf.ok ? nf.body : 'Not found', {
      status: 404,
      headers: { 'content-type': 'text/html; charset=utf-8' },
    });
  },
};

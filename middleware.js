// Site-wide password gate.
//
// Vercel's own Password Protection is an Advanced Deployment Protection
// add-on ($150/mo), so this does the same job at the edge: every request
// needs a cookie carrying a digest of SITE_PASSWORD, and anything without
// one gets the unlock page instead of the site.
//
// The password lives only in the SITE_PASSWORD environment variable. If it
// is unset the gate opens rather than locking everyone out of the site —
// a missing variable should not be able to take the site down.

const COOKIE = 'fl_gate';
const MAX_AGE = 60 * 60 * 24 * 30; // 30 days

// The data-network page is sent to customers directly, so it stands outside
// the gate. Its assets have to come with it — the fonts, script, hero tiles
// and the map it frames all live under /_assets, and the page is a blank
// screen without them. Opening that directory exposes no protected page:
// every other page's markup sits at the root, and the only document under
// _assets is the map this page frames.
const OPEN_PATHS = new Set([
  '/data',
  '/data-network',
  '/data-network.html',
  '/favicon.svg',
]);
const OPEN_PREFIXES = ['/_assets/'];

const isOpen = pathname =>
  OPEN_PATHS.has(pathname) ||
  OPEN_PREFIXES.some(prefix => pathname.startsWith(prefix));

export const config = {
  // Everything except the Vercel-internal paths. The unlock page posts to
  // /__gate, which this deliberately still matches so it can be handled here.
  matcher: '/((?!_vercel/).*)',
};

const hex = buf =>
  [...new Uint8Array(buf)].map(b => b.toString(16).padStart(2, '0')).join('');

async function digest(secret) {
  const bytes = new TextEncoder().encode(`fountain-labs:${secret}`);
  return hex(await crypto.subtle.digest('SHA-256', bytes));
}

// Compared without an early return so a wrong guess takes the same time as a
// near-miss.
function equal(a, b) {
  if (typeof a !== 'string' || typeof b !== 'string' || a.length !== b.length) {
    return false;
  }
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return diff === 0;
}

// Only same-origin absolute paths, so a crafted ?next= cannot bounce a
// visitor off the site after they authenticate.
function safeNext(value) {
  return typeof value === 'string' &&
    value.startsWith('/') &&
    !value.startsWith('//') ? value : '/';
}

function page(next, failed) {
  return `<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>FOUNTAIN</title>
<style>
  *{margin:0;padding:0;box-sizing:border-box}
  body{min-height:100vh;display:flex;align-items:center;justify-content:center;
    background:#FCFCFB;color:#111;padding:24px;
    font-family:Geist,-apple-system,BlinkMacSystemFont,'PingFang SC',
      'Noto Sans SC',sans-serif}
  .card{width:100%;max-width:360px}
  .mark{display:flex;align-items:center;gap:12px;margin-bottom:40px}
  .dia{width:13px;height:13px;background:#1E48D8;transform:rotate(45deg)}
  .name{font-size:22px;letter-spacing:.08em;font-weight:600}
  label{display:block;font-size:11px;letter-spacing:.18em;text-transform:uppercase;
    color:#8A8A85;margin-bottom:10px}
  input{width:100%;padding:13px 14px;font-size:15px;font-family:inherit;color:#111;
    background:#fff;border:1px solid #E6E6E2;border-radius:6px;outline:none}
  input:focus{border-color:#111}
  button{width:100%;margin-top:12px;padding:13px 14px;font-size:15px;
    font-family:inherit;font-weight:500;color:#fff;background:#111;border:0;
    border-radius:999px;cursor:pointer}
  button:hover{background:#333330}
  .err{margin-top:14px;font-size:13px;color:#B3261E}
  .foot{margin-top:36px;font-size:11px;letter-spacing:.1em;text-transform:uppercase;
    color:#8A8A85}
</style></head>
<body>
  <main class="card">
    <div class="mark"><span class="dia"></span><span class="name">FOUNTAIN</span></div>
    <form method="POST" action="/__gate">
      <input type="hidden" name="next" value="${next.replace(/"/g, '&quot;')}">
      <label for="p">Password</label>
      <input id="p" name="password" type="password" autocomplete="current-password"
        autofocus required>
      <button type="submit">Enter</button>
      ${failed ? '<p class="err">That password did not match.</p>' : ''}
    </form>
    <p class="foot">Silicon Valley · Shenzhen · Singapore</p>
  </main>
</body></html>`;
}

const unlockPage = (next, failed) =>
  new Response(page(next, failed), {
    status: 401,
    headers: {
      'content-type': 'text/html; charset=utf-8',
      'cache-control': 'no-store',
      'x-robots-tag': 'noindex, nofollow',
    },
  });

export default async function middleware(request) {
  const secret = process.env.SITE_PASSWORD;
  if (!secret) return; // unconfigured: fail open rather than lock the site out

  const url = new URL(request.url);
  if (isOpen(url.pathname)) return;

  const expected = await digest(secret);
  const cookie = request.headers.get('cookie') || '';
  const match = cookie.match(new RegExp(`(?:^|;\\s*)${COOKIE}=([^;]*)`));
  if (match && equal(match[1], expected)) return;

  if (url.pathname === '/__gate' && request.method === 'POST') {
    const form = await request.formData();
    const next = safeNext(form.get('next'));
    if (!equal(String(form.get('password') ?? ''), secret)) {
      return unlockPage(next, true);
    }
    return new Response(null, {
      status: 303,
      headers: {
        location: next,
        'cache-control': 'no-store',
        'set-cookie': `${COOKIE}=${expected}; Path=/; HttpOnly; Secure; ` +
          `SameSite=Lax; Max-Age=${MAX_AGE}`,
      },
    });
  }

  return unlockPage(url.pathname + url.search, false);
}

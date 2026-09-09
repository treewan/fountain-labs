# FOUNTAIN website · deploy package

Static site (8 pages) + two Vercel serverless functions that write to Supabase and notify via Resend.

```
deploy/
  public/          index.html nora.html eden-factory.html team.html data-network.html contact.html apply.html nora-memo.html favicon.svg
  api/             contact.js apply.js _lib.js
  supabase/        schema.sql
  vercel.json      clean URLs + /eden /data rewrites + security headers
  package.json     @supabase/supabase-js, resend
  .env.example
```

## 1 · Supabase (5 min)
1. supabase.com → New project (region: Singapore or US-West).
2. SQL Editor → paste `supabase/schema.sql` → Run. Creates `contact_requests` and `applications` with RLS locked (only service role can access).
3. Settings → API → copy **Project URL** and **service_role** key.

## 2 · Resend
1. resend.com → API Keys → create. Copy `re_...`.
2. Until `fountainbuild.com` is verified, keep `FROM_EMAIL=FOUNTAIN <onboarding@resend.dev>` (sandbox: can only send to your own verified addresses — verify tree@ / miki@ first).
3. Domains → Add `fountainbuild.com` → add the DNS records → once verified set `FROM_EMAIL=FOUNTAIN <hello@fountainbuild.com>`.

## 3 · GitHub
In `treewan/fountain-website`, replace the current root with the contents of this folder (the old `index.html`, `apply.html`, `api/apply.js`, pitchdeck files etc. move out or get deleted; the old `api/apply.js` dealflow webhook is not carried over — say if you want it back).

```
git rm -r --cached . && rm -rf api public *.html *.js *.py
cp -r <deploy>/* <deploy>/.env.example .
git add -A && git commit -m "v2 site: static pages + Supabase/Resend forms" && git push
```

## 4 · Vercel
1. vercel.com → Add New → Project → import `treewan/fountain-website`. Framework preset: **Other**. Output directory: `public`. Leave build command empty.
2. Settings → Environment Variables → add everything from `.env.example` (Production + Preview).
3. Deploy. You get `fountain-website-xxx.vercel.app`.

## 5 · Check
- `/`, `/nora`, `/eden`, `/team`, `/data`, `/contact`, `/apply`, `/nora-memo` all render.
- Submit the Contact form → row appears in Supabase → email arrives. Same for Apply.
- Forms auto-detect: opened as a local file they just show the success state; on `*.vercel.app` or the real domain they POST to `/api/*`.

## Later
- Custom domain: Vercel → Domains → `fountainbuild.com`; update `SITE_URL`.
- OG images: pages reference `/og/<page>.png` (1200×630). Drop them into `public/og/` when ready; until then the tag points at a missing file and platforms fall back to no image.
- Re-export: pages are compiled from the `.dc.html` sources in the design workspace; ask for a rebuild after design changes.

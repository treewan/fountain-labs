# Claude Code task: deploy FOUNTAIN website to Vercel with Supabase + Resend forms

You are in a folder that contains a finished static site and its serverless form handlers. Your job is to ship it. Do not redesign or rewrite the HTML in `public/` — it is compiled output; treat it as immutable.

## What's here

```
public/           8 self-contained HTML pages + favicon.svg   (immutable)
api/              contact.js  apply.js  _lib.js               (Vercel Node functions, ESM)
supabase/         schema.sql                                   (two tables, RLS locked)
vercel.json       cleanUrls + rewrites (/eden → eden-factory.html, /data → data-network.html) + headers
package.json      @supabase/supabase-js, resend
.env.example      every env var the functions read
README.md         human walkthrough of the same steps
```

Target repo: `github.com/treewan/fountain-website`, branch `main`. It currently holds an older version of the site (index.html, apply.html, api/apply.js with Resend + a dealflow webhook, pitchdeck HTML files, .py/.js generators, images/). All of that is superseded **except**: keep `.gitignore`; ask the user before deleting `images/`, `logo*.png|svg`, and the pitchdeck files (move them to `archive/` if they want them kept).

## Steps

### 0 · Preflight
- `node -v` ≥ 18. Install CLIs if missing: `npm i -g vercel supabase`.
- Confirm the user is logged in: `vercel whoami`, `supabase projects list`, `gh auth status` (or plain git with push rights). If any fails, run the matching `login` command and let the user complete the browser flow.

### 1 · Supabase
1. If the user has no project: `supabase projects create fountain-website --org-id <ask or list with supabase orgs list> --region ap-southeast-1 --db-password <generate, show to user once>`.
2. Apply schema: either `supabase db push` after `supabase link --project-ref <ref>` with `schema.sql` copied into `supabase/migrations/0001_init.sql`, or simply run the SQL via `psql "$(supabase db url)" -f supabase/schema.sql`. Either is fine; the SQL is idempotent.
3. Fetch `SUPABASE_URL` (`https://<ref>.supabase.co`) and the **service_role** key (`supabase projects api-keys --project-ref <ref>`). Never expose service_role to the browser; it is only used by `api/*`.

### 2 · Resend
- Cannot be automated without an API key. Ask the user for `RESEND_API_KEY` (resend.com → API Keys). If `fountainbuild.com` is not verified in Resend yet, use `FROM_EMAIL="FOUNTAIN <onboarding@resend.dev>"` and tell the user the sandbox only delivers to addresses verified in their Resend account. Default recipients live in `.env.example`; confirm them with the user.

### 3 · Git
```
git clone git@github.com:treewan/fountain-website.git && cd fountain-website
git checkout -b v2-site
# archive or remove the old site (confirm with user first — see note above)
mkdir -p archive && git mv *.html *.py generate-*.js pitchdeck* website* ig-*.html api archive/ 2>/dev/null || true
cp -r <this-folder>/{public,api,supabase,vercel.json,package.json,.env.example,README.md} .
npm install            # produces package-lock.json
git add -A && git commit -m "v2 site: 8 static pages + Supabase/Resend form handlers"
git push -u origin v2-site
```
Open a PR or merge to `main` per the user's preference; Vercel builds either.

### 4 · Vercel
```
vercel link            # pick/create project "fountain-website", link to the GitHub repo
vercel env add SUPABASE_URL production preview
vercel env add SUPABASE_SERVICE_ROLE_KEY production preview
vercel env add RESEND_API_KEY production preview
vercel env add FROM_EMAIL production preview
vercel env add TEAM_RECIPIENTS production preview
vercel env add APPLY_RECIPIENTS production preview
vercel env add SITE_URL production preview
vercel --prod
```
Project settings: Framework preset **Other**, Output Directory **public**, no build command, Node 20.x. `vercel.json` already handles routing; do not add a framework.

### 5 · Verify (do all of these, report results)
- `curl -sI https://<deployment>/` and `/nora /eden /team /data /contact /apply /nora-memo` → all 200, `content-type: text/html`.
- `curl -sI https://<deployment>/favicon.svg` → 200.
- `curl -s -X POST https://<deployment>/api/contact -H 'content-type: application/json' -d '{"name":"Deploy Test","email":"<user email>","audience":"lab","needs":["data"],"brief":"smoke test"}'` → `{"ok":true,"id":"…"}`.
- Same for `/api/apply` with `{"name":"Deploy Test","email":"…","stage":"proto","company":"Test Co"}`.
- `supabase db query "select count(*) from contact_requests"` (or via the dashboard) → 1 row each. Confirm the notification email arrived.
- Delete the two test rows afterwards.
- Open the site on a phone-width viewport once; the pages are responsive but confirm nothing 404s.

### 6 · Hand back
Report: deployment URL, Supabase project ref, which env vars are set, anything skipped (Resend domain verification, custom domain). Do not bind `fountainbuild.com` unless the user asks; the plan is to preview on `*.vercel.app` first.

## Notes
- Forms detect environment: served from `file:` or `localhost` they only show the success state; on any `https` host they POST to `/api/*`.
- `api/_lib.js` has a per-instance rate limiter (5 contact / 3 apply per IP per 10 min). Real protection is Vercel's WAF; leave as is.
- The old `api/apply.js` also forwarded applications to `https://dealflow.fountainbuild.ai/api/intake/webhook` with an HMAC secret. The new handler does **not**. If the user wants it back, port `buildDealflowPayload` + `postToDealflow` from the archived file into `api/apply.js` after the Supabase insert, reading URL and secret from `DEALFLOW_WEBHOOK_URL` / `DEALFLOW_WEBHOOK_SECRET` env vars only (never hardcode the secret again).
- OG images referenced at `/og/<page>.png` (1200×630) do not exist yet; that is expected. Skip.

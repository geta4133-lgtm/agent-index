# Agent Index — a directory site you own

A static directory of real AI agent use cases. Every entry has a ready-to-copy prompt.
Monetised with a sponsor bar, a sponsor page, and a newsletter CTA.

Built from the 1,267-entry dataset in `~/agentusecases/use_cases.json`.

## Layout

```
~/ucdir/
├── gen.py         # config + dataset load + base HTML template + helpers
├── build.py       # output dir, list/row/chip/newsletter helpers
├── pages.py       # home + paginated all
├── pages2.py      # category pages + 1,267 detail pages
├── pages3.py      # agents, topics, sponsor, about, privacy, 404, search index
├── pages4.py      # sitemap.xml, feed.xml, robots.txt  <- RUN THIS
├── audit.py       # link integrity + anti-slop pre-flight
├── refresh.py     # keep content fresh (sync + HN candidates) then rebuild
├── deploy.sh      # cloudflare | netlify | surge | ghpages | preview
├── static/        # style.css, app.js
└── public/        # build output (1,325 pages, ~15 MB)
```

## Build

```bash
cd ~/ucdir
python3 pages4.py     # writes public/
python3 audit.py      # expects: 0 broken links, no pre-flight issues
```

## Preview

```bash
cd ~/ucdir
./deploy.sh preview                      # local server on :8777
cloudflared tunnel --url http://127.0.0.1:8777 --no-autoupdate   # public URL
```

## Refresh content

```bash
python3 refresh.py                  # sync new entries from upstream + rebuild
python3 refresh.py --hn             # also pull fresh candidates from Hacker News
python3 refresh.py --sync --rebuild
```

## Deploy

```bash
./deploy.sh cloudflare    # npx wrangler login first
./deploy.sh netlify       # npx netlify-cli login first
./deploy.sh surge         # npm i -g surge; surge login
GH_TOKEN=xxx GH_USER=me ./deploy.sh ghpages
```

## Edit the branding

Everything user-facing lives in the `CFG` dict at the top of `gen.py`:

| key | meaning |
|---|---|
| `brand` | site name (renders as `First.last` in the header) |
| `domain` | canonical domain used in sitemap, RSS, OG tags |
| `tagline` / `desc` | hero headline and meta description |
| `sponsor.name` / `.pitch` / `.url` / `.live` | sponsor bar contents |
| `sponsor_price` / `sponsor_slots` | pricing shown on `/sponsor` |
| `newsletter_action` | POST endpoint for the signup form (`#` = local only) |

Then rebuild.

## What is in the build

- 1 home page (hero, search over 1,267 entries, latest 100, category chips)
- 13 paginated `all` pages (100 per page, fully crawlable)
- 11 category pages
- 28 agent pages
- 1,267 detail pages (summary, did / went / worth knowing, copy-ready prompt, source link, related)
- `topics`, `about`, `sponsor`, `privacy`, `404`
- `sitemap.xml` (1,324 URLs), `feed.xml` (RSS, newest 50), `robots.txt`, `search-index.json`

## Monetisation wiring

1. **Sponsor bar** — fixed bottom bar on every page. Set `CFG["sponsor"]` with `live: True`
   to show a paying sponsor, or leave it false so it advertises the slot.
2. **`/sponsor` page** — price, what is included, who visits, plus a booking mailto.
   Update the mailto in `pages3.py` (search for `sponsor@example.com`).
3. **Newsletter** — the form on every page. Point `CFG["newsletter_action"]` at a real
   endpoint (Buttondown, MailerLite, ConvertKit, or your own worker) to go live.
4. **Affiliate slots** — drop links into `try_prompt` copy or add a slot to the prompt box
   in `pages2.py`.

## Notes

- Content is attribution-preserving: every entry keeps its `source_url` and the detail page
  links out with "Read the original".
- Takedown path is documented on `/privacy`.
- Set your own `domain` in `CFG` before deploying. The `.example` default is a placeholder.
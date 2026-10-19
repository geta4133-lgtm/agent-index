#!/usr/bin/env python3
"""SEO files: sitemap, RSS, robots."""
import os, json, datetime, email.utils
from build import *
from pages import URLS, w
from pages2 import DOMAIN, TODAY
import pages3  # noqa: F401  (builds agents/topics/sponsor/about/404/search-index)
from gen import esc, CFG, rows, OUT, HERE, fmt
from pages import list_html, newsletter, page, track

def tourl(p):
    if p == "index.html": return "/"
    if p.endswith("/index.html"): return "/" + p[:-len("index.html")]
    return "/" + p

# ---- /new/ page (latest 50, real freshness signal for crawlers) ----
latest_new = sorted(rows, key=lambda r: r.get("slug",""), reverse=True)[:50]
body_new = f"""<h2 class="sect">Newest use cases</h2>
<p class="lede">The 50 most recent additions to the directory. Subscribe via <a href="../feed.xml">RSS</a>.</p>
{list_html(latest_new, 1, "../")}
<p style="margin-top:22px"><a class="btn ghost" href="../all/index.html">Browse all {fmt(len(rows))} use cases</a></p>
{newsletter(1, "../")}"""
w("new/index.html", page(f"Newest AI agent use cases - {CFG['brand']}",
   "The 50 newest real AI agent use cases added to Agent Index, each with the prompt to try it.",
   body_new, 1, canonical=CFG["domain"] + "/new/"))
print("  /new/ page written:", len(latest_new), "cards")

# ---- /prompts/ page: 100 best prompts (lead magnet, no signup) ----
from collections import defaultdict as _dd
_by_agent = _dd(list)
for _r in rows:
    if _r.get("try_prompt"):
        _by_agent[_r.get("try_agent", "?")].append(_r)
_picked = []
_idx = {a: 0 for a in _by_agent}
while len(_picked) < 100:
    _added = False
    for _a, _lst in sorted(_by_agent.items(), key=lambda x: -len(x[1])):
        if _idx[_a] < len(_lst) and len(_picked) < 100:
            _picked.append(_lst[_idx[_a]]); _idx[_a] += 1; _added = True
    if not _added:
        break
_by_cat = _dd(list)
for _r in _picked:
    _by_cat[_r.get("category", "Other")].append(_r)

_pblocks = []
_n = 0
for _cat in sorted(_by_cat, key=lambda c: -len(_by_cat[c])):
    _items = []
    for _r in _by_cat[_cat]:
        _n += 1
        _items.append(
            f'<div class="uc"><h3><a href="../use-case/{_r["slug"]}/">{esc(_r["title"])}</a></h3>'
            f'<p class="meta">{esc(_r.get("try_agent",""))}</p>'
            f'<pre class="promptbox-pre"><code>{esc(_r["try_prompt"].strip())}</code></pre></div>')
    _pblocks.append(f'<h2 class="sect">{esc(_cat)}</h2>' + "".join(_items))

body_prompts = f"""<h1>100 AI agent prompts that actually worked</h1>
<p class="lede">Every prompt below comes from a real documented use case &mdash; someone asked, it ran, here is what happened. Copy it, replace the [brackets], run. No signup, no email wall.</p>
<div class="statrow">
  <div class="stat"><b>{fmt(len(rows))}</b><span>use cases in the directory</span></div>
  <div class="stat"><b>100</b><span>prompts on this page</span></div>
  <div class="stat"><b>{fmt(len(_by_agent))}</b><span>different agents</span></div>
</div>
{"".join(_pblocks)}
<p style="margin-top:22px"><a class="btn ghost" href="../all/index.html">Browse all {fmt(len(rows))} use cases</a></p>
{newsletter(1, "../")}"""
w("prompts/index.html", page(f"100 AI agent prompts that actually worked - {CFG['brand']}",
   "100 copy-paste AI agent prompts from real documented use cases. What people asked, how it went, and the exact prompt.",
   body_prompts, 1, canonical=CFG["domain"] + "/prompts/"))
print("  /prompts/ page written:", _n, "prompts")
track("prompts/index.html", 1)


skip = {"404.html"}
track("new/index.html", 1)
urls = sorted({tourl(p) for p, d in URLS if p not in skip})
sm = ['<?xml version="1.0" encoding="UTF-8"?>',
      '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for u in urls:
    pri = "1.0" if u == "/" else ("0.9" if u.startswith(("/all", "/agents", "/category")) else "0.7")
    sm.append(f"<url><loc>{DOMAIN}{u}</loc><lastmod>{TODAY}</lastmod><priority>{pri}</priority></url>")
sm.append("</urlset>")
w("sitemap.xml", "".join(sm))

# RSS - newest 50
feed_items = sorted(rows, key=lambda r: r.get("slug",""), reverse=True)[:50]
now = email.utils.formatdate(usegmt=True)
items = []
for r in feed_items:
    link = f"{DOMAIN}/use-case/{r['slug']}/"
    items.append(
        "<item>"
        f"<title>{esc(r['title'] + ' with ' + r['agent'])}</title>"
        f"<link>{link}</link>"
        f"<guid isPermaLink=\"true\">{link}</guid>"
        f"<pubDate>{now}</pubDate>"
        f"<description>{esc(r.get('summary',''))}</description>"
        "</item>")
rss = ('<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel>'
       f"<title>{esc(CFG['brand'])}</title><link>{DOMAIN}/new/</link>"
       f'<atom:link href="{DOMAIN}/feed.xml" rel="self" type="application/rss+xml" />'
       f"<description>{esc(CFG['desc'])}</description><language>en</language>"
       f"<lastBuildDate>{now}</lastBuildDate>" + "".join(items) + "</channel></rss>")
w("feed.xml", rss)

w("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {DOMAIN}/sitemap.xml\n")

# IndexNow key (Bing/Yandex/DuckDuckGo/Seznam auto-discovery)
w("d7bc6a57760d5cc55250bae50ecd6a2f.txt", "d7bc6a57760d5cc55250bae50ecd6a2f")


# ---- report ----
n_html = sum(1 for _, _, fs in os.walk(OUT) for f in fs if f.endswith(".html"))
total = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(OUT) for f in fs)
print(f"BUILD OK")
print(f"  HTML pages : {n_html}")
print(f"  sitemap urls: {len(urls)}")
print(f"  size       : {total/1024/1024:.1f} MB")
print(f"  output     : {OUT}")
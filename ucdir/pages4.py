#!/usr/bin/env python3
"""SEO files: sitemap, RSS, robots."""
import os, json, datetime, email.utils
from build import *
from pages import URLS, w
from pages2 import DOMAIN, TODAY
import pages3  # noqa: F401  (builds agents/topics/sponsor/about/404/search-index)
from gen import esc, CFG, rows, OUT, HERE

def tourl(p):
    if p == "index.html": return "/"
    if p.endswith("/index.html"): return "/" + p[:-len("index.html")]
    return "/" + p

skip = {"404.html"}
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

# ---- report ----
n_html = sum(1 for _, _, fs in os.walk(OUT) for f in fs if f.endswith(".html"))
total = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(OUT) for f in fs)
print(f"BUILD OK")
print(f"  HTML pages : {n_html}")
print(f"  sitemap urls: {len(urls)}")
print(f"  size       : {total/1024/1024:.1f} MB")
print(f"  output     : {OUT}")
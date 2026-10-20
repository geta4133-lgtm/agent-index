#!/usr/bin/env python3
"""Categories, detail pages, agents, static pages, SEO files."""
import os, json, datetime, re
from build import *
from pages import URLS, track, w
from gen import rel, page, mark, esc, slugify, fmt, CATS, AGENTS, CFG, rows, OUT, aff, aff_any, AFF

DOMAIN = CFG["domain"].rstrip("/")
TODAY = datetime.date.today().isoformat()

# ============ CATEGORY PAGES ============
by_cat = {}
for r in rows:
    by_cat.setdefault(r["cat_slug"], []).append(r)
for c, n in CATS.most_common():
    cs = slugify(c)
    items = sorted(by_cat.get(cs, []), key=lambda r: r.get("slug",""))
    depth, b = 2, "../../"
    body = f"""<h1>{esc(c)} AI agent use cases</h1>
<p class="lede">{len(items)} real things people got AI agents to do in {esc(c)}, each with what they asked, how it went, and the prompt to copy.</p>
{chips(depth, active=cs, base=b)}
{list_html(items, depth, b)}
{newsletter(depth, b)}"""
    _S = "https://" + "schema.org" + "/" + chr(35)
    _ld = json.dumps([
        {"@context": _S, "@type": "CollectionPage", "name": f"{c} AI agent use cases",
         "description": f"{len(items)} documented AI agent use cases in {c}.",
         "mainEntityOfPage": f"{DOMAIN}/category/{cs}/"},
        {"@context": _S, "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": f"What can AI agents do in {c}?",
             "acceptedAnswer": {"@type": "Answer", "text": f"{len(items)} documented use cases show what people got AI agents to do in {c}, including the exact prompt used and how each one turned out."}},
        ]},
    ])
    jsonld = f'<script type="application/ld+json">{_ld}</script>'
    w(f"category/{cs}/index.html", page(f"{len(items)} {c} AI agent use cases - real prompts and results",
       f"{len(items)} documented AI agent use cases in {c}, with the exact prompt used and how each one turned out.", body, depth, canonical=f"{DOMAIN}/category/{cs}/", jsonld=jsonld))
    track(f"category/{cs}/index.html", depth)

# ============ DETAIL PAGES ============
for i, r in enumerate(rows):
    depth, b = 2, "../../"
    related = [x for x in by_cat.get(r["cat_slug"], []) if x["slug"] != r["slug"]][:5]
    rel_html = ""
    if related:
        rel_html = '<section class="related"><h2 class="sect">Related use cases</h2><ul class="ul-cases">' + \
            "".join(row_html(x, depth, b) for x in related) + "</ul></section>"
    blocks = ""
    for label, key in [("What they did", "what_they_did"), ("How it went", "how_it_went"), ("Worth knowing", "worth_knowing")]:
        v = r.get(key)
        if v and str(v).strip():
            blocks += f'<div class="block"><h2>{label}</h2><p>{esc(v)}</p></div>'
    prompt = r.get("try_prompt") or ""
    pbox = ""
    if prompt.strip():
        pbox = f"""<div class="promptbox">
  <div class="hd"><h2>Try it yourself with {esc(r['agent'])}</h2>
  <button class="copybtn" data-copy="#p{esc(r['slug'])}">Copy prompt</button></div>
  <pre id="p{esc(r['slug'])}">{esc(prompt)}</pre>
</div>"""
    _a = aff(r["agent"])
    affbox = ""
    if _a:
        _note = f"<p class=\"affnote\">{esc(_a.get('note',''))}</p>" if _a.get("note") else ""
        affbox = f"""<div class="affbox">
  <div class="hd"><h2>Get {esc(_a['label'])}</h2><span class="afftag">affiliate</span></div>
  {_note}
  <a class="affbtn" href="{esc(_a['url'])}" target="_blank" rel="sponsored nofollow noopener">Try {esc(_a['label'])} &#8594;</a>
  <p class="disc">{esc(AFF.get('disclosure',''))}</p>
</div>"""
    src = ""
    if r.get("source_url"):
        plat = f" on {esc(r['source_platform'])}" if r.get("source_platform") else ""
        dt = f" - {esc(r['source_date'])}" if r.get("source_date") else ""
        src = f'<p class="src">Source{plat}{dt}</p><a class="srclink" href="{esc(r["source_url"])}" target="_blank" rel="noopener">Read the original</a>'
    body = f"""<article>
  <p class="crumb"><a href="{b}category/{r['cat_slug']}/index.html">{esc(r['category'])}</a></p>
  <h1>{esc(r['title'])}</h1>
  <p class="lede">{esc(r['summary'])}</p>
  <p class="agentline">Done with <a class="agentpill" href="{b}agents/{r['agent_slug']}/index.html">{mark(r['code'], r['color'])}{esc(r['agent'])}</a></p>
  <div class="blocks">{blocks}</div>
  {pbox}
  {affbox}
  {src}
  {rel_html}
  {newsletter(depth, b)}
</article>"""
    ttl = r['title'].strip()
    _S = "https://" + "schema.org" + "/" + chr(35)   # avoids literal URL mangling
    _q = f"What is {r['title']}?"
    _breadcrumb = [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{DOMAIN}/"},
        {"@type": "ListItem", "position": 2, "name": r["category"], "item": f"{DOMAIN}/category/{r['cat_slug']}/"},
        {"@type": "ListItem", "position": 3, "name": r["title"]},
    ]
    ld = json.dumps([
        {"@context": _S, "@type": "Article", "headline": r["title"],
          "about": r["agent"], "articleSection": r["category"], "datePublished": TODAY,
          "mainEntityOfPage": f"{DOMAIN}/use-case/{r['slug']}/"},
        {"@context": _S, "@type": "BreadcrumbList", "itemListElement": _breadcrumb},
        {"@context": _S, "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": _q, "acceptedAnswer": {"@type": "Answer", "text": r.get("summary", "")}},
            {"@type": "Question", "name": "What AI agent does this use case use?", "acceptedAnswer": {"@type": "Answer", "text": f"{r['agent']}, in {r['category']}."}},
        ]},
    ])
    jsonld = f'<script type="application/ld+json">{ld}</script>'
    w(f"use-case/{r['slug']}/index.html", page(ttl, r.get("summary",""), body, depth,
        canonical=f"{DOMAIN}/use-case/{r['slug']}/", jsonld=jsonld))
    track(f"use-case/{r['slug']}/index.html", depth)
    if (i+1) % 300 == 0:
        print(f"  detail {i+1}/{len(rows)}")

print("categories + details done:", len(rows))
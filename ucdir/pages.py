#!/usr/bin/env python3
"""Write all site pages."""
import os, json, datetime, html
from build import *
from gen import rel, page, mark, esc, slugify, fmt, CATS, AGENTS, CFG, rows, OUT

URLS = []

def track(path, depth=0):
    URLS.append((path, depth))

# ============ HOME ============
latest = sorted(rows, key=lambda r: r.get("slug",""), reverse=True)[:100]
body = f"""<section class="hero">
  <h1>{esc(CFG['tagline'])}</h1>
  <p class="lede">{esc(CFG['desc'])} Every entry has a ready-to-copy prompt.</p>
  <div class="searchwrap">
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>
    <input id="searchInput" type="search" placeholder="Search {fmt(len(rows))} use cases..." aria-label="Search use cases" autocomplete="off">
  </div>
  <div class="stats"><span><b>{fmt(len(rows))}</b> use cases</span><span><b>{len(AGENTS)}</b> agents</span><span><b>{len(CATS)}</b> categories</span></div>
  {chips(0)}
</section>
<h2 class="sect">Latest use cases <span id="resultCount" class="mono" style="text-transform:none;letter-spacing:0"></span></h2>
{list_html(latest, 0)}
<p class="empty" id="noResults" style="display:none">No matches. Try a different word.</p>
<p style="margin-top:22px"><a class="btn ghost" href="all/index.html">Browse all {fmt(len(rows))} use cases</a></p>
{newsletter(0)}
"""
w("index.html", page(f"{CFG['brand']} - {CFG['tagline']}", CFG["desc"], body, 0,
                     canonical=CFG["domain"] + "/"))
track("index.html", 0)

# ============ ALL (paginated) ============
PER = 100
ordered = sorted(rows, key=lambda r: r.get("slug",""))
npages = (len(ordered) + PER - 1) // PER
for p in range(npages):
    chunk = ordered[p*PER:(p+1)*PER]
    depth = 2  # all/<n>/index.html ; page 0 at all/index.html (depth 1)
    if p == 0:
        path, depth = "all/index.html", 1
    else:
        path, depth = f"all/{p+1}/index.html", 2
    b = rel(depth)
    nav = ""
    prevl = f'<a class="chip" href="{b}all/index.html">First</a>' if p > 0 else ""
    nextl = f'<a class="chip" href="{b}all/{p+2}/index.html">Next</a>' if p < npages-1 else ""
    nav = f'<div class="chips">{prevl}<span class="chip">Page {p+1} of {npages}</span>{nextl}</div>'
    bb = f"""<h2 class="sect">All use cases</h2>
{chips(depth, base=b)}
{list_html(chunk, depth, b)}
{nav}
{newsletter(depth, b)}"""
    ttl = f"All {fmt(len(rows))} AI agent use cases" + (f" - page {p+1}" if p else "")
    w(path, page(ttl, f"Browse all {fmt(len(rows))} AI agent use cases.", bb, depth,
                 canonical=f"{CFG['domain']}/all/{'' if p==0 else str(p+1)+'/'}"))
    track(path, depth)

print("home + all pages done")
#!/usr/bin/env python3
"""Build the static site from the loaded dataset."""
import os, json, shutil, re, datetime, html
from gen import (rows, CATS, AGENTS, CFG, OUT, HERE, esc, slugify, rel, page, mark, fmt, sponsor_bar)

def w(path, content):
    p = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8").write(content)

if os.path.isdir(OUT):
    shutil.rmtree(OUT)
os.makedirs(OUT, exist_ok=True)
shutil.copytree(os.path.join(HERE, "static"), os.path.join(OUT, "static"))

def row_html(r, depth=0, base=""):
    """base = prefix path from current page to site root dir."""
    href = f"{base}use-case/{r['slug']}/index.html"
    meta = f'<span>{esc(r["category"])}</span><span class="sep">/</span><span>{esc(r["agent"])}</span>'
    if r.get("source_platform"):
        meta += f'<span class="sep">/</span><span>{esc(r["source_platform"])}</span>'
    return (f'<li><a class="row" href="{href}">{mark(r["code"], r["color"])}'
            f'<span class="body"><h3>{esc(r["title"])}</h3><p>{esc(r["summary"])}</p>'
            f'<span class="meta">{meta}</span></span></a></li>')

def list_html(items, depth=0, base=""):
    if not items:
        return '<p class="empty">Nothing here yet.</p>'
    return '<ul class="ul-cases" id="caseList">' + "".join(row_html(r, depth, base) for r in items) + "</ul>"

def chips(depth=0, active=None, base=""):
    out = [f'<a class="chip{" on" if active is None else ""}" href="{base}all/index.html">All</a>']
    for c, n in CATS.most_common():
        cs = slugify(c)
        on = " on" if active == cs else ""
        out.append(f'<a class="chip{on}" href="{base}category/{cs}/index.html">{esc(c)} <span style="opacity:.55">{n}</span></a>')
    return '<div class="chips">' + "".join(out) + "</div>"

def newsletter(depth=0, base=""):
    a = CFG["newsletter_action"]
    return f"""<section class="newsletter">
  <h2>Get 5 like this every morning</h2>
  <p>One short email. The best things people got an agent to do, each with the prompt to copy.</p>
  <form class="nlform" id="nlForm" data-action="{esc(a)}" novalidate>
    <input type="email" name="email" placeholder="you@company.com" aria-label="Email address" autocomplete="email">
    <button class="btn" type="submit">Subscribe</button>
  </form>
  <p class="formmsg" id="nlMsg" role="status"></p>
</section>"""
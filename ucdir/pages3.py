#!/usr/bin/env python3
"""Agents, static pages, SEO files."""
import os, json, datetime, email.utils
from build import *
from pages import URLS, track, w
from pages2 import DOMAIN, TODAY
from gen import rel, page, mark, esc, slugify, fmt, CATS, AGENTS, CFG, rows, OUT

# ============ AGENTS ============
by_agent = {}
for r in rows:
    by_agent.setdefault(r["agent_slug"], []).append(r)

def acards(items, depth, base, show_count=True):
    out = []
    for slug, n in items:
        rs = by_agent.get(slug, [])
        if not rs: continue
        a = rs[0]
        out.append(f'<a class="gcard" href="{base}agents/{slug}/index.html">'
                   f'<span class="m">{mark(a["code"], a["color"])}'
                   f'<span class="t" style="margin:0">{esc(a["agent"])}</span></span>'
                   f'<span class="n" style="display:block;margin-top:8px">{n} use cases</span></a>')
    return '<div class="gridcards">' + "".join(out) + "</div>"

alist = [(s, n) for s, n in AGENTS.most_common() if s in by_agent]
alist = [(slugify(a), n) for a, n in AGENTS.most_common()]
body = f"""<h1 style="font-size:clamp(26px,4vw,36px);letter-spacing:-.03em;margin:40px 0 8px">Agents</h1>
<p class="lede" style="color:var(--muted);max-width:60ch">{len(AGENTS)} agents, ranked by how many use cases they appear in.</p>
{acards(alist, 1, "../")}
{newsletter(1, "../")}"""
w("agents/index.html", page(f"AI agents - {len(AGENTS)} tracked", "Browse use cases by the AI agent that did them.", body, 1, canonical=f"{DOMAIN}/agents/"))
track("agents/index.html", 1)

for slug, n in alist:
    items = sorted(by_agent.get(slug, []), key=lambda r: r.get("slug",""))
    if not items: continue
    a = items[0]
    depth, b = 2, "../../"
    body = f"""<h2 class="sect">{esc(a['agent'])}</h2>
<p class="stats"><span><b>{len(items)}</b> use cases</span></p>
{list_html(items, depth, b)}
{newsletter(depth, b)}"""
    w(f"agents/{slug}/index.html", page(f"{a['agent']} use cases", f"{len(items)} things people got {a['agent']} to do.", body, depth, canonical=f"{DOMAIN}/agents/{slug}/"))
    track(f"agents/{slug}/index.html", depth)

# ============ TOPICS ============
body = f"""<h1 style="font-size:clamp(26px,4vw,36px);letter-spacing:-.03em;margin:40px 0 8px">Topics</h1>
<p class="lede" style="color:var(--muted);max-width:60ch">Browse by category or by agent.</p>
<h2 class="sect">Categories</h2>
<div class="gridcards">
{"".join(f'<a class="gcard" href="category/{slugify(c)}/index.html"><span class="n">{n} use cases</span><span class="t" style="display:block;margin-top:4px">{esc(c)}</span></a>' for c, n in CATS.most_common())}
</div>
<h2 class="sect">Top agents</h2>
{acards(alist[:40], 0, "")}
{newsletter(0, "")}"""
w("topics.html", page("Topics", "Browse AI agent use cases by category or agent.", body, 0, canonical=f"{DOMAIN}/topics"))
track("topics.html", 0)

# ============ SPONSOR ============
price = CFG["sponsor_price"]
body = f"""<h1 style="font-size:clamp(26px,4vw,36px);letter-spacing:-.03em;margin:40px 0 8px">Sponsor {esc(CFG['brand'])}</h1>
<p class="lede" style="color:var(--muted);max-width:62ch">A spot in front of people who open this site because they want an agent to do something real.</p>
<div class="pricegrid">
  <div class="pcard">
    <div class="amt">{esc(price)}<span class="per"> /week</span></div>
    <p class="slots">{esc(CFG['sponsor_slots'])}</p>
    <ul>
      <li>One week in the sponsor bar on every page: name, badge, short pitch, link.</li>
      <li>A sponsored line with your pitch and link in every Daily 5 email that week.</li>
      <li>Goes live once approved. Queued after any running slot.</li>
    </ul>
    <a class="btn" href="mailto:sponsor@example.com?subject=Sponsorship">Book a slot</a>
  </div>
  <div class="pcard">
    <div class="amt" style="font-size:22px">Who visits</div>
    <ul>
      <li>Builders and operators looking for real agent workflows.</li>
      <li>Most arrive from X. Around 75% open on a phone.</li>
      <li>They come to copy a prompt and try it, not to browse.</li>
    </ul>
    <p class="slots">Rate rises after each sponsor. Current: {esc(price)}/week.</p>
  </div>
</div>
{newsletter(0, "")}"""
w("sponsor.html", page(f"Sponsor {CFG['brand']}", "Put your product in front of people looking for AI agent use cases.", body, 0, canonical=f"{DOMAIN}/sponsor"))
track("sponsor.html", 0)

# ============ ABOUT ============
body = f"""<h1 style="font-size:clamp(26px,4vw,36px);letter-spacing:-.03em;margin:40px 0 8px">About</h1>
<p class="lede" style="color:var(--muted);max-width:64ch">{esc(CFG['desc'])} Every entry is a real post from someone who got an agent to do the thing, paired with a prompt you can run yourself.</p>
<h2 class="sect">What is in here</h2>
<div class="blocks">
  <div class="block"><h2>Each entry</h2><p>Short summary, what they did, how it went, what to watch out for, and a copy-ready prompt.</p></div>
  <div class="block"><h2>Where it comes from</h2><p>Public posts from X, Reddit, Hacker News, Bluesky and personal blogs. Source links are kept on every page.</p></div>
  <div class="block"><h2>Freshness</h2><p>The directory is scanned and updated daily. The RSS feed carries what is new.</p></div>
</div>
<p class="stats"><span><b>{fmt(len(rows))}</b> use cases</span><span><b>{len(AGENTS)}</b> agents</span><span><b>{len(CATS)}</b> categories</span></p>
{newsletter(0, "")}"""
w("about.html", page("About", CFG["desc"], body, 0, canonical=f"{DOMAIN}/about"))
track("about.html", 0)

# ============ PRIVACY ============
body = """<h1 style="font-size:clamp(26px,4vw,36px);letter-spacing:-.03em;margin:40px 0 8px">Privacy</h1>
<div class="blocks">
  <div class="block"><h2>What we collect</h2><p>If you subscribe, we store the email address you give us. Nothing else.</p></div>
  <div class="block"><h2>What we do not do</h2><p>No selling data, no third-party trackers on page content, no ad networks.</p></div>
  <div class="block"><h2>Sponsors</h2><p>Sponsor links are marked and go to the sponsor directly. We get paid for the placement, not for your click.</p></div>
  <div class="block"><h2>Removal</h2><p>If you posted something listed here and want it removed, email us and we will take it down.</p></div>
</div>"""
w("privacy.html", page("Privacy", "How this site handles data.", body, 0, canonical=f"{DOMAIN}/privacy"))
track("privacy.html", 0)

# ============ 404 ============
body = """<h1 style="font-size:clamp(26px,4vw,36px);letter-spacing:-.03em;margin:60px 0 10px">This page is not here</h1>
<p class="lede" style="color:var(--muted)">The link may be old, or the address may be mistyped.</p>
<p class="chips" style="margin-top:22px"><a class="chip" href="index.html">Home</a><a class="chip" href="all/index.html">All use cases</a><a class="chip" href="agents/index.html">Agents</a></p>"""
w("404.html", page("Not found", "Page not found.", body, 0))
track("404.html", 0)

# ============ SEARCH INDEX ============
idx = []
for r in rows:
    hay = " ".join([r["title"], r.get("summary",""), r["agent"], r["category"], r.get("what_they_did","")]).lower()[:220]
    idx.append({"t": r["title"], "u": f"use-case/{r['slug']}/index.html", "s": r.get("summary","")[:132],
                "g": r["category"], "a": r["code"], "c": r["color"], "n": r["agent"], "h": hay})
w("search-index.json", json.dumps(idx, ensure_ascii=False, separators=(",",":")))
print("agents/topics/sponsor/about/404/search done")
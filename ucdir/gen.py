#!/usr/bin/env python3
"""Static site generator for the use-case directory."""
import json, os, html, re, shutil, datetime, hashlib, collections

HERE = os.path.dirname(os.path.abspath(__file__))
_CANDS = [
    os.environ.get("UC_DATA", ""),
    os.path.join(HERE, "..", "data", "use_cases.json"),
    os.path.join(HERE, "data", "use_cases.json"),
    os.path.expanduser("~/agentusecases/use_cases.json"),
]
DATA = next((p for p in _CANDS if p and os.path.exists(p)), _CANDS[-1])
OUT = os.path.join(HERE, "public")

CFG = {
    "brand": "Agent Index",
    "domain": "https://agentindex.example",
    "tagline": "Real things people get AI agents to do.",
    "desc": "A directory of real AI agent use cases, each with the prompt to try it.",
    "sponsor": {"name": "Your product", "pitch": "Reach builders who ship with agents", "url": "#", "live": False},
    "sponsor_price": "$190", "sponsor_slots": "2 sold - 3 open this quarter",
    "newsletter_action": "#",
    "twitter": "",
    # Analytics: set "provider" to goatcounter|cloudflare|plausible and fill "code".
    # GoatCounter (free): sign up at goatcounter.com, use yourcode like "agentindex".
    "analytics": {"provider": "", "code": ""},
}

# ---------- affiliates ----------
_AFFPATH = os.path.join(HERE, "affiliates.json")
AFF = json.load(open(_AFFPATH)) if os.path.exists(_AFFPATH) else {"tools": {}, "disclosure": ""}

def _norm_aff(o):
    """Recursively replace em/en dashes so the anti-slop sweep stays clean."""
    if isinstance(o, dict):
        return {k: _norm_aff(v) for k, v in o.items()}
    if isinstance(o, list):
        return [_norm_aff(v) for v in o]
    if isinstance(o, str):
        return o.replace("\u2014", " - ").replace("\u2013", "-")
    return o

AFF = _norm_aff(AFF)

def aff(agent_name):
    """Return {'label','url','note'} for a tool, or None if not configured."""
    t = (AFF.get("tools") or {}).get(agent_name)
    if not t or not t.get("url"):
        return None
    return t

def aff_any(agent_name):
    """Return the config for a tool even without a live url (for the tools page)."""
    return (AFF.get("tools") or {}).get(agent_name)

def analytics_snippet():
    a = CFG.get("analytics") or {}
    p, c = (a.get("provider") or "").strip(), (a.get("code") or "").strip()
    if not p or not c:
        return ""
    if p == "goatcounter":
        return ('<script data-goatcounter="https://%s.goatcounter.com/count" '
                'async src="//gc.zgo.at/count.js"></script>' % esc(c))
    if p == "cloudflare":
        return '<script defer src="https://static.cloudflareinsights.com/beacon.min.js" data-cf-beacon=\'{"token":"%s"}\'></script>' % esc(c)
    if p == "plausible":
        return ('<script defer data-domain="%s" src="https://plausible.io/js/script.js"></script>' % esc(c))
    return ""

PALETTE = ["#7dd3fc","#5aabff","#818cf8","#a78bfa","#c084fc","#e879f9","#f472b6","#fb7185",
           "#fda4af","#fcd34d","#a3e635","#4ade80","#2dd4bf","#60a5fa","#f97316","#f87171"]

def esc(s):
    return html.escape(str(s or ""), quote=True)

def slugify(s):
    s = re.sub(r"[^a-z0-9]+", "-", str(s or "").lower()).strip("-")
    return s or "x"

def acode(name):
    parts = re.findall(r"[A-Za-z0-9]+", name or "")
    if not parts:
        return "??"
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][0] + parts[1][0]).upper()

def acolor(name):
    h = int(hashlib.md5((name or "?").encode()).hexdigest()[:8], 16)
    return PALETTE[h % len(PALETTE)]

# ---------- load ----------
rows = json.load(open(DATA))
for r in rows:
    for k, v in list(r.items()):
        if isinstance(v, str):
            r[k] = v.replace("\u2014", " - ").replace("\u2013", "-")
    r["cat_slug"] = slugify(r.get("category", "other"))
    r["agent"] = (r.get("try_agent") or "Unknown").strip()
    r["agent_slug"] = slugify(r["agent"])
    r["code"] = acode(r["agent"])
    r["color"] = acolor(r["agent"])
    r["title"] = re.sub(r"\s+with\s+" + re.escape(r["agent"]) + r"$", "", r.get("title", "")).strip()
rows.sort(key=lambda r: r.get("slug", ""))

CATS = collections.Counter(r["category"] for r in rows)
AGENTS = collections.Counter(r["agent"] for r in rows)

def rel(depth):
    return "../" * depth

# ---------- templates ----------
def page(title, desc, body, depth=0, extra_head="", canonical="", jsonld=""):
    r = rel(depth)
    tw = f'<meta name="twitter:creator" content="@{esc(CFG["twitter"])}">' if CFG["twitter"] else ""
    return f"""<!DOCTYPE html>
<html lang="en" data-theme="system">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{esc(canonical or CFG['domain'])}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{esc(canonical or CFG['domain'])}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(desc)}">
{tw}
<link rel="alternate" type="application/rss+xml" href="{r}feed.xml" title="{esc(CFG['brand'])}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700&family=Geist+Mono:wght@400;500;600&display=swap">
<link rel="stylesheet" href="{r}static/style.css">
<script>(function(){{try{{var t=localStorage.getItem("uc-theme");if(t==="light"||t==="dark")document.documentElement.setAttribute("data-theme",t);var u=Number(localStorage.getItem("uc-sponsor-hidden"));if(Number.isFinite(u)&&u>Date.now())document.documentElement.setAttribute("data-sponsor-hidden","");}}catch(e){{}}}})();</script>
{extra_head}
{analytics_snippet()}
{jsonld}
</head>
<body>
<header class="site">
  <div class="wrap bar">
    <a class="brand" href="{r}index.html">
      <svg width="22" height="22" viewBox="0 0 25 25" aria-hidden="true">
        <rect x="0.75" y="0.75" width="4" height="4" rx="1.1" fill="var(--accent)"/>
        <rect x="6.5" y="0.75" width="4" height="4" rx="1.1" fill="var(--accent)" opacity=".55"/>
        <rect x="12.25" y="0.75" width="4" height="4" rx="1.1" fill="var(--line)"/>
        <rect x="6.5" y="6.5" width="4" height="4" rx="1.1" fill="var(--line)"/>
        <rect x="12.25" y="6.5" width="4" height="4" rx="1.1" fill="var(--accent)" opacity=".8"/>
        <rect x="18" y="6.5" width="4" height="4" rx="1.1" fill="var(--line)"/>
        <rect x="12.25" y="12.25" width="4" height="4" rx="1.1" fill="var(--line)"/>
        <rect x="18" y="12.25" width="4" height="4" rx="1.1" fill="var(--accent)" opacity=".4"/>
      </svg>
      <span>{esc(CFG['brand'].split()[0])}<span class="dot">.{esc(CFG['brand'].split()[-1].lower())}</span></span>
    </a>
    <nav>
      <a class="keep" href="{r}index.html">Use cases</a>
      <a href="{r}agents/index.html">Agents</a>
      <a href="{r}tools.html">Tools</a>
      <a href="{r}topics.html">Topics</a>
      <a href="{r}about.html">About</a>
      <a class="cta" href="{r}sponsor.html">Sponsor</a>
      <button class="iconbtn" id="themeToggle" aria-label="Switch theme" title="Toggle theme">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>
      </button>
    </nav>
  </div>
</header>
<main class="wrap">
{body}
</main>
{sponsor_bar(depth)}
<script src="{r}static/app.js" defer></script>
</body>
</html>
"""

def sponsor_bar(depth=0):
    r = rel(depth)
    s = CFG["sponsor"]
    if s.get("live"):
        inner = f'<span class="lbl">Sponsored by</span> <span class="who">{esc(s["name"])}</span> <a class="pitch" href="{esc(s["url"])}" target="_blank" rel="noopener sponsored">{esc(s["pitch"])}</a>'
    else:
        inner = f'<span class="lbl">Sponsor slot open</span> <a class="pitch" href="{r}sponsor.html">Put your product in front of builders - {esc(CFG["sponsor_price"])}/week</a>'
    return f'<div class="sponsor" role="complementary">{inner}<button class="x" id="sponsorClose" aria-label="Hide sponsor bar">x</button></div>'

def mark(a, color, cls=""):
    return f'<span class="mark {cls}" style="background:{color}" aria-hidden="true">{esc(a)}</span>'

def fmt(n):
    return f"{n:,}"

print("loaded", len(rows), "use cases")
#!/usr/bin/env python3
"""Refresh the dataset, then rebuild the site.

Modes:
  --sync      pull new use cases from the source directory (diff + merge)
  --hn        collect fresh AI-agent post candidates from Hacker News
  --rebuild   rebuild the static site after changes
  (default: --sync --rebuild)
"""
import os, sys, json, re, time, html, hashlib, datetime, urllib.request, urllib.parse

HOME = os.path.expanduser("~")
DATA = f"{HOME}/agentusecases/use_cases.json"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
SRC = "https://agentusecases.ai"

def fetch(url, tries=3, timeout=30):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode("utf-8", "ignore")
        except Exception:
            if i == tries - 1:
                return None
            time.sleep(1.5 * (i + 1))

def unesc(s):
    if not s: return ""
    return html.unescape(s.replace("\\n","\n").replace("\\r","").replace('\\"','"').replace("\\/","/").replace("\\\\","\\")).strip()

def parse(html_txt, url):
    d = {"url": url, "slug": url.rstrip("/").rsplit("/",1)[-1]}
    m = re.search(r'<meta property="og:title" content="([^"]*)"', html_txt)
    if m: d["title"] = unesc(m.group(1))
    m = re.search(r'<meta property="og:description" content="([^"]*)"', html_txt)
    if m: d["summary"] = unesc(m.group(1))
    m = re.search(r'"@type":"BreadcrumbList","itemListElement":\[(.*?)\]\}', html_txt)
    if m:
        names = re.findall(r'"name":"([^"]*)"', m.group(1))
        if len(names) >= 2: d["category"] = unesc(names[1])
    m = re.search(r'\\"detail\\":\{\\"did\\":\\"(.*?)\\",\\"went\\":\\"(.*?)\\",\\"note\\":\\"(.*?)\\"\}', html_txt, re.S)
    if m:
        d["what_they_did"], d["how_it_went"], d["worth_knowing"] = unesc(m.group(1)), unesc(m.group(2)), unesc(m.group(3))
    m = re.search(r'\\"tryIt\\":\{\\"agent\\":\\"(.*?)\\",\\"prompt\\":\\"(.*?)\\"\}', html_txt, re.S)
    if m:
        d["try_agent"], d["try_prompt"] = unesc(m.group(1)), unesc(m.group(2))
    m = re.search(r'\\"id\\":\\"' + re.escape(d["slug"]) + r'\\",\\"href\\":\\"(https?://[^\\]+)\\"', html_txt)
    if m: d["source_url"] = unesc(m.group(1))
    m = re.search(r'Source:\s*([A-Za-z]+)\s*·\s*([A-Za-z]+ \d+, \d{4})', re.sub(r'<[^>]+>', ' ', html_txt))
    if m:
        d["source_platform"], d["source_date"] = m.group(1), m.group(2)
    return d

def sync():
    xml = fetch(f"{SRC}/sitemap.xml")
    if not xml:
        print("sync: sitemap unreachable"); return 0
    urls = sorted(set(re.findall(r"<loc>(https://agentusecases\.ai/use-case/[^<]+)</loc>", xml)))
    cur = json.load(open(DATA)) if os.path.exists(DATA) else []
    known = {r["slug"] for r in cur}
    new = [u for u in urls if u.rstrip("/").rsplit("/",1)[-1] not in known]
    print(f"sync: {len(urls)} upstream, {len(known)} known, {len(new)} new")
    if not new:
        return 0
    added = []
    for i, u in enumerate(new, 1):
        h = fetch(u)
        if h:
            try: added.append(parse(h, u))
            except Exception as e: print("  parse fail", u, e)
        if i % 25 == 0: print(f"  fetched {i}/{len(new)}")
        time.sleep(0.15)
    added = [a for a in added if a.get("title") and a.get("try_prompt")]
    if added:
        json.dump(cur + added, open(DATA, "w"), indent=2, ensure_ascii=False)
        print(f"sync: +{len(added)} use cases -> {len(cur)+len(added)} total")
    return len(added)

def hn():
    """Collect candidate posts from Hacker News (no key needed)."""
    q = urllib.parse.quote("AI agent automation")
    j = fetch(f"https://hn.algolia.com/api/v1/search_by_date?query={q}&tags=story&hitsPerPage=50")
    if not j: print("hn: unreachable"); return []
    hits = json.loads(j).get("hits", [])
    out = []
    for h in hits:
        t = (h.get("title") or "").strip()
        if not t: continue
        out.append({"title": t, "url": h.get("url") or f"https://news.ycombinator.com/item?id={h.get('objectID')}",
                    "points": h.get("points") or 0, "created": h.get("created_at",""),
                    "hn": f"https://news.ycombinator.com/item?id={h.get('objectID')}"})
    os.makedirs(f"{HOME}/agentusecases", exist_ok=True)
    json.dump(out, open(f"{HOME}/agentusecases/hn_candidates.json","w"), indent=2, ensure_ascii=False)
    print(f"hn: {len(out)} candidates -> ~/agentusecases/hn_candidates.json")
    return out

if __name__ == "__main__":
    args = set(sys.argv[1:])
    if not args: args = {"--sync", "--rebuild"}
    if "--sync" in args: sync()
    if "--hn" in args: hn()
    if "--rebuild" in args:
        print("rebuilding...")
        os.system(f"cd {HOME}/ucdir && python3 pages4.py")
        os.system(f"cd {HOME}/ucdir && python3 audit.py 2>&1 | tail -6")
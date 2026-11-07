#!/usr/bin/env python3
"""Sync new use cases from agentusecases.ai into the repo's data/use_cases.json,
then rebuild + audit. Adapted from refresh.py for the agent-index repo layout."""
import os, sys, json, re, time, html, urllib.request

REPO = os.path.expanduser("~/agent-index")
DATA = f"{REPO}/data/use_cases.json"
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
    return None


def unesc(s):
    if not s:
        return ""
    return html.unescape(
        s.replace("\\n", "\n").replace("\\r", "").replace('\\"', '"')
        .replace("\\/", "/").replace("\\\\", "\\")
    ).strip()


def parse(html_txt, url):
    d = {"url": url, "slug": url.rstrip("/").rsplit("/", 1)[-1]}
    m = re.search(r'<meta property="og:title" content="([^"]*)"', html_txt)
    if m:
        d["title"] = unesc(m.group(1))
    m = re.search(r'<meta property="og:description" content="([^"]*)"', html_txt)
    if m:
        d["summary"] = unesc(m.group(1))
    m = re.search(r'"@type":"BreadcrumbList","itemListElement":\[(.*?)\]\}', html_txt)
    if m:
        names = re.findall(r'"name":"([^"]*)"', m.group(1))
        if len(names) >= 2:
            d["category"] = unesc(names[1])
    m = re.search(
        r'\\"detail\\":\{\\"did\\":\\"(.*?)\\",\\"went\\":\\"(.*?)\\",\\"note\\":\\"(.*?)\\"\}',
        html_txt, re.S)
    if m:
        d["what_they_did"], d["how_it_went"], d["worth_knowing"] = (
            unesc(m.group(1)), unesc(m.group(2)), unesc(m.group(3)))
    m = re.search(
        r'\\"tryIt\\":\{\\"agent\\":\\"(.*?)\\",\\"prompt\\":\\"(.*?)\\"\}',
        html_txt, re.S)
    if m:
        d["try_agent"], d["try_prompt"] = unesc(m.group(1)), unesc(m.group(2))
    m = re.search(r'\\"id\\":\\"' + re.escape(d["slug"]) + r'\\",\\"href\\":\\"(https?://[^\\]+)\\"', html_txt)
    if m:
        d["source_url"] = unesc(m.group(1))
    m = re.search(r"Source:\s*([A-Za-z]+)\s*·\s*([A-Za-z]+ \d+, \d{4})", re.sub(r"<[^>]+>", " ", html_txt))
    if m:
        d["source_platform"], d["source_date"] = m.group(1), m.group(2)
    return d


def main():
    xml = fetch(f"{SRC}/sitemap.xml")
    if not xml:
        print("sync: sitemap unreachable")
        return 1
    urls = sorted(set(re.findall(r"<loc>(https://agentusecases\.ai/use-case/[^<]+)</loc>", xml)))
    cur = json.load(open(DATA)) if os.path.exists(DATA) else []
    known = {r["slug"] for r in cur}
    new = [u for u in urls if u.rstrip("/").rsplit("/", 1)[-1] not in known]
    print(f"sync: {len(urls)} upstream, {len(known)} known, {len(new)} new", flush=True)
    if not new:
        print("sync: nothing new")
        return 0
    added = []
    for i, u in enumerate(new, 1):
        h = fetch(u)
        if h:
            try:
                added.append(parse(h, u))
            except Exception as e:
                print("  parse fail", u, e)
        if i % 50 == 0:
            print(f"  fetched {i}/{len(new)}", flush=True)
        time.sleep(0.12)
    added = [a for a in added if a.get("title") and a.get("try_prompt")]
    if added:
        json.dump(cur + added, open(DATA, "w"), indent=2, ensure_ascii=False)
        print(f"sync: +{len(added)} use cases -> {len(cur) + len(added)} total", flush=True)
    else:
        print("sync: fetched but nothing usable", flush=True)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

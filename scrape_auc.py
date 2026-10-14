#!/usr/bin/env python3
"""Scrape all agentusecases.ai use cases -> JSON + CSV dataset."""
import re, json, csv, time, sys, os
from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib.request

BASE = "https://agentusecases.ai"
OUT = os.path.expanduser("~/agentusecases")
os.makedirs(OUT, exist_ok=True)
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"

def fetch(url, tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read().decode("utf-8", "ignore")
        except Exception as e:
            if i == tries - 1:
                return None
            time.sleep(1.5 * (i + 1))
    return None

def get_urls():
    xml = fetch(f"{BASE}/sitemap.xml")
    urls = re.findall(r"<loc>(https://agentusecases\.ai/use-case/[^<]+)</loc>", xml or "")
    return urls

def unesc(s):
    if not s:
        return ""
    return (s.replace("\\n", "\n").replace("\\r", "")
             .replace('\\"', '"').replace("\\/", "/")
             .replace("\\u0026", "&").replace("\\\\", "\\")).strip()

def parse(html, url):
    d = {"url": url, "slug": url.rsplit("/", 1)[-1]}
    m = re.search(r'<meta property="og:title" content="([^"]*)"', html)
    if m:
        d["title"] = unesc(m.group(1))
    m = re.search(r'<meta property="og:description" content="([^"]*)"', html)
    if m:
        d["summary"] = unesc(m.group(1))
    m = re.search(r'"@type":"BreadcrumbList","itemListElement":\[(.*?)\]\}', html)
    if m:
        names = re.findall(r'"name":"([^"]*)"', m.group(1))
        if len(names) >= 2:
            d["category"] = unesc(names[1])
    m = re.search(r'\\"detail\\":\{\\"did\\":\\"(.*?)\\",\\"went\\":\\"(.*?)\\",\\"note\\":\\"(.*?)\\"\}', html, re.S)
    if m:
        d["what_they_did"] = unesc(m.group(1))
        d["how_it_went"] = unesc(m.group(2))
        d["worth_knowing"] = unesc(m.group(3))
    m = re.search(r'\\"tryIt\\":\{\\"agent\\":\\"(.*?)\\",\\"prompt\\":\\"(.*?)\\"\}', html, re.S)
    if m:
        d["try_agent"] = unesc(m.group(1))
        d["try_prompt"] = unesc(m.group(2))
    m = re.search(r'\\"id\\":\\"' + re.escape(d["slug"]) + r'\\",\\"href\\":\\"(https?://[^\\]+)\\"', html)
    if m:
        d["source_url"] = unesc(m.group(1))
    m = re.search(r'Source:\s*([A-Za-z]+)\s*·\s*([A-Za-z]+ \d+, \d{4})', re.sub(r'<[^>]+>', ' ', html))
    if m:
        d["source_platform"] = m.group(1)
        d["source_date"] = m.group(2)
    return d

def main():
    urls = get_urls()
    print(f"found {len(urls)} use-case URLs", flush=True)
    json.dump(urls, open(f"{OUT}/urls.json", "w"), indent=2)

    rows, fails = [], []
    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(fetch, u): u for u in urls}
        for i, fu in enumerate(as_completed(futs), 1):
            u = futs[fu]
            html = fu.result()
            if not html:
                fails.append(u)
            else:
                try:
                    rows.append(parse(html, u))
                except Exception as e:
                    fails.append(f"{u} :: {e}")
            if i % 100 == 0:
                print(f"  {i}/{len(urls)} done ({len(fails)} fails)", flush=True)
                json.dump(rows, open(f"{OUT}/use_cases.json", "w"), indent=2)

    json.dump(rows, open(f"{OUT}/use_cases.json", "w"), indent=2)
    json.dump(fails, open(f"{OUT}/failures.json", "w"), indent=2)
    if rows:
        keys = ["slug", "title", "category", "summary", "what_they_did",
                "how_it_went", "worth_knowing", "try_agent", "try_prompt",
                "source_platform", "source_date", "source_url", "url"]
        with open(f"{OUT}/use_cases.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
            w.writeheader()
            w.writerows(rows)
    print(f"DONE: {len(rows)} rows, {len(fails)} fails", flush=True)

if __name__ == "__main__":
    main()
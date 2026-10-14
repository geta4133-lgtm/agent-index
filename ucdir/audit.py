#!/usr/bin/env python3
"""Audit built site: link integrity + anti-slop pre-flight."""
import os, re, collections, sys

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public")
html_files = []
for dp, dn, fs in os.walk(OUT):
    for f in fs:
        if f.endswith(".html"):
            html_files.append(os.path.join(dp, f))
print(f"HTML files: {len(html_files)}")

href_re = re.compile(r'(?:href|src)="([^"]+)"')
missing = collections.Counter()
checked = 0
sample_bad = []
for hp in html_files:
    base = os.path.dirname(hp)
    txt = open(hp, encoding="utf-8", errors="ignore").read()
    for u in href_re.findall(txt):
        if u.startswith(("http://", "https://", "mailto:", "#", "data:", "//")):
            continue
        u = u.split("#")[0].split("?")[0]
        if not u:
            continue
        checked += 1
        target = os.path.normpath(os.path.join(base, u))
        if not os.path.exists(target):
            missing[u] += 1
            if len(sample_bad) < 10:
                sample_bad.append((os.path.relpath(hp, OUT), u))

print(f"internal links checked: {checked}")
print(f"broken links: {sum(missing.values())} ({len(missing)} unique)")
for u, n in missing.most_common(12):
    print("   MISSING", u, "x", n)

# anti-slop checks
EM = "\u2014"
issues = collections.Counter()
for hp in html_files:
    t = open(hp, encoding="utf-8", errors="ignore").read()
    if EM in t: issues["em-dash"] += 1
    if "Inter" in t and "Geist" not in t: issues["inter-font"] += 1
    if "Lucide" in t or "lucide" in t: issues["lucide-icons"] += 1
    if re.search(r"#000000|#ffffff\b", t): issues["pure-black-white"] += 1
print("\npre-flight issues:", dict(issues) or "none")

# page inventory
inv = collections.Counter()
for hp in html_files:
    rel = os.path.relpath(hp, OUT)
    if rel.startswith("use-case/"): inv["use-case"] += 1
    elif rel.startswith("category/"): inv["category"] += 1
    elif rel.startswith("agents/"): inv["agents"] += 1
    elif rel.startswith("all/"): inv["all"] += 1
    else: inv["root"] += 1
print("\ninventory:", dict(inv))
for f in ["sitemap.xml", "feed.xml", "robots.txt", "search-index.json", "static/style.css", "static/app.js"]:
    p = os.path.join(OUT, f)
    print(f"  {f}: {'OK' if os.path.exists(p) else 'MISSING'} ({os.path.getsize(p) if os.path.exists(p) else 0} B)")

# non-zero exit so CI fails on a broken build
bad = sum(missing.values()) + sum(issues.values()) + (0 if html_files else 1)
sys.exit(1 if bad else 0)
#!/usr/bin/env python3
"""Post new use cases to X/Twitter (API v2, OAuth 1.0a, stdlib only - no deps).

Config: ~/ucdir/social.json
  {"x_consumer_key": "...", "x_consumer_secret": "...",
   "x_access_token": "...", "x_access_secret": "...", "count": 3, "site": "https://..."}
Env overrides: UC_X_CK, UC_X_CS, UC_X_AT, UC_X_AS, UC_POST_COUNT, UC_SITE

Get keys at developer.x.com -> Project -> Keys and tokens.
Free tier can post (~500/month on the basic free tier, subject to change).

State: posted_x.json keeps sent slugs so nothing repeats.
"""
import os, json, hmac, hashlib, base64, secrets, time, urllib.parse, urllib.request, sys, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
_CANDS = [os.environ.get("UC_DATA", ""),
          os.path.join(HERE, "..", "data", "use_cases.json"),
          os.path.join(HERE, "data", "use_cases.json"),
          os.path.expanduser("~/agentusecases/use_cases.json")]
DATA = next((p for p in _CANDS if p and os.path.exists(p)), _CANDS[-1])
STATE = os.path.join(HERE, "posted_x.json")
SOCIAL = os.path.join(HERE, "social.json")
URL = "https://api.x.com/2/tweets"

def cfg():
    c = {}
    if os.path.exists(SOCIAL):
        try: c = json.load(open(SOCIAL))
        except Exception: c = {}
    g = lambda k, d="": os.environ.get(k) or c.get(d, "")
    return {
        "ck": g("UC_X_CK", "x_consumer_key"), "cs": g("UC_X_CS", "x_consumer_secret"),
        "at": g("UC_X_AT", "x_access_token"), "as": g("UC_X_AS", "x_access_secret"),
        "count": int(os.environ.get("UC_POST_COUNT") or c.get("count", 3)),
        "site": (os.environ.get("UC_SITE") or c.get("site", "")).rstrip("/"),
        "tags": c.get("hashtags", "#AI #AIAgents"),
    }

def _enc(s):
    return urllib.parse.quote(str(s), safe="")

def oauth_header(method, url, c):
    p = {
        "oauth_consumer_key": c["ck"],
        "oauth_nonce": secrets.token_hex(16),
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp": str(int(time.time())),
        "oauth_token": c["at"],
        "oauth_version": "1.0",
    }
    base = "&".join([method.upper(), _enc(url),
                     _enc("&".join(f"{_enc(k)}={_enc(p[k])}" for k in sorted(p)))])
    key = f"{_enc(c['cs'])}&{_enc(c['as'])}"
    p["oauth_signature"] = base64.b64encode(
        hmac.new(key.encode(), base.encode(), hashlib.sha1).digest()).decode()
    return "OAuth " + ", ".join(f'{_enc(k)}="{_enc(p[k])}"' for k in sorted(p))

def x_len(text):
    """X counts every URL as 23 chars regardless of real length."""
    import re as _re
    n = len(_re.sub(r"https?://\S+", "", text))
    return n + 23 * len(_re.findall(r"https?://\S+", text))

def compose(r, site):
    """Budget so X's weighted length (links = 23) stays under 280."""
    url = f"{site}/use-case/{r['slug']}/"
    head = r["title"].strip()
    body = (r.get("summary") or "").strip()
    agent = (r.get("try_agent") or r.get("agent") or "AI").strip()
    tail = f"\n\nvia {agent}"
    budget = 280 - 23 - 1          # link + newline
    head_budget = max(40, budget - len(tail))
    txt = head if len(head) <= head_budget else head[:head_budget].rsplit(" ", 1)[0].rstrip()
    if body:
        room = head_budget - len(txt) - 2
        if room > 60:
            if len(body) <= room:
                b = body
            else:
                b = body[: room - 3].rsplit(" ", 1)[0].rstrip() + "..."
            txt += "\n\n" + b
    return txt.rstrip() + tail + "\n" + url

def post(text, c):
    body = json.dumps({"text": text}).encode()
    req = urllib.request.Request(URL, data=body, method="POST")
    req.add_header("Authorization", oauth_header("POST", URL, c))
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())

def main():
    c = cfg()
    if not all([c["ck"], c["cs"], c["at"], c["as"]]):
        print("no X keys in social.json (or UC_X_* env) - nothing posted")
        return 0
    rows = json.load(open(DATA))
    state = json.load(open(STATE)) if os.path.exists(STATE) else {"posted": [], "offset": 0}
    seen = set(state.get("posted", []))
    fresh = [r for r in rows if r.get("slug") and r["slug"] not in seen]
    if not fresh:
        print("nothing new to post")
        return 0
    off = int(state.get("offset", 0)) % max(1, len(fresh) - c["count"] + 1) if len(fresh) > c["count"] else 0
    batch = fresh[off:off + c["count"]] or fresh[:c["count"]]
    sent = failed = 0
    for r in batch:
        try:
            res = post(compose(r, c["site"]), c)
            if res.get("data", {}).get("id"):
                seen.add(r["slug"]); sent += 1
            else:
                failed += 1; print("x error:", str(res)[:200])
        except Exception as ex:
            failed += 1
            print("x exception:", str(ex)[:200])
            break  # usually rate limit / auth - stop the batch
    state["posted"] = sorted(seen); state["offset"] = off + c["count"]
    state["last_run"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    json.dump(state, open(STATE, "w"), indent=2)
    print(f"x: sent {sent}, failed {failed}, queue {len(fresh) - sent}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
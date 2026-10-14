#!/usr/bin/env python3
"""Post new use cases to a Telegram channel (traffic engine, no API cost).

Config: ~/ucdir/social.json
  {"tg_token": "123:ABC", "tg_chat": "@yourchannel", "count": 3, "site": "https://..."}
Env overrides: UC_TG_TOKEN, UC_TG_CHAT, UC_POST_COUNT, UC_SITE

State: posted.json keeps every slug already sent, so nothing repeats.
"""
import os, json, html, urllib.request, urllib.parse, datetime, sys

HERE = os.path.dirname(os.path.abspath(__file__))
_CANDS = [os.environ.get("UC_DATA", ""),
          os.path.join(HERE, "..", "data", "use_cases.json"),
          os.path.join(HERE, "data", "use_cases.json"),
          os.path.expanduser("~/agentusecases/use_cases.json")]
DATA = next((p for p in _CANDS if p and os.path.exists(p)), _CANDS[-1])
STATE = os.path.join(HERE, "posted.json")
SOCIAL = os.path.join(HERE, "social.json")

def cfg():
    c = {}
    if os.path.exists(SOCIAL):
        try: c = json.load(open(SOCIAL))
        except Exception: c = {}
    return {
        "token": os.environ.get("UC_TG_TOKEN") or c.get("tg_token", ""),
        "chat":  os.environ.get("UC_TG_CHAT")  or c.get("tg_chat", ""),
        "count": int(os.environ.get("UC_POST_COUNT") or c.get("count", 3)),
        "site":  (os.environ.get("UC_SITE") or c.get("site", "")).rstrip("/"),
        "hashtags": c.get("hashtags", "#AI #AIAgents #Automation"),
    }

def e(s):
    return html.escape(str(s or ""), quote=False)

def agent_of(r):
    return (r.get("try_agent") or r.get("agent") or "an AI agent").strip()

def compose(r, site):
    """Build the Telegram message for one use case."""
    url = f"{site}/use-case/{r['slug']}/"
    prompt = (r.get("try_prompt") or "").strip()
    if len(prompt) > 320:
        prompt = prompt[:317].rsplit(" ", 1)[0] + "..."
    lines = [f"<b>{e(r['title'])}</b>", ""]
    if r.get("summary"):
        lines += [e(r["summary"]), ""]
    lines.append(f"<i>Done with</i> <b>{e(agent_of(r))}</b>")
    if prompt:
        lines += ["", "<blockquote>" + e(prompt) + "</blockquote>"]
    lines += ["", f'<a href="{url}">Read it + copy the prompt</a>']
    return "\n".join(lines)

def send(token, chat, text):
    api = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": chat, "text": text,
        "parse_mode": "HTML", "disable_web_page_preview": "false",
    }).encode()
    req = urllib.request.Request(api, data=data)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())

def main():
    c = cfg()
    if not c["token"] or not c["chat"]:
        print("no tg_token/tg_chat in social.json (or UC_TG_TOKEN/UC_TG_CHAT env) - nothing sent")
        return 0
    rows = json.load(open(DATA))
    state = json.load(open(STATE)) if os.path.exists(STATE) else {"posted": []}
    seen = set(state.get("posted", []))
    fresh = [r for r in rows if r.get("slug") and r["slug"] not in seen]
    if not fresh:
        print("nothing new to post")
        return 0
    # rotate the starting point so we do not always post the same alphabet block
    off = int(state.get("offset", 0)) % max(1, len(fresh) - c["count"] + 1) if len(fresh) > c["count"] else 0
    batch = fresh[off:off + c["count"]] or fresh[:c["count"]]
    sent, failed = 0, 0
    for r in batch:
        try:
            res = send(c["token"], c["chat"], compose(r, c["site"]))
            if res.get("ok"):
                seen.add(r["slug"]); sent += 1
            else:
                failed += 1; print("tg error:", res.get("description"))
        except Exception as ex:
            failed += 1; print("tg exception:", ex)
    state["posted"] = sorted(seen)
    state["offset"] = off + c["count"]
    state["last_run"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    json.dump(state, open(STATE, "w"), indent=2)
    print(f"telegram: sent {sent}, failed {failed}, queue {len(fresh) - sent}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
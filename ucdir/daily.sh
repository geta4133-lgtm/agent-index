#!/usr/bin/env bash
# Daily traffic engine: post N use cases to Telegram channel
# Butuh: ucdir/social.json terisi (tg_token + tg_chat)
set -e
cd "$(dirname "$0")"
LOG="/root/.hermes/cron/output/telegram_post.log"
mkdir -p "$(dirname "$LOG")"

if [ ! -f social.json ]; then
  echo "$(date -u '+%F %T') social.json missing" >> "$LOG"; exit 0
fi

TOKEN=$(python3 -c "import json;print(json.load(open('social.json')).get('tg_token',''))")
CHAT=$(python3 -c "import json;print(json.load(open('social.json')).get('tg_chat',''))")

if [ -z "$TOKEN" ] || [ "$TOKEN" = "ISI_TOKEN_BOT_DARI_BOTFATHER" ] || [ -z "$CHAT" ]; then
  echo "$(date -u '+%F %T') token/chat belum diisi, skip" >> "$LOG"; exit 0
fi

echo "$(date -u '+%F %T') posting..." >> "$LOG"
python3 post_telegram.py >> "$LOG" 2>&1
tail -200 "$LOG" > "$LOG.tmp" && mv "$LOG.tmp" "$LOG"

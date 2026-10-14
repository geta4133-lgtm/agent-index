#!/usr/bin/env bash
# Deploy ~/ucdir/public to a static host.
# Usage: ./deploy.sh cloudflare | netlify | surge | ghpages | preview
set -euo pipefail
cd "$(dirname "$0")"
DIR="$PWD/public"
MODE="${1:-preview}"

[ -d "$DIR" ] || { echo "No build found. Run: python3 pages4.py"; exit 1; }
echo "Deploying $DIR ($(du -sh "$DIR" | cut -f1), $(find "$DIR" -name '*.html' | wc -l) pages)"

case "$MODE" in
  cloudflare)
    # Needs: npx wrangler login   (or CLOUDFLARE_API_TOKEN env)
    npx --yes wrangler pages deploy "$DIR" --project-name=agentindex --commit-dirty=true
    ;;
  netlify)
    # Needs: npx netlify-cli login   (or NETLIFY_AUTH_TOKEN env)
    npx --yes netlify-cli deploy --dir="$DIR" --prod
    ;;
  surge)
    # Needs: npm i -g surge ; surge login
    npx --yes surge "$DIR" agentindex.surge.sh
    ;;
  ghpages)
    # Needs: git remote + a valid PAT (GH_TOKEN)
    [ -n "${GH_TOKEN:-}" ] || { echo "Set GH_TOKEN first"; exit 1; }
    REPO="${REPO:-agentindex}"
    rm -rf .ghpages && mkdir .ghpages && cp -r "$DIR"/* .ghpages/
    touch .ghpages/.nojekyll
    cd .ghpages
    git init -q && git add -A && git commit -qm "deploy"
    git branch -M gh-pages
    git remote add origin "https://x-access-token:${GH_TOKEN}@github.com/${GH_USER:-user}/${REPO}.git"
    git push -f origin gh-pages
    cd .. && rm -rf .ghpages
    ;;
  preview)
    echo "Local:  http://127.0.0.1:8777"
    echo "Public: cloudflared tunnel --url http://127.0.0.1:8777 --no-autoupdate"
    (cd "$DIR" && python3 -m http.server 8777 --bind 127.0.0.1)
    ;;
  *)
    echo "Unknown mode: $MODE"; exit 1;;
esac
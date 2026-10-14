# agent-index

A static directory of real AI agent use cases, each with a copy-ready prompt.
Built with a Python static site generator, deployed to GitHub Pages.

Downloads: 1,267 use cases, 28 agents, 11 categories, ~1,325 pages.

## Local build

```bash
python3 ucdir/pages4.py     # -> ucdir/public
python3 ucdir/audit.py      # 0 broken links expected
```

## Refresh content

```bash
python3 refresh.py                       # sync new entries + rebuild
python3 refresh.py --hn                  # also pull Hacker News candidates
```

## Deploy

Push to `main`. GitHub Actions rebuilds and publishes to Pages.
Enable Pages once: Settings -> Pages -> Source: GitHub Actions.

## Branding

Edit the `CFG` dict at the top of `ucdir/gen.py` (brand, domain, tagline,
sponsor block, price, newsletter endpoint), then rebuild.

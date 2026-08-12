# Telebot AI — landing page

GitHub Pages site for the Telebot AI macOS app: product info + DMG download.

**Live:** https://qingbo93.github.io/telebot-ai-landing/

## Stack

Vanilla HTML/CSS/JS, zero build step. Deploys automatically via GitHub Actions
(`.github/workflows/pages.yml`) on every push to `main`.

- Design language: Apple-clean (mlxserve.com school) + dark mode toggle
- Fonts: system SF stack + JetBrains Mono (Google Fonts)
- No frameworks, no tracking, no external assets except Google Fonts
- The app's code repo is **private** — this site must never link to it;
  everything public lives in this repo only

## Publishing a new release

1. Build the DMG in the app repo: `./scripts/build_dmg.sh` → `dist/Telebot-AI-<version>.dmg`
2. Copy the DMG here: `cp <app-repo>/dist/Telebot-AI-<version>.dmg downloads/` and commit
   (GitHub Pages serves it at `downloads/Telebot-AI-<version>.dmg` — the canonical
   download path; release assets 404 on this GitHub account, so don't rely on them)
3. Update version / size / SHA-256 in `index.html`:
   - `#download-btn` href → `downloads/Telebot-AI-<version>.dmg`
   - `#meta-version`, `#meta-size`, and `#meta-checksum[data-sha]`

## Custom domain (whenever)

To hook up your own domain later: add a `CNAME` file containing the domain and
set the custom domain in the repo's Pages settings. Until then the site stays
pure GitHub Pages at `qingbo93.github.io/telebot-ai-landing/`.

## Local preview

```bash
python3 -m http.server 8000   # then open http://localhost:8000
```

## Files

| Path | Purpose |
|---|---|
| `index.html` | Single-page site (hero, bento features, steps, privacy, FAQ, download) |
| `style.css` | Design tokens + all styles, light & dark themes |
| `app.js` | Theme toggle, scroll reveals, nav state, checksum copy |
| `assets/` | App logo (`app-logo.png`, from the app's AppIcon source) + favicon |
| `downloads/` | DMG artifacts served to users |
| `.github/workflows/pages.yml` | Actions deploy to GitHub Pages |

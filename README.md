# Telebot AI — landing page

GitHub Pages site for [Telebot AI](https://github.com/qingbo93/Telebot-AI): product
info + DMG download for the macOS app.

**Live:** https://qingbo93.github.io/telebot-ai-landing/

## Stack

Vanilla HTML/CSS/JS, zero build step. Deploys automatically via GitHub Actions
(`.github/workflows/pages.yml`) on every push to `main`.

- Design language: Apple-clean (mlxserve.com school) + dark mode toggle
- Fonts: system SF stack + JetBrains Mono (Google Fonts)
- No frameworks, no tracking, no external assets except Google Fonts

## Publishing a new release

1. Build the DMG in the app repo: `./scripts/build_dmg.sh` → `dist/Telebot-AI-<version>.dmg`
2. Create the GitHub release and upload the asset:
   `gh release create v<version> "dist/Telebot-AI-<version>.dmg" --title "Telebot AI <version>" --notes "…"`
   (the download button points at `releases/latest`, so it picks up automatically)
3. Update version / size / SHA-256 in `index.html`:
   - `#download-btn` href → `…/releases/latest/download/Telebot-AI-<version>.dmg`
   - `#meta-version`, `#meta-size`, and `#meta-checksum[data-sha]`

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
| `.github/workflows/pages.yml` | Actions deploy to GitHub Pages |

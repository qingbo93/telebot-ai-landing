# Telebot AI — landing page

GitHub Pages site for the Telebot AI macOS app: product info + DMG download.

**Live:** https://qingbo93.github.io/telebot-ai-landing/ · https://telebot.abeaverscart.ca/

## Stack

Multi-language static site, zero runtime dependencies, built by `scripts/build.mjs`:

- **Source of truth:** `templates/` (HTML with `{{key}}` tokens) + `i18n/strings.json`
  (keyed catalog — same shape as the app's `app/Localizable/strings.json`).
- **Build:** `node scripts/build.mjs` renders one static site per language into
  `dist/` — English at the root (URLs unchanged), each language under `/zh/`,
  `/es/`, `/ja/`, `/de/`, … (per `i18n/langs.json`). A missing translation
  FAILS the build — a raw key can never ship.
- **Lint gate:** `node scripts/l10n_check.mjs` (run automatically by the build):
  duplicate keys, every key × every declared language, unique EN values,
  template coverage, no embedded tokens in values.
- **i18n machinery:** per-locale canonical + hreflang (incl. `x-default`) +
  `og:locale`, localized JSON-LD, no-JS language switcher (`<details>`),
  `window.I18N` injected per page for app.js runtime strings.
- Design language: Apple-clean (mlxserve.com school) + dark mode toggle
  (`data-theme` on `<html>`).
- Fonts: system SF stack + JetBrains Mono (Google Fonts).
- The app's code repo is **private** — this site must never link to it.

## Adding a language

1. Add the language to `i18n/langs.json` (code, native name, htmlLang, ogLocale).
2. Translate every key in `i18n/strings.json` for that language (see
   `l10n_check` — it lists exactly which keys are missing).
3. Add the code to the `languages` array in `i18n/strings.json` — only then
   does the build render it.
4. `node scripts/l10n_check.mjs && node scripts/build.mjs` — must pass.
5. Verify per language (rendering + OCR check; English regression must stay clean).

The 404 page is English-only by design (GitHub Pages / Cloudflare Pages serve
a single site-level 404 regardless of path).

## Publishing a new release

1. Build the DMG in the app repo: `./scripts/build_dmg.sh` → `dist/Telebot-AI-<version>.dmg`
2. Copy the DMG here: `cp <app-repo>/dist/Telebot-AI-<version>.dmg downloads/` and commit
   (GitHub Pages serves it at `downloads/Telebot-AI-<version>.dmg` — the canonical
   download path; release assets 404 on this GitHub account, so don't rely on them)
3. Update version / size / SHA-256 in `templates/index.html`:
   - `#download-btn` href → `downloads/Telebot-AI-<version>.dmg`
   - `#meta-size`, and `#meta-checksum[data-sha]`
4. Update `latest.json` (the app's update-check contract — keep it byte-stable;
   the build copies it verbatim). `notes_<lang>` per language.
5. Add a changelog entry in `templates/changelog/index.html` + `i18n/strings.json`.

## Cloudflare Pages mirror

The site also runs on Cloudflare Pages at **https://telebot.abeaverscart.ca** (project
`telebot-ai-landing`, account abeaverscart@gmail.com). Deploy is manual via wrangler:

```bash
# from this repo: build first, then drop the DMGs (Cloudflare's 25 MiB/file cap)
node scripts/build.mjs
rm -rf dist/downloads
npx wrangler pages deploy dist --project-name=telebot-ai-landing --branch=main
```

The download button points at the GitHub Pages-hosted DMG (absolute URL), so it works
from both deployments. To get auto-deploys on push, connect this repo in the
Cloudflare dashboard (Workers & Pages → telebot-ai-landing → Settings → Builds).

## Feedback form

The Feedback section posts to a Cloudflare Worker (`worker/`, project `telebot-feedback`)
mounted at `telebot.abeaverscart.ca/api/feedback` (same-origin, CORS open so the GitHub
mirror works too). The worker forwards submissions to Telegram via the Bot API.

- Secrets: `wrangler secret put BOT_TOKEN` (bot token) and `CHAT_ID` (owner chat id —
  message the bot once, read it from `getUpdates`)
- Deploy worker: `cd worker && npx wrangler deploy`
- Anti-spam: honeypot field + 3 msgs/min/IP rate limit in the worker
- If the form ever fails, check the worker with a test POST (validation errors
  respond without secrets; a full delivery needs both secrets set)

## SEO

Everything is set up for indexing; the canonical host is **https://telebot.abeaverscart.ca/**:

- Per-locale `canonical`, hreflang alternates (`x-default` → English root),
  Open Graph + Twitter cards, `apple-touch-icon`
- JSON-LD: `SoftwareApplication` (free, macOS 13+, Apple Silicon), `WebSite`,
  `Organization`, `FAQPage` (9 Q&As — kept consistent with the visible page),
  `BreadcrumbList`, `TechArticle`, `WebPage` — localized per language
- `sitemap.xml` (generated: every page × language with hreflang alternates)
  + `robots.txt` (Cloudflare injects its own AI-bot rules on top)
- Progressive enhancement: all content is visible without JS (`.reveal` hides
  only under `.js`)
- **IndexNow** key for Bing/Yandex/Naver/Seznam lives at `<key>.txt` in the repo
  root (copied by the build); regenerate + re-POST to
  `https://api.indexnow.org/indexnow` whenever the page changes materially
- Google: submit in Search Console (domain property → DNS TXT, or URL-prefix property)

## Local preview

```bash
node scripts/build.mjs
python3 -m http.server 8000 --directory dist   # then open http://localhost:8000
```

## Files

| Path | Purpose |
|---|---|
| `templates/` | HTML sources with `{{key}}` tokens (one per page) |
| `i18n/strings.json` | Translation catalog — source of truth (same shape as the app's) |
| `i18n/langs.json` | Language metadata (code, native name, htmlLang, ogLocale) |
| `scripts/build.mjs` | Zero-dep renderer → `dist/` (lint-gated, fail-on-missing-key) |
| `scripts/l10n_check.mjs` | Catalog lint (mirrors the app's `l10n_check.py`) |
| `style.css` | Design tokens + all styles, light & dark themes |
| `app.js` | Theme toggle, scroll reveals, nav state, checksum copy, feedback form |
| `assets/` | App logo (`app-logo.png`, from the app's AppIcon source) + favicon |
| `downloads/` | DMG artifacts served to users (GH Pages only; CF has a 25 MiB cap) |
| `latest.json` | App update-check manifest — copied verbatim, never tokenized |
| `.github/workflows/pages.yml` | Actions: lint + build + deploy `dist/` to GitHub Pages |

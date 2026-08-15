#!/usr/bin/env node
/**
 * build.mjs — render the multi-language static site.
 *
 * Reads templates/ + i18n/strings.json + i18n/langs.json, writes dist/:
 *   - English at the root (existing URLs unchanged), each other language
 *     under /<code>/ — per-locale canonical, hreflang alternates, og:locale,
 *     localized JSON-LD, language switcher, injected window.I18N for app.js.
 *   - Copies assets/, downloads/, latest.json, robots.txt, _headers,
 *     _redirects, the IndexNow key file, and generates sitemap.xml.
 *   - FAILS on any missing key or leftover token — a raw key never ships.
 *
 * Run `node scripts/l10n_check.mjs` first (build does it too).
 */
import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const SITE = 'https://telebot.abeaverscart.ca';
// I18N_CATALOG lets CI/tests point at an alternate catalog (e.g. a stub language)
const CATALOG_PATH = process.env.I18N_CATALOG || path.join(ROOT, 'i18n', 'strings.json');
const OUT = process.env.I18N_OUT || path.join(ROOT, 'dist');
const TOKEN_RE = /{{\s*(?:json:)?([a-z0-9_.]+)\s*}}/g;
const JSTOKEN_RE = /{{\s*json:([a-z0-9_.]+)\s*}}/g;

// app.js runtime strings — injected per page as window.I18N
const JS_KEYS = ['fb.err_short', 'fb.sending', 'fb.ok', 'fb.err_server', 'fb.err_network', 'footer.feedback', 'dl.copied'];

// page registry: template path → { path: URL path under locale root, depth }
const PAGES = [
  { tpl: 'index.html', path: '', depth: 0 },
  { tpl: 'guides/index.html', path: 'guides/', depth: 1 },
  { tpl: 'guides/run-local-ai-models-on-mac/index.html', path: 'guides/run-local-ai-models-on-mac/', depth: 2 },
  { tpl: 'docs/index.html', path: 'docs/', depth: 1 },
  { tpl: 'changelog/index.html', path: 'changelog/', depth: 1 },
];

// sitemap metadata (lastmod/changefreq/priority from the committed sitemap.xml)
const SITEMAP = {
  '': { lastmod: '2026-08-13', freq: 'monthly', pri: '1.0' },
  'changelog/': { lastmod: '2026-08-13', freq: 'monthly', pri: '0.6' },
  'guides/': { lastmod: '2026-08-13', freq: 'monthly', pri: '0.6' },
  'docs/': { lastmod: '2026-08-13', freq: 'monthly', pri: '0.8' },
  'guides/run-local-ai-models-on-mac/': { lastmod: '2026-08-13', freq: 'monthly', pri: '0.8' },
};

// files copied verbatim into dist/ (machine contracts + infra stay untouched)
const COPY_FILES = ['latest.json', 'robots.txt', '_headers', '_redirects', 'e5ac2fe2c8c162e377e03cec22ad41fa.txt'];
const COPY_DIRS = ['assets', 'downloads'];

function die(msg) { console.error(`build: ✗ ${msg}`); process.exit(1); }

// 0. lint gate
try { execFileSync(process.execPath, [path.join(ROOT, 'scripts', 'l10n_check.mjs')], { stdio: 'inherit', env: { ...process.env, I18N_CATALOG: CATALOG_PATH } }); }
catch { process.exit(1); }

const langs = JSON.parse(fs.readFileSync(path.join(ROOT, 'i18n', 'langs.json'), 'utf8')).languages;
const catalog = JSON.parse(fs.readFileSync(CATALOG_PATH, 'utf8'));
const LANGS = catalog.languages; // languages that actually ship
const table = catalog.strings;
const langOf = (code) => langs.find((l) => l.code === code);
const canonical = (lang, pagePath) => `${SITE}/${lang === 'en' ? '' : lang + '/'}${pagePath}`;

function render(tplPath, lang) {
  const meta = PAGES.find((p) => p.tpl === tplPath) || { path: '', depth: 0 }; // 404.html: en-only, root paths
  const pagePath = meta.path;
  const depth = meta.depth;
  const localeDepth = lang === 'en' ? 0 : 1;
  const base = '../'.repeat(depth + localeDepth);
  const L = langOf(lang);

  let html = fs.readFileSync(path.join(ROOT, 'templates', tplPath), 'utf8');

  // per-locale head bits
  const hreflang = LANGS.map((l) =>
    `  <link rel="alternate" hreflang="${l}" href="${canonical(l, pagePath)}">`).join('\n') +
    `\n  <link rel="alternate" hreflang="x-default" href="${canonical('en', pagePath)}">`;
  const switcherUp = '../'.repeat(depth + localeDepth);
  const langSwitcher =
    `<details class="lang-switcher">\n` +
    `  <summary aria-label="${esc(table['nav.language'][lang] || table['nav.language'].en)}" title="${esc(table['nav.language'][lang] || table['nav.language'].en)}">🌐</summary>\n` +
    `  <div class="lang-menu">\n` +
    LANGS.map((l) => {
      const href = (switcherUp + (l === 'en' ? '' : l + '/') + pagePath) || './';
      const name = langOf(l).nativeName;
      const current = l === lang ? ' aria-current="true"' : '';
      return `    <a href="${href}" hreflang="${l}"${current}>${name}</a>`;
    }).join('\n') + '\n  </div>\n</details>';
  const jsI18n =
    `<script>window.I18N = ${JSON.stringify(Object.fromEntries(JS_KEYS.map((k) => [k, table[k][lang] || table[k].en])))};</script>`;

  const inject = {
    canonical: canonical(lang, pagePath),
    rootcanonical: canonical(lang, ''),
    hreflang,
    oglocale: L.ogLocale,
    htmllang: L.htmlLang,
    langswitcher: langSwitcher,
    'js-i18n': jsI18n,
  };
  for (const [tok, val] of Object.entries(inject)) {
    html = html.split(`{{${tok}}}`).join(val);
  }

  // catalog substitution (values may embed {{base}} — loop until stable)
  const hasRealTokens = () => [...html.matchAll(TOKEN_RE)].some((m) => m[1] !== 'base');
  let pass = 0;
  while (hasRealTokens() && pass++ < 10) {
    html = html.replace(JSTOKEN_RE, (_, k) => {
      const v = table[k]?.[lang] || table[k]?.en;
      if (v === undefined) die(`missing key ${k} for ${lang}`);
      // JSON-LD gets clean text: decode the entities that belong in rendered text
      return JSON.stringify(v.replace(/&amp;/g, '&').replace(/&nbsp;/g, ' ').replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"'));
    });
    html = html.replace(/{{\s*([a-z0-9_.]+)\s*}}/g, (_, k) => {
      if (k === 'base') return '{{base}}'; // resolved in the final pass
      const v = table[k]?.[lang] || table[k]?.en;
      if (v === undefined) die(`missing key ${k} for ${lang}`);
      return v;
    });
  }
  html = html.split('{{base}}').join(base);

  const leftover = [...html.matchAll(TOKEN_RE)].map((m) => m[0]);
  if (leftover.length) die(`unresolved tokens in ${tplPath} (${lang}): ${[...new Set(leftover)].join(', ')}`);
  return html;
}

function esc(s) { return s.replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;'); }

// 1. render pages
fs.rmSync(OUT, { recursive: true, force: true });
for (const lang of LANGS) {
  const langRoot = lang === 'en' ? OUT : path.join(OUT, lang);
  for (const p of PAGES) {
    const outPath = path.join(langRoot, p.tpl);
    fs.mkdirSync(path.dirname(outPath), { recursive: true });
    fs.writeFileSync(outPath, render(p.tpl, lang));
    console.log(`  dist/${lang === 'en' ? '' : lang + '/'}${p.tpl}`);
  }
}

// 2. 404 (English-only by design — the platform serves one site-level 404)
{
  const html = render('404.html', 'en');
  fs.writeFileSync(path.join(OUT, '404.html'), html);
  console.log('  dist/404.html');
}

// 3. verbatim copies (downloads/ excluded from the CF deploy via README flow)
for (const f of COPY_FILES) {
  const src = path.join(ROOT, f);
  if (fs.existsSync(src)) fs.copyFileSync(src, path.join(OUT, f));
}
for (const d of COPY_DIRS) {
  fs.cpSync(path.join(ROOT, d), path.join(OUT, d), { recursive: true });
}

// 4. sitemap: one <url> per (page × language), each carrying ALL hreflang alternates
const urlBlocks = [];
for (const [pagePath, m] of Object.entries(SITEMAP)) {
  const alternates = LANGS.map((l) =>
    `    <xhtml:link rel="alternate" hreflang="${l}" href="${canonical(l, pagePath)}"/>`).join('\n');
  for (const lang of LANGS) {
    urlBlocks.push(
      `  <url>\n` +
      `    <loc>${canonical(lang, pagePath)}</loc>\n` +
      alternates + '\n' +
      `    <lastmod>${m.lastmod}</lastmod>\n` +
      `    <changefreq>${m.freq}</changefreq>\n` +
      `    <priority>${m.pri}</priority>\n` +
      `  </url>`
    );
  }
}
const sitemap =
  `<?xml version="1.0" encoding="UTF-8"?>\n` +
  `<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n` +
  urlBlocks.join('\n') + '\n</urlset>\n';
fs.writeFileSync(path.join(OUT, 'sitemap.xml'), sitemap);
console.log(`  dist/sitemap.xml (${Object.keys(SITEMAP).length * LANGS.length} URLs)`);

console.log(`build: OK — ${LANGS.length} language(s) → dist/`);

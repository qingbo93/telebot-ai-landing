#!/usr/bin/env node
/**
 * l10n_check.mjs — validate the site translation catalog (run before every build).
 *
 * Mirrors the app's scripts/l10n_check.py contract:
 * 1. no duplicate keys in strings.json
 * 2. every key has `en` + every language declared in the catalog's `languages` array
 * 3. `en` values are unique across the catalog (identical text = one key)
 * 4. every {{key}} / {{json:key}} token used in templates/ exists in the catalog
 * 5. every catalog key is used somewhere in templates/ (no orphans)
 * 6. catalog values may only embed {{base}} — never other catalog tokens
 * Exit 1 on any violation.
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const CATALOG = process.env.I18N_CATALOG || path.join(ROOT, 'i18n', 'strings.json');
const TEMPLATES = process.env.I18N_TEMPLATES || path.join(ROOT, 'templates');
const TOKEN_RE = /{{\s*(?:json:)?([a-z0-9_.]+)\s*}}/g;

// tokens injected by scripts/build.mjs — valid in templates, not catalog keys
const BUILTIN = new Set(['base', 'canonical', 'rootcanonical', 'hreflang', 'htmllang', 'langswitcher', 'oglocale', 'js-i18n']);
// keys consumed by app.js / build.mjs at runtime — never in templates
const JS_KEYS = new Set(['fb.err_short', 'fb.sending', 'fb.ok', 'fb.err_server', 'fb.err_network', 'footer.feedback', 'dl.copied', 'nav.language']);

const errors = [];
const raw = fs.readFileSync(CATALOG, 'utf8');
const data = JSON.parse(raw);
const table = data.strings || {};
const LANGS = data.languages || ['en'];

// 1. duplicate keys (JSON.parse keeps the last — scan raw text)
const keyCounts = {};
for (const m of raw.matchAll(/"((?:[a-z0-9_]+\.)+[a-z0-9_]+)"\s*:\s*\{/g)) {
  keyCounts[m[1]] = (keyCounts[m[1]] || 0) + 1;
}
for (const [k, c] of Object.entries(keyCounts)) {
  if (c > 1) errors.push(`duplicate key in strings.json: ${k}`);
}

// 2. coverage: every key has en + every declared language
for (const [k, v] of Object.entries(table)) {
  if (!v || typeof v !== 'object') { errors.push(`${k}: value is not a language map`); continue; }
  if (!v.en) errors.push(`${k}: missing en`);
  for (const lang of LANGS) {
    if (lang !== 'en' && !v[lang]) errors.push(`${k}: missing ${lang}`);
  }
}

// 3. unique en values
const ens = {};
for (const [k, v] of Object.entries(table)) {
  if (!v.en) continue;
  (ens[v.en] ||= []).push(k);
}
for (const [en, ks] of Object.entries(ens)) {
  if (ks.length > 1) errors.push(`duplicate EN value ${JSON.stringify(en)}: ${ks.join(', ')}`);
}

// 4+5. template coverage (both directions)
const used = new Set();
const walk = (dir) => {
  for (const ent of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, ent.name);
    if (ent.isDirectory()) walk(p);
    else if (ent.name.endsWith('.html')) {
      const src = fs.readFileSync(p, 'utf8');
      for (const m of src.matchAll(TOKEN_RE)) used.add(m[1]);
    }
  }
};
walk(TEMPLATES);
for (const k of [...used].sort()) {
  if (!(k in table) && !BUILTIN.has(k)) errors.push(`token used in template but missing from catalog: ${k}`);
}
for (const k of Object.keys(table).sort()) {
  if (!used.has(k) && !JS_KEYS.has(k)) errors.push(`catalog key never used in any template: ${k}`);
}

// 6. values may embed only {{base}}
for (const [k, v] of Object.entries(table)) {
  for (const lang of LANGS) {
    const val = v[lang];
    if (typeof val === 'string' && val.includes('{{')) {
      const bad = [...val.matchAll(/{{\s*(?:json:)?([a-z0-9_.]+)\s*}}/g)]
        .map((m) => m[1]).filter((name) => name !== 'base');
      if (bad.length) errors.push(`${k}.${lang}: value embeds catalog token(s): ${bad.join(', ')}`);
    }
  }
}

if (errors.length) {
  console.error(`l10n_check: ${errors.length} violation(s)`);
  for (const e of errors.slice(0, 60)) console.error(`  ✗ ${e}`);
  process.exit(1);
}
console.log(`l10n_check: OK — ${Object.keys(table).length} keys × [${LANGS.join(', ')}], all used, no dups`);

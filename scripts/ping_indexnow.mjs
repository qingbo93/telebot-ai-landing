#!/usr/bin/env node
// Notify IndexNow (Bing/Yandex/Seznam...) that the landing pages were
// updated. Run after every release push, once the pages are live.
// Usage: node scripts/ping_indexnow.mjs   (optional: SITE_BASE env override)
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const here = dirname(fileURLToPath(import.meta.url));
const j = JSON.parse(readFileSync(join(here, "..", "i18n", "strings.json"), "utf8"));
const LANGS = (Array.isArray(j.languages) ? j.languages : Object.keys(j.languages))
  .map((l) => (typeof l === "string" ? l : l.code));

const BASE = process.env.SITE_BASE || "https://qingbojiang.com/telebot-ai-landing";
const KEY = "e5ac2fe2c8c162e377e03cec22ad41fa"; // must match /<key>.txt at site root

// IndexNow caps 10,000 URLs per POST; we are far below that.
const urls = [
  BASE + "/",
  BASE + "/changelog/",
  ...LANGS.flatMap((l) => [
    `${BASE}/${l}/`,
    `${BASE}/${l}/changelog/`,
  ]),
];

const res = await fetch("https://api.indexnow.org/indexnow", {
  method: "POST",
  headers: { "Content-Type": "application/json; charset=utf-8" },
  // The key file lives under /telebot-ai-landing/, not the host root, so
  // we must pass keyLocation explicitly — IndexNow verifies it there.
  body: JSON.stringify({
    host: "qingbojiang.com",
    key: KEY,
    keyLocation: `${BASE}/e5ac2fe2c8c162e377e03cec22ad41fa.txt`,
    urlList: urls,
  }),
});
console.log(`IndexNow: HTTP ${res.status} for ${urls.length} URLs`);
if (!res.ok) {
  console.log(await res.text());
  process.exit(1);
}

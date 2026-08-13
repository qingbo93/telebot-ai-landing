/**
 * Telebot AI — feedback worker.
 * Receives POST /api/feedback and forwards the message to the developer's
 * Telegram via the Bot API. Secrets: BOT_TOKEN, CHAT_ID (wrangler secret put).
 */
const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type",
  "Access-Control-Max-Age": "86400",
};

const json = (data, status = 200) =>
  new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json", ...CORS },
  });

// per-isolate rate limiter (3 messages / min / IP) — plenty for a landing page
const hits = new Map();

const esc = (s) =>
  s.replace(/([_*[\]()~`>#+\-=|{}.!\\])/g, "\\$1");

export default {
  async fetch(request, env) {
    if (request.method === "OPTIONS") return new Response("ok", { headers: CORS });
    if (request.method !== "POST") return json({ ok: false, error: "Method not allowed" }, 405);

    const ip = request.headers.get("CF-Connecting-IP") || "unknown";
    const now = Date.now();
    const recent = (hits.get(ip) || []).filter((t) => now - t < 60_000);
    if (recent.length >= 3) return json({ ok: false, error: "Too many messages — try again in a minute." }, 429);
    recent.push(now);
    hits.set(ip, recent);

    let body;
    try {
      body = await request.json();
    } catch {
      return json({ ok: false, error: "Invalid request." }, 400);
    }

    // honeypot: bots fill this hidden field — pretend success, drop silently
    if (body.honey) return json({ ok: true });

    const message = String(body.message || "").trim();
    if (message.length < 5 || message.length > 4000)
      return json({ ok: false, error: "Message must be between 5 and 4000 characters." }, 400);

    const name = String(body.name || "").trim().slice(0, 80);
    const email = String(body.email || "").trim().slice(0, 120);

    const text =
      `📩 New website feedback\n\n` +
      `${message}\n\n` +
      `— ${name ? esc(name) : "anonymous"}${email ? ` (${esc(email)})` : ""}\n` +
      `ip: ${ip} · ${new Date().toISOString().slice(0, 16)}`;

    const tg = await fetch(`https://api.telegram.org/bot${env.BOT_TOKEN}/sendMessage`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        chat_id: env.CHAT_ID,
        text,
        parse_mode: "Markdown",
        disable_web_page_preview: true,
      }),
    });

    if (!tg.ok) return json({ ok: false, error: "Delivery failed — please try again." }, 502);
    return json({ ok: true });
  },
};

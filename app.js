/* Telebot AI landing — interactions */
(function () {
  'use strict';

  /* localized runtime strings — injected per page by scripts/build.mjs;
     English fallbacks keep this file working standalone */
  const I18N = window.I18N || {};
  const t = (k, fb) => (I18N[k] !== undefined && I18N[k] !== '') ? I18N[k] : fb;

  /* mark JS availability — CSS hides .reveal content only when JS is on */
  document.documentElement.classList.add('js');

  /* ── theme ─────────────────────────────────────────────────── */
  const root = document.documentElement;
  const toggle = document.getElementById('theme-toggle');
  const stored = (() => { try { return localStorage.getItem('theme'); } catch (e) { return null; } })();
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  const initial = stored || (prefersDark ? 'dark' : 'light');
  root.setAttribute('data-theme', initial);

  toggle.addEventListener('click', () => {
    const next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    root.setAttribute('data-theme', next);
    try { localStorage.setItem('theme', next); } catch (e) { /* private mode */ }
    const meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.setAttribute('content', next === 'dark' ? '#000000' : '#f5f5f7');
  });

  /* ── nav scrolled state ────────────────────────────────────── */
  const nav = document.getElementById('nav');
  const onScroll = () => nav.classList.toggle('scrolled', window.scrollY > 8);
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });

  /* ── scroll reveal ─────────────────────────────────────────── */
  const reveals = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((e) => {
        if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -36px 0px' });
    reveals.forEach((el) => io.observe(el));
  } else {
    reveals.forEach((el) => el.classList.add('in'));
  }

  /* ── checksum copy ─────────────────────────────────────────── */
  const checksumLink = document.getElementById('meta-checksum');
  if (checksumLink && checksumLink.getAttribute('data-sha')) {
    checksumLink.addEventListener('click', (e) => {
      e.preventDefault();
      navigator.clipboard.writeText(checksumLink.getAttribute('data-sha')).then(() => {
        const orig = checksumLink.textContent;
        checksumLink.textContent = t('dl.copied', 'copied ✓');
        setTimeout(() => { checksumLink.textContent = orig; }, 1600);
      }).catch(() => {});
    });
  }

  /* ── feedback form ─────────────────────────────────────────── */
  const form = document.getElementById('feedback-form');
  if (form) {
    const status = document.getElementById('f-status');
    const submit = document.getElementById('f-submit');
    const ENDPOINT = 'https://telebot.abeaverscart.ca/api/feedback';
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const message = document.getElementById('f-message').value.trim();
      if (message.length < 5) {
        status.textContent = t('fb.err_short', 'Please write at least a sentence.');
        status.className = 'f-status err';
        return;
      }
      status.textContent = '';
      submit.disabled = true;
      submit.textContent = t('fb.sending', 'Sending…');
      fetch(ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: document.getElementById('f-name').value.trim(),
          email: document.getElementById('f-email').value.trim(),
          message,
          honey: document.getElementById('f-honey').value,
        }),
      })
        .then((r) => r.json().catch(() => ({ ok: false })).then((d) => ({ r, d })))
        .then(({ r, d }) => {
          if (r.ok && d.ok) {
            status.textContent = t('fb.ok', 'Thanks — your message is on its way ✓');
            status.className = 'f-status ok';
            form.reset();
          } else {
            status.textContent = (d && d.error) || t('fb.err_server', 'Something went wrong — please try again.');
            status.className = 'f-status err';
          }
        })
        .catch(() => {
          status.textContent = t('fb.err_network', 'Network error — please try again.');
          status.className = 'f-status err';
        })
        .finally(() => {
          submit.disabled = false;
          submit.textContent = t('footer.feedback', 'Send feedback');
        });
    });
  }

  /* ── footer year ───────────────────────────────────────────── */
  const year = document.getElementById('year');
  if (year) year.textContent = String(new Date().getFullYear());
})();

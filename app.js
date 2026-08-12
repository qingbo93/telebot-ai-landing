/* Telebot AI landing — interactions */
(function () {
  'use strict';

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
        checksumLink.textContent = 'copied ✓';
        setTimeout(() => { checksumLink.textContent = orig; }, 1600);
      }).catch(() => {});
    });
  }

  /* ── footer year ───────────────────────────────────────────── */
  const year = document.getElementById('year');
  if (year) year.textContent = String(new Date().getFullYear());
})();

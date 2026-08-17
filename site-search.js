/*!
 * Silver Current Press — Site Search Widget
 * A self-contained fixed top-right search button for static HTML sites.
 * Requires only: <script src="/site-search.js" defer></script>
 * and a sibling /search-index.json file at site root.
 * (c) James F. Mulhern / Silver Current Press
 */
(function () {
  'use strict';

  if (window.__siteSearchLoaded) return;
  window.__siteSearchLoaded = true;

  // ---------- Resolve script directory so we can find the JSON index ----------
  var currentScript = document.currentScript;
  var scriptURL = currentScript ? currentScript.src : '';
  var indexURL = new URL('search-index.json', scriptURL || window.location.href).toString();

  // ---------- Inject scoped CSS ----------
  var css = ''
    + '.scp-search-btn{'
    +   'position:fixed;top:14px;right:14px;z-index:2147483000;'
    +   'width:42px;height:42px;border-radius:50%;border:1px solid rgba(0,0,0,0.12);'
    +   'background:#ffffff;color:#4a1d1d;cursor:pointer;'
    +   'box-shadow:0 2px 10px rgba(0,0,0,0.12);'
    +   'display:flex;align-items:center;justify-content:center;'
    +   'font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;'
    +   'transition:transform .15s ease, box-shadow .15s ease, background .15s ease;'
    + '}'
    + '.scp-search-btn:hover{transform:translateY(-1px);box-shadow:0 4px 14px rgba(0,0,0,0.16);background:#fbf6ef;}'
    + '.scp-search-btn:focus-visible{outline:2px solid #b7803f;outline-offset:2px;}'
    + '.scp-search-btn svg{width:19px;height:19px;}'
    + '@media (prefers-color-scheme: dark){'
    +   '.scp-search-btn{background:#1a1a1a;color:#e8d9b8;border-color:rgba(255,255,255,0.15);}'
    +   '.scp-search-btn:hover{background:#262626;}'
    + '}'
    + '[data-theme="dark"] .scp-search-btn{background:#1a1a1a;color:#e8d9b8;border-color:rgba(255,255,255,0.15);}'
    + '[data-theme="dark"] .scp-search-btn:hover{background:#262626;}'
    + '.scp-search-overlay{'
    +   'position:fixed;inset:0;z-index:2147483001;'
    +   'background:rgba(20,15,10,0.55);backdrop-filter:blur(4px);'
    +   'display:none;align-items:flex-start;justify-content:center;'
    +   'padding:8vh 20px 20px;'
    +   'font-family:Georgia,"Iowan Old Style","Palatino Linotype",serif;'
    + '}'
    + '.scp-search-overlay.open{display:flex;}'
    + '.scp-search-modal{'
    +   'width:100%;max-width:640px;background:#fdfaf3;color:#2a2118;'
    +   'border-radius:8px;box-shadow:0 20px 60px rgba(0,0,0,0.35);'
    +   'display:flex;flex-direction:column;max-height:80vh;overflow:hidden;'
    + '}'
    + '@media (prefers-color-scheme: dark){.scp-search-modal{background:#1e1a15;color:#ece0c8;}}'
    + '[data-theme="dark"] .scp-search-modal{background:#1e1a15;color:#ece0c8;}'
    + '.scp-search-field{'
    +   'display:flex;align-items:center;gap:12px;'
    +   'padding:16px 20px;border-bottom:1px solid rgba(0,0,0,0.08);'
    + '}'
    + '[data-theme="dark"] .scp-search-field{border-bottom-color:rgba(255,255,255,0.1);}'
    + '.scp-search-field svg{width:20px;height:20px;flex:0 0 auto;color:#8a6a3d;}'
    + '.scp-search-input{'
    +   'flex:1;border:0;background:transparent;outline:none;'
    +   'font:inherit;font-size:17px;color:inherit;padding:6px 0;'
    + '}'
    + '.scp-search-close{'
    +   'background:transparent;border:0;color:inherit;opacity:.6;cursor:pointer;'
    +   'padding:4px;border-radius:4px;line-height:0;'
    + '}'
    + '.scp-search-close:hover{opacity:1;background:rgba(0,0,0,0.05);}'
    + '.scp-search-close svg{width:16px;height:16px;}'
    + '.scp-search-results{overflow-y:auto;padding:6px 0;}'
    + '.scp-search-hint,.scp-search-empty,.scp-search-loading{'
    +   'padding:16px 20px;margin:0;color:#6b5a3d;font-size:14px;font-style:italic;'
    + '}'
    + '[data-theme="dark"] .scp-search-hint,'
    + '[data-theme="dark"] .scp-search-empty,'
    + '[data-theme="dark"] .scp-search-loading{color:#b8a785;}'
    + '.scp-search-result{'
    +   'display:block;padding:12px 20px;text-decoration:none;color:inherit;'
    +   'border-bottom:1px solid rgba(0,0,0,0.05);'
    + '}'
    + '[data-theme="dark"] .scp-search-result{border-bottom-color:rgba(255,255,255,0.06);}'
    + '.scp-search-result:hover,.scp-search-result.active{background:rgba(183,128,63,0.10);}'
    + '.scp-search-result-title{font-weight:600;font-size:15px;color:#4a1d1d;margin-bottom:2px;}'
    + '[data-theme="dark"] .scp-search-result-title{color:#e8b876;}'
    + '.scp-search-result-snippet{font-size:13px;color:#5a4a35;line-height:1.5;}'
    + '[data-theme="dark"] .scp-search-result-snippet{color:#b8a785;}'
    + '.scp-search-result-type{'
    +   'display:inline-block;font-size:10px;text-transform:uppercase;letter-spacing:.08em;'
    +   'padding:2px 6px;border-radius:3px;margin-right:6px;'
    +   'background:rgba(183,128,63,0.18);color:#8a6a3d;font-weight:600;'
    + '}'
    + '.scp-search-result mark{background:rgba(255,213,79,0.5);color:inherit;padding:0 2px;border-radius:2px;}'
    + '@media (max-width:520px){'
    +   '.scp-search-btn{top:10px;right:10px;width:38px;height:38px;}'
    +   '.scp-search-overlay{padding:5vh 12px 12px;}'
    + '}';

  var styleEl = document.createElement('style');
  styleEl.setAttribute('data-scp-search', '');
  styleEl.textContent = css;
  (document.head || document.documentElement).appendChild(styleEl);

  // ---------- Create trigger button ----------
  function init() {
    if (document.querySelector('.scp-search-btn')) return;
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'scp-search-btn';
    btn.setAttribute('aria-label', 'Search this site (press /)');
    btn.title = 'Search this site (press /)';
    btn.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M21 21 L16.65 16.65"/></svg>';
    btn.addEventListener('click', openSearch);
    document.body.appendChild(btn);
  }

  // ---------- Search state ----------
  var overlay, input, resultsBox;
  var indexData = null;
  var indexPromise = null;
  var activeIndex = -1;
  var currentResults = [];

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function escapeRegExp(s) {
    return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }
  function highlight(text, terms) {
    if (!terms.length) return escapeHtml(text);
    var escaped = escapeHtml(text);
    var pattern = new RegExp('(' + terms.map(escapeRegExp).join('|') + ')', 'ig');
    return escaped.replace(pattern, '<mark>$1</mark>');
  }
  function snippetFor(text, terms) {
    if (!text) return '';
    if (!terms.length) return text.slice(0, 180);
    var lower = text.toLowerCase();
    var bestIdx = -1;
    for (var i = 0; i < terms.length; i++) {
      var idx = lower.indexOf(terms[i]);
      if (idx !== -1 && (bestIdx === -1 || idx < bestIdx)) bestIdx = idx;
    }
    if (bestIdx === -1) return text.slice(0, 180);
    var start = Math.max(0, bestIdx - 70);
    var end = Math.min(text.length, bestIdx + 160);
    var s = text.slice(start, end);
    if (start > 0) s = '…' + s;
    if (end < text.length) s = s + '…';
    return s;
  }

  function loadIndex() {
    if (indexPromise) return indexPromise;
    if (resultsBox) resultsBox.innerHTML = '<p class="scp-search-loading">Loading search index…</p>';
    indexPromise = fetch(indexURL, { cache: 'default' })
      .then(function (r) {
        if (!r.ok) throw new Error('index fetch failed: ' + r.status);
        return r.json();
      })
      .then(function (data) { indexData = data; return data; })
      .catch(function (err) {
        if (resultsBox) resultsBox.innerHTML = '<p class="scp-search-empty">Search is temporarily unavailable.</p>';
        throw err;
      });
    return indexPromise;
  }

  function scorePage(page, terms) {
    var titleLower = (page.title || '').toLowerCase();
    var descLower = (page.description || '').toLowerCase();
    var textLower = (page.text || '').toLowerCase();
    var typeBoost = page.type === 'pdf' ? 0.9 : 1.0;
    var score = 0;
    for (var i = 0; i < terms.length; i++) {
      var t = terms[i];
      if (!t) continue;
      if (titleLower.indexOf(t) !== -1) score += 12;
      if (descLower.indexOf(t) !== -1) score += 5;
      var occ = 0, from = 0, hit;
      while ((hit = textLower.indexOf(t, from)) !== -1 && occ < 20) { occ++; from = hit + t.length; }
      score += Math.min(occ, 12) * 1.5;
    }
    return score * typeBoost;
  }

  function typeLabel(page) {
    if (page.type === 'pdf') return 'PDF';
    return '';
  }

  function renderResults(results, terms) {
    if (!results.length) {
      resultsBox.innerHTML = '<p class="scp-search-empty">No matches. Try a different word or phrase.</p>';
      currentResults = []; activeIndex = -1; return;
    }
    currentResults = results;
    activeIndex = -1;
    resultsBox.innerHTML = results.map(function (r) {
      var p = r.page;
      var snippet = snippetFor(p.text || p.description || '', terms);
      var tl = typeLabel(p);
      var badge = tl ? '<span class="scp-search-result-type">' + tl + '</span>' : '';
      return '<a class="scp-search-result" href="' + escapeHtml(p.url) + '"' + (p.type === 'pdf' ? ' target="_blank" rel="noopener"' : '') + '>'
        + '<div class="scp-search-result-title">' + badge + highlight(p.title || p.url, terms) + '</div>'
        + '<div class="scp-search-result-snippet">' + highlight(snippet, terms) + '</div>'
        + '</a>';
    }).join('');
  }

  function runSearch(q) {
    q = (q || '').trim();
    if (!q) {
      resultsBox.innerHTML = '<p class="scp-search-hint">Start typing to search this site — pages, guides, and PDFs.</p>';
      currentResults = []; activeIndex = -1;
      return;
    }
    loadIndex().then(function (data) {
      var terms = q.toLowerCase().split(/\s+/).filter(Boolean);
      var scored = data.map(function (page) { return { page: page, score: scorePage(page, terms) }; })
        .filter(function (r) { return r.score > 0; })
        .sort(function (a, b) { return b.score - a.score; })
        .slice(0, 30);
      renderResults(scored, terms);
    }).catch(function () {});
  }

  function updateActive() {
    var links = resultsBox.querySelectorAll('.scp-search-result');
    links.forEach(function (el, i) { el.classList.toggle('active', i === activeIndex); });
    if (links[activeIndex]) links[activeIndex].scrollIntoView({ block: 'nearest' });
  }

  function onKeyDown(e) {
    if (e.key === 'Escape') { closeSearch(); return; }
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      if (!currentResults.length) return;
      activeIndex = Math.min(activeIndex + 1, currentResults.length - 1);
      updateActive();
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      if (!currentResults.length) return;
      activeIndex = Math.max(activeIndex - 1, 0);
      updateActive();
    } else if (e.key === 'Enter') {
      var links = resultsBox.querySelectorAll('.scp-search-result');
      var target = links[activeIndex >= 0 ? activeIndex : 0];
      if (target) {
        var href = target.getAttribute('href');
        var isPdf = target.getAttribute('target') === '_blank';
        if (isPdf) window.open(href, '_blank', 'noopener');
        else window.location.href = href;
      }
    }
  }

  function buildOverlay() {
    overlay = document.createElement('div');
    overlay.className = 'scp-search-overlay';
    overlay.setAttribute('role', 'dialog');
    overlay.setAttribute('aria-modal', 'true');
    overlay.setAttribute('aria-label', 'Search this site');
    overlay.innerHTML = ''
      + '<div class="scp-search-modal">'
      +   '<div class="scp-search-field">'
      +     '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M21 21 L16.65 16.65"/></svg>'
      +     '<input type="text" class="scp-search-input" placeholder="Search this site…" autocomplete="off" spellcheck="false" aria-label="Search">'
      +     '<button type="button" class="scp-search-close" aria-label="Close search">'
      +       '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" aria-hidden="true"><path d="M5 5 L19 19 M19 5 L5 19"/></svg>'
      +     '</button>'
      +   '</div>'
      +   '<div class="scp-search-results"><p class="scp-search-hint">Start typing to search this site — pages, guides, and PDFs.</p></div>'
      + '</div>';
    document.body.appendChild(overlay);
    input = overlay.querySelector('.scp-search-input');
    resultsBox = overlay.querySelector('.scp-search-results');
    var closeBtn = overlay.querySelector('.scp-search-close');
    overlay.addEventListener('click', function (e) { if (e.target === overlay) closeSearch(); });
    closeBtn.addEventListener('click', closeSearch);
    input.addEventListener('input', function () { runSearch(input.value); });
    input.addEventListener('keydown', onKeyDown);
  }

  function openSearch() {
    if (!overlay) buildOverlay();
    overlay.classList.add('open');
    document.body.style.overflow = 'hidden';
    loadIndex().catch(function () {});
    setTimeout(function () { input.focus(); input.select(); }, 30);
  }

  function closeSearch() {
    if (!overlay) return;
    overlay.classList.remove('open');
    document.body.style.overflow = '';
  }

  // Global shortcut: "/" or Cmd/Ctrl+K
  document.addEventListener('keydown', function (e) {
    var tag = (e.target && e.target.tagName) || '';
    var typing = tag === 'INPUT' || tag === 'TEXTAREA' || (e.target && e.target.isContentEditable);
    if ((e.key === 'k' || e.key === 'K') && (e.metaKey || e.ctrlKey)) {
      e.preventDefault(); openSearch();
    } else if (e.key === '/' && !typing && !overlay) {
      e.preventDefault(); openSearch();
    } else if (e.key === '/' && !typing && overlay && !overlay.classList.contains('open')) {
      e.preventDefault(); openSearch();
    }
  });

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();

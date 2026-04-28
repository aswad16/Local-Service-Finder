/* ============================================================
   main.js — Local Service Finder
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {

  // ── Messages auto-dismiss ──────────────────────────────────
  const messages = document.querySelectorAll('.message');
  messages.forEach(msg => {
    setTimeout(() => {
      msg.style.transition = 'opacity 0.5s, max-height 0.5s';
      msg.style.opacity = '0';
      msg.style.maxHeight = '0';
      msg.style.padding = '0';
      msg.style.margin = '0';
      setTimeout(() => msg.remove(), 500);
    }, 4500);
  });

  // ── Star rating UI ─────────────────────────────────────────
  const ratingSelect = document.querySelector('select[name="rating"]');
  const starDisplay = document.getElementById('star-display');

  if (starDisplay && ratingSelect) {
    const renderStars = (val) => {
      starDisplay.innerHTML = '';
      for (let i = 1; i <= 5; i++) {
        const s = document.createElement('span');
        s.textContent = i <= val ? '★' : '☆';
        s.style.color = i <= val ? 'var(--gold)' : 'var(--text-muted)';
        s.style.fontSize = '1.6rem';
        s.style.cursor = 'pointer';
        s.style.transition = 'color 0.15s';
        s.addEventListener('click', () => {
          ratingSelect.value = i;
          renderStars(i);
        });
        s.addEventListener('mouseenter', () => renderStars(i));
        starDisplay.appendChild(s);
      }
      starDisplay.addEventListener('mouseleave', () => renderStars(ratingSelect.value || 0));
    };
    renderStars(ratingSelect.value || 0);
  }

  // ── Navbar scroll shadow ───────────────────────────────────
  const navbar = document.querySelector('.navbar');
  if (navbar) {
    window.addEventListener('scroll', () => {
      navbar.style.boxShadow = window.scrollY > 10
        ? '0 2px 24px rgba(0,0,0,0.4)'
        : 'none';
    }, { passive: true });
  }

  // ── Animate numbers (KPI cards) ────────────────────────────
  const animateCount = (el, target, duration = 1200) => {
    const start = performance.now();
    const update = (now) => {
      const elapsed = now - start;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      el.textContent = Math.round(eased * target).toLocaleString();
      if (progress < 1) requestAnimationFrame(update);
    };
    requestAnimationFrame(update);
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const el = entry.target;
        const raw = el.dataset.count;
        if (raw) { animateCount(el, parseInt(raw)); observer.unobserve(el); }
      }
    });
  }, { threshold: 0.5 });

  document.querySelectorAll('[data-count]').forEach(el => observer.observe(el));

  // ── Search bar enhancements ────────────────────────────────
  const searchInput = document.querySelector('.search-bar input[name="q"]');
  if (searchInput) {
    // Live suggestions (simple debounce)
    let debounceTimer;
    searchInput.addEventListener('input', () => {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => {
        const q = searchInput.value.trim();
        if (q.length > 2) fetchSuggestions(q);
      }, 300);
    });
  }

  async function fetchSuggestions(q) {
    try {
      const res = await fetch(`/api/search/?q=${encodeURIComponent(q)}&format=json`);
      if (!res.ok) return;
      const data = await res.json();
      // Suggestions dropdown — simplified inline
      let dropdown = document.getElementById('search-suggestions');
      if (!dropdown) {
        dropdown = document.createElement('div');
        dropdown.id = 'search-suggestions';
        dropdown.style.cssText = `
          position:absolute;background:var(--bg-card);border:1px solid var(--border);
          border-radius:var(--radius-md);z-index:999;width:100%;top:calc(100% + 4px);
          box-shadow:var(--shadow-card);overflow:hidden;
        `;
        const wrapper = document.querySelector('.search-bar');
        if (wrapper) { wrapper.style.position = 'relative'; wrapper.appendChild(dropdown); }
      }
      dropdown.innerHTML = '';
      if (data.results && data.results.length) {
        data.results.slice(0, 5).forEach(svc => {
          const item = document.createElement('a');
          item.href = `/services/${svc.slug}/`;
          item.style.cssText = `display:flex;padding:10px 16px;gap:10px;align-items:center;color:var(--text-secondary);font-size:0.875rem;border-bottom:1px solid var(--border);transition:background 0.15s;`;
          item.innerHTML = `<span style="font-size:1.2rem">${svc.category?.icon || '🔧'}</span><div><div style="color:var(--text-primary);font-weight:500">${svc.title}</div><div style="font-size:0.75rem;color:var(--text-muted)">${svc.city}</div></div>`;
          item.addEventListener('mouseover', () => item.style.background = 'var(--bg-hover)');
          item.addEventListener('mouseleave', () => item.style.background = 'transparent');
          dropdown.appendChild(item);
        });
      } else {
        dropdown.innerHTML = `<div style="padding:12px 16px;color:var(--text-muted);font-size:0.85rem">No results for "${q}"</div>`;
      }

      document.addEventListener('click', (e) => {
        if (!dropdown.contains(e.target) && e.target !== searchInput) dropdown.innerHTML = '';
      }, { once: true });
    } catch (_) {}
  }

  // ── Tab switching ──────────────────────────────────────────
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const group = btn.closest('[data-tabs]') || btn.parentElement;
      group.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const target = btn.dataset.tab;
      if (target) {
        document.querySelectorAll('[data-tab-content]').forEach(c => {
          c.style.display = c.dataset.tabContent === target ? 'block' : 'none';
        });
      }
    });
  });

  // ── Scroll-reveal cards ────────────────────────────────────
  const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
        revealObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll('.card, .kpi-card, .cat-card').forEach((el, i) => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(16px)';
    el.style.transition = `opacity 0.5s ${i * 0.06}s ease, transform 0.5s ${i * 0.06}s ease`;
    revealObserver.observe(el);
  });

  // ── Image lazy-load fallback ───────────────────────────────
  document.querySelectorAll('img[data-src]').forEach(img => {
    const io = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) {
        img.src = img.dataset.src;
        io.disconnect();
      }
    });
    io.observe(img);
  });

  // ── Mobile nav toggle ──────────────────────────────────────
  const mobileToggle = document.getElementById('mobile-nav-toggle');
  const navMenu = document.querySelector('.navbar__nav');
  if (mobileToggle && navMenu) {
    mobileToggle.addEventListener('click', () => {
      navMenu.style.display = navMenu.style.display === 'flex' ? 'none' : 'flex';
    });
  }

});

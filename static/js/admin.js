/* ============================================================
   admin.js — Admin Panel JavaScript
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {

  // ── Sidebar mobile toggle ──────────────────────────────────
  const sidebarToggle = document.getElementById('sidebar-toggle');
  const sidebar = document.querySelector('.admin-sidebar');
  const overlay = document.getElementById('sidebar-overlay');

  if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener('click', () => {
      sidebar.classList.toggle('open');
      if (overlay) overlay.classList.toggle('active');
    });
  }
  if (overlay) {
    overlay.addEventListener('click', () => {
      sidebar?.classList.remove('open');
      overlay.classList.remove('active');
    });
  }

  // ── Active sidebar link ────────────────────────────────────
  const currentPath = window.location.pathname;
  document.querySelectorAll('.sidebar-link').forEach(link => {
    if (link.getAttribute('href') === currentPath ||
        (link.getAttribute('href') !== '/adminpanel/' && currentPath.startsWith(link.getAttribute('href')))) {
      link.classList.add('active');
    }
  });

  // ── Animate KPI numbers ────────────────────────────────────
  const animateCount = (el, target, duration = 1000) => {
    const start = performance.now();
    const update = (now) => {
      const progress = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      el.textContent = Math.round(eased * target).toLocaleString();
      if (progress < 1) requestAnimationFrame(update);
    };
    requestAnimationFrame(update);
  };

  document.querySelectorAll('.admin-kpi__value[data-count]').forEach(el => {
    const target = parseInt(el.dataset.count);
    if (!isNaN(target)) animateCount(el, target);
  });

  // ── Animate bar charts ─────────────────────────────────────
  const bars = document.querySelectorAll('.chart-bar-fill[data-width]');
  setTimeout(() => {
    bars.forEach(bar => {
      bar.style.width = bar.dataset.width + '%';
    });
  }, 200);

  // ── Confirm delete modals ──────────────────────────────────
  document.querySelectorAll('[data-confirm]').forEach(el => {
    el.addEventListener('click', (e) => {
      const msg = el.dataset.confirm || 'Are you sure? This action cannot be undone.';
      if (!confirm(msg)) e.preventDefault();
    });
  });

  // ── Delete modal (custom) ──────────────────────────────────
  const deleteModal = document.getElementById('delete-modal');
  if (deleteModal) {
    let deleteForm = null;
    document.querySelectorAll('[data-modal-delete]').forEach(btn => {
      btn.addEventListener('click', () => {
        deleteForm = document.getElementById(btn.dataset.modalDelete);
        const name = btn.dataset.name || 'this item';
        const msg = deleteModal.querySelector('#modal-item-name');
        if (msg) msg.textContent = name;
        deleteModal.classList.add('open');
      });
    });
    document.getElementById('modal-confirm-delete')?.addEventListener('click', () => {
      if (deleteForm) deleteForm.submit();
    });
    document.querySelectorAll('[data-modal-close]').forEach(btn => {
      btn.addEventListener('click', () => deleteModal.classList.remove('open'));
    });
    deleteModal.addEventListener('click', (e) => {
      if (e.target === deleteModal) deleteModal.classList.remove('open');
    });
  }

  // ── Table search (client-side filter) ─────────────────────
  const tableSearch = document.getElementById('table-search');
  const tableBody = document.querySelector('.admin-table tbody');
  if (tableSearch && tableBody) {
    tableSearch.addEventListener('input', () => {
      const q = tableSearch.value.toLowerCase();
      tableBody.querySelectorAll('tr').forEach(row => {
        row.style.display = row.textContent.toLowerCase().includes(q) ? '' : 'none';
      });
    });
  }

  // ── Toast notifications ────────────────────────────────────
  window.showToast = (msg, type = 'info') => {
    const colors = {
      success: '#10b981', error: '#ef4444', info: '#3b82f6', warning: '#f59e0b'
    };
    const toast = document.createElement('div');
    toast.style.cssText = `
      position:fixed;bottom:24px;right:24px;z-index:9999;
      background:var(--bg-card);border:1px solid ${colors[type]};
      color:var(--text-primary);padding:14px 20px;border-radius:12px;
      font-size:0.875rem;box-shadow:0 8px 32px rgba(0,0,0,0.4);
      transform:translateY(10px);opacity:0;
      transition:all 0.25s ease;max-width:320px;
    `;
    toast.textContent = msg;
    document.body.appendChild(toast);
    requestAnimationFrame(() => {
      toast.style.transform = 'translateY(0)';
      toast.style.opacity = '1';
    });
    setTimeout(() => {
      toast.style.transform = 'translateY(10px)';
      toast.style.opacity = '0';
      setTimeout(() => toast.remove(), 250);
    }, 3500);
  };

  // Show toasts from session messages
  document.querySelectorAll('.message').forEach(msg => {
    const type = msg.classList.contains('message--success') ? 'success'
      : msg.classList.contains('message--error') ? 'error'
      : msg.classList.contains('message--warning') ? 'warning' : 'info';
    showToast(msg.textContent.trim(), type);
    msg.remove();
  });

  // ── Sortable table headers ─────────────────────────────────
  document.querySelectorAll('.admin-table th[data-sort]').forEach(th => {
    th.style.cursor = 'pointer';
    th.style.userSelect = 'none';
    th.addEventListener('click', () => {
      const col = th.dataset.sort;
      const url = new URL(window.location.href);
      const current = url.searchParams.get('sort');
      url.searchParams.set('sort', current === col ? `-${col}` : col);
      window.location.href = url.toString();
    });
  });

  // ── Auto-refresh dashboard stats ───────────────────────────
  if (document.querySelector('.admin-kpi-grid') && !document.hidden) {
    setInterval(async () => {
      try {
        const res = await fetch('/adminpanel/?format=json', { headers: { 'X-Requested-With': 'XMLHttpRequest' } });
        // Refresh handled by server; minimal client polling
      } catch {}
    }, 60000);
  }

});

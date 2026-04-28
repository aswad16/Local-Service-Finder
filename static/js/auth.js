/* ============================================================
   auth.js — JWT token management & role selector
   ============================================================ */

const Auth = (() => {
  const TOKEN_KEY = 'ls_access';
  const REFRESH_KEY = 'ls_refresh';

  const save = (access, refresh) => {
    sessionStorage.setItem(TOKEN_KEY, access);
    if (refresh) sessionStorage.setItem(REFRESH_KEY, refresh);
  };

  const clear = () => {
    sessionStorage.removeItem(TOKEN_KEY);
    sessionStorage.removeItem(REFRESH_KEY);
  };

  const getAccess = () => sessionStorage.getItem(TOKEN_KEY);
  const getRefresh = () => sessionStorage.getItem(REFRESH_KEY);

  const isLoggedIn = () => !!getAccess();

  const decode = (token) => {
    try {
      return JSON.parse(atob(token.split('.')[1]));
    } catch { return null; }
  };

  const isExpired = (token) => {
    const payload = decode(token);
    if (!payload) return true;
    return payload.exp * 1000 < Date.now();
  };

  const refresh = async () => {
    const refreshToken = getRefresh();
    if (!refreshToken) return false;
    try {
      const res = await fetch('/api/users/token/refresh/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh: refreshToken })
      });
      if (res.ok) {
        const data = await res.json();
        save(data.access, data.refresh || refreshToken);
        return true;
      }
    } catch {}
    return false;
  };

  const authFetch = async (url, options = {}) => {
    let token = getAccess();
    if (token && isExpired(token)) {
      const ok = await refresh();
      if (!ok) { clear(); return null; }
      token = getAccess();
    }
    const headers = {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    };
    if (token) headers['Authorization'] = `Bearer ${token}`;
    return fetch(url, { ...options, headers });
  };

  const login = async (username, password) => {
    const res = await fetch('/api/users/login/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    if (res.ok) {
      const data = await res.json();
      save(data.access, data.refresh);
      return { success: true, user: decode(data.access) };
    }
    const err = await res.json().catch(() => ({}));
    return { success: false, error: err.detail || 'Login failed' };
  };

  const logout = () => {
    clear();
    window.location.href = '/users/logout/';
  };

  const getUser = () => {
    const token = getAccess();
    return token ? decode(token) : null;
  };

  return { save, clear, getAccess, getRefresh, isLoggedIn, login, logout, getUser, authFetch };
})();


// ── Role selector animation ──────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  const roleOptions = document.querySelectorAll('.role-option');
  roleOptions.forEach(radio => {
    radio.addEventListener('change', () => {
      // Visual pulse on selection
      const label = document.querySelector(`label[for="${radio.id}"]`);
      if (label) {
        label.animate([
          { transform: 'scale(1)' },
          { transform: 'scale(1.03)' },
          { transform: 'scale(1)' }
        ], { duration: 250, easing: 'ease-out' });
      }
    });
  });

  // ── Login form AJAX (optional enhancement) ─────────────────
  const loginForm = document.getElementById('login-form');
  if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
      const btn = loginForm.querySelector('[type="submit"]');
      if (btn) {
        btn.disabled = true;
        btn.textContent = 'Signing in…';
        btn.style.opacity = '0.7';
      }
      // Let the native form submit handle the Django session login
      // JWT tokens are stored alongside for API use
      const usernameEl = loginForm.querySelector('[name="username"]');
      const passwordEl = loginForm.querySelector('[name="password"]');
      if (usernameEl && passwordEl) {
        Auth.login(usernameEl.value, passwordEl.value).catch(() => {});
      }
    });
  }

  // ── Register form: role selection highlight ─────────────────
  const registerForm = document.getElementById('register-form');
  if (registerForm) {
    const updateRoleUI = () => {
      const checked = registerForm.querySelector('.role-option:checked');
      if (!checked) return;
      const allLabels = registerForm.querySelectorAll('.role-option + label');
      allLabels.forEach(l => l.style.opacity = '0.65');
      const activeLabel = registerForm.querySelector(`label[for="${checked.id}"]`);
      if (activeLabel) activeLabel.style.opacity = '1';
    };
    registerForm.querySelectorAll('.role-option').forEach(r => {
      r.addEventListener('change', updateRoleUI);
    });
    updateRoleUI();
  }

  // ── Password strength meter ─────────────────────────────────
  const passwordInput = document.querySelector('#id_password1, input[name="password1"]');
  const strengthBar = document.getElementById('password-strength');
  if (passwordInput && strengthBar) {
    passwordInput.addEventListener('input', () => {
      const val = passwordInput.value;
      let strength = 0;
      if (val.length >= 8) strength++;
      if (/[A-Z]/.test(val)) strength++;
      if (/[0-9]/.test(val)) strength++;
      if (/[^A-Za-z0-9]/.test(val)) strength++;
      const colors = ['#ef4444', '#f59e0b', '#3b82f6', '#10b981'];
      const labels = ['Weak', 'Fair', 'Good', 'Strong'];
      strengthBar.style.width = `${strength * 25}%`;
      strengthBar.style.background = colors[strength - 1] || '#ef4444';
      const label = document.getElementById('password-strength-label');
      if (label) label.textContent = labels[strength - 1] || '';
    });
  }
});

<template>
  <div id="app">

    <!-- ── Navigation ─────────────────────────────── -->
    <nav class="nav">
      <div class="nav__inner">

        <!-- Logo -->
        <router-link to="/" class="nav__logo">
          <span class="nav__logo-icon" aria-hidden="true">
            <svg width="22" height="22" viewBox="0 0 22 22" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="11" cy="11" r="10" stroke="currentColor" stroke-width="1.5"/>
              <path d="M11 4c0 3.5-4 5-4 8a4 4 0 0 0 8 0c0-3-4-4.5-4-8z" fill="currentColor" opacity=".25"/>
              <path d="M11 7c0 2.5-2.5 3.5-2.5 5.5a2.5 2.5 0 0 0 5 0C13.5 10.5 11 9.5 11 7z" fill="currentColor"/>
            </svg>
          </span>
          <span class="nav__logo-text">HeatAware <strong>Hub</strong></span>
        </router-link>

        <!-- Links -->
        <div class="nav__links">
          <router-link to="/" class="nav__link" exact-active-class="nav__link--active">
            Home
          </router-link>
          <router-link to="/upload" class="nav__link" active-class="nav__link--active">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
              <line x1="12" y1="12" x2="12" y2="18"/>
              <line x1="9" y1="15" x2="15" y2="15"/>
            </svg>
            Upload documents
          </router-link>
          <router-link to="/about" class="nav__link" active-class="nav__link--active">
            About
          </router-link>
        </div>

      </div>
    </nav>

    <!-- ── Page content ────────────────────────────── -->
    <main class="main">
      <router-view />
    </main>

    <!-- ── Footer ──────────────────────────────────── -->
    <footer class="footer">
      <div class="footer__inner">
        <span class="footer__flame" aria-hidden="true">
          <svg width="14" height="14" viewBox="0 0 22 22" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M11 2c0 4-5 6-5 10a5 5 0 0 0 10 0c0-4-5-5.5-5-10z" fill="currentColor" opacity=".35"/>
            <path d="M11 7c0 2.8-3 4-3 6.5a3 3 0 0 0 6 0C14 11 11 9.8 11 7z" fill="currentColor"/>
          </svg>
        </span>
        <span>© 2026 HeatAware Hub — Climate intelligence for FIFA World Cup 2026</span>
      </div>
    </footer>

  </div>
</template>

<script setup>
// App shell
</script>

<style scoped>
/* ── Reset ────────────────────────────────────────────── */
*,
*::before,
*::after { box-sizing: border-box; margin: 0; padding: 0; }

/* ── Root layout ──────────────────────────────────────── */
#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f4f0;
  font-family: system-ui, -apple-system, sans-serif;
  color: #1a1a1a;
}

/* ── Nav ──────────────────────────────────────────────── */
.nav {
  position: sticky;
  top: 0;
  z-index: 100;
  background: #fff;
  border-bottom: 0.5px solid rgba(0, 0, 0, 0.1);
}

.nav__inner {
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 1.5rem;
  height: 58px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 2rem;
}

/* Logo */
.nav__logo {
  display: flex;
  align-items: center;
  gap: 9px;
  text-decoration: none;
  color: #1a1a1a;
  flex-shrink: 0;
}

.nav__logo-icon {
  display: flex;
  align-items: center;
  color: #d85a30;
}

.nav__logo-text {
  font-size: 16px;
  font-weight: 400;
  letter-spacing: -0.01em;
  color: #1a1a1a;
}

.nav__logo-text strong {
  font-weight: 600;
}

/* Links */
.nav__links {
  display: flex;
  align-items: center;
  gap: 2px;
}

.nav__link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 400;
  color: #4b5563;
  text-decoration: none;
  transition: background 0.12s, color 0.12s;
  white-space: nowrap;
}

.nav__link:hover {
  background: #f3f4f6;
  color: #1a1a1a;
}

.nav__link--active {
  background: #fff4f0;
  color: #d85a30;
  font-weight: 500;
}

/* Mobile nav collapse */
@media (max-width: 540px) {
  .nav__logo-text { font-size: 15px; }

  .nav__link {
    padding: 6px 8px;
    font-size: 13px;
  }
}

/* ── Main ─────────────────────────────────────────────── */
.main {
  flex: 1;
  max-width: 1100px;
  width: 100%;
  margin: 0 auto;
  padding: 2rem 1.5rem;
}

/* ── Footer ───────────────────────────────────────────── */
.footer {
  border-top: 0.5px solid rgba(0, 0, 0, 0.1);
  background: #fff;
  margin-top: auto;
}

.footer__inner {
  max-width: 1100px;
  margin: 0 auto;
  padding: 1.25rem 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
  font-size: 13px;
  color: #9ca3af;
}

.footer__flame {
  display: flex;
  align-items: center;
  color: #d85a30;
  opacity: 0.7;
}
</style>
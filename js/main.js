/* ============================================================
   Mass-EXPERT — Main JavaScript
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {

  // --- Theme System (Dark + Accessibility) ---
  const html = document.documentElement;

  // Desktop + Mobile toggle buttons
  const themeBtns = [
    document.getElementById('themeToggle'),
    document.getElementById('themeToggleMobile')
  ].filter(Boolean);
  const accessibilityBtns = [
    document.getElementById('accessibilityToggle'),
    document.getElementById('accessibilityToggleMobile')
  ].filter(Boolean);

  function setThemeUI(theme) {
    const isDark = theme === 'dark';
    const isA11y = theme === 'accessibility';
    themeBtns.forEach(btn => {
      btn.innerHTML = isDark
        ? '<i class="fas fa-sun"></i>'
        : '<i class="fas fa-moon"></i>';
      btn.title = isDark ? 'Светлая тема' : 'Тёмная тема';
    });
    accessibilityBtns.forEach(btn => {
      btn.innerHTML = isA11y
        ? '<i class="fas fa-eye-slash"></i>'
        : '<i class="fas fa-eye"></i>';
      btn.title = isA11y ? 'Обычный режим' : 'Режим для слабовидящих';
    });
    localStorage.setItem('mass-expert-theme', theme || '');
  }

  function setTheme(theme) {
    html.classList.remove('theme-dark', 'theme-accessibility');
    if (theme === 'dark') html.classList.add('theme-dark');
    if (theme === 'accessibility') html.classList.add('theme-accessibility');
    setThemeUI(theme);
  }

  // Load saved theme
  const saved = localStorage.getItem('mass-expert-theme');
  if (saved) setTheme(saved);

  // Theme toggle click (both desktop and mobile)
  themeBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const isDark = html.classList.contains('theme-dark');
      html.classList.remove('theme-accessibility');
      setTheme(isDark ? '' : 'dark');
    });
  });

  // Accessibility toggle click (both desktop and mobile)
  accessibilityBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const isA11y = html.classList.contains('theme-accessibility');
      html.classList.remove('theme-dark', 'theme-accessibility');
      setTheme(isA11y ? '' : 'accessibility');
    });
  });

  // --- Mobile Nav Toggle ---
  const toggle = document.querySelector('.navbar-toggle');
  const navLinks = document.querySelector('.navbar-links');
  if (toggle) {
    toggle.addEventListener('click', () => {
      const isOpen = navLinks.classList.toggle('open');
      document.body.style.overflow = isOpen ? 'hidden' : '';
      document.documentElement.style.overflow = isOpen ? 'hidden' : '';
      document.body.style.position = isOpen ? 'fixed' : '';
      document.body.style.width = isOpen ? '100%' : '';
      document.body.style.top = isOpen ? '-0px' : '';
      if (isOpen) createOverlay();
      else removeOverlay();
    });
    navLinks.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', closeNav);
    });
    // Close on Escape
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && navLinks.classList.contains('open')) closeNav();
    });
    // Close on swipe left
    let touchStartX = 0, touchStartY = 0;
    navLinks.addEventListener('touchstart', (e) => {
      touchStartX = e.changedTouches[0].screenX;
      touchStartY = e.changedTouches[0].screenY;
    }, { passive: true });
    navLinks.addEventListener('touchend', (e) => {
      const dx = e.changedTouches[0].screenX - touchStartX;
      const dy = e.changedTouches[0].screenY - touchStartY;
      if (Math.abs(dx) > 80 && Math.abs(dy) < 100) closeNav();
    }, { passive: true });
  }

  function createOverlay() {
    if (document.getElementById('nav-overlay')) return;
    const overlay = document.createElement('div');
    overlay.id = 'nav-overlay';
    overlay.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,0.5);z-index:999;';
    overlay.addEventListener('click', closeNav);
    overlay.addEventListener('touchstart', closeNav, { passive: true });
    // Add close button in menu
    const closeBtn = document.createElement('button');
    closeBtn.innerHTML = '<i class="fas fa-times"></i>';
    closeBtn.setAttribute('aria-label', 'Закрыть меню');
    closeBtn.style.cssText = 'position:absolute;top:0.5rem;right:0.5rem;background:none;border:none;color:rgba(255,255,255,0.7);font-size:1.5rem;cursor:pointer;padding:0.5rem;z-index:1001;';
    closeBtn.addEventListener('click', closeNav);
    closeBtn.addEventListener('touchstart', closeNav, { passive: true });
    document.body.appendChild(overlay);
    document.body.appendChild(closeBtn);
  }
  function removeOverlay() {
    const overlay = document.getElementById('nav-overlay');
    const closeBtn = document.querySelector('button[aria-label="Закрыть меню"]');
    if (overlay) overlay.remove();
    if (closeBtn) closeBtn.remove();
  }
  function closeNav() {
    navLinks.classList.remove('open');
    document.body.style.overflow = '';
    document.documentElement.style.overflow = '';
    document.body.style.position = '';
    document.body.style.width = '';
    document.body.style.top = '';
    removeOverlay();
  }

  // --- Navbar scroll effect ---
  const navbar = document.querySelector('.navbar');
  window.addEventListener('scroll', () => {
    navbar.classList.toggle('scrolled', window.scrollY > 50);
  });

  // --- Active nav link based on scroll ---
  const sections = document.querySelectorAll('section[id]');
  const navAnchors = document.querySelectorAll('.navbar-links a');

  function updateActiveNav() {
    let currentId = '';
    sections.forEach(section => {
      const top = section.offsetTop - 150;
      const bottom = top + section.offsetHeight;
      if (window.scrollY >= top && window.scrollY < bottom) {
        currentId = section.getAttribute('id');
      }
    });
    navAnchors.forEach(a => {
      a.classList.toggle('active', a.getAttribute('href') === '#' + currentId);
    });
  }
  window.addEventListener('scroll', updateActiveNav);
  updateActiveNav();

  // --- Smooth scroll for anchor links ---
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      // Instant for navbar links, smooth for other page links (CTA buttons etc)
      const isNavLink = this.closest('.navbar-links') !== null;
      
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: isNavLink ? 'instant' : 'smooth', block: 'start' });
      }
    });
  });

  // --- Product Line Tabs ---
  const tabs = document.querySelectorAll('.product-tab');
  const panels = document.querySelectorAll('.product-panel');

  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      const target = tab.dataset.tab;
      tabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      panels.forEach(p => {
        p.classList.toggle('active', p.id === target);
      });
    });
  });

  // --- Scroll-reveal animations ---
  const animatedElements = document.querySelectorAll('.animate-on-scroll');

  const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -40px 0px'
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, observerOptions);

  animatedElements.forEach(el => observer.observe(el));

  // --- Copyright year ---
  const yearEl = document.getElementById('year');
  if (yearEl) yearEl.textContent = new Date().getFullYear();

});

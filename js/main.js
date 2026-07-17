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
    localStorage.setItem('mass-expert-theme', theme || 'light');
  }

  function setTheme(theme) {
    html.classList.remove('theme-dark', 'theme-accessibility');
    if (theme === 'dark') html.classList.add('theme-dark');
    if (theme === 'accessibility') html.classList.add('theme-accessibility');
    setThemeUI(theme);
  }

  // Load saved theme, or detect system preference
  const saved = localStorage.getItem('mass-expert-theme');
  if (saved === 'dark') {
    setTheme('dark');
  } else if (saved === 'accessibility') {
    setTheme('accessibility');
  } else if (saved === 'light') {
    setTheme('');
  } else if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
    setTheme('dark');
  }

  // Listen for system theme changes only when user never made a choice
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
    if (!localStorage.getItem('mass-expert-theme')) {
      setTheme(e.matches ? 'dark' : '');
    }
  });

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

  // --- Mobile Nav Toggle (full-screen overlay) ---
  const toggle = document.querySelector('.navbar-toggle');
  const navLinks = document.querySelector('.navbar-links');
  const toggleIcon = toggle ? toggle.querySelector('i') : null;
  if (toggle) {
    let scrollTop = 0;
    function closeNav() {
      navLinks.classList.remove('open');
      if (toggleIcon) toggleIcon.className = 'fas fa-bars';
      toggle.setAttribute('aria-label', 'Открыть меню');
      document.body.style.overflow = '';
      document.documentElement.style.overflow = '';
      document.body.style.position = '';
      document.body.style.width = '';
      document.body.style.top = '';
      window.scrollTo({ top: scrollTop, behavior: 'instant' });
    }
    toggle.addEventListener('click', () => {
      const isOpen = navLinks.classList.toggle('open');
      if (toggleIcon) toggleIcon.className = isOpen ? 'fas fa-times' : 'fas fa-bars';
      toggle.setAttribute('aria-label', isOpen ? 'Закрыть меню' : 'Открыть меню');
      if (isOpen) {
        scrollTop = window.scrollY;
        document.body.style.overflow = 'hidden';
        document.documentElement.style.overflow = 'hidden';
        document.body.style.position = 'fixed';
        document.body.style.width = '100%';
        document.body.style.top = '-' + scrollTop + 'px';
      } else {
        closeNav();
      }
    });
    // Close on link click
    navLinks.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', closeNav);
    });
    // Close on Escape
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && navLinks.classList.contains('open')) closeNav();
    });
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
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'instant', block: 'start' });
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

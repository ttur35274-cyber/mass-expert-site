/* ============================================================
   Mass-EXPERT — Main JavaScript
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {

  // --- Theme System (Dark + Accessibility) ---
  const html = document.documentElement;
  const themeToggle = document.getElementById('themeToggle');
  const accessibilityToggle = document.getElementById('accessibilityToggle');

  function setTheme(theme) {
    // Remove both theme classes
    html.classList.remove('theme-dark', 'theme-accessibility');
    if (theme === 'dark') html.classList.add('theme-dark');
    if (theme === 'accessibility') html.classList.add('theme-accessibility');
    // Update icons
    if (themeToggle) {
      themeToggle.innerHTML = theme === 'dark'
        ? '<i class="fas fa-sun"></i>'
        : '<i class="fas fa-moon"></i>';
      themeToggle.title = theme === 'dark' ? 'Светлая тема' : 'Тёмная тема';
    }
    if (accessibilityToggle) {
      const isA11y = theme === 'accessibility';
      accessibilityToggle.innerHTML = isA11y
        ? '<i class="fas fa-eye-slash"></i>'
        : '<i class="fas fa-eye"></i>';
      accessibilityToggle.title = isA11y ? 'Обычный режим' : 'Режим для слабовидящих';
    }
    localStorage.setItem('mass-expert-theme', theme || '');
  }

  // Load saved theme
  const saved = localStorage.getItem('mass-expert-theme');
  if (saved) setTheme(saved);

  // Theme toggle click
  if (themeToggle) {
    themeToggle.addEventListener('click', () => {
      const current = html.classList.contains('theme-dark');
      setTheme(current ? '' : 'dark');
    });
  }

  // Accessibility toggle click
  if (accessibilityToggle) {
    accessibilityToggle.addEventListener('click', () => {
      const current = html.classList.contains('theme-accessibility');
      // When enabling accessibility, also apply dark theme for better contrast
      setTheme(current ? '' : 'accessibility');
      if (!current && !html.classList.contains('theme-dark')) {
        html.classList.add('theme-dark');
        if (themeToggle) {
          themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
          themeToggle.title = 'Светлая тема';
        }
      }
    });
  }

  // --- Mobile Nav Toggle ---
  const toggle = document.querySelector('.navbar-toggle');
  const navLinks = document.querySelector('.navbar-links');
  if (toggle) {
    toggle.addEventListener('click', () => {
      navLinks.classList.toggle('open');
    });
    navLinks.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => navLinks.classList.remove('open'));
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
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
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

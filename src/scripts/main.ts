// ============================================================
// Main island runtime — lightweight, progressive enhancement.
// No framework. One small script for the whole experience.
// ============================================================

(() => {
  const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // ---------- Reveal on scroll ----------
  const revealEls = document.querySelectorAll('[data-reveal]');
  if ('IntersectionObserver' in window && !prefersReduced) {
    const io = new IntersectionObserver(
      (entries) => {
        for (const e of entries) {
          if (e.isIntersecting) {
            e.target.classList.add('is-revealed');
            io.unobserve(e.target);
          }
        }
      },
      { threshold: 0.12, rootMargin: '0px 0px -8% 0px' }
    );
    revealEls.forEach((el) => io.observe(el));
  } else {
    revealEls.forEach((el) => el.classList.add('is-revealed'));
  }

  // ---------- Nav: scrolled state + scrollspy ----------
  const nav = document.querySelector('[data-nav]');
  const spyAnchors = [...document.querySelectorAll('.nav__link, .nav__menu-link')].filter(
    (a) => (a.getAttribute('href') || '').startsWith('#')
  );
  const sectionIds = [...new Set(spyAnchors.map((a) => a.getAttribute('href')!.slice(1)))];
  const sections = sectionIds
    .map((id) => document.getElementById(id))
    .filter((el): el is HTMLElement => !!el);

  const setActive = (id: string) => {
    spyAnchors.forEach((a) => {
      a.classList.toggle('is-active', a.getAttribute('href') === `#${id}`);
    });
  };

  const onScroll = () => {
    if (nav) nav.classList.toggle('is-scrolled', window.scrollY > 24);
    if (!('IntersectionObserver' in window)) return;
    // find section currently in viewport
    let current = '';
    for (const s of sections) {
      if (s.getBoundingClientRect().top <= window.innerHeight * 0.4) current = s.id;
    }
    if (current) setActive(current);
  };

  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  // ---------- Mobile nav toggle ----------
  const toggleBtn = document.querySelector<HTMLButtonElement>('[data-nav-toggle]');
  const menu = document.querySelector<HTMLElement>('[data-nav-menu]');
  if (toggleBtn && menu) {
    toggleBtn.addEventListener('click', () => {
      const open = toggleBtn.getAttribute('aria-expanded') === 'true';
      toggleBtn.setAttribute('aria-expanded', String(!open));
      menu.hidden = open;
      document.body.classList.toggle('nav-open', !open);
    });
    menu.querySelectorAll('a').forEach((a) =>
      a.addEventListener('click', () => {
        toggleBtn.setAttribute('aria-expanded', 'false');
        menu.hidden = true;
        document.body.classList.remove('nav-open');
      })
    );
  }

  // ---------- Model ladder: expandable rungs ----------
  document.querySelectorAll('[data-rung]').forEach((rung) => {
    const btn = rung.querySelector<HTMLButtonElement>('[data-rung-toggle]');
    const panel = rung.querySelector<HTMLElement>('[data-rung-panel]');
    if (!btn || !panel) return;
    // Card grid: single-open accordion within a group
    btn.addEventListener('click', () => {
      const group = rung.closest('[data-ladder]');
      const isOpen = rung.classList.contains('is-open');
      if (group) {
        group.querySelectorAll('[data-rung].is-open').forEach((o) => {
          if (o !== rung) {
            o.classList.remove('is-open');
            const ob = o.querySelector('[data-rung-toggle]');
            const op = o.querySelector('[data-rung-panel]');
            ob?.setAttribute('aria-expanded', 'false');
            op?.setAttribute('hidden', '');
          }
        });
      }
      rung.classList.toggle('is-open', !isOpen);
      btn.setAttribute('aria-expanded', String(!isOpen));
      panel.hidden = isOpen;
    });
    btn.setAttribute('aria-expanded', 'false');
    btn.setAttribute('aria-controls', panel.id || '');
  });

  // ---------- Experiment pipeline: progressive illumination ----------
  const pipeline = document.querySelector('[data-pipeline]');
  if (pipeline && 'IntersectionObserver' in window && !prefersReduced) {
    const steps = pipeline.querySelectorAll('[data-pipe-step]');
    const pio = new IntersectionObserver(
      (entries) => {
        for (const e of entries) {
          if (e.isIntersecting) {
            const idx = Number(e.target.getAttribute('data-pipe-step'));
            steps.forEach((s, i) => {
              s.classList.toggle('is-lit', i <= idx);
            });
          }
        }
      },
      { threshold: 0.35, rootMargin: '0px 0px -20% 0px' }
    );
    steps.forEach((s) => pio.observe(s));
  } else if (pipeline) {
    pipeline.querySelectorAll('[data-pipe-step]').forEach((s) => s.classList.add('is-lit'));
  }

  // ---------- Timeline reveal: phase 01 highlight ----------
  const timeline = document.querySelector('[data-timeline]');
  if (timeline) {
    const first = timeline.querySelector('[data-phase]');
    first?.classList.add('is-current');
  }
})();
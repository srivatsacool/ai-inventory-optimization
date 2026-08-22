// ============================================================
// Hero interaction — "the research instrument" (v0.3)
// GSAP + ScrollTrigger. Progressive enhancement: without JS the
// hero is fully readable and static (CSS defaults are the final
// states). All motion is transform/opacity-based and respects
// prefers-reduced-motion via gsap.matchMedia.
// ============================================================
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

const HUES: Record<string, string> = {
  trad: '#35618A',
  stat: '#27757A',
  neural: '#5B56A0',
  llm: '#7A53A6',
};

const DEFAULTS = { ease: 'power2.out' };
function q<T extends Element = HTMLElement>(sel: string): T | null {
  return document.querySelector(sel);
}
function qa(sel: string): HTMLElement[] {
  return Array.from(document.querySelectorAll(sel));
}

const hero = q<HTMLElement>('.hero');
const engine = q<HTMLElement>('[data-engine]');
const signalBox = q<HTMLElement>('[data-signal]');
const readout = q<HTMLElement>('[data-model-readout]');
const rungs = qa('[data-model]');
const headlineLines = qa('[data-reveal-line]');

const prefersReduced =
  window.matchMedia('(prefers-reduced-motion: reduce)').matches;

// ---------- chart line drawing (GSAP) ----------
function drawPath(el: SVGPathElement, duration = 0.9, onDone?: () => void) {
  const len = el.getTotalLength();
  gsap.set(el, { strokeDasharray: len, strokeDashoffset: len });
  gsap.to(el, {
    strokeDashoffset: 0,
    duration,
    ease: 'power1.inOut',
    onComplete: () => {
      gsap.set(el, { strokeDasharray: '', strokeDashoffset: '' });
      onDone?.();
    },
  });
}

// ---------- model hover / focus signals ----------
function activateModel(rung: HTMLElement) {
  const name = rung.dataset.name ?? '';
  const hue = rung.dataset.hue ?? 'trad';

  rungs.forEach((r) => r.classList.remove('is-active'));
  rung.classList.add('is-active');
  if (readout) readout.textContent = `Model: ${name}`;
  if (signalBox) signalBox.style.setProperty('--fc-hue', HUES[hue] ?? HUES.trad!);
  engine?.setAttribute('data-linked', '');
}

function deactivateModel() {
  rungs.forEach((r) => r.classList.remove('is-active'));
  if (readout) readout.textContent = 'Model: —';
  if (signalBox) signalBox.style.removeProperty('--fc-hue');
  engine?.removeAttribute('data-linked');
}

rungs.forEach((rung) => {
  rung.addEventListener('mouseenter', () => activateModel(rung));
  rung.addEventListener('mouseleave', deactivateModel);
  rung.addEventListener('focusin', () => activateModel(rung));
  rung.addEventListener('focusout', deactivateModel);
});

// ---------- master timeline + scroll exit ----------
if (!prefersReduced) {
  // load choreography
  const tl = gsap.timeline({ defaults: DEFAULTS, delay: 0.2 });

  tl.fromTo('.meta', { y: -10, opacity: 0 }, { y: 0, opacity: 1, duration: 0.55 }, 0.1)
    .fromTo(
      headlineLines,
      { yPercent: 112, opacity: 0 },
      { yPercent: 0, opacity: 1, duration: 0.8, stagger: 0.1 },
      '-=0.2'
    )
    .fromTo('.sub', { x: -16, opacity: 0 }, { x: 0, opacity: 1, duration: 0.6 }, '-=0.45')
    .fromTo('.engine', { x: 44, opacity: 0 }, { x: 0, opacity: 1, duration: 0.9, ease: 'power2.out' }, '-=0.35');

  tl.add(() => {
    const actual = q<SVGPathElement>('.signal__actual');
    const forecast = q<SVGPathElement>('.signal__forecast');
    const band = q<SVGPathElement>('.signal__band');
    if (actual) drawPath(actual, 0.9);
    if (forecast) {
      drawPath(forecast, 0.75, () => gsap.set(forecast, { strokeDasharray: '6 5' }));
    }
    if (band) {
      gsap.to(band, { opacity: 1, duration: 0.8, delay: 0.35 });
      gsap.to(band, { opacity: 0.55, duration: 4.2, ease: 'sine.inOut', delay: 1.2, yoyo: true, repeat: -1 });
    }
  }, '-=0.4');

  tl.fromTo('.timeline', { y: 18, opacity: 0 }, { y: 0, opacity: 1, duration: 0.65 }, '-=0.3')
    .fromTo(
      qa('.timeline__model'),
      { opacity: 0, y: 8 },
      { opacity: 1, y: 0, duration: 0.35, stagger: 0.045 },
      '-=0.35'
    )
    .fromTo('.statement', { y: 12, opacity: 0 }, { y: 0, opacity: 1, duration: 0.55 }, '-=0.2')
    .fromTo('.cta', { y: 12, opacity: 0 }, { y: 0, opacity: 1, duration: 0.5 }, '-=0.25');

  // scroll-based exit into the research content.
  const exitTl = gsap.timeline({
    defaults: { ease: 'none' },
    scrollTrigger: {
      trigger: hero,
      start: 'top top',
      end: 'bottom top',
      scrub: 0.6,
      invalidateOnRefresh: true,
    },
  });

  // phase 1 — subtle parallax for the entire scroll span (no opacity)
  exitTl.to('.engine', { yPercent: -3, duration: 1 }, 0)
        .to('.hero__left', { yPercent: -6, duration: 1 }, 0);

  // phase 2 — intentional exit fade, only as the hero hands off
  exitTl.to('.hero__left', { opacity: 0.5, ease: 'power1.in', duration: 0.4 }, 0.6)
        .to('.engine', { opacity: 0.78, ease: 'power1.in', duration: 0.34 }, 0.66);

  // re-measure once web fonts finish loading (layout shifts without a resize)
  if (document.fonts?.ready) document.fonts.ready.then(() => ScrollTrigger.refresh());
} else {
  // fast-forward to final states — no motion
  gsap.set([...headlineLines, ...[q('.meta'), q('.sub'), engine, q('.timeline'), q('.statement'), q('.cta')].filter(Boolean)], {
    opacity: 1, y: 0, x: 0,
  });
  const band = q<SVGPathElement>('.signal__band');
  if (band) gsap.set(band, { opacity: 1 });
}

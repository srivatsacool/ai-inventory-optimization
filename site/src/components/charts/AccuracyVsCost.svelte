<script>
  // AccuracyVsCost.svelte — the hero scatter, redesigned (paint pass).
  // Palette-driven points (12-model colors), efficient-frontier staircase,
  // hover dimming with chart-plate tooltip, dataset toggle, insight payoff.
  import { modelColor, OPACITY } from '../../lib/modelColors.js';

  export let m5Forecast = [];
  export let m5Inventory = [];
  export let forecast = [];
  export let inventory = [];

  let dataset = 'm5';
  let hovered = null;
  let plate = null; // { x, y, model, mase, cost, role }

  $: fc = dataset === 'm5' ? m5Forecast : forecast;
  $: inv = dataset === 'm5' ? m5Inventory : inventory;

  $: points = fc
    .map(f => {
      const invRow = inv.find(i => i.model === f.model);
      return invRow ? { model: f.model, mase: f.mase, cost: invRow.total } : null;
    })
    .filter(Boolean);

  // Efficient frontier: a point is ON the frontier if no other point has both
  // lower-or-equal MASE and lower-or-equal cost (with at least one strictly lower).
  $: frontier = points.filter(p =>
    !points.some(q => q !== p && q.mase <= p.mase && q.cost <= p.cost &&
      (q.mase < p.mase || q.cost < p.cost))
  );
  $: frontierPath = [...frontier]
    .sort((a, b) => a.mase - b.mase)
    .map((p, i) => `${i === 0 ? 'M' : 'L'} ${x(p.mase)} ${y(p.cost)}`)
    .join(' ');

  $: bestForecast = [...points].sort((a, b) => a.mase - b.mase)[0];
  $: bestCost = [...points].sort((a, b) => a.cost - b.cost)[0];

  const W = 680, H = 460, PAD = 56, RIGHT = 26, TOP = 30;
  $: maxMase = Math.max(...points.map(p => p.mase)) * 1.08;
  $: maxCost = Math.max(...points.map(p => p.cost)) * 1.08;
  $: x = m => PAD + ((m - 0) / maxMase) * (W - PAD - RIGHT);
  $: y = c => H - PAD - ((c - 0) / maxCost) * (H - PAD - TOP);

  $: xTicks = niceTicks(0, maxMase, 4);
  $: yTicks = niceTicks(0, maxCost, 4);

  function niceTicks(min, max, count) {
    const span = max - min;
    const raw = span / count;
    const mag = Math.pow(10, Math.floor(Math.log10(raw)));
    const norm = raw / mag;
    const step = (norm < 1.5 ? 1 : norm < 3 ? 2 : norm < 7 ? 5 : 10) * mag;
    const ticks = [];
    for (let v = 0; v <= max + step * 0.01; v += step) ticks.push(v);
    return ticks;
  }

  function fmt(v) {
    return v >= 1000 ? v.toLocaleString('en-US', { maximumFractionDigits: 0 })
      : v.toFixed(2);
  }

  function roleOf(p) {
    if (bestCost && p.model === bestCost.model) return 'inventory winner';
    if (bestForecast && p.model === bestForecast.model) return 'forecast winner';
    return '';
  }

  function enter(evt, p) {
    const rect = evt.currentTarget.closest('svg').getBoundingClientRect();
    hovered = p.model;
    plate = {
      px: ((x(p.mase) / W) * rect.width),
      py: ((y(p.cost) / H) * rect.height),
      model: p.model, mase: p.mase, cost: p.cost, role: roleOf(p),
    };
  }
  function leave() { hovered = null; plate = null; }

  $: anyHover = hovered !== null;

  // Cast curation (paint revision): the scatter tells the THESIS, not the
  // full ranking — the bar charts below carry every model. Named cast =
  // frontier models + both winners + Naive (worst-case anchor). The rest
  // render as unlabeled ghost dots at 10% so nothing is hidden, just quiet.
  $: namedCast = [...new Set([...frontier.map(p => p.model), bestForecast?.model, bestCost?.model, 'Naive'])]
    .filter(Boolean);
  $: cast = points.map(p => ({
    ...p,
    featured: namedCast.includes(p.model),
  }));
  $: featuredCount = cast.filter(p => p.featured).length;
</script>

<div class="avc">
  <div class="avc-head">
    <div class="legend">
      <span><i style="background:#35618A"></i> efficient frontier</span>
      <span><i class="sw" style="background:#D1495B"></i> forecast winner</span>
      <span><i class="sw" style="background:#3D7B55"></i> inventory winner</span>
    </div>
    <div class="ds-toggle" role="tablist" aria-label="Dataset">
      <button class:on={dataset === 'm5'} on:click={() => (dataset = 'm5')}>M5 · Sparse</button>
      <button class:on={dataset === 'store'} on:click={() => (dataset = 'store')}>Store · Dense</button>
    </div>
  </div>

  <div class="plate-wrap">
    <svg viewBox="0 0 {W} {H}" role="img" aria-label="Forecast error versus inventory cost, one point per model">
      <!-- gridlines + tick labels -->
      {#each yTicks as t}
        <line class="grid" x1={PAD} x2={W - RIGHT} y1={y(t)} y2={y(t)} />
        <text class="tick" x={PAD - 8} y={y(t) + 3} text-anchor="end">{fmt(t)}</text>
      {/each}
      {#each xTicks as t}
        <line class="grid" x1={x(t)} x2={x(t)} y1={TOP} y2={H - PAD} />
        <text class="tick" x={x(t)} y={H - PAD + 16} text-anchor="middle">{fmt(t)}</text>
      {/each}

      <!-- axes -->
      <line class="axis" x1={PAD} x2={W - RIGHT} y1={H - PAD} y2={H - PAD} />
      <line class="axis" x1={PAD} x2={PAD} y1={TOP} y2={H - PAD} />
      <text class="axis-label" x={(W + PAD) / 2} y={H - 12} text-anchor="middle">Forecast error (MASE) → worse</text>
      <text class="axis-label" x={16} y={(H - PAD + TOP) / 2} text-anchor="middle"
            transform="rotate(-90 16 {(H - PAD + TOP) / 2})">Inventory cost → worse</text>

      <!-- efficient frontier staircase -->
      {#if frontierPath}
        <path class="frontier" d={frontierPath} fill="none" />
      {/if}

      <!-- points: featured cast + quiet ghosts (hovered point last = on top) -->
      {#each [...cast].sort((a, b) => (a.model === hovered ? 1 : 0) - (b.model === hovered ? 1 : 0)) as p (p.model)}
        <g
          class="pt"
          class:ghost={!p.featured}
          class:dim={anyHover && hovered !== p.model}
          on:mouseenter={(e) => enter(e, p)}
          on:mouseleave={leave}
          on:focus={(e) => enter(e, p)}
          on:blur={leave}
          tabindex={p.featured ? '0' : '-1'}
          role="img"
          aria-label="{p.model}: MASE {p.mase.toFixed(3)}, cost {fmt(p.cost)}"
        >
          {#if p.featured}
            <circle class="halo" cx={x(p.mase)} cy={y(p.cost)} r="13" fill={modelColor(p.model)} />
            <circle class="dot" cx={x(p.mase)} cy={y(p.cost)} r="7" fill={modelColor(p.model)} />
            <text class="pt-label" x={x(p.mase)} y={y(p.cost) - 13} text-anchor="middle">{p.model}</text>
          {:else}
            <circle class="ghost-dot" cx={x(p.mase)} cy={y(p.cost)} r="4.5" fill={modelColor(p.model)} />
          {/if}
        </g>
      {/each}
    </svg>

    {#if plate}
      <div class="plate" style="left:{plate.px}px; top:{plate.py}px;">
        <div class="plate-model" style="color:{modelColor(plate.model)}">{plate.model}</div>
        {#if plate.role}<div class="plate-role">{plate.role}</div>{/if}
        <div class="plate-row"><span>MASE</span><b>{plate.mase.toFixed(3)}</b></div>
        <div class="plate-row"><span>Cost</span><b>{fmt(plate.cost)}</b></div>
      </div>
    {/if}
  </div>

  <p class="avc-note">
    {#if bestForecast && bestCost && bestForecast.model !== bestCost.model}
      <strong>{bestForecast.model}</strong> forecasts best (MASE {bestForecast.mase.toFixed(3)}) —
      but <strong>{bestCost.model}</strong> costs less ({fmt(bestCost.cost)} vs {fmt(bestForecast.cost)}).
      {:else}
      <strong>{bestForecast?.model}</strong> wins on both forecast accuracy and inventory cost in this dataset.
    {/if}
    <span class="note-meta">{featuredCount} of {cast.length} models featured · full ranking in the bar charts below</span>
  </p>
</div>

<style>
  .avc { width: 100%; }
  .avc-head { display: flex; justify-content: space-between; align-items: center; gap: 1rem; flex-wrap: wrap; margin-bottom: 0.4rem; }
  .legend { display: flex; align-items: center; gap: 1.1rem; font-family: var(--font-label); font-size: 0.64rem; letter-spacing: 0.1em; text-transform: uppercase; color: var(--ink-mute); }
  .legend i { display: inline-block; width: 18px; height: 2px; margin-right: 6px; vertical-align: middle; border-radius: 1px; }
  .legend i.sw { width: 10px; height: 10px; border-radius: 50%; }
  .ds-toggle { display: flex; gap: 0.3rem; }
  .ds-toggle button {
    font-family: var(--font-label); font-size: 0.64rem; letter-spacing: 0.1em; text-transform: uppercase;
    padding: 0.3rem 0.6rem; border: 1px solid var(--line); border-radius: 6px;
    background: transparent; color: var(--ink-mute); cursor: pointer; transition: all 120ms cubic-bezier(0.22,0.61,0.36,1);
  }
  .ds-toggle button:hover { border-color: var(--trad); color: var(--trad); }
  .ds-toggle button.on { background: var(--trad); border-color: var(--trad); color: #fff; }

  .plate-wrap { position: relative; }
  svg { width: 100%; height: auto; display: block; }
  .grid { stroke: rgba(30,34,42,0.06); stroke-width: 1; }
  .axis { stroke: #C4BBA8; stroke-width: 1.2; }
  .tick { font-family: var(--font-label); font-size: 10px; fill: var(--ink-mute); }
  .axis-label { font-family: var(--font-label); font-size: 10px; letter-spacing: 0.1em; text-transform: uppercase; fill: var(--ink-mute); }
  .frontier { stroke: #35618A; stroke-width: 1.6; stroke-dasharray: 5 4; opacity: 0.75; }

  .pt { cursor: pointer; outline: none; }
  .pt .dot { transition: opacity 120ms cubic-bezier(0.22,0.61,0.36,1); opacity: 0.55; }
  .pt .halo { opacity: 0; transition: opacity 120ms cubic-bezier(0.22,0.61,0.36,1); }
  .pt .pt-label { font-size: 10px; fill: var(--ink-soft); opacity: 0.85; transition: opacity 120ms cubic-bezier(0.22,0.61,0.36,1); }
  .pt.dim .dot, .pt.dim .pt-label { opacity: 0.18; }
  .pt:hover .dot, .pt:focus .dot { opacity: 1; }
  .pt:hover .halo, .pt:focus .halo { opacity: 0.18; }
  .pt:hover .pt-label, .pt:focus .pt-label { opacity: 1; font-weight: 600; }
  /* ghost cast: unlabeled, small, near-invisible until touched */
  .pt.ghost { cursor: default; }
  .pt.ghost .ghost-dot { opacity: 0.1; transition: opacity 120ms cubic-bezier(0.22,0.61,0.36,1); }
  .pt.ghost:hover .ghost-dot, .pt.ghost:focus .ghost-dot { opacity: 0.55; }

  .plate {
    position: absolute; transform: translate(-50%, calc(-100% - 14px));
    background: #FAF8F4; border: 1px solid #C4BBA8; border-radius: 6px;
    box-shadow: 0 2px 8px rgba(30,34,42,0.12);
    padding: 8px 11px; min-width: 128px; pointer-events: none; z-index: 5;
  }
  .plate-model { font-weight: 700; font-size: 0.82rem; }
  .plate-role { font-family: var(--font-label); font-size: 0.56rem; letter-spacing: 0.12em; text-transform: uppercase; color: var(--ink-mute); margin-top: 1px; }
  .plate-row { display: flex; justify-content: space-between; gap: 0.8rem; font-size: 0.72rem; color: var(--ink-soft); margin-top: 3px; }
  .plate-row b { font-variant-numeric: tabular-nums; color: var(--ink); }

  .avc-note {
    margin: 0.75rem 0 0; padding: 0.65rem 0.9rem; font-size: 0.85rem; color: var(--ink-soft);
    background: #F3EFE6; border-left: 3px solid #35618A; border-radius: 0 6px 6px 0;
  }
  .note-meta { display: block; margin-top: 4px; font-family: var(--font-label); font-size: 0.62rem; letter-spacing: 0.1em; text-transform: uppercase; color: var(--ink-mute); }
  @media (prefers-reduced-motion: reduce) {
    .pt .dot, .pt .halo, .pt .pt-label, .ds-toggle button { transition: none; }
  }
</style>

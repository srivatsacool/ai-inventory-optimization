<script>
  // CostBarChart.svelte — palette-driven horizontal bars (paint pass).
  // 12-model colors, winner full-saturation, metric toggle, hover dim.
  import { modelColor, OPACITY } from '../../lib/modelColors.js';

  export let data = [];          // [{model, holding, stockout, total, service}]
  export let title = '';
  export let unit = 'cost (H=1 units)';

  const METRICS = [
    { key: 'total', label: 'Total cost', format: v => v >= 1000 ? v.toLocaleString('en-US', { maximumFractionDigits: 0 }) : v.toFixed(2) },
    { key: 'holding', label: 'Holding', format: v => v.toFixed(2) },
    { key: 'stockout', label: 'Stockout', format: v => v.toFixed(2) },
    { key: 'service', label: 'Service %', format: v => v.toFixed(1) + '%', higherBetter: true },
  ];

  let metric = 'total';
  let hovered = null;

  $: current = METRICS.find(m => m.key === metric) || METRICS[0];
  $: maxVal = Math.max(...data.map(d => Math.abs(d[metric]))) || 1;
  $: sorted = [...data].sort((a, b) => current.higherBetter ? b[metric] - a[metric] : a[metric] - b[metric]);
  $: best = sorted[0];
  $: worst = sorted[sorted.length - 1];
  $: anyHover = hovered !== null;
</script>

<div class="chart">
  <div class="chart-head">
    <div>
      <p class="chart-label">{title}</p>
      <p class="chart-sub">{current.label} · {unit} · {current.higherBetter ? 'higher is better' : 'lower is better'}</p>
    </div>
    <div class="metric-toggle" role="tablist" aria-label="Metric">
      {#each METRICS as m}
        <button
          class="toggle-btn"
          class:active={metric === m.key}
          role="tab"
          aria-selected={metric === m.key}
          on:click={() => (metric = m.key)}
          on:mouseenter={() => {}}
        >{m.label}</button>
      {/each}
    </div>
  </div>

  <div class="bars">
    {#each sorted as d (d.model)}
      <div
        class="bar-row"
        class:dim={anyHover && hovered !== d.model}
        on:mouseenter={() => (hovered = d.model)}
        on:mouseleave={() => (hovered = null)}
      >
        <span class="bar-model" class:winner={d.model === best.model}>{d.model}</span>
        <div class="bar-track">
          <div
            class="bar-fill"
            class:best={d.model === best.model}
            style="width:{(Math.abs(d[metric]) / maxVal) * 100}%; background: {modelColor(d.model)}; opacity: {d.model === best.model ? OPACITY.winner : OPACITY.context};"
          ></div>
          <span class="bar-value">{current.format(d[metric])}</span>
        </div>
      </div>
    {/each}
  </div>

  <div class="chart-foot">
    <span class="winner">Best: <strong style="color:{modelColor(best.model)}">{best.model}</strong> · {current.format(best[metric])}</span>
    <span class="worst">Worst: <strong>{worst.model}</strong> · {current.format(worst[metric])}</span>
  </div>
</div>

<style>
  .chart { width: 100%; }
  .chart-head { display: flex; justify-content: space-between; align-items: start; gap: 1rem; flex-wrap: wrap; margin-bottom: 1rem; }
  .chart-label { margin: 0; font-size: 1.05rem; font-weight: 600; }
  .chart-sub { margin: 0.15rem 0 0; font-family: var(--font-label); font-size: 0.66rem; letter-spacing: 0.12em; text-transform: uppercase; color: var(--ink-mute); }
  .metric-toggle { display: flex; gap: 0.3rem; flex-wrap: wrap; }
  .toggle-btn {
    font-family: var(--font-label); font-size: 0.62rem; letter-spacing: 0.1em; text-transform: uppercase;
    padding: 0.3rem 0.55rem; border: 1px solid var(--line); border-radius: 5px;
    background: transparent; color: var(--ink-mute); cursor: pointer;
    transition: all 120ms cubic-bezier(0.22,0.61,0.36,1);
  }
  .toggle-btn:hover { border-color: var(--trad); color: var(--trad); }
  .toggle-btn.active { background: var(--trad); border-color: var(--trad); color: #fff; }
  .bars { display: flex; flex-direction: column; gap: 0.35rem; }
  .bar-row { display: grid; grid-template-columns: 130px 1fr; align-items: center; gap: 0.6rem; transition: opacity 120ms cubic-bezier(0.22,0.61,0.36,1); }
  .bar-row.dim { opacity: 0.45; }
  .bar-model { font-size: 0.8rem; color: var(--ink-soft); text-align: right; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .bar-model.winner { font-weight: 700; color: var(--ink); }
  .bar-track { position: relative; height: 22px; background: rgba(30,34,42,0.045); border-radius: 4px; overflow: hidden; display: flex; align-items: center; }
  .bar-fill { height: 100%; border-radius: 4px; min-width: 2px; transition: width 300ms cubic-bezier(0.22,0.61,0.36,1); }
  .bar-row:hover .bar-fill.best { box-shadow: inset 0 0 0 1.5px rgba(30,34,42,0.25); }
  .bar-value {
    position: absolute; right: 6px; font-family: var(--font-label); font-size: 0.66rem;
    color: var(--ink); background: rgba(250,248,244,0.85); padding: 0 4px; border-radius: 3px;
    font-variant-numeric: tabular-nums;
  }
  .chart-foot { display: flex; justify-content: space-between; gap: 1rem; margin-top: 0.75rem; font-size: 0.75rem; color: var(--ink-mute); }
  .winner strong { font-weight: 700; }
  @media (max-width: 40rem) {
    .bar-row { grid-template-columns: 90px 1fr; }
    .bar-model { font-size: 0.72rem; }
  }
  @media (prefers-reduced-motion: reduce) {
    .bar-fill, .bar-row, .toggle-btn { transition: none; }
  }
</style>

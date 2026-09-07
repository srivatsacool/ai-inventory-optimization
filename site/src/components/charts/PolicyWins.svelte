<script>
  // PolicyWins.svelte — 27-policy sensitivity grid winners, palette-driven.
  import { modelColor } from '../../lib/modelColors.js';

  export let m5Wins = {};   // {LSTM: 25, SES: 2}
  export let storeWins = {}; // {Moving Average: 9, SES: 7, Naive: 6, DES: 5}
  export let totalPolicies = 27;

  let dataset = 'm5';
  let hovered = null;

  $: wins = dataset === 'm5' ? m5Wins : storeWins;
  $: rows = Object.entries(wins)
    .map(([model, count]) => ({ model, count, pct: (count / totalPolicies) * 100 }))
    .sort((a, b) => b.count - a.count);
  $: anyHover = hovered !== null;
</script>

<div class="pw">
  <div class="pw-head">
    <p class="pw-label">Sensitivity grid · who wins</p>
    <div class="ds-toggle" role="tablist" aria-label="Dataset">
      <button class:on={dataset === 'm5'} on:click={() => (dataset = 'm5')}>M5</button>
      <button class:on={dataset === 'store'} on:click={() => (dataset = 'store')}>Store</button>
    </div>
  </div>

  {#each rows as r (r.model)}
    <div
      class="row"
      class:dim={anyHover && hovered !== r.model}
      on:mouseenter={() => (hovered = r.model)}
      on:mouseleave={() => (hovered = null)}
    >
      <span class="model" class:leader={r === rows[0]}>{r.model}</span>
      <div class="track">
        <div class="fill" style="width:{r.pct}%; background: {modelColor(r.model)}; opacity: {r === rows[0] ? 1 : 0.55};"></div>
      </div>
      <span class="count">{r.count} / {totalPolicies}</span>
    </div>
  {/each}

  <p class="note">
    {#if dataset === 'm5'}
      <strong style="color:{modelColor(rows[0]?.model)}">{rows[0]?.model}</strong> takes
      <strong>{rows[0]?.count} of {totalPolicies}</strong> policy cells — a robust winner.
    {:else}
      Leadership is <strong>fragmented</strong>: no model dominates — the winner depends on the policy you run.
    {/if}
  </p>
</div>

<style>
  .pw { width: 100%; }
  .pw-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.6rem; }
  .pw-label { margin: 0; font-family: var(--font-label); font-size: 0.66rem; letter-spacing: 0.12em; text-transform: uppercase; color: var(--ink-mute); }
  .ds-toggle { display: flex; gap: 0.3rem; }
  .ds-toggle button {
    font-family: var(--font-label); font-size: 0.62rem; letter-spacing: 0.1em; text-transform: uppercase;
    padding: 0.25rem 0.55rem; border: 1px solid var(--line); border-radius: 5px;
    background: transparent; color: var(--ink-mute); cursor: pointer; transition: all 120ms cubic-bezier(0.22,0.61,0.36,1);
  }
  .ds-toggle button:hover { border-color: var(--trad); color: var(--trad); }
  .ds-toggle button.on { background: var(--trad); border-color: var(--trad); color: #fff; }
  .row { display: grid; grid-template-columns: 120px 1fr 52px; align-items: center; gap: 0.5rem; margin: 0.3rem 0; transition: opacity 120ms cubic-bezier(0.22,0.61,0.36,1); }
  .row.dim { opacity: 0.45; }
  .model { font-size: 0.78rem; color: var(--ink-soft); text-align: right; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .model.leader { font-weight: 700; color: var(--ink); }
  .track { height: 18px; background: rgba(30,34,42,0.045); border-radius: 4px; overflow: hidden; }
  .fill { height: 100%; border-radius: 4px; transition: width 300ms cubic-bezier(0.22,0.61,0.36,1); }
  .count { font-family: var(--font-label); font-size: 0.68rem; color: var(--ink-mute); font-variant-numeric: tabular-nums; }
  .note { margin: 0.7rem 0 0; font-size: 0.8rem; color: var(--ink-soft); }
  @media (max-width: 40rem) {
    .row { grid-template-columns: 88px 1fr 46px; }
    .model { font-size: 0.7rem; }
  }
  @media (prefers-reduced-motion: reduce) {
    .fill, .row, .ds-toggle button { transition: none; }
  }
</style>

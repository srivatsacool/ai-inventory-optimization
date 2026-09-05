// Cloudflare Pages serves the static dist/ output. No adapter: the site is
// fully static; /lab embeds the independently hosted Streamlit runtime and
// /doc serves the canonical PDF as a static asset.
import { defineConfig } from 'astro/config';

export default defineConfig({
  output: 'static',
  site: 'https://ai-inventory-optimization-research-project.buildsrivatsa.qzz.io',
});

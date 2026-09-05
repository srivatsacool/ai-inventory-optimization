// Runtime boundary for the LAB surface. The Streamlit application is hosted
// independently of this static site; /lab only embeds it, never reimplements it.
// EXTERNAL DEPENDENCY: set ASTRO_STREAMLIT_URL (or edit the fallback below)
// once the Streamlit host is chosen. Empty string = unconfigured → graceful fallback.
export const STREAMLIT_URL = process.env.ASTRO_STREAMLIT_URL ?? "";

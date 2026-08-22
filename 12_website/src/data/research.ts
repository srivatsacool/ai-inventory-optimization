// The research itself — title, question, position, RQ set.

export const RESEARCH = {
  title: 'From Traditional Forecasting to Large Language Models',
  subtitle: 'Evaluating AI-Based Inventory Optimization',
  question:
    'How does the effectiveness of AI-based inventory optimization change from traditional forecasting models to large language model–based approaches?',
  heroStatements: {
    tension:
      'Better forecast accuracy does not automatically guarantee better inventory decisions.',
    position:
      'Inventory outcomes also depend on demand variability, lead time, safety stock, service levels, holding costs, stockout costs, and ordering policy.',
  },
  principle: 'Do not assume that the most sophisticated model is the best model.',
  finalStatement: {
    line1: 'The goal is not to find the most advanced model.',
    line2: 'The goal is to find out which approach makes the best inventory decision.',
  },
} as const;

export const RESEARCH_QUESTIONS: { code: string; q: string }[] = [
  { code: 'RQ1', q: 'How do traditional, statistical, neural-network, and LLM-based approaches differ in demand forecasting performance?' },
  { code: 'RQ2', q: 'How do forecasting differences translate into inventory-management outcomes?' },
  { code: 'RQ3', q: 'Does increasing model sophistication consistently improve inventory performance?' },
  { code: 'RQ4', q: 'Are model-performance patterns consistent across different retail demand environments?' },
  { code: 'RQ5', q: 'What trade-offs exist between accuracy, inventory performance, computational requirements, and complexity?' },
];

export const UNCERTAINTY = {
  headline: "We don't know which model will win.",
  body: 'This is a research proposal. No experimental results exist yet, and the study is designed to discover the answer rather than assume it. Any of these approaches could lead — or none of them could, consistently.',
  candidates: [
    { label: 'Traditional', hue: 'trad' },
    { label: 'Statistical', hue: 'stat' },
    { label: 'Neural', hue: 'neural' },
    { label: 'LLM', hue: 'llm' },
  ],
} as const;

export const SCOREBOARD_MESSAGE =
  'The best forecast is not necessarily the best inventory strategy.';
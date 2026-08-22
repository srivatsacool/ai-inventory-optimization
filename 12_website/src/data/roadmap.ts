// Research roadmap — twelve phases from foundation to publication.

export interface RoadmapPhase {
  n: string;
  name: string;
  detail: string;
  status: 'current' | 'ahead' | 'done';
}

export const ROADMAP: RoadmapPhase[] = [
  { n: '01', name: 'Foundation', detail: 'Research proposal, website concept, repository, decision log.', status: 'current' },
  { n: '02', name: 'Literature', detail: 'Verify sources, build the literature matrix, refine the design.', status: 'ahead' },
  { n: '03', name: 'Data exploration', detail: 'Acquire and document datasets; EDA; select experimental series.', status: 'ahead' },
  { n: '04', name: 'Baselines', detail: 'MA · SES · DES · TES under comparable conditions.', status: 'ahead' },
  { n: '05', name: 'Statistical models', detail: 'ARIMA · SARIMA with time-based validation.', status: 'ahead' },
  { n: '06', name: 'Neural model', detail: 'LSTM — architecture earns its place through validation.', status: 'ahead' },
  { n: '07', name: 'LLM experiment', detail: 'Ollama setup, model selection, prompt design, output validation.', status: 'ahead' },
  { n: '08', name: 'Inventory simulation', detail: 'Common policy, costs, service level, stockouts.', status: 'ahead' },
  { n: '09', name: 'Robustness', detail: 'Sensitivity analysis across material assumptions.', status: 'ahead' },
  { n: '10', name: 'Final comparison', detail: 'Forecast, inventory, and practicality rankings.', status: 'ahead' },
  { n: '11', name: 'Report', detail: 'Methodology, results, discussion, limitations, conclusions.', status: 'ahead' },
  { n: '12', name: 'Publication / presentation', detail: 'Share findings and the completed research experience.', status: 'ahead' },
];

export const CONTRIBUTIONS: { area: string; note: string; tag: 'academic' | 'method' | 'practical' | 'ai' }[] = [
  { area: 'Academic', note: 'A comparison across forecasting generations — smoothing, statistics, neural, and LLM — on shared retail data.', tag: 'academic' },
  { area: 'Methodological', note: 'Connecting forecast evaluation with inventory outcomes in one reproducible framework.', tag: 'method' },
  { area: 'Practical', note: 'Evidence on whether additional model complexity produces meaningful operational benefits.', tag: 'practical' },
  { area: 'AI perspective', note: 'Testing whether LLM-based forecasting adds value relative to established approaches — without assuming it does.', tag: 'ai' },
];

export const PRINCIPLES: { n: number; text: string }[] = [
  { n: 1, text: 'Neutrality — never design experiments to prove LLMs are better.' },
  { n: 2, text: 'Question-first scope — every element must help answer the central question.' },
  { n: 3, text: 'Forecasting is the mechanism; inventory performance is the business-level outcome.' },
  { n: 4, text: 'Fair comparison — comparable data, horizons, periods, policies, and metrics.' },
  { n: 5, text: 'Time integrity — no future information in training, prompts, or decisions.' },
  { n: 6, text: 'Reproducibility — versions, assumptions, and outputs are recorded.' },
  { n: 7, text: 'Explicit assumptions — simulation parameters documented and sensitivity-tested.' },
  { n: 8, text: 'No fake completeness — unfinished research is marked unfinished.' },
  { n: 9, text: 'Complexity must earn its place.' },
  { n: 10, text: 'Results can change the plan — through the decision log.' },
  { n: 11, text: 'Literature claims must be verified.' },
  { n: 12, text: 'The website follows the research, not the reverse.' },
];
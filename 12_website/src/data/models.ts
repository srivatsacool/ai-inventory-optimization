// Research content — single source of truth for the proposal website.
// Sourced from 01_research/research_proposal.md and the planning pack.
// v0.1 — conceptual freeze. No experimental results exist yet.

export interface ModelInfo {
  id: string;
  name: string;
  longName: string;
  category: 'Traditional' | 'Statistical' | 'Neural' | 'LLM';
  hue: 'trad' | 'stat' | 'neural' | 'llm';
  idea: string;
  whyIncluded: string;
  complexity: string;
}

export const MODELS: ModelInfo[] = [
  {
    id: 'ma',
    name: 'MA',
    longName: 'Moving Average',
    category: 'Traditional',
    hue: 'trad',
    idea: 'The average of the most recent demand observations, used directly as the forecast for the next period.',
    whyIncluded: 'The simplest reference point on the ladder — establishes the baseline that every more complex model must beat.',
    complexity: 'One window length to choose. No estimation, no parameters to learn.',
  },
  {
    id: 'ses',
    name: 'SES',
    longName: 'Simple Exponential Smoothing',
    category: 'Traditional',
    hue: 'trad',
    idea: 'An exponentially weighted average of past demand, where recent observations matter more than distant ones.',
    whyIncluded: 'A classic robust baseline. Tests whether a statistically principled weighting of history beats a plain average.',
    complexity: 'One smoothing parameter, estimated from data.',
  },
  {
    id: 'des',
    name: 'DES',
    longName: 'Double Exponential Smoothing',
    category: 'Traditional',
    hue: 'trad',
    idea: 'Adds a trend component on top of the smoothed level, so forecasts can follow sustained increases or decreases.',
    whyIncluded: 'Introduces the first explicit structural assumption — that demand may be trending.',
    complexity: 'Level and trend smoothing, two parameters.',
  },
  {
    id: 'tes',
    name: 'TES',
    longName: 'Triple Exponential Smoothing (Holt-Winters)',
    category: 'Traditional',
    hue: 'trad',
    idea: 'Adds a seasonal component to level and trend — the classic method for retail demand with repeating patterns.',
    whyIncluded: 'The first model that models seasonality explicitly; retail demand is expected to be seasonal.',
    complexity: 'Level, trend, and seasonal components — three or more parameters.',
  },
  {
    id: 'arima',
    name: 'ARIMA',
    longName: 'Autoregressive Integrated Moving Average',
    category: 'Statistical',
    hue: 'stat',
    idea: 'Models demand as a linear combination of its own past values and past forecast errors, after differencing for stationarity.',
    whyIncluded: 'The canonical statistical benchmark — the standard against which forecasting research measures new methods.',
    complexity: 'Model order selection (p, d, q), estimation, diagnostics.',
  },
  {
    id: 'sarima',
    name: 'SARIMA',
    longName: 'Seasonal ARIMA',
    category: 'Statistical',
    hue: 'stat',
    idea: 'ARIMA extended with seasonal autoregressive and moving-average terms for data with repeating seasonal structure.',
    whyIncluded: 'The formal statistical treatment of seasonality — the bridge between statistics and the seasonal structure retail demand exhibits.',
    complexity: 'Full (p,d,q)×(P,D,Q,m) specification — the richest purely statistical configuration.',
  },
  {
    id: 'lstm',
    name: 'LSTM',
    longName: 'Long Short-Term Memory Network',
    category: 'Neural',
    hue: 'neural',
    idea: 'A recurrent neural network whose memory cells decide what to keep and what to forget across the demand sequence.',
    whyIncluded: 'The first learned, nonlinear model — tests whether flexible pattern learning beats explicit statistical structure.',
    complexity: 'Architecture, hyperparameters, and training all become decisions — complexity must earn its place.',
  },
  {
    id: 'llm',
    name: 'LLM',
    longName: 'Local LLM via Ollama',
    category: 'LLM',
    hue: 'llm',
    idea: 'A general-purpose, locally hosted language model prompted with structured historical demand, returning a numerical forecast.',
    whyIncluded: 'The experiment at the top of the ladder — can a practical local LLM be a competitive demand forecasting mechanism at all?',
    complexity: 'Prompt design, model selection, generation parameters, output parsing and validation.',
  },
];

export const MODEL_LADDER = MODELS.map((m) => m.name).join(' → ');
// Datasets — conceptual descriptions only. No fabricated statistics.

export interface DatasetInfo {
  id: string;
  name: string;
  organization: string;
  role: string;
  roleTag: 'primary' | 'secondary';
  blurb: string;
  characteristics: { label: string; note: string }[];
  note?: string;
}

export const DATASETS: DatasetInfo[] = [
  {
    id: 'm5',
    name: 'M5',
    organization: 'Walmart',
    role: 'Primary benchmark environment',
    roleTag: 'primary',
    blurb:
      'A hierarchical retail dataset of unit sales across products, stores, and calendar features — the established benchmark for retail demand forecasting.',
    characteristics: [
      { label: 'Structure', note: 'Hierarchical: categories, products, stores' },
      { label: 'Demand', note: 'Daily unit sales with calendar, price and event context' },
      { label: 'Patterns', note: 'Seasonality, intermittency, variable volume' },
      { label: 'Role', note: 'Reference point for forecasting competitions' },
    ],
  },
  {
    id: 'favorita',
    name: 'Grocery / Favorita',
    organization: 'Corporación Favorita',
    role: 'Secondary robustness environment',
    roleTag: 'secondary',
    blurb:
      'A grocery retail sales dataset spanning many stores and items with promotion and contextual information — a different retail demand environment for robustness testing.',
    characteristics: [
      { label: 'Structure', note: 'Multiple stores and items, transaction context' },
      { label: 'Demand', note: 'Grocery sales with promotions and store/item info' },
      { label: 'Patterns', note: 'Different demand behaviour than general merchandise' },
      { label: 'Role', note: 'Robustness check, not added merely for volume' },
    ],
  },
];

export const DATA_DISTINCTION = {
  title: 'Sales are not inventory',
  body:
    'M5 and Favorita describe demand. They do not provide a complete real-world inventory ledger — no actual on-hand stock, supplier lead times, holding costs, or stockout costs. Inventory outcomes in this study are therefore simulated under explicit, documented assumptions.',
};
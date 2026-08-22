// References — starting literature set from literature.md.
// This is the STARTING bibliography, not a final claim. Papers are
// grouped by literature stream. No DOIs fabricated — details pending
// verification in Phase 1 (Literature).

export interface RefEntry {
  id: string;
  authors: string;
  topic: string;
  stream: 'A' | 'B' | 'C' | 'D';
}

export const STREAMS: Record<'A' | 'B' | 'C' | 'D', string> = {
  A: 'Retail forecasting benchmarks',
  B: 'Forecasting-to-inventory research',
  C: 'Deep learning for retail forecasting',
  D: 'LLM / time-series forecasting',
};

export const REFERENCES: RefEntry[] = [
  { id: 'R1', authors: 'Makridakis, Spiliotis & Assimakopoulos', topic: 'M5 accuracy competition', stream: 'A' },
  { id: 'R2', authors: 'Makridakis, Spiliotis & Assimakopoulos', topic: 'M5 competition background and implementation', stream: 'A' },
  { id: 'R3', authors: 'Theodorou et al.', topic: 'Representativeness of the M5 data', stream: 'A' },
  { id: 'R4', authors: 'Ma & Fildes', topic: 'Robustness of the M5 global bottom-up approach', stream: 'A' },
  { id: 'R5', authors: 'Li et al.', topic: 'Demand forecasting to inventory ordering decisions', stream: 'B' },
  { id: 'R6', authors: 'Pirayesh Neghab, Khayyati & Karaesmen', topic: 'Deep learning and the newsvendor inventory problem', stream: 'B' },
  { id: 'R7', authors: '—', topic: 'Order-up-to inventory optimization using time-series forecasting and ensemble deep learning', stream: 'B' },
  { id: 'R8', authors: 'Castro Moraes et al.', topic: 'Hybrid CNN-LSTM retail sales forecasting', stream: 'C' },
  { id: 'R9', authors: 'Jin et al.', topic: 'Time-LLM', stream: 'D' },
  { id: 'R10', authors: 'Ansari et al.', topic: 'Chronos', stream: 'D' },
];

export const REF_NOTICE =
  'Starting bibliography — not a final claim of the ten objectively best papers. Bibliographic details, DOIs, and full texts are verified in Phase 1, and stronger papers may be added.';
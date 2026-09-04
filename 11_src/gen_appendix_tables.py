"""Chunked appendix tabular fragments (regular tabular; no page-break packages)."""
import pandas as pd
import json

NL = chr(10)
BS = chr(92)

HDR_P = (BS + 'toprule Dataset & Pair (A vs.~B) & Mean $d$ & $d_z$ & Holm $p$ & $r$ '
         + BS + BS + NL + BS + 'midrule' + NL)
HDR_G = (BS + 'toprule Gate & Status & Detail ' + BS + BS + NL + BS + 'midrule' + NL)
HDR_W = (BS + 'toprule Dataset & $L$ & Service & $P$ & Winner ' + BS + BS + NL
         + BS + 'midrule' + NL)
OPEN_P = '{' + BS + 'scriptsize' + NL + BS + 'setlength' + BS + 'tabcolsep{4pt}' + NL + BS + 'begin{tabular}{llrrrr}' + NL
OPEN_G = '{' + BS + 'scriptsize' + NL + BS + 'setlength' + BS + 'tabcolsep{4pt}' + NL + BS + 'begin{tabular}{lll}' + NL
OPEN_W = '{' + BS + 'scriptsize' + NL + BS + 'setlength' + BS + 'tabcolsep{4pt}' + NL + BS + 'begin{tabular}{lllll}' + NL
CLOSE = BS + 'end{tabular}}' + NL
ROWEND = BS + BS + NL


def prow(r):
    ds = 'M5' if str(r['dataset'])=='m5' else 'Store'
    return (ds + ' & ' + str(r['model_a']) + ' vs.~' + str(r['model_b']) + ' & '
            + f"{r['mean_d_a_minus_b']:.4f} & {r['cohen_dz']:.3f} & "
            + f"{r['wilcoxon_p_holm']:.2e} & {r['wilcoxon_rank_biserial_r']:.3f} "
            + ROWEND)


def emit(path, text):
    with open(path, 'w') as f:
        f.write(text)


pw = pd.read_csv('06_results/statistical_tests/pairwise_tests.csv')
m5 = pw[pw.dataset == 'm5'].reset_index(drop=True)
st = pw[pw.dataset == 'store_item_demand'].reset_index(drop=True)
emit('09_reports/final/appendix/gen_pairs_m5a.tex',
     OPEN_P + HDR_P + ''.join(prow(m5.iloc[i]) for i in range(0, 28)) + BS + 'bottomrule' + NL + CLOSE)
emit('09_reports/final/appendix/gen_pairs_m5b.tex',
     OPEN_P + HDR_P + ''.join(prow(m5.iloc[i]) for i in range(28, len(m5))) + BS + 'bottomrule' + NL + CLOSE)
emit('09_reports/final/appendix/gen_pairs_store.tex',
     OPEN_P + HDR_P + ''.join(prow(st.iloc[i]) for i in range(len(st))) + BS + 'bottomrule' + NL + CLOSE)
print('pairs chunks:', len(m5), len(st))

v = json.load(open('06_results/validation_report.json'))
gates = list(v.get('gates', v).items())
grows = []
for name, info in gates:
    if isinstance(info, dict):
        status, detail = info.get('status', ''), str(info.get('detail', ''))
    else:
        status, detail = str(info), ''
    detail = ' '.join(detail.split())
    detail = detail.replace('_', BS + '_').replace('%', BS + '%').replace('{', '(').replace('}', ')')
    while len(detail) > 44:
        detail = detail[:44]
    detail = detail.rstrip(BS)
    if detail.endswith(BS):
        detail = detail[:-1]
    grows.append(str(name).replace('_', ' ') + ' & ' + status + ' & ' + detail + ' ' + ROWEND)
half = (len(grows) + 1) // 2
emit('09_reports/final/appendix/gen_gates_a.tex',
     OPEN_G + HDR_G + ''.join(grows[:half]) + BS + 'bottomrule' + NL + CLOSE)
emit('09_reports/final/appendix/gen_gates_b.tex',
     OPEN_G + HDR_G + ''.join(grows[half:]) + BS + 'bottomrule' + NL + CLOSE)
print('gate chunks:', len(grows))

g = pd.read_csv('06_results/sensitivity/sensitivity_grid.csv')
for ds, tag in [('m5', 'm5'), ('store_item_demand', 'store')]:
    piv = g[g.dataset == ds].pivot_table(index=['lead_time', 'service_target', 'P'],
                                         columns='model', values='total_cost')
    rows = [('M5' if ds == 'm5' else 'Store') + ' & ' + str(int(L)) + ' & '
            + f'{s:.2f}' + ' & ' + str(int(P)) + ' & ' + str(m) + ' ' + ROWEND
            for (L, s, P), m in piv.idxmin(axis=1).items()]
    emit('09_reports/final/appendix/gen_winners_' + tag + '.tex',
         OPEN_W + HDR_W + ''.join(rows) + BS + 'bottomrule' + NL + CLOSE)
print('winner tables written')

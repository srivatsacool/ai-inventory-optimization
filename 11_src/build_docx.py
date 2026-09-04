"""DOCX build: copy of LaTeX master with \\cref expanded to typed refs. Master untouched."""
import os
import re
import shutil
import subprocess

ROOT = r'D:\Brain\07_Research\AI-INVENTORY-OPTIMIZATION'
SRC = os.path.join(ROOT, '09_reports', 'final')
DST = os.path.join(SRC, 'build_docx')
TYPES = {'fig': ('Figure', 'Figures'), 'tab': ('Table', 'Tables'),
         'sec': ('Section', 'Sections'), 'app': ('Appendix', 'Appendices')}

aux = open(os.path.join(SRC, 'report.aux'), encoding='utf-8', errors='replace').read()
nums = dict(re.findall(r'\\newlabel\{([^}]+)\}\{\{([^}]*)\}', aux))
print('labels in aux:', len(nums))


def ref(keys, cap):
    parts, kinds = [], set()
    for k in keys:
        kinds.add(k.split(':')[0])
        parts.append(nums.get(k.strip(), '??'))
    if len(kinds) == 1:
        t = TYPES.get(next(iter(kinds)), ('Ref', 'Refs'))
        name = t[0] if (len(parts) == 1 or not cap) else t[1]
        if cap:
            name = name
        else:
            name = name[0].lower() + name[1:] if False else name
        # lowercase for \cref, capitalized for \Cref
        if not cap and len(parts) == 1:
            pass
        joined = parts[0] if len(parts) == 1 else ' and '.join(parts)
        return f'{name} {joined}'
    return '; '.join(f"{TYPES.get(k.split(':')[0], ('Ref', 'Refs'))[0]} {nums.get(k.strip(), '??')}" for k in keys)


def sub(m):
    cap = m.group(1) == 'C'
    keys = [k.strip() for k in m.group(2).split(',')]
    kinds = {k.split(':')[0] for k in keys}
    if len(kinds) == 1:
        t = TYPES[kinds.pop()]
        word = t[1] if len(keys) > 1 else t[0]
        if not cap:
            word = word[0].lower() + word[1:]
        return word + ' ' + (' and '.join(nums.get(k, '??') for k in keys))
    items = []
    for k in keys:
        t = TYPES.get(k.split(':')[0], ('Ref', 'Refs'))
        w = t[0] if cap else t[0][0].lower() + t[0][1:]
        items.append(f'{w} {nums.get(k, "??")}')
    return '; '.join(items)


if os.path.exists(DST):
    shutil.rmtree(DST)
for sub_rel in ['sections', 'appendix', 'figures', 'figures_new', 'bibliography']:
    shutil.copytree(os.path.join(SRC, sub_rel), os.path.join(DST, sub_rel))
shutil.copy(os.path.join(SRC, 'report.tex'), DST)
n = 0
for dp, _, fns in os.walk(DST):
    for fn in fns:
        if fn.endswith('.tex'):
            p = os.path.join(dp, fn)
            t = open(p, encoding='utf-8').read()
            t2, c = re.subn(r'\\(C?)cref\{([^}]+)\}', sub, t)
            n += c
            open(p, 'w', encoding='utf-8').write(t2)
print('crefs expanded:', n)
r = subprocess.run(['pandoc', 'report.tex', '--from=latex', '--to=docx', '--citeproc',
                    '--bibliography=bibliography/refs.bib', '--resource-path=figures:.',
                    '-o', 'research_report.docx'], cwd=DST, capture_output=True, text=True)
print('pandoc exit:', r.returncode, r.stderr[-500:] if r.stderr else 'ok')
shutil.copy(os.path.join(DST, 'research_report.docx'),
            os.path.join(SRC, 'research_report.docx'))
print('final bytes:', os.path.getsize(os.path.join(SRC, 'research_report.docx')))

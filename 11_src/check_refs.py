import re, glob

labels = set(); refs = set(); cites = set()
files = glob.glob('sections/*.tex') + glob.glob('appendix/*.tex') + ['report.tex']
for f in files:
    t = open(f, encoding='utf-8').read()
    labels.update(re.findall(r'\\label\{([^}]+)\}', t))
    for m in re.findall(r'\\cref\{([^}]+)\}', t):
        refs.update(x.strip() for x in m.split(','))
    for m in re.findall(r'\\cite[tp]?\{([^}]+)\}', t):
        cites.update(x.strip() for x in m.split(','))
bt = open('bibliography/refs.bib', encoding='utf-8').read()
bibs = set(re.findall(r'@\w+\{([^,]+),', bt))
print('labels:', len(labels), 'refs:', len(refs), 'cites:', len(cites), 'bibs:', len(bibs))
print('UNDEFINED REFS:', sorted(set(refs) - labels))
print('UNCITED BIB:', sorted(bibs - cites))
print('MISSING BIB:', sorted(cites - bibs))

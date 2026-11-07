#!/usr/bin/env python3
"""make_paperrefs.py -- the paper's numbering and its Tables 1 and 7, for the slides.

Writes paperrefs.tex (for every label of the paper, its name and number, read from paper.aux after the
paper has been compiled), tab_results_src.tex (the tabular of Table 1, cut out of sec1_intro.tex) and
tab_artefacts_src.tex (the tabular of Table 7, cut out of sec_appendix.tex).

usage: make_paperrefs.py [PAPER_DIR]      (default ../paper)
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
paper = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'paper')
NAMES = {'section': 'Section', 'subsection': 'Section', 'appendix': 'Appendix', 'figure': 'Figure',
         'table': 'Table', 'equation': 'Equation', 'lemma': 'Lemma', 'theorem': 'Theorem',
         'proposition': 'Proposition', 'corollary': 'Corollary', 'remark': 'Remark',
         'definition': 'Definition'}

out = []
for line in open(os.path.join(paper, 'paper.aux'), encoding='utf-8', errors='replace'):
    m = re.match(r'\\newlabel\{(.+?)@cref\}\{\{\[(\w+)\]\[[^]]*\]\[[^]]*\]([^}]*)\}', line)
    if not m:
        continue
    label, kind, num = m.groups()
    if kind not in NAMES:
        raise SystemExit('unknown label type %s of %s' % (kind, label))
    out.append('\\expandafter\\def\\csname lref@%s\\endcsname{%s~%s}' % (label, NAMES[kind], num))
    out.append('\\expandafter\\def\\csname lnum@%s\\endcsname{%s}' % (label, num))
open(os.path.join(HERE, 'paperrefs.tex'), 'w').write('\n'.join(out) + '\n')


def tabular(texfile, label, outfile):
    """copy the tabular that follows \\label{label} in texfile"""
    src = open(os.path.join(paper, texfile), encoding='utf-8').read()
    i = src.index('\\label{%s}' % label)
    a = src.index('\\begin{tabular}', i)
    b = src.index('\\end{tabular}', a) + len('\\end{tabular}')
    open(os.path.join(HERE, outfile), 'w').write(src[a:b] + '\n')
    return src[a:b].count('\n') + 1


print('%d labels; Table 1: %d lines; Table 7: %d lines'
      % (len(out) // 2, tabular('sec1_intro.tex', 'tab:results', 'tab_results_src.tex'),
         tabular('sec_appendix.tex', 'tab:artefacts', 'tab_artefacts_src.tex')))

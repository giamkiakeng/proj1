#!/usr/bin/env python3
"""ruletable.py -- LaTeX table of a five-state rule file (as in the appendix).
usage: ruletable.py rulefile name label machinefile"""
import sys

rule, name, label, mfile = sys.argv[1:5]
tab = {}
for ln in open(rule):
    t = ln.split('#')[0].split()
    if len(t) == 4:
        tab[tuple(t[:3])] = t[3]
S = ['L', 'G', 'A', 'B']
R = ['*', 'L', 'G', 'A', 'B']
m = lambda s: '$\\mathsf{%s}$' % s
out = ['\\begin{table}[p]', '\\centering\\small', '\\begin{tabular}{@{}cc|ccccc@{}}', '\\toprule',
       'left & centre & \\multicolumn{5}{c}{right neighbour}\\\\',
       ' & & $\\ast$ & ' + ' & '.join(m(s) for s in S) + '\\\\']
for c in S:
    out.append('\\midrule')
    for l in R:
        row = []
        for r in R:
            if l == '*' and r == '*':
                row.append('--')
            else:
                row.append(m(tab[(l, c, r)]))
        out.append(('$\\ast$' if l == '*' else m(l)) + ' & ' + m(c) + ' & ' + ' & '.join(row) + '\\\\')
out += ['\\bottomrule', '\\end{tabular}',
        '\\caption{The five-state rule $%s$ of \\cref{thm:frontier}: entry $\\delta(\\text{left},\\text{centre},\\text{right})$. '
        'The entries $\\delta(\\mathsf L,\\mathsf L,\\mathsf L)=\\delta(\\mathsf L,\\mathsf L,\\ast)=\\mathsf L$ are the quiescence conditions; '
        '``--\'\' marks the unused neighbourhoods $(\\ast,y,\\ast)$. Machine-readable copy: \\texttt{%s}.}' % (name, mfile.replace('_', '\\_')),
        '\\label{%s}' % label, '\\end{table}']
print('\n'.join(out))

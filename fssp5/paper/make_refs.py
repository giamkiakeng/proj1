#!/usr/bin/env python3
"""
make_refs.py -- write references.tex for paper.tex, in the journal's style.

usage: python3 make_refs.py [paper.aux]

The references are numbered in the order of their first citation, which is read from the
\\citation lines of the .aux file written by a first LaTeX run.  Each entry follows the
journal's template "Last name, initials (year). Title. Journal, volume, pages.", names all
authors, and abbreviates journal titles as in Mathematical Reviews.  The data are those of
the bibliography of the earlier versions of the paper.
"""
import re
import sys

LNCS = 'Lecture Notes in Comput.\\ Sci.'

REFS = {
    'Moore64': "Moore, E.~F. (1964). The firing squad synchronization problem. In: E.~F. Moore (ed.), "
               "\\emph{Sequential Machines: Selected Papers}, pp.~213--214. Reading, MA: Addison-Wesley.",
    'Goto62': "Goto, E. (1962). A minimal time solution of the firing squad problem. Dittoed course notes "
              "for Applied Mathematics~298, Harvard University, pp.~52--59.",
    'Waksman66': "Waksman, A. (1966). An optimum solution to the firing squad synchronization problem. "
                 "\\emph{Inform.\\ and Control}, 9, 66--78.",
    'Mazoyer86': "Mazoyer, J. (1988). An overview of the firing squad synchronization problem. In: "
                 "C.~Choffrut (ed.), \\emph{Automata Networks}, " + LNCS + " 316, pp.~82--94. Springer.",
    'Umeo09': "Umeo, H. (2009). Firing squad synchronization problem in cellular automata. In: "
              "R.~A. Meyers (ed.), \\emph{Encyclopedia of Complexity and Systems Science}, pp.~3537--3574. "
              "Springer.",
    'Correa17': "Correa, T., Gustavo, B., Lemos, L., Settle, A. (2017). An overview of recent solutions to "
                "and lower bounds for the firing synchronization problem. arXiv:1701.01045.",
    'Balzer67': "Balzer, R. (1967). An 8-state minimal time solution to the firing squad synchronization "
                "problem. \\emph{Inform.\\ and Control}, 10, 22--42.",
    'Gerken87': "Gerken, H.-D. (1987). \\emph{{\\\"U}ber Synchronisationsprobleme bei Zellularautomaten}. "
                "Diplomarbeit, Institut f{\\\"u}r Theoretische Informatik, Technische Universit{\\\"a}t "
                "Braunschweig.",
    'Mazoyer87': "Mazoyer, J. (1987). A six-state minimal time solution to the firing squad synchronization "
                 "problem. \\emph{Theoret.\\ Comput.\\ Sci.}, 50, 183--238.",
    'Yunes93': "Yun{\\`e}s, J.-B. (1993). \\emph{Synchronisation et automates cellulaires: la ligne de "
               "fusiliers}. PhD thesis, Universit{\\'e} Paris~7. Available from HAL, tel-00139049.",
    'Sanders94': "Sanders, P. (1994). Massively parallel search for transition-tables of polyautomata. In: "
                 "\\emph{Parcella '94: Proceedings of the VI International Workshop on Parallel Processing "
                 "by Cellular Automata and Arrays}, pp.~99--108. Berlin: Akademie Verlag.",
    'Clergue18': "Clergue, M., Verel, S., Formenti, E. (2018). An iterated local search to find many "
                 "solutions of the 6-states firing squad synchronization problem. \\emph{Appl.\\ Soft "
                 "Comput.}, 66, 449--461.",
    'NguyenMaignan20': "Nguyen, T.~T., Maignan, L. (2020). Exploring millions of 6-state FSSP solutions: the "
                       "formal notion of local CA simulation. In: \\emph{Cellular Automata and Discrete "
                       "Complex Systems (AUTOMATA 2020)}, " + LNCS + " 12286, pp.~1--13. Springer.",
    'UmeoYanagihara07': "Umeo, H., Yanagihara, T. (2007). A smallest five-state solution to the firing "
                        "squad synchronization problem. In: \\emph{Machines, Computations, and Universality "
                        "(MCU 2007)}, " + LNCS + " 4664, pp.~291--302. Springer.",
    'Yunes08': "Yun{\\`e}s, J.-B. (2008). A 4-states algebraic solution to linear cellular automata "
               "synchronization. \\emph{Inform.\\ Process.\\ Lett.}, 107, 71--75.",
    'UmeoKamikawaYunes09': "Umeo, H., Kamikawa, N., Yun{\\`e}s, J.-B. (2009). A family of smallest "
                           "symmetrical four-state firing squad synchronization protocols for ring arrays. "
                           "\\emph{Parallel Process.\\ Lett.}, 19, 299--313.",
    'Mazoyer96': "Mazoyer, J. (1996). On optimal solutions to the firing squad synchronization problem. "
                 "\\emph{Theoret.\\ Comput.\\ Sci.}, 168, 367--404.",
    'YamashitaEtAl14': "Yamashita, K., Nishitani, Y., Hirose, S., Okawa, S., Osato, N. (2014). The firing "
                       "squad synchronization problem with sub-generals. \\emph{Inform.\\ Process.\\ Lett.}, "
                       "114, 60--65.",
    'Kobayashi19': "Kobayashi, K. (2019). Nonexistence of minimal-time solutions for some variations of the "
                   "firing squad synchronization problem having simple geometric configurations. "
                   "arXiv:1909.10125.",
    'MazoyerTerrier99': "Mazoyer, J., Terrier, V. (1999). Signals in one-dimensional cellular automata. "
                        "\\emph{Theoret.\\ Comput.\\ Sci.}, 217, 53--80.",
    'BerthiaumeEtAl04': "Berthiaume, A., Bittner, T., Perkovi{\\'c}, L., Settle, A., Simon, J. (2004). "
                        "Bounding the firing synchronization problem on a ring. \\emph{Theoret.\\ Comput.\\ "
                        "Sci.}, 320, 213--228.",
    'DAntonioDelzanno04': "D'Antonio, M., Delzanno, G. (2004). SAT-based analysis of cellular automata. "
                          "In: \\emph{Cellular Automata (ACRI 2004)}, " + LNCS + " 3305, pp.~745--754. "
                          "Springer.",
    'WetzlerHeuleHunt14': "Wetzler, N., Heule, M.~J.~H., Hunt, W.~A., Jr. (2014). DRAT-trim: efficient "
                          "checking and trimming using expressive clausal proofs. In: \\emph{Theory and "
                          "Applications of Satisfiability Testing (SAT 2014)}, " + LNCS + " 8561, "
                          "pp.~422--429. Springer.",
    'CruzFilipeEtAl17': "Cruz-Filipe, L., Heule, M.~J.~H., Hunt, W.~A., Jr., Kaufmann, M., "
                        "Schneider-Kamp, P. (2017). Efficient certified RAT verification. In: "
                        "\\emph{Automated Deduction -- CADE 26}, " + LNCS + " 10395, pp.~220--236. Springer.",
    'HeuleKullmannMarek16': "Heule, M.~J.~H., Kullmann, O., Marek, V.~W. (2016). Solving and verifying "
                            "the Boolean Pythagorean triples problem via cube-and-conquer. In: \\emph{Theory "
                            "and Applications of Satisfiability Testing (SAT 2016)}, " + LNCS + " 9710, "
                            "pp.~228--245. Springer.",
    'Heule18': "Heule, M.~J.~H. (2018). Schur number five. In: \\emph{Proceedings of the Thirty-Second AAAI "
               "Conference on Artificial Intelligence (AAAI-18)}, pp.~6598--6606.",
    'CaDiCaL2': "Biere, A., Faller, T., Fazekas, K., Fleury, M., Froleyks, N., Pollitt, F. (2024). "
                "CaDiCaL~2.0. In: \\emph{Computer Aided Verification (CAV 2024)}, " + LNCS + " 14681, "
                "pp.~133--152. Springer.",
    'Kissat20': "Biere, A., Fazekas, K., Fleury, M., Heisinger, M. (2020). CaDiCaL, Kissat, Paracooba, "
                "Plingeling and Treengeling entering the SAT Competition 2020. In: \\emph{Proceedings of SAT "
                "Competition 2020: Solver and Benchmark Descriptions}, Department of Computer Science Report "
                "Series~B, B-2020-1, pp.~51--53. University of Helsinki.",
    'Duprat97': "Duprat, J. (1997). Firing Squad Synchronization Problem. Coq user contribution FiringSquad "
                "(formal proof of the correctness of Mazoyer's six-state solution), LIP, ENS Lyon. Archived "
                "at \\url{https://github.com/rocq-archive/firing-squad}.",
    'Wolfram83': "Wolfram, S. (1983). Statistical mechanics of cellular automata. \\emph{Rev.\\ Modern "
                 "Phys.}, 55, 601--644.",
}


def main():
    aux = sys.argv[1] if len(sys.argv) > 1 else 'paper.aux'
    order = []
    for m in re.finditer(r'\\citation\{([^}]*)\}', open(aux).read()):
        for key in m.group(1).split(','):
            key = key.strip()
            if key and key not in order:
                order.append(key)
    missing = [k for k in order if k not in REFS]
    if missing:
        sys.exit('no entry for: ' + ', '.join(missing))
    unused = sorted(set(REFS) - set(order))
    with open('references.tex', 'w') as f:
        f.write('%% generated by make_refs.py from the citations in paper.aux; do not edit\n')
        f.write('\\begin{thebibliography}{99}\n\\small\n')
        for k in order:
            f.write('\\bibitem{%s} %s\n' % (k, REFS[k]))
        f.write('\\end{thebibliography}\n')
    print('%d references written%s' % (len(order), ('; not cited: ' + ', '.join(unused)) if unused else ''))


if __name__ == '__main__':
    main()

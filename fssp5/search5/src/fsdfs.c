/* fsdfs.c -- exhaustive backtracking search for k-state rules that synchronize the lines nmin..N in minimal time.
 *
 * No SAT solver.  The lines nmin, nmin+1, ..., N are simulated in this order, row by row and cell by cell.  When
 * a transition delta(x,y,z) is needed that is not yet defined, the program branches over its admissible values.
 * A branch fails when a cell is in state F before time 2n-2, or when a cell is not F at time 2n-2.  When the line
 * N has fired, the partial rule (the transitions that the lines nmin..N use) is counted as a solution.  Every
 * partial rule is reached at most once, because the order in which transitions are needed is determined by the
 * values chosen before.  So the program counts the rules for nmin..N "up to unused transitions".
 *
 * States: 0 = L, 1 = G, 2.. = auxiliary states A, B, ...; the value k-1 is F, and as a neighbour k-1 is the border.
 * Names: an auxiliary state may be used as a value only when all auxiliary states of smaller index have been used
 * (the classes below are invariant under renaming the auxiliary states), unless -nosym is given.
 *
 * Class options
 *   -b1s     (B1) strong: delta(x,G,y) = G unless x and y are both in {G, border}
 *   -b1w     (B1) weak:   delta(x,G,y) = G for working x, y, not both G
 *   -b3s     (B3) strong: GGG, *GG, GG* give F, and no other neighbourhood gives F
 *   -b3w     (B3) weak:   GGG, *GG, GG* give F
 *   -b4      delta(G,v,G) = G for working v != G
 *   -set xyz=d,...   -neq xyz=d,...    single transitions (letters L G A B C D * F)
 * Pruning options (necessary conditions for a rule that synchronizes nmin..N; they do not change the solutions)
 *   -front   the front cell (t, t+1) is not L for t <= N-3            (Lemma 2.4 of the paper, lines t+2, t+3 <= N)
 *   -chain   the return chain of the line n differs from the line n+1  (Lemma 2.4, lines n, n+1 <= N)
 *   -prefire with -b3s: every cell is G at time 2n-3
 *   -wall    with -b1s -b3s: no G in a cell i >= 2 with t + i <= min(2n-2, 2N-4)   (wall lemma, lines <= N)
 *   -gap     with -b1s -b3s: gap bound (two barriers at distance d at time t: 2n-3-t <= M(d-1))
 * Other options
 *   -max      do not stop at N: report how far each branch gets (N is then only the limit of the simulation)
 *   -print M  print the first M solutions
 *   -split D J M   work on the part J of M: the branches are numbered at depth D (D transitions chosen)
 *   -report S progress line every S seconds
 *   -knuth R SEED   do not search: estimate the number of nodes and of solutions by R random descents
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <math.h>

#define MAXN 48
#define MAXK 7
static int K, W, N, NMIN = 2;          /* W = K-1 working states; F = W as a value; border = W as a neighbour */
static int tab[(MAXK) * (MAXK) * (MAXK)];
static unsigned mask[(MAXK) * (MAXK) * (MAXK)];
static signed char cellv[MAXN + 2][2 * MAXN + 2][MAXN + 3];
static int opt_b1s, opt_b1w, opt_b3s, opt_b3w, opt_b4, opt_front, opt_chain, opt_prefire, opt_wall, opt_gap, opt_max, opt_nosym;
static long long nodes, sols, fails_by_line[MAXN + 2], done_by_line[MAXN + 2];
static int nprint = 0, naux = 0, depth = 0;
static int split_d = 0, split_j = 0, split_m = 1;
static long long split_ctr = 0;
static int maxline = 0;
static time_t t_start, t_last; static int report_s = 60;
static int knuth_r = 0; static unsigned long long rng = 88172645463325252ULL; static double kw, kest, ksol; static int kline;
static unsigned long long rnd(void) { rng ^= rng << 13; rng ^= rng >> 7; rng ^= rng << 17; return rng; }
static const char *NAMES = "LGABCD";
static const long MG[] = {0, 3, 12, 39, 120, 363, 1092, 3279};
#define IDX(x, y, z) (((x) * (W + 1) + (y)) * (W + 1) + (z))

static int code(char c) {
    if (c == '*') return W;
    if (c == 'F') return W;
    const char *p = strchr(NAMES, c);
    if (!p || p - NAMES >= W) { fprintf(stderr, "bad state %c\n", c); exit(2); }
    return (int)(p - NAMES);
}
static char nm(int s, int isval) { return s == W ? (isval ? 'F' : '*') : NAMES[s]; }

static void print_rule(void) {
    printf("RULE");
    for (int x = 0; x <= W; x++) for (int y = 0; y < W; y++) for (int z = 0; z <= W; z++) {
        int e = IDX(x, y, z);
        if (tab[e] >= 0) printf(" %c%c%c=%c", nm(x, 0), nm(y, 0), nm(z, 0), nm(tab[e], 1));
    }
    printf("\n");
}

static void run(int n, int t, int i);

static void solution(void) {
    if (knuth_r) ksol += kw;
    sols++;
    if (sols <= nprint) print_rule();
}

/* gap bound for stable generals: row t+1 of the line n is complete; barriers are borders and cells in state G */
static int gap_ok(int n, int tt) {
    long rho = 2L * n - 3 - tt;                 /* steps left until every cell must be G */
    if (rho <= 0) return 1;
    int last = 0;                               /* position of the last barrier (0 = left border) */
    for (int i = 1; i <= n + 1; i++) {
        int bar = (i == n + 1) || cellv[n][tt][i] == 1;
        if (bar) {
            int len = i - last - 1;             /* cells strictly between two barriers */
            if (len >= 1 && len < 8 && rho > MG[len]) return 0;
            last = i;
        }
    }
    return 1;
}

static void next_line(int n) {
    done_by_line[n]++;
    if (n > kline) kline = n;
    if (n > maxline) { maxline = n; if (!knuth_r) fprintf(stderr, "# first rule for the lines %d..%d after %lld nodes, %ld s\n", NMIN, n, nodes, (long)(time(NULL) - t_start)); if (opt_max) print_rule(); fflush(stdout); }
    if (n == N) { solution(); return; }
    int m = n + 1;
    for (int i = 0; i <= m + 1; i++) cellv[m][0][i] = (i == 0 || i == m + 1) ? W : (i == 1 ? 1 : 0);
    run(m, 0, 1);
}

/* rows 0..t of the line n are complete, and the cells 1..i-1 of the row t+1; continue from the cell i */
static void run(int n, int t, int i) {
    signed char (*c)[MAXN + 3] = cellv[n];
    for (;;) {
        if (i > n) {                                             /* the row t+1 is complete */
            if (t + 1 == 2 * n - 2) { next_line(n); return; }
            if (opt_gap && !gap_ok(n, t + 1)) { fails_by_line[n]++; return; }
            c[t + 1][0] = W; c[t + 1][n + 1] = W;
            t++; i = 1;
            continue;
        }
        int e = IDX(c[t][i - 1], c[t][i], c[t][i + 1]);
        int last = (t + 1 == 2 * n - 2);
        int v = tab[e];
        if (v >= 0) {
            if (last ? v != W : v == W) { fails_by_line[n]++; return; }
            if (!last) {
                if (opt_prefire && t + 1 == 2 * n - 3 && v != 1) { fails_by_line[n]++; return; }
                if (opt_front && i == t + 2 && i <= n - 1 && t + 1 <= N - 3 && v == 0) { fails_by_line[n]++; return; }
                if (opt_wall && v == 1 && i >= 2 && t + 1 + i <= 2 * n - 2 && t + 1 + i <= 2 * N - 4) { fails_by_line[n]++; return; }
                if (opt_chain && n > NMIN && t + 1 + i == 2 * n - 3 && i <= n - 1 && t + 1 <= 2 * (n - 1) - 3 && v == cellv[n - 1][t + 1][i]) { fails_by_line[n]++; return; }
            }
            c[t + 1][i] = (signed char)v; i++;
            continue;
        }
        /* branch */
        if (time(NULL) - t_last >= report_s) {
            t_last = time(NULL);
            fprintf(stderr, "# %ld s: %lld nodes, %lld solutions, deepest line %d, now line %d depth %d\n", (long)(t_last - t_start), nodes, sols, maxline, n, depth);
        }
        unsigned m = mask[e];
        int naux0 = naux;
        if (knuth_r) {                                           /* one random descent (Knuth's estimator) */
            int vals[MAXK + 1], cnt = 0;
            for (v = 0; v <= W; v++) {
                if (!(m >> v & 1)) continue;
                if (last ? v != W : v == W) continue;
                if (!last) {
                    if (opt_prefire && t + 1 == 2 * n - 3 && v != 1) continue;
                    if (opt_front && i == t + 2 && i <= n - 1 && t + 1 <= N - 3 && v == 0) continue;
                    if (opt_wall && v == 1 && i >= 2 && t + 1 + i <= 2 * n - 2 && t + 1 + i <= 2 * N - 4) continue;
                    if (opt_chain && n > NMIN && t + 1 + i == 2 * n - 3 && i <= n - 1 && t + 1 <= 2 * (n - 1) - 3 && v == cellv[n - 1][t + 1][i]) continue;
                }
                if (!opt_nosym && v >= 2 && v < W && v - 2 > naux0) continue;
                vals[cnt++] = v;
            }
            if (!cnt) return;
            kw *= cnt; kest += kw;
            v = vals[rnd() % (unsigned)cnt];
            if (!opt_nosym && v >= 2 && v < W && v - 2 == naux0) naux = naux0 + 1;
            tab[e] = v; nodes++; depth++;
            c[t + 1][i] = (signed char)v;
            run(n, t, i + 1);
            depth--; tab[e] = -1; naux = naux0;
            return;
        }
        for (v = 0; v <= W; v++) {
            if (!(m >> v & 1)) continue;
            if (last ? v != W : v == W) continue;
            if (!last) {
                if (opt_prefire && t + 1 == 2 * n - 3 && v != 1) continue;
                if (opt_front && i == t + 2 && i <= n - 1 && t + 1 <= N - 3 && v == 0) continue;
                if (opt_wall && v == 1 && i >= 2 && t + 1 + i <= 2 * n - 2 && t + 1 + i <= 2 * N - 4) continue;
                if (opt_chain && n > NMIN && t + 1 + i == 2 * n - 3 && i <= n - 1 && t + 1 <= 2 * (n - 1) - 3 && v == cellv[n - 1][t + 1][i]) continue;
            }
            if (!opt_nosym && v >= 2 && v < W) {
                if (v - 2 > naux0) continue;                   /* an auxiliary state before its predecessors */
                naux = (v - 2 == naux0) ? naux0 + 1 : naux0;
            }
            if (split_m > 1 && depth == split_d) {
                long long id = split_ctr++;
                if (id % split_m != split_j) { naux = naux0; continue; }
            }
            tab[e] = v; nodes++; depth++;
            c[t + 1][i] = (signed char)v;
            run(n, t, i + 1);
            depth--; tab[e] = -1; naux = naux0;
        }
        fails_by_line[n]++;                                      /* all values tried */
        return;
    }
}

static void apply_list(const char *s, int neq) {
    char buf[4096]; strncpy(buf, s, sizeof buf - 1); buf[sizeof buf - 1] = 0;
    for (char *p = strtok(buf, ","); p; p = strtok(NULL, ",")) {
        if (strlen(p) != 5 || p[3] != '=') { fprintf(stderr, "bad transition %s\n", p); exit(2); }
        int e = IDX(code(p[0]), code(p[1]), code(p[2])), d = code(p[4]);
        if (neq) mask[e] &= ~(1u << d); else mask[e] &= (1u << d);
    }
}

int main(int argc, char **argv) {
    if (argc < 3) { fprintf(stderr, "usage: fsdfs K N [options]\n"); return 2; }
    K = atoi(argv[1]); N = atoi(argv[2]); W = K - 1;
    if (K < 3 || K > MAXK || N < 2 || N > MAXN) { fprintf(stderr, "bad K or N\n"); return 2; }
    const char *setl = NULL, *neql = NULL;
    for (int a = 3; a < argc; a++) {
        if (!strcmp(argv[a], "-b1s")) opt_b1s = 1; else if (!strcmp(argv[a], "-b1w")) opt_b1w = 1;
        else if (!strcmp(argv[a], "-b3s")) opt_b3s = 1; else if (!strcmp(argv[a], "-b3w")) opt_b3w = 1;
        else if (!strcmp(argv[a], "-b4")) opt_b4 = 1; else if (!strcmp(argv[a], "-front")) opt_front = 1;
        else if (!strcmp(argv[a], "-chain")) opt_chain = 1; else if (!strcmp(argv[a], "-prefire")) opt_prefire = 1;
        else if (!strcmp(argv[a], "-wall")) opt_wall = 1; else if (!strcmp(argv[a], "-gap")) opt_gap = 1;
        else if (!strcmp(argv[a], "-max")) opt_max = 1; else if (!strcmp(argv[a], "-nosym")) opt_nosym = 1;
        else if (!strcmp(argv[a], "-print")) nprint = atoi(argv[++a]);
        else if (!strcmp(argv[a], "-nmin")) NMIN = atoi(argv[++a]);
        else if (!strcmp(argv[a], "-report")) report_s = atoi(argv[++a]);
        else if (!strcmp(argv[a], "-knuth")) { knuth_r = atoi(argv[a + 1]); rng ^= (unsigned long long)atoll(argv[a + 2]) * 0x9E3779B97F4A7C15ULL; a += 2; }
        else if (!strcmp(argv[a], "-set")) setl = argv[++a]; else if (!strcmp(argv[a], "-neq")) neql = argv[++a];
        else if (!strcmp(argv[a], "-split")) { split_d = atoi(argv[a + 1]); split_j = atoi(argv[a + 2]); split_m = atoi(argv[a + 3]); a += 3; }
        else { fprintf(stderr, "unknown option %s\n", argv[a]); return 2; }
    }
    if ((opt_prefire || opt_wall || opt_gap) && !opt_b3s) { fprintf(stderr, "-prefire, -wall and -gap need -b3s\n"); return 2; }
    if ((opt_wall || opt_gap) && !opt_b1s) { fprintf(stderr, "-wall and -gap need -b1s\n"); return 2; }
    if (opt_max && (opt_front || opt_chain || opt_wall)) { fprintf(stderr, "-max: -front, -chain and -wall are sound for a fixed N only\n"); return 2; }
    unsigned work = (1u << W) - 1, all = (1u << (W + 1)) - 1;
    for (int x = 0; x <= W; x++) for (int y = 0; y < W; y++) for (int z = 0; z <= W; z++) {
        int e = IDX(x, y, z); tab[e] = -1; mask[e] = all;
        if (x == W && z == W) { mask[e] = 0; continue; }
        int fire3 = (y == 1) && (x == 1 || x == W) && (z == 1 || z == W);
        if (opt_b3s) mask[e] = fire3 ? (1u << W) : work;
        if (opt_b3w && fire3) mask[e] = 1u << W;
        if (opt_b1s && y == 1 && !fire3) mask[e] &= 1u << 1;
        if (opt_b1w && y == 1 && x < W && z < W && !(x == 1 && z == 1)) mask[e] &= 1u << 1;
        if (opt_b4 && x == 1 && z == 1 && y != 1) mask[e] &= 1u << 1;
    }
    mask[IDX(0, 0, 0)] &= 1u; mask[IDX(0, 0, W)] &= 1u;           /* quiescence */
    if (setl) apply_list(setl, 0);
    if (neql) apply_list(neql, 1);
    tab[IDX(0, 0, 0)] = 0; tab[IDX(0, 0, W)] = 0;
    if (!(mask[IDX(0, 0, 0)] & 1u) || !(mask[IDX(0, 0, W)] & 1u)) { printf("no rule: quiescence excluded\n"); return 0; }
    t_start = t_last = time(NULL);
    int m = NMIN;
    for (int i = 0; i <= m + 1; i++) cellv[m][0][i] = (i == 0 || i == m + 1) ? W : (i == 1 ? 1 : 0);
    if (knuth_r) {
        double s1 = 0, s2 = 0, q1 = 0, q2 = 0; long long hist[MAXN + 2]; memset(hist, 0, sizeof hist);
        for (int r = 0; r < knuth_r; r++) {
            kw = 1; kest = 0; ksol = 0; kline = NMIN - 1; naux = 0; depth = 0;
            run(m, 0, 1);
            s1 += kest; s2 += kest * kest; q1 += ksol; q2 += ksol * ksol; hist[kline]++;
        }
        double R = knuth_r, mean = s1 / R, var = (s2 / R - mean * mean) / (R > 1 ? R - 1 : 1), ms = q1 / R, vs = (q2 / R - ms * ms) / (R > 1 ? R - 1 : 1);
        printf("Knuth estimate from %d random descents: %.3g nodes (standard error %.2g); %.3g solutions (standard error %.2g); %ld s\n", knuth_r, mean, var > 0 ? sqrt(var) : 0.0, ms, vs > 0 ? sqrt(vs) : 0.0, (long)(time(NULL) - t_start));
        printf("descents by the last line that they completed:");
        for (int n = NMIN - 1; n <= N; n++) if (hist[n]) printf(" %d:%lld", n, hist[n]);
        printf("\n");
        return 0;
    }
    run(m, 0, 1);
    printf("k=%d lines %d..%d:%s%s%s%s%s%s%s%s%s%s%s%s", K, NMIN, N, opt_b1s ? " b1s" : "", opt_b1w ? " b1w" : "", opt_b3s ? " b3s" : "", opt_b3w ? " b3w" : "", opt_b4 ? " b4" : "",
           opt_front ? " front" : "", opt_chain ? " chain" : "", opt_prefire ? " prefire" : "", opt_wall ? " wall" : "", opt_gap ? " gap" : "", opt_max ? " max" : "", opt_nosym ? " nosym" : "");
    if (setl) printf(" set %s", setl);
    if (neql) printf(" neq %s", neql);
    if (split_m > 1) printf(" part %d of %d at depth %d", split_j, split_m, split_d);
    printf("\nnodes %lld, solutions %lld, deepest line completed %d, %ld s\n", nodes, sols, maxline, (long)(time(NULL) - t_start));
    printf("branches that completed the line n:");
    for (int n = NMIN; n <= N; n++) printf(" %d:%lld", n, done_by_line[n]);
    printf("\n");
    return 0;
}

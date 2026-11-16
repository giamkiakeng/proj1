/* fsdfs2.c -- exhaustive backtracking search with conflict-directed backjumping for k-state rules that
 * synchronize the lines nmin..N in minimal time.  No SAT solver.
 *
 * The search is that of fsdfs.c: the lines nmin, ..., N are simulated in this order, row by row and cell by
 * cell; a transition is branched on when it is first needed; a branch fails when a cell fires before the time
 * 2n-2 or does not fire at that time.  In addition every cell carries the set of transitions on which its state
 * depends, and a failure is returned together with a set of transitions that causes it (see run()).  A branching
 * whose own transition is not in that set is left at once.  The number of solutions for the lines nmin..N is the
 * same as that of fsdfs.c (a solution is never skipped); the numbers of branches that complete a shorter line
 * are not, because subtrees without a solution are cut.
 *
 * States: 0 = L, 1 = G, 2.. = auxiliary states A, B, ...; the value k-1 is F, and as a neighbour k-1 is the border.
 * Options as in fsdfs.c:
 *   classes  -b1s -b1w -b3s -b3w -b4 -set xyz=d,... -neq xyz=d,...   (-nosym: no naming rule for the auxiliary states)
 *   pruning  -front -chain -prefire -wall -gap      (necessary conditions for a rule that synchronizes nmin..N)
 *   -cell T,I=X;...  the half-line cell (T, I) is in the state X (a condition on the rule; needs N with T+I <= 2N-2)
 *   -cellany T,I=X;...  at least one of the listed half-line cells has the listed state (cells on one anti-diagonal
 *            T+I = D <= 2N-2; checked in the line N when its anti-diagonal D is complete)
 *   -keepsym   keep the naming rule although -set, -neq, -cell or -cellany names an auxiliary state: the conditions then
 *            speak about the rule in its canonical naming (the first auxiliary state that occurs is called A, ...)
 *   -split D J M   the part J of M: a branch at depth D (D transitions chosen) belongs to the part given by a hash of
 *            its transitions; the numbers of solutions of the M parts add up to the number of all solutions
 *   -nmin M, -print M, -report S
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define MAXN 48
#define MAXK 7
static int K, W, N, NMIN = 2;          /* W = K-1 working states; F = W as a value; border = W as a neighbour */
static int tab[(MAXK) * (MAXK) * (MAXK)];
static unsigned mask[(MAXK) * (MAXK) * (MAXK)];
static signed char cellv[MAXN + 2][2 * MAXN + 2][MAXN + 3];
static int opt_b1s, opt_b1w, opt_b3s, opt_b3w, opt_b4, opt_front, opt_chain, opt_prefire, opt_wall, opt_gap, opt_nosym, opt_keepsym;
static long long nodes, sols, jumps, fails_by_line[MAXN + 2], done_by_line[MAXN + 2];
static int nprint = 0, naux = 0, depth = 0;
static int maxline = 0;
static int split_d = 0, split_j = 0, split_m = 1; static unsigned long long hpath = 1469598103934665603ULL;
static inline unsigned long long hmix(unsigned long long h) { h ^= h >> 31; h *= 0x9E3779B97F4A7C15ULL; return h >> 33; }
static time_t t_start, t_last; static int report_s = 60;
static const char *NAMES = "LGABCD";
static const long MG[] = {0, 3, 12, 39, 120, 363, 1092, 3279};
#define IDX(x, y, z) (((x) * (W + 1) + (y)) * (W + 1) + (z))
typedef struct { unsigned long long w[4]; } bs;                 /* a set of transitions */
static const bs BS0 = {{0, 0, 0, 0}}, BSALL = {{~0ULL, ~0ULL, ~0ULL, ~0ULL}};
static inline bs bor(bs a, bs b) { a.w[0] |= b.w[0]; a.w[1] |= b.w[1]; a.w[2] |= b.w[2]; a.w[3] |= b.w[3]; return a; }
static inline bs bset(bs a, int e) { a.w[e >> 6] |= 1ULL << (e & 63); return a; }
static inline bs bclr(bs a, int e) { a.w[e >> 6] &= ~(1ULL << (e & 63)); return a; }
static inline int bhas(bs a, int e) { return (int)(a.w[e >> 6] >> (e & 63) & 1); }
static bs dep[MAXN + 2][2 * MAXN + 2][MAXN + 3];                 /* the transitions on which a cell depends */
static signed char need[2 * MAXN + 2][MAXN + 3];                 /* -cell: required state of a half-line cell, or -1 */
static int any_t[64], any_i[64], any_x[64], n_any = 0, any_diag = -1;

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
    printf("\n"); fflush(stdout);
}

static bs run(int n, int t, int i);

/* gap bound for stable generals: row tt of the line n is complete; barriers are borders and cells in state G.
 * On a violation *why receives the transitions on which the two barriers depend. */
static int gap_ok(int n, int tt, bs *why) {
    long rho = 2L * n - 3 - tt;                 /* steps left until every cell must be G */
    if (rho <= 0) return 1;
    int last = 0;                               /* position of the last barrier (0 = left border) */
    for (int i = 1; i <= n + 1; i++) {
        int bar = (i == n + 1) || cellv[n][tt][i] == 1;
        if (bar) {
            int len = i - last - 1;             /* cells strictly between two barriers */
            if (len >= 1 && len < 8 && rho > MG[len]) {
                *why = BS0;
                if (last >= 1) *why = bor(*why, dep[n][tt][last]);
                if (i <= n) *why = bor(*why, dep[n][tt][i]);
                return 0;
            }
            last = i;
        }
    }
    return 1;
}

static bs next_line(int n) {
    done_by_line[n]++;
    if (n > maxline) { maxline = n; fprintf(stderr, "# first rule for the lines %d..%d after %lld nodes, %ld s\n", NMIN, n, nodes, (long)(time(NULL) - t_start)); }
    if (n == N) {
        if (split_m > 1 && depth < split_d && split_j != 0) return BSALL;      /* counted by the part 0 */
        sols++; if (sols <= nprint) print_rule(); return BSALL;
    }
    int m = n + 1;
    for (int i = 0; i <= m + 1; i++) { cellv[m][0][i] = (i == 0 || i == m + 1) ? W : (i == 1 ? 1 : 0); dep[m][0][i] = BS0; }
    return run(m, 0, 1);
}

/* Rows 0..t of the line n are complete, and the cells 1..i-1 of the row t+1; continue from the cell i.
 * The value returned is a set C of transitions such that the subtree below this point holds no solution as long
 * as the transitions of C keep their present values (a nogood); it is the set of all transitions if a solution
 * was found below.  Every cell carries the set of transitions on which its state depends.  A failure at a cell
 * returns the dependencies of the cells that the violated condition mentions.  At a branching on the transition
 * e: if a value of e fails with a set that does not contain e, the failure does not depend on the choice, and
 * the branching returns that set at once (backjump); otherwise it returns the union of the sets of all values,
 * without e, together with the dependencies P of the three cells above (they are the reason why e is needed at
 * this place and time, on which all exclusions by position rest).  A value excluded by the naming rule needs no
 * reason: exchanging two unused names maps its subtree onto that of the admitted new name and fixes all earlier
 * transitions. */
static bs run(int n, int t, int i) {
    signed char (*c)[MAXN + 3] = cellv[n];
    bs (*d)[MAXN + 3] = dep[n];
    for (;;) {
        if (i > n) {                                             /* the row t+1 is complete */
            if (t + 1 == 2 * n - 2) return next_line(n);
            if (opt_gap) { bs why; if (!gap_ok(n, t + 1, &why)) { fails_by_line[n]++; return why; } }
            c[t + 1][0] = W; c[t + 1][n + 1] = W; d[t + 1][0] = BS0; d[t + 1][n + 1] = BS0;
            t++; i = 1;
            continue;
        }
        int e = IDX(c[t][i - 1], c[t][i], c[t][i + 1]);
        bs P = bor(bor(d[t][i - 1], d[t][i]), d[t][i + 1]);
        bs Pe = bset(P, e);
        int last = (t + 1 == 2 * n - 2);
        int v = tab[e];
        int halfline = (t + 1 + i <= 2 * n - 2);                 /* the cell agrees with the half-line */
        int is_front = opt_front && i == t + 2 && i <= n - 1 && t + 1 <= N - 3;
        int is_wall = opt_wall && i >= 2 && halfline && t + 1 + i <= 2 * N - 4;
        int is_chain = opt_chain && n > NMIN && t + 1 + i == 2 * n - 3 && i <= n - 1 && t + 1 <= 2 * (n - 1) - 3;
        int is_prefire = opt_prefire && t + 1 == 2 * n - 3;
        int want = halfline ? need[t + 1][i] : -1;               /* -cell */
        /* -cellany: in the line N, when the last listed cell of the anti-diagonal is reached and none matched */
        int any_last = 0;
        if (n_any && n == N && halfline && t + 1 + i == any_diag && t + 1 == any_t[n_any - 1] && i == any_i[n_any - 1]) any_last = 1;
        if (v >= 0) {
            if (last ? v != W : v == W) { fails_by_line[n]++; return Pe; }
            if (!last) {
                if (is_prefire && v != 1) { fails_by_line[n]++; return Pe; }
                if (is_front && v == 0) { fails_by_line[n]++; return Pe; }
                if (is_wall && v == 1) { fails_by_line[n]++; return Pe; }
                if (is_chain && v == cellv[n - 1][t + 1][i]) { fails_by_line[n]++; return bor(Pe, dep[n - 1][t + 1][i]); }
                if (want >= 0 && v != want) { fails_by_line[n]++; return Pe; }
                if (any_last) {
                    int hit = (v == any_x[n_any - 1]); bs why = Pe;
                    for (int j = 0; j < n_any - 1 && !hit; j++) { if (c[any_t[j]][any_i[j]] == any_x[j]) hit = 1; else why = bor(why, d[any_t[j]][any_i[j]]); }
                    if (!hit) { fails_by_line[n]++; return why; }
                }
            }
            c[t + 1][i] = (signed char)v; d[t + 1][i] = Pe; i++;
            continue;
        }
        /* branch */
        if (time(NULL) - t_last >= report_s) {
            t_last = time(NULL);
            fprintf(stderr, "# %ld s: %lld nodes, %lld backjumps, %lld solutions, deepest line %d, now line %d depth %d\n", (long)(t_last - t_start), nodes, jumps, sols, maxline, n, depth);
        }
        unsigned m = mask[e];
        int naux0 = naux;
        bs acc = P;
        if (is_chain) acc = bor(acc, dep[n - 1][t + 1][i]);
        int any_hit_before = 0;
        if (any_last) {
            for (int j = 0; j < n_any - 1; j++) { if (c[any_t[j]][any_i[j]] == any_x[j]) any_hit_before = 1; else acc = bor(acc, d[any_t[j]][any_i[j]]); }
        }
        for (v = 0; v <= W; v++) {
            if (!(m >> v & 1)) continue;
            if (last ? v != W : v == W) continue;
            if (!last) {
                if (is_prefire && v != 1) continue;
                if (is_front && v == 0) continue;
                if (is_wall && v == 1) continue;
                if (is_chain && v == cellv[n - 1][t + 1][i]) continue;
                if (want >= 0 && v != want) continue;
                if (any_last && !any_hit_before && v != any_x[n_any - 1]) continue;
            }
            if (!opt_nosym && v >= 2 && v < W) {
                if (v - 2 > naux0) continue;                   /* an auxiliary state before its predecessors */
                naux = (v - 2 == naux0) ? naux0 + 1 : naux0;
            }
            unsigned long long h0 = hpath;
            hpath = hpath * 1099511628211ULL + (unsigned)(e * 8 + v + 1);
            if (split_m > 1 && depth + 1 == split_d && (int)(hmix(hpath) % (unsigned)split_m) != split_j) {
                hpath = h0; naux = naux0; acc = BSALL;          /* another part searches this branch: nothing is known about it here */
                continue;
            }
            tab[e] = v; nodes++; depth++;
            c[t + 1][i] = (signed char)v; d[t + 1][i] = Pe;
            bs r = run(n, t, i + 1);
            depth--; tab[e] = -1; naux = naux0; hpath = h0;
            if (!bhas(r, e)) { jumps++; return r; }             /* the failure does not depend on this choice */
            acc = bor(acc, r);
        }
        fails_by_line[n]++;                                      /* all values tried */
        return bclr(acc, e);
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

static void cell_list(const char *s, int any) {
    char buf[4096]; strncpy(buf, s, sizeof buf - 1); buf[sizeof buf - 1] = 0;
    for (char *p = strtok(buf, ";"); p; p = strtok(NULL, ";")) {
        int t, i; char x;
        if (sscanf(p, "%d,%d=%c", &t, &i, &x) != 3) { fprintf(stderr, "bad cell %s\n", p); exit(2); }
        if (t + i > 2 * N - 2 || i < 1 || i > t + 1) { fprintf(stderr, "cell %s is not a half-line cell of the line N\n", p); exit(2); }
        if (!any) need[t][i] = (signed char)code(x);
        else {
            if (any_diag >= 0 && any_diag != t + i) { fprintf(stderr, "-cellany: cells on one anti-diagonal only\n"); exit(2); }
            if (n_any && t <= any_t[n_any - 1]) { fprintf(stderr, "-cellany: list the cells by increasing time\n"); exit(2); }
            any_diag = t + i; any_t[n_any] = t; any_i[n_any] = i; any_x[n_any] = code(x); n_any++;
        }
    }
}

int main(int argc, char **argv) {
    if (argc < 3) { fprintf(stderr, "usage: fsdfs2 K N [options]\n"); return 2; }
    K = atoi(argv[1]); N = atoi(argv[2]); W = K - 1;
    if (K < 3 || K > 6 || N < 2 || N > MAXN) { fprintf(stderr, "bad K or N (K <= 6: the sets of transitions have 256 bits)\n"); return 2; }
    const char *setl = NULL, *neql = NULL, *celll = NULL, *anyl = NULL;
    for (int a = 3; a < argc; a++) {
        if (!strcmp(argv[a], "-b1s")) opt_b1s = 1; else if (!strcmp(argv[a], "-b1w")) opt_b1w = 1;
        else if (!strcmp(argv[a], "-b3s")) opt_b3s = 1; else if (!strcmp(argv[a], "-b3w")) opt_b3w = 1;
        else if (!strcmp(argv[a], "-b4")) opt_b4 = 1; else if (!strcmp(argv[a], "-front")) opt_front = 1;
        else if (!strcmp(argv[a], "-chain")) opt_chain = 1; else if (!strcmp(argv[a], "-prefire")) opt_prefire = 1;
        else if (!strcmp(argv[a], "-wall")) opt_wall = 1; else if (!strcmp(argv[a], "-gap")) opt_gap = 1;
        else if (!strcmp(argv[a], "-nosym")) opt_nosym = 1;
        else if (!strcmp(argv[a], "-keepsym")) opt_keepsym = 1;
        else if (!strcmp(argv[a], "-print")) nprint = atoi(argv[++a]);
        else if (!strcmp(argv[a], "-nmin")) NMIN = atoi(argv[++a]);
        else if (!strcmp(argv[a], "-report")) report_s = atoi(argv[++a]);
        else if (!strcmp(argv[a], "-set")) setl = argv[++a]; else if (!strcmp(argv[a], "-neq")) neql = argv[++a];
        else if (!strcmp(argv[a], "-cell")) celll = argv[++a]; else if (!strcmp(argv[a], "-cellany")) anyl = argv[++a];
        else if (!strcmp(argv[a], "-split")) { split_d = atoi(argv[a + 1]); split_j = atoi(argv[a + 2]); split_m = atoi(argv[a + 3]); a += 3; }
        else { fprintf(stderr, "unknown option %s\n", argv[a]); return 2; }
    }
    if ((opt_prefire || opt_wall || opt_gap) && !opt_b3s) { fprintf(stderr, "-prefire, -wall and -gap need -b3s\n"); return 2; }
    if ((opt_wall || opt_gap) && !opt_b1s) { fprintf(stderr, "-wall and -gap need -b1s\n"); return 2; }
    {   /* the naming rule assumes a class that is invariant under renaming the auxiliary states */
        const char *ls[4] = {setl, neql, celll, anyl};
        for (int j = 0; j < 4; j++) if (ls[j] && strpbrk(ls[j], "ABCD") && !opt_nosym && !opt_keepsym) { opt_nosym = 1; fprintf(stderr, "# an option names an auxiliary state: the naming rule is switched off (-nosym); -keepsym keeps it\n"); }
    }
    memset(need, -1, sizeof need);
    if (celll) cell_list(celll, 0);
    if (anyl) cell_list(anyl, 1);
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
    if (!(mask[IDX(0, 0, 0)] & 1u) || !(mask[IDX(0, 0, W)] & 1u)) { printf("no rule: quiescence excluded\n"); return 0; }
    tab[IDX(0, 0, 0)] = 0; tab[IDX(0, 0, W)] = 0;
    t_start = t_last = time(NULL);
    int m = NMIN;
    for (int i = 0; i <= m + 1; i++) { cellv[m][0][i] = (i == 0 || i == m + 1) ? W : (i == 1 ? 1 : 0); dep[m][0][i] = BS0; }
    run(m, 0, 1);
    printf("k=%d lines %d..%d (backjumping):%s%s%s%s%s%s%s%s%s%s%s", K, NMIN, N, opt_b1s ? " b1s" : "", opt_b1w ? " b1w" : "", opt_b3s ? " b3s" : "", opt_b3w ? " b3w" : "", opt_b4 ? " b4" : "",
           opt_front ? " front" : "", opt_chain ? " chain" : "", opt_prefire ? " prefire" : "", opt_wall ? " wall" : "", opt_gap ? " gap" : "", opt_nosym ? " nosym" : "");
    if (setl) printf(" set %s", setl);
    if (neql) printf(" neq %s", neql);
    if (celll) printf(" cell %s", celll);
    if (anyl) printf(" cellany %s", anyl);
    if (split_m > 1) printf(" part %d of %d at depth %d", split_j, split_m, split_d);
    printf("\nnodes %lld, backjumps %lld, solutions %lld, deepest line completed %d, %ld s\n", nodes, jumps, sols, maxline, (long)(time(NULL) - t_start));
    printf("branches that completed the line n (not all are visited):");
    for (int n = NMIN; n <= N; n++) printf(" %d:%lld", n, done_by_line[n]);
    printf("\n");
    return 0;
}

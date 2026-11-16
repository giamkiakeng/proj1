/* fscount.c -- estimates of the numbers c_n of k-state rules that synchronize all lines nmin..n in minimal time,
 * counted up to the transitions that these lines do not use (the numbers that fsdfs.c computes exactly).
 *
 * Method (sequential importance sampling with resampling, level by level).  A pool P_n holds partial rules that
 * synchronize nmin..n, each with a weight, such that the sum of the weights is an unbiased estimate of c_n.  For
 * the next level, M trials are made: a trial takes a rule of P_n uniformly at random, simulates the line n+1 and
 * chooses a uniformly random admissible value for every transition that is not yet defined (the search tree of
 * fsdfs.c: a value is admissible if the class allows it, if it is F exactly at the time 2n-2, and by the naming
 * rule for the auxiliary states).  If the line is synchronized, the extended rule enters P_{n+1} with the weight
 * (weight of the parent) * |P_n| * (product of the numbers of admissible values) / M.  Then the sum of the weights
 * of P_{n+1} is an unbiased estimate of c_{n+1} (the pools are random, so the errors of the levels accumulate).
 * R independent runs give a mean and a standard error for every n.  P_{nmin-1} is the empty rule with weight 1.
 *
 * usage: fscount K N M R SEED [-nmin n0] [-b1s] [-b1w] [-b3s] [-b3w] [-b4] [-set xyz=d,...] [-neq xyz=d,...] [-nosym] [-cap C]
 *   -dump FILE L: the rules of the pools of the levels n >= L are written to FILE (at most 200 per pool).
 *   M trials per level, at most C rules kept per pool (default M; a pool larger than C is thinned uniformly and the
 *   weights are multiplied by the inverse of the fraction kept).  States: L G A B C D, F fires, * is the border.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#define MAXN 40
#define MAXK 7
#define NE (MAXK * MAXK * MAXK)
static int K, W, N, NMIN = 2;
static unsigned mask[NE];
static signed char tab[NE];
static int opt_nosym;
static unsigned long long rng = 88172645463325252ULL;
static FILE *dumpf = NULL; static int dump_from = 0;
static unsigned long long rnd(void) { rng ^= rng << 13; rng ^= rng >> 7; rng ^= rng << 17; return rng; }
static const char *NAMES = "LGABCD";
#define IDX(x, y, z) (((x) * (W + 1) + (y)) * (W + 1) + (z))
typedef struct { signed char t[NE]; signed char naux; double w; } rule;

static int code(char c) {
    if (c == '*' || c == 'F') return W;
    const char *p = strchr(NAMES, c);
    if (!p || p - NAMES >= W) { fprintf(stderr, "bad state %c\n", c); exit(2); }
    return (int)(p - NAMES);
}
static void apply_list(const char *s, int neq) {
    char buf[4096]; strncpy(buf, s, sizeof buf - 1); buf[sizeof buf - 1] = 0;
    for (char *p = strtok(buf, ","); p; p = strtok(NULL, ",")) {
        if (strlen(p) != 5 || p[3] != '=') { fprintf(stderr, "bad transition %s\n", p); exit(2); }
        int e = IDX(code(p[0]), code(p[1]), code(p[2])), d = code(p[4]);
        if (neq) mask[e] &= ~(1u << d); else mask[e] &= (1u << d);
    }
}

/* one random completion of the line n from the rule in tab[] (naux auxiliary states used); returns the product of
 * the numbers of admissible values, or 0 if the line is not synchronized */
static double descend(int n, int *naux) {
    static signed char row[2][MAXN + 3];
    double b = 1;
    int cur = 0;
    for (int i = 0; i <= n + 1; i++) row[0][i] = (signed char)((i == 0 || i == n + 1) ? W : (i == 1 ? 1 : 0));
    for (int t = 0; t < 2 * n - 2; t++) {
        signed char *c = row[cur], *d = row[cur ^ 1];
        int last = (t + 1 == 2 * n - 2);
        d[0] = (signed char)W; d[n + 1] = (signed char)W;
        for (int i = 1; i <= n; i++) {
            int e = IDX(c[i - 1], c[i], c[i + 1]);
            int v = tab[e];
            if (v < 0) {
                int vals[MAXK + 1], cnt = 0;
                unsigned m = mask[e];
                for (int u = 0; u <= W; u++) {
                    if (!(m >> u & 1)) continue;
                    if (last ? u != W : u == W) continue;
                    if (!opt_nosym && u >= 2 && u < W && u - 2 > *naux) continue;
                    vals[cnt++] = u;
                }
                if (!cnt) return 0;
                v = vals[rnd() % (unsigned)cnt];
                b *= cnt;
                if (!opt_nosym && v >= 2 && v < W && v - 2 == *naux) (*naux)++;
                tab[e] = (signed char)v;
            } else if (last ? v != W : v == W) return 0;
            d[i] = (signed char)v;
        }
        cur ^= 1;
    }
    return b;
}

int main(int argc, char **argv) {
    if (argc < 6) { fprintf(stderr, "usage: fscount K N M R SEED [options]\n"); return 2; }
    K = atoi(argv[1]); N = atoi(argv[2]); W = K - 1;
    long M = atol(argv[3]); int R = atoi(argv[4]); long cap = M;
    rng ^= (unsigned long long)atoll(argv[5]) * 0x9E3779B97F4A7C15ULL;
    if (K < 3 || K > MAXK || N < 2 || N > MAXN) { fprintf(stderr, "bad K or N\n"); return 2; }
    int b1s = 0, b1w = 0, b3s = 0, b3w = 0, b4 = 0; const char *setl = NULL, *neql = NULL;
    for (int a = 6; a < argc; a++) {
        if (!strcmp(argv[a], "-b1s")) b1s = 1; else if (!strcmp(argv[a], "-b1w")) b1w = 1;
        else if (!strcmp(argv[a], "-b3s")) b3s = 1; else if (!strcmp(argv[a], "-b3w")) b3w = 1;
        else if (!strcmp(argv[a], "-b4")) b4 = 1; else if (!strcmp(argv[a], "-nosym")) opt_nosym = 1;
        else if (!strcmp(argv[a], "-nmin")) NMIN = atoi(argv[++a]);
        else if (!strcmp(argv[a], "-cap")) cap = atol(argv[++a]);
        else if (!strcmp(argv[a], "-dump")) { dumpf = fopen(argv[a + 1], "w"); dump_from = atoi(argv[a + 2]); a += 2; if (!dumpf) { fprintf(stderr, "cannot write the dump file\n"); return 2; } }
        else if (!strcmp(argv[a], "-set")) setl = argv[++a]; else if (!strcmp(argv[a], "-neq")) neql = argv[++a];
        else { fprintf(stderr, "unknown option %s\n", argv[a]); return 2; }
    }
    unsigned work = (1u << W) - 1, all = (1u << (W + 1)) - 1;
    for (int x = 0; x <= W; x++) for (int y = 0; y < W; y++) for (int z = 0; z <= W; z++) {
        int e = IDX(x, y, z); mask[e] = all;
        if (x == W && z == W) { mask[e] = 0; continue; }
        int fire3 = (y == 1) && (x == 1 || x == W) && (z == 1 || z == W);
        if (b3s) mask[e] = fire3 ? (1u << W) : work;
        if (b3w && fire3) mask[e] = 1u << W;
        if (b1s && y == 1 && !fire3) mask[e] &= 1u << 1;
        if (b1w && y == 1 && x < W && z < W && !(x == 1 && z == 1)) mask[e] &= 1u << 1;
        if (b4 && x == 1 && z == 1 && y != 1) mask[e] &= 1u << 1;
    }
    mask[IDX(0, 0, 0)] &= 1u; mask[IDX(0, 0, W)] &= 1u;
    if (setl) apply_list(setl, 0);
    if (neql) apply_list(neql, 1);
    rule *pool = malloc(sizeof(rule) * (size_t)(cap + 1)), *next = malloc(sizeof(rule) * (size_t)(cap + 1));
    if (!pool || !next) { fprintf(stderr, "out of memory\n"); return 1; }
    static double s1[MAXN + 2], s2[MAXN + 2]; static long zero[MAXN + 2];
    for (int r = 0; r < R; r++) {
        long np = 1;
        memset(pool[0].t, -1, NE); pool[0].t[IDX(0, 0, 0)] = 0; pool[0].t[IDX(0, 0, W)] = 0; pool[0].naux = 0; pool[0].w = 1;
        for (int n = NMIN; n <= N; n++) {
            long nn = 0, seen = 0; double tot = 0;
            if (np > 0) for (long j = 0; j < M; j++) {
                rule *p = &pool[rnd() % (unsigned long long)np];
                memcpy(tab, p->t, NE);
                int naux = p->naux;
                double b = descend(n, &naux);
                if (b == 0) continue;
                double w = p->w * (double)np * b / (double)M;
                tot += w; seen++;
                /* reservoir of at most cap rules, uniform among the successful trials */
                long slot = -1;
                if (nn < cap) slot = nn++;
                else { unsigned long long q = rnd() % (unsigned long long)seen; if (q < (unsigned long long)cap) slot = (long)q; }
                if (slot >= 0) { memcpy(next[slot].t, tab, NE); next[slot].naux = (signed char)naux; next[slot].w = w; }
            }
            if (seen > nn)                           /* thinned uniformly: every success is kept with probability nn/seen */
                for (long j = 0; j < nn; j++) next[j].w *= (double)seen / (double)nn;
            if (dumpf && n >= dump_from) {              /* the rules of the pool: they synchronize the lines nmin..n */
                for (long j = 0; j < nn && j < 200; j++) {
                    fprintf(dumpf, "RULE run %d lines %d..%d:", r, NMIN, n);
                    for (int x = 0; x <= W; x++) for (int y = 0; y < W; y++) for (int z = 0; z <= W; z++) {
                        int e = IDX(x, y, z);
                        if (next[j].t[e] >= 0) fprintf(dumpf, " %c%c%c=%c", x == W ? '*' : NAMES[x], NAMES[y], z == W ? '*' : NAMES[z], next[j].t[e] == W ? 'F' : NAMES[(int)next[j].t[e]]);
                    }
                    fprintf(dumpf, "\n");
                }
                fflush(dumpf);
            }
            s1[n] += tot; s2[n] += tot * tot; if (tot == 0) zero[n]++;
            rule *tmp = pool; pool = next; next = tmp; np = nn;
        }
    }
    printf("k=%d lines %d..n, %ld trials per level, %d runs%s%s%s%s%s%s", K, NMIN, M, R, b1s ? " b1s" : "", b1w ? " b1w" : "", b3s ? " b3s" : "", b3w ? " b3w" : "", b4 ? " b4" : "", opt_nosym ? " nosym" : "");
    if (setl) printf(" set %s", setl);
    if (neql) printf(" neq %s", neql);
    printf("\n  n   estimate of c_n   standard error   runs with an empty pool\n");
    for (int n = NMIN; n <= N; n++) {
        double m = s1[n] / R, v = R > 1 ? (s2[n] / R - m * m) / (R - 1) : 0;
        printf("%3d   %14.4g   %14.2g   %ld of %d\n", n, m, v > 0 ? sqrt(v) : 0.0, zero[n], R);
    }
    return 0;
}

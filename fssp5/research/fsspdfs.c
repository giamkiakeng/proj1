/*
 * fsspdfs.c -- exhaustive depth-first search for k-state minimal-time FSSP tables (Balzer/Sanders style)
 *
 * The table is filled lazily: all lines are simulated in time order (time-major, the half-line
 * C_inf first, then the reflected triangles R_n), and when a cell needs a neighbourhood whose entry is
 * not yet defined, the search branches on its value: F if the cell is in a firing row (time 2n-2 of
 * a complete line), a working state otherwise.  A branch dies when a defined entry gives F at a
 * non-firing cell or a working state at a firing cell, when the half-line would fire, or when a
 * return-chain cell of a complete line n equals the half-line's cell (Lemma 2.3 of the note).
 *
 * Lines 2..N are complete (they must fire exactly at 2n-2); lines N+1..N1 are early lines, simulated
 * up to relative time T only (no cell may fire there).  The quiescent entries LLL and LL* are L.
 * The two auxiliary states A, B are interchangeable: the first of them to be assigned is A.
 *
 * usage: fsspdfs K N [N1 T] [--print P] [--maxnodes M] [--plain]
 *   --plain: the lines 2..N alone (no return chain for line N, half-line only to t + i = 2N1 - 2);
 *            otherwise also the consequences of line N+1 not firing early at its left cells
 *   prints the number of nodes per depth (number of defined entries), the number of complete
 *   assignments (tables restricted to the entries used), and the first P of them
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAXN 128
#define MAXT 2 * MAXN
#define STAR 0
#define L 1
#define G 2
/* working states 1..K-1, F = K, undefined = 0 */

static int K, N, N1, T, F;
static int tab[8][8][8];                  /* tab[x][y][z], x,z in 0..K-1 (0 = border), y in 1..K-1 */
static unsigned char H[MAXT][MAXT];       /* half-line C_inf(t, i), i >= 1 */
static unsigned char R[MAXN][MAXT][MAXN]; /* R[n][t][i] for cells of R_n */
static int hmax;                          /* half-line encoded for t + i <= hmax */
static int tlast[MAXN];                   /* last time simulated for line n */

typedef struct { short n, t, i; } Cell;   /* n = 0: half-line cell */
static Cell *cells;
static int ncells;

static long long nodes, sols, maxnodes = -1;
static long long depthcount[256];
static int depth, seenAB, printmax, plain;
static char sym[] = "*LGABCDEF";

static int symch(int v) { return v == F ? 'F' : sym[v]; }

static void print_table(void)
{
    printf("TABLE");
    for (int x = 0; x < K; x++)
        for (int y = 1; y < K; y++)
            for (int z = 0; z < K; z++)
                if (tab[x][y][z])
                    printf(" %c%c%c>%c", sym[x], sym[y], sym[z], symch(tab[x][y][z]));
    printf("\n");
}

static inline int getH(int t, int i)
{
    if (i == 0)
        return STAR;
    if (i > t + 1)
        return L;
    return H[t][i];
}

static inline int inR(int n, int t, int i) { return t + i >= 2 * n - 1 && t >= n - 1 && i <= n && i >= 1; }

static inline int getR(int n, int t, int i)
{
    if (i == 0 || i == n + 1)
        return STAR;
    if (inR(n, t, i))
        return R[n][t][i];
    return getH(t, i);
}

static void dfs(int p);

/* compute cells from position p; on an undefined entry, branch */
static void dfs(int p)
{
    nodes++;
    if (depth < 256)
        depthcount[depth]++;
    if (maxnodes >= 0 && nodes > maxnodes)
        return;
    for (; p < ncells; p++) {
        Cell c = cells[p];
        int x, y, z, fire;
        if (c.n == 0) {
            x = getH(c.t - 1, c.i - 1);
            y = getH(c.t - 1, c.i);
            z = getH(c.t - 1, c.i + 1);
            fire = 0;
        } else {
            x = getR(c.n, c.t - 1, c.i - 1);
            y = getR(c.n, c.t - 1, c.i);
            z = getR(c.n, c.t - 1, c.i + 1);
            fire = c.n <= N && c.t == 2 * c.n - 2;
        }
        int v = tab[x][y][z];
        if (v == 0) {
            if (fire) {
                tab[x][y][z] = F;
                depth++;
                dfs(p);
                depth--;
                tab[x][y][z] = 0;
            } else {
                int top = seenAB ? K - 1 : (K - 1 >= 3 ? 3 : K - 1);
                for (int w = 1; w <= top; w++) {
                    int was = seenAB;
                    if (w >= 3)
                        seenAB = 1;
                    tab[x][y][z] = w;
                    depth++;
                    dfs(p);
                    depth--;
                    tab[x][y][z] = 0;
                    seenAB = was;
                }
            }
            return;
        }
        if ((v == F) != fire)
            return;
        if (c.n == 0) {
            H[c.t][c.i] = v;
        } else {
            /* return chain of a complete line differs from the half-line (Lemma 2.3) */
            if (c.n <= N && c.t + c.i == 2 * c.n - 1 && !fire && v == getH(c.t, c.i) && !(plain && c.n == N))
                return;
            R[c.n][c.t][c.i] = v;
        }
    }
    sols++;
    if (sols <= printmax)
        print_table();
}

int main(int argc, char **argv)
{
    if (argc < 3) {
        fprintf(stderr, "usage: fsspdfs K N [N1 T] [--print P] [--maxnodes M]\n");
        return 1;
    }
    K = atoi(argv[1]);
    N = atoi(argv[2]);
    N1 = N;
    T = 0;
    int a = 3;
    if (argc > 4 && argv[3][0] != '-') {
        N1 = atoi(argv[3]);
        T = atoi(argv[4]);
        a = 5;
    }
    for (; a < argc; a++) {
        if (!strcmp(argv[a], "--print"))
            printmax = atoi(argv[++a]);
        else if (!strcmp(argv[a], "--maxnodes"))
            maxnodes = atoll(argv[++a]);
        else if (!strcmp(argv[a], "--plain"))
            plain = 1;
    }
    F = K;
    for (int n = 2; n <= N1; n++)
        tlast[n] = n <= N ? 2 * n - 2 : n - 1 + T;
    int tmax = plain ? 2 * N - 2 : 2 * N - 1;             /* half-line cell (2N-2, 1) is read by the return chains */
    for (int n = 2; n <= N1; n++)
        if (tlast[n] > tmax)
            tmax = tlast[n];
    /* the half-line is needed on t + i <= 2n - 2 for every line n, at times <= tlast[n] */
    hmax = 2 * N1 - 2 > 2 * N ? 2 * N1 - 2 : 2 * N;     /* the return chain of line N reads t + i = 2N - 1 */
    if (plain && hmax > 2 * N1 - 2)
        hmax = 2 * N1 - 2;                                /* --plain: half-line only as far as the lines read it */
    if (tmax + 2 >= MAXT || N1 + 2 >= MAXN) {
        fprintf(stderr, "too large\n");
        return 1;
    }
    memset(tab, 0, sizeof tab);
    tab[L][L][L] = L;
    tab[L][L][STAR] = L;
    /* time 0 */
    memset(H, L, sizeof H);
    H[0][1] = G;
    cells = malloc(sizeof(Cell) * 4000000);
    ncells = 0;
    for (int t = 1; t <= tmax; t++) {
        for (int i = 1; i <= t + 1 && t + i <= hmax; i++)
            cells[ncells++] = (Cell){0, (short)t, (short)i};
        for (int n = N1; n >= 2; n--) {
            if (t > tlast[n])
                continue;
            for (int i = 1; i <= n; i++)
                if (inR(n, t, i))
                    cells[ncells++] = (Cell){(short)n, (short)t, (short)i};
        }
    }
    fprintf(stderr, "K=%d N=%d N1=%d T=%d cells=%d\n", K, N, N1, T, ncells);
    dfs(0);
    printf("nodes %lld solutions %lld%s\n", nodes, sols, (maxnodes >= 0 && nodes > maxnodes) ? " (node limit)" : "");
    for (int d = 0; d < 256; d++)
        if (depthcount[d])
            printf("depth %d nodes %lld\n", d, depthcount[d]);
    return 0;
}

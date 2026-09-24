/*
 * fsspdfs.c -- exhaustive depth-first enumeration of k-state rules that
 * synchronize every line of length 2..N in minimal time 2n-2.
 *
 * The rule is filled lazily: the space-time diagrams are evaluated along a
 * fixed "program" of cell computations; whenever a transition that has not
 * been fixed yet is needed, the search branches over all admissible values.
 * The program evaluates the half-line diagram C_inf along anti-diagonals and,
 * as soon as the part of C_inf that a line of length n depends on is known,
 * the reflected triangle R_n of that line (see gencnf.py for the geometry).
 *
 * Symmetry: auxiliary states are introduced in increasing order along the
 * search path (a value a>=3 may be used only after a-1 has been used).
 *
 * usage: fsspdfs k N [-p prefixdepth part nparts] [-s] [-q]
 *   -s  print every solution (restricted to the entries that are used)
 *   -p  split: only explore the subtrees whose first `prefixdepth`
 *       branching choices have index == part (mod nparts)
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAXK 8
#define BND 7
enum { NONF = 0, FIRE = 1, DIFF = 2, FRONT = 3 };

static int K, N, WS; /* WS = number of working states = K-1 */
static int FST;      /* fire state code = K-1 */
static int tab[8][8][8];
static int *cell;    /* cell values */
typedef struct { int x, a, b, c, kind; } op_t;
static op_t *prog;
static int nprog;
static long long nodes, sols;
static int print_sols;
static int use_diff = 1, use_front = 1;
static int split_depth = 0, split_part = 0, split_n = 1;
static int cube_depth = -1; static long long ncubes;
static int setorder[512][3]; static int nset;
static long long split_counter = 0;
static int maxaux; /* highest auxiliary state used so far (1 if none) */
static long long *hist; /* depth histogram of dead ends by program position */

static int ncell, cap;
static int newcell(int v) {
  if (ncell == cap) { cap = cap ? 2 * cap : 1024; cell = realloc(cell, cap * sizeof(int)); }
  cell[ncell] = v;
  return ncell++;
}
static int pcap;
static void emit(int x, int a, int b, int c, int kind) {
  if (nprog == pcap) { pcap = pcap ? 2 * pcap : 1024; prog = realloc(prog, pcap * sizeof(op_t)); }
  prog[nprog++] = (op_t){x, a, b, c, kind};
}

static char sym(int s) {
  if (s == BND) return '*';
  if (s == 0) return 'L';
  if (s == 1) return 'G';
  if (s == FST) return 'F';
  return (char)('A' + s - 2);
}

static void build(void) {
  int M = 2 * N - 2;
  /* inf[t][i] cell index; allocate (M+1) x (M+3) */
  int W = M + 3;
  int *inf = malloc((M + 1) * W * sizeof(int));
  int cB = newcell(BND), cL = newcell(0), cG = newcell(1);
#define INF(t, i) inf[(t) * W + (i)]
  for (int t = 0; t <= M; t++)
    for (int i = 0; i < W; i++) {
      if (i == 0) INF(t, i) = cB;
      else if (t == 0) INF(t, i) = (i == 1) ? cG : cL;
      else if (i > t + 1) INF(t, i) = cL;
      else INF(t, i) = -1;
    }
  /* anti-diagonal order: m = t+i, t increasing */
  int nextn = 2;
  int **retdiag = calloc(N + 2, sizeof(int *)); /* R_n(2n-1-i, i), i=1..n */
  for (int m = 2; m <= M; m++) {
    for (int t = 1; t <= M; t++) {
      int i = m - t;
      if (i < 1) break;
      if (i > t + 1) continue;
      int x = newcell(-1);
      INF(t, i) = x;
      emit(x, INF(t - 1, i - 1), INF(t - 1, i), INF(t - 1, i + 1),
           (i == t + 1 && use_front) ? FRONT : NONF);
    }
    /* implied: the return signal of line n differs from C_inf (n <= N-1) */
    if (use_diff && (m + 1) % 2 == 0) {
      int n = (m + 1) / 2;
      if (n >= 2 && n <= N && retdiag[n]) {
        for (int i = n; i >= 2; i--) emit(-1, retdiag[n][i], INF(m - i, i), -1, DIFF);
      }
    }
    /* after anti-diagonal 2n-2 is known, line n can be evaluated */
    while (nextn <= N && 2 * nextn - 2 <= m) {
      int n = nextn++;
      int T = 2 * n - 3;
      /* R[t][i] for t in [n-1, 2n-3], i in [1,n] */
      int RW = n + 2;
      int *R = malloc((2 * n) * RW * sizeof(int));
#define RV(t, j) (((j) == 0 || (j) == n + 1) ? cB : (((t) + (j) >= 2 * n - 1) ? R[(t) * RW + (j)] : INF(t, j)))
      for (int t = n - 1; t <= T; t++)
        for (int i = 1; i <= n; i++)
          if (t + i >= 2 * n - 1) {
            int x = newcell(-1);
            R[t * RW + i] = x;
            emit(x, RV(t - 1, i - 1), RV(t - 1, i), RV(t - 1, i + 1), NONF);
          }
      for (int i = 1; i <= n; i++) emit(-1, RV(T, i - 1), RV(T, i), RV(T, i + 1), FIRE);
      retdiag[n] = malloc((n + 1) * sizeof(int));
      for (int i = 2; i <= n; i++) retdiag[n][i] = R[(2 * n - 1 - i) * RW + i];
#undef RV
      free(R);
    }
  }
#undef INF
  free(inf);
}

static int usedmark[8][8][8];
static void print_solution(void) {
  /* recompute which entries are used */
  memset(usedmark, 0, sizeof usedmark);
  for (int p = 0; p < nprog; p++) {
    op_t *o = &prog[p];
    if (o->kind == DIFF) continue;
    usedmark[cell[o->a]][cell[o->b]][cell[o->c]] = 1;
  }
  printf("SOL %lld:", sols);
  for (int l = 0; l < 8; l++)
    for (int c = 0; c < 8; c++)
      for (int r = 0; r < 8; r++)
        if (usedmark[l][c][r]) printf(" %c%c%c>%c", sym(l), sym(c), sym(r), sym(tab[l][c][r]));
  printf("\n");
}

static int branchdepth;
static void print_cube(void) {
  ncubes++;
  printf("a");
  for (int q = 0; q < nset; q++) {
    int *e = setorder[q];
    printf(" %c%c%c=%c", sym(e[0]), sym(e[1]), sym(e[2]), sym(tab[e[0]][e[1]][e[2]]));
  }
  printf("\n");
}
static void dfs(int p) {
  nodes++;
  if (branchdepth == cube_depth) { print_cube(); return; }
  for (; p < nprog; p++) {
    op_t *o = &prog[p];
    if (o->kind == DIFF) {
      if (cell[o->a] == cell[o->b]) { hist[p]++; return; }
      continue;
    }
    int a = cell[o->a], b = cell[o->b], c = cell[o->c];
    int v = tab[a][b][c];
    if (v < 0) {
      /* branch */
      int lo, hi;
      if (o->kind == FIRE) { lo = hi = FST; }
      else if (o->kind == FRONT) { lo = 1; hi = WS - 1; }
      else { lo = 0; hi = WS - 1; }
      int savemax = maxaux;
      int mydepth = branchdepth++;
      for (int d = lo; d <= hi; d++) {
        if (d >= 2 && d < FST && d > maxaux + 1) continue; /* symmetry */
        if (mydepth < split_depth) {
          /* the choices at the top of the tree are distributed */
          if (mydepth == split_depth - 1) {
            long long id = split_counter++;
            if (id % split_n != split_part) continue;
          }
        }
        tab[a][b][c] = d;
        setorder[nset][0] = a; setorder[nset][1] = b; setorder[nset][2] = c; nset++;
        if (d >= 2 && d < FST && d > maxaux) maxaux = d;
        if (o->x >= 0) cell[o->x] = d;
        dfs(p + 1);
        nset--;
        maxaux = savemax;
      }
      tab[a][b][c] = -1;
      branchdepth--;
      return;
    }
    if (o->kind == FIRE) {
      if (v != FST) { hist[p]++; return; }
    } else {
      if (v == FST || (o->kind == FRONT && v == 0)) { hist[p]++; return; }
      cell[o->x] = v;
    }
  }
  sols++;
  if (print_sols) print_solution();
}

int main(int argc, char **argv) {
  if (argc < 3) { fprintf(stderr, "usage: %s k N [-p d part n] [-s]\n", argv[0]); return 2; }
  K = atoi(argv[1]); N = atoi(argv[2]);
  WS = K - 1; FST = K - 1;
  for (int i = 3; i < argc; i++) {
    if (!strcmp(argv[i], "-s")) print_sols = 1;
    else if (!strcmp(argv[i], "-c") && i + 1 < argc) { cube_depth = atoi(argv[i + 1]); i++; }
    else if (!strcmp(argv[i], "-nodiff")) { use_diff = 0; use_front = 0; }
    else if (!strcmp(argv[i], "-p") && i + 3 < argc) {
      split_depth = atoi(argv[i + 1]); split_part = atoi(argv[i + 2]); split_n = atoi(argv[i + 3]);
      i += 3;
    }
  }
  memset(tab, -1, sizeof tab);
  tab[0][0][0] = 0;       /* d(L,L,L) = L */
  tab[0][0][BND] = 0;     /* d(L,L,*) = L */
  maxaux = 1;
  build();
  hist = calloc(nprog + 1, sizeof(long long));
  fprintf(stderr, "k=%d N=%d program length %d, cells %d\n", K, N, nprog, ncell);
  dfs(0);
  if (cube_depth >= 0) fprintf(stderr, "cubes=%lld nodes=%lld solutions=%lld\n", ncubes, nodes, sols);
  else printf("k=%d N=%d nodes=%lld solutions=%lld\n", K, N, nodes, sols);
  return 0;
}

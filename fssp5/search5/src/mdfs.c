/*
 * mdfs.c -- exhaustive depth-first enumeration of k-state rules that synchronize the lines of
 * lengths nmin..N in minimal time AND have the exact recursive structure of mcopy.py:
 *
 *   chain of cuts of the line n:  r = n;  while m = (r + a) / 3 >= mmin:  the sub-line [r-m+1, r] is a
 *   verbatim copy of the diagram of the line of length m from its row s0 on,
 *        C_n(T + s, r - m + i) = C_m(s, i)   (s >= s0, 1 <= i <= m),   T = 2n - 2m;      r -= m.
 *   wake: a cell of a sub-line above its copy region, more than `wake` cells behind the return chain and
 *   to the right of the seed (i > p + s0 + margin), is quiescent.   (wake = 0: no such condition)
 *
 * The rule is filled lazily, as in fsspdfs.c: the diagrams are evaluated along a fixed program of cell
 * computations, and the search branches whenever a transition that is not fixed yet is needed.
 *
 * usage: mdfs k N a s0 mmin wake margin nmin [-s] [-n maxnodes] [-g gstatic] [-c] [-f table]
 *   -s  print every solution (restricted to the entries that are used)
 *   -c  no copies (plain enumeration)
 *   -g T  the first cell is G at every time >= T
 *   -f  fix the transitions listed in a rule table (soundness test)
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define BND 7
enum { NONF = 0, FIRE = 1, DIFF = 2, FRONT = 3, EQ = 4, ISL = 5, MARK = 6, ISG = 7, HNONF = 8 };

static int K, N, WS, FST, A_, S0, MMIN, WAKE, MARGIN, NMIN, GSTATIC = -1, NOCOPY = 0, PERIOD = 0, CTHETA = 2, B3 = 0, B1S = 0, NOGH = 0, RBG = 0;
static int tab[8][8][8];
static int *cell;
typedef struct { int x, a, b, c, kind; } op_t;
static op_t *prog;
static int nprog;
static long long nodes, sols, maxnodes = 0;
static int print_sols;
static int maxaux;
static long long pass[512];
static int ncell, cap, pcap;

static int newcell(int v) {
  if (ncell == cap) { cap = cap ? 2 * cap : 1024; cell = realloc(cell, cap * sizeof(int)); }
  cell[ncell] = v;
  return ncell++;
}
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
static int code(char ch) {
  if (ch == '*') return BND;
  if (ch == 'L') return 0;
  if (ch == 'G') return 1;
  if (ch == 'F') return FST;
  return ch - 'A' + 2;
}

typedef struct { int p, m, T; } cut_t;
static cut_t cuts[512][16];
static int ncut[512];
static int *idx[512]; /* idx[n][t*(n+2)+i]: cell index of C_n(t,i), 0<=t<=2n-3, 0<=i<=n+1 */

static int *inf, INFW, cB, cL, cG, hl_done = 1, MM;
static int **retdiag;
static int order[512], norder;
#define INF(t, i) inf[(t) * INFW + (i)]

static void extend_halfline(int mto) {
  if (mto > MM) mto = MM;
  for (int m = hl_done + 1; m <= mto; m++) {
    for (int t = 1; t <= MM; t++) {
      int i = m - t;
      if (i < 1) break;
      if (i > t + 1) continue;
      int x = newcell(-1);
      INF(t, i) = x;
      emit(x, INF(t - 1, i - 1), INF(t - 1, i), INF(t - 1, i + 1), (i == t + 1 && t <= N - 2) ? FRONT : HNONF);
      if (i == 1 && GSTATIC >= 0 && t >= GSTATIC) emit(-1, x, -1, -1, ISG);
      if (PERIOD && t - PERIOD >= 2 * (t + 1 - i) + CTHETA && t - PERIOD >= 1) emit(-1, x, INF(t - PERIOD, i - PERIOD), -1, EQ);
    }
    if ((m + 1) % 2 == 0) {            /* anti-diagonal 2n-1: the return chain of the line n differs from the half-line */
      int n = (m + 1) / 2;
      if (n >= NMIN && n <= N && retdiag[n])
        for (int i = n; i >= 2; i--) emit(-1, retdiag[n][i], INF(m - i, i), -1, DIFF);
    }
  }
  if (mto > hl_done) hl_done = mto;
}

static void emit_line(int n) {
  extend_halfline(2 * n - 2);
  int T = 2 * n - 3;
  int RW = n + 2;
  int *R = malloc((2 * n) * RW * sizeof(int));
  idx[n] = R;
  for (int t = 0; t <= T; t++)
    for (int i = 0; i <= n + 1; i++)
      R[t * RW + i] = (i == 0 || i == n + 1) ? cB : ((t + i <= 2 * n - 2) ? INF(t, i) : -1);
  for (int t = n - 1; t <= T; t++)
    for (int i = 1; i <= n; i++)
      if (t + i >= 2 * n - 1) {
        int x = newcell(-1);
        R[t * RW + i] = x;
        emit(x, R[(t - 1) * RW + i - 1], R[(t - 1) * RW + i], R[(t - 1) * RW + i + 1], NONF);
        for (int j = 0; j < ncut[n]; j++) {
          cut_t *c = &cuts[n][j];
          if (i < c->p || i > c->p + c->m - 1) continue;
          if (t >= c->T + S0) {
            if (!idx[c->m]) { fprintf(stderr, "order: the line %d needs the line %d first\n", n, c->m); exit(1); }
            int y = idx[c->m][(t - c->T) * (c->m + 2) + (i - c->p + 1)];
            emit(-1, x, y, -1, EQ);
          } else if (WAKE && t + i >= 2 * n - 1 + WAKE && i > c->p + S0 + MARGIN) {
            emit(-1, x, -1, -1, ISL);
          }
        }
      }
  for (int i = 1; i <= n; i++) emit(-1, R[T * RW + i - 1], R[T * RW + i], R[T * RW + i + 1], FIRE);
  emit(-1, n, -1, -1, MARK);
  retdiag[n] = malloc((n + 1) * sizeof(int));
  for (int i = 2; i <= n; i++) retdiag[n][i] = R[(2 * n - 1 - i) * RW + i];
  /* if the half-line already covers the anti-diagonal 2n-1, compare the return chain now */
  if (hl_done >= 2 * n - 1)
    for (int i = n; i >= 2; i--) emit(-1, retdiag[n][i], INF(2 * n - 1 - i, i), -1, DIFF);
}

static void build(void) {
  MM = 2 * N - 1;
  INFW = MM + 3;
  inf = malloc((MM + 1) * INFW * sizeof(int));
  cB = newcell(BND); cL = newcell(0); cG = newcell(1);
  for (int t = 0; t <= MM; t++)
    for (int i = 0; i < INFW; i++) {
      if (i == 0) INF(t, i) = cB;
      else if (t == 0) INF(t, i) = (i == 1) ? cG : cL;
      else if (i > t + 1) INF(t, i) = cL;
      else INF(t, i) = -1;
    }
  for (int n = NMIN; n <= N; n++) {
    int r = n;
    ncut[n] = 0;
    while (!NOCOPY) {
      int m = (r + A_) / 3;
      if (m < MMIN || m >= r) break;
      if (m < NMIN) { fprintf(stderr, "sub-line shorter than nmin\n"); exit(1); }
      cuts[n][ncut[n]++] = (cut_t){r - m + 1, m, 2 * n - 2 * m};
      if (2 * n - 2 * m + S0 + (r - m + 1) < 2 * n - 1) { fprintf(stderr, "copy region reaches the half-line zone (n=%d m=%d)\n", n, m); exit(1); }
      r -= m;
    }
  }
  retdiag = calloc(N + 2, sizeof(int *));
  if (!norder) for (int n = NMIN; n <= N; n++) order[norder++] = n;
  for (int q = 0; q < norder; q++) emit_line(order[q]);
  extend_halfline(MM);
}

static int usedmark[8][8][8];
static void print_solution(void) {
  memset(usedmark, 0, sizeof usedmark);
  for (int p = 0; p < nprog; p++) {
    op_t *o = &prog[p];
    if (o->kind == NONF || o->kind == FIRE || o->kind == FRONT || o->kind == HNONF) usedmark[cell[o->a]][cell[o->b]][cell[o->c]] = 1;
  }
  printf("SOL %lld:", sols);
  for (int l = 0; l < 8; l++)
    for (int c = 0; c < 8; c++)
      for (int r = 0; r < 8; r++)
        if (usedmark[l][c][r]) printf(" %c%c%c>%c", sym(l), sym(c), sym(r), sym(tab[l][c][r]));
  printf("\n");
  fflush(stdout);
}

static void dfs(int p) {
  nodes++;
  if (maxnodes && nodes > maxnodes) return;
  for (; p < nprog; p++) {
    op_t *o = &prog[p];
    switch (o->kind) {
    case DIFF: if (cell[o->a] == cell[o->b]) return; continue;
    case EQ: if (cell[o->a] != cell[o->b]) return; continue;
    case ISL: if (cell[o->a] != 0) return; continue;
    case ISG: if (cell[o->a] != 1) return; continue;
    case MARK: if (!pass[o->a]++) fprintf(stderr, "passed the line %d after %lld nodes\n", o->a, nodes); continue;
    default: break;
    }
    int a = cell[o->a], b = cell[o->b], c = cell[o->c];
    int half = (o->kind == HNONF || o->kind == FRONT);
    if (RBG && c == BND) c = 1;          /* the right border behaves like a general */
    if (B3) {                 /* exactly the neighbourhoods GGG, *GG, GG* give F */
      int gt = (b == 1) && (a == 1 || a == BND) && (c == 1 || c == BND);
      if (o->kind == FIRE) { if (!gt) return; continue; }
      if (gt) return;
    }
    if (B1S && b == 1) {      /* a general that is not between two generals/borders stays a general */
      if (o->kind == FIRE) return;
      cell[o->x] = 1;
      continue;
    }
    int v = tab[a][b][c];
    if (v < 0) {
      int lo, hi;
      if (o->kind == FIRE) { lo = hi = FST; }
      else if (o->kind == FRONT) { lo = 1; hi = WS - 1; }
      else { lo = 0; hi = WS - 1; }
      int savemax = maxaux;
      for (int d = lo; d <= hi; d++) {
        if (d >= 2 && d < FST && d > maxaux + 1) continue;
        if (NOGH && half && d == 1) continue;    /* no general on the half-line beyond the first cell */
        tab[a][b][c] = d;
        if (d >= 2 && d < FST && d > maxaux) maxaux = d;
        if (o->x >= 0) cell[o->x] = d;
        dfs(p + 1);
        maxaux = savemax;
        if (maxnodes && nodes > maxnodes) break;
      }
      tab[a][b][c] = -1;
      return;
    }
    if (o->kind == FIRE) {
      if (v != FST) return;
    } else {
      if (v == FST || (o->kind == FRONT && v == 0) || (NOGH && half && v == 1)) return;
      cell[o->x] = v;
    }
  }
  sols++;
  if (print_sols) print_solution();
}

int main(int argc, char **argv) {
  if (argc < 9) { fprintf(stderr, "usage: mdfs k N a s0 mmin wake margin nmin [-s] [-n maxnodes] [-g T] [-c] [-f table]\n"); return 1; }
  K = atoi(argv[1]); N = atoi(argv[2]); A_ = atoi(argv[3]); S0 = atoi(argv[4]); MMIN = atoi(argv[5]);
  WAKE = atoi(argv[6]); MARGIN = atoi(argv[7]); NMIN = atoi(argv[8]);
  WS = K - 1; FST = K - 1;
  memset(tab, -1, sizeof tab);
  tab[0][0][0] = 0; tab[0][0][BND] = 0; tab[0][0][1] = -1;
  maxaux = 1;
  const char *fixfile = NULL;
  for (int i = 9; i < argc; i++) {
    if (!strcmp(argv[i], "-s")) print_sols = 1;
    else if (!strcmp(argv[i], "-c")) NOCOPY = 1;
    else if (!strcmp(argv[i], "-n")) maxnodes = atoll(argv[++i]);
    else if (!strcmp(argv[i], "-g")) GSTATIC = atoi(argv[++i]);
    else if (!strcmp(argv[i], "-f")) fixfile = argv[++i];
    else if (!strcmp(argv[i], "-b3")) B3 = 1;
    else if (!strcmp(argv[i], "-b1s")) B1S = 1;
    else if (!strcmp(argv[i], "-nogh")) NOGH = 1;
    else if (!strcmp(argv[i], "-rbg")) RBG = 1;
    else if (!strcmp(argv[i], "-o")) { char *q = strtok(argv[++i], ","); while (q) { order[norder++] = atoi(q); q = strtok(NULL, ","); } }
    else if (!strcmp(argv[i], "-P")) { PERIOD = atoi(argv[++i]); CTHETA = atoi(argv[++i]); }
  }
  if (fixfile) {
    FILE *f = fopen(fixfile, "r");
    char line[256], l[8], c[8], r[8], d[8];
    while (fgets(line, sizeof line, f)) {
      if (line[0] == '#' || line[0] == 'k') continue;
      if (sscanf(line, "%7s %7s %7s %7s", l, c, r, d) == 4) tab[code(l[0])][code(c[0])][code(r[0])] = code(d[0]);
    }
    fclose(f);
    maxaux = FST - 1;
  }
  build();
  fprintf(stderr, "k=%d N=%d a=%d s0=%d mmin=%d wake=%d margin=%d nmin=%d: %d ops, %d cells\n", K, N, A_, S0, MMIN, WAKE, MARGIN, NMIN, nprog, ncell);
  dfs(0);
  printf("nodes %lld  solutions %lld%s\n", nodes, sols, (maxnodes && nodes > maxnodes) ? "  (node limit reached)" : "");
  printf("partial rules passing the lines up to n:");
  for (int n = NMIN; n <= N; n++) printf(" %d:%lld", n, pass[n]);
  printf("\n");
  return 0;
}

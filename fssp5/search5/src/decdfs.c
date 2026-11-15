/*
 * decdfs.c -- is there a k-state rule whose diagrams are a local re-encoding of the diagrams of a given
 * solution (the target, e.g. Mazoyer's six-state rule)?
 *
 *   for every line n0 <= n <= N, every time t < 2n-2 and every cell i:
 *        target_n(t, i) = phi( c_n(t, i-r), ..., c_n(t, i+r) )         (decoder of radius r; borders = *)
 *   and the k-state rule fires every line at time 2n-2 (and not before).
 *
 * Depth-first search over the transitions of the k-state rule, filled lazily in the order in which the
 * diagrams need them (as in fsspdfs.c).  The decoder phi is not searched: it is determined by the diagram,
 * and the search fails as soon as two occurrences of a window require different target states.
 *
 * usage: decdfs k N r target.txt [-n0 3] [-s] [-m maxnodes] [-q]
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define BND 7
enum { NONF = 0, FIRE = 1, FRONT = 3, DEC = 4, MARK = 6 };

static int K, N, R, WS, FST, N0 = 3, REV = 0, HLONLY = 0, FIRSTN = 0, KEEPL = 0, KEEPG = 0;
static int tab[8][8][8];
static int *cell;
typedef struct { int x, a, b, c, kind, tg; } op_t;   /* DEC: x = target state, a = index into win[]; tg = target of the computed cell */
static op_t *prog;
static int nprog, ncell, cap, pcap;
static int *win;                                  /* windows: (2r+1) cell indices each */
static int nwin, wcap;
static long long nodes, sols, maxnodes = 0;
static int print_sols, maxaux, quiet;
static long long pass[512];
static signed char *phi;                          /* 5^(2r+1) entries */
static int *trail, ntrail;
static int nphi;

static int newcell(int v) {
  if (ncell == cap) { cap = cap ? 2 * cap : 1024; cell = realloc(cell, cap * sizeof(int)); }
  cell[ncell] = v;
  return ncell++;
}
static void emit(int x, int a, int b, int c, int kind) {
  if (nprog == pcap) { pcap = pcap ? 2 * pcap : 1024; prog = realloc(prog, pcap * sizeof(op_t)); }
  prog[nprog++] = (op_t){x, a, b, c, kind, -1};
}
static char sym(int s) {
  if (s == BND) return '*';
  if (s == 0) return 'L';
  if (s == 1) return 'G';
  if (s == FST) return 'F';
  return (char)('A' + s - 2);
}

/* ---- the target rule and its diagrams ---- */
static int TK, ttab[8][8][8];
static int tcode(char ch) {
  if (ch == '*') return BND;
  if (ch == 'L') return 0;
  if (ch == 'G') return 1;
  if (ch == 'F') return TK - 1;
  return ch - 'A' + 2;
}
static void load_target(const char *path) {
  FILE *f = fopen(path, "r");
  if (!f) { perror(path); exit(1); }
  char line[256], l[8], c[8], r[8], d[8];
  memset(ttab, -1, sizeof ttab);
  while (fgets(line, sizeof line, f)) {
    if (line[0] == '#') continue;
    if (line[0] == 'k') { TK = atoi(line + 1); continue; }
    if (sscanf(line, "%7s %7s %7s %7s", l, c, r, d) == 4) ttab[tcode(l[0])][tcode(c[0])][tcode(r[0])] = tcode(d[0]);
  }
  fclose(f);
}
/* target diagram of the line of length n: rows 0..2n-2, cells 1..n; returns malloc'd array [t*(n+2)+i] */
static int *target_line(int n, int tmax) {
  int *d = malloc((tmax + 1) * (n + 2) * sizeof(int));
  for (int i = 0; i <= n + 1; i++) d[i] = (i == 0 || i == n + 1) ? BND : (i == 1 ? 1 : 0);
  for (int t = 1; t <= tmax; t++) {
    d[t * (n + 2)] = BND; d[t * (n + 2) + n + 1] = BND;
    for (int i = 1; i <= n; i++) {
      int a = d[(t - 1) * (n + 2) + i - 1], b = d[(t - 1) * (n + 2) + i], c = d[(t - 1) * (n + 2) + i + 1];
      int v = (b == TK - 1 || a == TK - 1 || c == TK - 1) ? TK - 1 : ttab[a][b][c];
      if (v < 0) { fprintf(stderr, "target undefined at n=%d t=%d i=%d (%d %d %d)\n", n, t, i, a, b, c); exit(1); }
      d[t * (n + 2) + i] = v;
    }
  }
  return d;
}

static void emit_dec(int tgt, int *w) {
  if (nwin + 2 * R + 1 > wcap) { wcap = wcap ? 2 * wcap : 4096; win = realloc(win, wcap * sizeof(int)); }
  memcpy(win + nwin, w, (2 * R + 1) * sizeof(int));
  emit(tgt, nwin, -1, -1, DEC);
  nwin += 2 * R + 1;
}

static int *inf, INFW, cB, cL, cG, hl_done = 1, BIG, *th;
#define INF(t, i) inf[(t) * INFW + (i)]

static void extend_halfline(int mto) {       /* anti-diagonals hl_done+1 .. mto */
  int M = 2 * N - 2, w[32];
  for (int m = hl_done + 1; m <= mto; m++) {
    for (int t = 1; t <= M; t++) {
      int i = m - t;
      if (i < 1) break;
      if (i > t + 1) continue;
      int x = newcell(-1);
      INF(t, i) = x;
      emit(x, INF(t - 1, i - 1), INF(t - 1, i), INF(t - 1, i + 1), (i == t + 1 && t <= N - 2) ? FRONT : NONF);
      prog[nprog - 1].tg = th[t * (BIG + 2) + i];
      /* windows of row t that are complete now: centre i - R; at the front also the centres up to t + 1 + R */
      int lo = i - R, hi = (i == t + 1) ? t + 1 + R : i - R;
      for (int cc = lo; cc <= hi; cc++) {
        if (cc < 1) continue;
        if (cc + R > N) continue;                          /* not a window of the line of length N */
        int okw = 1;
        for (int q = -R; q <= R; q++) {
          int j = cc + q;
          w[q + R] = (j < 1) ? cB : INF(t, j);
          if (w[q + R] < 0) okw = 0;
        }
        if (okw) emit_dec(th[t * (BIG + 2) + cc], w);
      }
    }
  }
  if (mto > hl_done) hl_done = mto;
}

static void emit_line(int n) {
  int w[32];
  extend_halfline(2 * n - 2);
  int T = 2 * n - 3;
  int RW = n + 2;
  int *Rr = malloc((2 * n) * RW * sizeof(int));
  int *tg = target_line(n, 2 * n - 2);
  for (int i = 1; i <= n; i++) if (tg[(2 * n - 2) * RW + i] != TK - 1) { fprintf(stderr, "target does not fire n=%d\n", n); exit(1); }
  for (int t = 0; t <= T; t++)
    for (int i = 0; i <= n + 1; i++)
      Rr[t * RW + i] = (i == 0 || i == n + 1) ? cB : ((t + i <= 2 * n - 2) ? INF(t, i) : -1);
  for (int t = 0; t <= T; t++) {
    for (int i = 1; i <= n; i++)
      if (t + i >= 2 * n - 1) {
        int x = newcell(-1);
        Rr[t * RW + i] = x;
        emit(x, Rr[(t - 1) * RW + i - 1], Rr[(t - 1) * RW + i], Rr[(t - 1) * RW + i + 1], NONF);
        prog[nprog - 1].tg = tg[t * RW + i];
      }
    /* decode checks of the windows of row t that touch the right border or the reflected triangle */
    for (int cc = 1; cc <= n; cc++) {
      if (!(cc + R >= n + 1 || t + cc + R >= 2 * n - 1)) continue;
      for (int q = -R; q <= R; q++) {
        int j = cc + q;
        w[q + R] = (j < 1 || j > n) ? cB : Rr[t * RW + j];
      }
      emit_dec(tg[t * RW + cc], w);
    }
  }
  for (int i = 1; i <= n; i++) emit(-1, Rr[T * RW + i - 1], Rr[T * RW + i], Rr[T * RW + i + 1], FIRE);
  emit(-1, n, -1, -1, MARK);
  free(Rr); free(tg);
}

static void build(void) {
  int M = 2 * N - 2, w[32];
  INFW = M + 6 + 2 * R;
  inf = malloc((M + 1) * INFW * sizeof(int));
  cB = newcell(BND); cL = newcell(0); cG = newcell(1);
  BIG = M + R + 4;
  th = target_line(BIG, M);                 /* the target's half-line: a long line, t <= M < BIG - 1 */
  for (int t = 0; t <= M; t++)
    for (int i = 0; i < INFW; i++) {
      if (i == 0) INF(t, i) = cB;
      else if (t == 0) INF(t, i) = (i == 1) ? cG : cL;
      else if (i > t + 1) INF(t, i) = cL;
      else INF(t, i) = -1;
    }
  for (int i = 1; i <= 1 + R && i + R <= N; i++) {
    for (int q = -R; q <= R; q++) w[q + R] = (i + q < 1) ? cB : INF(0, i + q);
    emit_dec(th[i], w);
  }
  if (HLONLY) { extend_halfline(M); emit(-1, 0, -1, -1, MARK); return; }
  if (REV) { extend_halfline(M); emit(-1, 0, -1, -1, MARK); for (int n = N; n >= N0; n--) emit_line(n); return; }
  /* lines FIRST..N in increasing order, then FIRST-1 down to N0 */
  for (int n = FIRSTN; n <= N; n++) emit_line(n);
  for (int n = FIRSTN - 1; n >= N0; n--) emit_line(n);
}

static int usedmark[8][8][8];
static void print_solution(void) {
  memset(usedmark, 0, sizeof usedmark);
  for (int p = 0; p < nprog; p++) {
    op_t *o = &prog[p];
    if (o->kind == NONF || o->kind == FIRE || o->kind == FRONT) usedmark[cell[o->a]][cell[o->b]][cell[o->c]] = 1;
  }
  printf("SOL %lld:", sols);
  for (int l = 0; l < 8; l++)
    for (int c = 0; c < 8; c++)
      for (int r = 0; r < 8; r++)
        if (usedmark[l][c][r]) printf(" %c%c%c>%c", sym(l), sym(c), sym(r), sym(tab[l][c][r]));
  printf("\n");
  fflush(stdout);
}

static inline int widx(const int *w) {
  int h = 0;
  for (int q = 0; q < 2 * R + 1; q++) { int v = cell[w[q]]; h = h * 5 + (v == BND ? 4 : v); }
  return h;
}

static inline int allowed(int d, int tg) {
  if (tg < 0) return 1;
  if (KEEPL && ((d == 0) != (tg == 0))) return 0;
  if (KEEPG && ((d == 1) != (tg == 1))) return 0;
  return 1;
}

static void dfs(int p) {
  nodes++;
  if (maxnodes && nodes > maxnodes) return;
  for (; p < nprog; p++) {
    op_t *o = &prog[p];
    if (o->kind == DEC) {
      int h = widx(win + o->a);
      if (phi[h] < 0) { phi[h] = (signed char)o->x; trail[ntrail++] = h; }
      else if (phi[h] != o->x) return;
      continue;
    }
    if (o->kind == MARK) {
      pass[o->a]++;
      if (pass[o->a] == 1 && !quiet) fprintf(stderr, "passed mark %d after %lld nodes\n", o->a, nodes);
      continue;
    }
    int a = cell[o->a], b = cell[o->b], c = cell[o->c];
    int v = tab[a][b][c];
    if (v < 0) {
      int lo, hi;
      if (o->kind == FIRE) { lo = hi = FST; }
      else if (o->kind == FRONT) { lo = 1; hi = WS - 1; }
      else { lo = 0; hi = WS - 1; }
      int savemax = maxaux, savetrail = ntrail;
      for (int d = lo; d <= hi; d++) {
        if (d >= 2 && d < FST && d > maxaux + 1) continue;
        if (d < FST && !allowed(d, o->tg)) continue;
        tab[a][b][c] = d;
        if (d >= 2 && d < FST && d > maxaux) maxaux = d;
        if (o->x >= 0) cell[o->x] = d;
        dfs(p + 1);
        while (ntrail > savetrail) phi[trail[--ntrail]] = -1;
        maxaux = savemax;
        if (maxnodes && nodes > maxnodes) break;
      }
      tab[a][b][c] = -1;
      return;
    }
    if (o->kind == FIRE) {
      if (v != FST) return;
    } else {
      if (v == FST || (o->kind == FRONT && v == 0) || !allowed(v, o->tg)) return;
      cell[o->x] = v;
    }
  }
  sols++;
  if (print_sols) print_solution();
}

int main(int argc, char **argv) {
  if (argc < 5) { fprintf(stderr, "usage: decdfs k N r target.txt [-n0 3] [-s] [-m maxnodes] [-q]\n"); return 1; }
  K = atoi(argv[1]); N = atoi(argv[2]); R = atoi(argv[3]);
  load_target(argv[4]);
  WS = K - 1; FST = K - 1;
  memset(tab, -1, sizeof tab);
  tab[0][0][0] = 0; tab[0][0][BND] = 0;
  maxaux = 1;
  for (int i = 5; i < argc; i++) {
    if (!strcmp(argv[i], "-s")) print_sols = 1;
    else if (!strcmp(argv[i], "-q")) quiet = 1;
    else if (!strcmp(argv[i], "-m")) maxnodes = atoll(argv[++i]);
    else if (!strcmp(argv[i], "-n0")) N0 = atoi(argv[++i]);
    else if (!strcmp(argv[i], "-rev")) REV = 1;
    else if (!strcmp(argv[i], "-keepL")) KEEPL = 1;
    else if (!strcmp(argv[i], "-keepG")) KEEPG = 1;
    else if (!strcmp(argv[i], "-first")) FIRSTN = atoi(argv[++i]);
    else if (!strcmp(argv[i], "-hl")) REV = HLONLY = 1;
  }
  if (FIRSTN < N0) FIRSTN = N0;
  nphi = 1;
  for (int q = 0; q < 2 * R + 1; q++) nphi *= 5;
  phi = malloc(nphi);
  memset(phi, -1, nphi);
  trail = malloc((nphi + 8) * sizeof(int));
  build();
  if (!quiet) fprintf(stderr, "k=%d N=%d radius %d, target with %d states, lines %d..%d: %d ops, %d cells\n", K, N, R, TK, N0, N, nprog, ncell);
  dfs(0);
  printf("k=%d N=%d r=%d: nodes %lld  solutions %lld%s\n", K, N, R, nodes, sols, (maxnodes && nodes > maxnodes) ? "  (node limit reached)" : "");
  printf("partial rules passing the lines up to n:");
  if (REV) printf(" half-line:%lld", pass[0]);
  for (int n = N0; n <= N; n++) printf(" %d:%lld", n, pass[n]);
  printf("\n");
  return 0;
}

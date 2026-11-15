/*
 * facdfs.c -- k-state rules that are local images (factors) of a given solution.
 *
 * Target: a minimal-time solution M (Mazoyer's six-state rule) with diagrams M_n.  We look for a block map
 *     c_n(t, i) = pi( M_n(t, i-r), ..., M_n(t, i+r) )          (borders = *; radius r)
 * with values in the working states of a k-state rule (L, G, A, ...), such that the image diagrams are the
 * diagrams of ONE k-state rule delta that fires at time 2n-2:
 *     c_n(0, .) = G L ... L,
 *     delta(c_n(t,i-1), c_n(t,i), c_n(t,i+1)) = c_n(t+1, i)   (t+1 < 2n-2),     = F   (t+1 = 2n-2),
 *     delta is a function (the same neighbourhood never needs two different values).
 * Such a delta is a k-state minimal-time solution for the lengths n0..N; if all windows of radius r+1 of the
 * target have been seen, for every length that the target synchronizes.
 *
 * Depth-first search over the values of pi on the windows that occur, in the order in which they occur.
 *
 * usage: facdfs k N r target.txt [-n0 3] [-s] [-m maxnodes] [-q] [-up]
 *   -up  process the lines in increasing order (default: decreasing, the longest line first)
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define BND 7
static int K, N, R, N0 = 3, UP = 0, FST;
static int TK, ttab[8][8][8];
static long long nodes, sols, maxnodes;
static int print_sols, quiet;

static int tcode(char ch) {
  if (ch == '*') return BND;
  if (ch == 'L') return 0;
  if (ch == 'G') return 1;
  if (ch == 'F') return TK - 1;
  return ch - 'A' + 2;
}
static char tsym(int s) { return s == BND ? '*' : s == 0 ? 'L' : s == 1 ? 'G' : s == TK - 1 ? 'F' : (char)('A' + s - 2); }
static char sym(int s) { return s == BND ? '*' : s == 0 ? 'L' : s == 1 ? 'G' : s == FST ? 'F' : (char)('A' + s - 2); }
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
static int *target_line(int n) {          /* rows 0..2n-2, [t*(n+2)+i], i = 0 and n+1 are borders */
  int tmax = 2 * n - 2;
  int *d = malloc((tmax + 1) * (n + 2) * sizeof(int));
  for (int i = 0; i <= n + 1; i++) d[i] = (i == 0 || i == n + 1) ? BND : (i == 1 ? 1 : 0);
  for (int t = 1; t <= tmax; t++) {
    d[t * (n + 2)] = BND; d[t * (n + 2) + n + 1] = BND;
    for (int i = 1; i <= n; i++) {
      int a = d[(t - 1) * (n + 2) + i - 1], b = d[(t - 1) * (n + 2) + i], c = d[(t - 1) * (n + 2) + i + 1];
      int v = ttab[a][b][c];
      if (v < 0) { fprintf(stderr, "target undefined at n=%d t=%d i=%d\n", n, t, i); exit(1); }
      d[t * (n + 2) + i] = v;
    }
  }
  for (int i = 1; i <= n; i++) if (d[tmax * (n + 2) + i] != TK - 1) { fprintf(stderr, "target does not fire at 2n-2 for n=%d\n", n); exit(1); }
  for (int t = 0; t < tmax; t++) for (int i = 1; i <= n; i++) if (d[t * (n + 2) + i] == TK - 1) { fprintf(stderr, "target fires early n=%d\n", n); exit(1); }
  return d;
}

/* ---- windows ---- */
#define HSIZE (1 << 20)
static long long hkey[HSIZE];
static int hval[HSIZE];
static int nwinid;
static long long *winkey;
static int wincap;
static int win_id(long long key) {
  unsigned long long h = (unsigned long long)key * 0x9E3779B97F4A7C15ULL >> 44;
  while (hval[h] >= 0) { if (hkey[h] == key) return hval[h]; h = (h + 1) & (HSIZE - 1); }
  hkey[h] = key; hval[h] = nwinid;
  if (nwinid == wincap) { wincap = wincap ? 2 * wincap : 1024; winkey = realloc(winkey, wincap * sizeof(long long)); }
  winkey[nwinid] = key;
  return nwinid++;
}

/* ---- program ---- */
enum { SETC = 0, CHK = 1, CHKF = 2, MARK = 3 };
typedef struct { int kind, x, a, b, c; } op_t;   /* SETC: cell x := pi[a];  CHK: delta(a,b,c) = cell x;  CHKF: delta(a,b,c) = F */
static op_t *prog;
static int nprog, pcap, ncell;
static int *cell;
static signed char *pi;         /* per window id */
static int tab[8][8][8];
static int trail[4096][3], ntrail;
static int maxaux;
static long long pass[1024];

static void emit(int kind, int x, int a, int b, int c) {
  if (nprog == pcap) { pcap = pcap ? 2 * pcap : 4096; prog = realloc(prog, pcap * sizeof(op_t)); }
  prog[nprog++] = (op_t){kind, x, a, b, c};
}

static int cBND;
static void emit_line(int n) {
  int RW = n + 2, T = 2 * n - 2;
  int *d = target_line(n);
  int *ci = malloc(T * RW * sizeof(int));    /* cell indices of rows 0..2n-3 */
  for (int t = 0; t < T; t++) {
    ci[t * RW] = cBND; ci[t * RW + n + 1] = cBND;
    for (int i = 1; i <= n; i++) {
      long long key = 0;
      for (int q = -R; q <= R; q++) { int j = i + q; key = key * 8 + ((j < 1 || j > n) ? BND : d[t * RW + j]); }
      int w = win_id(key);
      int x = ncell++;
      ci[t * RW + i] = x;
      emit(SETC, x, w, t == 0 ? (i == 1 ? 1 : 0) : -1, -1);       /* b = forced value in row 0 */
      if (t >= 1) emit(CHK, x, ci[(t - 1) * RW + i - 1], ci[(t - 1) * RW + i], ci[(t - 1) * RW + i + 1]);
    }
  }
  for (int i = 1; i <= n; i++) emit(CHKF, -1, ci[(T - 1) * RW + i - 1], ci[(T - 1) * RW + i], ci[(T - 1) * RW + i + 1]);
  emit(MARK, n, -1, -1, -1);
  free(d); free(ci);
}

static void print_solution(void) {
  printf("SOL %lld: PI", sols);
  for (int w = 0; w < nwinid; w++) {
    printf(" ");
    long long key = winkey[w];
    char buf[32];
    for (int q = 2 * R; q >= 0; q--) { buf[q] = tsym((int)(key & 7)); key >>= 3; }
    buf[2 * R + 1] = 0;
    printf("%s>%c", buf, pi[w] < 0 ? '?' : sym(pi[w]));
  }
  printf("\nRULE %lld:", sols);
  for (int l = 0; l < 8; l++)
    for (int c = 0; c < 8; c++)
      for (int r = 0; r < 8; r++)
        if (tab[l][c][r] >= 0) printf(" %c%c%c>%c", sym(l), sym(c), sym(r), sym(tab[l][c][r]));
  printf("\n");
  fflush(stdout);
}

static inline int settab(int a, int b, int c, int v) {   /* 0 = conflict */
  int cur = tab[a][b][c];
  if (cur < 0) { tab[a][b][c] = v; trail[ntrail][0] = a; trail[ntrail][1] = b; trail[ntrail][2] = c; ntrail++; return 1; }
  return cur == v;
}

static void dfs(int p) {
  nodes++;
  if (maxnodes && nodes > maxnodes) return;
  for (; p < nprog; p++) {
    op_t *o = &prog[p];
    if (o->kind == CHK) { if (!settab(cell[o->a], cell[o->b], cell[o->c], cell[o->x])) return; continue; }
    if (o->kind == CHKF) { if (!settab(cell[o->a], cell[o->b], cell[o->c], FST)) return; continue; }
    if (o->kind == MARK) { pass[o->x]++; if (pass[o->x] == 1 && !quiet) fprintf(stderr, "passed line %d after %lld nodes\n", o->x, nodes); continue; }
    /* SETC */
    int v = pi[o->a];
    if (o->b >= 0) {                        /* row 0: forced */
      if (v < 0) {
        pi[o->a] = (signed char)o->b; cell[o->x] = o->b;
        int st = ntrail;
        dfs(p + 1);
        while (ntrail > st) { ntrail--; tab[trail[ntrail][0]][trail[ntrail][1]][trail[ntrail][2]] = -1; }
        pi[o->a] = -1;
        return;
      }
      if (v != o->b) return;
      cell[o->x] = v;
      continue;
    }
    if (v >= 0) { cell[o->x] = v; continue; }
    int savemax = maxaux, st = ntrail;
    for (int d = 0; d < K - 1; d++) {
      if (d >= 2 && d > maxaux + 1) continue;
      pi[o->a] = (signed char)d; cell[o->x] = d;
      if (d >= 2 && d > maxaux) maxaux = d;
      dfs(p + 1);
      while (ntrail > st) { ntrail--; tab[trail[ntrail][0]][trail[ntrail][1]][trail[ntrail][2]] = -1; }
      maxaux = savemax;
      if (maxnodes && nodes > maxnodes) break;
    }
    pi[o->a] = -1;
    return;
  }
  sols++;
  if (print_sols) print_solution();
}

int main(int argc, char **argv) {
  if (argc < 5) { fprintf(stderr, "usage: facdfs k N r target.txt [-n0 3] [-s] [-m maxnodes] [-q] [-up]\n"); return 1; }
  K = atoi(argv[1]); N = atoi(argv[2]); R = atoi(argv[3]);
  load_target(argv[4]);
  FST = K - 1;
  for (int i = 5; i < argc; i++) {
    if (!strcmp(argv[i], "-s")) print_sols = 1;
    else if (!strcmp(argv[i], "-q")) quiet = 1;
    else if (!strcmp(argv[i], "-up")) UP = 1;
    else if (!strcmp(argv[i], "-m")) maxnodes = atoll(argv[++i]);
    else if (!strcmp(argv[i], "-n0")) N0 = atoi(argv[++i]);
  }
  memset(hval, -1, sizeof hval);
  memset(tab, -1, sizeof tab);
  tab[0][0][0] = 0; tab[0][0][BND] = 0;
  maxaux = 1;
  ncell = 0;
  cBND = ncell++;
  if (UP) for (int n = N0; n <= N; n++) emit_line(n);
  else for (int n = N; n >= N0; n--) emit_line(n);
  cell = malloc(ncell * sizeof(int));
  cell[cBND] = BND;
  pi = malloc(nwinid + 1);
  memset(pi, -1, nwinid + 1);
  if (!quiet) fprintf(stderr, "k=%d N=%d radius %d: %d ops, %d cells, %d distinct windows of the target\n", K, N, R, nprog, ncell, nwinid);
  dfs(0);
  printf("k=%d lines %d..%d radius %d: %d windows, nodes %lld, solutions %lld%s\n", K, N0, N, R, nwinid, nodes, sols,
         (maxnodes && nodes > maxnodes) ? " (node limit reached)" : "");
  return 0;
}

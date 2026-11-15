/*
 * germw.c -- half-line germs of the class "stable generals" (B1 strong, B3 weak):
 * the first cell is always G, and no other cell of the half-line is G, so the half-line is a diagram over
 * {L, A, B} with a constant left neighbour G.  We enumerate ALL such germs up to the anti-diagonal M
 * (no bound on the number of transitions) that satisfy the necessary conditions on the half-line:
 *   - the front is never L;
 *   - PUMP(n, n') for 4 <= n < n' <= NP, checked as soon as the anti-diagonal 2n'-2 is complete.
 * A before B (symmetry).  usage: germw M NP [-q] [-c]     (-c: count only)
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define BND 7
static int M_, NP, quiet;
static int tab[8][8][8];
static int nused;
static int usedl[256][3];
static int *val;
static int W_;
static long long nodes, leaves, pumpcuts;
static long long hist[64];
static int maxaux;
#define V(t, i) val[(t) * W_ + (i)]
static char sym(int s) { return s == BND ? '*' : s == 0 ? 'L' : s == 1 ? 'G' : (char)('A' + s - 2); }
static inline int cellv(int t, int i) {
  if (i == 0) return BND;
  if (i == 1) return 1;                 /* the general is always G */
  if (i > t + 1) return 0;
  return V(t, i);
}
static int pump_ok(int n, int n2) {
  int half = n / 2;
  for (int k = 1; k <= half; k++) {
    if (cellv(n - 3 + k, n - k) != cellv(n2 - 3 + k, n2 - k)) return 1;
    if (cellv(n - 2 + k, n - k) != cellv(n2 - 2 + k, n2 - k)) return 1;
  }
  if (n % 2) {
    int k = (n + 1) / 2;
    if (cellv(n - 3 + k, n - k) != cellv(n2 - 3 + k, n2 - k)) return 1;
  }
  return 0;
}
static void print_germ(void) {
  printf("GERM");
  for (int q = 0; q < nused; q++) {
    int *e = usedl[q];
    printf(" %c%c%c>%c", sym(e[0]), sym(e[1]), sym(e[2]), sym(tab[e[0]][e[1]][e[2]]));
  }
  printf("\n");
}
static void dfs(int m, int t) {
  nodes++;
  for (;;) {
    if (m > M_) { leaves++; hist[nused]++; if (!quiet) print_germ(); return; }
    int i = m - t;
    if (t > m - 1 || i < 2) {
      if (m % 2 == 0) {
        int n2 = (m + 2) / 2;
        if (n2 <= NP)
          for (int n = 4; n < n2; n++)
            if (!pump_ok(n, n2)) { pumpcuts++; return; }
      }
      m++;
      t = 1;
      continue;
    }
    if (i > t + 1) { t++; continue; }
    int a = cellv(t - 1, i - 1), b = cellv(t - 1, i), c = cellv(t - 1, i + 1);
    int d = tab[a][b][c];
    if (d < 0) {
      int savemax = maxaux;
      usedl[nused][0] = a; usedl[nused][1] = b; usedl[nused][2] = c;
      nused++;
      for (int v = 0; v < 4; v++) {
        if (v == 1) continue;                      /* no G on the half-line beyond the first cell */
        if (v == 0 && i == t + 1) continue;        /* the front is never L */
        if (v >= 2 && v > maxaux + 1) continue;
        tab[a][b][c] = v;
        if (v >= 2 && v > maxaux) maxaux = v;
        V(t, i) = v;
        dfs(m, t + 1);
        maxaux = savemax;
      }
      nused--;
      tab[a][b][c] = -1;
      return;
    }
    if (i == t + 1 && d == 0) return;
    V(t, i) = d;
    t++;
  }
}
int main(int argc, char **argv) {
  if (argc < 3) { fprintf(stderr, "usage: %s M NP [-q]\n", argv[0]); return 2; }
  M_ = atoi(argv[1]); NP = atoi(argv[2]);
  quiet = argc > 3 && !strcmp(argv[3], "-q");
  W_ = M_ + 3;
  val = calloc((size_t)(M_ + 2) * W_, sizeof(int));
  memset(tab, -1, sizeof tab);
  tab[0][0][0] = 0;
  maxaux = 1;
  dfs(2, 1);
  fprintf(stderr, "M=%d NP=%d: nodes=%lld germs=%lld pumpcuts=%lld; germs by number of transitions:", M_, NP, nodes, leaves, pumpcuts);
  for (int q = 0; q < 64; q++) if (hist[q]) fprintf(stderr, " %d:%lld", q, hist[q]);
  fprintf(stderr, "\n");
  return 0;
}

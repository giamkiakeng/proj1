/*
 * germdfs.c -- enumerate half-line "germs" of bounded complexity.
 *
 * A germ is the restriction of a k-state rule to the transitions used by the
 * half-line diagram C_inf on the anti-diagonals t+i <= M.  We enumerate all
 * germs that use at most K distinct transitions and satisfy the necessary
 * conditions that involve the half-line only:
 *   - no half-line cell fires (values are taken in W = {L,G,A,B,...});
 *   - the front never is L (return-chain lemma);
 *   - PUMP(n,n') for 4 <= n < n' <= NP (pumping lemma), checked as soon as
 *     anti-diagonal 2n'-2 is complete.
 * Auxiliary states are introduced in increasing order (symmetry breaking).
 * Surviving germs are printed (one line of transitions each) for the
 * completion test.
 *
 * usage: germdfs k M K NP [-q]
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define BND 7
static int K_, M_, KMAX, NP, WS, quiet;
static int tab[8][8][8];
static int nused;
static int usedl[256][3];
static int *val;       /* val[t*(M+3)+i] */
static int W_;
static long long nodes, leaves, pumpcuts, budgetcuts;
static int maxaux;

#define V(t, i) val[(t) * W_ + (i)]

static char sym(int s) {
  if (s == BND) return '*';
  if (s == 0) return 'L';
  if (s == 1) return 'G';
  return (char)('A' + s - 2);
}

static inline int cellv(int t, int i) {
  if (i == 0) return BND;
  if (t == 0) return i == 1 ? 1 : 0;
  if (i > t + 1) return 0;
  return V(t, i);
}

/* cone positions for pumping (see pumping.py): upper at 0, both at 1..floor(n/2),
   lower at (n+1)/2 when n odd.  Input cells: lower (n-3+k, n-k), upper (n-2+k, n-k). */
static int pump_ok(int n, int n2) {
  /* return 1 if J_n and J_n2 differ somewhere on cone_n */
  int half = n / 2;
  /* upper at 0: both L -> equal, skip */
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

/* process anti-diagonal m, cell index within it (t increasing) */
static void dfs(int m, int t) {
  nodes++;
  for (;;) {
    if (m > M_) { leaves++; if (!quiet) print_germ(); return; }
    int i = m - t;
    if (t > m - 1 || i < 1) {
      /* anti-diagonal m complete: pumping checks for n' with 2n'-2 == m */
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
      if (nused >= KMAX) { budgetcuts++; return; }
      int lo = (i == t + 1) ? 1 : 0; /* front cell cannot be L */
      int savemax = maxaux;
      usedl[nused][0] = a; usedl[nused][1] = b; usedl[nused][2] = c;
      nused++;
      for (int v = lo; v < WS; v++) {
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
    if (i == t + 1 && d == 0) return; /* front L: impossible */
    V(t, i) = d;
    t++;
  }
}

int main(int argc, char **argv) {
  if (argc < 5) { fprintf(stderr, "usage: %s k M K NP [-q]\n", argv[0]); return 2; }
  K_ = atoi(argv[1]); M_ = atoi(argv[2]); KMAX = atoi(argv[3]); NP = atoi(argv[4]);
  quiet = argc > 5 && !strcmp(argv[5], "-q");
  WS = K_ - 1;
  W_ = M_ + 3;
  val = calloc((size_t)(M_ + 2) * W_, sizeof(int));
  memset(tab, -1, sizeof tab);
  tab[0][0][0] = 0;
  nused = 0;
  maxaux = 1;
  dfs(2, 1);
  fprintf(stderr, "k=%d M=%d K=%d NP=%d: nodes=%lld germs=%lld pumpcuts=%lld budgetcuts=%lld\n",
          K_, M_, KMAX, NP, nodes, leaves, pumpcuts, budgetcuts);
  return 0;
}

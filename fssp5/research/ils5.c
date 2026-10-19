/*
 * ils5.c -- iterated local search for k-state minimal-time firing squad rules (k <= 6).
 *
 * In the spirit of Clergue, Verel and Formenti (Appl. Soft Comput. 66, 2018), who found 718
 * six-state solutions this way: a rule table is scored only by how well the lines of lengths
 * 2..NMAX synchronize, and a local search with neutral moves and perturbations climbs that score.
 *
 * Score of a table: the number s of consecutive lengths 2, 3, ..., s+1 that fire exactly at time
 * 2n-2 (all cells, none before), and as a tie-breaker the quality of the first failing length n:
 * the number of time steps it survives without any cell firing (capped at 2n-2) plus the number of
 * its cells that are F at time 2n-2 when nothing fired before.
 *
 * Moves change one transition among those used by the lines simulated so far (others are neutral);
 * a move is accepted if the score does not decrease.  After STALL moves without improvement, PERT
 * random used transitions are reset (perturbation) and the search continues from there.
 *
 * usage: ils5 k NMAX seed maxevals [STALL PERT] [-o best.txt]
 * states: L=0 G=1 A=2 B=3 C=4 ... F=k-1, border = k (index); table T[left][mid][right]
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAXK 6
#define MAXN 64
static int K, NMAX;
static unsigned char T[MAXK + 1][MAXK][MAXK + 1];
static unsigned char used[MAXK + 1][MAXK][MAXK + 1];
static unsigned long long rs;

static unsigned rnd(void) { rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17; return (unsigned)(rs >> 11); }

/* simulate line n; returns 2 if correct; otherwise fills partial quality */
static int line(int n, long *quality, int mark) {
  unsigned char a[MAXN + 2], b[MAXN + 2];
  int B = K, F = K - 1, t, i;
  a[0] = B; a[n + 1] = B; b[0] = B; b[n + 1] = B;
  a[1] = 1; for (i = 2; i <= n; i++) a[i] = 0;
  for (t = 1; t <= 2 * n - 2; t++) {
    int nf = 0;
    for (i = 1; i <= n; i++) {
      unsigned char x = T[a[i - 1]][a[i]][a[i + 1]];
      if (mark) used[a[i - 1]][a[i]][a[i + 1]] = 1;
      b[i] = x;
      if (x == F) nf++;
    }
    if (nf) {
      if (t < 2 * n - 2) { *quality = t; return 0; }
      if (nf == n) return 2;
      *quality = 2 * n - 2 + nf; return 0;
    }
    memcpy(a + 1, b + 1, n);
  }
  *quality = 2 * n - 2; return 0;
}

static long score(int mark) {
  long q = 0; int n;
  if (mark) memset(used, 0, sizeof used);
  for (n = 2; n <= NMAX; n++) {
    if (line(n, &q, mark) != 2) return (long)(n - 2) * 1000 + (q * 1000) / (3 * n);
  }
  return (long)(NMAX - 1) * 1000;
}

static int fixed(int l, int c, int r) { return c == 0 && l == 0 && (r == 0 || r == K); }

static void randomize_entry(int l, int c, int r) { T[l][c][r] = rnd() % K; }

static void write_table(const char *path) {
  FILE *f = fopen(path, "w"); int l, c, r; const char *S = "LGABCDE";
  if (!f) return;
  fprintf(f, "k %d\n", K);
  for (l = 0; l <= K; l++) for (c = 0; c < K - 1; c++) for (r = 0; r <= K; r++) {
    if (l == K && r == K) continue;
    if (l == K - 1 || r == K - 1) continue;           /* F never appears as a neighbour */
    char cl = l == K ? '*' : S[l], cr = r == K ? '*' : S[r];
    char d = T[l][c][r] == K - 1 ? 'F' : S[T[l][c][r]];
    fprintf(f, "%c %c %c %c\n", cl, S[c], cr, d);
  }
  fclose(f);
}

int main(int argc, char **argv) {
  if (argc < 5) { fprintf(stderr, "usage: %s k NMAX seed maxevals [STALL PERT] [-o best.txt]\n", argv[0]); return 2; }
  K = atoi(argv[1]); NMAX = atoi(argv[2]); rs = 88172645463325252ULL ^ (unsigned long long)atoll(argv[3]) * 2654435761ULL;
  long long maxevals = atoll(argv[4]);
  int STALL = argc > 5 && argv[5][0] != '-' ? atoi(argv[5]) : 20000, PERT = argc > 6 && argv[6][0] != '-' ? atoi(argv[6]) : 3;
  const char *out = NULL; int i;
  for (i = 5; i < argc; i++) if (!strcmp(argv[i], "-o") && i + 1 < argc) out = argv[i + 1];
  int l, c, r;
  for (l = 0; l <= K; l++) for (c = 0; c < K; c++) for (r = 0; r <= K; r++) T[l][c][r] = rnd() % K;
  T[0][0][0] = 0; T[0][0][K] = 0;
  long cur = score(1), best = cur; long long ev, since = 0;
  unsigned char bestT[MAXK + 1][MAXK][MAXK + 1]; memcpy(bestT, T, sizeof T);
  for (ev = 0; ev < maxevals; ev++) {
    /* pick a used, non-fixed entry */
    int tries = 0;
    do { l = rnd() % (K + 1); c = rnd() % (K - 1); r = rnd() % (K + 1); tries++; }
    while ((!used[l][c][r] || fixed(l, c, r) || (l == K && r == K)) && tries < 10000);
    unsigned char old = T[l][c][r];
    do randomize_entry(l, c, r); while (T[l][c][r] == old);
    long s = score(1);
    if (s >= cur) {
      if (s > cur) since = 0; else since++;
      cur = s;
      if (s > best) {
        best = s; memcpy(bestT, T, sizeof T);
        fprintf(stdout, "eval %lld best %ld (lengths 2..%ld)\n", ev, best, best / 1000 + 1);
        fflush(stdout);
        if (out) write_table(out);
      }
    } else { T[l][c][r] = old; score(1); since++; }
    if (since > STALL) {                     /* perturbation from the best table */
      memcpy(T, bestT, sizeof T); score(1);
      int p;
      for (p = 0; p < PERT; p++) {
        int tr = 0;
        do { l = rnd() % (K + 1); c = rnd() % (K - 1); r = rnd() % (K + 1); tr++; }
        while ((!used[l][c][r] || fixed(l, c, r) || (l == K && r == K)) && tr < 10000);
        randomize_entry(l, c, r);
      }
      cur = score(1); since = 0;
    }
  }
  memcpy(T, bestT, sizeof T);
  printf("final best %ld (lengths 2..%ld)\n", best, best / 1000 + 1);
  if (out) write_table(out);
  return 0;
}

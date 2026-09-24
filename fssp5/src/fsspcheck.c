/*
 * fsspcheck.c -- independent brute-force checker for firing squad rules.
 *
 * Reads a rule table and simulates the line of n cells, n = nmin..nmax,
 * started from  G L L ... L  with the boundary symbol '*' on both sides.
 * It reports whether every line fires exactly at time 2n-2 (minimal time),
 * i.e. all cells are in F at time 2n-2 and no cell is in F before.
 *
 * Rule file format (whitespace separated tokens, '#' starts a comment):
 *     k <number of states>
 *     <l> <c> <r> <d>        one line per defined transition
 * State symbols:  L (quiescent) = 0, G (general) = 1, auxiliary states
 * A, B, C, ... = 2 .. k-2, F (fire) = k-1, and '*' for the boundary.
 *
 * Usage: fsspcheck rulefile nmin nmax [-v]
 *   -v prints the space-time diagram of every simulated line.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAXK 16
#define BND MAXK /* boundary code */
static int K;
static int table[MAXK + 1][MAXK][MAXK + 1]; /* -1 = undefined */

static int sym2code(char ch) {
  if (ch == '*') return BND;
  if (ch == 'L') return 0;
  if (ch == 'G') return 1;
  if (ch == 'F') return K - 1;
  if (ch >= 'A' && ch <= 'E' && ch - 'A' + 2 <= K - 2) return ch - 'A' + 2;
  if (ch >= 'H' && ch <= 'K' && ch - 'H' + 2 + 5 <= K - 2) return ch - 'H' + 7;
  fprintf(stderr, "bad symbol %c\n", ch);
  exit(2);
}

static char code2sym(int c) {
  if (c == BND) return '*';
  if (c == 0) return 'L';
  if (c == 1) return 'G';
  if (c == K - 1) return 'F';
  if (c - 2 < 5) return (char)('A' + c - 2);
  return (char)('H' + c - 7);
}

int main(int argc, char **argv) {
  if (argc < 4) {
    fprintf(stderr, "usage: %s rulefile nmin nmax [-v]\n", argv[0]);
    return 2;
  }
  int verbose = argc > 4 && !strcmp(argv[4], "-v");
  FILE *f = fopen(argv[1], "r");
  if (!f) { perror(argv[1]); return 2; }
  memset(table, -1, sizeof table);
  char tok[4][64];
  char line[512];
  K = 0;
  while (fgets(line, sizeof line, f)) {
    char *h = strchr(line, '#');
    if (h) *h = 0;
    int m = sscanf(line, "%63s %63s %63s %63s", tok[0], tok[1], tok[2], tok[3]);
    if (m <= 0) continue;
    if (m == 2 && !strcmp(tok[0], "k")) {
      K = atoi(tok[1]);
      if (K < 3 || K > MAXK) { fprintf(stderr, "bad k\n"); return 2; }
      continue;
    }
    if (m != 4 || !K) { fprintf(stderr, "bad line: %s\n", line); return 2; }
    int l = sym2code(tok[0][0]), c = sym2code(tok[1][0]);
    int r = sym2code(tok[2][0]), d = sym2code(tok[3][0]);
    if (c == BND || d == BND) { fprintf(stderr, "bad line: %s\n", line); return 2; }
    if (table[l][c][r] != -1 && table[l][c][r] != d) {
      fprintf(stderr, "conflicting entries for %s %s %s\n", tok[0], tok[1], tok[2]);
      return 2;
    }
    table[l][c][r] = d;
  }
  fclose(f);
  /* the quiescent conditions of the problem statement */
  if (table[0][0][0] != 0 || table[0][0][BND] != 0) {
    printf("FAIL quiescent condition d(L,L,L)=d(L,L,*)=L violated\n");
    return 1;
  }
  int nmin = atoi(argv[2]), nmax = atoi(argv[3]);
  if (nmin < 2) nmin = 2;
  int *cur = malloc((nmax + 2) * sizeof(int));
  int *nxt = malloc((nmax + 2) * sizeof(int));
  for (int n = nmin; n <= nmax; n++) {
    int T = 2 * n - 2;
    cur[0] = cur[n + 1] = nxt[0] = nxt[n + 1] = BND;
    cur[1] = 1;
    for (int i = 2; i <= n; i++) cur[i] = 0;
    for (int t = 0; t <= T; t++) {
      if (verbose) {
        printf("n=%d t=%3d  ", n, t);
        for (int i = 1; i <= n; i++) putchar(code2sym(cur[i]));
        putchar('\n');
      }
      int nf = 0;
      for (int i = 1; i <= n; i++) nf += cur[i] == K - 1;
      if (t < T && nf) {
        printf("FAIL n=%d: a cell fires at time %d < %d\n", n, t, T);
        return 1;
      }
      if (t == T) {
        if (nf != n) {
          printf("FAIL n=%d: only %d of %d cells fire at time %d\n", n, nf, n, T);
          return 1;
        }
        break;
      }
      for (int i = 1; i <= n; i++) {
        int d = table[cur[i - 1]][cur[i]][cur[i + 1]];
        if (d < 0) {
          printf("UNDEF n=%d t=%d cell %d uses undefined entry (%c,%c,%c)\n", n, t, i,
                 code2sym(cur[i - 1]), code2sym(cur[i]), code2sym(cur[i + 1]));
          return 3;
        }
        nxt[i] = d;
      }
      int *tmp = cur; cur = nxt; nxt = tmp;
    }
  }
  printf("OK: fires exactly at time 2n-2 for all %d <= n <= %d\n", nmin, nmax);
  return 0;
}

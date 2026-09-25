/*
 * germext2.c -- streaming version of the left-border check of germext.c for
 * very long lines.
 *
 * For each input germ ("GERM l c r>d ..."), the half-line diagram is computed
 * row by row (memory O(T)) on the cells with t+i <= T = 2N-2, recording the two
 * input anti-diagonals of the line of length N.  If the germ determines all
 * these cells, the left-border lemma is checked for s <= SMAX, L <= LMAX:
 * a stretch [s,Y], Y <= N-s, on which y -> C(2N-2-y,y) (s<=y<=Y) and
 * y -> C(2N-3-y,y) (s<=y<=Y-1) are L-periodic with Y-s > (k-1)^(2s) L refutes
 * the germ.  Output: "<line> CLOSED|OPEN m [REFUTED N s L Y]".
 *
 * usage: germext2 k N SMAX LMAX < germs.txt
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define BND 7
static signed char tab[8][8][8];

static int code(char ch, int K) {
  switch (ch) {
  case '*': return BND;
  case 'L': return 0;
  case 'G': return 1;
  case 'F': return K - 1;
  default: return 2 + (ch - 'A');
  }
}

int main(int argc, char **argv) {
  if (argc < 5) { fprintf(stderr, "usage: %s k N SMAX LMAX < germs\n", argv[0]); return 2; }
  int K = atoi(argv[1]), N = atoi(argv[2]), SMAX = atoi(argv[3]), LMAX = atoi(argv[4]);
  int T = 2 * N - 2;
  unsigned char *cur = malloc(T + 4), *nxt = malloc(T + 4);
  unsigned char *up = malloc(T + 2), *lo = malloc(T + 2); /* up[t] = C(t,T-t), lo[t] = C(t,T-1-t) */
  static char line[1 << 16];
  int lineno = 0;
  while (fgets(line, sizeof line, stdin)) {
    char *p = strstr(line, "GERM");
    if (!p) continue;
    lineno++;
    memset(tab, -1, sizeof tab);
    tab[0][0][0] = 0;
    for (char *tok = strtok(p + 4, " \n"); tok; tok = strtok(NULL, " \n")) {
      if (strlen(tok) != 5 || tok[3] != '>') continue;
      tab[code(tok[0], K)][code(tok[1], K)][code(tok[2], K)] = (signed char)code(tok[4], K);
    }
    memset(cur, 0, T + 4);
    cur[1] = 1; /* time 0: G at cell 1 */
    memset(up, 255, T + 2);
    memset(lo, 255, T + 2);
    int open_at = -1;
    for (int t = 1; t < T; t++) {
      int imax = T - t; /* cells with t+i <= T */
      for (int i = 1; i <= imax; i++) {
        if (i > t + 1) { nxt[i] = 0; continue; }
        int a = (i == 1) ? BND : cur[i - 1], b = cur[i], c = cur[i + 1];
        int d;
        if (a == 255 || b == 255 || c == 255 || tab[a][b][c] < 0) {
          d = 255;
          if (open_at < 0 || t + i < open_at) open_at = t + i;
        } else d = tab[a][b][c];
        nxt[i] = (unsigned char)d;
      }
      nxt[imax + 1] = 255; /* beyond the computed range */
      up[t] = nxt[T - t];
      if (T - 1 - t >= 1) lo[t] = nxt[T - 1 - t];
      unsigned char *tmp = cur; cur = nxt; nxt = tmp;
    }
    if (open_at >= 0) { printf("%d OPEN %d\n", lineno, open_at); fflush(stdout); continue; }
    /* words: U(y) = C(T-y,y) = up[T-y], Lw(y) = C(T-1-y,y) = lo[T-1-y] */
    int found = 0;
    for (int s = 1; s <= SMAX && !found; s++) {
      double pw = 1;
      for (int e = 0; e < 2 * s; e++) pw *= (K - 1);
      for (int L = 1; L <= LMAX && !found; L++) {
        double bound = pw * L;
        if (bound >= N) break;
        int Y = s + L - 1;
        while (Y + 1 <= N - s) {
          int y = Y + 1;
          if (y - L >= s && up[T - y] != up[T - y + L]) break;
          int x = y - 1;
          if (x - L >= s && lo[T - 1 - x] != lo[T - 1 - x + L]) break;
          Y = y;
        }
        if (Y - s > bound) { printf("%d CLOSED REFUTED N=%d s=%d L=%d Y=%d\n", lineno, N, s, L, Y); found = 1; }
      }
    }
    if (!found) printf("%d CLOSED\n", lineno);
    fflush(stdout);
  }
  return 0;
}

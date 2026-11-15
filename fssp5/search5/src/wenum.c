/*
 * wenum.c -- second, independent enumerator for the stable-general class (cross-check of mdfs.c).
 *
 * States L=0 G=1 A=2 B=3 F=4, border 5.  Class: delta(x,G,y) = G unless x and y are both G or the border, in
 * which case it is F; no other neighbourhood gives F.  A partial rule is extended only when a diagram needs
 * a transition (values L, G, A, B).  Order of the enumeration: for n = 2, ..., N first the half-line on the
 * anti-diagonals up to t + i = 2n-1, then the cells of the line n below its anti-diagonal 2n-2, row by row.
 * Conditions (the formula Phi_N of README.md with the wall lemma):
 *   half-line (t + i <= 2N-1): no F; the first cell is G and no other cell is G; the front cell (t, t+1) is not
 *     L for t <= N-2;
 *   line n: it agrees with the half-line for t + i <= 2n-2 (used, not checked); no F before time 2n-2; every
 *     cell is F at time 2n-2; on the anti-diagonal t + i = 2n-1 the line differs from the half-line.
 * Transitions listed on standard input (lines "x y z d") are fixed in advance.
 * Output: the number of partial rules that satisfy all conditions, and the number of branching nodes.
 *
 * usage: wenum N [maxnodes] < cube.txt
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
enum { L = 0, G = 1, A = 2, B = 3, F = 4, BD = 5 };
static int N, tab[6][4][6];
static int H[80][80];                 /* half-line H[t][i], i >= 1; H[t][i] = L for i > t + 1 */
static int C[40][80][42];             /* C[n][t][i] for the cells with t + i >= 2n-1 */
static long long nodes, sols, maxnodes;
static int code(char c) { return c == '*' ? BD : c == 'L' ? L : c == 'G' ? G : c == 'A' ? A : c == 'B' ? B : F; }
static int look(int x, int y, int z) {
  if (y == G) return ((x == G || x == BD) && (z == G || z == BD)) ? F : G;
  return tab[x][y][z];
}
static int cell(int n, int t, int i) {          /* state of the cell (t, i) of the line n, or the border */
  if (i < 1 || i > n) return BD;
  return (t + i <= 2 * n - 2) ? H[t][i] : C[n][t][i];
}
static void tri(int n, int t, int i);
static void halfdiag(int n, int m, int t) {     /* half-line: anti-diagonals m.., up to 2n-1; cell (t, m - t) */
  if (maxnodes && nodes > maxnodes) return;
  for (;;) {
    if (t > m - 1) { m++; t = 1; }
    if (m > 2 * n - 1) { tri(n, n - 1, 1); return; }
    int i = m - t;
    if (i > t + 1) { t++; continue; }
    int x = (i == 1) ? BD : H[t - 1][i - 1], y = H[t - 1][i], z = H[t - 1][i + 1];
    int v = look(x, y, z);
    if (v < 0) {
      nodes++;
      for (int d = 0; d < 4; d++) {
        tab[x][y][z] = d;
        halfdiag(n, m, t);
        if (maxnodes && nodes > maxnodes) break;
      }
      tab[x][y][z] = -1;
      return;
    }
    if (v == F) return;
    if (i == 1 ? v != G : v == G) return;
    if (i == t + 1 && t <= N - 2 && v == L) return;
    H[t][i] = v;
    t++;
  }
}
static void tri(int n, int t, int i) {          /* line n: cells (t, i) with t + i >= 2n-1, t = n-1 .. 2n-2 */
  if (maxnodes && nodes > maxnodes) return;
  for (;;) {
    if (i > n) { t++; i = 1; }
    if (t > 2 * n - 2) {
      if (n == N) { sols++; return; }
      halfdiag(n + 1, 2 * n, 1);
      return;
    }
    if (t + i <= 2 * n - 2) { i++; continue; }
    int x = cell(n, t - 1, i - 1), y = cell(n, t - 1, i), z = cell(n, t - 1, i + 1);
    int v = look(x, y, z);
    if (v < 0) {
      if (t == 2 * n - 2) return;                 /* only the three neighbourhoods of generals give F */
      nodes++;
      for (int d = 0; d < 4; d++) {
        tab[x][y][z] = d;
        tri(n, t, i);
        if (maxnodes && nodes > maxnodes) break;
      }
      tab[x][y][z] = -1;
      return;
    }
    if (t == 2 * n - 2) { if (v != F) return; }
    else {
      if (v == F) return;
      if (t + i == 2 * n - 1 && i >= 2 && v == H[t][i]) return;             /* return chain */
    }
    C[n][t][i] = v;
    i++;
  }
}
int main(int argc, char **argv) {
  N = atoi(argv[1]);
  maxnodes = argc > 2 ? atoll(argv[2]) : 0;
  memset(tab, -1, sizeof tab);
  tab[L][L][L] = L; tab[L][L][BD] = L;
  char a[8], b[8], c[8], d[8], line[256];
  while (fgets(line, sizeof line, stdin))
    if (line[0] != 'k' && line[0] != '#' && sscanf(line, "%7s %7s %7s %7s", a, b, c, d) == 4)
      tab[code(a[0])][code(b[0])][code(c[0])] = code(d[0]);
  for (int t = 0; t < 80; t++) for (int i = 0; i < 80; i++) H[t][i] = L;
  H[0][1] = G;
  halfdiag(2, 2, 1);
  printf("wenum N=%d: rules %lld, nodes %lld%s\n", N, sols, nodes, (maxnodes && nodes > maxnodes) ? " (node limit reached)" : "");
  return 0;
}

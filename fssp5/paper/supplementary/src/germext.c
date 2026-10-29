/*
 * germext.c -- extend half-line germs far beyond anti-diagonal 78 and apply
 * the left-border lemma.
 *
 * For each input line "GERM l c r>d ..." (output of germdfs), the half-line
 * diagram C_inf is simulated with the germ's transitions only, on all cells
 * (t,i) with t+i <= MBIG.  If some cell needs a neighbourhood that is not in
 * the germ, the germ does not determine the half-line that far; we report the
 * anti-diagonal where this first happens ("OPEN m").  Otherwise ("CLOSED") we
 * look for a length n with 2n-2 <= MBIG, integers s >= 1, L >= 1 and a stretch
 * [s,Y], Y <= n-s, on which the words
 *     y -> C_inf(2n-2-y, y)   (s <= y <= Y)   and
 *     y -> C_inf(2n-3-y, y)   (s <= y <= Y-1)
 * are L-periodic with Y - s > (k-1)^(2s) L.  By the left-border lemma no rule
 * containing the germ synchronizes the line of length n in minimal time, so
 * the germ is refuted ("REFUTED n s L Y").  Also reported: firing cells and
 * front L beyond anti-diagonal 78 (which refute the germ as well).
 *
 * usage: germext k MBIG SMAX LMAX [PMAX] < germs.txt
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define BND 7
static int K, MBIG, SMAX, LMAX, PMAX;
static signed char tab[8][8][8];
static unsigned char *C; /* C[t*(MBIG+3)+i] */
static int WID;

static int code(char ch) {
  switch (ch) {
  case '*': return BND;
  case 'L': return 0;
  case 'G': return 1;
  case 'F': return 4 < K ? K - 1 : 4;
  default: return 2 + (ch - 'A');
  }
}

#define CV(t, i) C[(size_t)(t) * WID + (i)]

int main(int argc, char **argv) {
  if (argc < 5) { fprintf(stderr, "usage: %s k MBIG SMAX LMAX [PMAX] < germs\n", argv[0]); return 2; }
  K = atoi(argv[1]); MBIG = atoi(argv[2]); SMAX = atoi(argv[3]); LMAX = atoi(argv[4]);
  PMAX = argc > 5 ? atoi(argv[5]) : MBIG / 2; /* pumping pairs n < n2 <= PMAX */
  WID = MBIG + 3;
  C = malloc((size_t)(MBIG + 2) * WID);
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
      tab[code(tok[0])][code(tok[1])][code(tok[2])] = (signed char)code(tok[4]);
    }
    /* simulate: C(0,1)=G, C(0,i)=L; cells with i > t+1 are L.  Value 255 marks a
       cell that the germ does not determine (unknown neighbourhood, or an
       undetermined neighbour). */
    int open_at = -1, fire_at = -1, frontL_at = -1;
    for (int i = 0; i < WID; i++) CV(0, i) = 0;
    CV(0, 1) = 1;
    for (int t = 1; t < MBIG; t++) {
      for (int i = 1; i + t <= MBIG; i++) {
        if (i > t + 1) { CV(t, i) = 0; continue; }
        int a = (i == 1) ? BND : CV(t - 1, i - 1), b = CV(t - 1, i), c = CV(t - 1, i + 1);
        int d;
        if (a == 255 || b == 255 || c == 255 || tab[a][b][c] < 0) {
          d = 255;
          if (open_at < 0 || t + i < open_at) open_at = t + i;
        } else {
          d = tab[a][b][c];
          if (d == K - 1 && (fire_at < 0 || t + i < fire_at)) fire_at = t + i;
          if (i == t + 1 && d == 0 && (frontL_at < 0 || t + i < frontL_at)) frontL_at = t + i;
        }
        CV(t, i) = (unsigned char)d;
      }
    }
    int reach = open_at < 0 ? MBIG : open_at - 1; /* anti-diagonals <= reach are determined */
    printf("%d %s reach=%d", lineno, open_at < 0 ? "CLOSED" : "OPEN", reach);
    if (fire_at >= 0 && fire_at <= reach) printf(" FIRE %d", fire_at);
    if (frontL_at >= 0 && frontL_at <= reach) printf(" FRONTL %d", frontL_at);
    /* left-border lemma on every length n with 2n-2 <= reach */
    int found = 0;
    for (int n = 4; 2 * n - 2 <= reach && !found; n++) {
      for (int s = 1; s <= SMAX && !found; s++) {
        double pw = 1;
        for (int e = 0; e < 2 * s; e++) pw *= (K - 1);
        for (int L = 1; L <= LMAX && !found; L++) {
          double bound = pw * L;
          if (bound >= n) break; /* Y - s <= n - 2s can never exceed it */
          /* extend Y from s+L-1 while periodic */
          int Y = s + L - 1;
          while (Y + 1 <= n - s) {
            int y = Y + 1;
            if (y - L >= s && CV(2 * n - 2 - y, y) != CV(2 * n - 2 - y + L, y - L)) break;
            int x = y - 1;
            if (x - L >= s && CV(2 * n - 3 - x, x) != CV(2 * n - 3 - x + L, x - L)) break;
            Y = y;
          }
          if (Y - s > bound) {
            printf(" REFUTED n=%d s=%d L=%d Y=%d", n, s, L, Y);
            found = 1;
          }
        }
      }
    }
    /* pumping lemma for 4 <= n < n2, 2*n2-2 <= reach: J_n and J_n2 must differ
       on cone_n(n-1,0): both input cells at 1..floor(n/2), the lower cell at
       (n+1)/2 when n is odd (the upper cell at 0 is L for every length) */
    int pviol = 0, pn = 0, pn2 = 0;
    for (int n2 = 5; 2 * n2 - 2 <= reach && n2 <= PMAX && !pviol; n2++) {
      for (int n = 4; n < n2 && !pviol; n++) {
        int diff = 0;
        for (int kk = 1; kk <= n / 2 && !diff; kk++) {
          if (CV(n - 3 + kk, n - kk) != CV(n2 - 3 + kk, n2 - kk)) diff = 1;
          else if (CV(n - 2 + kk, n - kk) != CV(n2 - 2 + kk, n2 - kk)) diff = 1;
        }
        if (!diff && (n % 2)) {
          int kk = (n + 1) / 2;
          if (CV(n - 3 + kk, n - kk) != CV(n2 - 3 + kk, n2 - kk)) diff = 1;
        }
        if (!diff) { pviol = 1; pn = n; pn2 = n2; }
      }
    }
    if (pviol) printf(" PUMPFAIL n=%d n2=%d", pn, pn2);
    printf("\n");
    fflush(stdout);
  }
  return 0;
}

#!/bin/bash
# check_quick.sh -- every computational statement of the paper that needs only Python 3 (with PySAT)
# and a C compiler: simulations, enumerations, satisfiable formulas, and the digests of the
# unsatisfiable four-state formulas.  The unsatisfiable formulas themselves are certified by
# check_certificates.sh.  Run from any directory; about 7 minutes on one core.
set -e
H=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$H/cnf"
TMPD=$(mktemp -d)
trap 'rm -rf "$TMPD"' EXIT
sec() { echo; echo "=== $*"; }

sec "building the C programs"
cd "$H/src"
gcc -O2 -o fsspcheck fsspcheck.c
gcc -O3 -o fsspdfs fsspdfs.c
gcc -O2 -o germdfs germdfs.c
gcc -O2 -o germext germext.c

sec "Remark 3.5: theta(j) and PUMP (simulations)"
python3 theta.py ../results/mazoyer6.txt 2600 699 1 | grep -E "horizon|- 2j|periods"
python3 theta.py ../results/uniformA_2-12.txt 1400 300 10 | grep -E "horizon|ceil|periods"
python3 pumping.py ../results/uniformA_2-12.txt 650 | tail -1

sec "Section 6.1, validation: Mazoyer's solution"
./fsspcheck ../results/mazoyer6.txt 3 3000
python3 validate_mazoyer.py 12 78 40 | grep "symbreak=False"
cd "$H/research"
python3 ../src/germcompare.py --germline ../results/mazoyer6.txt 3000 > "$TMPD/g_mazoyer.txt"
OUT=$(python3 asymp.py "$TMPD/g_mazoyer.txt" 8 15)
echo "$OUT" | sed -n 1p
REPS=$(echo "$OUT" | tail -1)
echo "(G2), (G3) for T = 8 and all n >= 15, Mazoyer's table fixed:"
python3 gfix.py "$TMPD/g_mazoyer.txt" 6 $REPS --fix ../results/mazoyer6.txt --solve cadical | grep '^cadical'

sec "Section 6.1, validation: the table of delta14 fixed"
for spec in "full:2-14" "full:2-15" "full:2-14 early:15-30:6" "full:2-14 early:15-30:8"; do
  echo "$spec: $(python3 gfix.py FREE 5 $spec --fix ../results/delta14.txt --solve cadical | grep '^cadical')"
done

sec "Theorem 6.1: the three formulas (certified by check_certificates.sh)"
(cd "$H/src" && python3 gencnf.py 4 9 ../cnf/mt4_9.cnf)
GFIX_SHARE=1 python3 gfix.py FREE 4 full:2-7 early:8-10:6 --cnf ../cnf/k4_G6.cnf | cut -c1-110
GFIX_SHARE=1 python3 gfix.py FREE 4 full:2-5 early:6-10:4 cone:6-10 --cnf ../cnf/k4_G4c.cnf | cut -c1-110
(cd "$H" && grep -v k14_n10 SHA256SUMS | sha256sum -c -)

sec "Proposition 6.2: sharpness (enumeration and satisfiable weakenings)"
cd "$H/src"
./fsspdfs 4 8 -s 2>/dev/null | grep -v '^SOL'
echo "partial rules for the lengths 2..8: $(./fsspdfs 4 8 -s 2>/dev/null | grep -c '^SOL'); using (*,L,L): $(./fsspdfs 4 8 -s 2>/dev/null | grep '^SOL' | grep -c '\*LL>' || true)"
./fsspdfs 4 9 2>/dev/null
cd "$H/research"
for spec in "full:2-6 early:7-30:5" "full:2-7 early:8-9:6" "full:2-5 early:6-30:4 cone:6-9" "full:2-4 early:5-30:3 cone:5-12" "full:2-5 cone:6-12"; do
  echo "$spec: $(GFIX_SHARE=1 python3 gfix.py FREE 4 $spec --solve cadical | grep '^cadical')"
done
echo "full:2-7 early:8-10:6 without (G3): $(GFIX_NORC=8,9,10 GFIX_SHARE=1 python3 gfix.py FREE 4 full:2-7 early:8-10:6 --solve cadical | grep '^cadical')"

sec "Proposition 6.3: the five rules delta14, delta14b, ..., delta14e"
cd "$H/src"
for r in delta14 delta14b delta14c delta14d delta14e; do
  ./fsspcheck ../results/$r.txt 2 14
  python3 firstfire.py ../results/$r.txt 15 60 | grep "every line"
done
cd "$H/research"
for rt in "delta14 10" "delta14b 14" "delta14c 22" "delta14d 12" "delta14e 14"; do
  set -- $rt
  echo "$1, T = $2:"
  python3 failall.py ../results/$1.txt $2 | sed 's/^/  /'
done

sec "Section 6.3, after Proposition 6.3: the half-line of delta14, delta12, delta13, and the seven rules"
cd "$H/src"
python3 halflines.py values ../results/delta14.txt 1500
./germext 5 10000 3 24 800 < ../results/germs/germ_delta14.txt
for r in uniformA_2-12 delta13; do python3 firstfire.py ../results/$r.txt 2 60 9 | grep -E "^\.\.|synchronized at|smallest"; done
for r in delta14 delta14b delta14c delta14d delta14e; do python3 firstfire.py ../results/$r.txt 2 60 9 | grep -E "^\.\.|smallest"; done

sec "Proposition 6.4, the remark after it, and Table 5: germs of complexity at most 14"
python3 germcompare.py ../results/mazoyer6.txt 78 | sed -n 1p
python3 germcompare.py ../results/uniformA_2-12.txt 78 | sed -n 1p
python3 germcompare.py ../results/delta13.txt 78 | sed -n 1p
python3 germcompare.py ../results/delta14.txt 78 | sed -n 1p
python3 germcompare.py ../results/delta14b.txt 78 | sed -n 1p
python3 germcompare.py ../results/delta14c.txt 78 | sed -n 1p
python3 germcompare.py ../results/delta14d.txt 78 | sed -n 1p
python3 germcompare.py ../results/delta14e.txt 78 | sed -n 1p
./germdfs 5 78 14 40 | cmp - ../results/germs/germs_K14.txt && echo "germdfs: the 244 germs of results/germs/germs_K14.txt"
python3 germdfs_check.py 14 78 40 > "$TMPD/germs_check.txt"
grep -v '^GERM' "$TMPD/germs_check.txt"
python3 -c "
def germs(p): return {tuple(sorted(l.split()[1:])) for l in open(p) if l.startswith('GERM')}
a, b = germs('$TMPD/germs_check.txt'), germs('../results/germs/germs_K14.txt')
print('germdfs_check.py (independent): the same germs as results/germs/germs_K14.txt:', a == b, len(a))"
python3 germinc.py ../results/germs/germs_K14.txt 10 78 | tail -1
./germext 5 3300 3 12 < ../results/germs/germs_K14_surv10.txt
python3 germ_k14_check.py | awk '/survivors/ {print "germ_k14_check.py: " $0} /applies/ {c++} END {print "  Lemma 4.1 applies (s = 1) to " c " of them"}'

sec "Corollary 6.5: the half-line of delta12 and delta13"
python3 germcompare.py ../results/uniformA_2-12.txt ../results/delta13.txt 78 | tail -1
python3 germcompare.py --germline ../results/uniformA_2-12.txt 78 | cmp - ../results/germs/germ_delta12.txt && echo "the 22 transitions = results/germs/germ_delta12.txt"
python3 antidiag.py ../results/uniformA_2-12.txt 1034 1034 2 260 1033 2 259 | grep -v '^GERM'
./germext 5 1300 3 6 < ../results/germs/germ_delta12.txt

sec "Proposition 6.6: the rule for the lengths up to 11 (the formulas: check_certificates.sh)"
./fsspcheck ../results/balzer_sym11.txt 2 11
./fsspcheck ../results/balzer_sym11.txt 12 12 || true

sec "Section 7: the two models of the germ of delta14d"
cd "$H/research"
python3 models_check.py

sec "Figures 1, 6, 7 and 12-18, Table 4, and the dependency cones of Section 7"
cd "$H/src"
python3 figures.py "$TMPD/figures"

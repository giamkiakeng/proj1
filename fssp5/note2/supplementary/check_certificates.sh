#!/bin/bash
# check_certificates.sh -- the unsatisfiable formulas of the note, with LRAT proofs checked by lrat-check.
#
# Needs CaDiCaL (version 2 or later, which writes LRAT; we used 3.0.1), Kissat (we used 4.0.4),
# drat-trim and lrat-check.  Binaries: the variables CADICAL, KISSAT, DRATTRIM, LRATCHECK, else the PATH.
# Writes the formulas and proofs to cnf/ (about 4 GB, most of it the proof of the Kissat case).
# Times on one core: about 30 minutes, of which about 20 for the Kissat case of Proposition 6.5.
set -e
H=$(cd "$(dirname "$0")" && pwd)
export CADICAL=${CADICAL:-$(command -v cadical || echo cadical)}
export KISSAT=${KISSAT:-$(command -v kissat || echo kissat)}
export DRATTRIM=${DRATTRIM:-$(command -v drat-trim || echo drat-trim)}
export LRATCHECK=${LRATCHECK:-$(command -v lrat-check || echo lrat-check)}
mkdir -p "$H/cnf"
export TMPDIR="$H/cnf"        # balzer.py and balzer_k.py write their formulas and proofs to $TMPDIR/balzer_*/
sec() { echo; echo "=== $*"; }

sec "Theorem 6.1 (i)-(iii): formulas, digests, LRAT proofs"
(cd "$H/src" && python3 gencnf.py 4 9 ../cnf/mt4_9.cnf)
cd "$H/research"
GFIX_SHARE=1 python3 gfix.py FREE 4 full:2-7 early:8-10:6 --cnf ../cnf/k4_G6.cnf | cut -c1-110
GFIX_SHARE=1 python3 gfix.py FREE 4 full:2-5 early:6-10:4 cone:6-10 --cnf ../cnf/k4_G4c.cnf | cut -c1-110
(cd "$H" && grep -v k14_n10 SHA256SUMS | sha256sum -c -)
for f in mt4_9 k4_G6 k4_G4c; do
  echo "$f:"
  ./certify_lrat.sh ../cnf/$f.cnf | sed 's/^/  /'
done

sec "Proposition 6.3: one LRAT certificate for the 230 refuted germs"
cd "$H/src"
python3 germcert.py ../results/germs/K14_refuted10.txt 10 ../cnf/k14_n10
(cd "$H" && grep k14_n10 SHA256SUMS | sha256sum -c -)

sec "Proposition 6.5: Balzer's conditions"
python3 balzer.py 10 1234 AB --lrat
python3 balzer.py 9 1234 LA --lrat
python3 balzer.py 9 1234 LB --lrat
python3 balzer_k.py 5 12 1234 id --cnf=../cnf/w.cnf
set +e; "$KISSAT" -q ../cnf/w.cnf ../cnf/w.drat | grep '^s '; set -e
"$DRATTRIM" ../cnf/w.cnf ../cnf/w.drat -L ../cnf/w.lrat | grep '^s '
"$LRATCHECK" ../cnf/w.cnf ../cnf/w.lrat | grep -E "VERIFIED|FAIL|ERROR"
python3 balzer.py 11 1234s id | grep -E "SATISFIABLE|rule"
sha256sum ../cnf/w.cnf


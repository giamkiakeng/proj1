#!/bin/bash
# check_certificates.sh -- the unsatisfiable formulas of the paper, with LRAT proofs checked by lrat-check.
#
# Needs CaDiCaL (version 2 or later, which writes LRAT; we used 3.0.1), Kissat (we used 4.0.4),
# drat-trim and lrat-check.  Binaries: the variables CADICAL, KISSAT, DRATTRIM, LRATCHECK, else the PATH.
# Writes the formulas and proofs to cnf/ (about 5 GB, most of it the proofs of the Kissat case).
# Times on one core: about an hour, most of it for the Kissat case of Proposition 6.6 (Kissat about
# 15 minutes, drat-trim about 30 minutes).  Then the proofs written to cnf/ are compared with the
# digests recorded in formulas/PROOFS.sha256 (the Balzer proofs with results/balzer.log).  Finally,
# the eight formulas of the second encoder (src/encode_independent.py, Section 6.1, check (5)) are
# written to cnf/independent/ and refuted in the same way, each proof checked with lrat-check
# (about another hour and 5 GB).  With the argument --second-encoder, only this last part is run.
# If the variable CAKELPR names the binary of cake_lpr (https://github.com/tanyongkiam/cake_lpr, we used
# commit 033aad5), every proof is also checked with this formally verified checker.
set -e
H=$(cd "$(dirname "$0")" && pwd)
export CADICAL=${CADICAL:-$(command -v cadical || echo cadical)}
export KISSAT=${KISSAT:-$(command -v kissat || echo kissat)}
export DRATTRIM=${DRATTRIM:-$(command -v drat-trim || echo drat-trim)}
export LRATCHECK=${LRATCHECK:-$(command -v lrat-check || echo lrat-check)}
mkdir -p "$H/cnf"
export TMPDIR="$H/cnf"        # balzer.py and balzer_k.py write their formulas and proofs to $TMPDIR/balzer_*/
sec() { echo; echo "=== $*"; }

if [ "$1" != "--second-encoder" ]; then      # with --second-encoder, only the last section is run

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

sec "Proposition 6.4: one LRAT certificate for the 230 refuted germs"
cd "$H/src"
python3 germcert.py ../results/germs/K14_refuted10.txt 10 ../cnf/k14_n10
(cd "$H" && grep k14_n10 SHA256SUMS | sha256sum -c -)

sec "Proposition 6.6: Balzer's conditions"
python3 balzer.py 10 1234 AB --lrat
python3 balzer.py 9 1234 LA --lrat
python3 balzer.py 9 1234 LB --lrat
python3 balzer_k.py 5 12 1234 id --cnf=../cnf/w.cnf
set +e
"$KISSAT" -q ../cnf/w.cnf ../cnf/w.drat | grep '^s '
"$DRATTRIM" ../cnf/w.cnf ../cnf/w.drat -L ../cnf/w.lrat > ../cnf/w.drat-trim.log 2>&1
echo "drat-trim (exit code $?): $(grep '^s ' ../cnf/w.drat-trim.log || echo 'no verdict line; the LRAT file is checked next')"
set -e
"$LRATCHECK" ../cnf/w.cnf ../cnf/w.lrat | grep -E "VERIFIED|FAIL|ERROR"
sha256sum ../cnf/w.cnf ../cnf/w.lrat
python3 balzer.py 11 1234s id | grep -E "SATISFIABLE|rule"

sec "the regenerated proofs against the recorded digests"
(cd "$H" && sha256sum -c formulas/PROOFS.sha256)

if [ -n "$CAKELPR" ]; then
sec "the same proofs checked again with cake_lpr, a formally verified checker"
cd "$H/cnf"
for f in mt4_9 k4_G6 k4_G4c k14_n10 w; do
  echo "$f: $("$CAKELPR" --CML_HEAP_SIZE=6000 --CML_STACK_SIZE=4000 $f.cnf $f.lrat 2>&1)"
done
for d in balzer_*/; do
  if [ -f "$d/f.lrat" ]; then
    echo "$d: $("$CAKELPR" --CML_HEAP_SIZE=6000 --CML_STACK_SIZE=4000 "$d/f.cnf" "$d/f.lrat" 2>&1)"
  fi
done
fi
fi

sec "Section 6.1, check (5): the eight formulas of the second encoder, with LRAT proofs"
cd "$H/src"
python3 encode_independent.py write ../cnf/independent | sed 's/ written to .*//'
for f in mt4_9 k4_G6 k4_G4c k14_n10 balzer_AB_10 balzer_LA_9 balzer_LB_9; do
  echo "$f:"
  "$H/research/certify_lrat.sh" ../cnf/independent/$f.cnf | sed 's/^/  /'
done
echo "balzer_id_12:"
I=../cnf/independent/balzer_id_12
set +e
"$KISSAT" -q $I.cnf $I.drat | grep '^s ' | sed 's/^/  /'
"$DRATTRIM" $I.cnf $I.drat -L $I.lrat > $I.drat-trim.log 2>&1
echo "  drat-trim (exit code $?): $(grep '^s ' $I.drat-trim.log || echo 'no verdict line; the LRAT file is checked next')"
set -e
"$LRATCHECK" $I.cnf $I.lrat | grep -E "VERIFIED|FAIL|ERROR" | sed 's/^/  /'
sha256sum $I.cnf $I.lrat | sed 's/^/  /'
if [ -n "$CAKELPR" ]; then
  for f in mt4_9 k4_G6 k4_G4c k14_n10 balzer_AB_10 balzer_LA_9 balzer_LB_9 balzer_id_12; do
    echo "$f, cake_lpr: $("$CAKELPR" --CML_HEAP_SIZE=6000 --CML_STACK_SIZE=4000 ../cnf/independent/$f.cnf ../cnf/independent/$f.lrat 2>&1)"
  done
fi

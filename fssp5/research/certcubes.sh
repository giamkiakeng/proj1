#!/bin/bash
# certcubes.sh CNF ICNF LOG [first] [last] [step]
# For each cube c_i (index first..last-1, stride step) of ICNF: F_i = CNF + unit clauses of c_i,
# CaDiCaL 3.0.1 with a text LRAT proof (--binary=false), then lrat-check; one line per cube in LOG:
#   idx  cadical-result  lrat-check-result  seconds
# Cubes already VERIFIED in LOG are skipped.  The proof and F_i are deleted after checking.
CNF=$1; ICNF=$2; LOG=$3; FIRST=${4:-0}; LAST=${5:-1000000}; STEP=${6:-1}
CAD=${CADICAL:-/home/user/tools/cadical/build/cadical}; CHK=${LRATCHECK:-/home/user/tools/drat-trim/lrat-check}
TMP=$(mktemp -d -p "$(dirname "$LOG")" cert.XXXX)
read NV NC < <(awk '/^p cnf/{print $3, $4; exit}' $CNF)
mapfile -t CUBES < <(grep '^a ' $ICNF)
touch $LOG
for ((i=FIRST; i<LAST && i<${#CUBES[@]}; i+=STEP)); do
  if grep -q "^$i .* VERIFIED" $LOG; then continue; fi
  lits=$(echo "${CUBES[$i]}" | awk '{for(j=2;j<NF;j++) print $j}')
  k=$(echo "$lits" | wc -l)
  { echo "p cnf $NV $((NC+k))"; grep -v '^[pc]' $CNF; for l in $lits; do echo "$l 0"; done; } > $TMP/f.cnf
  t0=$(date +%s.%N)
  $CAD -q --lrat --binary=false $TMP/f.cnf $TMP/f.lrat > $TMP/out 2>&1
  res=$(grep '^s ' $TMP/out | awk '{print $2}')
  if [ "$res" = "UNSATISFIABLE" ]; then
    # lrat-check exits 0 and prints the line "c VERIFIED" exactly when the proof is complete and correct
    if $CHK $TMP/f.cnf $TMP/f.lrat > $TMP/chk 2>&1 && grep -qx 'c VERIFIED' $TMP/chk; then chk=VERIFIED; else chk=NOTVERIFIED; fi
  else chk=NOCHECK; fi
  t1=$(date +%s.%N)
  printf '%d %s %s %.1f\n' $i "${res:-NONE}" "${chk:-NONE}" $(echo "$t1 - $t0" | bc) >> $LOG
  rm -f $TMP/f.cnf $TMP/f.lrat $TMP/out $TMP/chk
done
rmdir $TMP

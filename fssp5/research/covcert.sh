#!/bin/bash
# covcert.sh ICNF NV LOG : the cubes of ICNF cover the assignment space of NV variables iff the CNF of their
# negations is unsatisfiable; CaDiCaL 3.0.1 refutes it with a text LRAT proof, checked by lrat-check.
# Appends one line "ICNF ncubes cadical-result lrat-check-result seconds" to LOG.
ICNF=$1; NV=$2; LOG=$3
CAD=${CADICAL:-/home/user/tools/cadical/build/cadical}; CHK=${LRATCHECK:-/home/user/tools/drat-trim/lrat-check}
TMP=$(mktemp -d -p "$(dirname "$LOG")" cov.XXXX)
nc=$(grep -c '^a ' $ICNF)
{ echo "p cnf $NV $nc"; grep '^a ' $ICNF | awk '{s=""; for(j=2;j<NF;j++) s=s (-$j) " "; print s "0"}'; } > $TMP/c.cnf
t0=$(date +%s.%N)
$CAD -q --lrat --binary=false $TMP/c.cnf $TMP/c.lrat > $TMP/out 2>&1
res=$(grep '^s ' $TMP/out | awk '{print $2}')
if [ "$res" = "UNSATISFIABLE" ]; then
  if $CHK $TMP/c.cnf $TMP/c.lrat > $TMP/chk 2>&1 && grep -qx 'c VERIFIED' $TMP/chk; then chk=VERIFIED; else chk=NOTVERIFIED; fi
else chk=NOCHECK; fi
t1=$(date +%s.%N)
printf '%s %d %s %s %.1f\n' $ICNF $nc "${res:-NONE}" "$chk" $(echo "$t1 - $t0" | bc) >> $LOG
rm -rf $TMP

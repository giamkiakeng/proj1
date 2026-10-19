#!/bin/bash
# certify_lrat.sh CNF -- re-solve an unsatisfiable formula with CaDiCaL (3.x), which writes an LRAT proof
#   directly (no DRAT-to-LRAT conversion), and check it with lrat-check; prints times, size and SHA-256
set -e
CNF=$1; B=${CNF%.cnf}
CADICAL=${CADICAL:-$(command -v cadical || echo /home/user/tools/cadical/build/cadical)}
LRATCHECK=${LRATCHECK:-/home/user/tools/drat-trim/lrat-check}
t0=$(date +%s)
set +e; $CADICAL -q --lrat=true --binary=false "$CNF" "$B.lrat" > /dev/null; rc=$?; set -e
[ $rc -eq 20 ] || { echo "cadical exit $rc (expected 20 = UNSAT)"; exit 1; }
t1=$(date +%s)
$LRATCHECK "$CNF" "$B.lrat" | grep -E "VERIFIED|FAIL|ERROR"
t2=$(date +%s)
echo "times: cadical $((t1-t0)) s, lrat-check $((t2-t1)) s; size: $(stat -c %s $B.lrat) B LRAT"
sha256sum "$CNF" "$B.lrat"

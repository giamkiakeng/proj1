#!/bin/bash
# certify.sh NAME.cnf : CaDiCaL with an LRAT proof, checked by lrat-check; prints digests.
# A certificate is reported only if CaDiCaL answers UNSATISFIABLE and the last lemma of the proof is the empty clause
# (lrat-check also prints VERIFIED for a proof without the empty clause).
CAD=${CADICAL:-cadical}; LC=${LRATCHECK:-lrat-check}
f=$1; b=${f%.cnf}
t0=$(date +%s); $CAD -q --lrat --no-binary $f $b.lrat > $b.out 2>&1; t1=$(date +%s)
ans=$(grep -E '^s ' $b.out)
echo "cadical: $ans ($((t1-t0)) s)"
if [ "$ans" != "s UNSATISFIABLE" ]; then echo "NO CERTIFICATE: the formula was not refuted"; exit 1; fi
last=$(grep -v ' d ' $b.lrat | tail -1 | awk '{print $2}')
if [ "$last" != "0" ]; then echo "NO CERTIFICATE: the proof does not end with the empty clause"; exit 1; fi
$LC $f $b.lrat 2>&1 | grep -E 'VERIFIED|FAILED' | sed 's/^/lrat-check: /'; t2=$(date +%s); echo "lrat-check: $((t2-t1)) s"
echo "cnf  sha256 $(sha256sum $f | cut -c1-64)  $(grep -m1 '^p cnf' $f)"
echo "lrat sha256 $(sha256sum $b.lrat | cut -c1-64)  $(stat -c %s $b.lrat) bytes"

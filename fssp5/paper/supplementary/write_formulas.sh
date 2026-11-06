#!/bin/bash
# write_formulas.sh -- the eight unsatisfiable formulas of the paper, written by the generators
# without solving, compared with the SHA-256 digests recorded when the proofs were made, and
# packed as formulas/*.cnf.xz.  Needs only Python 3; about one minute.
#
#   Theorem 6.1 (i)-(iii)   mt4_9, k4_G6, k4_G4c
#   Proposition 6.4         k14_n10  (the 230 refuted germs, with selectors)
#   Proposition 6.6         balzer_AB_10, balzer_LA_9, balzer_LB_9 (CaDiCaL), balzer_id_12 (Kissat)
#
# With --check, the published files formulas/*.cnf.xz are not rewritten; instead each is
# decompressed and compared with the same digests.
set -e
H=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$H/cnf" "$H/formulas"
cd "$H/src"
python3 gencnf.py 4 9 ../cnf/mt4_9.cnf
cd "$H/research"
GFIX_SHARE=1 python3 gfix.py FREE 4 full:2-7 early:8-10:6 --cnf ../cnf/k4_G6.cnf | cut -c1-100
GFIX_SHARE=1 python3 gfix.py FREE 4 full:2-5 early:6-10:4 cone:6-10 --cnf ../cnf/k4_G4c.cnf | cut -c1-100
cd "$H/src"
python3 germcert.py ../results/germs/K14_refuted10.txt 10 ../cnf/k14_n10 --cnf-only
python3 balzer.py 10 1234 AB --cnf=../cnf/balzer_AB_10.cnf
python3 balzer.py 9 1234 LA --cnf=../cnf/balzer_LA_9.cnf
python3 balzer.py 9 1234 LB --cnf=../cnf/balzer_LB_9.cnf
python3 balzer_k.py 5 12 1234 id --cnf=../cnf/balzer_id_12.cnf
cd "$H"
sha256sum -c formulas/SHA256SUMS
F="mt4_9 k4_G6 k4_G4c k14_n10 balzer_AB_10 balzer_LA_9 balzer_LB_9 balzer_id_12"
if [ "$1" = "--check" ]; then
  for f in $F; do
    want=$(grep " cnf/$f.cnf\$" formulas/SHA256SUMS | cut -d' ' -f1)
    got=$(xz -dc "formulas/$f.cnf.xz" | sha256sum | cut -d' ' -f1)
    [ "$want" = "$got" ] && echo "formulas/$f.cnf.xz: OK" || { echo "formulas/$f.cnf.xz: FAILED"; exit 1; }
  done
else
  for f in $F; do
    xz -9 -T1 -c "cnf/$f.cnf" > "formulas/$f.cnf.xz"
  done
  ls -l formulas
fi

#!/bin/bash
# germpipe.sh K OUTDIR -- complete classification of the half-line germs of
# complexity <= K (anti-diagonal 78, pumping to 40):
#   1. enumeration by germdfs;
#   2. incremental completion test for the lengths 2..10 (germinc.py);
#   3. germext: the survivors' half-lines are extended to anti-diagonal 1300;
#      germs refuted there by the left-border lemma or the pumping lemma
#      (lengths up to 650) are discarded;
#   4. completion tests for the lengths 2..13, 2..16, 2..20 on the rest.
set -e
K=$1; OUT=$2
cd "$(dirname "$0")"
mkdir -p "$OUT"
[ -s "$OUT/germs_K$K.txt" ] || ./germdfs 5 78 "$K" 40 > "$OUT/germs_K$K.txt" 2> "$OUT/germs_K$K.err"
[ -s "$OUT/K${K}_n10.log" ] && grep -q SUMMARY "$OUT/K${K}_n10.log" || python3 germinc.py "$OUT/germs_K$K.txt" 10 78 > "$OUT/K${K}_n10.log"
awk '$2!="UNSATISFIABLE" && $1!="SUMMARY"' "$OUT/K${K}_n10.log" | cut -d' ' -f4- > "$OUT/K${K}_s10.txt"
./germext 5 1300 3 8 < "$OUT/K${K}_s10.txt" > "$OUT/K${K}_ext.txt"
awk '$0 !~ /REFUTED/ && $0 !~ /PUMPFAIL/ && $0 !~ /FIRE/ && $0 !~ /FRONTL/ {print $1}' "$OUT/K${K}_ext.txt" > "$OUT/K${K}_ext.idx"
awk 'NR==FNR {keep[$1]=1; next} (FNR in keep)' "$OUT/K${K}_ext.idx" "$OUT/K${K}_s10.txt" > "$OUT/K${K}_sx.txt"
prev="$OUT/K${K}_sx.txt"
for N in 13 16 20; do
  [ -s "$prev" ] || break
  python3 germinc.py "$prev" $N 78 > "$OUT/K${K}_n$N.log"
  awk '$2!="UNSATISFIABLE" && $1!="SUMMARY"' "$OUT/K${K}_n$N.log" | cut -d' ' -f4- > "$OUT/K${K}_s$N.txt"
  prev="$OUT/K${K}_s$N.txt"
done
echo DONE > "$OUT/K${K}_done"

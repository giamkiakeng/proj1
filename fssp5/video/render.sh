#!/bin/bash
# render.sh [QUALITY] [SCENE ...] -- render the scenes (default: all, 1080p30), four in parallel.
#   QUALITY: hd (1920x1080, 30 fps; default) or low (854x480, 15 fps, for checking layouts)
# Each scene gets its own media directory: parallel Manim processes must not share media/Tex.
cd "$(dirname "$0")"
MANIM=${MANIM:-manim}
Q=${1:-hd}; shift || true
case $Q in
  hd) OPTS="-r 1920,1080 --frame_rate 30";;
  low) OPTS="-ql";;
  *) echo "quality must be hd or low"; exit 2;;
esac
ALL="scenes1.py:S01_ColdOpen scenes1.py:S02_Puzzle scenes1.py:S03_SpeedLimit scenes1.py:S04_History
scenes1.py:S05_HowSolutionsWork scenes2.py:S06_Haystack scenes2.py:S07_HalfLine scenes2.py:S08_Pumping
scenes2.py:S09_LeftBorder scenes2.py:S10_FourStates scenes3.py:S11_Frontier scenes3.py:S12_Germs
scenes3.py:S13_Balzer scenes3.py:S14_Outlook"
if [ $# -gt 0 ]; then SEL=""; for s in "$@"; do SEL="$SEL $(echo $ALL | tr ' ' '\n' | grep ":$s\$")"; done; else SEL=$ALL; fi
mkdir -p build/logs
run(){ f=${1%%:*}; s=${1##*:}; $MANIM render $OPTS --disable_caching --media_dir build/media_$s $f $s \
       > build/logs/$s.$Q.log 2>&1; echo "exit $?" >> build/logs/$s.$Q.log; }
N=0
for a in $SEL; do run "$a" & N=$((N+1)); if [ $N -ge 4 ]; then wait -n; N=$((N-1)); fi; done
wait
for a in $SEL; do s=${a##*:}; echo "$s: $(tail -n 1 build/logs/$s.$Q.log) $(grep -m1 -E '^[A-Za-z]*Error' build/logs/$s.$Q.log)"; done

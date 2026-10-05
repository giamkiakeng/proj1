# The Five-State Question (video)

A narrated, 3Blue1Brown-style explainer (about 25 minutes) of the firing squad synchronization
problem, its history, and the results of the paper *Towards five-state minimal-time firing squads:
two barriers on the half-line and certified bounds*. It is built with
[Manim Community](https://www.manim.community/) and a local neural voice
([Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M)).

Every space-time diagram in the video is computed from a rule table in `../results`
(`mazoyer6.txt`, `delta14.txt`, `uniformA_2-12.txt` = δ12, ...) by `fsspsim.py`. Every number
and statement in the narration (`script.md`) is taken from the paper, and the narration keeps the
paper's distinction between proofs, certified computations, simulations and heuristics. The three
facts recomputed for the video (δ14 fires cells 13–15 at time 22 on the line of length 15; the
depth-rows of Mazoyer's half-line are 3-periodic from time 2j+1 or 2j+2; c78 = 57, 22, 16 for
Mazoyer's rule, δ12 and δ14) agree with the paper.

## Files

| file | purpose |
|---|---|
| `script.md` | narration, 14 scenes / 75 blocks, with visual notes and pronunciation hints |
| `narration.py` | synthesizes every block with Kokoro (CPU) into `build/audio/` + `manifest.json` (durations, subtitle cues) |
| `fsspsim.py` | simulation of lines and half-lines from the rule tables |
| `common.py` | palette, `NarratedScene` (animations timed by the narration), `Diagram` (pixel-exact space-time diagrams) |
| `scenes1.py`, `scenes2.py`, `scenes3.py` | the 14 scenes |
| `render.sh` | renders the scenes (1080p30 or a low-quality preview), four in parallel |
| `assemble.py` | joins the scenes, adds soft subtitles and chapter markers, normalizes loudness |

## Building

Requirements: Python 3.11, LaTeX with `dvisvgm`, `ffmpeg`, and in a virtual environment
`pip install manim kokoro soundfile` plus a CPU build of PyTorch
(`pip install torch --index-url https://download.pytorch.org/whl/cpu`). The first Kokoro run downloads
the model from HuggingFace.

```
python3 narration.py                    # ~10 min on 4 CPU cores; --voice=am_michael etc. to change the voice
./render.sh hd                          # all scenes at 1920x1080, 30 fps (./render.sh low for a quick preview)
python3 assemble.py --crf=24            # -> build/five_state_question.mp4 and .srt
```

Re-rendering one scene: `./render.sh hd S08_Pumping`, then `python3 assemble.py` again.
The scenes read the narration durations from `build/audio/manifest.json`, so re-synthesizing the
narration (for instance with another voice) re-times all animations automatically.

The colours of the working states G, A, B are the first three slots of a palette validated for
colour-vision deficiencies on the dark background (all pairs: CVD ΔE ≥ 9.4, normal-vision ΔE ≥ 20.9,
contrast ≥ 3:1); C (used only by six-state rules) is a neutral grey, L a recessive slate and F white.

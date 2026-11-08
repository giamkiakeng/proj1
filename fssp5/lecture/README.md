# Video lecture: *Two barriers for minimal-time firing squads*

A narrated video lecture (93 minutes, 15 chapters, English captions) that explains every result of the
paper, from the puzzle itself to the certified computations. Chapters 1–3 need no mathematics; chapters
4–8 explain the proofs of Sections 2–5; chapters 9–13 explain the computer-assisted results of
Section 6 and how they are checked; chapter 14 is Section 7. These are its sources; the video is built
from them.

| file | content |
|---|---|
| `script1.txt`, `script2.txt`, `script3.txt` | the narration, one block per beat (`@ beat-id`), chapters marked `# CHAPTER`; `{display\|spoken}` gives the caption text and the spoken text of a formula |
| `slides1.tex`, `slides2.tex`, `slides3.tex`, `lecture.tex`, `lecstyle.tex` | the slides (Beamer, 16:9), one page per beat; `\beat{id}` ties a page to its narration |
| `lecture_handout.tex` | the same slides with animation stills, for the PDF handout |
| `figures` → `../paper/figures` | the figures and tables of the paper, used unchanged |
| `rules` → `../paper/supplementary/results` | the rule tables, simulated for the animations |
| `paperrefs.tex`, `tab_results_src.tex` | the paper's numbering (from `paper.aux`) and its Table 1, written by `make_paperrefs.py` |
| `anim.py` | the animations: Mazoyer's solution on the line of length 24, a signal there and back, and δ14 on the lines of lengths 14 and 15 |
| `lecture_lib.py` | parsing of the script, the pronunciation tables, speech synthesis with a cache |
| `voice_take.py` | the narration as a beat-numbered `script.md` for an external narrator, with its direction and the sentence list that `build.py --take` uses to time the captions |
| `synth_all.py` | synthesizes every sentence (fills the cache) |
| `asr_qa.py` | transcribes every synthesized sentence with a speech recognizer and compares it with the script |
| `build.py` | builds the video: slides → pages, narration → audio (synthesized, or a finished take with `--take`), captions (SRT), chapters, H.264/AAC MP4 with soft English subtitles |
| `burn_captions.py` | a second MP4 with the captions burned in below the slide, for players without subtitle support |
| `extras.py` | animation stills, the slide handout (PDF), a chapter list with timestamps and a description for a video platform |
| `check_video.py` | checks a built video: its streams and chapters, and, for every beat, that the frame in its middle shows its slide |

## Building

Requirements: TeX Live (Beamer, TikZ, pgfplots, adjustbox, tcolorbox), poppler-utils, ffmpeg with
libx264 and libass, the font DejaVu Sans, Python 3 with `piper-tts`, `pillow` and `numpy`, and the Piper
voice `en_US-ryan-high` (`.onnx` and `.onnx.json` from `https://huggingface.co/rhasspy/piper-voices`), in
`voices/` or at the path given by the environment variable `PIPER_VOICE`. For the speech check also
`faster-whisper` and `num2words`.

    python3 make_paperrefs.py     # after compiling ../paper/paper.tex
    python3 synth_all.py          # narration, about 15 minutes on four cores
    python3 asr_qa.py             # optional: speech-recognition check of every sentence
    python3 build.py              # out/lecture.mp4, .srt, .chapters.txt, .transcript.md
    python3 burn_captions.py      # out/lecture_captioned.mp4
    python3 extras.py             # out/lecture_slides.pdf, out/lecture_chapters.txt, out/lecture_description.txt
    python3 check_video.py        # optional: checks of out/lecture.mp4

The build checks that the slides and the script have the same beats in the same order.

## The narration

The published video is narrated by a computer-generated clone of the author's voice, made from recordings
of the author with Qwen3-TTS; the voice itself is not part of this repository. It reads the script that
`voice_take.py` writes:

    python3 voice_take.py take --narrator DIR     # take/script.md, take/voice/direction.json, take/sentences.json
    # the narrator reads take/script.md into take/voice/recording.wav and take/voice/recording.cues.json
    python3 build.py --take take/voice/recording.wav

`voice_take.py` puts one beat per slide, joins the paragraphs of a beat with a pause, asks for longer pauses
around the chapter titles, and spells out symbols and acronyms (`CLONE_SPOKEN` in `lecture_lib.py`); names
are respelled only where the clone's audio showed the plain spelling to be wrong. `build.py --take` shows each
slide from just before its first word to just before the next slide's, and times each caption by matching
its sentence to the chunks the narrator read. Without `--take`, `build.py` synthesizes the narration with
Piper (voice `en_US-ryan-high`, `synth_all.py`), and the welcome sentence should then be changed to say so.

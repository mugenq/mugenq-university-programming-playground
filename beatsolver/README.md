# Beat Timer v0.5

Clean split project for audio-only beat/timing prediction and external `.osu` evaluation.

- `beattimer_core.py`: MP3-only predictor.
- `beattimer_evaluation.py`: `.osu` parser and evaluator.
- `beattimer_dev_v0.5.ipynb`: predictor development.
- `beattimer_evaluator_v0.5.ipynb`: stable evaluation/report runner.

## v0.5 fixes

- one-to-one onset/grid matching;
- fallback sections preserve the original global phase;
- cross-window phase comparison uses actual grids at a common time;
- phase diagnostics are computed before segmentation;
- continuation scoring keeps the existing BPM and phase fixed;
- onset-derived phase candidates replace the 2,000-step brute-force scan;
- initial timing anchor is evaluated separately from later section boundaries;
- corrected summaries, paths, benchmark output, and duplicate keys.

## Setup

Place audio/maps under a local `songs/<name>/` directory, then edit `song_selection` in the notebooks. User song files are intentionally not bundled.

```bash
python -m pip install -r requirements.txt
```

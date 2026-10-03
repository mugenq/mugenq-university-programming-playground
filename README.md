# Programming & Data Science Portfolio

A collection of programming, mathematical computing, data analysis, machine-learning, and rhythm-analysis projects created while studying mathematics at the University of Tsukuba.

The repository includes both more substantial projects and a **learning archive**. The projects below are the best starting points.

## Highlights

### BeatSolver / Beat Timer
`beatsolver/`

An experimental audio-analysis project for estimating tempo, timing sections, phase, and beat-grid candidates from music, with external evaluation against osu! beatmaps. The current code separates prediction from evaluation so map data is not used by the predictor.

Key themes: signal processing, onset detection, local tempo estimation, grid/phase matching, benchmark design, and iterative algorithm evaluation.

### Statistical & mathematical computing
`statistics-and-mathematics/` and selected notebooks in `python-projects/`

Experiments and coursework involving probability/statistics, multivariate normal distributions, numerical mathematics, Gram-Schmidt orthogonalization, symbolic mathematics, and related topics.

### Machine-learning experiments
`machine-learning/`

TensorFlow/PyTorch learning experiments covering neural networks, convolutions, and language-model fundamentals. Some notebooks are exploratory/tutorial work rather than production projects.

### Minecraft book generator
`python-projects/minecraftbook.ipynb`

A small automation project that splits long text into Minecraft/Stendhal-compatible books while respecting page and book-size limits and preserving word boundaries.

### Python seminar material
`python-seminar/`

Python teaching/learning notebooks covering fundamentals, plotting, symbolic computation, and a small neural-network layer implementation.

## Other material

- `sql/` — SQL practice and a small SQLite example.
- `lean/` — introductory Lean experiments.
- `learning-experiments/` — older chatbot/osu!/coding experiments retained as an archive.
- `misc/` — non-Python source experiments, including a small C# game mod.

## Repository hygiene

Generated executables, build directories, notebook caches, private access tokens, large media files, and third-party song/beatmap files are intentionally excluded. BeatSolver's local `songs/` directory contains only instructions, not redistributed audio.

## About this repository

This is a broad development archive, so code quality and documentation vary by age. The highlighted projects above are the most representative of my current interests in **statistics, data science, machine learning, and practical problem solving**.

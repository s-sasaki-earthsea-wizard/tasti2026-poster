# TASTI 2026 Poster — GPU-Accelerated InSAR Time-Series Analysis (Paper No. T0043)

Poster for [TASTI 2026](https://tasti2026.conf.tw/) (Taiwan International
Assembly of Space Science, Technology, and Industry; November 2026, International
Convention Center, Tainan, Taiwan), presenting the PyTorch-based GPU solver
contributed to [MintPy](https://github.com/insarlab/MintPy) via
[insarlab/MintPy#1490](https://github.com/insarlab/MintPy/pull/1490).

| | |
|---|---|
| Paper No. | **T0043** |
| Session | **Poster** — 10 November 2026, 11:30–14:00, Room Tayouan D (3F) |
| Topic | 02 Space Applications and Services / 0201 Earth Observation and Remote Sensing |
| Title | Accelerating Open-Source InSAR Time-Series Analysis on Consumer GPUs: A PyTorch-Based Network Inversion Solver for MintPy |
| Poster size | **A0, 84.1 cm × 118.9 cm** (official requirement) |
| Poster PDF | [doi:10.5281/zenodo.23669874](https://doi.org/10.5281/zenodo.23669874) (Zenodo, latest version, CC BY 4.0) |

This is the third repository of the series:

| Repository | Role |
|---|---|
| [s-sasaki-earthsea-wizard/MintPy](https://github.com/s-sasaki-earthsea-wizard/MintPy) | Development fork; the implementation behind PR #1490 |
| [mintpy-benchmark](https://github.com/s-sasaki-earthsea-wizard/mintpy-benchmark) | Benchmark harness and the reports every number on the poster comes from |
| [tasti2026-abstract](https://github.com/s-sasaki-earthsea-wizard/tasti2026-abstract) | The accepted extended abstract (frozen at the 2026-08-06 submission) |
| [vrc-insar-batched-cholesky-LT](https://github.com/s-sasaki-earthsea-wizard/vrc-insar-batched-cholesky-LT) | Japanese lightning-talk deck on the numerical-linear-algebra side; source of most figures |
| **this repository** | The poster, its figures, and the working documentation for the poster session |

The full link index (reports pinned to commits, Zenodo datasets, references) is in
[docs/sources.md](docs/sources.md).

## Layout

| Path | Purpose |
|---|---|
| `poster.tex` | Poster source (beamerposter, A0 portrait, three columns) |
| `beamerthemetasti2026.sty` | Poster theme: navy masthead with the logo, warm off-white ground, open numbered blocks, references band; palette shared with the figures |
| `figures/src/*.svg` | Hand-drawn figure sources (English). Converted to PDF by `make` |
| `figures/src/ja/` | Untranslated Japanese originals kept as candidates (not built) |
| `scripts/plot_speedup.py` | Generates the five-scene speedup chart from the S3 benchmark series |
| `scripts/estimate_scale.py` | NISAR-scale compute estimates for the Q&A (`docs/compute_scale.md`) |
| `docs/` | Working documentation (Japanese): requirements, content plan, benchmark canon, Q&A prep, link index |
| `print/` | Dated copies of the PDF that actually went to the printer |
| `Makefile` | `make` / `make preview` / `make check` / `make print` (`make help` lists everything) |
| `HANDOVER.md` | Session handover notes (Japanese) |

## Build

Requires TeX Live (with `beamerposter`, `qrcode`, TikZ and the `sourcesanspro` /
`sourceserifpro` / `sourcecodepro` fonts), librsvg, Python 3 with
matplotlib, and poppler for the preview/check targets.

```bash
# macOS
brew install librsvg poppler
# Debian/Ubuntu
sudo apt-get install texlive-latex-extra texlive-fonts-extra latexmk librsvg2-bin poppler-utils

make            # poster.pdf
make preview    # preview/poster.png (low-dpi raster for a quick look)
make check      # page size is A0 and every font is embedded
make print      # copy to print/poster_<date>.pdf
```

## Numbers

Every figure on the poster is traced to a benchmark series in
[docs/results.md](docs/results.md). Three series exist and must never be mixed;
no size dependence may be claimed from the five-scene series. Read that file
before touching any number.

## Key dates

| Date | Item |
|---|---|
| 2026-10-13 | Registration deadline |
| 2026-11-07 15:00–17:00 or 2026-11-08 08:30–12:00 | Poster setup, Tayouan D (3F) |
| **2026-11-10 11:30–14:00** | **Poster session** |
| 2026-11-11 12:00–14:00 | Poster removal (unclaimed posters are disposed of) |

## License

MIT — see [LICENSE](LICENSE). Benchmark numbers and figures may be reused with
attribution to the repositories above.

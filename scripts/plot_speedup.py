"""Generate Fig. 2 of the TASTI 2026 poster: step-level speedup over five scenes.

The numbers are the S3 series of the benchmark: step-level wall time of
``invert_network`` extracted from complete 18-step ``smallbaselineApp`` runs,
CPU reference path versus the opt-in torch solver, on an NVIDIA GeForce
RTX 5080 (16 GB).

Source of record:
    mintpy-benchmark ``reports/report_end_to_end_bench.md`` @ commit ``0fbf71b``
    (mirrored in ``docs/results.md`` of this repository, section "S3").

Do not mix this series with S1 (QR versus Cholesky on the same GPU, 16.5x) or
S2 (the conditioned large-scene measurement, 36.4x step / 44.4x kernel).
Do not read a size dependence into the bars either: the ranking does not
follow pixel count (Spearman rank correlation -0.20, see docs/results.md).

The figure is sized for a poster column: it is included at roughly 1.6x its
nominal width, and the default font scale of 1.3 then puts the labels at
about 19-25 pt on the printed A0 sheet.

Usage:
    python3 scripts/plot_speedup.py [-o figures/fig2_speedup.pdf]
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402  (must follow the backend selection)

# Palette shared with the SVG figures so the whole poster reads as one set.
BAR_COLOR = "#1a6fb5"
TEXT_COLOR = "#333333"
MUTED_COLOR = "#777777"
GRID_COLOR = "#dddddd"

# S3 series. Fields: scene, processor, band, interferograms K, dates D,
# CPU step wall [s], torch step wall [s].
SCENES = [
    ("Fernandina", "ISCE-2", "C", 288, 98, 645.12, 6.88),
    ("San Francisco Bay", "GMTSAR", "C", 1297, 333, 1080.38, 17.42),
    ("Galápagos", "ISCE-2", "C", 490, 98, 2976.72, 79.40),
    ("Kuju", "ROI_PAC", "L", 167, 24, 31.01, 4.53),
    ("San Francisco", "ARIA", "C", 505, 114, 58.85, 11.07),
]


def _format_seconds(value: float) -> str:
    """Render a wall-clock duration compactly for an axis annotation.

    Args:
        value: Duration in seconds.

    Returns:
        The duration in minutes when it exceeds two minutes, seconds otherwise.
    """
    if value >= 120.0:
        return f"{value / 60.0:.0f} min"
    return f"{value:.1f} s"


def build_figure(font_scale: float = 1.3) -> plt.Figure:
    """Draw the horizontal speedup chart.

    Args:
        font_scale: Multiplier applied to every font size, for re-tuning the
            figure when the poster scale changes.

    Returns:
        The populated matplotlib figure, sized for one poster column.
    """
    rows = sorted(SCENES, key=lambda row: row[5] / row[6], reverse=True)

    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"],
            "pdf.fonttype": 42,  # embed TrueType so the PDF stays text-searchable
            # Helvetica Neue has no U+2192; render the arrow through mathtext,
            # with "regular" so it inherits the upright body weight.
            "mathtext.default": "regular",
        }
    )
    fs = lambda size: size * font_scale  # noqa: E731  (tiny local helper)

    fig, ax = plt.subplots(figsize=(6.0, 3.5))
    positions = range(len(rows))
    speedups = [row[5] / row[6] for row in rows]

    ax.barh(list(positions), speedups, height=0.62, color=BAR_COLOR, zorder=3)

    labels = []
    for scene, processor, band, n_ifg, n_date, _cpu, _gpu in rows:
        labels.append(f"{scene}\n{processor}, {band}-band, K={n_ifg}, D={n_date}")

    ax.set_yticks(list(positions))
    ax.set_yticklabels(labels, fontsize=fs(10.0), color=TEXT_COLOR)
    ax.invert_yaxis()

    ax.set_xscale("log")
    ax.set_xlim(1.0, 400.0)
    ax.set_xticks([1, 3, 10, 30, 100])
    ax.set_xticklabels(
        ["1×", "3×", "10×", "30×", "100×"],
        fontsize=fs(10.5),
        color=TEXT_COLOR,
    )
    ax.set_xlabel(
        "Step-level speedup over the CPU path (log scale)",
        fontsize=fs(11.0),
        color=TEXT_COLOR,
    )

    # Annotate each bar with the speedup and the wall times behind it.
    for index, (row, speedup) in enumerate(zip(rows, speedups)):
        _scene, _proc, _band, _k, _d, cpu, gpu = row
        ax.text(
            speedup * 1.12,
            index - 0.02,
            f"{speedup:.1f}×",
            va="center",
            ha="left",
            fontsize=fs(12.0),
            fontweight="bold",
            color=BAR_COLOR,
        )
        ax.text(
            speedup * 1.12,
            index + 0.30,
            f"{_format_seconds(cpu)} $\\rightarrow$ {_format_seconds(gpu)}",
            va="center",
            ha="left",
            fontsize=fs(9.0),
            color=MUTED_COLOR,
        )

    ax.xaxis.grid(True, which="major", color=GRID_COLOR, linewidth=0.6, zorder=0)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(GRID_COLOR)
    ax.tick_params(axis="both", length=0)

    fig.tight_layout(pad=0.4)
    return fig


def main() -> None:
    """Parse arguments and write the figure to disk."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "figures" / "fig2_speedup.pdf",
        help="output path; the suffix selects the format (.pdf keeps it vector)",
    )
    parser.add_argument(
        "--font-scale",
        type=float,
        default=1.3,
        help="multiply every font size by this factor (default 1.3, tuned for A0)",
    )
    args = parser.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    figure = build_figure(font_scale=args.font_scale)
    figure.savefig(args.output, bbox_inches="tight", pad_inches=0.02)
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()

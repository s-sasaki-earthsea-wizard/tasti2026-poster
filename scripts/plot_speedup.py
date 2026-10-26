"""Generate Fig. 2 of the TASTI 2026 poster: CPU versus GPU wall time, five scenes.

The numbers are the S3 series of the benchmark: step-level wall time of
``invert_network`` extracted from complete 18-step ``smallbaselineApp`` runs,
CPU reference path versus the opt-in torch solver, on an NVIDIA GeForce
RTX 5080 (16 GB).

The chart is a dumbbell on a log time axis: one grey dot for the CPU, one
blue dot for the GPU, and an arrow from CPU to GPU. On a log axis the length
of the arrow is the speedup itself, which a bar drawn from an arbitrary
origin would not show.

Source of record:
    mintpy-benchmark ``reports/report_end_to_end_bench.md`` @ commit ``0fbf71b``
    (mirrored in ``docs/results.md`` of this repository, section "S3").

Do not mix this series with S1 (QR versus Cholesky on the same GPU, 16.5x) or
S2 (the large-scene measurement, 44.4x internal / 36.4x step wall). The rows
are labelled with the pixels actually inverted, so that Galapagos here (1.29 M
pixels after masking) is not confused with the 3.4 M-pixel S2 run. Do not read
a size dependence into the chart either: the ranking does not follow pixel
count (Spearman rank correlation -0.10, see docs/results.md).

The figure is sized for a poster column: it is included at roughly 1.6x its
nominal width, and the default font scale of 1.5 then puts the labels at
about 22-28 pt on the printed A0 sheet.

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
# The GPU carries the accent; the CPU is context, so it stays grey.
GPU_COLOR = "#1a6fb5"
CPU_COLOR = "#8994a0"
ARROW_COLOR = "#b4bcc4"
TEXT_COLOR = "#333333"
MUTED_COLOR = "#666666"
GRID_COLOR = "#e4e4e4"

# S3 series. Fields: scene, processor, band, pixels actually inverted (after
# masking), note, CPU step wall [s], torch step wall [s].
SCENES = [
    ("Fernandina", "ISCE-2", "C", "270 k", "", 645.12, 6.88),
    ("San Francisco Bay", "GMTSAR", "C", "234 k", "", 1080.38, 17.42),
    ("Galápagos", "ISCE-2", "C", "1.29 M", "", 2976.72, 79.40),
    ("Kuju", "ROI_PAC", "L", "226 k", "", 31.01, 4.53),
    # Run with weightFunc = no: the CPU path solves all pixels in one call.
    ("San Francisco", "ARIA", "C", "758 k", "unweighted", 58.85, 11.07),
]

TIME_TICKS = [1, 10, 60, 600, 3600]
TIME_TICK_LABELS = ["1 s", "10 s", "1 min", "10 min", "1 h"]


def _format_seconds(value: float) -> str:
    """Render a wall-clock duration compactly for a point annotation.

    Args:
        value: Duration in seconds.

    Returns:
        Whole minutes above two minutes, whole seconds above twenty seconds,
        and seconds with one decimal otherwise.
    """
    if value >= 120.0:
        return f"{value / 60.0:.0f} min"
    if value >= 20.0:
        return f"{value:.0f} s"
    return f"{value:.1f} s"


def build_figure(font_scale: float = 1.5) -> plt.Figure:
    """Draw the CPU-to-GPU dumbbell chart.

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
        }
    )
    fs = lambda size: size * font_scale  # noqa: E731  (tiny local helper)

    fig, ax = plt.subplots(figsize=(6.0, 4.8))

    # Each scene is labelled on its own line above its row rather than as a
    # y tick label, so the plot keeps the full column width at poster sizes.
    ax.set_yticks([])
    ax.set_ylim(len(rows) - 0.55, -0.75)  # inverted: first row at the top
    label_x = ax.get_yaxis_transform()  # x in axes fraction, y in data
    renderer = fig.canvas.get_renderer()

    for index, (scene, proc, band, pixels, note, cpu, gpu) in enumerate(rows):
        extra = f", {note}" if note else ""
        name = ax.text(0.0, index - 0.38, scene, transform=label_x, ha="left",
                       va="baseline", fontsize=fs(10.0), color=TEXT_COLOR)
        # Place the muted details right after the rendered scene name.
        name_width_pt = name.get_window_extent(renderer).width * 72.0 / fig.dpi
        ax.annotate(f"{proc}, {band}-band, {pixels} px{extra}",
                    xy=(0.0, index - 0.38), xycoords=label_x,
                    xytext=(name_width_pt + fs(5.0), 0), textcoords="offset points",
                    ha="left", va="baseline", fontsize=fs(8.5), color=MUTED_COLOR)

        # Arrow from the CPU dot to the GPU dot; shrink keeps the head clear
        # of the dot so it reads as "this much faster".
        ax.annotate(
            "",
            xy=(gpu, index),
            xytext=(cpu, index),
            arrowprops={
                "arrowstyle": "-|>,head_length=0.6,head_width=0.3",
                "color": ARROW_COLOR,
                "linewidth": 2.4,
                "shrinkA": 7,
                "shrinkB": 8,
            },
            zorder=2,
        )
        ax.scatter([cpu], [index], s=fs(70), color=CPU_COLOR, edgecolor="white",
                   linewidth=1.5, zorder=3)
        ax.scatter([gpu], [index], s=fs(70), color=GPU_COLOR, edgecolor="white",
                   linewidth=1.5, zorder=4)
        # Times sit on the dot line (GPU to the left of its dot, CPU to the
        # right of its dot) so nothing collides with the next row's label;
        # the speedups line up in a column at the right edge.
        ax.annotate(_format_seconds(gpu), xy=(gpu, index), xytext=(-fs(7.0), 0),
                    textcoords="offset points", ha="right", va="center",
                    fontsize=fs(8.5), color=MUTED_COLOR)
        ax.annotate(_format_seconds(cpu), xy=(cpu, index), xytext=(fs(7.0), 0),
                    textcoords="offset points", ha="left", va="center",
                    fontsize=fs(8.5), color=MUTED_COLOR)
        ax.text(1.0, index, f"{cpu / gpu:.1f}×", transform=label_x, ha="right",
                va="center", fontsize=fs(11.5), color=TEXT_COLOR)

    ax.set_xscale("log")
    ax.set_xlim(1.0, 60000.0)
    ax.set_xticks(TIME_TICKS)
    ax.set_xticklabels(TIME_TICK_LABELS, fontsize=fs(10.0), color=TEXT_COLOR)
    ax.minorticks_off()
    ax.set_xlabel("Step wall time (log scale)", fontsize=fs(10.5), color=TEXT_COLOR)

    handles = [
        plt.Line2D([], [], marker="o", linestyle="", color=CPU_COLOR, markersize=8),
        plt.Line2D([], [], marker="o", linestyle="", color=GPU_COLOR, markersize=8),
    ]
    ax.legend(handles, ["CPU (reference)", "GPU (torch solver)"], loc="lower center",
              bbox_to_anchor=(0.5, 1.0), ncol=2, fontsize=fs(9.5), frameon=False)

    ax.xaxis.grid(True, which="major", color=GRID_COLOR, linewidth=0.8, zorder=0)
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
        default=1.5,
        help="multiply every font size by this factor (default 1.5, tuned for A0)",
    )
    args = parser.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    figure = build_figure(font_scale=args.font_scale)
    figure.savefig(args.output, bbox_inches="tight", pad_inches=0.02)
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()

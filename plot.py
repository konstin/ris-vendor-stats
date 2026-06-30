#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# dependencies = [
#   "matplotlib>=3.5.1",
#   "pandas>=1.4.0",
# ]
# ///

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas


RESULTS_PATTERN = "[0-9][0-9][0-9][0-9]/results-*.csv"
SCRIPT_DIR = Path(__file__).resolve().parent
# Bad crawler snapshot; keep it as NaN so plotted series have a gap.
EXCLUDED_RESULT_DATES = {
    date(2026, 1, 11),
}


def result_date(path: Path) -> date:
    prefix = "results-"
    return date.fromisoformat(path.stem[len(prefix) :])


def load_vendor_counts(results_dir: Path, verbose: bool = False) -> pandas.DataFrame:
    files = sorted(results_dir.glob(RESULTS_PATTERN))
    if not files:
        raise SystemExit(f"No result CSVs found below {results_dir}")

    dates = []
    counts = []
    for path in files:
        snapshot_date = result_date(path)
        if verbose:
            label = " excluded" if snapshot_date in EXCLUDED_RESULT_DATES else ""
            print(f"{path}{label}")
        if snapshot_date in EXCLUDED_RESULT_DATES:
            vendor_counts = pandas.Series(dtype="int64")
        else:
            csv = pandas.read_csv(path, usecols=["vendor"])
            vendor_counts = csv["vendor"].value_counts()
        dates.append(snapshot_date)
        counts.append(vendor_counts)

    return pandas.DataFrame(counts, index=dates).sort_index()


def plot_vendor_counts(vendor_counts: pandas.DataFrame) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(12, 8))

    for vendor in vendor_counts.columns:
        ax.plot(vendor_counts.index, vendor_counts[vendor], label=vendor)

    ax.legend()
    ax.grid()
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.set_ylabel("Number of Websites")
    fig.tight_layout()
    return fig


def output_path(output_stem: Path, suffix: str) -> Path:
    return output_stem.parent / f"{output_stem.name}{suffix}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=SCRIPT_DIR,
        help="directory containing the year buckets",
    )
    parser.add_argument(
        "--output-stem",
        type=Path,
        default=SCRIPT_DIR / "vendors-over-time",
        help="output path without extension",
    )
    parser.add_argument("--show", action="store_true", help="display the plot window")
    parser.add_argument("--verbose", action="store_true", help="print each CSV path")
    args = parser.parse_args()

    vendor_counts = load_vendor_counts(args.results_dir, verbose=args.verbose)
    fig = plot_vendor_counts(vendor_counts)

    args.output_stem.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path(args.output_stem, ".svg"))
    fig.savefig(output_path(args.output_stem, ".png"))

    if args.show:
        plt.show()

    plt.close(fig)


if __name__ == "__main__":
    main()

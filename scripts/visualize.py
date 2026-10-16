#!/usr/bin/env python3
"""Compare an empirical Gaussian sample against its theoretical distribution."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

# Allow `python scripts/visualize.py` without installing a package.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from gaussian_stats import (  # noqa: E402
    diagnose,
    format_diagnostics,
    gaussian_pdf,
    gaussian_ppf,
)


def plot_histogram_vs_pdf(
    samples: np.ndarray,
    mu: float,
    sigma: float,
    bins: int,
    output: Path,
) -> None:
    fig, ax = plt.subplots(figsize=(8, 5), constrained_layout=True)
    ax.hist(
        samples,
        bins=bins,
        density=True,
        alpha=0.65,
        color="#3d5a80",
        edgecolor="white",
        linewidth=0.4,
        label="Empirical density",
    )

    x = np.linspace(samples.min() - sigma, samples.max() + sigma, 500)
    ax.plot(
        x,
        gaussian_pdf(x, mu, sigma),
        color="#e63946",
        linewidth=2.2,
        label=rf"PDF $\mathcal{{N}}({mu:g}, {sigma:g}^2)$",
    )

    ax.set_xlabel("Value")
    ax.set_ylabel("Density")
    ax.set_title("Box–Muller sample vs. theoretical Gaussian PDF")
    ax.legend(frameon=False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=160)
    plt.close(fig)


def plot_qq(
    samples: np.ndarray,
    mu: float,
    sigma: float,
    output: Path,
) -> None:
    ordered = np.sort(samples)
    n = ordered.size
    # Plotting positions avoid 0/1 endpoints where the normal quantile diverges.
    probs = (np.arange(1, n + 1) - 0.5) / n
    theoretical = gaussian_ppf(probs, mu, sigma)

    fig, ax = plt.subplots(figsize=(6.5, 6.5), constrained_layout=True)
    ax.scatter(
        theoretical,
        ordered,
        s=12,
        alpha=0.55,
        color="#3d5a80",
        edgecolors="none",
        label="Sample quantiles",
    )

    lo = min(theoretical.min(), ordered.min())
    hi = max(theoretical.max(), ordered.max())
    ax.plot([lo, hi], [lo, hi], color="#e63946", linewidth=2.0, label="y = x")

    ax.set_xlabel("Theoretical quantiles")
    ax.set_ylabel("Sample quantiles")
    ax.set_title(rf"QQ plot vs $\mathcal{{N}}({mu:g}, {sigma:g}^2)$")
    ax.legend(frameon=False)
    ax.set_aspect("equal", adjustable="datalim")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=160)
    plt.close(fig)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Plot Gaussian diagnostics: histogram vs PDF and QQ plot."
    )
    parser.add_argument("--input", type=Path, default=Path("data/sample.dat"))
    parser.add_argument("--mu", type=float, required=True)
    parser.add_argument("--sigma", type=float, required=True)
    parser.add_argument("--bins", type=int, default=50)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("figures/histogram_vs_pdf.png"),
    )
    parser.add_argument(
        "--qq-output",
        type=Path,
        default=Path("figures/qq_plot.png"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.sigma <= 0:
        raise SystemExit("--sigma must be > 0")
    if args.bins < 2:
        raise SystemExit("--bins must be >= 2")

    samples = np.loadtxt(args.input)
    if samples.ndim != 1 or samples.size == 0:
        raise SystemExit(f"Expected a non-empty 1D sample file: {args.input}")

    plot_histogram_vs_pdf(
        samples=samples,
        mu=args.mu,
        sigma=args.sigma,
        bins=args.bins,
        output=args.output,
    )
    plot_qq(
        samples=samples,
        mu=args.mu,
        sigma=args.sigma,
        output=args.qq_output,
    )

    diag = diagnose(samples, args.mu, args.sigma)
    print(f"Saved figure to {args.output}")
    print(f"Saved QQ plot to {args.qq_output}")
    print(format_diagnostics(diag))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Compare an empirical Gaussian sample against its theoretical PDF."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def gaussian_pdf(x: np.ndarray, mu: float, sigma: float) -> np.ndarray:
    """Evaluate the normal density $\\mathcal{N}(\\mu, \\sigma^2)$."""
    return (1.0 / (sigma * np.sqrt(2.0 * np.pi))) * np.exp(
        -0.5 * ((x - mu) / sigma) ** 2
    )


def summarize(samples: np.ndarray, mu: float, sigma: float) -> dict[str, float]:
    return {
        "n": float(samples.size),
        "sample_mean": float(np.mean(samples)),
        "sample_std": float(np.std(samples, ddof=1)),
        "target_mean": mu,
        "target_std": sigma,
    }


def plot_histogram_vs_pdf(
    samples: np.ndarray,
    mu: float,
    sigma: float,
    bins: int,
    output: Path,
) -> dict[str, float]:
    stats = summarize(samples, mu, sigma)

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
    return stats


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Plot a Gaussian sample histogram against its PDF."
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

    stats = plot_histogram_vs_pdf(
        samples=samples,
        mu=args.mu,
        sigma=args.sigma,
        bins=args.bins,
        output=args.output,
    )

    print(
        f"Saved figure to {args.output}\n"
        f"n={int(stats['n'])}  "
        f"mean={stats['sample_mean']:.4f} (target {stats['target_mean']:.4f})  "
        f"std={stats['sample_std']:.4f} (target {stats['target_std']:.4f})"
    )


if __name__ == "__main__":
    main()

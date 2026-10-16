#!/usr/bin/env python3
"""Gaussian PDF/CDF helpers and sample–theory diagnostics."""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np
from scipy.special import erf, erfinv


def gaussian_pdf(x: np.ndarray, mu: float, sigma: float) -> np.ndarray:
    """Evaluate $f_X(x)$ for $X \\sim \\mathcal{N}(\\mu, \\sigma^2)$."""
    return (1.0 / (sigma * np.sqrt(2.0 * np.pi))) * np.exp(
        -0.5 * ((x - mu) / sigma) ** 2
    )


def gaussian_cdf(x: np.ndarray, mu: float, sigma: float) -> np.ndarray:
    """Evaluate $F_X(x) = \\Phi((x-\\mu)/\\sigma)$ via `erf`."""
    z = (x - mu) / (sigma * np.sqrt(2.0))
    return 0.5 * (1.0 + erf(z))


def gaussian_ppf(p: np.ndarray, mu: float, sigma: float) -> np.ndarray:
    """Quantile function $F_X^{-1}(p)$ via `erfinv`."""
    return mu + sigma * np.sqrt(2.0) * erfinv(2.0 * p - 1.0)


@dataclass(frozen=True)
class SampleDiagnostics:
    n: int
    sample_mean: float
    sample_std: float
    target_mean: float
    target_std: float
    mean_abs_error: float
    std_abs_error: float
    mean_rel_error: float
    std_rel_error: float
    ks_statistic: float
    ks_critical_95: float

    def as_dict(self) -> dict[str, float]:
        return {k: float(v) for k, v in asdict(self).items()}


def kolmogorov_smirnov_statistic(
    samples: np.ndarray, mu: float, sigma: float
) -> float:
    """
    One-sample KS distance against $\\mathcal{N}(\\mu, \\sigma^2)$:

    $$
    D_N = \\sup_x \\lvert F_N(x) - F_X(x) \\rvert
    $$
    """
    ordered = np.sort(samples)
    n = ordered.size
    theoretical = gaussian_cdf(ordered, mu, sigma)
    empiric_low = np.arange(0, n) / n
    empiric_high = np.arange(1, n + 1) / n
    return float(
        np.max(
            np.maximum(
                np.abs(theoretical - empiric_low),
                np.abs(theoretical - empiric_high),
            )
        )
    )


def diagnose(samples: np.ndarray, mu: float, sigma: float) -> SampleDiagnostics:
    n = int(samples.size)
    sample_mean = float(np.mean(samples))
    sample_std = float(np.std(samples, ddof=1))
    mean_abs = abs(sample_mean - mu)
    std_abs = abs(sample_std - sigma)
    mean_scale = max(abs(mu), 1.0)
    std_scale = max(abs(sigma), 1.0)
    # Asymptotic 95% critical value for the Kolmogorov distribution:
    # P(sqrt(N) D_N > 1.36) ≈ 0.05 under the null.
    ks_critical_95 = 1.36 / np.sqrt(n)

    return SampleDiagnostics(
        n=n,
        sample_mean=sample_mean,
        sample_std=sample_std,
        target_mean=mu,
        target_std=sigma,
        mean_abs_error=mean_abs,
        std_abs_error=std_abs,
        mean_rel_error=mean_abs / mean_scale,
        std_rel_error=std_abs / std_scale,
        ks_statistic=kolmogorov_smirnov_statistic(samples, mu, sigma),
        ks_critical_95=float(ks_critical_95),
    )


def format_diagnostics(diag: SampleDiagnostics) -> str:
    ks_flag = "OK" if diag.ks_statistic <= diag.ks_critical_95 else "CHECK"
    return (
        f"n={diag.n}\n"
        f"mean={diag.sample_mean:.6f}  target={diag.target_mean:.6f}  "
        f"|err|={diag.mean_abs_error:.6f}  rel={diag.mean_rel_error:.4%}\n"
        f"std ={diag.sample_std:.6f}  target={diag.target_std:.6f}  "
        f"|err|={diag.std_abs_error:.6f}  rel={diag.std_rel_error:.4%}\n"
        f"KS D={diag.ks_statistic:.6f}  "
        f"critical_95={diag.ks_critical_95:.6f}  [{ks_flag}]"
    )

#!/usr/bin/env python3
"""Unit tests for Gaussian diagnostic helpers (no C binary required)."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from gaussian_stats import (  # noqa: E402
    diagnose,
    gaussian_cdf,
    gaussian_pdf,
    gaussian_ppf,
    kolmogorov_smirnov_statistic,
)


class GaussianStatsTests(unittest.TestCase):
    def test_pdf_normalizes_on_a_wide_grid(self) -> None:
        mu, sigma = 1.5, 2.0
        x = np.linspace(mu - 8 * sigma, mu + 8 * sigma, 20001)
        density = gaussian_pdf(x, mu, sigma)
        mass = np.trapezoid(density, x) if hasattr(np, "trapezoid") else np.trapz(density, x)
        self.assertAlmostEqual(mass, 1.0, places=3)

    def test_cdf_ppf_roundtrip(self) -> None:
        mu, sigma = -0.5, 1.25
        probs = np.array([0.05, 0.25, 0.5, 0.75, 0.95])
        quantiles = gaussian_ppf(probs, mu, sigma)
        recovered = gaussian_cdf(quantiles, mu, sigma)
        np.testing.assert_allclose(recovered, probs, atol=1e-10)

    def test_exact_normal_sample_has_tiny_ks(self) -> None:
        rng = np.random.default_rng(0)
        mu, sigma = 0.0, 1.0
        samples = rng.normal(mu, sigma, size=8000)
        d = kolmogorov_smirnov_statistic(samples, mu, sigma)
        self.assertLess(d, 1.36 / np.sqrt(samples.size))

    def test_diagnose_flags_shifted_sample(self) -> None:
        rng = np.random.default_rng(1)
        samples = rng.normal(0.0, 1.0, size=4000) + 3.0
        diag = diagnose(samples, mu=0.0, sigma=1.0)
        self.assertGreater(diag.mean_abs_error, 2.5)
        self.assertGreater(diag.ks_statistic, diag.ks_critical_95)


if __name__ == "__main__":
    unittest.main()

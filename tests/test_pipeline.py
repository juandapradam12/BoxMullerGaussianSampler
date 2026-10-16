#!/usr/bin/env python3
"""End-to-end smoke test: build sampler → draw sample → check moments / KS."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from gaussian_stats import diagnose  # noqa: E402

N = 8000
MU = 2.5
SIGMA = 3.5
SEED = 42


class PipelineSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.sampler = ROOT / "bin" / "gaussian_sampler"
        if not cls.sampler.exists():
            raise unittest.SkipTest(
                f"Missing {cls.sampler}; run `make bin/gaussian_sampler` first"
            )

    def test_fixed_seed_moments_and_ks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "sample.dat"
            subprocess.run(
                [
                    str(self.sampler),
                    "--n",
                    str(N),
                    "--mu",
                    str(MU),
                    "--sigma",
                    str(SIGMA),
                    "--seed",
                    str(SEED),
                    "--output",
                    str(out),
                ],
                check=True,
                cwd=ROOT,
            )
            samples = np.loadtxt(out)
            self.assertEqual(samples.ndim, 1)
            self.assertEqual(samples.size, N)

            diag = diagnose(samples, MU, SIGMA)
            # Monte Carlo tolerance: a few standard errors on the mean/std.
            self.assertLess(diag.mean_abs_error, 0.15)
            self.assertLess(diag.std_abs_error, 0.15)
            self.assertLessEqual(diag.ks_statistic, diag.ks_critical_95)

    def test_reproducible_under_fixed_seed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            a = Path(tmp) / "a.dat"
            b = Path(tmp) / "b.dat"
            cmd = [
                str(self.sampler),
                "--n",
                "500",
                "--mu",
                "0",
                "--sigma",
                "1",
                "--seed",
                "7",
            ]
            subprocess.run(cmd + ["--output", str(a)], check=True, cwd=ROOT)
            subprocess.run(cmd + ["--output", str(b)], check=True, cwd=ROOT)
            np.testing.assert_array_equal(np.loadtxt(a), np.loadtxt(b))


if __name__ == "__main__":
    unittest.main()

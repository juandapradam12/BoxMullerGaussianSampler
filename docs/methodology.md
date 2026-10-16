# Methodology

## Problem

Given parameters $\mu \in \mathbb{R}$ and $\sigma > 0$, generate $N$ independent samples

$$
X_1, X_2, \ldots, X_N \sim \mathcal{N}(\mu, \sigma^2)
$$

and compare the empirical distribution of $\{X_i\}$ with the closed-form density of the target law.

## Target density

The probability density function of $X \sim \mathcal{N}(\mu, \sigma^2)$ is

$$
f_X(x) = \frac{1}{\sigma\sqrt{2\pi}}
\exp\left(-\frac{(x - \mu)^2}{2\sigma^2}\right),
\qquad x \in \mathbb{R}.
$$

## Box–Muller transform

Uniform draws on $(-1, 1)^2$ are rejected until they fall inside the unit disk. Let $(U, V)$ be such a pair and set

$$
S = U^2 + V^2.
$$

Conditional on $0 < S < 1$, the polar Box–Muller mapping

$$
Z_1 = U \sqrt{\frac{-2\ln S}{S}},
\qquad
Z_2 = V \sqrt{\frac{-2\ln S}{S}}
$$

yields two independent standard normals $Z_1, Z_2 \sim \mathcal{N}(0, 1)$. Affine rescaling

$$
X = \mu + \sigma Z
$$

then produces samples from $\mathcal{N}(\mu, \sigma^2)$.

Each accepted pair supplies two standard normals; the implementation caches the unused twin so that consecutive calls amortize the rejection loop.

## Empirical check

From a realized sample $\{x_i\}_{i=1}^{N}$, the visualization module overlays:

1. a density-normalized histogram of $\{x_i\}$, and
2. the analytic curve $f_X(x)$.

Agreement improves with $N$; the sample mean and sample standard deviation are reported next to $(\mu, \sigma)$ as a quick consistency check:

$$
\bar{x} = \frac{1}{N}\sum_{i=1}^{N} x_i,
\qquad
s = \sqrt{\frac{1}{N-1}\sum_{i=1}^{N}(x_i - \bar{x})^2}.
$$

## Pipeline

```text
CLI / Makefile
      │
      ▼
src/main.c  ──►  src/box_muller.*  ──►  data/sample.dat
                                              │
                                              ▼
                                   scripts/visualize.py
                                              │
                                              ▼
                              figures/histogram_vs_pdf.png
```

The C layer owns sampling and I/O. The Python layer owns visualization and summary statistics. Generated artifacts stay out of version control.

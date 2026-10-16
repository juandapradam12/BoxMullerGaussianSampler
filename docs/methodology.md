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

## Uniform source (scope note)

The transform above assumes i.i.d. uniforms. This project uses the C standard library `rand()` for clarity and portability. That generator is adequate for a didactic / portfolio sampler; production Monte Carlo would typically swap in a higher-quality PRNG (for example PCG or xoshiro) behind the same Box–Muller API.

## Validation

From a realized sample $\{x_i\}_{i=1}^{N}$ the analysis layer reports:

1. **Histogram vs PDF** — density-normalized histogram overlaid on $f_X$.
2. **QQ plot** — sample quantiles against $F_X^{-1}$.
3. **Moment errors** —

$$
\bar{x} = \frac{1}{N}\sum_{i=1}^{N} x_i,
\qquad
s = \sqrt{\frac{1}{N-1}\sum_{i=1}^{N}(x_i - \bar{x})^2},
\qquad
\lvert\bar{x}-\mu\rvert,\ \lvert s-\sigma\rvert.
$$

4. **Kolmogorov–Smirnov distance** against the target CDF,

$$
D_N = \sup_x \lvert F_N(x) - F_X(x) \rvert,
$$

compared with the asymptotic $95\%$ critical value $1.36 / \sqrt{N}$.

## Pipeline

```text
CLI / Makefile
      │
      ▼
src/main.c  ──►  src/box_muller.*  ──►  data/sample.dat
                                              │
                                              ▼
                          scripts/visualize.py + gaussian_stats.py
                                              │
                              ┌───────────────┴───────────────┐
                              ▼                               ▼
                 figures/histogram_vs_pdf.png          figures/qq_plot.png
```

Automated checks live under `tests/` and run via `make test` (also wired into GitHub Actions).

# Gaussian Sampling with the Box–Muller Transform

Portfolio case study: a small, reproducible pipeline that draws i.i.d. Gaussian samples in C and validates them against the theoretical density in Python.

$$
X \sim \mathcal{N}(\mu, \sigma^2),
\qquad
f_X(x)=\frac{1}{\sigma\sqrt{2\pi}}
\exp\left(-\frac{(x-\mu)^2}{2\sigma^2}\right)
$$

## What this project demonstrates

- **Numerical sampling** via the polar Box–Muller method (rejection sampling on the unit disk, twin-sample caching).
- **Separation of concerns**: portable C sampler + thin Python visualization layer.
- **Reproducible runs** through CLI flags, Makefile parameters, and an explicit RNG seed.
- **Empirical validation**: density-normalized histogram overlaid on the closed-form PDF, plus sample mean / std checks.

## Repository layout

```text
├── src/
│   ├── box_muller.h      # Public sampling API
│   ├── box_muller.c      # Box–Muller implementation
│   └── main.c            # CLI entry point
├── scripts/
│   └── visualize.py      # Histogram vs. PDF
├── docs/
│   └── methodology.md    # Math background and design notes
├── Makefile
├── requirements.txt
└── README.md
```

Generated outputs (`bin/`, `data/`, `figures/`) are ignored by git.

## Requirements

- GCC (C11) with `libm`
- Python 3.10+
- `numpy`, `matplotlib` (see `requirements.txt`)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Quick start

Default run ($N=5000$, $\mu=2.5$, $\sigma=3.5$, seed $42$):

```bash
make
```

This builds `bin/gaussian_sampler`, writes `data/sample.dat`, and saves `figures/histogram_vs_pdf.png`.

### Custom parameters

```bash
make N=10000 MU=0 SIGMA=1 SEED=7 BINS=60
```

### Direct CLI usage

```bash
make bin/gaussian_sampler
./bin/gaussian_sampler --n 5000 --mu 2.5 --sigma 3.5 --seed 42 --output data/sample.dat
python3 scripts/visualize.py --input data/sample.dat --mu 2.5 --sigma 3.5 --bins 50
```

## Design notes

| Concern | Choice |
| --- | --- |
| Sampling | Polar Box–Muller with cached spare normal |
| Interface | `box_muller_sample` / `box_muller_fill` / `write_samples` |
| Configuration | Explicit CLI flags (no hardcoded experiment knobs in library code) |
| Validation | Visual PDF overlay + printed moment summary |
| Artifacts | Build products and plots stay local; sources stay clean |

See [docs/methodology.md](docs/methodology.md) for the transform derivation and pipeline diagram.

## Example output

For $\mu = 2.5$, $\sigma = 3.5$, $N = 5000$, seed $42$:

```text
Wrote 5000 samples from N(2.5, 3.5^2) to data/sample.dat (seed=42)
n=5000  mean=2.4676 (target 2.5000)  std=3.4701 (target 3.5000)
```

![Empirical histogram vs theoretical Gaussian PDF](docs/assets/example_histogram.png)

The histogram tracks $f_X$ closely; residual mismatch is ordinary Monte Carlo noise.

## License

MIT

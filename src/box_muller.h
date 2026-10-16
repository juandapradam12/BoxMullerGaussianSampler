#ifndef BOX_MULLER_H
#define BOX_MULLER_H

#include <stddef.h>

/**
 * Draw one sample from N(mu, sigma^2) using the polar Box–Muller method.
 * Internally caches the unused twin sample from each transform pair.
 */
double box_muller_sample(double mu, double sigma);

/**
 * Fill `out` with `n` i.i.d. samples from N(mu, sigma^2).
 * Returns 0 on success, -1 if `out` is NULL or `n` is zero.
 */
int box_muller_fill(double *out, size_t n, double mu, double sigma);

/**
 * Write `n` samples (one per line) to `path`.
 * Returns 0 on success, -1 on allocation or I/O failure.
 */
int write_samples(const char *path, size_t n, double mu, double sigma);

#endif /* BOX_MULLER_H */

#include "box_muller.h"

#include <math.h>
#include <stdio.h>
#include <stdlib.h>

double box_muller_sample(double mu, double sigma)
{
    static int has_spare = 0;
    static double spare = 0.0;

    if (has_spare) {
        has_spare = 0;
        return mu + sigma * spare;
    }

    double u;
    double v;
    double s;

    do {
        u = -1.0 + 2.0 * ((double)rand() / (double)RAND_MAX);
        v = -1.0 + 2.0 * ((double)rand() / (double)RAND_MAX);
        s = u * u + v * v;
    } while (s >= 1.0 || s == 0.0);

    const double scale = sqrt(-2.0 * log(s) / s);
    spare = v * scale;
    has_spare = 1;

    return mu + sigma * (u * scale);
}

int box_muller_fill(double *out, size_t n, double mu, double sigma)
{
    if (out == NULL || n == 0) {
        return -1;
    }

    for (size_t i = 0; i < n; ++i) {
        out[i] = box_muller_sample(mu, sigma);
    }

    return 0;
}

int write_samples(const char *path, size_t n, double mu, double sigma)
{
    if (path == NULL || n == 0) {
        return -1;
    }

    double *values = malloc(n * sizeof(*values));
    if (values == NULL) {
        return -1;
    }

    if (box_muller_fill(values, n, mu, sigma) != 0) {
        free(values);
        return -1;
    }

    FILE *fp = fopen(path, "w");
    if (fp == NULL) {
        free(values);
        return -1;
    }

    for (size_t i = 0; i < n; ++i) {
        if (fprintf(fp, "%.10f\n", values[i]) < 0) {
            fclose(fp);
            free(values);
            return -1;
        }
    }

    fclose(fp);
    free(values);
    return 0;
}

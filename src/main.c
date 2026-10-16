#include "box_muller.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

static void usage(const char *prog)
{
    fprintf(stderr,
            "Usage: %s [options]\n"
            "\n"
            "Generate i.i.d. Gaussian samples via the Box–Muller transform.\n"
            "\n"
            "Options:\n"
            "  --n N           Number of samples (default: 1000)\n"
            "  --mu MU         Mean (default: 0.0)\n"
            "  --sigma SIGMA   Standard deviation, must be > 0 (default: 1.0)\n"
            "  --seed SEED     RNG seed; omit to use time-based seed\n"
            "  --output PATH   Output file (default: data/sample.dat)\n"
            "  -h, --help      Show this help\n",
            prog);
}

static int parse_size(const char *text, size_t *out)
{
    char *end = NULL;
    unsigned long value = strtoul(text, &end, 10);
    if (end == text || *end != '\0' || value == 0) {
        return -1;
    }
    *out = (size_t)value;
    return 0;
}

static int parse_double(const char *text, double *out)
{
    char *end = NULL;
    double value = strtod(text, &end);
    if (end == text || *end != '\0') {
        return -1;
    }
    *out = value;
    return 0;
}

int main(int argc, char *argv[])
{
    size_t n = 1000;
    double mu = 0.0;
    double sigma = 1.0;
    unsigned int seed = (unsigned int)time(NULL);
    int seed_set = 0;
    const char *output = "data/sample.dat";

    for (int i = 1; i < argc; ++i) {
        if (strcmp(argv[i], "-h") == 0 || strcmp(argv[i], "--help") == 0) {
            usage(argv[0]);
            return 0;
        }
        if (strcmp(argv[i], "--n") == 0 && i + 1 < argc) {
            if (parse_size(argv[++i], &n) != 0) {
                fprintf(stderr, "Invalid --n value\n");
                return 1;
            }
        } else if (strcmp(argv[i], "--mu") == 0 && i + 1 < argc) {
            if (parse_double(argv[++i], &mu) != 0) {
                fprintf(stderr, "Invalid --mu value\n");
                return 1;
            }
        } else if (strcmp(argv[i], "--sigma") == 0 && i + 1 < argc) {
            if (parse_double(argv[++i], &sigma) != 0 || sigma <= 0.0) {
                fprintf(stderr, "Invalid --sigma value (must be > 0)\n");
                return 1;
            }
        } else if (strcmp(argv[i], "--seed") == 0 && i + 1 < argc) {
            char *end = NULL;
            unsigned long value = strtoul(argv[++i], &end, 10);
            if (end == argv[i] || *end != '\0') {
                fprintf(stderr, "Invalid --seed value\n");
                return 1;
            }
            seed = (unsigned int)value;
            seed_set = 1;
            (void)seed_set;
        } else if (strcmp(argv[i], "--output") == 0 && i + 1 < argc) {
            output = argv[++i];
        } else {
            fprintf(stderr, "Unknown or incomplete argument: %s\n", argv[i]);
            usage(argv[0]);
            return 1;
        }
    }

    srand(seed);

    if (write_samples(output, n, mu, sigma) != 0) {
        fprintf(stderr, "Failed to write samples to '%s'\n", output);
        return 1;
    }

    printf("Wrote %zu samples from N(%.6g, %.6g^2) to %s (seed=%u)\n",
           n, mu, sigma, output, seed);
    return 0;
}

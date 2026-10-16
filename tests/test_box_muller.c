#include "../src/box_muller.h"

#include <math.h>
#include <stdio.h>
#include <stdlib.h>

static int failures = 0;

static void expect(int condition, const char *message)
{
    if (!condition) {
        fprintf(stderr, "FAIL: %s\n", message);
        failures += 1;
    }
}

int main(void)
{
    expect(box_muller_fill(NULL, 10, 0.0, 1.0) == -1, "null buffer rejected");
    expect(write_samples(NULL, 10, 0.0, 1.0) == -1, "null path rejected");
    expect(write_samples("/tmp/box_muller_empty.dat", 0, 0.0, 1.0) == -1,
           "zero length rejected");

    box_muller_reset();
    srand(12345);

    const size_t n = 20000;
    double *values = malloc(n * sizeof(*values));
    expect(values != NULL, "allocation succeeded");
    if (values == NULL) {
        return 1;
    }

    expect(box_muller_fill(values, n, 1.0, 2.0) == 0, "fill succeeded");

    double mean = 0.0;
    for (size_t i = 0; i < n; ++i) {
        mean += values[i];
    }
    mean /= (double)n;

    double var = 0.0;
    for (size_t i = 0; i < n; ++i) {
        const double d = values[i] - mean;
        var += d * d;
    }
    var /= (double)(n - 1);
    const double std = sqrt(var);

    expect(fabs(mean - 1.0) < 0.05, "sample mean near 1");
    expect(fabs(std - 2.0) < 0.05, "sample std near 2");

    free(values);

    if (failures == 0) {
        puts("test_box_muller: OK");
        return 0;
    }
    fprintf(stderr, "test_box_muller: %d failure(s)\n", failures);
    return 1;
}

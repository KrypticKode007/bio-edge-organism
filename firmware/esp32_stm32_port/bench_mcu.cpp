#include <stdio.h>
#include <time.h>
#include "bio_edge_core.h"

static LifSnnCore bench_snn = {
    .weights = {
        { 0.95f,  0.40f, -0.20f,  0.10f },
        {-0.30f, -0.60f, -0.20f,  0.85f },
        { 0.20f,  0.75f,  0.90f, -0.50f }
    },
    .membrane_v = {0.0f, 0.0f, 0.0f},
    .tau = 0.85f,
    .threshold = 1.0f,
    .lr = 0.02f
};

int main(void) {
    const uint64_t ITERATIONS = 100000;
    BioTelemetry bus = {0.82f, 37.8f, 0.15f, 3.95f, {true, true, true, true}};
    uint32_t repairs = 0;
    volatile uint32_t sink = 0;

    struct timespec t0, t1;
    clock_gettime(CLOCK_MONOTONIC, &t0);

    for (uint64_t i = 0; i < ITERATIONS; i++) {
        if ((i % 25) == 0) bus.nodes[i % 4] = false;
        OrganismCommand c = step_organism_bare_metal(&bench_snn, &bus, &repairs);
        sink += (uint32_t)c;
    }

    clock_gettime(CLOCK_MONOTONIC, &t1);
    double elapsed_ns = (double)(t1.tv_sec - t0.tv_sec) * 1e9 + (double)(t1.tv_nsec - t0.tv_nsec);
    double mean_ns = elapsed_ns / (double)ITERATIONS;

    printf("=== BARE-METAL C++11 ARM64 BENCHMARK (%llu CYCLES) ===\n", (unsigned long long)ITERATIONS);
    printf("Mean Inference + Self-Repair Latency : %.2f ns (%.4f us)\n", mean_ns, mean_ns / 1000.0);
    printf("Throughput                           : %.2f MHz (cycles/sec)\n", 1000.0 / mean_ns);
    printf("Autonomous Node Repairs Executed     : %u\n", repairs);
    return 0;
}

#include <stdio.h>
#include "bio_edge_core.h"

static LifSnnCore edge_snn = {
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
    BioTelemetry sensor_bus = {
        .atp_nutrient = 0.85f,
        .tissue_temp_c = 37.4f,
        .shock_g = 0.12f,
        .voltage = 3.92f,
        .nodes = {true, true, true, true}
    };
    uint32_t total_repairs = 0;

    for (int cycle = 1; cycle <= 5; cycle++) {
        if (cycle == 3) {
            sensor_bus.shock_g = 2.95f;
            sensor_bus.nodes[0] = false;
        } else {
            sensor_bus.shock_g = 0.10f;
        }
        OrganismCommand cmd = step_organism_bare_metal(&edge_snn, &sensor_bus, &total_repairs);
        printf("[MCU Cycle %d] Command=%d | Repairs=%u\n", cycle, (int)cmd, total_repairs);
    }
    return 0;
}

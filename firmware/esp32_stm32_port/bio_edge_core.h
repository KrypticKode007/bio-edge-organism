#ifndef BIO_EDGE_CORE_H
#define BIO_EDGE_CORE_H

#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define NUM_INPUTS 4
#define NUM_POPS   3
#define LIF_STEPS  8

typedef struct {
    float atp_nutrient;
    float tissue_temp_c;
    float shock_g;
    float voltage;
    bool nodes[4]; // [motor_left, motor_right, chemo_sensor, thermo_receptor]
} BioTelemetry;

typedef struct {
    float weights[NUM_POPS][NUM_INPUTS];
    float membrane_v[NUM_POPS];
    float tau;
    float threshold;
    float lr;
} LifSnnCore;

typedef enum {
    CMD_FORAGE_ORGANIC = 0,
    CMD_EXPLORE_PERIMETER = 1,
    CMD_LOW_POWER_STASIS = 2,
    CMD_REFLEX_EVASION = 3
} OrganismCommand;

static inline float compute_free_energy(const BioTelemetry *t, uint8_t healthy_nodes) {
    float v_err = fmaxf(0.0f, (4.00f - t->voltage) / (4.00f - 3.35f));
    float atp_err = fmaxf(0.0f, (0.85f - t->atp_nutrient) / 0.85f);
    float temp_err = fmaxf(0.0f, (t->tissue_temp_c - 37.0f) / (42.0f - 37.0f));
    float node_err = 1.0f - ((float)healthy_nodes / 4.0f);
    float fe = sqrtf(0.35f*v_err*v_err + 0.30f*atp_err*atp_err + 0.20f*temp_err*temp_err + 0.15f*node_err*node_err);
    return fminf(1.0f, fe);
}

static inline OrganismCommand step_organism_bare_metal(LifSnnCore *snn, BioTelemetry *t, uint32_t *repairs_out) {
    // Priority 1: Hardware-Interrupt Threat Reflex (< 5 microseconds on ESP32/STM32)
    if (t->tissue_temp_c >= 45.0f || t->shock_g >= 2.2f) {
        return CMD_REFLEX_EVASION;
    }

    // Priority 2: Topological Self-Repair
    uint8_t healthy = 0;
    for (int i = 0; i < 4; i++) {
        if (!t->nodes[i]) {
            t->nodes[i] = true; // Reroute bus around damaged bio-actuator
            (*repairs_out)++;
        }
        healthy++;
    }

    // Priority 3: Free-Energy Homeostasis & LIF Spiking Inference
    float fe = compute_free_energy(t, healthy);
    float inputs[NUM_INPUTS] = {
        1.0f - t->atp_nutrient,
        fe,
        t->tissue_temp_c / 50.0f,
        (float)healthy / 4.0f
    };

    uint8_t spikes[NUM_POPS] = {0, 0, 0};
    for (int k = 0; k < LIF_STEPS; k++) {
        for (int p = 0; p < NUM_POPS; p++) {
            float current = 0.0f;
            for (int j = 0; j < NUM_INPUTS; j++) {
                current += snn->weights[p][j] * inputs[j];
            }
            snn->membrane_v[p] = (snn->tau * snn->membrane_v[p]) + (0.35f * current);
            if (snn->membrane_v[p] >= snn->threshold) {
                spikes[p]++;
                snn->membrane_v[p] = 0.0f;
            }
        }
    }

    uint8_t winner = 0;
    for (int p = 1; p < NUM_POPS; p++) {
        if (spikes[p] > spikes[winner]) winner = p;
    }

    // Online Reward-Modulated Hebbian Plasticity
    float reward = 1.0f - fe;
    for (int j = 0; j < NUM_INPUTS; j++) {
        snn->weights[winner][j] += snn->lr * reward * (inputs[j] - 0.5f);
        if (snn->weights[winner][j] > 1.5f) snn->weights[winner][j] = 1.5f;
        if (snn->weights[winner][j] < -1.5f) snn->weights[winner][j] = -1.5f;
    }

    return (OrganismCommand)winner;
}

#endif // BIO_EDGE_CORE_H

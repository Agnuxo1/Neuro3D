#version 430

// Dormant Blender GPU contract. This file is intentionally not dispatched by the
// addon or by the CPU test runner. A later GPU gate must compare its readback with
// Blender/core/photonic_model.py before enabling it.

layout(local_size_x = 64, local_size_y = 1, local_size_z = 1) in;

struct NeuronState {
    vec4 position_radius;
    vec4 optical_state; // phase, frequency, intensity, energy
    vec4 color;
};

layout(std430, binding = 0) readonly buffer NeuronInput { NeuronState input_state[]; };
layout(std430, binding = 1) writeonly buffer NeuronOutput { NeuronState output_state[]; };

uniform uint neuron_count;
uniform float delta_seconds;
uniform float activation_threshold;

void main() {
    uint index = gl_GlobalInvocationID.x;
    if (index >= neuron_count) {
        return;
    }

    NeuronState state = input_state[index];
    float phase = state.optical_state.x + state.optical_state.y * delta_seconds;
    float intensity = clamp(state.optical_state.z, 0.0, 1.0);
    float energy = clamp(state.optical_state.w * 0.98, 0.0, 1.0);
    if (intensity < activation_threshold) {
        energy *= 0.98;
    }
    state.optical_state = vec4(phase, state.optical_state.y, intensity, energy);
    output_state[index] = state;
}

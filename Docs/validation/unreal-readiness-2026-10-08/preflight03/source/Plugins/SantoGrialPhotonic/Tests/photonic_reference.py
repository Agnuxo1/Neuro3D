"""Small deterministic CPU oracle for the Santo Grial GPU vertical slice.

This is not a physical optics solver. It is the readable reference for the
digital model: intensity, phase, frequency and RGB are transported along a
fixed graph and accumulated as a coherent field.
"""

from __future__ import annotations

import hashlib
import math
import random
from dataclasses import dataclass


@dataclass
class Neuron:
    intensity: float
    phase: float
    frequency: float
    activation: float
    energy: float
    color: tuple[float, float, float]


@dataclass(frozen=True)
class Edge:
    source: int
    target: int
    weight: float
    delay: float


def build_graph(count: int, edges_per_neuron: int, seed: int) -> tuple[list[Neuron], list[Edge]]:
    rng = random.Random(seed)
    neurons = []
    for index in range(count):
        angle = index / count * 24.0 * math.pi
        color = (
            0.35 + 0.65 * abs(math.sin(angle)),
            0.25 + 0.75 * abs(math.sin(angle + 2.094)),
            0.25 + 0.75 * abs(math.sin(angle + 4.188)),
        )
        neurons.append(Neuron(0.05, 0.0, 450.0 + 120.0 * color[0], 0.0, 1.0, color))

    edges = []
    for source in range(count):
        for slot in range(edges_per_neuron):
            if count == 1:
                target = 0
            else:
                target = (source + 1 + ((source * 17 + slot * 13 + seed) % (count - 1))) % count
            edges.append(Edge(source, target, 0.65 / (slot + 1), 0.002 * (slot + 1)))
    rng.random()  # Keep the seed explicit in the oracle's construction contract.
    return neurons, edges


def step(neurons: list[Neuron], edges: list[Edge], dt: float, attenuation: float, threshold: float) -> list[Neuron]:
    real = [[0.0, 0.0, 0.0] for _ in neurons]
    imag = [[0.0, 0.0, 0.0] for _ in neurons]
    weighted_frequency = [0.0 for _ in neurons]
    total_weight = [0.0 for _ in neurons]

    for edge in edges:
        source = neurons[edge.source]
        travel = math.exp(-attenuation * edge.delay)
        intensity = max(0.0, source.intensity) * max(0.0, source.activation) * edge.weight * travel
        phase = source.phase + 2.0 * math.pi * source.frequency * (dt - edge.delay)
        c = math.cos(phase)
        s = math.sin(phase)
        for channel in range(3):
            real[edge.target][channel] += source.color[channel] * intensity * c
            imag[edge.target][channel] += source.color[channel] * intensity * s
        weighted_frequency[edge.target] += source.frequency * intensity
        total_weight[edge.target] += intensity

    result = []
    for index, previous in enumerate(neurons):
        power = [real[index][c] ** 2 + imag[index][c] ** 2 for c in range(3)]
        total_power = sum(power)
        response = max(0.0, min(1.0, 1.0 - math.exp(-total_power / max(threshold, 1e-5))))
        magnitude = math.sqrt(total_power)
        if magnitude > 1e-12:
            color = tuple(math.sqrt(value) / magnitude for value in power)
        else:
            color = previous.color
        color_length = math.sqrt(sum(value * value for value in color))
        color = tuple(value / color_length for value in color)
        if total_weight[index] > 1e-12:
            frequency = weighted_frequency[index] / total_weight[index]
        else:
            frequency = previous.frequency
        field_phase = math.atan2(
            sum(imag[index][c] * color[c] for c in range(3)),
            sum(real[index][c] * color[c] for c in range(3)),
        )
        result.append(
            Neuron(
                intensity=previous.intensity * 0.985 * (1.0 - min(1.0, dt * 8.0)) + magnitude * min(1.0, dt * 8.0),
                phase=field_phase,
                frequency=frequency,
                activation=response,
                energy=max(0.0, min(1.0, previous.energy - magnitude * dt * 0.01 + response * dt * 0.03)),
                color=color,
            )
        )
    return result


def signal_intensity(source: Neuron, edge: Edge, dt: float, attenuation: float) -> float:
    """The scalar transport invariant shared with EmitSignalsCS."""
    travel = math.exp(-attenuation * max(0.0, edge.delay))
    return max(0.0, source.intensity) * max(0.0, source.activation) * max(0.0, edge.weight) * travel


def checksum(neurons: list[Neuron]) -> str:
    payload = bytearray()
    for neuron in neurons:
        for value in (neuron.intensity, neuron.phase, neuron.frequency, neuron.activation, neuron.energy, *neuron.color):
            payload.extend(f"{value:.9e},".encode("ascii"))
    return hashlib.sha256(payload).hexdigest()


def run_oracle() -> dict[str, object]:
    neurons, edges = build_graph(32, 4, 1337)
    neurons[0] = Neuron(1.0, 0.0, 520.0, 1.0, 1.0, (1.0, 0.1, 0.05))
    initial = checksum(neurons)
    zero_weight = Edge(0, 1, 0.0, 0.0)
    direct = Edge(0, 1, 1.0, 0.0)
    delayed = Edge(0, 1, 1.0, 10.0)
    assert signal_intensity(neurons[0], zero_weight, 1.0 / 120.0, 0.015) == 0.0
    assert signal_intensity(neurons[0], delayed, 1.0 / 120.0, 0.015) <= signal_intensity(neurons[0], direct, 1.0 / 120.0, 0.015)
    neurons = step(neurons, edges, 1.0 / 120.0, 0.015, 0.25)
    reached = sum(1 for neuron in neurons if neuron.activation > 1e-6)
    assert reached > 0, "the pulse must reach at least one target neuron"
    for _ in range(7):
        neurons = step(neurons, edges, 1.0 / 120.0, 0.015, 0.25)
    final = checksum(neurons)
    active = sum(1 for neuron in neurons if neuron.activation > 1e-6)
    assert initial != final, "the pulse must change the state"
    assert all(0.0 <= neuron.activation <= 1.0 for neuron in neurons)
    assert all(0.0 <= neuron.energy <= 1.0 for neuron in neurons)
    return {"initial_checksum": initial, "final_checksum": final, "reached_neurons": reached, "active_neurons": active}


if __name__ == "__main__":
    print(run_oracle())

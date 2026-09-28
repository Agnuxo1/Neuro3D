"""Deterministic CPU oracle shared by Blender previews and future GPU adapters.

This module deliberately imports no Blender or GPU package. It is safe to run while
the GPU is occupied and is the reference against which a future shader readback is
compared.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import hashlib
import math
import struct
from typing import Iterable


Color = tuple[float, float, float]
Vector3 = tuple[float, float, float]


@dataclass
class NeuronState:
    position: Vector3
    phase: float = 0.0
    frequency: float = 520.0
    intensity: float = 0.0
    energy: float = 0.0
    color: Color = (1.0, 1.0, 1.0)


@dataclass(frozen=True)
class Edge:
    source: int
    target: int
    weight: float
    delay: float


@dataclass
class Graph:
    neurons: list[NeuronState]
    edges: list[Edge]


def _clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, value))


def build_deterministic_graph(neuron_count: int = 64, edges_per_neuron: int = 4, seed: int = 1337) -> Graph:
    """Create a repeatable spiral graph without relying on global random state."""

    neuron_count = max(1, int(neuron_count))
    edges_per_neuron = max(1, int(edges_per_neuron))
    neurons: list[NeuronState] = []
    for index in range(neuron_count):
        normalized = index / float(neuron_count)
        angle = normalized * 24.0 * math.pi + seed * 0.001
        radius = 1000.0 * math.sqrt(max(normalized, 0.001))
        position = (
            radius * math.cos(angle),
            radius * math.sin(angle),
            80.0 * math.sin(angle * 0.37),
        )
        color = (
            0.35 + 0.65 * abs(math.sin(angle)),
            0.25 + 0.75 * abs(math.sin(angle + 2.094)),
            0.25 + 0.75 * abs(math.sin(angle + 4.188)),
        )
        neurons.append(NeuronState(position=position, frequency=450.0 + 120.0 * color[0], color=color))

    edges: list[Edge] = []
    for source in range(neuron_count):
        for slot in range(edges_per_neuron):
            if neuron_count == 1:
                target = source
            else:
                offset = 1 + ((source * 17 + slot * 13 + seed) % max(1, neuron_count - 1))
                target = (source + offset) % neuron_count
            edges.append(Edge(source=source, target=target, weight=0.65 / (1 + slot), delay=0.002 * (1 + slot)))
    return Graph(neurons=neurons, edges=edges)


def clone_graph(graph: Graph) -> Graph:
    return deepcopy(graph)


def inject_pulse(graph: Graph, neuron_index: int, intensity: float, color: Color, frequency: float, phase: float) -> None:
    if not graph.neurons:
        return
    index = max(0, min(len(graph.neurons) - 1, int(neuron_index)))
    neuron = graph.neurons[index]
    neuron.intensity = max(0.0, float(intensity))
    neuron.energy = _clamp(float(intensity))
    neuron.color = tuple(_clamp(float(channel)) for channel in color)  # type: ignore[assignment]
    neuron.frequency = max(0.0, float(frequency))
    neuron.phase = float(phase)


def propagate_signals(graph: Graph, delta_seconds: float, attenuation: float = 0.015) -> list[tuple[Edge, float, float, Color]]:
    """Emit edge signals as (edge, amplitude, phase, color), without mutating state."""

    signals: list[tuple[Edge, float, float, Color]] = []
    attenuation = max(0.0, float(attenuation))
    for edge in graph.edges:
        source = graph.neurons[edge.source]
        amplitude = max(0.0, source.intensity) * max(0.0, edge.weight)
        amplitude *= math.exp(-attenuation * max(0.0, edge.delay))
        phase = source.phase + source.frequency * float(delta_seconds) - source.frequency * edge.delay
        signals.append((edge, amplitude, phase, source.color))
    return signals


def step(graph: Graph, delta_seconds: float, attenuation: float = 0.015, activation_threshold: float = 0.25) -> None:
    """Advance one deterministic reference step using coherent RGB accumulation."""

    delta_seconds = max(0.0, float(delta_seconds))
    accum = [[0.0, 0.0, 0.0] for _ in graph.neurons]
    phase_accum = [[0.0, 0.0] for _ in graph.neurons]
    frequency_accum = [0.0 for _ in graph.neurons]
    weight_accum = [0.0 for _ in graph.neurons]

    for edge, amplitude, phase, color in propagate_signals(graph, delta_seconds, attenuation):
        if amplitude <= 0.0:
            continue
        target = edge.target
        cosine = math.cos(phase)
        sine = math.sin(phase)
        for channel in range(3):
            accum[target][channel] += amplitude * color[channel] * cosine
        phase_accum[target][0] += amplitude * cosine
        phase_accum[target][1] += amplitude * sine
        frequency_accum[target] += amplitude * graph.neurons[edge.source].frequency
        weight_accum[target] += amplitude

    for index, neuron in enumerate(graph.neurons):
        coherent = math.sqrt(sum(channel * channel for channel in accum[index]) / 3.0)
        old_intensity = neuron.intensity
        neuron.intensity = _clamp(0.75 * old_intensity + coherent)
        neuron.energy = _clamp(0.94 * neuron.energy + 0.5 * coherent)
        if coherent >= max(0.0001, activation_threshold):
            neuron.phase = math.atan2(phase_accum[index][1], phase_accum[index][0])
            if weight_accum[index] > 0.0:
                neuron.frequency = frequency_accum[index] / weight_accum[index]
            norm = max(coherent, 1e-8)
            neuron.color = tuple(_clamp(abs(channel) / norm) for channel in accum[index])  # type: ignore[assignment]
        else:
            neuron.intensity = _clamp(neuron.intensity * 0.98)
            neuron.energy = _clamp(neuron.energy * 0.98)


def state_checksum(graph: Graph) -> str:
    """Return a stable checksum over the observable neural state."""

    digest = hashlib.sha256()
    for neuron in graph.neurons:
        values = (*neuron.position, neuron.phase, neuron.frequency, neuron.intensity, neuron.energy, *neuron.color)
        digest.update(struct.pack("<10f", *values))
    return digest.hexdigest()


def snapshot(graph: Graph) -> list[dict[str, object]]:
    return [
        {
            "position": list(neuron.position),
            "phase": neuron.phase,
            "frequency": neuron.frequency,
            "intensity": neuron.intensity,
            "energy": neuron.energy,
            "color": list(neuron.color),
        }
        for neuron in graph.neurons
    ]

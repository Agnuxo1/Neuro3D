"""Portable, CPU-only reference layer for Neuro3D."""

from .photonic_model import (
    Edge,
    Graph,
    NeuronState,
    build_deterministic_graph,
    clone_graph,
    inject_pulse,
    propagate_signals,
    state_checksum,
    step,
)

__all__ = [
    "Edge",
    "Graph",
    "NeuronState",
    "build_deterministic_graph",
    "clone_graph",
    "inject_pulse",
    "propagate_signals",
    "state_checksum",
    "step",
]

import math
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.photonic_model import Edge, Graph, NeuronState, build_deterministic_graph, inject_pulse, propagate_signals, snapshot, state_checksum, step


class PhotonicModelTests(unittest.TestCase):
    def test_same_seed_is_reproducible(self):
        self.assertEqual(
            state_checksum(build_deterministic_graph(32, 3, 1337)),
            state_checksum(build_deterministic_graph(32, 3, 1337)),
        )

    def test_different_seed_changes_graph_state(self):
        self.assertNotEqual(
            state_checksum(build_deterministic_graph(16, 2, 1337)),
            state_checksum(build_deterministic_graph(16, 2, 1338)),
        )

    def test_pulse_reaches_connected_neuron(self):
        graph = Graph(
            neurons=[NeuronState((0.0, 0.0, 0.0)), NeuronState((1.0, 0.0, 0.0))],
            edges=[Edge(0, 1, 0.8, 0.002)],
        )
        inject_pulse(graph, 0, 1.0, (0.2, 0.8, 1.0), 500.0, 0.0)
        step(graph, 0.016)
        self.assertGreater(graph.neurons[1].intensity, 0.0)

    def test_zero_weight_does_not_activate_target(self):
        graph = Graph(
            neurons=[NeuronState((0.0, 0.0, 0.0)), NeuronState((1.0, 0.0, 0.0))],
            edges=[Edge(0, 1, 0.0, 0.002)],
        )
        inject_pulse(graph, 0, 1.0, (1.0, 1.0, 1.0), 500.0, 0.0)
        step(graph, 0.016)
        self.assertEqual(graph.neurons[1].intensity, 0.0)
        self.assertEqual(graph.neurons[1].energy, 0.0)

    def test_attenuation_never_increases_signal(self):
        graph = Graph(
            neurons=[NeuronState((0.0, 0.0, 0.0)), NeuronState((1.0, 0.0, 0.0))],
            edges=[Edge(0, 1, 0.8, 0.5)],
        )
        inject_pulse(graph, 0, 1.0, (1.0, 0.5, 0.25), 500.0, 0.0)
        weak = propagate_signals(graph, 0.016, attenuation=0.01)[0][1]
        strong = propagate_signals(graph, 0.016, attenuation=2.0)[0][1]
        self.assertLessEqual(strong, weak)

    def test_state_stays_finite_and_bounded(self):
        graph = build_deterministic_graph(64, 4)
        inject_pulse(graph, 0, 1.0, (0.1, 0.5, 1.0), 600.0, 0.25)
        before = state_checksum(graph)
        for _ in range(8):
            step(graph, 1.0 / 60.0)
        after = state_checksum(graph)
        self.assertNotEqual(before, after)
        for neuron in graph.neurons:
            for value in (neuron.phase, neuron.frequency, neuron.intensity, neuron.energy, *neuron.color):
                self.assertTrue(math.isfinite(value))
            self.assertGreaterEqual(neuron.intensity, 0.0)
            self.assertLessEqual(neuron.intensity, 1.0)
            self.assertGreaterEqual(neuron.energy, 0.0)
            self.assertLessEqual(neuron.energy, 1.0)

    def test_boundary_inputs_are_safe(self):
        graph = build_deterministic_graph(0, 0, 1337)
        inject_pulse(graph, 999, 3.0, (2.0, -1.0, 0.5), -50.0, 0.0)
        step(graph, -1.0)
        neuron = graph.neurons[0]
        self.assertGreaterEqual(neuron.intensity, 0.0)
        self.assertLessEqual(neuron.intensity, 1.0)
        self.assertGreaterEqual(neuron.frequency, 0.0)
        self.assertEqual(len(snapshot(graph)), 1)

    def test_single_neuron_self_loop_is_stable(self):
        graph = build_deterministic_graph(1, 1, 1337)
        inject_pulse(graph, 0, 1.0, (1.0, 0.0, 0.0), 450.0, 0.0)
        for _ in range(32):
            step(graph, 1.0 / 60.0)
        self.assertTrue(all(math.isfinite(value) for value in (graph.neurons[0].phase, graph.neurons[0].intensity, graph.neurons[0].energy)))

    def test_repeated_steps_remain_bounded(self):
        graph = build_deterministic_graph(8, 2, 77)
        inject_pulse(graph, 0, 1.0, (0.3, 0.7, 1.0), 800.0, 0.0)
        for _ in range(256):
            step(graph, 1.0 / 120.0)
        self.assertTrue(all(0.0 <= neuron.energy <= 1.0 for neuron in graph.neurons))
        self.assertTrue(all(0.0 <= neuron.intensity <= 1.0 for neuron in graph.neurons))


if __name__ == "__main__":
    unittest.main(verbosity=2)

"""CPU-only ABI regressions; do not import or dispatch a GPU backend."""
import cmath
import copy
import math
from pathlib import Path
import struct
import unittest

from exp005_cascade_fixture import cascade_fixture
from exp005_gpu_pack import pack_paths
from exp005_triangle_oracle import trace_scene


def interpret(packed):
    # Test-only independent interpreter, NEVER an inference fallback.
    fields = {port: 0j for port in packed.ports}
    for b in range(0, len(packed.paths), 8):
        port, first, count, re, im, offset, _, _ = packed.paths[b:b+8]
        value = complex(re, im)
        for j in range(int(count)):
            distance, phase, code, _ = packed.hits[(int(first)+j)*4:(int(first)+j+1)*4]
            value *= cmath.exp(2j*math.pi*distance/packed.wavelength)
            value *= {0: 1, 1: 1/math.sqrt(2), 2: 1j/math.sqrt(2),
                      3: -cmath.exp(1j*phase)}[int(code)]
        fields[packed.ports[int(port)]] += value*cmath.exp(2j*math.pi*offset/packed.wavelength)
    return fields


def explicit_inputs(scene, paths):
    sources = {s['id']: s['field_reim'] for s in scene['sources']}
    return [dict(path, initial_field=sources[path['source_id']]) for path in paths]


class PackTests(unittest.TestCase):
    def fixture(self):
        scene = cascade_fixture(surface='binary_quad')
        return scene, explicit_inputs(scene, trace_scene(scene)['paths'])

    def test_all_bases_and_pairs_match_independent_oracle(self):
        from exp005_cascade_runtime import probes
        for _, amps in probes():
            scene = cascade_fixture(surface='binary_quad')
            for source, value in zip(scene['sources'], amps):
                source['field_reim'] = [value.real, value.imag]
            oracle = trace_scene(scene)
            actual = interpret(pack_paths(scene, explicit_inputs(scene, oracle['paths'])))
            self.assertEqual(set(actual), set(oracle['fields']))
            self.assertLess(max(abs(actual[p]-oracle['fields'][p]) for p in actual), 1e-12)

    def test_buffers_roundtrip_and_explicit_dark_port(self):
        scene, paths = self.fixture()
        # Keep only b.col; a.Y is explicitly dark, not dropped by packing.
        scene['sources'][0]['field_reim'] = [0, 0]
        scene['sources'][2]['field_reim'] = [1, 0]
        packed = pack_paths(scene, explicit_inputs(scene, trace_scene(scene)['paths']))
        self.assertEqual(interpret(packed)['a.Y'], 0j)
        for raw, values in zip(packed.buffers(), (packed.paths, packed.hits)):
            self.assertEqual(struct.unpack(f'<{len(values)}d', raw), values)

    def test_invalid_history_and_input_rejected(self):
        scene, paths = self.fixture()
        for change in ('distance', 'event', 'field', 'offset', 'truncated', 'count', 'unknown'):
            altered = copy.deepcopy(paths)
            if change == 'distance': altered[0]['hits'][0]['distance_BU'] = float('nan')
            if change == 'event': altered[0]['hits'][0]['event'] = 'mirror'
            if change == 'field': altered[0]['initial_field'] = [0, 1]
            if change == 'offset': altered[0]['reference_offset_BU'] = float('inf')
            if change == 'truncated': altered[0]['hits'].pop()
            if change == 'count': altered = paths*513
            if change == 'unknown': altered[0]['hits'][0]['object_id'] = 'missing'
            with self.subTest(change=change), self.assertRaises((ValueError, KeyError)):
                pack_paths(scene, altered)

    def test_phase_causality_is_not_packed_as_a_cpu_coefficient(self):
        scene, paths = self.fixture()
        original = pack_paths(scene, paths)
        scene['objects']['a.r1']['phase_rad'] += .1
        changed = pack_paths(scene, paths)
        self.assertEqual(original.paths, changed.paths)
        diffs = [i for i, (a,b) in enumerate(zip(original.hits, changed.hits)) if a != b]
        self.assertTrue(diffs)
        self.assertTrue(all(i % 4 == 1 for i in diffs))
        self.assertGreater(max(abs(interpret(original)[p]-interpret(changed)[p]) for p in original.ports), .001)

    def test_shader_has_gpu_phase_and_full_complex_reduction(self):
        shader = (Path(__file__).parents[1]/'shaders'/'exp005_path_fields.glsl').read_text()
        for token in ('rotate_field', 'sum_field+=value', 'dot(sum_field,sum_field)', 'double wavelength_BU'):
            self.assertIn(token, shader)
        import re
        self.assertIsNone(re.search(r'\batomic\w*\s*\(', shader))


if __name__ == '__main__': unittest.main()

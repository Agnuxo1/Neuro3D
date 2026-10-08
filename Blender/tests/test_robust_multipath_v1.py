"""Prospective point-3 gates: independent analytic optics and adverse geometry."""
import copy
from fractions import Fraction as F
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'benchmarks'/'capacity_audit'))
from robust_multipath_v1 import trace_scene, select, geometry, reflected, vector
from exp005_chain_fixture import chain_fixture, inputs, set_fields, analytic_fields


def plane_x(x, role='det', axis=(1, 0, 0), **extra):
    row = {'kind': role, 'vertices_world_BU': [(x, -4, -4), (x, 4, -4), (x, 0, 5)], 'faces': [(0, 1, 2)]}
    if role in ('det', 'escape'): row.update(mode_origin_BU=(x, 0, 0), mode_direction=axis)
    if role == 'mirror': row['phase_rad'] = 0
    if role == 'bs': row['power_transmittance'] = .5
    row.update(extra)
    return row


def scene(objects, origin=(0, 0, 0), direction=(1, 0, 0)):
    return {'schema': 'exp005-readback-v2', 'lambda_BU': .125, 'objects': objects, 'undeclared_meshes': [],
            'sources': [{'id': 'input', 'position_BU': origin, 'direction': direction, 'field_reim': [1, 0]}]}


class CompletePaths(unittest.TestCase):
    def test_all_k3_k4_analytic_inputs(self):
        for cells in (3, 4):
            snapshot = chain_fixture(cells)
            for label, amplitudes in inputs(cells+1):
                with self.subTest(cells=cells, probe=label):
                    set_fields(snapshot, amplitudes)
                    result = trace_scene(snapshot)
                    self.assertEqual(result['status'], 'COMPLETE', result['unresolved'][:1])
                    expected = analytic_fields(cells, amplitudes)
                    self.assertLessEqual(max(abs(result['fields'][p]-expected[p]) for p in expected), 1e-11)
                    self.assertLessEqual(abs(result['input_power']-result['output_power']), 1e-11)
                    self.assertGreater(result['departure_exclusions'], 0)

    def test_all_k3_k4_treatments(self):
        for cells in (3, 4):
            baseline = trace_scene(chain_fixture(cells))
            for treatment in ('phase', 'shift', 'T', 'lambda', 'sham'):
                with self.subTest(cells=cells, treatment=treatment):
                    result = trace_scene(chain_fixture(cells, treatment=treatment))
                    self.assertEqual(result['status'], 'COMPLETE', result['unresolved'][:1])
                    effect = max(abs(result['powers'][p]-baseline['powers'][p]) for p in baseline['powers'])
                    self.assertGreater(effect, 1e-3) if treatment != 'sham' else self.assertEqual(effect, 0)

    def test_tiny_positive_gap_is_retained(self):
        gap = F(1, 2**44)
        result = trace_scene(scene({'splitter': plane_x(1, 'bs', power_transmittance=1), 'out': plane_x(1+gap)}))
        self.assertEqual(result['status'], 'COMPLETE')
        self.assertEqual(result['paths'][0]['hits'][-1]['parameter'], gap)
        self.assertEqual(len(result['paths'][0]['hits']), 2)

    def test_both_splitter_branches_and_exact_zeros(self):
        for tau, expected_count in ((.5, 2), (0, 1), (1, 1)):
            result = trace_scene(scene({'bs': plane_x(1, 'bs', power_transmittance=tau),
                'right': plane_x(2), 'left': plane_x(-1, 'escape', axis=(-1, 0, 0))}))
            self.assertEqual(result['status'], 'COMPLETE')
            self.assertEqual(len(result['paths']), expected_count)
            self.assertAlmostEqual(result['output_power'], 1, places=14)

    def test_return_to_same_primitive_and_loop_is_incomplete(self):
        result = trace_scene(scene({'left': plane_x(0, 'mirror'), 'right': plane_x(1, 'mirror'),
                                  'out': plane_x(2)}, origin=(.5, 0, 0)), max_depth=7)
        self.assertEqual(result['status'], 'INCOMPLETE')
        self.assertIsNone(result['fields'])
        self.assertEqual(result['unresolved'][0]['status'], 'RESOURCE_LIMIT')
        history = result['unresolved'][0]['ray']['history']
        self.assertEqual(history[0]['primitive_id'], history[2]['primitive_id'])
        self.assertEqual(history[2]['parameter'], 1)

    def test_oblique_exact_reflection(self):
        self.assertEqual(reflected(vector((1, 2, 3)), vector((3, -1, 2))), vector((-2, 3, 1)))


class ExplicitUnresolved(unittest.TestCase):
    def assert_status(self, snapshot, expected, **kwargs):
        result = trace_scene(snapshot, **kwargs)
        self.assertEqual(result['status'], 'INCOMPLETE')
        self.assertIsNone(result['fields']); self.assertIsNone(result['powers'])
        self.assertEqual(result['unresolved'][0]['status'], expected)

    def test_independent_contact(self):
        self.assert_status(scene({'contact': plane_x(0, 'mirror'), 'out': plane_x(2)}), 'CONTACT')

    def test_tie_different_objects(self):
        self.assert_status(scene({'a': plane_x(1, 'mirror'), 'b': plane_x(1, 'mirror'), 'out': plane_x(2)}), 'TRUE_TIE')

    def test_outer_boundary(self):
        self.assert_status(scene({'out': plane_x(1)}, origin=(0, 0, -4)), 'BOUNDARY')

    def test_lost_ray(self):
        self.assert_status(scene({'out': plane_x(1)}, direction=(-1, 0, 0)), 'MISS')

    def test_mode_mismatch(self):
        self.assert_status(scene({'out': plane_x(1, axis=(1, 1, 0))}), 'MODE_MISMATCH')

    def test_cast_bound_preserves_pending(self):
        snapshot = scene({'bs': plane_x(1, 'bs'), 'right': plane_x(2), 'left': plane_x(-1, 'escape', axis=(-1, 0, 0))})
        self.assert_status(snapshot, 'RESOURCE_LIMIT', max_rays=1)
        result = trace_scene(snapshot, max_rays=1)
        self.assertEqual(len(result['unresolved'][0]['pending']), 1)

    def test_degenerate_and_zero_direction_rejected(self):
        snapshot = scene({'out': plane_x(1)})
        snapshot['objects']['out']['vertices_world_BU'][2] = (1, 0, -4)
        with self.assertRaisesRegex(ValueError, 'degenerate'): trace_scene(snapshot)
        with self.assertRaisesRegex(ValueError, 'nonzero'): trace_scene(scene({'out': plane_x(1)}, direction=(0, 0, 0)))

    def test_internal_seam_and_departure(self):
        quad = plane_x(1, 'bs', power_transmittance=1)
        quad['vertices_world_BU'] = [(1, -1, -1), (1, 1, -1), (1, 1, 1), (1, -1, 1)]
        quad['faces'] = [(0, 1, 2), (0, 2, 3)]
        result = trace_scene(scene({'quad': quad, 'out': plane_x(2)}))
        self.assertEqual(result['status'], 'COMPLETE')
        self.assertEqual(result['paths'][0]['hits'][0]['coincident_primitives'], [0, 1])
        self.assertEqual(result['departure_exclusions'], 2)

    def test_nonplanar_crease_is_unresolved(self):
        crease = plane_x(1, 'mirror')
        crease['vertices_world_BU'] = [(1, -1, -1), (1, 1, -1), (1, 1, 1), (2, -1, 1)]
        crease['faces'] = [(0, 1, 2), (0, 2, 3)]
        self.assert_status(scene({'crease': crease, 'out': plane_x(3)}), 'TRUE_TIE')

    def test_finite_coplanar_ray_not_in_remote_triangle(self):
        remote = {'kind': 'mirror', 'phase_rad': 0, 'vertices_world_BU': [(1, 4, 0), (3, 4, 0), (2, 6, 0)], 'faces': [(0, 1, 2)]}
        result = trace_scene(scene({'remote': remote, 'out': plane_x(4)}))
        self.assertEqual(result['status'], 'COMPLETE')

    def test_actual_coplanar_overlap(self):
        surface = {'kind': 'mirror', 'phase_rad': 0, 'vertices_world_BU': [(1, -1, 0), (3, -1, 0), (2, 1, 0)], 'faces': [(0, 1, 2)]}
        self.assert_status(scene({'surface': surface, 'out': plane_x(4)}), 'COPLANAR')


if __name__ == '__main__': unittest.main()

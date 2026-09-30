import hashlib
import math
import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[1]/'benchmarks'/'capacity_audit'))
from unittest.mock import patch
import nearest_hit_v2 as previous
import precision_v3 as candidate
from exp005_precision_fixture import cases, direct, reflected, query, cpu_evidence
from exp005_triangle_oracle import trace_scene


class PrecisionV3Tests(unittest.TestCase):
    def test_shader_only_changes_two_declared_boundaries(self):
        before = previous.shader_source(); after = candidate.shader_source()
        expected = before.replace('const double BIAS=1.0e-6lf;', 'const double BIAS=0.0lf;')
        expected = expected.replace('if(dot(ray.d,axis)<1.0lf-1.0e-6lf)',
                                    'if(dot(ray.d,axis)<1.0lf-1.0e-9lf)')
        self.assertEqual(after, expected)
        self.assertEqual(hashlib.sha256(previous.BASE.read_bytes()).hexdigest(), previous.BASE_SHA)
        self.assertIn('if(t<=1.0e-9lf) return false;', after)
        self.assertIn('abs(t-best)<=1.0e-9lf', after)
        with patch.object(candidate, 'PART_SHA', 'wrong'):
            with self.assertRaises(ValueError): candidate.shader_source()

    def test_close_initial_surface_is_not_skipped(self):
        scene = direct()
        self.assertIsNone(query(scene, (0., 0., 0.), (1., 0., 0.), bias=1e-6))
        hit = query(scene, (0., 0., 0.), (1., 0., 0.))
        self.assertEqual(hit['object'], 'D'); self.assertAlmostEqual(hit['distance_BU'], 1e-8, places=15)
        oracle = trace_scene(scene, max_rays=4)
        self.assertAlmostEqual(oracle['paths'][0]['length_BU'], 1e-8, places=15)

    def test_close_surface_after_reflection_and_self_hit(self):
        scene = reflected()
        self.assertIsNone(query(scene, (1., 0., 0.), (0., -1., 0.), bias=1e-6))
        hit = query(scene, (1., 0., 0.), (0., -1., 0.))
        self.assertEqual(hit['object'], 'D')
        self.assertAlmostEqual(hit['distance_BU'], 1e-8, places=15)
        oracle = trace_scene(scene, max_rays=4)
        self.assertEqual(oracle['rays'], 2)
        self.assertAlmostEqual(oracle['paths'][0]['length_BU'], 1+1e-8, places=14)
        self.assertEqual([h['object_id'] for h in oracle['paths'][0]['hits']], ['M', 'D'])

    def test_mode_old_acceptance_disagrees_with_oracle(self):
        axis = (math.cos(2e-4), math.sin(2e-4), 0.)
        self.assertTrue(candidate.terminal_accept((1., 0., 0.), axis, dot_tolerance=1e-6))
        self.assertFalse(candidate.terminal_accept((1., 0., 0.), axis))
        with self.assertRaisesRegex(ValueError, 'arrival direction'):
            trace_scene(direct(2., 2e-4), max_rays=4)

    def test_all_frozen_fixtures_have_expected_oracle_status(self):
        self.assertEqual(len(list(cases())), 8)
        for _, scene, status in cases():
            if status:
                with self.assertRaisesRegex(ValueError, 'arrival direction'): trace_scene(scene, max_rays=4)
            else:
                oracle = trace_scene(scene, max_rays=4)
                self.assertAlmostEqual(oracle['output_power'], 1.)
                self.assertEqual(len(oracle['paths']), 1)

    def test_t_min_and_invalid_modes_stay_explicit(self):
        # This candidate still cannot resolve distances <=1e-9; no Maxwell claim.
        self.assertIsNone(query(direct(1e-9), (0., 0., 0.), (1., 0., 0.)))
        self.assertIsNotNone(query(direct(2e-9), (0., 0., 0.), (1., 0., 0.)))
        for axis in ((0., 0., 0.), (float('nan'), 0., 0.), (True, 0., 0.)):
            with self.assertRaises(ValueError): candidate.terminal_accept((1., 0., 0.), axis)
        for tolerance in (True, -1., 1., float('inf')):
            with self.assertRaises(ValueError): candidate.terminal_accept((1., 0., 0.), (1., 0., 0.), dot_tolerance=tolerance)

    def test_retained_cpu_evidence_and_runtime_readiness(self):
        from exp005_precision_runtime import probes
        from frontier_inputs import pack_frontier
        from exp005_mode_gate import mode_geometry
        evidence = cpu_evidence()
        self.assertEqual(len(evidence['cases']), 8)
        rows = list(probes())
        self.assertEqual(len(rows), 29)
        self.assertEqual(sum(r[2] != 0 for r in rows), 15)
        for _, snapshot, _ in rows:
            mode_geometry(snapshot)
            self.assertLessEqual(pack_frontier(snapshot).geometry.triangle_count, 8)

    def test_reauditor_rejects_failed_or_incomplete_runtime(self):
        from exp005_precision_audit import audit
        with self.assertRaisesRegex(ValueError, 'runtime'):
            audit({'passed': False})
        with self.assertRaisesRegex(ValueError, '36 dispatches'):
            audit({'passed': True, 'raw_cases': [], 'legacy_precision': [], 'real_cases': []})


if __name__ == '__main__': unittest.main()

"""New adjacent-binary64 gaps; no PRECISION005/006 sweep or native run."""
from copy import deepcopy
from fractions import Fraction as F
import hashlib
import json
import math
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'Blender/tests'))
sys.path.insert(0, str(ROOT/'Blender/benchmarks/capacity_audit'))
from root_transport_topology_cpu_v1 import audit_root_transport

PINS = {
    'Blender/benchmarks/capacity_audit/history_lineage_cpu_v2.py': '391dfc06fd2f37d8fb6ce2845b71f02d4eeba33007619ae6e4aae27ae5169bae',
    'Blender/benchmarks/capacity_audit/frontier_inputs.py': '8f6ad2037ede24934c50fb9c3980f0e00a3aeafaa87bf1de53b80c54271375a1',
    'Blender/tests/exp005_blender_gpu.py': '851f29f9b1fb9b22948f59597d40fa8a55828040673fe0050d24e077b57cf497',
    'coordinacion/respuestas/LEDGER-INTERVAL-001-CODEX.json': '77a0b36f096cdf8ff603d41993bec661765f7be3c303bba73ac7fae69f8ca398',
    'Blender/shaders/exp005_shared_frontier.glsl': '914bf2962ead3c6a7b721a8dc2aa6c1e796af4bde1892db1802c3ca93ebdfcd1',
}


def scene(origin_x, terminal_xs):
    return {'schema': 'exp005-readback-v2', 'lambda_BU': .125,
        'undeclared_meshes': [], 'objects': {name: {'kind': 'det',
            'vertices_world_BU': [[x,.875,-.125], [x,1.125,-.125],
                                  [x,1.125,.125], [x,.875,.125]],
            'faces': [[0,1,2],[0,2,3]], 'mode_origin_BU': [x,1.,0.],
            'mode_direction': [1.,0.,0.]}
            for name,x in terminal_xs},
        'sources': [{'id': 's', 'position_BU': [origin_x,1.,0.],
                     'direction': [1.,0.,0.], 'field_reim': [1.,0.]}]}


class RootTransportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for path, sha in PINS.items():
            if hashlib.sha256((ROOT/path).read_bytes()).hexdigest() != sha:
                raise ValueError('changed frozen dependency: '+path)
        cls.evidence = {'pins_verified': PINS, 'new_cases': {},
                        'old_precision_sweeps_rerun': False, 'GPU_executed': False}

    def test_adjacent_source_terminal_gap_becomes_unproved_zero_contact(self):
        x = .1; neighbor = math.nextafter(x, math.inf)
        self.assertEqual(F(neighbor)-F(x), F(1,2**56))
        result = audit_root_transport(scene(x, [('A',neighbor)]))
        row = result['root_queries'][0]
        self.assertEqual(row['original']['ray_parameter_rational'], [1,2**56])
        self.assertFalse(row['decoded']['accepted_exact_CPU_root_query'])
        self.assertIn('source contact', row['decoded']['reason'])
        self.assertFalse(result['accepted_CPU_root_topology_parity_only'])
        self.evidence['new_cases']['source_gap_2^-56_FAIL'] = result

    def test_adjacent_terminal_gap_becomes_ambiguous_hit(self):
        result = audit_root_transport(scene(0., [('A',.1), ('B',math.nextafter(.1,math.inf))]))
        row = result['root_queries'][0]
        self.assertEqual(row['original']['object_id'], 'A')
        self.assertIn('coincident hit ambiguous', row['decoded']['reason'])
        self.assertFalse(result['accepted_CPU_root_topology_parity_only'])
        self.evidence['new_cases']['terminal_gap_2^-56_FAIL'] = result

    def test_resolved_gap_and_exact_control_preserve_root_topology(self):
        for name, snapshot in (
                ('resolved_gap_2^-30', scene(0., [('A',.1), ('B',.1+2.**-30)])),
                ('exact_dyadic_control', scene(0., [('A',.125), ('B',.25)]))):
            before = deepcopy(snapshot)
            result = audit_root_transport(snapshot)
            self.assertEqual(snapshot, before)
            self.assertTrue(result['accepted_CPU_root_topology_parity_only'])
            self.assertFalse(result['complete_scene_or_field_certified'])
            self.assertFalse(result['native_promotion_allowed'])
            self.evidence['new_cases'][name] = result

    def test_original_contact_is_never_repaired_by_transport(self):
        result = audit_root_transport(scene(.125, [('A',.125)]))
        row = result['root_queries'][0]
        self.assertFalse(row['original']['accepted_exact_CPU_root_query'])
        self.assertFalse(result['accepted_CPU_root_topology_parity_only'])
        self.evidence['new_cases']['original_source_contact_FAIL'] = result

    def test_distinct_sources_each_have_a_bound_root_query(self):
        snapshot = scene(0., [('A',.125)])
        second = deepcopy(snapshot['sources'][0]); second['id']='other'
        second['position_BU'][0] = -.125; snapshot['sources'].append(second)
        result = audit_root_transport(snapshot)
        self.assertEqual(result['source_order'], ['s','other'])
        self.assertEqual([row['source_id'] for row in result['root_queries']], ['s','other'])
        self.assertEqual([row['original']['ray_parameter_rational'] for row in result['root_queries']], [[1,8],[1,4]])

    def test_fail_closed_unknown_mesh_or_degenerate_direction(self):
        snapshot = scene(0., [('A',.125)])
        snapshot['undeclared_meshes'] = ['untracked']
        with self.assertRaises(ValueError): audit_root_transport(snapshot)
        snapshot['undeclared_meshes'] = []; snapshot['sources'][0]['direction'] = [0.,0.,0.]
        with self.assertRaises(ValueError): audit_root_transport(snapshot)


if __name__ == '__main__':
    result = unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromTestCase(RootTransportTests))
    if hasattr(RootTransportTests,'evidence'):
        print(json.dumps(RootTransportTests.evidence,sort_keys=True,allow_nan=False))
    sys.exit(0 if result.wasSuccessful() else 1)

import unittest
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[1]/'benchmarks'/'capacity_audit'))
from primitive_return_guard_v1 import classify_return
from exp005_primitive_return_audit import folded_control, audit as return_audit
from exp005_self_hit_audit import audit as self_hit_audit


class PrimitiveReturnTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.retained = self_hit_audit()

    def test_replay_after_json_roundtrip_has_no_numeric_relaxation(self):
        retained = json.loads(json.dumps(self.retained))
        result = return_audit(retained)
        self.assertEqual(len(result['explicit_same_triangle_candidates']), 12)
        self.assertTrue(all(x['guard']['action'] == 'abort'
                            for x in result['explicit_same_triangle_candidates']))

    def test_corrupt_retained_numeric_query_is_rejected(self):
        retained = json.loads(json.dumps(self.retained))
        retained['retained_same_triangle_adversaries'][0]['world_query']['first_distance_BU'] += 1e-4
        with self.assertRaisesRegex(ValueError, 'replay mismatch'): return_audit(retained)

    def classify(self, previous=0, candidate=0, event='mirror', distance=1e-8):
        return classify_return(previous_primitive=previous, candidate_primitive=candidate,
            departure_event=event, distance_BU=distance)

    def test_same_triangle_aborts_instead_of_skipping(self):
        for event in ('mirror', 't', 'r'):
            for distance in (1e-12, 1e-8, 2.):
                self.assertEqual(self.classify(event=event, distance=distance)['action'], 'abort')

    def test_source_ray_has_no_previous_primitive(self):
        self.assertEqual(self.classify(previous=None, event=None)['action'], 'continue')

    def test_other_triangles_not_excluded_by_object_identity(self):
        result = folded_control()
        steps = result['steps']
        self.assertEqual([x['query']['first_triangle']//2 for x in steps], [0, 1, 0])
        self.assertTrue(all(x['guard']['action'] == 'continue' for x in steps))
        self.assertEqual(set(result['initial_record']['object_ids']), {'folded_object'})

    def test_only_immediate_primitive_is_remembered(self):
        self.assertEqual(self.classify(previous=2, candidate=0)['action'], 'continue')

    def test_invalid_primitive_ids_fail_closed(self):
        for value in (True, -1, 64, '0', 1.5):
            with self.assertRaises(ValueError): self.classify(candidate=value)
            with self.assertRaises(ValueError): self.classify(previous=value)

    def test_invalid_departure_state_fails_closed(self):
        for event in (None, 'detect', 'escape', 'scatter'):
            with self.assertRaises(ValueError): self.classify(event=event)
        with self.assertRaises(ValueError): self.classify(previous=None)

    def test_invalid_distance_fails_closed(self):
        for value in (0., -1., True, float('nan'), float('inf')):
            with self.assertRaises(ValueError): self.classify(distance=value)


if __name__ == '__main__': unittest.main()

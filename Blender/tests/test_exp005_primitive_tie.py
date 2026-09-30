import itertools
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).parents[1]/'benchmarks'/'capacity_audit'))
from primitive_tie_guard_v1 import resolve_candidates
from exp005_primitive_tie_audit import SNAPSHOT, MANIFEST, PREVIOUS, hit, audit


class PrimitiveTieTests(unittest.TestCase):
    def resolve(self, hits, previous=PREVIOUS, manifest=MANIFEST, sha=SNAPSHOT):
        return resolve_candidates(snapshot_sha256=sha, manifest=manifest,
                                  candidates=hits, previous=previous)

    def test_naive_composition_counterexample_retained(self):
        r = audit()
        self.assertEqual(r['naive_continues'], 3)
        self.assertEqual(r['proposed_aborts'], 6)

    def test_manifest_and_candidates_reordering_stable(self):
        expected = self.resolve([hit(7), hit(2), hit(9, 3.)])
        for manifest in itertools.permutations(MANIFEST):
            for hits in itertools.permutations((hit(7), hit(2), hit(9, 3.))):
                self.assertEqual(self.resolve(hits, manifest=manifest), expected)
        self.assertEqual(expected['selected_primitive'], 2)

    def test_exact_inclusive_boundary_and_outside(self):
        self.assertEqual(self.resolve([hit(2, 1e-9), hit(7, 2e-9)])['action'], 'abort')
        r = self.resolve([hit(2, 1e-9), hit(7, 2.000001e-9)])
        self.assertEqual(r['action'], 'continue')
        self.assertEqual(r['minimum_distance_BU'], 1e-9)
        self.assertEqual(r['tie_primitive_ids'], [2])

    def test_band_does_not_replace_true_minimum(self):
        r = self.resolve([hit(7, 3.), hit(2, 2.+5e-10), hit(9, 2.)])
        self.assertEqual(r['selected_primitive'], 9)
        self.assertEqual(r['minimum_distance_BU'], 2.)
        self.assertEqual(r['action'], 'continue')

    def test_source_coplanar_tie_and_reverse_normals(self):
        r = self.resolve([hit(7, normal=(-2., 0., 0.)), hit(2)], previous=None)
        self.assertEqual(r['action'], 'continue')
        self.assertEqual(r['selected_primitive'], 2)

    def test_object_and_normal_ambiguity_not_suppressed(self):
        m = [dict(row, object_id=str(row['primitive_id'])) for row in MANIFEST]
        self.assertEqual(self.resolve([hit(2), hit(9)], manifest=m)['action'], 'abort')
        self.assertEqual(self.resolve([hit(2), hit(9, normal=(0., 1., 0.))])['action'], 'abort')

    def test_legitimate_other_face_and_later_return_not_globally_excluded(self):
        for previous, candidate in ((7, 2), (2, 7)):
            state = dict(PREVIOUS, primitive_id=previous)
            self.assertEqual(self.resolve([hit(candidate)], previous=state)['action'], 'continue')

    def test_miss_does_not_invent_valid_hit(self):
        self.assertEqual(self.resolve([])['action'], 'miss')

    def test_snapshot_state_mismatch_and_bad_labels(self):
        with self.assertRaises(ValueError): self.resolve([hit(2)], sha='b'*64)
        for sha in ('', 'a'*63, 'A'*64, None):
            with self.assertRaises(ValueError): self.resolve([hit(2)], sha=sha)
        for event in (None, 'detect', 'scatter'):
            with self.assertRaises(ValueError):
                self.resolve([hit(2)], previous=dict(PREVIOUS, departure_event=event))

    def test_duplicate_unknown_and_bad_primitive_ids(self):
        for hits in ([hit(2), hit(2)], [hit(1)], [hit(True)], [hit(64)]):
            with self.assertRaises(ValueError): self.resolve(hits)
        for m in ([], MANIFEST+[MANIFEST[0]], [{'primitive_id': 0, 'object_id': ''}]):
            with self.assertRaises(ValueError): self.resolve([], manifest=m)
        with self.assertRaises(ValueError):
            self.resolve([], previous=dict(PREVIOUS, primitive_id=1))

    def test_invalid_distance_and_normals(self):
        for value in (0., -1., True, float('nan'), float('inf')):
            with self.assertRaises(ValueError): self.resolve([hit(2, value)])
        for normal in ((0., 0., 0.), (float('nan'), 0., 0.), (True, 0., 0.), (1., 0.)):
            with self.assertRaises(ValueError): self.resolve([hit(2, normal=normal)])


if __name__ == '__main__': unittest.main()

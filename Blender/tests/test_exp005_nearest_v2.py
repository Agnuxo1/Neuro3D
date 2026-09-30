"""CPU contract regressions. No native GPU/runtime certification here."""
import hashlib
import itertools
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).parents[1]/'benchmarks'/'capacity_audit'))
from nearest_hit_v2 import BASE, BASE_SHA, Candidate, select, shader_source
from exp005_peer_ambiguity_audit import plane
from exp005_triangle_oracle import triangle_hit, unit


class NearestV2Tests(unittest.TestCase):
    def test_all_six_real_triangle_permutations_reject_counterexample(self):
        # Independent triangle intersection implementation, not distances fed
        # into the shader. CPU oracle is used solely for specification testing.
        for order in itertools.permutations(range(3)):
            hits = []
            for index in order:
                obj = plane(5 - index*.9e-9, 'mirror')
                vertices = obj['vertices_world_BU']
                for face in obj['faces']:
                    hit = triangle_hit((0, 0, 0), (1, 0, 0), tuple(vertices[i] for i in face), 1e-9)
                    self.assertIsNotNone(hit)
                    hits.append(Candidate(hit[0], index, hit[1]))
            winner, ambiguous = select(hits)
            self.assertTrue(ambiguous)
            self.assertEqual(winner.object_id, 2)

    def test_far_ambiguity_does_not_taint_unique_nearest(self):
        hits = [Candidate(5., 0, (1, 0, 0)), Candidate(5.+.5e-9, 1, (1, 0, 0)),
                Candidate(4., 2, (1, 0, 0))]
        for order in itertools.permutations(hits):
            winner, ambiguous = select(order)
            self.assertEqual(winner.object_id, 2)
            self.assertFalse(ambiguous)

    def test_coplanar_triangles_same_object_and_opposite_winding_are_not_ambiguous(self):
        hits = [Candidate(2., 0, (1, 0, 0)), Candidate(2., 0, (-1, 0, 0))]
        for order in itertools.permutations(hits):
            self.assertFalse(select(order)[1])

    def test_tie_band_is_inclusive_and_relative_to_global_minimum(self):
        hits = [Candidate(2e-9, 0, (1, 0, 0)), Candidate(3e-9, 1, (1, 0, 0))]
        self.assertTrue(select(hits)[1])
        self.assertFalse(select([hits[0], Candidate(3.01e-9, 1, (1, 0, 0))])[1])
        # Non-transitive chain: global minimum only, not a connected-component tie.
        chain = [Candidate(2e-9, 0, (1, 0, 0)), Candidate(2.9e-9, 0, (1, 0, 0)),
                 Candidate(3.8e-9, 1, (1, 0, 0))]
        for order in itertools.permutations(chain):
            self.assertFalse(select(order)[1])

    def test_same_object_nonparallel_edge_is_ambiguous(self):
        self.assertTrue(select([Candidate(2, 0, (1, 0, 0)),
                                Candidate(2, 0, unit((1, 1, 0)))])[1])

    def test_exact_distance_normal_tie_break_is_order_and_winding_independent(self):
        hits = [Candidate(2, 0, unit((1, y, 0))) for y in (0, -4e-5, 4e-5)]
        normals = set()
        for order in itertools.permutations(hits):
            winner, ambiguous = select(order)
            self.assertTrue(ambiguous)
            normals.add(winner.normal)
        self.assertEqual(len(normals), 1)
        reversed_winding = [Candidate(h.distance_BU, h.object_id, tuple(-x for x in h.normal)) for h in hits]
        winner, ambiguous = select(reversed_winding)
        self.assertTrue(ambiguous)
        self.assertEqual(tuple(-x for x in winner.normal), next(iter(normals)))

    def test_miss_and_invalid_candidates_fail_closed(self):
        self.assertEqual(select([]), (None, False))
        bad = [Candidate(float('nan'), 0, (1, 0, 0)), Candidate(float('inf'), 0, (1, 0, 0)),
               Candidate(1e-9, 0, (1, 0, 0)), Candidate(2, True, (1, 0, 0)),
               Candidate(2, -1, (1, 0, 0)), Candidate(2, 0, (2, 0, 0)),
               Candidate(2, 0, (float('nan'), 0, 0))]
        for item in bad:
            with self.assertRaises(ValueError): select([Candidate(1, 0, (1, 0, 0)), item])

    def test_composed_shader_preserves_base_and_non_nearest_optics(self):
        raw = BASE.read_bytes()
        source = shader_source()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), BASE_SHA)
        self.assertEqual(source[source.index('\nvoid main() {'):],
                         raw.decode('utf-8')[raw.decode('utf-8').index('\nvoid main() {'):])
        self.assertEqual(source.count('for(int tri=0;tri<triangle_count;++tri)'), 2)
        self.assertNotIn('t<best-1.0e-9lf', source)
        self.assertIn('t<best || (t==best && earlier_normal)', source)
        self.assertIn('abs(t-best)<=1.0e-9lf', source)
        self.assertEqual(hashlib.sha256(BASE.read_bytes()).hexdigest(), BASE_SHA)


if __name__ == '__main__': unittest.main()

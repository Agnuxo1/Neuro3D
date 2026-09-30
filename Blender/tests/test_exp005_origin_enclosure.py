import copy
import hashlib
import json
from fractions import Fraction
from pathlib import Path
import unittest
from exp005_origin_enclosure_audit import enclosure, audit, REPLAY_SHA
from exp005_departure_replay_audit import load_frozen


class OriginEnclosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.retained = load_frozen('D:/PROJECTS/.cognition/neuro3d/exp005_self_hit_cpu_20260930_0804.json')
        raw = Path('D:/PROJECTS/.cognition/neuro3d/exp005_departure_replay_cpu_20260930_0942.json').read_bytes()
        if hashlib.sha256(raw).hexdigest() != REPLAY_SHA: raise ValueError('frozen replay changed')
        cls.replay = json.loads(raw); cls.report = audit(cls.retained, cls.replay)

    def test_24_signed_offsets_contained_without_forcing_zero(self):
        self.assertEqual(len(self.report['rows']), 24)
        for row in self.report['rows']:
            result = row['enclosure']
            self.assertLessEqual(abs(Fraction(*result['signed_plane_t_BU_exact'])),
                Fraction(*result['projected_plane_t_radius_BU_exact']))
            self.assertNotEqual(result['signed_plane_t_BU_exact'][0], 0)

    def test_exact_plane_control_has_zero_offset_but_nonzero_rounding_box(self):
        record = {'vertices': [[1., -1., -1.], [1., 1., -1.], [1., 1., 1.]],
            'faces': [[0, 1, 2]], 'origin_BU': [0., 0., 0.], 'direction': [1., 0., 0.]}
        result = enclosure(record, 0, [1., 0., 0.], [-1., 0., 0.])
        self.assertEqual(result['signed_plane_t_BU_exact'][0], 0)
        self.assertGreater(Fraction(*result['projected_plane_t_radius_BU_exact']), 0)
        with self.assertRaises(ValueError): enclosure(record, 0, [1., 0., 0.], [0., 1., 0.])
        with self.assertRaises(ValueError): enclosure(record, True, [1., 0., 0.], [-1., 0., 0.])

    def test_changed_query_and_duplicate_coverage_fail_closed(self):
        altered = copy.deepcopy(self.replay); altered['rows'][0]['first_query']['point_BU'][0] += 1.
        with self.assertRaises(ValueError): audit(self.retained, altered)
        altered = copy.deepcopy(self.replay); altered['rows'][0] = copy.deepcopy(altered['rows'][1])
        with self.assertRaises(ValueError): audit(self.retained, altered)

    def test_replay_is_immutable(self):
        original = copy.deepcopy(self.replay); audit(self.retained, self.replay)
        self.assertEqual(self.replay, original)


if __name__ == '__main__': unittest.main()

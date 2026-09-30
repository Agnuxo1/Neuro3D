import copy
import unittest
from exp005_departure_audit import witness, diagnose, audit
from exp005_cutoff_audit import fixture
from exp005_geometric_return_audit import geometric_candidates
from exp005_primitive_return_audit import folded_record


def build(record, **kwargs):
    return witness(record, previous_pid=kwargs.pop('previous_pid', 0),
        expected_geometry_sha256=geometric_candidates(record)['geometry_sha256'], **kwargs)


class DepartureTests(unittest.TestCase):
    def test_seam_zero_only_not_tiny_positive_or_far(self):
        record = fixture(5e-10); cert = build(record); rows = diagnose(record, cert)
        self.assertEqual(cert['exact_zero_coplanar_same_owner_ids'], [0, 1])
        self.assertEqual([rows[i]['diagnostic'] for i in (2, 3)], ['possible_near_origin']*2)
        for i in (2, 3, 4, 5):
            self.assertEqual(rows[i]['diagnostic'], rows[i]['interval_result']['status'])

    def test_changed_geometry_owner_ray_and_tampered_proof_reject(self):
        record = fixture(5e-10); cert = build(record)
        for field, value in (('vertices', 0), ('object_ids', 0), ('origin_BU', 1), ('direction', 0)):
            altered = copy.deepcopy(record)
            if field == 'vertices': altered[field][value][1] -= .25
            elif field == 'object_ids': altered[field][value] = 'other'
            elif field == 'origin_BU': altered[field][value] = .1
            else: altered[field] = [-1., 0., 0.]
            with self.assertRaises(ValueError): diagnose(altered, cert)
        altered = copy.deepcopy(cert); altered['exact_zero_coplanar_same_owner_ids'].append(2)
        with self.assertRaises(ValueError): diagnose(record, altered)

    def test_wrong_prior_offplane_parallel_event_and_missing_owner_reject(self):
        record = fixture(5e-10)
        with self.assertRaises(ValueError): build(record, previous_pid=2)
        with self.assertRaises(ValueError): build(record, previous_pid=True)
        with self.assertRaises(ValueError): build(record, event='source')
        shifted = copy.deepcopy(record); shifted['origin_BU'][0] = 1e-16
        with self.assertRaises(ValueError): build(shifted)
        parallel = copy.deepcopy(record); parallel['direction'] = [0., 1., 0.]
        with self.assertRaises(ValueError): build(parallel)
        del record['object_ids']
        with self.assertRaises(ValueError): build(record)

    def test_other_owner_exact_zero_remains_unresolved(self):
        record = fixture(5e-10); record['object_ids'][1] = 'different'
        cert = build(record); rows = diagnose(record, cert)
        self.assertEqual(cert['exact_zero_coplanar_same_owner_ids'], [0])
        self.assertEqual(rows[1]['diagnostic'], 'possible_near_origin')

    def test_same_owner_folded_other_plane_is_not_exempted(self):
        record = folded_record(); record['origin_BU'] = record['vertices'][0]
        cert = build(record)
        self.assertIn(0, cert['exact_zero_coplanar_same_owner_ids'])
        self.assertFalse(set(cert['exact_zero_coplanar_same_owner_ids']) & {2, 3})

    def test_positive_plane_same_owner_is_not_exempted(self):
        record = fixture(5e-10); record['object_ids'] = ['same']*6
        self.assertEqual(build(record)['exact_zero_coplanar_same_owner_ids'], [0, 1])

    def test_bound_and_input_immutability(self):
        record = fixture(5e-10); original = copy.deepcopy(record)
        cert = build(record); diagnose(record, cert)
        self.assertEqual(record, original)
        record['faces'] *= 2; record['object_ids'] *= 2
        with self.assertRaises(ValueError): build(record)

    def test_retained_cases_do_not_claim_complete_gate_pass(self):
        result = audit()
        self.assertEqual(len(result['gap_cases']), 4)
        self.assertEqual(len(result['folded_saved_rays']), 2)
        self.assertTrue(all(len(row['diagnostics']) == 6 for row in result['gap_cases']))


if __name__ == '__main__': unittest.main()

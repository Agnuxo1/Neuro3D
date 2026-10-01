"""New completeness-witness tests, not a replay of frozen geometry suites."""
from copy import deepcopy
from fractions import Fraction as F
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'benchmarks'/'capacity_audit'))
import axial_tree_completeness_cpu_v1 as m


class TreeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.output = m.audit(model=m.MODEL)
        _, cls.cases, cls.closure = m.load_retained()

    def witness(self, name='positive'):
        return deepcopy(self.output['cases'][name]['certificate'])

    def verify(self, w, name='positive'):
        return m.verify_witness(self.cases[name], w, model=m.MODEL)

    def test_complete_bound_profile_and_unchanged_rejections(self):
        self.assertEqual(self.output['counts'], {
            'cases': 13, 'source_ids': 14, 'certified_cases': 8, 'records': 27,
            'transitions': 18, 'primitive_checks_per_verification': 72})
        for name, c in self.output['cases'].items():
            self.assertEqual(c['retained_closure_gates_UNCHANGED'], self.closure[name]['stage_gates_retained'])
            self.assertEqual(c['geometric_tree_complete_restricted_CPU_only'],
                             self.cases[name]['accepted_geometry_words_CPU_only'])
            self.assertFalse(c['accepted_full_field_pipeline'])
        for n in ('nonexact_geometry_phase_FAIL', 'lambda_transport_FAIL'):
            c = self.output['cases'][n]
            self.assertTrue(c['geometric_tree_complete_restricted_CPU_only'])
            self.assertEqual(c['retained_phase_gates_UNCHANGED'], [False])
        self.assertFalse(self.output['cases']['two_sources']['retained_closure_gates_UNCHANGED'][-1])

    def test_both_signs_and_shared_owner_departure(self):
        for name in ('positive', 'negative', 'thin_resolved', 'declared_radius_PASS', 'two_sources'):
            for t in self.witness(name)['trees']:
                root, mirror, det = t
                self.assertEqual(mirror['direction_sign'], -root['direction_sign'])
                self.assertEqual(det['children'], [])
                self.assertEqual([p['primitive_id'] for p in root['next_primitive_partition']], [0,1,2,3])
                d = mirror['next_primitive_partition'][1]
                self.assertEqual(d['relation'], 'same_owner_departure')
                self.assertEqual(d['distance_BU'], [[0,1],[0,1]])
                self.assertEqual(mirror['origin_context'], 'SAME-owner-0-X-variable')

    def test_missing_duplicate_extra_nodes_and_terminal_successor_reject(self):
        for alter in (
                lambda w: w['trees'][0].pop(),
                lambda w: w['trees'][0].append(deepcopy(w['trees'][0][0])),
                lambda w: w['trees'][0][2]['children'].append('fake'),
                lambda w: w['trees'][0][1].update(parent=None),
                lambda w: w['trees'][0][1].update(id='s:root')):
            w = self.witness(); alter(w)
            with self.assertRaises(ValueError): self.verify(w)

    def test_missing_duplicate_partition_and_lied_relation_reject(self):
        for alter in (
                lambda p: p.pop(),
                lambda p: p.append(deepcopy(p[0])),
                lambda p: p[3].update(relation='projected_miss'),
                lambda p: p[1].update(distance_BU=[[0,1],[0,1]]),
                lambda p: p[0].update(primitive_id=True),
                lambda p: p.reverse()):
            w = self.witness(); alter(w['trees'][0][0]['next_primitive_partition'])
            with self.assertRaises(ValueError): self.verify(w)

    def test_foreign_source_binding_order_context_and_role_reject(self):
        for alter in (
                lambda w: w.update(scene_binding_sha256='0'*64),
                lambda w: w.update(word_ABI_sha256='0'*64),
                lambda w: w.update(object_order=['D','M']),
                lambda w: w['trees'][0][1].update(source_id='foreign'),
                lambda w: w['trees'][0][1].update(origin_context='independent mirror interval'),
                lambda w: w['trees'][0][1].update(event='transmit'),
                lambda w: w['trees'][0][1].update(direction_sign=1),
                lambda w: w.update(primitive_count=True)):
            w = self.witness(); alter(w)
            with self.assertRaises(ValueError): self.verify(w)
        w = self.witness('two_sources'); w['trees'].pop()
        with self.assertRaises(ValueError): self.verify(w, 'two_sources')

    def test_retained_coverage_context_corruption_is_not_trusted(self):
        for key, value in (('behind', []), ('primitive_id', 3),
                           ('segment_interval_scaled', [0,0])):
            g = deepcopy(self.cases['positive']); g['sources'][0]['segments'][0][key] = value
            with self.assertRaises(ValueError): m.make_witness(g, model=m.MODEL)
        g = deepcopy(self.cases['positive']); g['sources'][0]['projected_misses'] = [0]
        with self.assertRaises(ValueError): m.make_witness(g, model=m.MODEL)
        g = deepcopy(self.cases['positive']); g['sources'][0]['segments'][1]['same_owner_departures_skipped'] = []
        with self.assertRaises(ValueError): m.make_witness(g, model=m.MODEL)

    def test_rejected_contacts_boundary_not_revived(self):
        for name in ('thin_collapsed_FAIL','source_contact_FAIL','otherowner_contact_FAIL',
                     'boundary_FAIL','declared_contact_FAIL'):
            with self.assertRaises(ValueError): m.make_witness(self.cases[name], model=m.MODEL)
        # A lied PASS plus borrowed transition is still rejected by the new proof.
        g = deepcopy(self.cases['boundary_FAIL'])
        row = deepcopy(self.cases['positive']['sources'][0])
        g['sources'] = [row]; g['accepted_geometry_words_CPU_only'] = True
        with self.assertRaisesRegex(ValueError, 'boundary'): m.make_witness(g, model=m.MODEL)

    def test_retained_integer_context_bool_alias_rejected(self):
        for alter in (
                lambda r: r.update(projected_misses=[False,2]),
                lambda r: r.update(mirror_owner=False),
                lambda r: r['segments'][1].update(same_owner_departures_skipped=[True]),
                lambda r: r['segments'][0].update(segment_interval_scaled=[True,True])):
            g = deepcopy(self.cases['positive']); alter(g['sources'][0])
            with self.assertRaises(ValueError): m.make_witness(g, model=m.MODEL)

    def test_geometry_profile_and_ABI_fail_closed(self):
        for alter in (
                lambda a: a['triangles'].pop(),
                lambda a: a.update(object_ids=['D','M']),
                lambda a: a.update(kinds=['bs','det']),
                lambda a: a['triangles'][0].update(owner=True),
                lambda a: a['triangles'][0].update(X_radius_scaled=1),
                lambda a: a['sources'][0]['direction_uint32_hilo'][0].__setitem__(0, True)):
            g = deepcopy(self.cases['positive']); alter(g['word_ABI'])
            g['word_ABI_sha256'] = m.digest(g['word_ABI'])
            with self.assertRaises(ValueError): m.make_witness(g, model=m.MODEL)
        with self.assertRaises(ValueError): m.make_witness(self.cases['positive'], model='general-BS-history')

    def test_interval_contacts_overlap_and_strict_later_new_synthetic_controls(self):
        ts = [(0, [[F(0),F(0),F(0)], [F(0),F(1),F(0)], [F(0),F(0),F(1)]]),
              (1, [[F(0),F(0),F(0)], [F(0),F(1),F(0)], [F(0),F(0),F(1)]])]
        yz = [F(1,4),F(1,4)]
        p = m._transition(ts, {0:(F(1),F(1)),1:(F(2),F(2))}, yz, (F(0),F(0)),1,None,0)
        self.assertEqual(p[1]['shared_origin_clearance_BU'], [1,1])
        for planes in ({0:(F(0),F(1)),1:(F(2),F(2))},
                       {0:(F(1),F(2)),1:(F(2),F(3))},
                       {0:(F(1),F(3)),1:(F(2),F(4))}):
            with self.assertRaises(ValueError): m._transition(ts, planes, yz, (F(0),F(0)),1,None,0)

    def test_no_native_runtime_promotion_or_old_producers(self):
        for flag in ('geometry_signed512_graph_replayed','retained_writers_executed',
                     'GPU_executed','Bpy_executed','RT_executed','execution_authenticated',
                     'physical_coherence_verified','accepted_full_field_pipeline','native_promotion_allowed'):
            self.assertIs(self.output[flag], False)
        names = ('axial_geometry_words_cpu_v1','history_completeness_cpu_v1','bpy','exp005_blender_gpu')
        self.assertFalse(any(n in sys.modules for n in names))


if __name__ == '__main__':
    result = unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromTestCase(TreeTests))
    if result.wasSuccessful():
        print(json.dumps(TreeTests.output,sort_keys=True,separators=(',', ':'),allow_nan=False))
    raise SystemExit(not result.wasSuccessful())

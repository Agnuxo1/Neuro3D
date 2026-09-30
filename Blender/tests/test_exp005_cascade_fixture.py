"""Small connected-scene CPU gate; not actual Blender/RT inference."""
import cmath
import copy
import math
import unittest

from exp005_cascade_fixture import cascade_fixture, closed_form_columns
from exp005_modal_audit import modal_audit
from exp005_triangle_oracle import trace_scene


class CascadeFixtureTests(unittest.TestCase):
    def test_connected_fixture_and_all_complex_ports_against_closed_form(self):
        for phases in [(0.,0.),(.2,.37),(.9,-.4)]:
            scene = cascade_fixture(*phases)
            audit = modal_audit(scene)
            self.assertEqual(len(scene['objects']),15)
            self.assertEqual(audit['ports'],['a.Y','b.X','b.Y'])
            self.assertEqual(audit['traces'],9)  # three bases, six direct pairs
            for actual, expected in zip(audit['columns'],closed_form_columns(*phases)):
                self.assertLess(max(abs(a-b) for a,b in zip(actual,expected)),1e-12)
            self.assertLess(audit['gram_identity_error'],1e-12)
            self.assertLess(audit['worst_pair_complex_error'],1e-12)
            self.assertLess(audit['worst_pair_conditional_power_error'],1e-12)
            self.assertFalse(audit['geometry_gate_passed'])

    def test_paths_cross_cells_and_no_intermediate_detector(self):
        result = trace_scene(cascade_fixture())
        downstream = [p for p in result['paths'] if p['terminal'].startswith('b.')]
        self.assertTrue(downstream)
        for path in downstream:
            ids = [hit['object_id'] for hit in path['hits']]
            self.assertIn('a.bs1',ids)
            self.assertIn('a.bs2',ids)
            self.assertIn('b.bs1',ids)
            self.assertNotIn('a.X',ids)
        self.assertLess(result['rays'],4096)

    def test_both_cell_phase_changes_are_causal(self):
        base = trace_scene(cascade_fixture())['powers']
        for phases in [(.6,.37),(.2,.8)]:
            changed = trace_scene(cascade_fixture(*phases))['powers']
            self.assertGreater(max(abs(changed[p]-base[p]) for p in base),.001)

    def test_roof_displacement_matches_two_d_phase_before_runtime(self):
        scene = cascade_fixture()
        for name in ('a.r1','a.r2'):
            record=scene['objects'][name]
            record['vertices_world_BU']=[(x+.0125,y,z) for x,y,z in record['vertices_world_BU']]
        audit=modal_audit(scene)
        reference=closed_form_columns(.2+math.pi/2,.37)
        self.assertLess(max(abs(a-b) for col,ref in zip(audit['columns'],reference)
                            for a,b in zip(col,ref)),1e-12)

    def test_global_input_phase_preserves_power_but_rotates_all_fields(self):
        scene = cascade_fixture(); base = trace_scene(scene)
        factor = cmath.exp(.4j)
        scene['sources'][0]['field_reim']=[factor.real,factor.imag]
        changed = trace_scene(scene)
        for port in base['fields']:
            self.assertLess(abs(changed['fields'][port]-factor*base['fields'][port]),1e-12)
            self.assertLess(abs(changed['powers'][port]-base['powers'][port]),1e-12)

    def test_sham_colour_is_not_an_optical_coefficient(self):
        scene = cascade_fixture(); changed = copy.deepcopy(scene)
        for record in changed['objects'].values(): record['display_colour']=[.2,.7,.1]
        self.assertEqual(trace_scene(scene)['fields'],trace_scene(changed)['fields'])

    def test_missing_reflector_fails_closed_and_fixture_is_not_mutated(self):
        scene = cascade_fixture(); before = copy.deepcopy(scene)
        modal_audit(scene); self.assertEqual(scene,before)
        del scene['objects']['b.r1']
        with self.assertRaises(ValueError): trace_scene(scene)

    def test_removed_splitter_can_conserve_energy_but_changes_the_network(self):
        scene = cascade_fixture(); del scene['objects']['b.bs1']
        audit = modal_audit(scene)
        self.assertLess(audit['gram_identity_error'],1e-12)
        expected = closed_form_columns()
        error = max(abs(a-b) for column, reference in zip(audit['columns'],expected)
                    for a,b in zip(column,reference))
        self.assertGreater(error,.1)


if __name__=='__main__': unittest.main()

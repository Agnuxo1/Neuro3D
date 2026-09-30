"""Raw source/property ABI tests, not GPU inference evidence."""
import copy
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).parents[1]/'benchmarks'/'capacity_audit'))
from frontier_inputs import pack_frontier
from exp005_escape_fixture import escape_fixture


class FrontierInputTests(unittest.TestCase):
    def test_raw_scene_payload_has_only_source_rays(self):
        scene=escape_fixture(); batch=pack_frontier(scene)
        self.assertEqual(batch.geometry.query_count,3)
        self.assertEqual(batch.geometry.triangle_count,30)
        self.assertEqual(len(batch.sources),24)
        self.assertEqual(len(batch.optics),12*len(scene['objects']))
        self.assertEqual(batch.source_ids,tuple(s['id'] for s in scene['sources']))
        self.assertEqual(batch.sources[:8],(*scene['sources'][0]['position_BU'],1.,*scene['sources'][0]['direction'],0.))
        self.assertEqual(set(batch.ports),{'a.Y','b.Y','b.escape'})

    def test_mutations_are_raw_not_cpu_computed_coefficients(self):
        scene=escape_fixture(); scene['schema']='exp005-readback-v2'
        for obj in scene['objects'].values():
            if obj['kind']=='bs': obj['power_transmittance']=.2
        scene['objects']['a.r1']['phase_rad']=.13
        scene['sources'][1]['field_reim']=[.3,-.7]
        batch=pack_frontier(scene); index=batch.geometry.object_ids.index('a.r1')
        self.assertEqual(batch.optics[12*index+2],.13)
        index=batch.geometry.object_ids.index('a.bs1')
        self.assertEqual(batch.optics[12*index+1],.2)  # Not sqrt(T), no CPU optics.
        self.assertEqual((batch.sources[11],batch.sources[15]),(.3,-.7))

    def test_no_defaults_for_mandatory_v2_or_mirror_properties(self):
        scene=escape_fixture(); scene['schema']='exp005-readback-v2'
        with self.assertRaises(KeyError): pack_frontier(scene)
        scene=escape_fixture(); del scene['objects']['a.r1']['phase_rad']
        with self.assertRaises(KeyError): pack_frontier(scene)
        scene=escape_fixture(); scene['objects']['a.bs1']['power_transmittance']=.5
        with self.assertRaises(ValueError): pack_frontier(scene)

    def test_invalid_source_and_terminal_fail_closed(self):
        for case in ('id','bool','missing','axis','T','lambda','sources'):
            scene=escape_fixture()
            if case=='id': scene['sources'][1]['id']=scene['sources'][0]['id']
            if case=='bool': scene['sources'][0]['field_reim']=[True,0]
            if case=='missing': del scene['sources'][0]['field_reim']
            if case=='axis': scene['objects']['a.Y']['mode_direction']=[0,0,0]
            if case=='lambda': scene['lambda_BU']=0
            if case=='sources': scene['sources']*=2
            if case=='T':
                scene['schema']='exp005-readback-v2'
                for obj in scene['objects'].values():
                    if obj['kind']=='bs': obj['power_transmittance']=1.01
            with self.subTest(case=case),self.assertRaises((ValueError,KeyError)): pack_frontier(scene)

    def test_pilot_geometry_bound(self):
        scene=escape_fixture()
        for i in range(18): scene['objects'][f'clone{i}']=copy.deepcopy(scene['objects']['a.r1'])
        with self.assertRaisesRegex(ValueError,'triangle bound'): pack_frontier(scene)


if __name__=='__main__': unittest.main()

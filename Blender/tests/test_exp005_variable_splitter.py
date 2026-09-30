"""CPU-only v2 property contract and independently traced energy/fields."""
import copy
import math
import unittest

from exp005_cascade_runtime import probes
from exp005_escape_fixture import escape_fixture
from exp005_splitter_fixture import splitter_fixture,CASES
from exp005_triangle_oracle import trace_scene
from exp005_scene_properties import decode_scene,sum_declared_channels
from exp005_gpu_pack import pack_paths
from exp005_blender_gpu import dispatch


class VariableSplitterTests(unittest.TestCase):
    def test_all_seven_treatments_and_nine_inputs_conserve_energy(self):
        for case in CASES:
            for label,amps in probes():
                scene=splitter_fixture(case)
                for s,a in zip(scene['sources'],amps): s['field_reim']=[a.real,a.imag]
                oracle=trace_scene(scene)
                inputs={s['id']:complex(*s['field_reim']) for s in scene['sources']}
                paths=[dict(p,initial_field=inputs[p['source_id']]) for p in oracle['paths']]
                actual=sum_declared_channels(decode_scene(scene),paths)
                with self.subTest(case=case,probe=label):
                    self.assertLess(abs(sum(actual['powers'].values())-sum(abs(a)**2 for a in amps)),1e-11)
                    self.assertLess(max(abs(actual['fields'][p]-oracle['fields'][p]) for p in actual['fields']),1e-11)

    def test_half_split_matches_frozen_v1_contract(self):
        for label,amps in probes():
            a,b=splitter_fixture(),escape_fixture()
            for scene in (a,b):
                for s,x in zip(scene['sources'],amps): s['field_reim']=[x.real,x.imag]
            aa,bb=trace_scene(a),trace_scene(b)
            self.assertLess(max(abs(aa['fields'][p]-bb['fields'][p]) for p in aa['fields']),1e-11)

    def test_raw_property_not_cpu_coefficient_is_packed(self):
        scene=splitter_fixture('T02'); oracle=trace_scene(scene)
        paths=[dict(p,initial_field=1+0j) for p in oracle['paths']]
        packed=pack_paths(scene,paths)
        values=[packed.hits[i+3] for i in range(0,len(packed.hits),4) if packed.hits[i+2] in (4,5)]
        self.assertIn(.2,values); self.assertIn(.5,values)
        self.assertNotIn(math.sqrt(.2),values)
        with self.assertRaisesRegex(ValueError,'unsupported hit code'):
            dispatch(None,None,packed)  # Rejection before any GPU API is touched.

    def test_missing_invalid_or_wrong_version_property_rejected(self):
        for value in (None,-.01,1.01,True,float('nan'),'0.2'):
            scene=splitter_fixture()
            if value is None: del scene['objects']['b.bs2']['power_transmittance']
            else: scene['objects']['b.bs2']['power_transmittance']=value
            for decoder in (decode_scene,trace_scene):
                with self.subTest(value=value,decoder=decoder.__name__),self.assertRaises((KeyError,ValueError)):
                    decoder(scene)
        scene=escape_fixture(); scene['objects']['b.bs2']['power_transmittance']=.2
        for decoder in (decode_scene,trace_scene):
            with self.assertRaises(ValueError): decoder(scene)

    def test_splitter_and_phase_causal_but_sham_is_equal(self):
        a,b,c=[trace_scene(splitter_fixture(case))['powers'] for case in ('T02','T05','phase')]
        self.assertGreater(max(abs(a[p]-b[p]) for p in a),1e-3)
        self.assertGreater(max(abs(a[p]-c[p]) for p in a),1e-3)
        self.assertEqual(trace_scene(splitter_fixture('T05')),trace_scene(splitter_fixture('sham')))

    def test_complementary_ratios_can_hide_field_changes_in_intensity(self):
        a,b=[trace_scene(splitter_fixture(case)) for case in ('T02','T08')]
        self.assertLess(max(abs(a['powers'][p]-b['powers'][p]) for p in a['powers']),1e-11)
        self.assertGreater(max(abs(a['fields'][p]-b['fields'][p]) for p in a['fields']),1e-3)

    def test_readback_requires_v2_property_and_matches_evaluated_object(self):
        from test_exp005_scene_readback import Scene,ReadbackTests
        from exp005_scene_readback import export_snapshot
        scene=Scene(); scene['optical_contract']='exp005-readback-v2'
        scene.objects['mirror']['kind']='bs'; scene.objects['mirror']['power_transmittance']=.2
        graph=ReadbackTests().graph(scene)
        result=export_snapshot(scene,depsgraph=graph)
        self.assertEqual(result['objects']['mirror']['power_transmittance'],.2)
        graph.objects[0]['power_transmittance']=.8
        with self.assertRaisesRegex(ValueError,'transmittance mismatch'):
            export_snapshot(scene,depsgraph=graph)
        del scene.objects['mirror']['power_transmittance']
        with self.assertRaises(KeyError): export_snapshot(scene)


if __name__=='__main__': unittest.main()

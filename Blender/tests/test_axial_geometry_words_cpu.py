"""New scene ABI fixtures only; no retained geometry sweeps or writers."""
from copy import deepcopy
from fractions import Fraction as F
import json
import math
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'Blender/tests'))
sys.path.insert(0,str(ROOT/'Blender/benchmarks/capacity_audit'))
import axial_geometry_words_cpu_v1 as new

def fixture(mirror=.25,terminal=-.125,source=0.,sign=1):
    objects={}
    for name,x,kind in [('M',mirror,'mirror'),('D',terminal,'det')]:
        objects[name]={'kind':kind,'vertices_world_BU':[[x,.875,-.125],[x,1.125,-.125],[x,1.125,.125],[x,.875,.125]],
                       'faces':[[0,1,2],[0,2,3]]}
        if kind=='mirror':objects[name]['phase_rad']=0.
        else:objects[name].update(mode_origin_BU=[x,1.,0.],mode_direction=[-float(sign),0.,0.])
    return {'schema':'exp005-readback-v2','lambda_BU':.125,'undeclared_meshes':[],'objects':objects,
            'sources':[{'id':'s','position_BU':[source,1.,.03125],'direction':[float(sign),0.,0.],'field_reim':[.1,0.]}]}

class GeometryWordTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.evidence={'cases':{},'rejections':{},'CPU_only':True}
    def keep(self,name,s,**opts):
        opts={'geometry_model':new.MODEL,'phase_budget_rad':F(1,10**12),**opts};before=deepcopy(s)
        with patch('axial_reflection_margin_cpu_v1.certify_axial_reflection',side_effect=AssertionError('no old geometry certificate')),patch('axial_root_margin_cpu_v1.certify_axial_roots',side_effect=AssertionError('no roots replay')),patch('exp005_precision_transport_audit.transported',side_effect=AssertionError('no CPU64 ABI decode replay')):
            r=new.audit_scene_geometry_words(s,**opts)
        self.assertEqual(s,before);self.evidence['cases'][name]=r
        return r

    def test_signed_exact_self_departure_from_plane(self):
        for n,s in [('positive',fixture()),('negative',fixture(-.25,.125,sign=-1))]:
            r=self.keep(n,s,phase_budget_rad=0);p=r['sources'][0]
            self.assertTrue(r['accepted_phase_budget_CPU_only'])
            self.assertEqual(p['original_length_BU_rational'],[5,8])
            self.assertEqual(p['length_interval_BU_rational'],[[5,8],[5,8]])
            self.assertEqual([s['primitive_id'] for s in p['segments']],[1,3])
            self.assertEqual(p['segments'][1]['same_owner_departures_skipped'],[1])

    def test_original_gap_resolved_vs_rounded_contact(self):
        r=self.keep('thin_resolved',fixture(.1+2**-30,source=.1))
        self.assertTrue(r['accepted_geometry_words_CPU_only'])
        self.assertGreater(r['sources'][0]['segments'][0]['segment_interval_scaled'][0],0)
        r=self.keep('thin_collapsed_FAIL',fixture(math.nextafter(.1,math.inf),source=.1))
        self.assertFalse(r['accepted_geometry_words_CPU_only'])
        self.assertIn('source zero contact',r['sources'][0]['reason'])

    def test_source_contact_otherowner_and_boundary_reject(self):
        for name,s in [('source_contact_FAIL',fixture(terminal=0.)),('otherowner_contact_FAIL',fixture(terminal=.25)),('boundary_FAIL',fixture())]:
            if name=='boundary_FAIL':s['sources'][0]['position_BU'][2]=0.
            r=self.keep(name,s);self.assertFalse(r['accepted_geometry_words_CPU_only'])
            self.assertFalse(r['accepted_phase_budget_CPU_only'])

    def test_geometry_phase_budget_not_free(self):
        loose=self.keep('nonexact_geometry_phase_PASS',fixture(mirror=.1))
        tight=self.keep('nonexact_geometry_phase_FAIL',fixture(mirror=.1),phase_budget_rad=0)
        self.assertTrue(loose['accepted_phase_budget_CPU_only'])
        self.assertTrue(tight['accepted_geometry_words_CPU_only'])
        self.assertFalse(tight['accepted_phase_budget_CPU_only'])
        self.assertGreater(F(*tight['sources'][0]['phase_error_bound_rad']),0)

    def test_declared_radius_and_correlated_length(self):
        r=self.keep('declared_radius_PASS',fixture(),extra_radius_BU=F(1,128),phase_budget_rad=2)
        p=r['sources'][0]
        self.assertTrue(r['accepted_phase_budget_CPU_only'])
        self.assertEqual(p['length_interval_BU_rational'],[[19,32],[21,32]])
        self.assertEqual(p['phase_error_bound_rad'],[2,1])
        r=self.keep('declared_contact_FAIL',fixture(),extra_radius_BU=F(1,16),phase_budget_rad=8)
        self.assertFalse(r['accepted_geometry_words_CPU_only'])

    def test_wavelength_and_sources_separate(self):
        s=fixture();s['lambda_BU']=.1
        r=self.keep('lambda_transport_FAIL',s,phase_budget_rad=0)
        self.assertTrue(r['accepted_geometry_words_CPU_only']);self.assertFalse(r['accepted_phase_budget_CPU_only'])
        s=fixture();other=deepcopy(s['sources'][0]);other['id']='other';other['position_BU'][0]=-.0625;s['sources'].append(other)
        r=self.keep('two_sources',s,phase_budget_rad=0)
        self.assertTrue(r['accepted_phase_budget_CPU_only'])
        self.assertEqual([p['original_length_BU_rational'] for p in r['sources']],[[5,8],[11,16]])
        self.assertNotEqual(r['sources'][0]['phase_reference_id'],r['sources'][1]['phase_reference_id'])

    def test_word_ABI_actual_scene_binds_ids_not_supplied_roots(self):
        r=self.evidence['cases'].get('positive') or self.keep('binding_control',fixture())
        bundle=r['word_ABI']
        self.assertEqual(bundle['source_order'],['s'])
        self.assertEqual(bundle['object_ids'],['M','D'])
        self.assertNotIn('hits',bundle);self.assertNotIn('length',bundle)
        for flag in ('GPU_executed','ALU_executed','native_geometry_implemented','execution_authenticated','accepted_full_field_pipeline','field_values_computed','native_promotion_allowed'):
            self.assertFalse(r[flag])
        self.assertIn('HOST',r['scope'])
        c=deepcopy(bundle);c['source_order']=['different']
        with self.assertRaises(ValueError):new.geometry_words(c,geometry_model=new.MODEL)

    def test_domains_overflow_unshared_planes_and_optin(self):
        for bad in (True,-1,float('inf'),float('nan')):
            with self.assertRaises(ValueError):new.audit_scene_geometry_words(fixture(),geometry_model=new.MODEL,phase_budget_rad=bad)
            with self.assertRaises(ValueError):new.encode_scene(fixture(),bad)
        self.evidence['rejections']['HOST_budget_domain']='bool/negative/Inf/NaN budgets reject; int/Fraction remain exact, no changed threshold'
        for name,change in [('unshared',lambda s:s['objects']['M']['vertices_world_BU'][0].__setitem__(0,.3)),('mirrorphase',lambda s:s['objects']['M'].__setitem__('phase_rad',.1)),('YZloss',lambda s:s['sources'][0]['position_BU'].__setitem__(1,.1))]:
            s=fixture();change(s)
            with self.assertRaises(ValueError):new.audit_scene_geometry_words(s,geometry_model=new.MODEL,phase_budget_rad=0)
            self.evidence['rejections'][name]='HOST restricted profile rejected; no dispatch'
        bundle,_,_=new.encode_scene(fixture(),0)
        for word in (True,1,0x7f800000,0x7fc00000):
            c=deepcopy(bundle);c['triangles'][0]['vertices_uint32_hilo'][0][0][0]=word
            with self.assertRaises(ValueError):new.geometry_words(c,geometry_model=new.MODEL)
        with self.assertRaises(ValueError):new.checked(1<<511)
        with self.assertRaises(ValueError):new.word512(True)
        with self.assertRaises(ValueError):new.audit_scene_geometry_words(fixture(),geometry_model='GPU',phase_budget_rad=0)
        with patch.object(new,'SHA','0'*64):
            with self.assertRaisesRegex(ValueError,'SHA'):new.pins()
        self.evidence['rejections']['normalzero_domain']='bool/subnormal/NaN/Inf/signed512 overflow reject; no FTZ/fallback'

if __name__=='__main__':
    r=unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromTestCase(GeometryWordTests))
    if hasattr(GeometryWordTests,'evidence'):print(json.dumps(GeometryWordTests.evidence,sort_keys=True,allow_nan=False))
    sys.exit(0 if r.wasSuccessful() else 1)

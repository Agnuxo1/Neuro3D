"""NEW exact one-bounce fixtures; no old sweep or producer execution."""
from copy import deepcopy
from fractions import Fraction as F
from itertools import product
import hashlib
import json
import math
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'Blender/tests'))
sys.path.insert(0,str(ROOT/'Blender/benchmarks/capacity_audit'))
from axial_reflection_margin_cpu_v1 import certify_axial_reflection, two_events, select_step
from history_lineage_cpu_v2 import scene_binding, triangles
from test_axial_root_margin_cpu import interior_scene, PINS as ROOT_PINS

PINS=dict(ROOT_PINS,**{
    'Blender/benchmarks/capacity_audit/axial_root_margin_cpu_v1.py':'edc2c9be9eb29ff56bba403ebd0639d1773b69bbd789db63c0322288aeb327b6',
    'Blender/tests/test_axial_root_margin_cpu.py':'40c86492630eade90fe04bb8c0ad6272496cb4553ffdc6eea0fe2b8c057c32d5',
    'coordinacion/respuestas/AXIAL-ROOT-MARGIN-001-CODEX.json':'9d0635ffc55fa45106674cb3287ef5981ee964dee6f455159e58e8db8377fe3b'})


def reflected_scene(mirror=.25, terminal=-.125, sign=1, mirror_phase=0.):
    snapshot=interior_scene(0.,[('M',mirror),('D',terminal)])
    snapshot['objects']['M']['kind']='mirror'
    snapshot['objects']['M']['phase_rad']=mirror_phase
    snapshot['sources'][0]['direction']=[float(sign),0.,0.]
    return snapshot


class ReflectionMarginTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for path,h in PINS.items():
            if hashlib.sha256((ROOT/path).read_bytes()).hexdigest()!=h:
                raise ValueError('changed frozen foundation: '+path)
        cls.evidence={'pins_verified':PINS,'new_cases':{},'GPU_executed':False,'old_sweeps_rerun':False}

    def keep(self,name,result):
        self.evidence['new_cases'][name]=result
        return result['path_certificates'][0]

    def test_exact_reflection_and_same_owner_zero_departure(self):
        for name,snapshot in (('positive',reflected_scene()),('negative',reflected_scene(-.25,.125,-1))):
            original=deepcopy(snapshot)
            result=certify_axial_reflection(snapshot,phase_budget_rad=0)
            row=self.keep(name+'_exact_PASS',result)
            self.assertEqual(snapshot,original)
            self.assertTrue(result['accepted_CPU_one_bounce_phase_budget'])
            self.assertEqual(row['original_length_BU'],[5,8])
            self.assertEqual(row['length_interval_BU'],[[5,8],[5,8]])
            self.assertEqual(row['segments'][1]['identical_plane_departures_skipped'],[1])
            self.assertEqual([r['primitive_id'] for r in row['segments']],[1,3])
            self.assertFalse(result['native_promotion_allowed'])

    def test_mirror_position_double_charge_and_optical_phase_charge(self):
        result=certify_axial_reflection(reflected_scene(.1,-.25,mirror_phase=.1),phase_budget_rad=F(1,10**12))
        row=self.keep('geometry_and_mirror_phase_PASS',result)
        self.assertTrue(result['accepted_CPU_one_bounce_phase_budget'])
        self.assertEqual(row['geometric_phase_error_bound_rad'],[1,2**48])
        self.assertEqual(row['mirror_phase_transport_error_rad'],[1,2**55])
        self.assertEqual(F(*row['phase_error_bound_rad']),F(1,2**48)+F(1,2**55))
        tight=certify_axial_reflection(reflected_scene(.1,-.25,mirror_phase=.1),phase_budget_rad=0)
        self.keep('tight_phase_FAIL',tight)
        self.assertTrue(tight['accepted_CPU_one_bounce_topology'])
        self.assertFalse(tight['accepted_CPU_one_bounce_phase_budget'])

    def test_independent_source_mirror_terminal_box_corners(self):
        snapshot=reflected_scene();radius=F(1,128)
        result=certify_axial_reflection(snapshot,phase_budget_rad=2,extra_axial_radius_BU=radius)
        row=self.keep('eight_correlated_corners_PASS',result)
        self.assertTrue(result['accepted_CPU_one_bounce_phase_budget'])
        self.assertEqual(row['length_interval_BU'],[[19,32],[21,32]])
        self.assertEqual(row['phase_error_bound_rad'],[2,1])
        _,packed=scene_binding(snapshot);base=triangles(packed)
        for sx,mx,dx in product((-radius,radius),repeat=3):
            geom=[(owner,tuple((p[0]+(mx if owner==0 else dx),p[1],p[2]) for p in tri)) for owner,tri in base]
            p1,_,p2,_,length,_=two_events((sx,F(1),F(1,32)),(F(1),F(0),F(0)),geom)
            self.assertEqual((p1,p2),(1,3))
            self.assertLessEqual(F(19,32),length);self.assertLessEqual(length,F(21,32))
            self.assertLessEqual(8*abs(length/F(1,8)-5),2)

    def test_original_source_contact_not_given_departure_exemption(self):
        result=certify_axial_reflection(reflected_scene(terminal=0.),phase_budget_rad=0)
        row=self.keep('source_contact_FAIL',result)
        self.assertFalse(result['accepted_CPU_one_bounce_topology'])
        self.assertIn('source contact',row['reason'])

    def test_other_owner_contact_not_given_self_exemption(self):
        planes={0:(F(1),F(1),F(1),F(1)),1:(F(1),F(1),F(1),F(1))}
        with self.assertRaisesRegex(ValueError,'another owner'):
            select_step((F(1),F(1)),-1,planes,[(0,0),(1,1)],1,departure_owner=0)

    def test_radius_contact_and_thin_gap_collapse_fail(self):
        result=certify_axial_reflection(reflected_scene(),phase_budget_rad=8,extra_axial_radius_BU=F(1,16))
        row=self.keep('box_source_contact_FAIL',result)
        self.assertFalse(result['accepted_CPU_one_bounce_topology'])
        self.assertIn('source clearance',row['reason'])
        snapshot=reflected_scene(mirror=math.nextafter(.1,math.inf),terminal=-.125)
        snapshot['sources'][0]['position_BU'][0]=.1
        result=certify_axial_reflection(snapshot,phase_budget_rad=1)
        row=self.keep('thin_mirror_source_gap_FAIL',result)
        self.assertFalse(result['accepted_CPU_one_bounce_topology'])
        self.assertIn('source contact',row['reason'])

    def test_shared_owner_plane_and_single_branch_are_required(self):
        snapshot=reflected_scene()
        # Two parallel triangles of one owner at DIFFERENT X: reject shared-variable claim.
        obj=snapshot['objects']['M'];original=deepcopy(obj['vertices_world_BU'])
        obj['vertices_world_BU']=original[:3]+[[v[0]+.03125,v[1],v[2]] for v in (original[0],original[2],original[3])]
        obj['faces']=[[0,1,2],[3,4,5]]
        result=certify_axial_reflection(snapshot,phase_budget_rad=0)
        row=self.keep('unshared_owner_planes_FAIL',result)
        self.assertIn('shared X plane',row['reason'])
        snapshot=reflected_scene();snapshot['objects']['M']['kind']='bs';snapshot['objects']['M']['power_transmittance']=.5
        result=certify_axial_reflection(snapshot,phase_budget_rad=0)
        row=self.keep('splitter_outside_contract_FAIL',result)
        self.assertIn('exactly one mirror',row['reason'])

    def test_sources_and_wavelength_stay_separate(self):
        snapshot=reflected_scene();second=deepcopy(snapshot['sources'][0])
        second['id']='other';second['position_BU'][0]=-.0625;snapshot['sources'].append(second)
        result=certify_axial_reflection(snapshot,phase_budget_rad=0)
        self.evidence['new_cases']['separate_sources_PASS']=result
        self.assertTrue(result['accepted_CPU_one_bounce_phase_budget'])
        self.assertEqual([r['source_id'] for r in result['path_certificates']],['s','other'])
        self.assertEqual([r['original_length_BU'] for r in result['path_certificates']],[[5,8],[11,16]])
        snapshot=reflected_scene();snapshot['lambda_BU']=.1
        result=certify_axial_reflection(snapshot,phase_budget_rad=0)
        row=self.keep('wavelength_transport_phase_FAIL',result)
        self.assertTrue(result['accepted_CPU_one_bounce_topology'])
        self.assertGreater(F(*row['phase_error_bound_rad']),0)
        self.assertFalse(result['accepted_CPU_one_bounce_phase_budget'])


if __name__=='__main__':
    result=unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromTestCase(ReflectionMarginTests))
    if hasattr(ReflectionMarginTests,'evidence'):
        print(json.dumps(ReflectionMarginTests.evidence,sort_keys=True,allow_nan=False))
    sys.exit(0 if result.wasSuccessful() else 1)

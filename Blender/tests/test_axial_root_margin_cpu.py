"""Focused NEW margin certificate cases; no old sweep/producer execution."""
from copy import deepcopy
from fractions import Fraction as F
import hashlib
from itertools import product
import json
import math
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'Blender/tests'))
sys.path.insert(0,str(ROOT/'Blender/benchmarks/capacity_audit'))
from axial_root_margin_cpu_v1 import certify_axial_roots
from history_lineage_cpu_v2 import scene_binding, triangles, nearest, vec
from test_root_transport_topology_cpu import scene, PINS as ROOT_PINS

PINS = dict(ROOT_PINS, **{
    'Blender/benchmarks/capacity_audit/root_transport_topology_cpu_v1.py':'b01b853b2bfe0ed8fd58d2d7cb5221d0e3d847f26cbb4f77fd66ece47eefac40',
    'Blender/tests/test_root_transport_topology_cpu.py':'93268447556c989150d3a838f5ad315d41c12e38dae919b15df08f24dc632376',
    'Blender/tests/exp005_precision_transport_audit.py':'9fee9688f41ac39ae4b2d97003d86f4f4f3f8483e07dc781b77e0a545acc6e4a',
    'coordinacion/respuestas/ROOT-TRANSPORT-TOPOLOGY-001-CODEX.json':'8782b245dd482e8545e3a0edf2904b86d1520612b834a8cad32019b47ed8a5eb'})


def interior_scene(origin, planes):
    result = scene(origin, planes)
    result['sources'][0]['position_BU'][2] = .03125
    return result


class AxialMarginTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for p,h in PINS.items():
            if hashlib.sha256((ROOT/p).read_bytes()).hexdigest() != h:
                raise ValueError('changed frozen foundation: '+p)
        cls.evidence={'pins_verified':PINS,'new_cases':{},'old_sweeps_rerun':False,'GPU_executed':False}

    def keep(self,name,value):
        self.evidence['new_cases'][name] = value
        return value['root_certificates'][0]

    def test_resolved_gap_margin_and_phase_bound(self):
        snapshot=interior_scene(0.,[('A',.1),('B',.1+2.**-30)])
        before=deepcopy(snapshot)
        result=certify_axial_roots(snapshot,phase_budget_rad=F(1,10**12))
        row=self.keep('resolved_margin_phase_PASS',result)
        self.assertEqual(snapshot,before)
        self.assertTrue(result['accepted_CPU_axial_root_margin'])
        self.assertTrue(result['accepted_CPU_one_leg_phase_budget'])
        self.assertGreater(F(*row['competitor_clearance_lower_BU']),0)
        self.assertEqual(row['primitive_id'],1)
        self.assertEqual(F(*row['phase_error_bound_rad']),F(1,2**49))
        self.assertFalse(result['native_promotion_allowed'])

    def test_exact_and_negative_direction_controls(self):
        for name, origin, planes, sign in (
                ('exact_positive',0.,[('A',.125),('B',.25)],1),
                ('exact_negative',.5,[('A',.375),('B',.25)],-1)):
            snapshot=interior_scene(origin,planes)
            snapshot['sources'][0]['direction']=[float(sign),0.,0.]
            result=certify_axial_roots(snapshot,phase_budget_rad=0)
            row=self.keep(name,result)
            self.assertTrue(result['accepted_CPU_one_leg_phase_budget'])
            self.assertEqual(row['length_interval_BU'],[[1,8],[1,8]])
            self.assertEqual(row['phase_error_bound_rad'],[0,1])

    def test_contact_and_competitor_collapse_remain_fail(self):
        for name,snapshot,text in (
                ('source_collapse_FAIL',interior_scene(.1,[('A',math.nextafter(.1,math.inf))]),'source-contact'),
                ('terminal_collapse_FAIL',interior_scene(0.,[('A',.1),('B',math.nextafter(.1,math.inf))]),'ambiguous')):
            result=certify_axial_roots(snapshot,phase_budget_rad=F(1,10**12))
            row=self.keep(name,result)
            self.assertFalse(result['accepted_CPU_axial_root_margin'])
            self.assertIn(text,row['reason'])
            self.assertFalse(result['accepted_CPU_one_leg_phase_budget'])

    def test_explicit_extra_uncertainty_can_fail_margin_without_changing_gate(self):
        snapshot=interior_scene(0.,[('A',.125),('B',.25)])
        result=certify_axial_roots(snapshot,phase_budget_rad=0,extra_axial_radius_BU=F(1,32))
        row=self.keep('touching_boxes_FAIL',result)
        self.assertIn('overlap or touch',row['reason'])
        self.assertFalse(result['accepted_CPU_axial_root_margin'])

    def test_phase_budget_zero_fails_nonexact_geometry_not_topology(self):
        result=certify_axial_roots(interior_scene(0.,[('A',.1)]),phase_budget_rad=0)
        row=self.keep('tight_phase_FAIL',result)
        self.assertTrue(result['accepted_CPU_axial_root_margin'])
        self.assertFalse(result['accepted_CPU_one_leg_phase_budget'])
        self.assertGreater(F(*row['phase_error_bound_rad']),0)

    def test_independent_axial_box_corners_enclosed(self):
        snapshot=interior_scene(0.,[('A',.125),('B',.25)])
        radius=F(1,128)
        result=certify_axial_roots(snapshot,phase_budget_rad=1,extra_axial_radius_BU=radius)
        row=self.keep('independent_box_corners_PASS',result)
        self.assertTrue(result['accepted_CPU_one_leg_phase_budget'])
        low,high=map(lambda x:F(*x),row['length_interval_BU'])
        _,packed=scene_binding(snapshot); base=triangles(packed)
        for sx,ax,bx in product((-radius,radius),repeat=3):
            geom=[(owner,tuple((p[0]+(ax if owner==0 else bx),p[1],p[2]) for p in tri)) for owner,tri in base]
            origin=(sx,F(1),F(1,32))
            t,pid,_,_=nearest(origin,(F(1),F(0),F(0)),geom,None)
            self.assertEqual(pid,row['primitive_id'])
            self.assertLessEqual(low,t);self.assertLessEqual(t,high)
            self.assertLessEqual(8*abs(t/F(1,8)-1),F(*row['phase_error_bound_rad']))

    def test_wavelength_charge_and_nonterminal_reference_excluded(self):
        snapshot=interior_scene(0.,[('A',.125)])
        snapshot['lambda_BU']=.1
        result=certify_axial_roots(snapshot,phase_budget_rad=0)
        row=self.keep('wavelength_transport_phase_FAIL',result)
        self.assertTrue(result['accepted_CPU_axial_root_margin'])
        self.assertNotEqual(*row['wavelength_interval_BU'])
        self.assertGreater(F(*row['phase_error_bound_rad']),0)
        self.assertFalse(result['accepted_CPU_one_leg_phase_budget'])
        # The frozen packer requires a declared terminal even if the root is a mirror.
        snapshot=interior_scene(0.,[('A',.125),('B',.25)])
        snapshot['objects']['A']['kind']='mirror';snapshot['objects']['A']['phase_rad']=0.
        result=certify_axial_roots(snapshot,phase_budget_rad=1)
        row=self.keep('nonterminal_phase_excluded',result)
        self.assertTrue(result['accepted_CPU_axial_root_margin'])
        self.assertFalse(result['accepted_CPU_one_leg_phase_budget'])
        self.assertNotIn('phase_error_bound_rad',row)
        self.assertIn('nonterminal',row['phase_exclusion'])

    def test_excluded_boundary_tilt_and_source_direction(self):
        boundary=scene(0.,[('A',.125)])
        result=certify_axial_roots(boundary,phase_budget_rad=0)
        self.assertIn('boundary',result['root_certificates'][0]['reason'])
        tilt=interior_scene(0.,[('A',.125)])
        tilt['objects']['A']['vertices_world_BU'][0][0]+=.03125
        result=certify_axial_roots(tilt,phase_budget_rad=0)
        self.assertIn('translated triangle',result['root_certificates'][0]['reason'])
        tilted_ray=interior_scene(0.,[('A',.125)])
        tilted_ray['sources'][0]['direction']=[1.,.125,0.]
        result=certify_axial_roots(tilted_ray,phase_budget_rad=0)
        self.assertIn('unit X',result['root_certificates'][0]['reason'])
        self.keep('boundary_outside_contract_FAIL',certify_axial_roots(boundary,phase_budget_rad=0))

    def test_two_sources_and_input_validation(self):
        snapshot=interior_scene(0.,[('A',.125)])
        second=deepcopy(snapshot['sources'][0]);second['id']='other';second['position_BU'][0]=-.125
        snapshot['sources'].append(second)
        result=certify_axial_roots(snapshot,phase_budget_rad=0)
        self.assertEqual([r['source_id'] for r in result['root_certificates']],['s','other'])
        self.assertEqual([r['original_length_BU'] for r in result['root_certificates']],[[1,8],[1,4]])
        self.assertTrue(result['accepted_CPU_one_leg_phase_budget'])
        self.evidence['new_cases']['separate_sources_PASS']=result
        for bad in (-1,True,float('nan'),float('inf')):
            with self.assertRaises(ValueError):certify_axial_roots(snapshot,phase_budget_rad=bad)
        unknown=deepcopy(snapshot);unknown['undeclared_meshes']=['unknown']
        with self.assertRaises(ValueError):certify_axial_roots(unknown,phase_budget_rad=0)


if __name__=='__main__':
    result=unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromTestCase(AxialMarginTests))
    if hasattr(AxialMarginTests,'evidence'):
        print(json.dumps(AxialMarginTests.evidence,sort_keys=True,allow_nan=False))
    sys.exit(0 if result.wasSuccessful() else 1)

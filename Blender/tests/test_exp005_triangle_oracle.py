"""Independent closed-form controls on SYNTHETIC triangle scenes; no Blender."""
import cmath
import copy
import math
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parent))
from exp005_triangle_oracle import trace_scene, unit, cross, add, scale
from exp005_scene_properties import decode_scene, sum_declared_channels


def disk(center, normal, kind, radius=.2):
    n = unit(normal); u = (0,0,1); v = cross(n,u)
    vertices = [center]+[add(center,add(scale(u,radius*math.cos(2*math.pi*j/12)),
                      scale(v,radius*math.sin(2*math.pi*j/12)))) for j in range(12)]
    record = {'kind':kind,'vertices_world_BU':vertices,
              'faces':[(0,j+1,(j+1)%12+1) for j in range(12)]}
    if kind=='mirror': record['phase_rad'] = 0.0
    if kind in ('det','escape'):
        record.update(mode_origin_BU=center,mode_direction=normal)
    return record


def mz():
    a,b = (1,-1,0),(1,1,0)
    objects = {name:disk(pos,n,kind) for name,pos,n,kind in [
        ('bs1',(0,0,0),a,'bs'), ('r1',(2,0,0),a,'mirror'),
        ('r2',(2,.5,0),b,'mirror'), ('f1',(1,.5,0),b,'mirror'),
        ('m2',(0,2,0),a,'mirror'), ('bs2',(1,2,0),a,'bs'),
        ('X',(2,2,0),(1,0,0),'det'), ('Y',(1,3,0),(0,1,0),'det')]}
    return {'schema':'exp005-readback-v1','lambda_BU':.1,'objects':objects,
            'undeclared_meshes':[],'sources':[{'id':'s','position_BU':(-1,0,0),
                'direction':(1,0,0),'field_reim':[1,0]}]}


class TriangleOracleTests(unittest.TestCase):
    def test_base_closed_form_no_hardcoded_paths(self):
        r = trace_scene(mz())
        self.assertEqual(len(r['paths']),4)
        self.assertLess(abs(r['fields']['X']+1j),1e-12)
        self.assertLess(abs(r['fields']['Y']),1e-12)
        self.assertAlmostEqual(r['output_power'],1,places=12)
        self.assertEqual(sorted(round(p['length_BU'],9) for p in r['paths']),[5,5,7,7])

    def test_scene_mirror_phase_matches_independent_mz_law(self):
        scene = mz(); scene['objects']['r1']['phase_rad'] = .1
        r = trace_scene(scene)
        self.assertAlmostEqual(r['powers']['Y'],math.sin(.05)**2,places=12)
        self.assertAlmostEqual(r['powers']['X'],math.cos(.05)**2,places=12)
        self.assertAlmostEqual(r['output_power'],1,places=12)

    def test_wavelength_rephases_all_measured_paths(self):
        scene = mz(); scene['lambda_BU'] = .101
        r = trace_scene(scene)
        expected = -.5j*(cmath.exp(2j*math.pi*7/.101)+cmath.exp(2j*math.pi*5/.101))
        self.assertLess(abs(r['fields']['X']-expected),1e-12)
        self.assertAlmostEqual(r['output_power'],1,places=12)

    def test_phase_reference_for_oblique_incidence(self):
        scene = mz()
        terminal = disk((2,0,0),(1,0,0),'det',radius=3)
        terminal['mode_direction'] = (1,1,0)
        scene['objects'] = {'d':terminal}
        scene['sources'] = [{'id':'s','position_BU':(-1,-1,0),
                              'direction':(1,1,0),'field_reim':[1,0]}]
        r = trace_scene(scene)
        expected = cmath.exp(2j*math.pi*2*math.sqrt(2)/.1)
        self.assertLess(abs(r['fields']['d']-expected),1e-12)
        self.assertAlmostEqual(r['paths'][0]['reference_offset_BU'],-math.sqrt(2))
        uncorrected = cmath.exp(2j*math.pi*3*math.sqrt(2)/.1)
        self.assertGreater(abs(r['fields']['d']-uncorrected),.1)
        ledger = sum_declared_channels(decode_scene(scene),[dict(p,initial_field=1+0j)
                                       for p in r['paths']])
        self.assertLess(abs(ledger['fields']['d']-expected),1e-12)

    def test_missing_mirror_and_unknown_decoration_fail(self):
        scene = mz(); del scene['objects']['r2']
        with self.assertRaises(ValueError): trace_scene(scene)
        scene = mz(); scene['undeclared_meshes'] = ['decor']
        with self.assertRaises(ValueError): trace_scene(scene)

    def test_escape_is_explicit_coherent_terminal(self):
        scene = mz(); scene['objects']['X']['kind'] = 'escape'
        r = trace_scene(scene)
        self.assertAlmostEqual(r['powers']['X'],1,places=12)
        self.assertEqual(sum(p['terminal']=='X' for p in r['paths']),2)

    def test_no_silent_angle_mix(self):
        scene = mz(); scene['objects']['X']['mode_direction'] = (-1,0,0)
        with self.assertRaises(ValueError): trace_scene(scene)

    def test_geometry_controls_calculation(self):
        base = mz(); shifted = copy.deepcopy(base)
        for name in ('r1','r2'):
            shifted['objects'][name]['vertices_world_BU'] = [add(v,(.0125,0,0))
                                      for v in shifted['objects'][name]['vertices_world_BU']]
        a,b = trace_scene(base),trace_scene(shifted)
        self.assertAlmostEqual(a['powers']['Y'],0,places=12)
        self.assertAlmostEqual(b['powers']['Y'],.5,places=12)

    def test_coincident_objects_and_resource_limits_abort(self):
        scene = mz(); scene['objects']['duplicate'] = copy.deepcopy(scene['objects']['bs1'])
        with self.assertRaises(ValueError): trace_scene(scene)
        with self.assertRaises(ValueError): trace_scene(mz(),max_rays=1)

    def test_coherent_two_source_energy_with_changed_wavelength(self):
        scene = mz(); scene['lambda_BU'] = .101
        scene['sources'].append({'id':'s2','position_BU':(0,-1,0),
                                  'direction':(0,1,0),'field_reim':[0,1]})
        r = trace_scene(scene)
        self.assertEqual(len(r['paths']),8)
        self.assertAlmostEqual(r['input_power'],2)
        self.assertAlmostEqual(r['output_power'],2,places=12)

    def test_terminal_reference_must_lie_on_plane(self):
        scene = mz(); scene['objects']['X']['mode_origin_BU'] = (2.1,2,0)
        with self.assertRaises(ValueError): trace_scene(scene)

    def test_visual_sham_and_missing_phase(self):
        scene = mz(); scene['objects']['r1']['display_color'] = [1,0,0]
        self.assertEqual(trace_scene(scene),trace_scene(mz()))
        del scene['objects']['r1']['phase_rad']
        with self.assertRaises(KeyError): trace_scene(scene)


if __name__=='__main__': unittest.main(verbosity=2)

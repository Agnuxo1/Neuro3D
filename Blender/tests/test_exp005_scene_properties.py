"""Small deterministic contract tests, not Blender or scene-oracle evidence."""
import cmath
import copy
import math
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from exp005_scene_properties import decode_scene, field_for_path


def snapshot():
    return {'lambda_BU': 0.1, 'objects': {
        's': {'kind': 'bs'}, 'm': {'kind': 'mirror', 'phase_rad': 0.0},
        'd': {'kind': 'det'}}}


def path(repeat=False):
    hits = [{'object_id': 's', 'event': 'r', 'distance_BU': 0.17},
            {'object_id': 'm', 'event': 'mirror', 'distance_BU': 0.231}]
    if repeat:
        hits.append({'object_id': 'm', 'event': 'mirror', 'distance_BU': 0.329})
    return hits + [{'object_id': 'd', 'event': 'detect', 'distance_BU': 0.413}]


class ScenePropertyTests(unittest.TestCase):
    def test_closed_form_reference_and_ledger(self):
        result = field_for_path(decode_scene(snapshot()), path())
        expected = -1j/math.sqrt(2) * cmath.exp(2j*math.pi*0.814/0.1)
        self.assertLess(abs(result['field']-expected), 1e-13)
        self.assertEqual(len(result['hits']), 3)
        self.assertAlmostEqual(abs(result['field'])**2, 0.5)

    def test_phase_factor_is_per_hit_not_per_unique_mirror(self):
        for repeated, multiplicity in ((False,1),(True,2)):
            with self.subTest(repeated=repeated):
                base = snapshot()
                changed = copy.deepcopy(base)
                changed['objects']['m']['phase_rad'] = 0.1
                a = field_for_path(decode_scene(base), path(repeated))['field']
                b = field_for_path(decode_scene(changed), path(repeated))['field']
                self.assertLess(abs(b/a-cmath.exp(1j*multiplicity*0.1)), 1e-13)

    def test_wavelength_factor(self):
        base, changed = snapshot(), snapshot()
        changed['lambda_BU'] = 0.101
        a = field_for_path(decode_scene(base), path())
        b = field_for_path(decode_scene(changed), path())
        expected = cmath.exp(2j*math.pi*a['length_BU']*(1/0.101-1/0.1))
        self.assertLess(abs(b['field']/a['field']-expected), 1e-13)

    def test_visual_sham_and_immutable_snapshot(self):
        base, sham = snapshot(), snapshot()
        sham['objects']['m']['display_color'] = [1,0,0,1]
        optics = decode_scene(base)
        base['objects']['m']['phase_rad'] = 1.0
        self.assertEqual(field_for_path(optics,path()),
                         field_for_path(decode_scene(sham),path()))
        with self.assertRaises(TypeError):
            optics.phases_rad['m'] = 2.0

    def test_missing_wavelength_and_phase_fail_closed(self):
        for remove_wavelength in (True,False):
            bad = snapshot()
            if remove_wavelength:
                del bad['lambda_BU']
            else:
                del bad['objects']['m']['phase_rad']
            with self.assertRaises(KeyError):
                decode_scene(bad)

    def test_invalid_wavelength(self):
        for value in (0,-1,float('nan'),float('inf'),True,'0.1'):
            with self.subTest(value=value):
                bad = snapshot(); bad['lambda_BU'] = value
                with self.assertRaises(ValueError): decode_scene(bad)

    def test_invalid_phase(self):
        for value in (float('nan'),float('inf'),True,'0'):
            bad = snapshot(); bad['objects']['m']['phase_rad'] = value
            with self.assertRaises(ValueError): decode_scene(bad)

    def test_invalid_distance(self):
        for value in (-1,float('inf'),float('nan'),True):
            bad = path(); bad[0]['distance_BU'] = value
            with self.assertRaises(ValueError): field_for_path(decode_scene(snapshot()),bad)

    def test_unknown_object_and_wrong_event(self):
        bad = path(); bad[0]['object_id'] = 'unregistered'
        with self.assertRaises(KeyError): field_for_path(decode_scene(snapshot()),bad)
        bad = path(); bad[0]['event'] = 'mirror'
        with self.assertRaises(ValueError): field_for_path(decode_scene(snapshot()),bad)

    def test_nonterminal_detector_and_incomplete_path(self):
        for hits in (path()+path(),path()[:-1],[]):
            with self.assertRaises(ValueError): field_for_path(decode_scene(snapshot()),hits)

    def test_initial_field_validation_and_zero(self):
        with self.assertRaises(ValueError):
            field_for_path(decode_scene(snapshot()),path(),complex(float('nan'),0))
        self.assertEqual(field_for_path(decode_scene(snapshot()),path(),0)['field'],0)


if __name__ == '__main__':
    unittest.main(verbosity=2)

"""Fake-scene bridge tests only: importing this file never imports bpy."""
import copy
import json
from pathlib import Path
import sys
from types import SimpleNamespace as NS
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from exp005_scene_readback import export_snapshot


class OffsetMatrix:
    def __init__(self, x=0): self.x = x
    def __matmul__(self, vector): return (vector[0]+self.x, vector[1], vector[2])


class Object(dict):
    def __init__(self, name, kind, x=0):
        super().__init__(kind=kind)
        if kind == 'mirror': self['phase_rad'] = 0.0
        if kind in ('det','escape'):
            self['mode_origin_BU'] = [0,0,0]
            self['mode_direction'] = [0,0,1]
        self.name, self.type = name, 'MESH'
        self.modifiers = []
        self.matrix_world = OffsetMatrix(x)
        self.data = NS(vertices=[NS(co=v) for v in ((0,0,0),(1,0,0),(0,1,0))],
                       polygons=[NS(vertices=(0,1,2))])


class Objects(dict):
    def __iter__(self): return iter(self.values())


class Scene(dict):
    def __init__(self):
        super().__init__(lambda_BU=0.1,
                         optical_object_ids=json.dumps(['mirror','detector']),
                         optical_sources=json.dumps([{'id':'s','position_BU':[0,0,-1],
                              'direction':[0,0,1],'field_reim':[1,0]}]))
        self.objects = Objects(mirror=Object('mirror','mirror',2),
                               detector=Object('detector','det'), decor=Object('decor','mesh'))


class ReadbackTests(unittest.TestCase):
    def test_geometry_exported_from_world_vertices(self):
        result = export_snapshot(Scene())
        self.assertEqual(result['objects']['mirror']['vertices_world_BU'][1],[3,0,0])
        self.assertEqual(result['objects']['mirror']['faces'],[[0,1,2]])
        self.assertEqual(result['undeclared_meshes'],['decor'])

    def test_scene_phase_and_wavelength_not_external_defaults(self):
        scene = Scene(); scene['lambda_BU'] = .101
        scene.objects['mirror']['phase_rad'] = .1
        result = export_snapshot(scene)
        self.assertEqual(result['lambda_BU'],.101)
        self.assertEqual(result['objects']['mirror']['phase_rad'],.1)

    def test_missing_phase_and_scene_properties(self):
        scene = Scene(); del scene.objects['mirror']['phase_rad']
        with self.assertRaises(KeyError): export_snapshot(scene)
        for key in ('lambda_BU','optical_object_ids','optical_sources'):
            scene = Scene(); del scene[key]
            with self.assertRaises(KeyError): export_snapshot(scene)

    def test_deleted_object_and_duplicate_declarations(self):
        scene = Scene(); del scene.objects['mirror']
        with self.assertRaises(KeyError): export_snapshot(scene)
        for ids in ([],['mirror','mirror'],[False]):
            scene = Scene(); scene['optical_object_ids'] = json.dumps(ids)
            with self.assertRaises(ValueError): export_snapshot(scene)

    def test_modifiers_do_not_export_stale_geometry(self):
        scene = Scene(); scene.objects['mirror'].modifiers = [object()]
        with self.assertRaises(ValueError): export_snapshot(scene)

    def test_undeclared_optical_geometry_fails_closed(self):
        scene = Scene(); scene.objects['surprise'] = Object('surprise','mirror')
        with self.assertRaises(ValueError): export_snapshot(scene)

    def test_empty_mesh_and_invalid_faces(self):
        for faces in ([],[NS(vertices=(0,1,9))],[NS(vertices=(0,1,1))]):
            scene = Scene(); scene.objects['mirror'].data.polygons = faces
            with self.assertRaises(ValueError): export_snapshot(scene)

    def test_nonfinite_geometry(self):
        scene = Scene(); scene.objects['mirror'].matrix_world = OffsetMatrix(float('nan'))
        with self.assertRaises(ValueError): export_snapshot(scene)

    def test_invalid_sources_and_duplicate_ids(self):
        for field, value in (('direction',[0,0,0]),('field_reim',[1]),
                             ('field_reim',[float('inf'),0]),('position_BU',[1,2])):
            scene = Scene(); sources = json.loads(scene['optical_sources'])
            sources[0][field] = value; scene['optical_sources'] = json.dumps(sources)
            with self.assertRaises(ValueError): export_snapshot(scene)
        scene = Scene(); s = json.loads(scene['optical_sources'])
        scene['optical_sources'] = json.dumps(s+s)
        with self.assertRaises(ValueError): export_snapshot(scene)

    def test_no_mutation_and_json_round_trip(self):
        scene = Scene(); before = copy.deepcopy(dict(scene))
        snapshot = export_snapshot(scene)
        self.assertEqual(dict(scene),before)
        self.assertEqual(json.loads(json.dumps(snapshot)),snapshot)


if __name__ == '__main__':
    unittest.main(verbosity=2)

"""Mode exclusions without Blender, GPU or field calculations in the gate."""
import copy
import unittest

from exp005_escape_fixture import escape_fixture, CASES
from exp005_mode_gate import mode_geometry, validate_native_modes
from exp005_mode_gate_runtime import adverse_cases


def minimal_paths(scene):
    name = 'b.escape'; record = scene['objects'][name]
    return [{'source_id': scene['sources'][0]['id'], 'reference_offset_BU': 0.,
             'hits': [{'object_id': name, 'event': 'escape',
                       'point_BU': list(record['mode_origin_BU']),
                       'incoming_direction': list(record['mode_direction'])}]}]


class ModeGateTests(unittest.TestCase):
    def test_all_new_fixture_treatments_accepted_conditionally(self):
        for case in CASES:
            scene = escape_fixture(case)
            result = validate_native_modes(scene, minimal_paths(scene))
            self.assertEqual((result['sources'],result['terminals']), (3,3))
            self.assertFalse(result['geometry_gate_passed'])

    def test_all_eight_adversaries_rejected_before_packing(self):
        scene = escape_fixture(); paths = minimal_paths(scene)
        for label, s, p in adverse_cases(scene, paths):
            with self.subTest(case=label), self.assertRaises((ValueError,KeyError)):
                validate_native_modes(s, p)

    def test_distinct_parallel_source_lines_remain_distinct(self):
        scene = escape_fixture()
        scene['sources'][1] = dict(scene['sources'][0], id='offset',position_BU=[-1,.01,0])
        self.assertEqual(len(mode_geometry(scene)[0]),3)

    def test_nonfinite_and_nonplanar_geometry_rejected(self):
        for label in ('nan','warped','grazing'):
            scene = escape_fixture()
            if label == 'nan': scene['sources'][1]['direction'] = [float('nan'),0,0]
            if label == 'warped':
                vertices=list(scene['objects']['b.escape']['vertices_world_BU'])
                vertices[0]=(6.01,vertices[0][1],vertices[0][2])
                scene['objects']['b.escape']['vertices_world_BU']=vertices
            if label == 'grazing': scene['objects']['b.escape']['mode_direction']=[0,1,0]
            with self.subTest(case=label), self.assertRaises(ValueError): mode_geometry(scene)

    def test_no_input_mutation_and_no_optical_propagation(self):
        scene=escape_fixture(); paths=minimal_paths(scene); before=copy.deepcopy((scene,paths))
        validate_native_modes(scene,paths)
        self.assertEqual((scene,paths),before)
        import ast
        from pathlib import Path
        import exp005_mode_gate
        tree=ast.parse(Path(exp005_mode_gate.__file__).read_text())
        imports=[n.module for n in ast.walk(tree) if isinstance(n,ast.ImportFrom)]
        self.assertFalse(any(n and ('oracle' in n or 'gpu' in n or 'bpy' in n) for n in imports))

    def test_native_entrypoints_validate_before_pack_and_dispatch(self):
        import ast
        from pathlib import Path
        for name in ('exp005_blender_gpu.py','exp005_escape_runtime.py'):
            tree=ast.parse(Path(__file__).with_name(name).read_text())
            calls={ast.unparse(n.func):(n.lineno,n.col_offset) for n in ast.walk(tree) if isinstance(n,ast.Call)}
            with self.subTest(name=name):
                self.assertLess(calls['validate_native_modes'],calls['pack_paths'])
                self.assertLess(calls['pack_paths'],calls['dispatch'])

    def test_mode_bounds_and_explicit_reference_data(self):
        scene=escape_fixture(); paths=minimal_paths(scene)
        for label in ('paths_empty','paths_many','hits_many','source_unknown','offset_missing'):
            changed=copy.deepcopy(paths)
            if label=='paths_empty': changed=[]
            if label=='paths_many': changed=changed*513
            if label=='hits_many': changed[0]['hits']*=65
            if label=='source_unknown': changed[0]['source_id']='missing'
            if label=='offset_missing': del changed[0]['reference_offset_BU']
            with self.subTest(case=label),self.assertRaises((ValueError,KeyError)):
                validate_native_modes(scene,changed)


if __name__=='__main__': unittest.main()

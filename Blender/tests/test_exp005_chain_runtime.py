"""CPU-only runtime-contract regression; actual Blender/GPU is separate."""
import ast
import copy
from pathlib import Path
import unittest
from exp005_chain_fixture import chain_fixture,inputs,set_fields
from exp005_chain_runtime import validate_roundtrip,analytic_check,causal_check,CASES,NEGATIVES
from exp005_triangle_oracle import trace_scene


def ideal_native(scene):
    oracle=trace_scene(scene)
    return {'valid':True,'errors':{},'ports':{p:{'field_reim':[f.real,f.imag],'power':abs(f)**2}
                                             for p,f in oracle['fields'].items()}}


class ChainRuntimeTests(unittest.TestCase):
    def test_phase_stays_inside_real_path_causal_cone(self):
        from exp005_chain_audit import phase_locality
        for cells in (3,4):
            scene=chain_fixture(cells); base=ideal_native(scene)
            phase=ideal_native(chain_fixture(cells,treatment='phase'))
            counts=phase_locality(cells,base,phase,trace_scene(scene))
            self.assertGreaterEqual(counts['untouched_port_probes'],cells-1)
            phase['ports']['c0.Y']['field_reim'][0]+=.000001
            with self.assertRaises(ValueError): phase_locality(cells,base,phase,trace_scene(scene))

    def test_roundtrip_requires_evaluated_exact_scene_properties(self):
        fixture=chain_fixture(4); snap=copy.deepcopy(fixture); snap['evaluated_optics_checked']=True
        validate_roundtrip(fixture,snap,copy.deepcopy(snap))
        for key in ('phase','T','geometry','lambda','source','unchecked'):
            bad=copy.deepcopy(snap)
            if key=='phase': bad['objects']['c3.r1']['phase_rad']+=.01
            if key=='T': bad['objects']['c3.bs2']['power_transmittance']=.2
            if key=='geometry': bad['objects']['c3.r1']['vertices_world_BU'][0]=(0,0,0)
            if key=='lambda': bad['lambda_BU']=.126
            if key=='source': bad['sources'][0]['field_reim']=[0,0]
            if key=='unchecked': bad['evaluated_optics_checked']=False
            with self.subTest(key=key),self.assertRaises(ValueError): validate_roundtrip(fixture,bad,bad)

    def test_counts_and_raw_gpu_call_without_cpu_paths(self):
        self.assertEqual(sum(len(list(inputs(c+1)))*len(CASES) for c in (3,4)),246)
        self.assertEqual(len(NEGATIVES)*2,10)
        code=Path(__file__).with_name('exp005_chain_runtime.py').read_text(); tree=ast.parse(code)
        calls=[n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='dispatch']
        self.assertEqual(len(calls),2)
        for call in calls: self.assertEqual([arg.id for arg in call.args],['gpu','shader','snapshot'])
        self.assertIn('mode_cap=5',code); self.assertIn('folder.exists()',code)
        self.assertIn('validate_roundtrip(fixture,before,after)',code)

    def test_independent_analytic_complex_phase_and_port_gate(self):
        for cells in (3,4):
            amps=[1+0j]+[0j]*cells
            for case in ('base','sham','phase'):
                scene=chain_fixture(cells,treatment=case); native=ideal_native(scene)
                self.assertLess(analytic_check(cells,case,amps,native),1e-11)
                native['ports']['c0.Y']['field_reim'][0]+=.01
                with self.assertRaises(ValueError): analytic_check(cells,case,amps,native)
            self.assertIsNone(analytic_check(cells,'T',amps,{}))

    def test_causal_and_exact_sham_gate_against_full_cpu_scene(self):
        results={}; cells=3
        for case in CASES:
            scene=chain_fixture(cells,treatment=case)
            for label,amps in inputs(cells+1):
                set_fields(scene,amps); results[(case,label)]=ideal_native(scene)
        self.assertGreater(min(causal_check(results,4).values()),1e-3)
        bad=copy.deepcopy(results); bad[('sham','basis0')]['ports']['c0.Y']['field_reim'][0]+=.000001
        with self.assertRaises(ValueError): causal_check(bad,4)
        bad=copy.deepcopy(results); bad[('phase','basis0')]=copy.deepcopy(bad[('base','basis0')])
        with self.assertRaises(ValueError): causal_check(bad,4)


if __name__=='__main__': unittest.main()

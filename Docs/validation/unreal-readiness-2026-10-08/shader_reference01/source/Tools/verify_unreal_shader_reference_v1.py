"""Analytic coherence controls and malformed buffer negatives, CPU only."""
import argparse
import copy
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
FILE=ROOT/'Plugins/SantoGrialPhotonic/Tests/photonic_shader_reference_v1.py'
spec=importlib.util.spec_from_file_location('shader_reference',FILE);ref=importlib.util.module_from_spec(spec);spec.loader.exec_module(ref)


def neuron(phase=0.,color=(1.,0.,0.),*,active=True,intensity=1.,frequency=0.):
    return [[0.,0.,0.,intensity],[phase,frequency,float(active),1.],[*color,0.]]


def evaluate(values,edges):return ref.step_records(values,edges,dt=.125,attenuation=0.,threshold=.25)


class Tests(unittest.TestCase):
    def test_nonunit_color_counterexample_fixed_in_versioned_reference(self):
        result=evaluate([neuron(color=(2.,0.,0.)),neuron(active=False,intensity=0.)],[[0.,1.,1.,0.]])
        self.assertEqual(result['neuron_output'][1][0][3],1.)
        self.assertEqual(result['signals'][0][2],[1.,0.,0.,0.])

    def test_coherence_not_individual_intensities(self):
        for phase,expected in ((0.,2.),(math.pi/2,math.sqrt(2)),(math.pi,0.)):
            result=evaluate([neuron(),neuron(phase),neuron(active=False,intensity=0.)],[[0.,2.,1.,0.],[1.,2.,1.,0.]])
            self.assertAlmostEqual(result['neuron_output'][2][0][3],expected,places=13)
        # Phase pi preserves nonzero incoming signal amplitudes while cancelling.
        self.assertEqual([s[0][2] for s in result['signals']],[1.,1.])
        self.assertLess(result['neuron_output'][2][1][2],1e-25)

    def test_zero_weight_and_loss_do_not_activate_target(self):
        result=evaluate([neuron(),neuron(active=False,intensity=0.)],[[0.,1.,0.,0.]])
        self.assertEqual(result['neuron_output'][1][0][3],0.)
        self.assertEqual(result['neuron_output'][1][1][2],0.)
        rows=[neuron(),neuron(active=False,intensity=0.)]
        lossy=ref.step_records(rows,[[0.,1.,1.,1.]],dt=.125,attenuation=2.,threshold=.25)
        self.assertLess(lossy['neuron_output'][1][0][3],1.)

    def test_actual_frequency_and_blended_energy_rule(self):
        rows=[neuron(frequency=2.),neuron(active=False,intensity=.25,frequency=10.)]
        result=ref.step_records(rows,[[0.,1.,1.,0.]],dt=0.,attenuation=0.,threshold=.25)
        target=result['neuron_output'][1]
        self.assertEqual(target[1][1],10.) # HLSL max(Frequency,OpticalState.y)
        self.assertEqual(target[0][3],.25*.985);self.assertEqual(target[1][3],1.)

    def test_malformed_nonfinite_and_wrong_endpoints_rejected(self):
        rows=[neuron(),neuron(active=False,intensity=0.)]
        for edge in ([0.,2.,1.,0.],[.5,1.,1.,0.],[0.,1.,float('nan'),0.],[0.,1.,1.],[-1.,1.,1.,0.]):
            with self.assertRaises(ValueError):evaluate(rows,[edge])
        bad=copy.deepcopy(rows);bad[1][1][3]=float('inf')
        with self.assertRaises(ValueError):evaluate(bad,[[0.,1.,1.,0.]])
        with self.assertRaises(ValueError):ref.step_records(rows,[],dt=-1.,attenuation=0.,threshold=.25)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True);args=parser.parse_args()
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
    files=[Path(__file__),FILE,ROOT/'Plugins/SantoGrialPhotonic/Shaders/SantoGrialPhotonic.usf']
    receipt={'schema':'neuro3d.unreal.shader_reference_tests.v1','status':'PASS' if result.wasSuccessful() else 'FAIL',
             'tests':result.testsRun,'errors':len(result.errors),'failures':len(result.failures),'GPU_executed':False,
             'scope':'CPU semantic/analytic controls; no Unreal compilation/readback parity/native binary32 certificate',
             'source_sha256':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}
    with args.out.open('xb') as stream:stream.write((json.dumps(receipt,indent=2,allow_nan=False)+'\n').encode())
    return 0 if result.wasSuccessful() else 1


if __name__=='__main__':raise SystemExit(main())

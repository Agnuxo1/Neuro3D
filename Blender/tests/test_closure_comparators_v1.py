"""Regression controls for leakage, imports and the exact EEG decision rules."""
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
COMPARISON=ROOT/"Benchmarks/eeg-motor-imagery/comparativa-anidada"


def load(path):
    spec=importlib.util.spec_from_file_location(path.stem,path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ComparatorRegressions(unittest.TestCase):
    def test_imports_do_not_change_cwd_or_environment(self):
        before=(Path.cwd(),dict(os.environ),list(sys.path))
        for path in [COMPARISON/"run_nested_comparators_v1.py",COMPARISON/"analyze_comparators_v1.py",
                     ROOT/"Benchmarks/eeg-motor-imagery/codigo/work/nested/predict_var_v2.py",
                     ROOT/"Blender/tests/test_validacion_onda_portable_v2.py"]:
            load(path)
        self.assertEqual((Path.cwd(),dict(os.environ),list(sys.path)),before)

    def test_grid_size_defaults_and_ties(self):
        m=load(COMPARISON/"run_nested_comparators_v1.py")
        self.assertEqual(len(m.EEG_CONFIGS),36)
        self.assertEqual(len(m.BANDS)*len(m.CS),36)
        self.assertEqual(m.choose(None,9),9)
        self.assertEqual(m.choose([1.,1.,2.],1),1)
        self.assertEqual(m.choose([0.,1.,2.],1),0)
        with self.assertRaises(ValueError):
            m.choose([float("nan")],0)

    def test_fbcsp_never_uses_evaluation_labels(self):
        m=load(COMPARISON/"run_nested_comparators_v1.py")
        from scipy.linalg import eigh
        class CSP:
            @staticmethod
            def csp_filters(X,y,k=3):
                cov=[np.mean([x@x.T/np.trace(x@x.T) for x in X[y==c]],axis=0) for c in (0,1)]
                _,v=eigh(cov[1],cov[0]+cov[1])
                return np.concatenate([v[:,:k],v[:,-k:]],axis=1)
        rng=np.random.default_rng(13)
        X=rng.normal(size=(28,8,100)); y=np.arange(28)%2
        train=np.arange(20); test=np.arange(20,28)
        a=m.fit_fbcsp(CSP,[X],y,train,[test],1.)[0]
        changed=y.copy();changed[test]=1-changed[test]
        b=m.fit_fbcsp(CSP,[X],changed,train,[test],1.)[0]
        np.testing.assert_array_equal(a,b)

    def test_holm_family_keeps_missing_comparison(self):
        m=load(COMPARISON/"analyze_comparators_v1.py")
        np.testing.assert_allclose(m.holm([0.01,1.]),[0.02,1.])
        np.testing.assert_allclose(m.holm([0.04,0.03]),[0.06,0.06])

    def test_zero_differences_and_primary_rule(self):
        m=load(COMPARISON/"analyze_comparators_v1.py")
        r=m.contrast([0.,0.,0.]);self.assertEqual(r["p_wilcoxon"],1.)
        self.assertEqual(r["decision"],"equivalent")
        self.assertEqual(m.contrast([-0.1]*4)["description"],"inferior")
        self.assertEqual(m.contrast([0.1]*4)["decision"],"superior")
        with self.assertRaises(ValueError):m.contrast([0.])

    def test_analyzer_rejects_pilot_and_altered_selection(self):
        m=load(COMPARISON/"analyze_comparators_v1.py")
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/"S001.npz"
            np.savez(p,meta=json.dumps({"pilot":True}))
            with self.assertRaisesRegex(ValueError,"Pilot"):
                m.estimates([p])
            np.savez(p,meta=json.dumps({"configs":[["A",1],["D",1]],"default_index":0}),
                     **{"y|0":np.array([0,1]),"o|0|0":np.array([-1.,1.]),"o|0|1":np.array([1.,-1.]),
                        "selected|0":np.array([1]),"inner_bce|0":np.array([]),"inner_acc|0":np.array([])})
            with self.assertRaisesRegex(ValueError,"selection differs"):
                m.estimates([p])


if __name__=="__main__":
    unittest.main()

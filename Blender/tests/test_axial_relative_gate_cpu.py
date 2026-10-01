"""Only retained data and new metadata gates; never run producer or old suite."""
from copy import deepcopy
from fractions import Fraction as F
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'Blender/benchmarks/capacity_audit'))
from axial_relative_gate_cpu_v1 import audit_retained_axial_relative, _relative, _audit_case, _load_retained

NAMES=['integer','quarter','coupled','dark','separate_groups','phase0','source0','underflow','high_intensity_FAIL','wrong_mode_FAIL']
def run(names,field=F(1,10**6),power=F(1,10**6)):
    return audit_retained_axial_relative(case_names=names,field_relative_budget=field,intensity_relative_budget=power)

class RelativeGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.previous=_load_retained()
        cls.evidence={'retained_report_sha256':'c4eceb7c32d54b7e996aacbc19af448e54bc42e6fa1ace18639494543a574277',
            'results':{},'synthetic_boundary_checks':{},'producer_or_old_suites_rerun':False,'GPU_executed':False}
    def keep(self,name,r):self.evidence['results'][name]=r;return r
    def test_bright_retained_cases_certify_positive_denominators(self):
        r=self.keep('bright_relative_PASS',run(['integer','quarter','coupled','separate_groups']))
        self.assertTrue(r['accepted_retained_relative_CPU_only'])
        for c in r['cases'].values():
            for p in c['ports'].values():
                for g in p['field_L1_groups'].values():self.assertGreater(F(*g['ideal_reference_lower_rational']),0)
                self.assertGreater(F(*p['incoherent_total_power']['ideal_reference_lower_rational']),0)
    def test_dark_retained_case_NO_relative_certificate_despite_absolute_PASS(self):
        r=self.keep('dark_relative_FAIL',run(['dark']));c=r['cases']['dark'];g=c['ports']['D']['field_L1_groups']['g']
        self.assertTrue(c['previous_absolute_and_upstream_accepted'])
        self.assertEqual(g['observed_rational'],[0,1]);self.assertIsNone(g['relative_error_upper_rational'])
        self.assertFalse(c['accepted_retained_relative_CPU_only'])
        prior=self.previous['run']['observations']['cases']['dark']['independent_exact_oracle']
        self.assertEqual(prior['actual_error_L1_rational'],[1,2**30])
        self.evidence['retained_dark_actual_relative_error']=[1,1]  # Exact oracle nonzero; observed0.
    def test_zero_budget_does_not_hide_conversion_error(self):
        r=self.keep('zero_relative_budget_FAIL',run(['integer'],field=0,power=0));c=r['cases']['integer']
        self.assertTrue(c['previous_absolute_and_upstream_accepted']);self.assertFalse(c['accepted_retained_relative_CPU_only'])
    def test_all_prior_failures_retained_even_with_loose_relative_budgets(self):
        r=self.keep('all_retained_cases',run(NAMES,field=100,power=100))
        for n in ['phase0','source0','underflow','high_intensity_FAIL','wrong_mode_FAIL']:
            self.assertFalse(r['cases'][n]['accepted_retained_relative_CPU_only'])
        self.assertFalse(r['cases']['wrong_mode_FAIL']['field_values_computed_in_retained_run'])
    def test_zero_zero_and_contact_denominators_never_floor_or_divide(self):
        for name,n,b in [('zero_zero',F(0),F(0)),('touching',F(1),F(1)),('overlapping',F(1),F(2))]:
            gate=_relative(n,b,F(100));self.assertFalse(gate['relative_budget_satisfied'])
            self.assertIsNone(gate['relative_error_upper_rational']);self.evidence['synthetic_boundary_checks'][name]=gate
    def test_exact_relative_threshold_and_no_epsilon(self):
        yes=_relative(F(3,2),F(1,2),F(1,2));no=_relative(F(3,2),F(1,2),F(1,2)-F(1,2**100))
        self.assertTrue(yes['relative_budget_satisfied']);self.assertFalse(no['relative_budget_satisfied'])
        self.evidence['synthetic_boundary_checks'].update(exact_threshold=yes,below_threshold=no)
    def test_invalid_selection_budget_and_changed_report_reject(self):
        for names in ([],['integer','integer'],['missing']):
            with self.assertRaises(ValueError):run(names)
        for b in (True,-1,float('nan'),float('inf'),'1e-6'):
            with self.assertRaises(ValueError):run(['integer'],field=b)
        with patch('axial_relative_gate_cpu_v1.Path.read_bytes',return_value=b'{}'):
            with self.assertRaisesRegex(ValueError,'report SHA mismatch'):run(['integer'])
        self.evidence['synthetic_boundary_checks']['malformed']='selection/budget/SHA reject; no file writes or external tamper claim'
    def test_synthetic_coverage_and_original_gauge_reject(self):
        c=deepcopy(self.previous['run']['observations']['cases']['integer'])
        c['composition']['ports']['D']['groups']['g']['phase_reference_id']='wrong'
        with self.assertRaisesRegex(ValueError,'gauge mismatch'):_audit_case(c,F(1),F(1))
        c=deepcopy(self.previous['run']['observations']['cases']['integer']);c['composition']['ports']={}
        with self.assertRaisesRegex(ValueError,'port coverage'):_audit_case(c,F(1),F(1))
        self.evidence['synthetic_boundary_checks']['coverage_gauge']='synthetic own metadata rejected; no scene/native replay'

if __name__=='__main__':
    result=unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromTestCase(RelativeGateTests))
    if hasattr(RelativeGateTests,'evidence'):print(json.dumps(RelativeGateTests.evidence,sort_keys=True,allow_nan=False))
    sys.exit(0 if result.wasSuccessful() else 1)

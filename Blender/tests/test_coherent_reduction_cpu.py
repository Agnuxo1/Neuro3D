"""Small new adversaries: coherent cancellation, input coverage and frequency."""
from copy import deepcopy
from itertools import permutations
import math
from pathlib import Path
import struct
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'Blender/benchmarks/capacity_audit'))
from coherent_reduction_cpu_v1 import reduce_fields


def words(x,y=0.): return [struct.unpack('<I',struct.pack('<f',v))[0] for v in (x,y)]
def rows(values): return [{'id':i,'source_id':'s','port':'p','field_uint32':words(v)} for i,v in enumerate(values)]
SOURCE = {'s':{'coherence_group':'g','lambda_BU':.125}}
def run(data, algorithm='linear32', sources=SOURCE):
    return reduce_fields(data, expected_ids=list(range(len(data))), sources=sources,
                         algorithm=algorithm, field_budget=1e-4, intensity_budget=2e-4)


class ReductionTests(unittest.TestCase):
    def test_six_orders_exact_same_reference_expose_linear_loss_not_gate_relaxation(self):
        data = rows([2.**25,1.,-2.**25]); observed = set(); failures=0
        for order in permutations(data):
            result = run(list(order)); group=result['ports']['p']['groups']['g']
            self.assertEqual(group['reference_field_rational'],[[1,1],[0,1]])
            observed.add(group['modeled_field_reim'][0])
            failures += not result['accepted_represented_reduction_only']
        self.assertEqual(observed,{0.,1.}); self.assertEqual(failures,4)

    def test_compensated_CPU_model_recovers_unit_residual_all_six_orders(self):
        for order in permutations(rows([2.**25,1.,-2.**25])):
            result=run(list(order),'neumaier32'); group=result['ports']['p']['groups']['g']
            self.assertEqual(group['modeled_field_reim'],[1.,0.])
            self.assertEqual(group['field_error_L1_rational'],[0,1])
            self.assertTrue(result['accepted_represented_reduction_only'])
            self.assertFalse(result['native_promotion_allowed'])

    def test_normalized_cancelled_field_absolute_and_relative_not_confused(self):
        result=run(rows([1.,2.**-25,-1.]))
        group=result['ports']['p']['groups']['g']
        self.assertEqual(group['modeled_field_reim'],[0.,0.])
        self.assertEqual(group['reference_field_rational'][0],[1,2**25])
        # 100% relative error yet absolute budgets pass: retain BOTH facts.
        self.assertTrue(result['accepted_represented_reduction_only'])
        self.assertEqual(group['field_error_L1_rational'],[1,2**25])

    def test_complex_quadrature_residual_checks_both_components_and_power(self):
        data=rows([2.**25,1.,-2.**25])
        for row,value in zip(data,[2.**25,1.,-2.**25]):row['field_uint32']=words(value,value)
        lost=run(data)['ports']['p']['groups']['g']
        self.assertEqual(lost['reference_field_rational'],[[1,1],[1,1]])
        self.assertEqual(lost['field_error_L1_rational'],[2,1])
        self.assertEqual(lost['intensity_error_rational'],[2,1])
        fixed=run(data,'neumaier32')['ports']['p']['groups']['g']
        self.assertEqual(fixed['modeled_field_reim'],[1.,1.])
        self.assertEqual(fixed['field_error_L1_rational'],[0,1])

    def test_two_coherence_groups_never_cross_sum_fields(self):
        data=rows([1.,-1.]); data[1]['source_id']='t'
        sources={'s':SOURCE['s'],'t':{'coherence_group':'h','lambda_BU':.25}}
        result=run(data,sources=sources)
        self.assertEqual(result['ports']['p']['groups']['g']['reference_intensity_rational'],[1,1])
        self.assertEqual(result['ports']['p']['groups']['h']['reference_intensity_rational'],[1,1])
        coherent={'s':SOURCE['s'],'t':SOURCE['s']}
        self.assertEqual(run(data,sources=coherent)['ports']['p']['groups']['g']['reference_intensity_rational'],[0,1])

    def test_mixed_wavelength_coherent_group_rejects(self):
        data=rows([1.,1.]); data[1]['source_id']='t'
        sources={'s':SOURCE['s'],'t':{'coherence_group':'g','lambda_BU':math.nextafter(.125,1.)}}
        with self.assertRaises(ValueError): run(data,sources=sources)

    def test_missing_duplicate_unknown_rows_or_sources_reject(self):
        data=rows([1.,-1.])
        for bad in ([data[0],data[0]], [dict(data[0],id=7),data[1]],
                    [dict(data[0],source_id='foreign'),data[1]], [dict(data[0],extra=1),data[1]]):
            with self.assertRaises(ValueError): run(bad)
        with self.assertRaises(ValueError):
            reduce_fields(data[:1],expected_ids=[0,1],sources=SOURCE,algorithm='linear32',
                          field_budget=1e-4,intensity_budget=2e-4)

    def test_nonfinite_subnormal_bool_and_overflow_fail_closed(self):
        for components in ([0x7f800000,0],[0x7fc00000,0],[1,0],[True,0]):
            data=rows([1.]);data[0]['field_uint32']=components
            with self.assertRaises(ValueError):run(data)
        with self.assertRaises(ValueError):run(rows([3e38,3e38]))
        with self.assertRaises(ValueError):
            reduce_fields(rows([1.]),expected_ids=[0],sources=SOURCE,algorithm='linear32',
                          field_budget=True,intensity_budget=2e-4)


if __name__=='__main__':unittest.main()

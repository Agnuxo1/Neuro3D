"""Small conditional composition regressions, no GPU/peer/frozen suite replay."""
from copy import deepcopy
from fractions import Fraction as F
from itertools import permutations, product
from pathlib import Path
import struct
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'Blender/benchmarks/capacity_audit'))
from coherent_error_composition_cpu_v1 import compose_field_errors

SOURCE = {'s': {'coherence_group': 'g', 'lambda_BU': .125, 'phase_reference_id': 'origin0'}}


def rows(values):
    return [{'id': i, 'source_id': 's', 'port': 'p',
             'field_uint32': [struct.unpack('<I', struct.pack('<f', x))[0] for x in value]}
            for i, value in enumerate(values)]


def errors(data, budget=F(0), sources=SOURCE):
    return [{**deepcopy(row), 'coherence_group': sources[row['source_id']]['coherence_group'],
             'phase_reference_id': sources[row['source_id']]['phase_reference_id'],
             'lambda_BU': sources[row['source_id']]['lambda_BU'],
             'field_error_L1_upper_rational': [budget.numerator, budget.denominator]}
            for row in data]


def run(data, budgets=None, sources=SOURCE, algorithm='neumaier32'):
    return compose_field_errors(data, expected_ids=list(range(len(data))), sources=sources,
        path_error_bounds=errors(data, sources=sources) if budgets is None else budgets,
        algorithm=algorithm, field_budget=1e-4, intensity_budget=2e-4)


class ComposedErrorTests(unittest.TestCase):
    def test_zero_prior_bounds_reproduce_reduction_contributions(self):
        data = rows([(1., 0.), (2.**-25, 0.), (-1., 0.)])
        for algorithm in ('linear32', 'neumaier32'):
            out = run(data, algorithm=algorithm); group = out['ports']['p']['groups']['g']
            old = out['represented_reduction']['ports']['p']['groups']['g']
            self.assertEqual(group['composed_field_error_upper_rational'], old['field_error_L1_rational'])
            self.assertEqual(group['composed_intensity_error_upper_rational'], old['intensity_error_rational'])
            self.assertEqual(out['accepted_conditional_upstream_and_reduction_only'],
                             out['represented_reduction']['accepted_represented_reduction_only'])
            self.assertFalse(out['native_promotion_allowed'])

    def test_exact_compensated_reduction_cannot_hide_upstream_error_all_orders(self):
        data = rows([(2.**25, 0.), (1., 0.), (-2.**25, 0.)])
        budgets = errors(data, F(1, 20000))
        for order in permutations(data):
            out = run(list(order), budgets)
            self.assertTrue(out['represented_reduction']['accepted_represented_reduction_only'])
            self.assertEqual(out['ports']['p']['groups']['g']['composed_field_error_upper_rational'], [3, 20000])
            self.assertFalse(out['accepted_conditional_upstream_and_reduction_only'])

    def test_field_gate_can_pass_while_composed_power_gate_fails(self):
        data = rows([(1., 0.)]); out = run(data, errors(data, F(1, 10000)))
        group = out['ports']['p']['groups']['g']
        self.assertTrue(group['field_budget_satisfied'])
        self.assertEqual(group['composed_intensity_error_upper_rational'], [20001, 100000000])
        self.assertFalse(out['ports']['p']['intensity_budget_satisfied'])
        self.assertFalse(out['accepted_conditional_upstream_and_reduction_only'])

    def test_complex_perturbations_bounded_by_exact_rational_oracle(self):
        data = rows([(1., .5), (-.25, .125)])
        out = run(data, errors(data, F(1, 100000)))
        group = out['ports']['p']['groups']['g']; b = F(2, 100000)
        field_bound = F(*group['composed_field_error_upper_rational'])
        power_bound = F(*group['composed_intensity_error_upper_rational'])
        y = [F(3,4), F(5,8)]
        # 25 rational perturbations, including non-axis complex ones; L1<=B.
        count = 0
        for a,c in product(range(-2,3), repeat=2):
            dr,di = F(a,4)*b, F(c,4)*b
            actual = [y[0]+dr, y[1]+di]
            self.assertLessEqual(abs(dr)+abs(di), field_bound)
            self.assertLessEqual(abs(sum(x*x for x in actual)-sum(x*x for x in y)), power_bound)
            count += 1
        self.assertEqual(count, 25)

    def test_independent_coherence_groups_add_power_bounds_not_fields(self):
        data = rows([(1., 0.), (-1., 0.)]); data[1]['source_id'] = 't'
        sources = {**SOURCE, 't': {'coherence_group':'h','lambda_BU':.25,'phase_reference_id':'other'}}
        out = run(data, errors(data, F(1, 100000), sources), sources)
        self.assertEqual(out['ports']['p']['intensity_error_upper_rational'], [200001, 5000000000])
        self.assertEqual(set(out['ports']['p']['groups']), {'g','h'})

    def test_missing_duplicate_or_mismatched_error_binding_rejects(self):
        data = rows([(1., 0.), (-1., 0.)]); original = errors(data)
        bad = [original[:1], [original[0], original[0]]]
        for key,value in [('id',7), ('port','foreign'), ('source_id','unknown'),
                          ('coherence_group','other'), ('phase_reference_id','other'), ('lambda_BU',.25),
                          ('field_uint32',[True,0]), ('field_uint32',[0,0])]:
            changed = deepcopy(original); changed[0][key] = value; bad.append(changed)
        for record in bad:
            with self.assertRaises(ValueError): run(data, record)

    def test_noncanonical_negative_bool_unbounded_error_rational_rejects(self):
        data = rows([(1., 0.)])
        for value in ([1,0],[-1,1],[True,1],[2,4],[2**257,1], [0,2], 'zero'):
            budgets = errors(data); budgets[0]['field_error_L1_upper_rational'] = value
            with self.assertRaises(ValueError): run(data, budgets)

    def test_coherent_sources_need_common_reference_and_same_wavelength(self):
        data = rows([(1., 0.), (-1., 0.)]); data[1]['source_id'] = 't'
        for change in ({'phase_reference_id':'other'}, {'lambda_BU':.25}):
            sources = {**SOURCE, 't': {**SOURCE['s'], **change}}
            with self.assertRaises(ValueError): run(data, errors(data, sources=sources), sources)
        sources = {**SOURCE, 't': dict(SOURCE['s'])}
        self.assertTrue(run(data, errors(data, sources=sources), sources)['accepted_conditional_upstream_and_reduction_only'])


if __name__ == '__main__': unittest.main()

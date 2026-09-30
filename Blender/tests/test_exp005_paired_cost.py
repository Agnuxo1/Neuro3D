"""Paired order/statistics/full-source oracle and measurement-boundary gates."""
import ast
import copy
from pathlib import Path
import unittest
from exp005_paired_cost import plan,order,percentile,summarize,PAIRS,WARMUPS
from exp005_chain_fixture import chain_fixture,set_fields,analytic_fields
from exp005_triangle_oracle import trace_scene


class PairedCostTests(unittest.TestCase):
    def samples(self):
        return [{'pair':index,'backend':name,'hot_inference_ms':2. if name=='repeated' else 4.,
                 'dispatch_sync_readback_ms':1. if name=='repeated' else 2.}
                for index in range(PAIRS) for name in order(index)]

    def test_fixed_balanced_order_and_no_post_measurement_selection(self):
        self.assertEqual((len(list(plan())),PAIRS,WARMUPS),(4,20,3))
        self.assertEqual(sum(order(i)[0]=='repeated' for i in range(PAIRS)),10)
        for index in (-1,20,True,1.):
            with self.assertRaises(ValueError): order(index)
        data=self.samples(); result=summarize(data)
        self.assertEqual(result['paired_repeated_over_shared']['median'],.5)
        self.assertEqual(result['shared']['hot_p95_ms'],4.)
        for bad in (data[:-1],list(reversed(data))):
            with self.assertRaises(ValueError): summarize(bad)
        bad=copy.deepcopy(data); bad[0]['pair']=1
        with self.assertRaises(ValueError): summarize(bad)

    def test_percentiles_reject_invalid_times_and_keep_outliers(self):
        self.assertAlmostEqual(percentile([1.,2.,3.,4.,100.],.95),80.8)
        for values in ([],[0.],[-1.],[float('nan')],[float('inf')]):
            with self.assertRaises(ValueError): percentile(values,.95)

    def test_all_sources_simultaneously_has_independent_field_and_balance(self):
        for cells,label,amps in plan():
            scene=chain_fixture(cells); set_fields(scene,amps); oracle=trace_scene(scene)
            reference=analytic_fields(cells,amps)
            self.assertLess(max(abs(reference[p]-f) for p,f in oracle['fields'].items()),1e-11)
            self.assertLess(abs(oracle['output_power']-sum(abs(a)**2 for a in amps)),1e-11)
            if label=='all1': self.assertEqual((len(oracle['paths']),oracle['rays']),(58,184) if cells==3 else (128,415))

    def test_timer_boundary_precedes_oracle_and_records_cpu_cost(self):
        code=Path(__file__).with_name('exp005_paired_cost.py').read_text(); tree=ast.parse(code)
        once=next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name=='once')
        text=ast.get_source_segment(code,once)
        self.assertLess(text.index('start=time.perf_counter()'),text.index('source_fields(scene,amps)'))
        self.assertLess(text.index('source_fields(scene,amps)'),text.index('readback(bpy,scene)'))
        self.assertLess(text.index('hot_ms='),text.index('metrics,oracle=check('))
        self.assertIn('independent_validation_ms',text); self.assertNotIn('save_as_mainfile',code)
        calls=[n for n in ast.walk(once) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='dispatch']
        self.assertEqual(len(calls),1)
        self.assertEqual([ast.unparse(n) for n in calls[0].args],['gpu','shaders[name]','snapshot'])


if __name__=='__main__': unittest.main()

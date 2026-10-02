"""New HOST-only reflected budget controls; frozen plans are never output-fitted."""
import copy,json,sys,unittest
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'benchmarks/capacity_audit'))
import axial_reflected_source_budget_bridge_HOST_v1 as core
DATA={}
class ReflectedBudgetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.loaded=core.load_retained();cls.names=list(cls.loaded[0][0])
        cls.plans=copy.deepcopy(cls.loaded[0][-1]['synthetic_INPUT_plans'])
    def reject(self,label,fn,rows):
        try:fn()
        except (ValueError,KeyError,TypeError,IndexError) as e:rows.append({'label':label,'reason':str(e)})
        else:self.fail('expected STOP: '+label)
    def test_a_absent(self):
        with patch.object(core,'load_retained',return_value=self.loaded),patch.object(core,'admit_reflection',side_effect=AssertionError('no absent-plan proof inspection')) as adm,patch.object(core,'compare_source',side_effect=AssertionError('no missing-plan comparison')) as comp:
            a=core.audit_reflected_budget_HOST(self.names,{},model=core.MODEL)
            self.assertEqual(adm.call_count,comp.call_count,0)
        self.assertEqual((a['missing_INPUT_plans_STOP'],a['explicit_INPUT_plans_valid'],a['partial_source_comparisons']),(17,0,0))
        self.assertEqual(sum(len(c['sources']) for c in a['cases'].values()),19)
        DATA['real_missing']=a
    def test_b_retained_INPUT(self):
        before=core.digest(self.loaded);DATA['retained_synthetic_INPUT_plans']=copy.deepcopy(self.plans)
        with ExitStack() as stack:
            stack.enter_context(patch.object(core,'load_retained',return_value=self.loaded))
            for mod,key in ((core.prior,'execute'),(core.prior,'native_negate'),(core.prior,'runtime_probe'),
                            (core.material.bridge.prior,'execute'),(core.material.bridge.prior,'native_cast32'),
                            (core.material.bridge.prior.prior,'execute'),(core.material.original,'trace_original'),
                            (core.quotas,'compare_source')):
                stack.enter_context(patch.object(mod,key,side_effect=AssertionError('no old native producer/probe/retrace/substitution')))
            a=core.audit_reflected_budget_HOST(list(self.plans),self.plans,model=core.MODEL)
        self.assertEqual(core.digest(self.loaded),before)
        self.assertEqual((a['explicit_INPUT_plans_valid'],a['partial_source_comparisons'],a['partial_seven_stage_comparisons_fit']),(3,2,2))
        for c in a['cases'].values():
            self.assertEqual(c['status'],'STOP');self.assertTrue(all(c[n] is False for n in core.FALSE))
            for row in c['sources']:
                self.assertTrue(all(row[n] is False for n in core.FALSE))
                if row['stage_comparisons'] is not None:
                    self.assertEqual(set(row['stage_comparisons']),set(core.quotas.STAGES))
                    self.assertEqual(row['stage_comparisons']['ideal_material_L1']['charge_L1'],[0,1])
                    self.assertIs(row['retained_reflection_executed_CPU'],True);self.assertEqual(row['new_material_operations'],0)
        DATA['synthetic_partial']=a
        for label,control,name in [('Horner_zero_FAIL','stage_overspend_control','nonexact_geometry_phase_PASS'),('source_zero_FAIL','explicit_zero_FAIL','thin_resolved')]:
            plan=copy.deepcopy(self.loaded[0][-1][control]['INPUT_plan'])
            with patch.object(core,'load_retained',return_value=self.loaded):
                out=core.audit_reflected_budget_HOST([name],{name:plan},model=core.MODEL)
            row=out['cases'][name]['sources'][0];self.assertFalse(row['partial_seven_stage_comparison_fits'])
            if label=='Horner_zero_FAIL':
                self.assertTrue(row['partial_total_fits_source_cap']);self.assertFalse(row['stage_comparisons']['source_Horner_L1']['fits'])
            else:self.assertFalse(row['partial_total_fits_source_cap'])
            DATA[label]={'retained_INPUT_plan':plan,'audit':out}
    def test_c_atomic_proofs(self):
        names=['nonexact_geometry_phase_PASS','thin_resolved'];rows=[]
        def row(r):return r[1]['cases']['thin_resolved']['sources'][0]
        mutations=[
            ('reflection_word',lambda r:row(r)['result']['reflected_uint64'].__setitem__(0,row(r)['result']['reflected_uint64'][0]+1)),
            ('material_node',lambda r:row(r)['result']['material_nodes'][0].__setitem__('output_uint64',0)),
            ('material_charge_launder',lambda r:row(r)['result']['fifteen_source_material_charges_L1'].__setitem__('ideal_material_L1',[1,1])),
            ('bool_zero_node_charge',lambda r:row(r)['result']['material_nodes'][0].__setitem__('exact_material_rounding_error_L1',[False,1])),
            ('integer_material_flag',lambda r:row(r)['result'].__setitem__('material_executed',1)),
            ('integer_node_count',lambda r:row(r)['result'].__setitem__('new_main_CPU_unary_negations',True)),
            ('upstream_source_word',lambda r:r[0][1]['cases']['thin_resolved']['sources'][0]['result']['product_uint64'].__setitem__(0,0)),
            ('profile_phase',lambda r:row(r)['result']['material_profile'].__setitem__('mirror_phase_ORIGINAL_uint64',1)),
            ('gauge',lambda r:row(r)['result'].__setitem__('phase_reference_id','foreign')),
            ('material_parent_SHA',lambda r:row(r)['result'].__setitem__('retained_material_admission_row_sha256','0'*64)),
            ('quota_invented',lambda r:row(r)['result'].__setitem__('executed_material_quota_fits',True)),
        ]
        with patch.object(core,'compare_source',side_effect=AssertionError('ALL proofs before ANY comparisons')) as comp:
            for label,f in mutations:
                r=copy.deepcopy(self.loaded);f(r)
                with patch.object(core,'load_retained',return_value=r):
                    self.reject(label,lambda:core.audit_reflected_budget_HOST(names,{n:self.plans[n] for n in names},model=core.MODEL),rows)
            with patch.object(core,'PREVIOUS_SHA','0'*64):
                self.reject('parent_SHA',core.load_retained,rows)
            self.assertEqual(comp.call_count,0)
        DATA['proof_rejections']={'rows':rows,'comparison_calls':0}
    def test_d_INPUT_mapping(self):
        names=['nonexact_geometry_phase_PASS','thin_resolved'];rows=[]
        mutations=[
            ('second_plan_context',lambda p:p['thin_resolved'].__setitem__('context_sha256','0'*64)),
            ('bool_material_quota',lambda p:p['thin_resolved']['sources'][0]['stages_L1'].__setitem__('ideal_material_L1',[True,1])),
            ('negative_material_quota',lambda p:p['thin_resolved']['sources'][0]['stages_L1'].__setitem__('ideal_material_L1',[-1,1])),
            ('missing_material_quota',lambda p:p['thin_resolved']['sources'][0]['stages_L1'].pop('ideal_material_L1')),
            ('output_fitting_injection',lambda p:p['thin_resolved'].__setitem__('expected_output',[0,0])),
        ]
        with patch.object(core,'load_retained',return_value=self.loaded),patch.object(core,'admit_reflection',side_effect=AssertionError('ALL INPUT before proof inspection')) as adm:
            for label,f in mutations:
                ps={n:copy.deepcopy(self.plans[n]) for n in names};f(ps)
                self.reject(label,lambda ps=ps:core.audit_reflected_budget_HOST(names,ps,model=core.MODEL),rows)
            for label,ns,ps,m in [('model',names,{},'bad'),('empty',[],{},core.MODEL),('duplicate',names*2,{},core.MODEL),('unknown',['foreign'],{},core.MODEL),('unused_plan',['thin_resolved'],self.plans,core.MODEL)]:
                self.reject(label,lambda ns=ns,ps=ps,m=m:core.audit_reflected_budget_HOST(ns,ps,model=m),rows)
            self.assertEqual(adm.call_count,0)
        with patch.object(core,'load_retained',return_value=self.loaded),patch.object(core,'compare_source',side_effect=AssertionError('None missing no comparison')):
            none=core.audit_reflected_budget_HOST(['thin_resolved'],{'thin_resolved':None},model=core.MODEL)
        self.assertEqual(none['missing_INPUT_plans_STOP'],1);DATA['explicit_None_missing']=none
        src=self.loaded[1]['cases']['thin_resolved']['sources'][0]['result']
        ev={'fifteen_charges_L1':copy.deepcopy(src['fifteen_source_material_charges_L1']),'point_reflected_source_bound_L1':src['point_reflected_source_bound_to_FIXED_ORIGINAL_L1']}
        for label,f in [('charge_missing',lambda e:e['fifteen_charges_L1'].pop('ideal_material_L1')),('charge_negative',lambda e:e['fifteen_charges_L1'].__setitem__('ideal_material_L1',[-1,1])),('charge_bool',lambda e:e['fifteen_charges_L1'].__setitem__('ideal_material_L1',[False,1])),('sum_wrong',lambda e:e.__setitem__('point_reflected_source_bound_L1',[0,1]))]:
            e=copy.deepcopy(ev);f(e);self.reject(label,lambda e=e:core.map_charges(e),rows)
        mapping=copy.deepcopy(core.MAPPING);mapping['source_Horner_L1']+=('ideal_material_L1',)
        with patch.object(core,'MAPPING',mapping):self.reject('duplicate_material_mapping',lambda:core.map_charges(ev),rows)
        DATA['INPUT_mapping_rejections']={'rows':rows,'proof_inspection_calls':0}
if __name__=='__main__':
    r=unittest.TextTestRunner(verbosity=2,stream=sys.stderr).run(unittest.defaultTestLoader.loadTestsFromTestCase(ReflectedBudgetTests))
    print(json.dumps({'PASS':r.wasSuccessful(),'tests':r.testsRun,'data':DATA},sort_keys=True,separators=(',',':'),allow_nan=False))
    raise SystemExit(0 if r.wasSuccessful() else 1)

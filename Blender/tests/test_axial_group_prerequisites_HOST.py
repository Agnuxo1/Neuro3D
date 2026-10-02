"""Group prerequisites must never promote a partial retained source fit."""
import copy,json,sys,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'benchmarks/capacity_audit'))
import axial_group_prerequisites_HOST_v1 as core
DATA={}
class GroupPrerequisiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.loaded=core.load_retained()
    def test_a_real(self):
        with patch.object(core,'load_retained',return_value=self.loaded):
            a=core.audit_group_prerequisites_HOST('real_missing',model=core.MODEL)
        self.assertEqual(len(a['cases']),17);self.assertEqual(a['ready_groups'],0)
        groups=[g for c in a['cases'].values() for g in c['groups']]
        self.assertEqual(sum(len(g['source_order']) for g in groups),19)
        self.assertTrue(all(g['INPUT_reserves_L1'] is None and g['group_field_L1_bound'] is None for g in groups))
        DATA['real_missing']=a
    def test_b_controls(self):
        outputs={}
        with patch.object(core,'load_retained',return_value=self.loaded),patch.object(core.prior,'audit_reflected_budget_HOST',side_effect=AssertionError('no prior recomputation')):
            for variant in core.VARIANTS[1:]:
                a=core.audit_group_prerequisites_HOST(variant,model=core.MODEL);outputs[variant]=a
                for c in a['cases'].values():
                    for g in c['groups']:
                        self.assertEqual(g['readiness'],'STOP');self.assertEqual(g['source_phase_missing'],g['source_order'])
                        self.assertTrue(all(g[n] is False for n in core.FALSE))
                        self.assertIsNone(g['executed_reduction_charge_L1']);self.assertIsNone(g['group_field_uint64'])
            groups=[g for c in outputs['synthetic_partial']['cases'].values() for g in c['groups']]
            self.assertEqual(sum(len(g['point_fit_sources']) for g in groups),2)
            self.assertEqual(outputs['synthetic_partial']['cases']['two_sources']['groups'][0]['missing_point_sources'],['s','other'])
            for v in ('Horner_zero_FAIL','source_zero_FAIL'):
                g=next(iter(outputs[v]['cases'].values()))['groups'][0]
                self.assertEqual(g['failed_point_sources'],['s']);self.assertIn('retained_point_stage_quota_FAIL',g['blockers'])
        DATA.update(outputs)
    def reject(self,label,fn,rows):
        try:fn()
        except (ValueError,KeyError,TypeError,IndexError,StopIteration) as e:rows.append({'label':label,'reason':str(e)})
        else:self.fail('expected STOP '+label)
    def test_c_atomic(self):
        rows=[]
        def mutate(label,fn):
            r=copy.deepcopy(self.loaded);fn(r[1]['synthetic_partial']['cases']['thin_resolved'])
            with patch.object(core,'load_retained',return_value=r):
                self.reject(label,lambda:core.audit_group_prerequisites_HOST('synthetic_partial',model=core.MODEL),rows)
        with patch.object(core,'group_report',side_effect=AssertionError('ALL cases before ANY group')) as gr:
            for label,fn in [
                ('source_omission',lambda c:c['sources'].clear()),
                ('context_gauge',lambda c:c['context']['assignments'][0].__setitem__('terminal_reference_id','foreign')),
                ('point_bool_as_int',lambda c:c['sources'][0].__setitem__('partial_seven_stage_comparison_fits',1)),
                ('group_flag_injection',lambda c:c['sources'][0].__setitem__('group_budget_accepted',True)),
                ('missing_stages_fit',lambda c:c['sources'][0].__setitem__('stage_comparisons',None)),
                ('stage_fit_bool_as_int',lambda c:c['sources'][0]['stage_comparisons']['ideal_material_L1'].__setitem__('fits',1)),
                ('plan_reserve_alias',lambda c:c['allocation_INPUT']['groups'][0]['reserves_L1'].__setitem__('power', [0,1])),
                ('plan_context',lambda c:c['allocation_INPUT'].__setitem__('context_sha256','0'*64)),
                ('material_count_bool',lambda c:c['sources'][0].__setitem__('new_material_operations',False))]:
                mutate(label,fn)
            for label,order in [('duplicate_case_order',['thin_resolved']*3),('omitted_case_order',['thin_resolved'])]:
                r=copy.deepcopy(self.loaded);r[1]['synthetic_partial']['case_order']=order
                with patch.object(core,'load_retained',return_value=r):
                    self.reject(label,lambda:core.audit_group_prerequisites_HOST('synthetic_partial',model=core.MODEL),rows)
            self.assertEqual(gr.call_count,0)
        DATA['atomic_rejections']={'rows':rows,'group_report_calls':0}
    def test_d_identity(self):
        rows=[]
        for label,variant,model in [('unknown','new',core.MODEL),('bool',True,core.MODEL),('wrong_model','real_missing','foreign')]:
            with patch.object(core,'load_retained',side_effect=AssertionError('preflight before loading')) as ld:
                self.reject(label,lambda:core.audit_group_prerequisites_HOST(variant,model=model),rows)
                self.assertEqual(ld.call_count,0)
        with patch.object(core,'PARENT_SHA','0'*64):
            self.reject('parent_SHA',core.load_retained,rows)
        r=copy.deepcopy(self.loaded);r[1]['Horner_zero_FAIL']['retained_INPUT_plan']['sources'][0]['stages_L1']['source_Horner_L1']=[1,1]
        with patch.object(core,'load_retained',return_value=r):
            self.reject('old_FAIL_plan_mutation',lambda:core.audit_group_prerequisites_HOST('Horner_zero_FAIL',model=core.MODEL),rows)
        DATA['identity_rejections']=rows
if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(GroupPrerequisiteTests))
    print(json.dumps({'tests':result.testsRun,'PASS':result.wasSuccessful(),'data':DATA},sort_keys=True))
    raise SystemExit(not result.wasSuccessful())

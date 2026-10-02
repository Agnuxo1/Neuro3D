"""New HOST bridge controls reuse frozen static INPUT plans, never fit new errors."""
import copy,json,sys,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'benchmarks/capacity_audit'))
import axial_guarded_source_budget_bridge_HOST_v1 as core
DATA={}
class BridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.retained=core.load_retained();cls.names=list(cls.retained[0]);cls.plans=copy.deepcopy(cls.retained[-1]['synthetic_INPUT_plans'])
    def reject(self,label,fn,rows):
        try:fn()
        except (ValueError,KeyError,TypeError,IndexError) as e:rows.append({'label':label,'reason':str(e)})
        else:self.fail('expected STOP: '+label)
    def test_a_absent(self):
        with patch.object(core,'load_retained',return_value=self.retained),patch.object(core,'admit_source',side_effect=AssertionError('no missing-plan numerical admission')) as adm,patch.object(core,'compare_source',side_effect=AssertionError('no missing-plan comparison')) as compare:
            a=core.audit_budget_bridge_HOST(self.names,{},model=core.MODEL)
            self.assertEqual(adm.call_count,compare.call_count,0)
        self.assertEqual((a['missing_INPUT_plans_STOP'],a['explicit_INPUT_plans_valid'],a['partial_source_comparisons']),(17,0,0))
        self.assertEqual(sum(len(c['sources']) for c in a['cases'].values()),19)
        DATA['real_missing']=a
    def test_b_retained_INPUT(self):
        before=core.digest(self.retained);DATA['retained_synthetic_INPUT_plans']=copy.deepcopy(self.plans)
        with patch.object(core,'load_retained',return_value=self.retained),patch.object(core.prior,'execute',side_effect=AssertionError('no source product replay')),patch.object(core.prior,'native_cast32',side_effect=AssertionError('no source casts')),patch.object(core.prior,'native_add',side_effect=AssertionError('no native arithmetic')),patch.object(core.prior.prior,'execute',side_effect=AssertionError('no unit replay')),patch.object(core.quotas,'compare_source',side_effect=AssertionError('no old stage evidence substitution')):
            a=core.audit_budget_bridge_HOST(list(self.plans),self.plans,model=core.MODEL)
        self.assertEqual((a['explicit_INPUT_plans_valid'],a['partial_source_comparisons'],a['partial_six_stage_comparisons_fit']),(3,2,2))
        self.assertEqual(core.digest(self.retained),before)
        for c in a['cases'].values():
            self.assertEqual(c['status'],'STOP');self.assertTrue(all(c[n] is False for n in core.FALSE))
            for row in c['sources']:
                self.assertTrue(all(row[n] is False for n in core.FALSE))
                if row['stage_comparisons'] is not None:
                    self.assertEqual(set(row['stage_comparisons']),set(core.MAPPING))
                    self.assertIsNone(row['unexecuted_stages']['ideal_material_L1']['charge_L1'])
                    self.assertIsNone(row['unexecuted_stages']['ideal_material_L1']['fits'])
        DATA['synthetic_partial']=a
        for label,control in [('Horner_zero_FAIL',self.retained[-1]['stage_overspend_control']),('source_zero_FAIL',self.retained[-1]['explicit_zero_FAIL'])]:
            plan=copy.deepcopy(control['INPUT_plan']);name='nonexact_geometry_phase_PASS' if label=='Horner_zero_FAIL' else 'thin_resolved'
            with patch.object(core,'load_retained',return_value=self.retained):
                v=core.audit_budget_bridge_HOST([name],{name:plan},model=core.MODEL)
            row=v['cases'][name]['sources'][0];self.assertFalse(row['partial_six_stage_comparison_fits'])
            if label=='Horner_zero_FAIL':
                self.assertTrue(row['partial_total_fits_source_cap']);self.assertFalse(row['stage_comparisons']['source_Horner_L1']['fits'])
            else:self.assertFalse(row['partial_total_fits_source_cap'])
            DATA[label]={'retained_INPUT_plan':plan,'audit':v}
    def test_c_proof_atomic(self):
        names=['nonexact_geometry_phase_PASS','thin_resolved'];changes=[]
        def change(label,f):
            r=copy.deepcopy(self.retained);f(r);changes.append((label,r))
        def row(r):return r[1]['cases']['thin_resolved']['sources'][0]
        change('second_context',lambda r:r[1]['cases']['thin_resolved']['context'].__setitem__('scene_binding_sha256','0'*64))
        change('foreign_gauge',lambda r:row(r).__setitem__('phase_reference_id','foreign'))
        change('product_word',lambda r:row(r)['result']['product_uint64'].__setitem__(0,row(r)['result']['product_uint64'][0]+1))
        change('product_node',lambda r:row(r)['result']['nodes'][2].__setitem__('output_uint64',row(r)['result']['nodes'][2]['output_uint64']+1))
        change('encoder_word',lambda r:row(r)['result']['source_encoder']['limb_uint32'].__setitem__(0,row(r)['result']['source_encoder']['limb_uint32'][0]+1))
        change('charge_laundering',lambda r:row(r)['result']['detailed_source_charges_L1'].__setitem__('source_encoding_L1',[0,1]))
        change('promotion',lambda r:row(r).__setitem__(core.FALSE[0],True))
        change('integer_false_policy',lambda r:row(r)['result'].__setitem__('material_applied',0))
        change('source_admission',lambda r:row(r)['admission']['ORIGINAL_source_uint64'].__setitem__(0,row(r)['admission']['ORIGINAL_source_uint64'][0]+1))
        rows=[]
        with patch.object(core,'compare_source',side_effect=AssertionError('ALL proofs before any comparisons')) as compare:
            for label,r in changes:
                with patch.object(core,'load_retained',return_value=r):
                    self.reject(label,lambda:core.audit_budget_bridge_HOST(names,{n:self.plans[n] for n in names},model=core.MODEL),rows)
            with patch.object(core,'PREVIOUS_SHA','0'*64):
                self.reject('predecessor_SHA',core.load_retained,rows)
            self.assertEqual(compare.call_count,0)
        DATA['proof_rejections']={'rejections':rows,'partial_comparison_calls':0}
    def test_d_INPUT_and_mapping(self):
        rows=[];names=['nonexact_geometry_phase_PASS','thin_resolved']
        changes=[('second_plan_context',lambda v:v['thin_resolved'].__setitem__('context_sha256','0'*64)),
          ('quota_bool',lambda v:v['thin_resolved']['sources'][0]['stages_L1'].__setitem__('source_Horner_L1',[True,1])),
          ('quota_negative',lambda v:v['thin_resolved']['sources'][0]['stages_L1'].__setitem__('source_Horner_L1',[-1,1])),
          ('missing_material_quota',lambda v:v['thin_resolved']['sources'][0]['stages_L1'].pop('ideal_material_L1')),
          ('output_fitting_injection',lambda v:v['thin_resolved'].__setitem__('expected_output',[0,0]))]
        with patch.object(core,'load_retained',return_value=self.retained),patch.object(core,'admit_source',side_effect=AssertionError('ALL plans before proof inspection')) as adm:
            for label,f in changes:
                plans={n:copy.deepcopy(self.plans[n]) for n in names};f(plans)
                self.reject(label,lambda plans=plans:core.audit_budget_bridge_HOST(names,plans,model=core.MODEL),rows)
            for label,ns,ps,m in [('model',names,{},'bad'),('empty',[],{},core.MODEL),('duplicate',names*2,{},core.MODEL),('unknown',['foreign'],{},core.MODEL),('unused_plan',['thin_resolved'],self.plans,core.MODEL)]:
                self.reject(label,lambda ns=ns,ps=ps,m=m:core.audit_budget_bridge_HOST(ns,ps,model=m),rows)
            self.assertEqual(adm.call_count,0)
        # None is missing, not zero quota or charge.
        with patch.object(core,'load_retained',return_value=self.retained),patch.object(core,'compare_source',side_effect=AssertionError('None no comparison')):
            absent=core.audit_budget_bridge_HOST(['thin_resolved'],{'thin_resolved':None},model=core.MODEL)
        self.assertEqual(absent['missing_INPUT_plans_STOP'],1);DATA['explicit_None_missing']=absent
        source_row=self.retained[1]['cases']['thin_resolved']['sources'][0]
        ev={'charges_L1':copy.deepcopy(source_row['result']['detailed_source_charges_L1']),'partial_bare_source_bound_L1':source_row['result']['point_bare_source_bound_to_FIXED_ORIGINAL_L1']}
        for label,f in [('charge_missing',lambda e:e['charges_L1'].pop('source_encoding_L1')),('charge_negative',lambda e:e['charges_L1'].__setitem__('source_encoding_L1',[-1,1])),('charge_bool',lambda e:e['charges_L1'].__setitem__('source_encoding_L1',[True,1])),('sum_wrong',lambda e:e.__setitem__('partial_bare_source_bound_L1',[0,1]))]:
            e=copy.deepcopy(ev);f(e);self.reject(label,lambda e=e:core.map_charges(e),rows)
        mapping=copy.deepcopy(core.MAPPING);mapping['source_Horner_L1']+=('source_encoding_L1',)
        with patch.object(core,'MAPPING',mapping):self.reject('duplicate_charge_mapping',lambda:core.map_charges(ev),rows)
        DATA['INPUT_mapping_rejections']={'rejections':rows,'numerical_proof_inspections':0}
if __name__=='__main__':
    r=unittest.TextTestRunner(verbosity=2,stream=sys.stderr).run(unittest.defaultTestLoader.loadTestsFromTestCase(BridgeTests))
    print(json.dumps({'PASS':r.wasSuccessful(),'tests':r.testsRun,'data':DATA},sort_keys=True,separators=(',',':'),allow_nan=False))
    raise SystemExit(0 if r.wasSuccessful() else 1)

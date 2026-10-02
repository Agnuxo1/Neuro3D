"""CPU1/60s own reference-scope tests; old cap comparisons and FAILs not replayed."""
import copy,json,sys,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'benchmarks/capacity_audit'))
import axial_SOURCE_phase_reference_scope_gate_HOST_v1 as c
DATA={}
class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.loaded=c.load_retained()
    def audit(self,v,loaded=None):
        with patch.object(c,'load_retained',return_value=self.loaded if loaded is None else loaded):
            return c.audit_reference_scope_HOST(v,model=c.MODEL)
    def scope(self,source,plan):return c.assess_scope_HOST(source,plan,model=c.MODEL)
    def reject(self,label,fn,rows):
        try:fn()
        except (ValueError,KeyError,TypeError,IndexError) as e:rows.append({'label':label,'reason':str(e)})
        else:self.fail('expected reject '+label)
    def test_a_missing(self):
        with patch.object(c,'assess_scope_HOST',side_effect=AssertionError('no scope without INPUT')):
            a=self.audit('real_missing');b=self.audit('explicit_None_missing')
        # Legacy fixtures intentionally have different case orders; do not normalize.
        self.assertEqual(b['case_order'],['thin_resolved'])
        self.assertEqual(c.digest(a['cases']['thin_resolved']['phase_INPUT']),c.digest(b['cases']['thin_resolved']['phase_INPUT']))
        self.assertEqual(len(a['cases']),17);self.assertEqual(sum(len(v['context']['source_order']) for v in a['cases'].values()),19)
        self.assertTrue(all(v['sources'] is None for x in (a,b) for v in x['cases'].values()))
        DATA['real_missing']=a;DATA['explicit_None_missing']=b
    def test_b_immutable_controls_FAILs(self):
        with patch.object(c.prior,'audit_reflected_phase_HOST',side_effect=AssertionError('no old constructor')),patch.object(c.prior.prior.producer,'execute',side_effect=AssertionError('no native producer')):
            audits={v:self.audit(v) for v in ('synthetic_retained','phase_zero_FAIL','Horner_zero_FAIL','source_zero_FAIL')}
        for v,a in audits.items():
            expected=2 if v in ('synthetic_retained','phase_zero_FAIL') else 1
            self.assertEqual((a['reference_scope_assessments'],a['blocked_variable_box_quota_scopes']),(expected,expected))
            self.assertEqual(a['new_numeric_phase_comparisons'],0);self.assertFalse(a['SOURCE_phase_policy_adopted'])
            for name,case in a['cases'].items():
                for row,old in zip(case['sources'],self.loaded[4][v]['cases'][name]['sources']):
                    self.assertEqual(c.digest(row['retained_point_consumer']),c.digest(old))
                    self.assertIsNone(row['uniform_phase_comparison']);self.assertIsNone(row['uniform_phase_INPUT_quota_fits'])
                    if row['scope'] is not None:self.assertFalse(row['scope']['uniform_reference_scope_supported_by_retained_INPUT'])
        for v in ('Horner_zero_FAIL','source_zero_FAIL'):
            self.assertTrue(any(r['retained_point_consumer']['budget'] is not None and not r['retained_point_consumer']['budget']['partial_seven_stage_comparison_fits'] for case in audits[v]['cases'].values() for r in case['sources']))
        self.assertTrue(any(r['retained_point_consumer']['phase_INPUT_quota_fits'] is False for case in audits['phase_zero_FAIL']['cases'].values() for r in case['sources']))
        DATA.update(audits)
    def test_c_scope_controls(self):
        src=copy.deepcopy(self.loaded[1]['synthetic_scene_domains']['cases']['thin_resolved']['domain_INPUT']['sources'][0])
        plan=self.loaded[3]['synthetic_control_INPUT_plans']['thin_resolved']['sources'][0]
        point=copy.deepcopy(src);point['box_reim']=[[copy.deepcopy(x),copy.deepcopy(x)] for x in src['ORIGINAL_anchor_reim']]
        axis=copy.deepcopy(point);axis['box_reim'][1]=copy.deepcopy(src['box_reim'][1])
        controls={'singleton':self.scope(point,plan),'one_axis_variable':self.scope(axis,plan),'retained_box':self.scope(src,plan)}
        self.assertTrue(controls['singleton']['uniform_reference_scope_supported_by_retained_INPUT'])
        self.assertFalse(controls['one_axis_variable']['uniform_reference_scope_supported_by_retained_INPUT'])
        self.assertFalse(controls['retained_box']['uniform_reference_scope_supported_by_retained_INPUT'])
        for p in controls.values():self.assertIsNone(p['uniform_phase_INPUT_quota_fits']);self.assertFalse(p['comparison_performed'])
        DATA['scope_controls']=controls;DATA['scope_control_sources']={'singleton':point,'one_axis_variable':axis,'retained_box':src};DATA['scope_control_phase_INPUT']=plan
    def test_d_types_identity(self):
        src=self.loaded[1]['synthetic_scene_domains']['cases']['thin_resolved']['domain_INPUT']['sources'][0]
        plan=self.loaded[3]['synthetic_control_INPUT_plans']['thin_resolved']['sources'][0];rows=[]
        for name,mut in [
          ('variable_reference_alias',lambda p:p.__setitem__('reference_model','variable-A')),
          ('domain_scope_injection',lambda p:p.__setitem__('domain_sha256','0'*64)),
          ('bool_cap',lambda p:p.__setitem__('cap_rad',[True,1])),
          ('SOURCE_gauge',lambda p:p.__setitem__('source_phase_reference_id','foreign'))]:
            p=copy.deepcopy(plan);mut(p);self.reject(name,lambda:self.scope(src,p),rows)
        bad=copy.deepcopy(src);bad['ORIGINAL_anchor_reim'][0]=[0,1]
        self.reject('anchor_bit_mismatch',lambda:self.scope(bad,plan),rows)
        self.reject('wrong_model',lambda:c.assess_scope_HOST(src,plan,model='foreign'),rows)
        DATA['typed_reference_rejections']=rows
    def test_e_ALL_INPUT_before_scope(self):
        rows=[]
        for name,mut in [
          ('late_phase_INPUT_context',lambda x:x[3]['synthetic_control_INPUT_plans']['two_sources'].__setitem__('context_sha256','0'*64)),
          ('late_phase_INPUT_gauge',lambda x:x[3]['synthetic_control_INPUT_plans']['two_sources']['sources'][-1].__setitem__('terminal_reference_id','foreign')),
          ('late_domain_context',lambda x:x[1]['synthetic_domain_INPUT_plans']['thin_resolved'].__setitem__('context_sha256','0'*64)),
          ('late_conditional_flag_bool',lambda x:x[2]['synthetic_domains']['cases']['thin_resolved']['sources'][0]['proof'].__setitem__(c.prior.FLAG,1)),
          ('late_conditional_phase',lambda x:x[2]['synthetic_domains']['cases']['thin_resolved']['sources'][0]['proof'].__setitem__('conditional_principal_phase_bound_rad',[0,1]))]:
            x=copy.deepcopy(self.loaded);mut(x)
            with patch.object(c,'assess_scope_HOST',side_effect=AssertionError('ALL INPUT first')) as spy:
                self.reject(name,lambda:self.audit('synthetic_retained',x),rows);self.assertEqual(spy.call_count,0)
        with patch.object(c,'PARENT_SHA','0'*64),patch.object(c,'assess_scope_HOST',side_effect=AssertionError('SHA first')) as spy:
            self.reject('parent_SHA',c.load_retained,rows);self.assertEqual(spy.call_count,0)
        DATA['INPUT_SHA_rejections']=rows
if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
    print(json.dumps({'tests':result.testsRun,'PASS':result.wasSuccessful(),'data':DATA},sort_keys=True))
    raise SystemExit(not result.wasSuccessful())

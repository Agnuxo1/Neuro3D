"""CPU1/60s new conditional consumer; immutable INPUT/certificate/FAIL lineage."""
import copy,json,sys,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'benchmarks/capacity_audit'))
import axial_SOURCE_domain_phase_consumer_HOST_v1 as c
DATA={}
class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.loaded=c.load_retained()
    def audit(self,variant,loaded=None):
        with patch.object(c,'load_retained',return_value=self.loaded if loaded is None else loaded):
            return c.audit_consumer_HOST(variant,model=c.MODEL)
    def reject(self,label,fn,rows):
        try:fn()
        except (ValueError,KeyError,TypeError,IndexError) as e:rows.append({'label':label,'reason':str(e)})
        else:self.fail('expected rejection '+label)
    def test_a_missing(self):
        with patch.object(c,'inspect_certificate_HOST',side_effect=AssertionError('no certificate without INPUT')) as ins,patch.object(c,'compare_conditional_HOST',side_effect=AssertionError('no comparison without INPUT')) as cmp:
            a=self.audit('real_missing');b=self.audit('explicit_None_missing');d=self.audit('domain_present_phase_missing')
            self.assertEqual((ins.call_count,cmp.call_count),(0,0))
        self.assertEqual(a['cases'],b['cases']);self.assertEqual(len(a['cases']),17)
        self.assertEqual(sum(len(x['context']['source_order']) for x in a['cases'].values()),19)
        self.assertTrue(all(x['sources'] is None for out in (a,b,d) for x in out['cases'].values()))
        DATA['real_missing']=a;DATA['explicit_None_missing']=b;DATA['domain_present_phase_missing']=d
    def test_b_control_and_zero_FAIL(self):
        with patch.object(c.phase,'reflected_phase_HOST',side_effect=AssertionError('no producer bound')),patch.object(c.phase,'audit_reflected_phase_HOST',side_effect=AssertionError('no old audit')),patch.object(c.phase.prior.producer,'execute',side_effect=AssertionError('no native SOURCE')):
            a=self.audit('synthetic_valid');b=self.audit('synthetic_zero_valid')
        self.assertEqual((a['conditional_certificate_inspections'],a['new_conditional_phase_comparisons'],a['conditional_fit_count'],a['conditional_fail_count']),(2,2,2,0))
        self.assertEqual((b['conditional_certificate_inspections'],b['new_conditional_phase_comparisons'],b['conditional_fit_count'],b['conditional_fail_count']),(2,2,0,2))
        for out in (a,b):
            self.assertEqual(out['missing_conditional_certificate_sources'],2)
            self.assertFalse(out['SOURCE_phase_policy_adopted']);self.assertEqual(out['group_admissions'],0)
            for n,row in out['cases'].items():
                self.assertIsNone(row['group_phase_bound_rad']);self.assertIsNone(row['group_field_bound_L1'])
                for s in row['sources']:
                    self.assertIsNone(s['uniform_phase_INPUT_quota_fits']);self.assertEqual(s['status'],'STOP')
                    self.assertTrue(all(s[k] is False and s['conditional_comparison'][k] is False for k in c.FALSE))
                    if n=='two_sources':
                        self.assertIsNone(s['conditional_certificate']);self.assertIsNone(s['whole_box_guard_admission_disproved'])
                        self.assertIsNone(s['conditional_comparison']['conditional_phase_quota_fits'])
                    else:self.assertIs(s['whole_box_guard_admission_disproved'],True)
        DATA['synthetic_valid']=a;DATA['synthetic_zero_valid']=b
    def test_c_exact_boundaries(self):
        controls={n:c.compare_conditional_HOST(b,q,model=c.MODEL) for n,b,q in (
            ('below',[1,3],[1,2]),('equal',[1,2],[1,2]),('above',[2,3],[1,2]),
            ('zero_hypothesis',[0,1],[0,1]),('absent',None,[0,1]))}
        self.assertEqual([x['conditional_phase_quota_fits'] for x in controls.values()],[True,True,False,True,None])
        self.assertTrue(all(x['uniform_phase_INPUT_quota_fits'] is x['uniform_executed_SOURCE_error_L1'] is None for x in controls.values()))
        rows=[]
        for n,b,q in (('bool_bound',[True,1],[0,1]),('bool_cap',[0,1],[0,True]),
            ('negative_bound',[-1,1],[0,1]),('negative_cap',[0,1],[-1,1]),
            ('float',[0.0,1],[0,1]),('noncanonical',[0,2],[0,1]),('oversized',[1,1<<4097],[0,1])):
            self.reject(n,lambda:c.compare_conditional_HOST(b,q,model=c.MODEL),rows)
        self.reject('wrong_model',lambda:c.compare_conditional_HOST([0,1],[0,1],model='foreign'),rows)
        DATA['boundary_controls']=controls;DATA['typed_comparison_rejections']=rows
    def test_d_ALL_INPUT_before_inspection(self):
        rows=[]
        for label,mut in [
            ('late_context',lambda x:x[1]['synthetic_control_INPUT_plans']['two_sources'].__setitem__('context_sha256','0'*64)),
            ('late_domainSHA',lambda x:x[1]['synthetic_control_INPUT_plans']['two_sources'].__setitem__('domain_sha256','0'*64)),
            ('late_SOURCEgauge',lambda x:x[1]['synthetic_control_INPUT_plans']['two_sources']['sources'][-1].__setitem__('source_phase_reference_id','foreign')),
            ('late_boolcap',lambda x:x[1]['synthetic_control_INPUT_plans']['two_sources']['sources'][-1].__setitem__('cap_rad',[True,1])),
            ('late_retained_INPUT',lambda x:x[1]['synthetic_valid']['cases']['two_sources']['INPUT']['sources'][-1].__setitem__('cap_rad',[0,1])),
            ('late_domainbox',lambda x:x[1]['synthetic_domain_INPUT_plans']['two_sources']['sources'][-1]['box_reim'][0].__setitem__(1,[99,1]))]:
            x=copy.deepcopy(self.loaded);mut(x)
            with patch.object(c,'inspect_certificate_HOST',side_effect=AssertionError('INPUT first')) as ins,patch.object(c,'compare_conditional_HOST',side_effect=AssertionError('INPUT first')) as cmp:
                self.reject(label,lambda:self.audit('synthetic_valid',x),rows);self.assertEqual((ins.call_count,cmp.call_count),(0,0))
        with patch.object(c,'PARENT_SHA','0'*64):self.reject('parent_SHA',c.load_retained,rows)
        DATA['INPUT_rejections']=rows
    def test_e_ALL_certificates_before_comparison(self):
        rows=[]
        def source(x):return x[2]['synthetic_domains']['cases']['thin_resolved']['sources'][0]
        mutations=[
            ('cert_context',lambda x:x[2]['synthetic_domains']['cases']['thin_resolved'].__setitem__('context',{})),
            ('source_identity',lambda x:source(x).__setitem__('source_id','foreign')),
            ('domainSHA',lambda x:source(x).__setitem__('domain_source_sha256','0'*64)),
            ('guard_bool',lambda x:source(x).__setitem__('whole_box_guard_admission_disproved',1)),
            ('guard_relaxed',lambda x:source(x).__setitem__('whole_box_guard_admission_disproved',False)),
            ('point_reference',lambda x:source(x)['proof'].__setitem__('reference','fixed-A')),
            ('proof_model',lambda x:source(x)['proof'].__setitem__('model','foreign')),
            ('conditional_flag',lambda x:source(x)['proof'].__setitem__(c.phase.FLAG,1)),
            ('actual_error_zero',lambda x:source(x)['proof'].__setitem__('uniform_executed_SOURCE_error_L1',[0,1])),
            ('material_execution',lambda x:source(x)['proof'].__setitem__('material_executed',True)),
            ('unwrapped',lambda x:source(x)['proof'].__setitem__('unwrapped_phase_proved',True)),
            ('phase_policy',lambda x:source(x)['proof'].__setitem__('phase_INPUT_quota_fits',True)),
            ('forged_phase',lambda x:source(x)['proof'].__setitem__('conditional_principal_phase_bound_rad',[0,1])),
            ('radial_margin',lambda x:source(x)['proof'].__setitem__('positive_radial_projection_lower_bound',[0,1])),
            ('model_material_charge',lambda x:source(x)['proof']['fifteen_conditional_reflected_charges_L1'].__setitem__('ideal_material_exact_model_L1',[1,1])),
            ('dependency_SHA',lambda x:source(x).__setitem__('retained_material_admission_SOURCE_sha256','foreign')),
            ('omitted_cert',lambda x:x[2]['synthetic_domains']['cases']['thin_resolved']['sources'].pop())]
        for label,mut in mutations:
            x=copy.deepcopy(self.loaded);mut(x)
            with patch.object(c,'compare_conditional_HOST',side_effect=AssertionError('ALL certificates first')) as cmp:
                self.reject(label,lambda:self.audit('synthetic_valid',x),rows);self.assertEqual(cmp.call_count,0)
        DATA['certificate_rejections']=rows
if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
    print(json.dumps({'tests':result.testsRun,'PASS':result.wasSuccessful(),'data':DATA},sort_keys=True))
    raise SystemExit(not result.wasSuccessful())

"""New consumer executes only HOST comparisons of immutable synthetic INPUT controls."""
import copy,json,sys,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'benchmarks/capacity_audit'))
import axial_SOURCE_phase_quota_consumer_HOST_v1 as core
DATA={}
class PhaseQuotaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.loaded=core.load_retained()
    def audit(self,v):return core.audit_quota_consumer_HOST(v,model=core.MODEL)
    def reject(self,label,fn,rows):
        try:fn()
        except (ValueError,KeyError,TypeError,IndexError,StopIteration) as e:rows.append({'label':label,'reason':str(e)})
        else:self.fail('expected reject '+label)
    def test_a_missing(self):
        with patch.object(core,'load_retained',return_value=self.loaded),patch.object(core,'inspect_certificate',side_effect=AssertionError('no certificate without INPUT')) as ins,patch.object(core,'compare_phase',side_effect=AssertionError('no comparison without INPUT')) as cmp:
            a=self.audit('real_missing');b=self.audit('explicit_None_missing')
            self.assertEqual((ins.call_count,cmp.call_count),(0,0))
        self.assertEqual(len(a['cases']),17);self.assertEqual(sum(len(c['sources']) for c in a['cases'].values()),19)
        for x in (a,b):
            self.assertEqual(x['point_phase_comparisons'],0)
            self.assertTrue(all(s['phase_comparison'] is s['phase_INPUT_quota_fits'] is s['budget'] is None for c in x['cases'].values() for s in c['sources']))
        DATA['real_missing']=a;DATA['explicit_None_missing']=b
    def test_b_controls_and_FAILs(self):
        with patch.object(core,'load_retained',return_value=self.loaded),patch.object(core.prior,'audit_phase_budget_consumer_HOST',side_effect=AssertionError('no old suite/consumer replay')),patch.object(core.phase,'audit_source_phase_HOST',side_effect=AssertionError('no old phase suite')),patch.object(core.phase.prior.prior,'execute',side_effect=AssertionError('no native operation')):
            audits={v:self.audit(v) for v in ('synthetic_retained','phase_zero_FAIL','Horner_zero_FAIL','source_zero_FAIL')}
        a=audits['synthetic_retained'];z=audits['phase_zero_FAIL']
        self.assertEqual((a['point_phase_comparisons'],a['point_phase_quota_fits']),(2,2))
        self.assertEqual((z['point_phase_comparisons'],z['point_phase_quota_fits']),(2,0))
        for x in audits.values():
            self.assertEqual(x['group_admissions'],0);self.assertFalse(x['SOURCE_phase_policy_adopted'])
            for c in x['cases'].values():
                self.assertTrue(all(c[k] is False for k in core.FALSE))
                for g in c['groups']:
                    self.assertEqual(g['status'],'STOP');self.assertIsNone(g['group_phase_bound_rad']);self.assertIsNone(g['group_field_uint64'])
                    self.assertIn('reduction_error_unproved',g['blockers']);self.assertIn('uniform_SOURCE_enclosure_unproved',g['blockers'])
        for v in ('Horner_zero_FAIL','source_zero_FAIL'):
            s=next(iter(audits[v]['cases'].values()))['sources'][0]
            self.assertTrue(s['phase_INPUT_quota_fits']);self.assertFalse(s['budget']['partial_seven_stage_comparison_fits'])
        for s in a['cases']['two_sources']['sources']:
            self.assertFalse(s[core.FLAG]);self.assertIsNone(s['phase_INPUT_quota_fits'])
        DATA.update(audits)
    def test_c_INPUT_atomic(self):
        rows=[]
        def p(r):return r[4]['synthetic_control_INPUT_plans']['thin_resolved']
        mutations=[
            ('late_phase_context',lambda r:p(r).__setitem__('context_sha256','0'*64)),
            ('late_phase_source_omission',lambda r:p(r)['sources'].clear()),
            ('late_phase_units',lambda r:p(r).__setitem__('units','UNIT-rad')),
            ('late_phase_bool',lambda r:p(r)['sources'][0].__setitem__('cap_rad',[True,1])),
            ('late_phase_reference',lambda r:p(r)['sources'][0].__setitem__('source_phase_reference_id','foreign')),
            ('late_stage_context',lambda r:r[2]['synthetic_partial']['cases']['thin_resolved']['allocation_INPUT'].__setitem__('context_sha256','0'*64)),
            ('late_stage_source_omission',lambda r:r[2]['synthetic_partial']['cases']['thin_resolved']['sources'].clear()),
            ('late_current_context',lambda r:r[3]['synthetic_partial']['cases']['thin_resolved']['context'].__setitem__('scene_binding_sha256','0'*64))]
        with patch.object(core,'inspect_certificate',side_effect=AssertionError('all INPUT before inspection')) as ins,patch.object(core,'compare_phase',side_effect=AssertionError('all INPUT before comparison')) as cmp:
            for label,mut in mutations:
                r=copy.deepcopy(self.loaded);mut(r)
                with patch.object(core,'load_retained',return_value=r):self.reject(label,lambda:self.audit('synthetic_retained'),rows)
            self.assertEqual((ins.call_count,cmp.call_count),(0,0))
        DATA['INPUT_rejections']={'rows':rows,'certificate_inspections':0,'numeric_phase_comparisons':0}
    def test_d_certificates_atomic_typed(self):
        rows=[]
        def c(r):return r[1]['cases']['thin_resolved']['sources'][0]
        mutations=[
            ('phase_bound_forged',lambda r:c(r)['proof'].__setitem__('point_principal_phase_distance_bound_rad',[0,1])),
            ('amplitude_words_bool',lambda r:c(r)['proof']['ORIGINAL_source_uint64'].__setitem__(0,True)),
            ('source_reference',lambda r:c(r).__setitem__('phase_reference_id','foreign')),
            ('terminal_reference',lambda r:c(r).__setitem__('terminal_reference_id','foreign')),
            ('epsilon_forged',lambda r:c(r)['proof'].__setitem__('point_reflected_error_L1',[0,1])),
            ('margin_bool',lambda r:c(r)['proof'].__setitem__('positive_radial_projection_lower_bound',[True,1])),
            ('unwrapped_bool_as_int',lambda r:c(r)['proof'].__setitem__('unwrapped_phase_proved',0)),
            ('zero_canonicalization_int',lambda r:c(r)['proof'].__setitem__('zero_canonicalization_performed',0)),
            ('phase_INPUT_invented',lambda r:c(r)['proof'].__setitem__('phase_INPUT_quota_fits',True)),
            ('eligibility_int',lambda r:c(r).__setitem__(core.phase.FLAG,1))]
        with patch.object(core,'compare_phase',side_effect=AssertionError('all certificates before ANY compare')) as cmp:
            for label,mut in mutations:
                r=copy.deepcopy(self.loaded);mut(r)
                # Change matching cached SHA to test proof revalidation, not merely first identity hash.
                cert=c(r);r[3]['synthetic_partial']['cases']['thin_resolved']['sources'][0]['phase_certificate_sha256']=core.digest(cert)
                with patch.object(core,'load_retained',return_value=r):self.reject(label,lambda:self.audit('synthetic_retained'),rows)
            self.assertEqual(cmp.call_count,0)
        DATA['certificate_rejections']={'rows':rows,'numeric_phase_comparisons':0}
    def test_e_boundaries(self):
        rows=[]
        with patch.object(core,'load_retained',side_effect=AssertionError('preflight')):
            self.reject('model',lambda:core.audit_quota_consumer_HOST('synthetic_retained',model='foreign'),rows)
            self.reject('variant',lambda:core.audit_quota_consumer_HOST('foreign',model=core.MODEL),rows)
        with patch.object(core,'PARENT_SHA','0'*64):self.reject('parent_SHA',core.load_retained,rows)
        DATA['boundary_rejections']=rows
if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(PhaseQuotaTests))
    print(json.dumps({'tests':result.testsRun,'PASS':result.wasSuccessful(),'data':DATA},sort_keys=True))
    raise SystemExit(not result.wasSuccessful())

"""All INPUT/certificates before compares, no missing phase INPUT promotion."""
import copy,json,sys,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'benchmarks/capacity_audit'))
import axial_phase_budget_consumer_HOST_v1 as core
DATA={}
class PhaseConsumerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.loaded=core.load_retained()
    def reject(self,label,fn,rows):
        try:fn()
        except (ValueError,KeyError,TypeError,IndexError,StopIteration) as e:rows.append({'label':label,'reason':str(e)})
        else:self.fail('expected STOP '+label)
    def test_a_missing(self):
        with patch.object(core,'load_retained',return_value=self.loaded),patch.object(core,'inspect_certificate',side_effect=AssertionError('no proof without INPUT')) as inspect:
            a=core.audit_phase_budget_consumer_HOST('real_missing',model=core.MODEL)
            none=core.audit_phase_budget_consumer_HOST('explicit_None_missing',model=core.MODEL)
            self.assertEqual(inspect.call_count,0)
        self.assertEqual((len(a['cases']),a['certificates_consumed']),(17,0))
        self.assertEqual(sum(len(c['sources']) for c in a['cases'].values()),19)
        self.assertTrue(all(r['budget'] is None for c in a['cases'].values() for r in c['sources']))
        DATA['real_missing']=a;DATA['explicit_None_missing']=none
    def test_b_consumption(self):
        with patch.object(core,'load_retained',return_value=self.loaded),patch.object(core.phase,'audit_source_phase_HOST',side_effect=AssertionError('no prior suite/proof outputs replay')),patch.object(core.phase.prior.prior,'execute',side_effect=AssertionError('no native execution')):
            a=core.audit_phase_budget_consumer_HOST('synthetic_partial',model=core.MODEL)
            h=core.audit_phase_budget_consumer_HOST('Horner_zero_FAIL',model=core.MODEL)
            z=core.audit_phase_budget_consumer_HOST('source_zero_FAIL',model=core.MODEL)
        self.assertEqual((a['certificates_consumed'],a['partial_seven_stage_fits']),(2,2))
        for audit in (a,h,z):
            self.assertEqual(audit['group_admissions'],0)
            for c in audit['cases'].values():
                for g in c['groups']:
                    self.assertEqual(g['status'],'STOP');self.assertIsNone(g['phase_INPUT_quota_fits'])
                    self.assertIn('missing_explicit_SOURCE_phase_INPUT',g['blockers'])
                    self.assertIsNone(g['executed_reduction_charge_L1']);self.assertIsNone(g['group_field_uint64'])
                    self.assertTrue(all(g[n] is False for n in core.FALSE))
        self.assertEqual(a['cases']['two_sources']['groups'][0]['missing_source_certificates'],['s','other'])
        for v in (h,z):
            row=next(iter(v['cases'].values()))['sources'][0]
            self.assertTrue(row[core.FLAG]);self.assertFalse(row['budget']['partial_seven_stage_comparison_fits'])
        DATA['synthetic_partial']=a;DATA['Horner_zero_FAIL']=h;DATA['source_zero_FAIL']=z
    def test_c_INPUT_atomic(self):
        rejected=[]
        with patch.object(core,'inspect_certificate',side_effect=AssertionError('all INPUT before certificate')) as ins:
            for label,fn in [
                ('late_INPUT_context',lambda r:r[2]['synthetic_partial']['cases']['thin_resolved']['allocation_INPUT'].__setitem__('context_sha256','0'*64)),
                ('late_source_omission',lambda r:r[2]['synthetic_partial']['cases']['thin_resolved']['sources'].clear()),
                ('late_phase_context',lambda r:r[1]['cases']['thin_resolved']['context'].__setitem__('scene_binding_sha256','0'*64)),
                ('late_plan_units',lambda r:r[0][0][-1]['synthetic_INPUT_plans']['thin_resolved'].__setitem__('units','power')),
                ('phase_case_missing_source',lambda r:r[1]['cases']['thin_resolved']['sources'].clear())]:
                r=copy.deepcopy(self.loaded);fn(r)
                with patch.object(core,'load_retained',return_value=r):
                    self.reject(label,lambda:core.audit_phase_budget_consumer_HOST('synthetic_partial',model=core.MODEL),rejected)
            self.assertEqual(ins.call_count,0)
        DATA['INPUT_rejections']={'rows':rejected,'certificate_inspection_calls':0}
    def test_d_certificate_atomic(self):
        rejected=[]
        def row(r):return r[1]['cases']['thin_resolved']['sources'][0]
        with patch.object(core.budget,'compare_source',side_effect=AssertionError('all certificates before ANY comparison')) as compare:
            for label,fn in [
                ('phase_bound_forged',lambda r:row(r)['proof'].__setitem__('point_principal_phase_distance_bound_rad',[0,1])),
                ('reference_forged',lambda r:row(r).__setitem__('phase_reference_id','foreign')),
                ('point_error_forged',lambda r:row(r)['proof'].__setitem__('point_reflected_error_L1',[0,1])),
                ('phase_INPUT_fits_invented',lambda r:row(r)['proof'].__setitem__('phase_INPUT_quota_fits',True)),
                ('ORIGINAL_words_forged',lambda r:row(r)['proof']['ORIGINAL_source_uint64'].__setitem__(0,0)),
                ('margin_bool',lambda r:row(r)['proof'].__setitem__('positive_radial_projection_lower_bound',[True,1])),
                ('eligibility_as_int',lambda r:row(r).__setitem__(core.phase.FLAG,1))]:
                r=copy.deepcopy(self.loaded);fn(r)
                with patch.object(core,'load_retained',return_value=r):
                    self.reject(label,lambda:core.audit_phase_budget_consumer_HOST('synthetic_partial',model=core.MODEL),rejected)
            self.assertEqual(compare.call_count,0)
        for label,v,m in [('variant','foreign',core.MODEL),('model','real_missing','foreign')]:
            with patch.object(core,'load_retained',side_effect=AssertionError('preflight')):
                self.reject(label,lambda v=v,m=m:core.audit_phase_budget_consumer_HOST(v,model=m),rejected)
        with patch.object(core,'PARENT_SHA','0'*64):self.reject('parent_SHA',core.load_retained,rejected)
        DATA['certificate_identity_rejections']={'rows':rejected,'budget_compare_calls':0}
if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(PhaseConsumerTests))
    print(json.dumps({'tests':result.testsRun,'PASS':result.wasSuccessful(),'data':DATA},sort_keys=True))
    raise SystemExit(not result.wasSuccessful())

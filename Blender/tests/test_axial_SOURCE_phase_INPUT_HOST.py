"""Typed SOURCE phase schema controls are synthetic, not fitted real INPUT."""
import copy,json,sys,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'benchmarks/capacity_audit'))
import axial_SOURCE_phase_INPUT_HOST_v1 as core
DATA={}
CAP=[1,1000000000000] # Literal schema CONTROL, not inherited UNIT cap or output-derived policy.
ZERO=[0,1]
class PhaseINPUTTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packets,cls.budgets,cls.pins=core.load_retained()
        cls.names=list(cls.budgets['synthetic_partial']['case_order'])
        cls.real=list(cls.budgets['real_missing']['case_order'])
        cls.plans={}
        for name in cls.names:
            ctx=cls.budgets['synthetic_partial']['cases'][name]['context']
            cls.plans[name]={'model':core.MODEL,'units':core.UNITS,'context_sha256':core.digest(ctx),
                'sources':[{'source_id':a['source_id'],'source_phase_reference_id':a['source_phase_reference_id'],
                    'terminal_reference_id':a['terminal_reference_id'],'common_terminal_reference_id':a['common_terminal_reference_id'],
                    'reference_model':core.REFERENCE,'cap_rad':CAP.copy()} for a in ctx['assignments']]}
        DATA['synthetic_control_INPUT_plans']=copy.deepcopy(cls.plans)
    def audit(self,names,plans):
        return core.audit_INPUT_HOST(names,plans,self.packets,model=core.MODEL)
    def reject(self,label,fn,rows):
        try:fn()
        except (ValueError,KeyError,TypeError,IndexError) as e:rows.append({'label':label,'reason':str(e)})
        else:self.fail('expected rejection '+label)
    def test_a_missing(self):
        a=self.audit(self.real,{})
        b=self.audit(self.real,{n:None for n in self.real})
        self.assertEqual(a,b);self.assertEqual((a['valid_INPUT_cases'],a['missing_INPUT_cases']),(0,17))
        self.assertEqual(sum(len(c['context']['source_order']) for c in a['cases'].values()),19)
        self.assertTrue(all(c['INPUT']['sources'] is c['INPUT']['phase_INPUT_quota_fits'] is None for c in a['cases'].values()))
        DATA['real_missing']=a;DATA['explicit_None_missing']=b
    def test_b_controls(self):
        with patch.object(core.prior,'inspect_certificate',side_effect=AssertionError('no certificate inspection')) as ins,patch.object(core.prior.budget,'compare_source',side_effect=AssertionError('no numeric comparison')) as cmp,patch.object(core.prior.phase.prior.prior,'execute',side_effect=AssertionError('no native execution')):
            a=self.audit(self.names,self.plans)
            zero=copy.deepcopy(self.plans)
            for p in zero.values():
                for s in p['sources']:s['cap_rad']=ZERO.copy()
            b=self.audit(self.names,zero)
            self.assertEqual((ins.call_count,cmp.call_count),(0,0))
        self.assertEqual(a['valid_INPUT_cases'],3);self.assertEqual(b['valid_INPUT_cases'],3)
        self.assertEqual(len(a['cases']['two_sources']['INPUT']['sources']),2)
        for audit in (a,b):
            self.assertEqual(audit['group_admissions'],0)
            self.assertFalse(audit['SOURCE_phase_policy_adopted'])
            self.assertTrue(all(c['INPUT']['phase_INPUT_quota_fits'] is None and c['status']=='STOP' for c in audit['cases'].values()))
            self.assertTrue(all(c[k] is False and c['INPUT'][k] is False for c in audit['cases'].values() for k in core.FALSE))
        DATA['synthetic_valid']=a;DATA['synthetic_zero_INPUT_plans']=zero;DATA['synthetic_zero_valid']=b
    def test_c_rationals(self):
        bad=[('bool_num',[True,1]),('bool_den',[1,True]),('float',[1.0,1]),('negative',[-1,1]),
             ('den_zero',[0,0]),('den_negative',[1,-1]),('noncanonical',[2,2]),('zero_noncanonical',[0,2]),
             ('tuple',(1,2)),('missing',None),('string','0'),('scalar',0),('extra',[0,1,2])]
        rows=[]
        for label,cap in bad:
            plans=copy.deepcopy(self.plans);plans['two_sources']['sources'][1]['cap_rad']=cap
            self.reject(label,lambda:self.audit(self.names,plans),rows)
        DATA['rational_rejections']=rows
    def test_d_identity_and_atomic(self):
        rows=[]
        def row(plans):return plans['two_sources']['sources'][1]
        mutations=[
            ('source',lambda p:row(p).__setitem__('source_id','s')),
            ('source_phase',lambda p:row(p).__setitem__('source_phase_reference_id','foreign')),
            ('terminal',lambda p:row(p).__setitem__('terminal_reference_id','foreign')),
            ('common_terminal',lambda p:row(p).__setitem__('common_terminal_reference_id','foreign')),
            ('reference_MODEL',lambda p:row(p).__setitem__('reference_model','UNIT')),
            ('cap_alias',lambda p:row(p).__setitem__('UNIT_cap_rad',CAP)),
            ('forged_PASS',lambda p:row(p).__setitem__('phase_INPUT_quota_fits',True)),
            ('omission',lambda p:p['two_sources']['sources'].pop()),
            ('order',lambda p:p['two_sources']['sources'].reverse()),
            ('context',lambda p:p['two_sources'].__setitem__('context_sha256','0'*64)),
            ('units',lambda p:p['two_sources'].__setitem__('units','UNIT-phase-rad')),
            ('model',lambda p:p['two_sources'].__setitem__('model','foreign')),
            ('expected_output',lambda p:p['two_sources'].__setitem__('expected_output',0))]
        with patch.object(core.prior,'inspect_certificate',side_effect=AssertionError('no inspection')) as ins,patch.object(core.prior.budget,'compare_source',side_effect=AssertionError('no comparisons')) as cmp:
            for label,fn in mutations:
                plans=copy.deepcopy(self.plans);fn(plans)
                self.reject(label,lambda:self.audit(self.names,plans),rows)
            self.assertEqual((ins.call_count,cmp.call_count),(0,0))
        DATA['identity_rejections']={'rows':rows,'certificate_inspections':0,'numeric_phase_comparisons':0}
    def test_e_boundary_and_copy(self):
        rows=[]
        for label,fn in [
            ('wrong_model',lambda:core.audit_INPUT_HOST(self.names,self.plans,self.packets,model='foreign')),
            ('duplicate_case',lambda:self.audit(self.names+[self.names[-1]],self.plans)),
            ('foreign_plan_case',lambda:self.audit(self.names,{**self.plans,'foreign':None})),
            ('bad_packet_SHA',lambda:core.validate_plan(self.packets[self.names[0]],'0'*64,None,model=core.MODEL)),
            ('duplicate_json_key',lambda:core.allocation.parse('{"cap_rad":[0,1],"cap_rad":[1,1]}')),
            ('nonfinite_json',lambda:core.allocation.parse('{"cap_rad":NaN}'))]:
            self.reject(label,fn,rows)
        p=copy.deepcopy(self.plans);a=self.audit(self.names,p)
        p[self.names[0]]['sources'][0]['cap_rad'][0]=999
        self.assertEqual(a['cases'][self.names[0]]['INPUT']['sources'][0]['cap_rad'],CAP)
        with patch.object(core,'PARENT_SHA','0'*64):self.reject('parent_SHA',core.load_retained,rows)
        DATA['boundary_rejections']=rows
if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(PhaseINPUTTests))
    print(json.dumps({'tests':result.testsRun,'PASS':result.wasSuccessful(),'data':DATA},sort_keys=True))
    raise SystemExit(not result.wasSuccessful())

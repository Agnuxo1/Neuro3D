"""New bounded retained-power domain tests; no scene/RN producer replay."""
import copy,json,sys,unittest
from fractions import Fraction as F
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'benchmarks/capacity_audit'))
import axial_singleton_power_domain_HOST_v1 as core
DATA={}
class PowerDomainTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packets,cls.old,cls.power,cls.red,cls.reflected,cls.pins=core.load_retained()
        cls.n='positive';cls.packet=cls.packets[cls.n];cls.ctx=cls.old['cases'][cls.n]['context']
        cls.g=cls.old['cases'][cls.n]['groups'][0];cls.pc=cls.power['explicit_synthetic_INPUT_controls']['cases'][cls.n]
        cls.rc=cls.red[cls.n];cls.fc=cls.reflected['cases'][cls.n]
    def test_audit(self):
        a=core.audit_singleton_power_domain_HOST(self.old['case_order'],model=core.MODEL);DATA['audit']=a
        self.assertEqual((a['restricted_complete_singleton_power_groups_proved'],a['blocked_complete_groups'],a['retained_RN_cell_checks']),(2,15,24))
        self.assertEqual(a['inherited_pins_verified'],288)
        self.assertEqual((a['retained_unit_STOPs'],a['nonzero_domains_not_refined']),(14,2))
        for n,c in a['cases'].items():
            for g in c['groups']:
                for k in core.FALSE:self.assertIs(g[k],False)
                self.assertEqual(g['status'],'STOP');self.assertFalse(g['power_budget_evaluated'])
                if 'proof' in g:
                    self.assertIn(n,['positive','negative'])
                    p=g['proof'];self.assertTrue(p['missing_allocation_NOT_promoted'])
                    self.assertTrue(p['synthetic_power_budget_admission_NOT_inherited'])
                    self.assertGreater(core.number(p['uniform_exact_absolute_power_error']),0)
                    self.assertGreater(core.number(p['fixed_ORIGINAL_power_exact']),0)
                    self.assertLessEqual(core.number(p['uniform_exact_absolute_power_error']),core.number(p['retained_conservative_absolute_power_bound']))
                    self.assertEqual(len(p['retained_corner_checks']),4)
        g=a['cases']['two_sources']['groups'][0]
        self.assertEqual(g['source_order'],['s','other']);self.assertEqual(g['blocked_source_ids'],['other']);self.assertNotIn('proof',g)
        self.assertEqual(a['retained_zero_budget_FAIL_controls']['zero_absolute']['positive']['group_statuses'],['FAIL'])
        self.assertEqual(a['new_RN_or_copy_or_scene_producer_executions'],0)
    def test_single_group(self):
        p=core.power_domain_proof(self.packet,self.ctx,self.g,self.pc,self.rc,self.fc);DATA['single_group']=p
        self.assertEqual(p['complete_source_order'],['s'])
        self.assertEqual(core.number(p['uniform_exact_relative_power_error']),
                         core.number(p['uniform_exact_absolute_power_error'])/core.number(p['fixed_ORIGINAL_power_exact']))
    def test_synthetic_cells(self):
        w=0x3ff0000000000000;v=core.decode(w)
        lo=(core.decode(w-1)+v)/2;hi=(v+core.decode(w+1))/2
        DATA['SYNTHETIC_cell_controls']=[core.rn_cell(v,w),core.rn_cell(lo,w),core.rn_cell(hi,w),core.rn_cell(F(0),0)]
        self.assertTrue(DATA['SYNTHETIC_cell_controls'][1]['ties_included'])
        self.assertTrue(DATA['SYNTHETIC_cell_controls'][-1]['exact_zero_identity'])
    def test_rejections(self):
        rejected=[];DATA['rejections']=rejected
        def reject(label,fn):
            with self.assertRaises((ValueError,TypeError,KeyError,IndexError)) as cm:fn()
            rejected.append({'label':label,'reason':str(cm.exception)})
        for label,n,m in [('model',['positive'],'wrong'),('empty',[],core.MODEL),('duplicate',['positive','positive'],core.MODEL),
                          ('boolcase',[False],core.MODEL),('tuple',('positive',),core.MODEL),('unknown',['other'],core.MODEL)]:
            reject(label,lambda n=n,m=m:core.audit_singleton_power_domain_HOST(n,model=m))
        w=0x3ff0000000000000
        midpoint=(core.decode(w)+core.decode(w+1))/2
        for label,q,out in [('odd_midpoint',midpoint,w+1),('outside_cell',F(2),w),('signed_zero',F(0),2**63),
                            ('bool_word',F(0),False),('nonfinite_word',F(1),0x7ff0000000000000),
                            ('zero_FTZ',F(1,2**1075),0),('negative_exact',F(-1),w)]:
            reject(label,lambda q=q,out=out:core.rn_cell(q,out))
        for label,mut in [
            ('group_domain_absent',lambda g:g.__setitem__(core.group.FLAG,False)),
            ('group_admitted',lambda g:g.__setitem__('status','PASS')),
            ('partial_two_sources',lambda g:g.__setitem__('source_order',['s','other'])),
            ('reduction_group_sha',lambda g:g['proof'].__setitem__('retained_reduction_group_sha256','0'*64)),
            ('reflected_source_sha',lambda g:g['proof'].__setitem__('retained_reflected_source_row_sha256','0'*64)),
            ('field_error_hidden',lambda g:g['proof'].__setitem__('uniform_group_L1_error_to_fixed_ORIGINAL_bound',[0,1])),
            ('copy_corner_missing',lambda g:g['proof']['retained_copy_identities'].pop()),
            ('copy_word_zero_sign',lambda g:g['proof']['retained_copy_identities'][0]['retained_copy_uint64'].__setitem__(1,0))]:
            g=copy.deepcopy(self.g);mut(g)
            reject(label,lambda g=g:core.power_domain_proof(self.packet,self.ctx,g,self.pc,self.rc,self.fc))
        for label,mut in [
            ('power_context',lambda p:p['context'].__setitem__('word_ABI_sha256','0'*64)),
            ('power_group_order',lambda p:p['groups'][0].__setitem__('port','other')),
            ('power_source_order',lambda p:p['groups'][0].__setitem__('source_order',['other'])),
            ('power_reduction_sha',lambda p:p['groups'][0].__setitem__('retained_group_row_sha256','0'*64)),
            ('power_limit_changed',lambda p:p['groups'][0]['unchanged_original_limits'].__setitem__('power',[1,1])),
            ('power_corner_missing',lambda p:p['groups'][0]['power_corners'].pop()),
            ('power_field_corner_sha',lambda p:p['groups'][0]['power_corners'][0].__setitem__('retained_field_corner_sha256','0'*64)),
            ('power_trace_missing',lambda p:p['groups'][0]['power_corners'][0]['trace'].pop()),
            ('power_RN_bool',lambda p:p['groups'][0]['power_corners'][0].__setitem__('RN64_operations',True)),
            ('power_op_changed',lambda p:p['groups'][0]['power_corners'][0]['trace'][0].__setitem__('op','add')),
            ('power_output_wrong_cell',lambda p:p['groups'][0]['power_corners'][0]['trace'][0].__setitem__('output_uint64',4576918229304087673)),
            ('power_exact_changed',lambda p:p['groups'][0]['power_corners'][0]['trace'][0].__setitem__('exact_rational',[0,1])),
            ('power_RNcharge_hidden',lambda p:p['groups'][0]['power_corners'][0]['trace'][0].__setitem__('rounding_error_abs',[0,1])),
            ('power_output_rational',lambda p:p['groups'][0]['power_corners'][0].__setitem__('observed_power_rational',[0,1])),
            ('power_ORIGINAL_lower_zero',lambda p:p['groups'][0]['power_corners'][0].__setitem__('ORIGINAL_power_lower_bound',[0,1])),
            ('power_relative_hidden',lambda p:p['groups'][0]['power_corners'][0].__setitem__('relative_power_error_bound',[0,1])),
            ('power_group_charge_hidden',lambda p:p['groups'][0].__setitem__('combined_error_abs_to_ORIGINAL_power_bound',[0,1]))]:
            p=copy.deepcopy(self.pc);mut(p)
            reject(label,lambda p=p:core.power_domain_proof(self.packet,self.ctx,self.g,p,self.rc,self.fc))
        fc=copy.deepcopy(self.fc);fc['sources'][0]['proof']['retained_corner_identities'].pop()
        reject('reflected_source_corner_missing',lambda:core.power_domain_proof(self.packet,self.ctx,self.g,self.pc,self.rc,fc))
        target=core.io.ROOT/core.PREVIOUS;read=Path.read_bytes
        with patch.object(Path,'read_bytes',lambda p:read(p)+b' ' if p==target else read(p)):
            reject('predecessor_SHA',lambda:core.load_retained())
if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2,stream=sys.stderr).run(unittest.defaultTestLoader.loadTestsFromTestCase(PowerDomainTests))
    print(json.dumps({'PASS':result.wasSuccessful(),'tests':result.testsRun,'data':DATA},sort_keys=True,separators=(',',':'),allow_nan=False))
    raise SystemExit(0 if result.wasSuccessful() else 1)

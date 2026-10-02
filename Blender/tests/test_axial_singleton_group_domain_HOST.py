"""Bounded singleton completeness/domain/receipt tests; no reduction producer replay."""
import copy,json,sys,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'benchmarks/capacity_audit'))
import axial_singleton_group_domain_HOST_v1 as core
DATA={}
class GroupDomainTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.retained=core.load_retained()
        cls.packets,cls.old,cls.red,cls.tree,cls.mirror,cls.pins,cls.discrepancy=cls.retained
        cls.n='positive';cls.ctx=cls.old['cases'][cls.n]['context'];cls.key=cls.ctx['groups'][0]
        cls.sources=cls.old['cases'][cls.n]['sources'];cls.rc=cls.red['explicit_synthetic_INPUT_controls']['cases'][cls.n]
        cls.tr=cls.tree[cls.n];cls.mi=cls.mirror[cls.n]
    def test_audit(self):
        a=core.audit_singleton_group_domain_HOST(self.old['case_order'],model=core.MODEL);DATA['audit']=a
        self.assertEqual((a['restricted_complete_singleton_groups_proved'],a['blocked_complete_groups'],a['retained_bit_copy_identities']),(2,15,16))
        self.assertEqual(a['inherited_pins_verified'],283)
        self.assertEqual((a['retained_unit_STOPs'],a['nonzero_domains_not_refined']),(14,2))
        for n,c in a['cases'].items():
            self.assertEqual(c['sources'],self.old['cases'][n]['sources'])
            for g in c['groups']:
                self.assertEqual(g['status'],'STOP');self.assertFalse(g['group_budget_evaluated'])
                for k in core.FALSE:self.assertIs(g[k],False)
                if 'proof' in g:
                    self.assertIn(n,['positive','negative'])
                    p=g['proof'];self.assertEqual(p['uniform_group_L1_error_to_fixed_ORIGINAL_bound'],[1,2**55])
                    self.assertEqual(p['reduction_rounding_error_L1'],[0,1])
                    self.assertTrue(p['synthetic_budget_admission_NOT_inherited'])
                    for q in p['retained_copy_identities']:self.assertEqual(q['retained_copy_uint64'][1],2**63)
        g=a['cases']['two_sources']['groups'][0]
        self.assertEqual(g['source_order'],['s','other']);self.assertEqual(g['blocked_source_ids'],['other'])
        self.assertNotIn('proof',g);self.assertNotIn('sum_uint64',g)
    def test_singleton_copy(self):
        p=core.singleton_proof(self.ctx,self.key,self.sources,self.rc,self.tr,self.mi)
        DATA['single_retained_proof']=p
        self.assertEqual(p['complete_source_order'],['s'])
        self.assertEqual(sum(q['bit_copy_identities_checked'] for q in p['retained_copy_identities']),8)
        self.assertEqual(p['new_RN_or_copy_or_scene_producer_executions'],0)
        for k in core.FALSE:self.assertIs(p[k],False)
    def test_metadata_discrepancy(self):
        DATA['metadata_discrepancy']=self.discrepancy
        self.assertEqual(self.discrepancy['recorded_rational'],[1,36028797018963970])
        self.assertEqual(self.discrepancy['captured_audit_rational'],[1,36028797018963968])
        self.assertNotEqual(core.number(self.discrepancy['recorded_rational']),core.number(self.discrepancy['captured_audit_rational']))
        self.assertFalse(self.discrepancy['predecessor_modified'])
    def test_rejections(self):
        rejected=[];DATA['rejections']=rejected
        def reject(label,fn):
            with self.assertRaises((ValueError,KeyError,TypeError)) as cm:fn()
            rejected.append({'label':label,'reason':str(cm.exception)})
        for label,n,m in [('model',['positive'],'wrong'),('empty',[],core.MODEL),('duplicate',['positive','positive'],core.MODEL),
                          ('boolcase',[False],core.MODEL),('tuple',('positive',),core.MODEL),('unknown',['other'],core.MODEL)]:
            reject(label,lambda n=n,m=m:core.audit_singleton_group_domain_HOST(n,model=m))
        reject('partial_multisource',lambda:core.group_members(self.old['cases']['two_sources']['context'],self.key,
                                                             self.old['cases']['two_sources']['sources'][:1]))
        reject('complete_multisource_not_singleton',lambda:core.singleton_proof(self.old['cases']['two_sources']['context'],self.key,
               self.old['cases']['two_sources']['sources'],self.rc,self.tr,self.mi))
        reject('unknown_group',lambda:core.group_members(self.ctx,['wrong','g'],self.sources))
        reject('partial_empty',lambda:core.group_members(self.ctx,self.key,[]))
        for label,mut in [
            ('missing_source_domain',lambda s:s[0].__setitem__('restricted_ideal_reflected_fixed_source_error_to_ORIGINAL_proved',False)),
            ('source_admitted',lambda s:s[0].__setitem__('status','PASS')),
            ('source_missingallocation_changed',lambda s:s[0]['proof'].__setitem__('missing_source_allocation_NOT_promoted',False)),
            ('uniform_event_chain_changed',lambda s:s[0]['proof']['profile'].__setitem__('restricted_entire_domain_event_chain_proved',False)),
            ('mirror_receipt_sha',lambda s:s[0]['proof'].__setitem__('retained_mirror_source_row_sha256','0'*64)),
            ('source_error_zero',lambda s:s[0]['proof'].__setitem__('uniform_ideal_reflected_source_L1_error_to_fixed_ORIGINAL_bound',[0,1])),
            ('corner_missing',lambda s:s[0]['proof']['retained_corner_identities'].pop()),
            ('corner_zero_sign_changed',lambda s:s[0]['proof']['retained_corner_identities'][1]['reflected_uint64'].__setitem__(1,0)),
            ('ORIGINAL_gauge_changed',lambda s:s[0]['proof']['retained_corner_identities'][1].__setitem__('negated_fixed_ORIGINAL_source_rational',[[0,1],[0,1]])),
            ('corner_error_changed',lambda s:s[0]['proof']['retained_corner_identities'][1].__setitem__('uniform_reflected_source_error_L1',[0,1]))]:
            s=copy.deepcopy(self.sources);mut(s);reject(label,lambda s=s:core.singleton_proof(self.ctx,self.key,s,self.rc,self.tr,self.mi))
        for label,mut in [
            ('reduction_context',lambda r:r['context'].__setitem__('word_ABI_sha256','0'*64)),
            ('reduction_tree_sha',lambda r:r.__setitem__('retained_tree_row_sha256','0'*64)),
            ('reduction_group_missing',lambda r:r['groups'].pop()),
            ('reduction_source_order',lambda r:r['groups'][0].__setitem__('source_order',['other'])),
            ('certificate',lambda r:r['groups'][0].__setitem__('certificate_sha256','0'*64)),
            ('reduction_corner_missing',lambda r:r['groups'][0]['corner_sums'].pop()),
            ('copy_sum_changed',lambda r:r['groups'][0]['corner_sums'][0]['sum_uint64'].__setitem__(1,0)),
            ('copy_source_changed',lambda r:r['groups'][0]['corner_sums'][0]['source_uint64'][0].__setitem__(0,0)),
            ('copy_rational_changed',lambda r:r['groups'][0]['corner_sums'][0].__setitem__('sum_rational',[[0,1],[0,1]])),
            ('new_addition',lambda r:r['groups'][0]['corner_sums'][0].__setitem__('RN64_additions',1)),
            ('RN_bool',lambda r:r['groups'][0]['corner_sums'][0].__setitem__('RN64_additions',False)),
            ('nonempty_trace',lambda r:r['groups'][0]['corner_sums'][0].__setitem__('trace',[{}])),
            ('hidden_roundingerror',lambda r:r['groups'][0]['corner_sums'][0].__setitem__('rounding_error_L1_bound',[1,2])),
            ('wrong_ledger',lambda r:r['groups'][0].__setitem__('error_L1_to_ORIGINAL_group_corner_sum_bound',[0,1]))]:
            r=copy.deepcopy(self.rc);mut(r);reject(label,lambda r=r:core.singleton_proof(self.ctx,self.key,self.sources,r,self.tr,self.mi))
        tr=copy.deepcopy(self.tr);tr['tree_lineage_matches_restricted_CPU_only']=False
        reject('tree_match_missing',lambda:core.singleton_proof(self.ctx,self.key,self.sources,self.rc,tr,self.mi))
        changed=copy.deepcopy(self.retained);changed[1]['cases']['positive']['context']['assignments'][0]['rebase_cycles']=[1,1]
        with patch.object(core,'load_retained',lambda:changed):
            reject('fresh_gauge_context',lambda:core.audit_singleton_group_domain_HOST(['positive'],model=core.MODEL))
        changed=copy.deepcopy(self.retained);changed[2]['missing']['cases']['positive']['allocation_result']['allocation_INPUT_valid']=True
        with patch.object(core,'load_retained',lambda:changed):
            reject('missing_allocation_promoted',lambda:core.audit_singleton_group_domain_HOST(['positive'],model=core.MODEL))
        target=core.io.ROOT/core.PREVIOUS;read=Path.read_bytes
        with patch.object(Path,'read_bytes',lambda p:read(p)+b' ' if p==target else read(p)):
            reject('predecessor_SHA',lambda:core.load_retained())
if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2,stream=sys.stderr).run(unittest.defaultTestLoader.loadTestsFromTestCase(GroupDomainTests))
    print(json.dumps({'PASS':result.wasSuccessful(),'tests':result.testsRun,'data':DATA},sort_keys=True,separators=(',',':'),allow_nan=False))
    raise SystemExit(0 if result.wasSuccessful() else 1)

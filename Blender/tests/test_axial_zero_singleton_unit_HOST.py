"""New bounded tests: exact identities only; no previous numeric tests/producers."""
import copy,json,sys,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'benchmarks/capacity_audit'))
import axial_zero_singleton_unit_HOST_v1 as core
DATA={}
class ZeroTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packets,cls.prior,cls.rect,cls.units,cls.pins=core.load_retained()
        cls.profile=core.profile_from_retained(cls.units)
    def test_audit(self):
        a=core.audit_zero_singleton_HOST(list(self.prior['case_order']),model=core.MODEL)
        DATA['audit']=a
        self.assertEqual((a['restricted_zero_unit_proofs'],a['retained_unit_STOPs'],a['nonzero_domains_not_refined']),(3,14,2))
        self.assertEqual(a['inherited_pins_verified'],268)
        proofs=[s['proof'] for c in a['cases'].values() for s in c['sources'] if 'proof' in s]
        self.assertEqual(len(proofs),3)
        for p in proofs:
            self.assertTrue(p['exact_charge_fits_unchanged_cap'])
            self.assertEqual(p['unit_L1_error_to_ORIGINAL_bound'],[0,1])
            self.assertEqual(p['unchanged_original_phase_cap_rad'],[0,1])
            self.assertEqual(len(p['graph_checks']),5)
            for g in p['graph_checks']:
                self.assertEqual(g['identities_checked'],26)
                self.assertEqual(len(g['canonical_HOST_zero_not_IEEE_signed_zero_labels']),6)
                self.assertFalse(g['native_signed_zero_graph_equivalence_proved'])
        for c in a['cases'].values():
            for s in c['sources']:
                self.assertEqual(s['status'],'STOP')
                for k in core.FALSE:self.assertIs(s[k],False)
    def test_word_identities(self):
        trace,labels=core.exact_trace(self.profile)
        DATA['identity_labels']=labels
        self.assertEqual(len(trace),26)
        self.assertEqual(core.decode(core.ONE),1)
        self.assertEqual(core.decode(1<<63),0)
        self.assertEqual(sum(v['output_uint64']==0 for v in trace),14)
    def test_quarter_permutation(self):
        DATA['permutations']=[]
        for k in (-2,-1,0,1,2):
            words=core.permuted_zero(k)
            DATA['permutations'].append({'quarter':k,'words':words,'rational':[core.pair(core.decode(w)) for w in words]})
        self.assertEqual(DATA['permutations'][2]['words'],[core.ONE,0])
    def test_fail_closed(self):
        rejects=[];DATA['rejections']=rejects
        def reject(label,fn):
            with self.assertRaises((ValueError,TypeError,KeyError)) as cm:fn()
            rejects.append({'label':label,'reason':str(cm.exception)})
        for label,n,m in [('model',['positive'],'other'),('empty',[],core.MODEL),
                          ('duplicates',['positive','positive'],core.MODEL),('unknown',['no'],core.MODEL),
                          ('boolcase',[True],core.MODEL),('tuple',('positive',),core.MODEL)]:
            reject(label,lambda n=n,m=m:core.audit_zero_singleton_HOST(n,model=m))
        for w in (True,-1,2**64,1,0x7ff0000000000000):
            reject('word_'+str(w),lambda w=w:core.decode(w))
        for k in (True,3,0.0):
            reject('quarter_'+str(k),lambda k=k:core.permuted_zero(k))
        for value in ([[0,1],[1,2]],[[False,1],[0,1]],[[0,2],[0,1]]):
            reject('interval_'+str(value),lambda value=value:core.zero_interval(value))
        unit=self.units['positive']['sources'][0]['ideal_ORIGINAL_unit_HOST']
        for label,mut in [
            ('node_word',lambda u:u['rotation_RN64']['operations'][3].__setitem__('output_uint64',1<<63)),
            ('node_bool',lambda u:u['rotation_RN64']['operations'][0].__setitem__('output_uint64',False)),
            ('node_operand',lambda u:u['rotation_RN64']['operations'][0].__setitem__('inputs_rational',[[1,1],[0,1]])),
            ('node_delta',lambda u:u['rotation_RN64']['operations'][0].__setitem__('rounding_delta_rational',[1,2])),
            ('node_missing',lambda u:u['rotation_RN64']['operations'].pop()),
            ('term_word',lambda u:u['rotation_RN64']['terms']['cos'].__setitem__('output_uint64',0)),
            ('angle_nonzero',lambda u:u['rotation_RN64'].__setitem__('angle_uint64',core.ONE)),
            ('coefficient',lambda u:u['rotation_RN64']['coefficients']['cos'][3].__setitem__('uint64',core.ONE)),
            ('permutation',lambda u:u.__setitem__('unit_uint64',[0,core.ONE])),
            ('ABI',lambda u:u['unit_uint32_little_endian'][0].__setitem__(0,1))]:
            u=copy.deepcopy(unit);mut(u);reject(label,lambda u=u:core.verify_zero_graph(u,self.profile,0))
        for word in (0,True,core.ONE+1,1,0x7ff0000000000000):
            p=copy.deepcopy(self.profile);p['cos'][0]['uint64']=word
            reject('c0_'+str(word),lambda p=p:core.exact_trace(p))
        n='positive';d=self.prior['cases'][n]['sources'][0];r=self.rect['cases'][n]['sources'][0];u=self.units[n]['sources'][0]
        for label,mut in [('nonzero_domain',lambda r:r['argument_image'].__setitem__('argument_interval',[[0,1],[1,2]])),
                          ('ORIGINALnonzero',lambda r:r['parameter_branch'].__setitem__('ORIGINAL_quarter_residual',[1,2])),
                          ('nonzero_charge',lambda r:r['argument_image'].__setitem__('uniform_argument_error_bound_rad',[1,2]))]:
            rr=copy.deepcopy(r);mut(rr);dd=copy.deepcopy(d);dd['retained_argument_rectangle_source_sha256']=core.allocation.digest(rr)
            reject(label,lambda dd=dd,rr=rr:core.restricted_zero_proof(dd,rr,u,self.profile,[0,1]))
        reject('changed_cap',lambda:core.restricted_zero_proof(d,r,u,self.profile,[1,1]))
        target=core.io.ROOT/core.PREVIOUS;read=Path.read_bytes
        with patch.object(Path,'read_bytes',lambda p:read(p)+b' ' if p==target else read(p)):
            reject('predecessor_SHA',lambda:core.load_retained())
if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2,stream=sys.stderr).run(unittest.defaultTestLoader.loadTestsFromTestCase(ZeroTests))
    print(json.dumps({'PASS':result.wasSuccessful(),'tests':result.testsRun,'data':DATA},sort_keys=True,separators=(',',':'),allow_nan=False))
    raise SystemExit(0 if result.wasSuccessful() else 1)

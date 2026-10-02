"""Bounded new HOST fixed-source checks; no old numeric producers/tests."""
import base64,copy,hashlib,json,struct,sys,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'benchmarks/capacity_audit'))
import axial_zero_source_domain_HOST_v1 as core
DATA={}
class SourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packets,cls.old,cls.products,cls.pins=core.load_retained()
    def test_audit(self):
        a=core.audit_zero_source_domain_HOST(self.old['case_order'],model=core.MODEL);DATA['audit']=a
        self.assertEqual((a['restricted_fixed_source_domains_proved'],a['retained_unit_STOPs'],a['nonzero_domains_not_refined']),(3,14,2))
        self.assertEqual(a['inherited_pins_verified'],273)
        count=0
        for c in a['cases'].values():
            for s in c['sources']:
                self.assertEqual(s['status'],'STOP')
                for k in core.FALSE:self.assertIs(s[k],False)
                if 'proof' in s:
                    p=s['proof'];self.assertEqual(p['uniform_bare_product_L1_error_to_fixed_ORIGINAL_bound'],[1,2**55])
                    self.assertTrue(p['nonzero_encoding_error_preserved'])
                    self.assertTrue(p['phase_cap_NOT_compared_to_amplitude'])
                    self.assertEqual(p['unchanged_original_phase_cap_rad'],[0,1])
                    self.assertEqual(len(p['graph_checks']),4);count+=sum(g['retained_node_identities_checked'] for g in p['graph_checks'])
                    for g in p['graph_checks']:
                        self.assertEqual(g['charges_L1']['source_encoding'],[1,2**55])
                        self.assertEqual(g['charges_L1']['unit_to_ORIGINAL'],[0,1])
        self.assertEqual(count,96)
    def test_original_words_and_encoding(self):
        DATA['source_word_checks']=[]
        for n in ('negative','positive','two_sources'):
            c=self.old['cases'][n]['context'];w=core.fixed_source_words(self.packets[n],c,0)
            self.assertEqual(w,self.products[n]['sources'][0]['original_source_uint64'])
            p=self.products[n]['sources'][0]['encoded_corner_products'][0]
            g=core.verify_product_identity(p,w,[core.zero.ONE,0]);DATA['source_word_checks'].append({'case':n,'proof':g})
            self.assertNotEqual(g['fixed_original_source_rational'],g['represented_source_rational'])
    def test_binary_limbs(self):
        DATA['binary_controls']=[]
        for w,v in [(0,0),(2**31,0),(0x3f800000,1),(0xbf800000,-1)]:
            x=core.decode32(w);self.assertEqual(x,v);DATA['binary_controls'].append({'word':w,'rational':core.pair(x)})
    def test_rejections(self):
        rejected=[];DATA['rejections']=rejected
        def reject(label,fn):
            with self.assertRaises((ValueError,TypeError,KeyError,struct.error)) as cm:fn()
            rejected.append({'label':label,'reason':str(cm.exception)})
        for label,n,m in [('model',['positive'],'bad'),('empty',[],core.MODEL),('duplicate',['positive','positive'],core.MODEL),
                          ('boolcase',[True],core.MODEL),('unknown',['unknown'],core.MODEL),('tuple',('positive',),core.MODEL)]:
            reject(label,lambda n=n,m=m:core.audit_zero_source_domain_HOST(n,model=m))
        for w in (True,-1,2**32,1,0x7f800000):
            reject('limb_'+str(w),lambda w=w:core.decode32(w))
        original=self.products['positive']['sources'][0]['original_source_uint64']
        product=self.products['positive']['sources'][0]['encoded_corner_products'][0]
        for label,mut in [
            ('unit_word',lambda p:p.__setitem__('unit_uint64',[0,core.zero.ONE])),
            ('unit_bool',lambda p:p.__setitem__('unit_uint64',[core.zero.ONE,False])),
            ('unit_charge',lambda p:p.__setitem__('unit_error_L1_to_ORIGINAL_bound',[1,2])),
            ('encoder_original',lambda p:p['source_encoder']['original_source_uint64'].__setitem__(0,core.zero.ONE)),
            ('encoder_limb',lambda p:p['source_encoder']['source_limb_uint32'].__setitem__(1,0)),
            ('encoder_limb_bool',lambda p:p['source_encoder']['source_limb_uint32'].__setitem__(2,False)),
            ('encoder_bytes',lambda p:p['source_encoder'].__setitem__('source_hilo_le_base64','AAAA')),
            ('encoder_sha',lambda p:p['source_encoder'].__setitem__('source_hilo_le_sha256','0'*64)),
            ('encoder_error_zero',lambda p:p['source_encoder'].__setitem__('source_encoding_error_L1',[0,1])),
            ('encoder_residual',lambda p:p['source_encoder']['HOST_trace'][0].__setitem__('HOST_exact_residual',[0,1])),
            ('node_missing',lambda p:p['operations'].pop()),
            ('node_delta',lambda p:p['operations'][2].__setitem__('delta',[1,2])),
            ('node_input',lambda p:p['operations'][2].__setitem__('inputs',[[0,1],[1,1]])),
            ('node_bool',lambda p:p['operations'][1].__setitem__('output_uint64',False)),
            ('product_words',lambda p:p.__setitem__('product_uint64',original)),
            ('product_reference',lambda p:p.__setitem__('exact_original_times_represented_unit',p['source_decoded_RN64'])),
            ('charge_hidden',lambda p:p['charges_L1'].__setitem__('source_encoding',[0,1])),
            ('total_hidden',lambda p:p.__setitem__('error_L1_to_original_source_times_ideal_unit_bound',[0,1])),
            ('observed_hidden',lambda p:p.__setitem__('observed_error_to_original_times_represented_unit_L1',[0,1]))]:
            p=copy.deepcopy(product);mut(p);reject(label,lambda p=p:core.verify_product_identity(p,original,[core.zero.ONE,0]))
        ctx=self.old['cases']['positive']['context'];packet=self.packets['positive']
        for index in (True,-1,1):
            reject('source_index_'+str(index),lambda index=index:core.fixed_source_words(packet,ctx,index))
        altered=copy.deepcopy(ctx);altered['input_packet_sha256']='0'*64
        reject('caller_context',lambda:core.fixed_source_words(packet,altered,0))
        p=copy.deepcopy(packet);raw=bytearray(base64.b64decode(p['buffers_base64']['sources']));raw[112]^=1;raw=bytes(raw)
        p['buffers_base64']['sources']=base64.b64encode(raw).decode();p['manifest']['buffers']['sources']={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
        fresh=core.allocation.context_from_packet(p,core.digest(p),model=core.allocation.MODEL)
        reject('ORIGINAL_field_word_changed',lambda:core.fixed_source_words(p,fresh,0))
        u=self.old['cases']['positive']['sources'][0];p=self.products['positive']['sources'][0]
        for label,mut in [('domain_absent',lambda u:u.__setitem__('restricted_exact_unit_error_to_ORIGINAL_proved',False)),
                          ('domain_charge',lambda u:u['proof'].__setitem__('unit_L1_error_to_ORIGINAL_bound',[1,2])),
                          ('domain_quarter',lambda u:u['proof'].__setitem__('quarter_turn',1))]:
            uu=copy.deepcopy(u);mut(uu);reject(label,lambda uu=uu:core.fixed_source_domain_proof(packet,ctx,0,uu,p))
        pp=copy.deepcopy(p);pp['terminal_reference_id']='wrong'
        reject('gauge_changed',lambda:core.fixed_source_domain_proof(packet,ctx,0,u,pp))
        pp=copy.deepcopy(p);pp['encoded_corner_products'].pop()
        reject('missing_corner',lambda:core.fixed_source_domain_proof(packet,ctx,0,u,pp))
        target=core.io.ROOT/core.PREVIOUS;read=Path.read_bytes
        with patch.object(Path,'read_bytes',lambda p:read(p)+b' ' if p==target else read(p)):
            reject('predecessor_SHA',lambda:core.load_retained())
if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2,stream=sys.stderr).run(unittest.defaultTestLoader.loadTestsFromTestCase(SourceTests))
    print(json.dumps({'PASS':result.wasSuccessful(),'tests':result.testsRun,'data':DATA},sort_keys=True,separators=(',',':'),allow_nan=False))
    raise SystemExit(0 if result.wasSuccessful() else 1)

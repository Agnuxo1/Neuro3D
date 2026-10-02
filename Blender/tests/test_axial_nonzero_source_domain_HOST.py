"""Own bounded regression tests; retained data read once, no old numerical writers."""
import copy,json,sys,unittest
from pathlib import Path
from unittest.mock import patch
from fractions import Fraction as F
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'benchmarks/capacity_audit'))
import axial_nonzero_source_domain_HOST_v1 as core
DATA={}
class SourceDomainTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.retained=core.load_retained();cls.packets,cls.old,cls.products,cls.pins=cls.retained
        cls.n='thin_resolved';cls.ctx=cls.old['cases'][cls.n]['context']
        cls.u=cls.old['cases'][cls.n]['sources'][0];cls.p=cls.products[cls.n]['sources'][0]
    def test_complete_domain_bound(self):
        with patch.object(core,'load_retained',return_value=self.retained):
            a=core.audit_nonzero_source_domain_HOST(self.old['case_order'],model=core.MODEL)
        DATA['audit']=a
        self.assertEqual((a['restricted_nonzero_bare_source_bounds_proved'],a['retained_unit_STOPs'],a['zero_domains_outside_scope']),(2,14,3))
        self.assertEqual(a['inherited_pins_verified'],303)
        found=[]
        for n,c in a['cases'].items():
            for s in c['sources']:
                self.assertEqual(s['status'],'STOP')
                for k in core.FALSE:self.assertIs(s[k],False)
                if s[core.FLAG]:
                    found.append(n);p=s['proof'];charges=p['charges_L1_decimal']
                    self.assertEqual(core.unit.number(p['nonzero_encoding_error_L1']),F(1,2**55))
                    self.assertEqual(core.rational(charges['source_decode_RN64']),0)
                    self.assertGreater(core.rational(charges['source_encoding']),0)
                    self.assertGreater(core.rational(charges['unit_to_fixed_ORIGINAL']),0)
                    self.assertGreater(core.rational(charges['product_RN64']),0)
                    self.assertEqual(core.rational(p['uniform_bare_source_L1_error_to_fixed_ORIGINAL_bound_decimal']),sum(map(core.rational,charges.values()),F(0)))
                    self.assertEqual(len(p['product_RN_nodes']),6)
                    self.assertFalse(p['material_reflection_charge_included'])
        self.assertEqual(set(found),{'thin_resolved','nonexact_geometry_phase_PASS'})
        self.assertFalse(a['cases']['two_sources']['sources'][1][core.FLAG])
        self.assertNotIn('proof',a['cases']['two_sources']['sources'][1])
    def test_rejections(self):
        rejected=[];DATA['rejections']=rejected
        def reject(label,fn):
            with self.assertRaises((ValueError,TypeError,KeyError,IndexError)) as cm:fn()
            rejected.append({'label':label,'reason':str(cm.exception)})
        mutations=[
          ('stale_context',lambda c,u,p:c.__setitem__('input_packet_sha256','0'*64)),
          ('gauge',lambda c,u,p:u['proof'].__setitem__('ORIGINAL_assignment_sha256','0'*64)),
          ('source_id',lambda c,u,p:p.__setitem__('source_id','other')),
          ('unit_absent',lambda c,u,p:u.__setitem__(core.unit.FLAG,False)),
          ('unit_proof_absent',lambda c,u,p:u['proof'].__setitem__(core.unit.FLAG,False)),
          ('unit_promotion',lambda c,u,p:u['proof'].__setitem__('native_kernel_implemented',True)),
          ('FMA',lambda c,u,p:u['proof'].__setitem__('arithmetic_hypothesis','FMA')),
          ('hidden_unit_error',lambda c,u,p:u['proof'].__setitem__('uniform_unit_L1_to_fixed_ORIGINAL_bound_decimal',['0','1'])),
          ('hidden_phase_error',lambda c,u,p:u['proof'].__setitem__('argument_phase_bound_rad',[0,1])),
          ('raised_cap',lambda c,u,p:u['proof'].__setitem__('unchanged_original_phase_cap_rad',[1,1])),
          ('source_gauge',lambda c,u,p:p.__setitem__('phase_reference_id','other')),
          ('terminal_gauge',lambda c,u,p:p.__setitem__('terminal_reference_id','other')),
          ('source_word',lambda c,u,p:p['original_source_uint64'].__setitem__(0,0)),
          ('product_witness_absent',lambda c,u,p:p.__setitem__('source_product_evaluated',False)),
          ('missing_corner',lambda c,u,p:p['encoded_corner_products'].pop()),
          ('hidden_encoding_error',lambda c,u,p:[v['source_encoder'].__setitem__('source_encoding_error_L1',[0,1]) for v in p['encoded_corner_products']]),
          ('decode_error',lambda c,u,p:p['encoded_corner_products'][0]['operations'][0].__setitem__('delta',[1,1])),
          ('decode_word',lambda c,u,p:p['encoded_corner_products'][0]['operations'][0].__setitem__('output_uint64',0)),
          ('graph_order',lambda c,u,p:p['encoded_corner_products'][0]['operations'][2].__setitem__('label','ad')),
          ('graph_model',lambda c,u,p:p['encoded_corner_products'][0].__setitem__('model','FMA'))]
        for label,mut in mutations:
            c,u,p=copy.deepcopy((self.ctx,self.u,self.p));mut(c,u,p)
            reject(label,lambda c=c,u=u,p=p:core.prove_source(self.packets[self.n],c,0,u,p))
        for label,M in [('norm_too_large',F(2)),('norm_negative',F(-1))]:
            reject(label,lambda M=M:core.product_majorants(F(1,10),F(0),M))
        for label,v in [('noncanonical_rational',['01','2']),('float_rational',[0.1,1]),('unreduced_rational',['2','4'])]:
            reject(label,lambda v=v:core.rational(v))
        with patch.object(core,'load_retained',return_value=self.retained):
            for label,n,m in [('model',[self.n],'wrong'),('empty',[],core.MODEL),('duplicate',[self.n,self.n],core.MODEL),('unknown',['unknown'],core.MODEL)]:
                reject(label,lambda n=n,m=m:core.audit_nonzero_source_domain_HOST(n,model=m))
        read=Path.read_bytes;target=core.io.ROOT/core.PREVIOUS
        with patch.object(Path,'read_bytes',lambda p:read(p)+b' ' if p==target else read(p)):
            reject('predecessor_SHA',core.load_retained)
    def test_generic_complex_majorants(self):
        a,b,M=F(1,10),F(-1,20),F(3,2)
        E=lambda m:m/F(2**53)+F(1,2**1075) if m else F(0)
        er=E(abs(a)*M)+E(abs(b)*M)
        expected=2*er+2*E((abs(a)+abs(b))*M+er)
        total,nodes=core.product_majorants(a,b,M)
        self.assertEqual(total,expected);self.assertEqual(len(nodes),6)
        DATA['generic_complex_control']={'a':core.unit.pair(a),'b':core.unit.pair(b),'M':core.unit.pair(M),'bound_decimal':core.decimal(total)}
    def test_no_input_mutation(self):
        packet=self.packets[self.n];before=core.digest((packet,self.ctx,self.u,self.p))
        core.prove_source(packet,self.ctx,0,self.u,self.p)
        self.assertEqual(before,core.digest((packet,self.ctx,self.u,self.p)))
if __name__=='__main__':
    r=unittest.TextTestRunner(verbosity=2,stream=sys.stderr).run(unittest.defaultTestLoader.loadTestsFromTestCase(SourceDomainTests))
    print(json.dumps({'PASS':r.wasSuccessful(),'tests':r.testsRun,'data':DATA},sort_keys=True,separators=(',',':'),allow_nan=False))
    raise SystemExit(0 if r.wasSuccessful() else 1)

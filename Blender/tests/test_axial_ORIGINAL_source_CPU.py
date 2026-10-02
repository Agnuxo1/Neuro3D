"""Own fresh ORIGINAL bare-source prefix tests, legacy failures immutable."""
import copy,json,math,sys,unittest
from pathlib import Path
from unittest.mock import patch
from fractions import Fraction as F
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'benchmarks/capacity_audit'))
import axial_ORIGINAL_source_CPU_v1 as core
DATA={}
class SourcePrefixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.retained=core.load_retained();cls.packets,cls.old,cls.pins=cls.retained
    def test_a_fresh_prefix(self):
        before=core.digest(self.retained)
        with patch.object(core,'load_retained',return_value=self.retained),patch.object(core.source,'execute_graph',side_effect=AssertionError('legacy SOURCE must not execute')),patch.object(core.original.prior,'execute_horner',side_effect=AssertionError('retained Horner forbidden')):
            a=core.audit_ORIGINAL_source_CPU(self.old['case_order'],model=core.MODEL)
        DATA['audit']=a
        self.assertEqual(core.digest(self.retained),before)
        self.assertEqual((a['fresh_ORIGINAL_bare_source_prefixes_executed'],a['retained_sources_not_executed'],a['inherited_pins_verified']),(2,17,328))
        self.assertEqual((a['new_CPU_source_RN32_casts'],a['new_CPU_source_RN64_subtractions'],a['new_CPU_source_decode_product_nodes']),(8,4,16))
        found=[]
        for n,c in a['cases'].items():
            for r in c['sources']:
                self.assertEqual(r['status'],'STOP')
                for key in core.FALSE:self.assertIs(r[key],False)
                if r[core.FLAG]:
                    found.append(n);p=r['bare_source_prefix'];e=r['encoder']
                    self.assertEqual(e['source_encoding_error_L1'],[1,2**55])
                    self.assertEqual(len(p['nodes']),8);self.assertFalse(p['source_amplitude_budget_admitted'])
                    self.assertFalse(p['zero_canonicalization_performed']);self.assertFalse(p['source_phase_bound_proved'])
                    self.assertEqual(F(*p['bare_source_error_charges_L1']['source_decode_RN64_L1']),0)
                    self.assertEqual(F(*p['point_bare_source_to_ORIGINAL_bound_L1']),sum(F(*v) for v in p['bare_source_error_charges_L1'].values()))
        self.assertEqual(set(found),{'nonexact_geometry_phase_PASS','thin_resolved'})
        self.assertEqual(a['cases']['thin_resolved']['sources'][0]['trace']['hits'][0]['segment_BU'],[1,2**30])
        self.assertFalse(a['cases']['two_sources']['sources'][1][core.FLAG])
    def test_b_signed_zero_and_imaginary_controls(self):
        controls=[]
        words=[0x3ff0000000000000,0x8000000000000000]
        for field in ([-0.0,0.0],[0.1,-0.25],[0.0,0.0]):
            enc=core.encode_source(field);p=core.product_prefix(enc,words,[0,1])
            controls.append({'field_uint64':[core.source.word(v) for v in field],'encoder':enc,'prefix':p})
        DATA['primitive_controls']=controls
        self.assertEqual(controls[0]['encoder']['source_limb_uint32'][0],0x80000000)
        self.assertEqual(controls[0]['encoder']['components'][0]['residual_uint64'],0)
        self.assertEqual(controls[0]['encoder']['source_limb_uint32'][1],0)
        self.assertEqual(controls[1]['prefix']['decoded_source_uint64'][1],core.source.word(-0.25))
        self.assertEqual(controls[2]['prefix']['nodes'][4]['output_uint64'],0x8000000000000000)
    def test_c_rejections(self):
        rejected=[];DATA['rejections']=rejected
        def reject(label,fn):
            with self.assertRaises((ValueError,TypeError,KeyError,IndexError)) as cm:fn()
            rejected.append({'label':label,'reason':str(cm.exception)})
        for label,field in [('field_tuple',(0.1,0.0)),('short_field',[0.1]),('bool_component',[True,0.0]),('nan',[float('nan'),0.0]),('infinity',[float('inf'),0.0]),('subnormal_ORIGINAL',[math.ldexp(1.0,-1074),0.0]),('overflow32',[1e40,0.0]),('subnormal_high32',[1e-40,0.0]),('subnormal_low32',[math.ldexp(1.0,-126)+math.ldexp(1.0,-149),0.0])]:
            # At 2^-120 the high32 ULP is 2^-143; residual 2^-146 is a nonzero subnormal32.
            if label=='subnormal_low32':field=[math.ldexp(1.0,-120)+math.ldexp(1.0,-146),0.0]
            reject(label,lambda field=field:core.encode_source(field))
        row=DATA['audit']['cases']['thin_resolved']['sources'][0];enc=row['encoder'];words=row['unit']['unit_uint64'];U=row['composition']['point_unit_L1_to_ORIGINAL_bound']
        for label,mut in [('transport_SHA',lambda e:e.__setitem__('source_hilo_le_sha256','0'*64)),('transport_bytes',lambda e:e.__setitem__('source_hilo_le_base64','AAAA')),('encoding_charge',lambda e:e.__setitem__('source_encoding_error_L1',[0,1])),('exact_sum',lambda e:e['exact_source_limb_sums'].__setitem__(0,[0,1])),('bool_limb',lambda e:e['source_limb_uint32'].__setitem__(0,True))]:
            e=copy.deepcopy(enc);mut(e);reject(label,lambda e=e:core.product_prefix(e,words,U))
        reject('short_unit',lambda:core.product_prefix(enc,[words[0]],U))
        reject('negative_unit_error',lambda:core.product_prefix(enc,words,[-1,1]))
        reject('large_unit_error',lambda:core.product_prefix(enc,words,[1,1]))
        reject('nonfinite_unit_word',lambda:core.product_prefix(enc,[0x7ff0000000000000,words[1]],U))
        with patch.object(core,'load_retained',return_value=self.retained):
            for label,n,m in [('wrong_model',['thin_resolved'],'bad'),('empty',[],core.MODEL),('duplicate',['thin_resolved']*2,core.MODEL),('unknown',['unknown'],core.MODEL)]:
                reject(label,lambda n=n,m=m:core.audit_ORIGINAL_source_CPU(n,model=m))
            with patch.object(core,'runtime_probe',return_value={'PASS':False}),patch.object(core.original,'trace_original',side_effect=AssertionError('guard before scene')):
                reject('guard_FAIL',lambda:core.audit_ORIGINAL_source_CPU(['thin_resolved'],model=core.MODEL))
        old=copy.deepcopy(self.old);old['cases']['thin_resolved']['context']['input_packet_sha256']='0'*64
        with patch.object(core,'load_retained',return_value=(self.packets,old,self.pins)):
            reject('stale_INPUT',lambda:core.audit_ORIGINAL_source_CPU(['thin_resolved'],model=core.MODEL))
        old=copy.deepcopy(self.old);old['cases']['thin_resolved']['sources'][0]['unit']['unit_uint64'][0]^=1
        with patch.object(core,'load_retained',return_value=(self.packets,old,self.pins)):
            reject('retained_unit_tamper_after_fresh',lambda:core.audit_ORIGINAL_source_CPU(['thin_resolved'],model=core.MODEL))
        read=Path.read_bytes;target=core.io.ROOT/core.PREVIOUS
        with patch.object(Path,'read_bytes',lambda p:read(p)+b' ' if p==target else read(p)):
            reject('predecessor_SHA',core.load_retained)
    def test_d_INPUT_word_binding(self):
        n='thin_resolved';ctx=self.old['cases'][n]['context'];packet=self.packets[n]
        snap,_=core.original.snapshot_from_packet(packet,ctx);original=snap['sources'][0]['field_reim']
        self.assertEqual(core.encode_source(original)['ORIGINAL_source_uint64'],[core.source.word(v) for v in original])
        self.assertTrue(DATA['audit']['previous_SOURCE_eight_bit_FAILs_preserved'])
if __name__=='__main__':
    r=unittest.TextTestRunner(verbosity=2,stream=sys.stderr).run(unittest.defaultTestLoader.loadTestsFromTestCase(SourcePrefixTests))
    print(json.dumps({'PASS':r.wasSuccessful(),'tests':r.testsRun,'data':DATA},sort_keys=True,separators=(',',':'),allow_nan=False))
    raise SystemExit(0 if r.wasSuccessful() else 1)

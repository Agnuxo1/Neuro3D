"""Bounded new CPU stage tests; reference fixtures retained, not reexecuted."""
import copy,json,sys,unittest
from fractions import Fraction as F
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'benchmarks/capacity_audit'))
import axial_source_float64_stage_CPU_v1 as core
DATA={}
class FloatStageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.retained=core.load_retained();cls.packets,cls.old,cls.products,cls.pins=cls.retained
        cls.n='thin_resolved';cls.ctx=cls.old['cases'][cls.n]['context']
        cls.certificate=cls.old['cases'][cls.n]['sources'][0];cls.product=cls.products[cls.n]['sources'][0]
    def test_pinned_partial_stage_execution(self):
        with patch.object(core,'load_retained',return_value=self.retained):
            a=core.audit_source_float64_stage_CPU(self.old['case_order'],model=core.MODEL)
        DATA['audit']=a
        self.assertEqual(a['inherited_pins_verified'],308)
        self.assertEqual((a['executed_source_fixture_sets'],a['retained_sources_not_executed'],a['new_CPU_float64_RN_nodes_executed']),(2,17,64))
        self.assertEqual(a['point_graphs_bits_MATCH']+a['point_graphs_bits_FAIL'],8)
        self.assertTrue(a['runtime_probe']['PASS']);self.assertFalse(a['unit_or_scene_inference_executed_new'])
        found=[]
        for n,c in a['cases'].items():
            for s in c['sources']:
                self.assertEqual(s['status'],'STOP')
                for k in core.FALSE:self.assertIs(s[k],False)
                if s[core.FLAG]:
                    found.append(n);self.assertEqual(len(s['points']),4)
                    for v in s['points']:
                        self.assertEqual(len(v['nodes']),8)
                        bad=[q['label'] for q in v['nodes'] if q['output_uint64']!=q['reference_output_uint64']]
                        self.assertEqual(v['node_word_mismatches'],bad)
                        self.assertEqual(v['exact_retained_node_bits_match'],not bad)
                        self.assertFalse(v['zero_canonicalization_performed'])
        self.assertEqual(set(found),{'thin_resolved','nonexact_geometry_phase_PASS'})
        self.assertFalse(a['cases']['two_sources']['sources'][1][core.FLAG])
        self.assertNotIn('points',a['cases']['two_sources']['sources'][1])
    def test_signed_zero_FAIL_preserved(self):
        # The retained Fraction HOST model canonicalizes zeros. This explicit
        # mathematical fixture makes the negative bc zero observable in IEEE CPU.
        limbs=self.certificate['proof']['source_hilo_uint32']
        hi,lo=[core.prev.source.decode32(w) for w in limbs[:2]];a=hi+lo;z=F(0)
        inputs=[[hi,lo],[z,z],[a,F(-1)],[z,z],[a,z],[z,F(-1)],[-a,z],[z,z]]
        aw=4591870180066957720;neg=aw|2**63
        expected=[aw,0,neg,0,0,0,neg,0]
        ops=[{'label':label,'op':'mul' if 2<=i<=5 else 'add','inputs':list(map(core.prev.unit.pair,ins)),
              'output_uint64':out} for i,(label,ins,out) in enumerate(zip(core.LABELS,inputs,expected))]
        unitwords=[0xbff0000000000000,0]
        v=core.execute_graph(limbs,unitwords,ops)
        self.assertEqual(v['status'],'FAIL_RETAINED_NODE_BITS');self.assertEqual(v['node_word_mismatches'],['bc'])
        self.assertEqual(v['nodes'][5]['output_uint64'],2**63)
        self.assertTrue(v['nodes'][5]['zero_sign_only_mismatch'])
        self.assertEqual(v['product_uint64'],[neg,0])
        DATA['signed_zero_control']={'scope':'synthetic partial-stage control, not scene or bound admission',
            'limbs_uint32':limbs,'unit_uint64':unitwords,'reference_ops':ops,'actual':v,
            'FAIL_preserved':True,'native_signed_zero_graph_equivalence_proved':False}
    def test_rejections_before_execution(self):
        rejected=[];DATA['rejections']=rejected
        def reject(label,fn):
            with self.assertRaises((ValueError,TypeError,KeyError,IndexError)) as cm:fn()
            rejected.append({'label':label,'reason':str(cm.exception)})
        mutations=[
          ('stale_context',lambda ctx,c,p:ctx.__setitem__('input_packet_sha256','0'*64)),
          ('source_id',lambda ctx,c,p:p.__setitem__('source_id','other')),
          ('source_certificate_absent',lambda ctx,c,p:c.__setitem__(core.prev.FLAG,False)),
          ('certificate_promotion',lambda ctx,c,p:c['proof'].__setitem__('native_kernel_implemented',True)),
          ('input_binding',lambda ctx,c,p:c['proof'].__setitem__('original_input_packet_sha256','0'*64)),
          ('gauge_binding',lambda ctx,c,p:c['proof'].__setitem__('ORIGINAL_assignment_sha256','0'*64)),
          ('product_SHA',lambda ctx,c,p:c['proof'].__setitem__('retained_product_row_sha256','0'*64)),
          ('ORIGINAL_source_word',lambda ctx,c,p:c['proof']['fixed_original_source_uint64'].__setitem__(0,0)),
          ('source_gauge',lambda ctx,c,p:p.__setitem__('phase_reference_id','other')),
          ('terminal_gauge',lambda ctx,c,p:p.__setitem__('terminal_reference_id','other')),
          ('missing_witness',lambda ctx,c,p:p['encoded_corner_products'].pop()),
          ('encoded_SOURCE_word',lambda ctx,c,p:c['proof']['source_hilo_uint32'].__setitem__(0,0)),
          ('encoder_SHA',lambda ctx,c,p:c['proof'].__setitem__('retained_encoder_sha256','0'*64)),
          ('SOURCE_subnormal',lambda ctx,c,p:[x['source_encoder']['source_limb_uint32'].__setitem__(0,1) for x in p['encoded_corner_products']]),
          ('unit_nonfinite',lambda ctx,c,p:p['encoded_corner_products'][0]['unit_uint64'].__setitem__(0,0x7ff0000000000000))]
        for label,mut in mutations:
            ctx,c,p=copy.deepcopy((self.ctx,self.certificate,self.product));mut(ctx,c,p)
            if label!='product_SHA':c['proof']['retained_product_row_sha256']=core.digest(p)
            reject(label,lambda ctx=ctx,c=c,p=p:core.bind_fixture(self.packets[self.n],ctx,0,c,p))
        for label,w,b in [('bool_word',True,64),('uint_overflow',2**64,64),('SOURCE_subnormal_primitive',1,32),
                          ('unit_subnormal_primitive',1,64),('unit_NaN',0x7ff8000000000000,64)]:
            reject(label,lambda w=w,b=b:core.value(w,b))
        corner=self.product['encoded_corner_products'][0]
        for label,mut in [('node_order',lambda ops:ops[2].__setitem__('label','ad')),
                         ('FMA_graph',lambda ops:ops[2].__setitem__('op','fma')),
                         ('operand_substitution',lambda ops:ops[0].__setitem__('inputs',[[0,1],[0,1]]))]:
            ops=copy.deepcopy(corner['operations']);mut(ops)
            reject(label,lambda ops=ops:core.execute_graph(corner['source_encoder']['source_limb_uint32'],corner['unit_uint64'],ops))
        with patch.object(core,'load_retained',return_value=self.retained):
            for label,n,m in [('model',[self.n],'wrong'),('empty',[],core.MODEL),('duplicate',[self.n,self.n],core.MODEL),('unknown',['unknown'],core.MODEL)]:
                reject(label,lambda n=n,m=m:core.audit_source_float64_stage_CPU(n,model=m))
            with patch.object(core,'runtime_probe',return_value={'PASS':False}):
                reject('runtime_probe_FAIL',lambda:core.audit_source_float64_stage_CPU([self.n],model=core.MODEL))
        read=Path.read_bytes;target=core.io.ROOT/core.PREVIOUS
        with patch.object(Path,'read_bytes',lambda p:read(p)+b' ' if p==target else read(p)):
            reject('predecessor_SHA',core.load_retained)
    def test_binding_does_not_mutate_or_execute(self):
        packet=self.packets[self.n];before=core.digest((packet,self.ctx,self.certificate,self.product))
        with patch.object(core,'execute_graph',side_effect=AssertionError('no CPU operation allowed in binding')):
            corners=core.bind_fixture(packet,self.ctx,0,self.certificate,self.product)
        self.assertEqual(len(corners),4);self.assertEqual(before,core.digest((packet,self.ctx,self.certificate,self.product)))
if __name__=='__main__':
    r=unittest.TextTestRunner(verbosity=2,stream=sys.stderr).run(unittest.defaultTestLoader.loadTestsFromTestCase(FloatStageTests))
    print(json.dumps({'PASS':r.wasSuccessful(),'tests':r.testsRun,'data':DATA},sort_keys=True,separators=(',',':'),allow_nan=False))
    raise SystemExit(0 if r.wasSuccessful() else 1)

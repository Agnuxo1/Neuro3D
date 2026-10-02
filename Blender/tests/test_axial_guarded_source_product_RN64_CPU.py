"""New bounded CPU source stage tests; prior numerical producers never replayed."""
import copy,json,sys,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'benchmarks'/'capacity_audit'))
import axial_guarded_source_product_RN64_CPU_v1 as core
DATA={}
class SourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.retained=core.load_retained();cls.names=list(cls.retained[0])
    def reject(self,label,fn,rows):
        try:fn()
        except (ValueError,KeyError,TypeError,OverflowError) as e:rows.append({'label':label,'reason':str(e)})
        else:self.fail('expected STOP: '+label)
    def test_a_main(self):
        with patch.object(core,'load_retained',return_value=self.retained),patch.object(core.prior,'execute',side_effect=AssertionError('no old Horner execution')),patch.object(core.prior.prior,'execute',side_effect=AssertionError('no old argument execute')),patch.object(core.transport,'encode_source',side_effect=AssertionError('no old source encoder')),patch.object(core.transport,'product_prefix',side_effect=AssertionError('no old source product')),patch.object(core,'native_cast32',wraps=core.native_cast32) as cast,patch.object(core,'native_subtract',wraps=core.native_subtract) as sub,patch.object(core,'native_add',wraps=core.native_add) as add,patch.object(core,'native_multiply',wraps=core.native_multiply) as mul:
            a=core.audit_source_CPU(self.names,model=core.MODEL)
            self.assertEqual((cast.call_count,sub.call_count,add.call_count,mul.call_count),(8,4,8,8))
        self.assertEqual(a['new_point_sources_executed'],2);self.assertEqual(a['retained_sources_not_executed'],17)
        for c in a['cases'].values():
            for row in c['sources']:
                self.assertEqual(row['status'],'STOP');self.assertTrue(all(row[n] is False for n in core.FALSE))
                if row[core.FLAG]:
                    self.assertEqual(len(row['result']['detailed_source_charges_L1']),14)
                    self.assertFalse(row['result']['source_amplitude_budget_admitted'])
        DATA['audit']=a
    def test_b_preflight(self):
        names=['nonexact_geometry_phase_PASS','thin_resolved'];changes=[]
        def change(label,f):
            r=copy.deepcopy(self.retained);f(r);changes.append((label,r))
        def row(r):return r[1]['cases']['thin_resolved']['sources'][0]
        change('second_context',lambda r:r[1]['cases']['thin_resolved']['context'].__setitem__('scene_binding_sha256','0'*64))
        change('foreign_gauge',lambda r:row(r).__setitem__('phase_reference_id','foreign'))
        change('unit_word',lambda r:row(r)['result']['unit_uint64'].__setitem__(0,row(r)['result']['unit_uint64'][0]+1))
        change('unit_node',lambda r:row(r)['result']['nodes'][1].__setitem__('output_uint64',row(r)['result']['nodes'][1]['output_uint64']+1))
        change('unit_charge',lambda r:row(r)['result']['unit_L1_charges_to_FIXED_ORIGINAL'].__setitem__('Taylor_L1',[0,1]))
        change('phase_cap',lambda r:row(r)['result'].__setitem__('unchanged_phase_cap_rad',[1,1]))
        change('boolean_cap',lambda r:row(r)['result'].__setitem__('unchanged_phase_cap_rad',[True,10**12]))
        change('integer_bit_policy',lambda r:row(r)['result'].__setitem__('quarter_bit_permutation_executed',1))
        change('promotion',lambda r:row(r).__setitem__(core.FALSE[0],True))
        change('source_order',lambda r:row(r).__setitem__('source_id','foreign'))
        rows=[]
        with patch.object(core,'native_cast32',side_effect=AssertionError('ALL cases before first new cast')) as native:
            for label,r in changes:
                with patch.object(core,'load_retained',return_value=r):
                    self.reject(label,lambda:core.audit_source_CPU(names,model=core.MODEL),rows)
            with patch.object(core,'PREVIOUS_SHA','0'*64):
                self.reject('predecessor_SHA',core.load_retained,rows)
            self.assertEqual(native.call_count,0)
        DATA['preflight_rejections']={'rejections':rows,'new_CPU_ops':0,'prior_case_also_not_executed':True}
    def test_c_controls(self):
        base=DATA['audit']['cases']['thin_resolved']['sources'][0]['admission'];controls=[]
        for i,field in enumerate(([0.0,0.0],[0.0,-0.0],[-0.0,0.0],[-0.0,-0.0],[1.0000000596046448,-1.0000001788139343],[.123456789,-.987654321],[1.0,-1.0])):
            a=copy.deepcopy(base);a['ORIGINAL_source_uint64']=[core.source.word(x) for x in field]
            a['unit_uint64']=[core.source.word(-1.0),1<<63];a['unit_L1_charges']={n:[0,1] for n in core.UNIT_NAMES};a['unit_L1_bound']=[0,1]
            v=core.execute(a);controls.append({'label':'scalar_'+str(i),'admission':a,'result':v,'scope':'synthetic scalar only, no scene promotion'})
            self.assertFalse(v['zero_canonicalization_performed'])
        DATA['scalar_controls']=controls;fails=[]
        for label,stage in [('wrong_high_RN32','native_cast32'),('wrong_residual_RN64','native_subtract'),('wrong_decode_RN64','native_add'),('wrong_product_RN64','native_multiply')]:
            fn=getattr(core,stage);attempts=[];rows=[]
            def wrong(*args,fn=fn,stage=stage):
                good=fn(*args)
                if stage=='native_cast32':
                    _,w=good;attempts.append({'correct_word':w,'forged_word':w+1,'width':32});return core.source.value(w+1,32),w+1
                w=core.source.word(good);attempts.append({'correct_word':w,'forged_word':w+1,'width':64});return core.source.value(w+1,64)
            with patch.object(core,stage,side_effect=wrong) as bad:
                self.reject(label,lambda:core.execute(base),rows);self.assertEqual(bad.call_count,1)
            fails.append({'label':label,'admission':base,'attempts':attempts,'reason':rows[0]['reason']})
        edge=[]
        for label,x in [('cast_overflow',float(2**200)),('selected_binary32_subnormal',2.0**-140)]:
            a=copy.deepcopy(base);a['ORIGINAL_source_uint64']=[core.source.word(x),core.source.word(0.0)]
            with patch.object(core,'native_add',side_effect=AssertionError('no decode after encode STOP')) as native:
                self.reject(label,lambda:core.execute(a),edge);self.assertEqual(native.call_count,0)
        DATA['runtime_FAILs']=fails;DATA['encoding_edge_STOPs']=edge
    def test_d_typed(self):
        rows=[];base=DATA['audit']['cases']['thin_resolved']['sources'][0]['admission']
        with patch.object(core,'load_retained',return_value=self.retained):
            for label,ns,m in [('model',['thin_resolved'],'bad'),('empty',[],core.MODEL),('duplicate',['thin_resolved']*2,core.MODEL),('unknown',['absent'],core.MODEL)]:
                self.reject(label,lambda ns=ns,m=m:core.audit_source_CPU(ns,model=m),rows)
        changes=[('source_bool',lambda a:a['ORIGINAL_source_uint64'].__setitem__(0,True)),
          ('source_nan',lambda a:a['ORIGINAL_source_uint64'].__setitem__(0,0x7ff8000000000001)),
          ('source_subnormal',lambda a:a['ORIGINAL_source_uint64'].__setitem__(1,1)),
          ('source_length',lambda a:a['ORIGINAL_source_uint64'].pop()),
          ('unit_bool',lambda a:a['unit_uint64'].__setitem__(0,True)),
          ('unit_subnormal',lambda a:a['unit_uint64'].__setitem__(0,1)),
          ('charge_missing',lambda a:a['unit_L1_charges'].pop(core.UNIT_NAMES[0])),
          ('charge_negative',lambda a:a['unit_L1_charges'].__setitem__(core.UNIT_NAMES[0],[-1,1])),
          ('charge_bool',lambda a:a['unit_L1_charges'].__setitem__(core.UNIT_NAMES[0],[True,1])),
          ('total_wrong',lambda a:a.__setitem__('unit_L1_bound',[0,1]))]
        with patch.object(core,'native_cast32',side_effect=AssertionError('typed before CPU')) as native:
            for label,f in changes:
                a=copy.deepcopy(base);f(a);self.reject(label,lambda a=a:core.execute(a),rows)
            self.assertEqual(native.call_count,0)
        DATA['typed_rejections']={'rejections':rows,'new_CPU_ops':0}
if __name__=='__main__':
    r=unittest.TextTestRunner(verbosity=2,stream=sys.stderr).run(unittest.defaultTestLoader.loadTestsFromTestCase(SourceTests))
    print(json.dumps({'PASS':r.wasSuccessful(),'tests':r.testsRun,'data':DATA},sort_keys=True,separators=(',',':'),allow_nan=False))
    raise SystemExit(0 if r.wasSuccessful() else 1)

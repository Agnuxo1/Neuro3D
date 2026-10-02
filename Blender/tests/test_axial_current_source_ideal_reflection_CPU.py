"""Fresh CPU ideal reflection verification on SHA-retained current source evidence."""
import copy,json,struct,sys,unittest
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'benchmarks/capacity_audit'))
import axial_current_source_ideal_reflection_CPU_v1 as core
DATA={}
class ReflectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.loaded=core.load_retained();cls.names=list(cls.loaded[1]['cases'])
    def reject(self,label,fn,rows):
        try:fn()
        except (ValueError,KeyError,TypeError,IndexError) as e:rows.append({'label':label,'reason':str(e)})
        else:self.fail('expected STOP: '+label)
    def test_a_current_reflection(self):
        before=core.digest(self.loaded)
        with ExitStack() as stack:
            stack.enter_context(patch.object(core,'load_retained',return_value=self.loaded))
            stack.enter_context(patch.object(core.prior,'load_retained',return_value=self.loaded[0]))
            for mod,key in ((core.prior.bridge.prior,'execute'),(core.prior.bridge.prior,'native_cast32'),
                            (core.prior.bridge.prior,'native_add'),(core.prior.bridge.prior.prior,'execute'),
                            (core.prior.original,'trace_original')):
                stack.enter_context(patch.object(mod,key,side_effect=AssertionError('no old producers/stages/retrace')))
            a=core.audit_reflection_CPU(self.names,model=core.MODEL)
        self.assertEqual(core.digest(self.loaded),before)
        self.assertEqual((a['new_ideal_reflected_sources'],a['retained_sources_not_executed'],a['new_main_CPU_unary_negations'],a['new_probe_CPU_unary_negations']),(2,17,4,4))
        for c in a['cases'].values():
            self.assertEqual(c['status'],'STOP');self.assertTrue(all(c[n] is False for n in core.FALSE+core.TRUE))
            for r in c['sources']:
                self.assertTrue(all(r[n] is False for n in core.FALSE))
                self.assertIsNone(r['executed_material_quota_fits'])
                if r[core.FLAG]:
                    v=r['result'];self.assertEqual(v['reflected_uint64'],[w^core.SIGN for w in v['input_uint64']])
                    self.assertEqual(v['fifteen_source_material_charges_L1']['ideal_material_L1'],[0,1])
                    self.assertTrue(all(v[n] is True for n in core.TRUE));self.assertEqual(v['new_main_CPU_unary_negations'],2)
        DATA['audit']=a
    def test_b_atomic_admission(self):
        rows=[];names=['nonexact_geometry_phase_PASS','thin_resolved']
        def row(r):return r[1]['cases']['thin_resolved']['sources'][0]
        changes=[
            ('current_source_word',lambda r:row(r)['current_bare_source_uint64'].__setitem__(0,row(r)['current_bare_source_uint64'][0]+1)),
            ('phase_subnormal',lambda r:row(r)['material_profile'].__setitem__('mirror_phase_ORIGINAL_uint64',1)),
            ('foreign_hit_owner',lambda r:row(r)['material_profile']['selected_hit_chain'][0].__setitem__('owner',1)),
            ('gauge',lambda r:row(r).__setitem__('phase_reference_id','foreign')),
            ('upstream_charge',lambda r:row(r)['fourteen_source_charges_L1'].__setitem__('source_encoding_L1',[0,1])),
            ('profile_promoted',lambda r:row(r).__setitem__('material_executed',True)),
            ('integer_eligibility',lambda r:row(r).__setitem__('source_profile_admitted_HOST_only',1)),
            ('root_SHA',lambda r:row(r).__setitem__('retained_root_row_sha256','0'*64)),
        ]
        with patch.object(core.prior,'load_retained',return_value=self.loaded[0]),patch.object(core,'native_negate',side_effect=AssertionError('ALL preflight before ANY native operation')) as native:
            for label,f in changes:
                r=copy.deepcopy(self.loaded);f(r)
                with patch.object(core,'load_retained',return_value=r):
                    self.reject(label,lambda:core.audit_reflection_CPU(names,model=core.MODEL),rows)
            for label,n,m in [('model',names,'bad'),('empty',[],core.MODEL),('duplicate',names*2,core.MODEL),('unknown',['foreign'],core.MODEL)]:
                with patch.object(core,'load_retained',return_value=self.loaded):
                    self.reject(label,lambda n=n,m=m:core.audit_reflection_CPU(n,model=m),rows)
            with patch.object(core,'PREVIOUS_SHA','0'*64):
                self.reject('parent_SHA',core.load_retained,rows)
            self.assertEqual(native.call_count,0)
        DATA['atomic_rejections']={'rows':rows,'native_calls':0}
    def test_c_native_controls_and_failure(self):
        words=[0,core.SIGN,0x3ff0000000000000,0xbff0000000000000,0x0010000000000000,0x8010000000000000,0x3fb999999999999a,0xbfb999999999999a]
        output=[core.native_negate(w) for w in words];self.assertEqual(output,[w^core.SIGN for w in words])
        DATA['scalar_controls']={'input_uint64':words,'output_uint64':output,'new_test_CPU_unary_negations':8}
        row=self.loaded[1]['cases']['thin_resolved']['sources'][0];a=core.admit(row);rejects=[]
        calls=[]
        def fail_probe(w):
            calls.append(w);return w # deliberately wrong; MUST not reach main source operations
        with patch.object(core,'load_retained',return_value=self.loaded),patch.object(core.prior,'load_retained',return_value=self.loaded[0]),patch.object(core,'native_negate',side_effect=fail_probe):
            self.reject('runtime_probe_identity_FAIL',lambda:core.audit_reflection_CPU(['thin_resolved'],model=core.MODEL),rejects)
        self.assertEqual(calls,[0,core.SIGN,0x3ff0000000000000,0xbff0000000000000])
        with patch.object(core,'native_negate',side_effect=lambda w:w):
            self.reject('wrong_main_unary_minus',lambda:core.execute(a),rejects)
        with patch.object(core,'native_negate',return_value=False):
            self.reject('bool_native_word',lambda:core.execute(a),rejects)
        for label,w in [('subnormal_input',1),('nonfinite_input',0x7ff0000000000000),('bool_input',True)]:
            self.reject(label,lambda w=w:core.native_negate(w),rejects)
        DATA['native_FAILURE_controls']={'rejections':rejects,'probe_FAIL_native_calls':4,'main_calls_after_probe_FAIL':0}
    def test_d_admission_typed(self):
        row=self.loaded[1]['cases']['thin_resolved']['sources'][0];rejects=[]
        changes=[
            ('bool_phase',lambda r:r['material_profile'].__setitem__('mirror_phase_ORIGINAL_uint64',False)),
            ('integer_profile_bool',lambda r:r['material_profile'].__setitem__('profile_admitted_HOST_only',1)),
            ('invented_prior_charge0',lambda r:r.__setitem__('executed_material_charge_L1',[0,1])),
            ('bool_source_charge',lambda r:r['fourteen_source_charges_L1'].__setitem__('source_encoding_L1',[True,1])),
            ('missing_source_charge',lambda r:r['fourteen_source_charges_L1'].pop('source_encoding_L1')),
            ('negative_source_charge',lambda r:r['fourteen_source_charges_L1'].__setitem__('source_encoding_L1',[-1,1])),
            ('source_sum_laundered',lambda r:r.__setitem__('partial_bare_source_bound_L1',[0,1])),
        ]
        for label,f in changes:
            r=copy.deepcopy(row);f(r);self.reject(label,lambda r=r:core.admit(r),rejects)
        DATA['typed_rejections']=rejects
if __name__=='__main__':
    r=unittest.TextTestRunner(verbosity=2,stream=sys.stderr).run(unittest.defaultTestLoader.loadTestsFromTestCase(ReflectionTests))
    print(json.dumps({'PASS':r.wasSuccessful(),'tests':r.testsRun,'data':DATA},sort_keys=True,separators=(',',':'),allow_nan=False))
    raise SystemExit(0 if r.wasSuccessful() else 1)

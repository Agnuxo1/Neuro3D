"""P0 guard regression tests: no old scientific producer or arithmetic replay."""
import copy,json,sys,unittest
from pathlib import Path
from unittest.mock import patch
from fractions import Fraction as F
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'benchmarks/capacity_audit'))
import axial_geometry_decode_guard_CPU_v1 as core
DATA={}
class GuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.retained=core.load_retained();cls.packets,cls.old,cls.pins,cls.controls=cls.retained
    def snapshot(self):return core.original.snapshot_from_packet(self.packets['thin_resolved'],self.old['cases']['thin_resolved']['context'])[0]
    def encoder(self):return copy.deepcopy(self.old['cases']['thin_resolved']['sources'][0]['encoder'])
    def forge(self,enc,j=0):
        r=enc['records'][j];r['decoded_uint64']=r['decoded_uint64']+1 if r['decoded_uint64'] else 0x3ff0000000000000
        val=core.bits(r['decoded_uint64'],64);q=core.bits(r['original_uint64'],64);sm=F(*r['represented_exact_sum'])
        r['decode_RN64_delta']=core.pair(val-sm);r['decoded_coordinate_error_abs']=core.pair(abs(val-q))
        return enc
    def test_a_guarded_decode(self):
        before=core.digest(self.retained)
        with patch.object(core,'load_retained',return_value=self.retained),patch.object(core.prior,'encode_geometry',side_effect=AssertionError('old encoder forbidden')),patch.object(core.original,'trace_original',side_effect=AssertionError('old traversal forbidden')),patch.object(core.prior,'audit_geometry_CPU',side_effect=AssertionError('old audit forbidden')):
            a=core.audit_guard_CPU(self.old['case_order'],model=core.MODEL)
        DATA['audit']=a
        self.assertEqual(core.digest(self.retained),before)
        self.assertEqual((a['guarded_sources_executed'],a['retained_sources_not_executed'],a['inherited_pins_verified'],a['new_native_decode_adds']),(2,17,338,76))
        self.assertEqual(a['new_encoder_casts_subtractions'],0)
        for case in a['cases'].values():
            for r in case['sources']:
                self.assertEqual(r['status'],'STOP')
                for k in core.FALSE:self.assertFalse(r[k])
        self.assertFalse(a['cases']['two_sources']['sources'][1][core.FLAG])
    def test_b_self_consistent_forgery(self):
        snap=self.snapshot();enc=self.forge(self.encoder())
        # Read-only old deserializer accepts a forged decoded word plus coherent ledger.
        dec=core.prior.decode_geometry(snap,0,enc)
        self.assertEqual(core.source.word(core.prior.get(dec,enc['records'][0]['path'])),enc['records'][0]['decoded_uint64'])
        with patch.object(core,'native_add',side_effect=AssertionError('must reject before native add')) as mock:
            with self.assertRaises(ValueError) as cm:core.decode_guarded(snap,0,enc)
            self.assertEqual(mock.call_count,0)
        DATA['forged_decode_control']={'encoder':enc,'old_deserializer_accepted':True,'old_point_audit_not_reexecuted_or_invalidated':True,
            'new_guard_rejected':True,'new_native_adds_before_rejection':0,'reason':str(cm.exception),'forged_decoded_snapshot_digest':core.digest(dec)}
    def test_c_rejections(self):
        rejected=[];DATA['rejections']=rejected;snap=self.snapshot()
        def reject(label,fn):
            with patch.object(core,'native_add',side_effect=AssertionError('admission must be atomic')) as mock:
                with self.assertRaises((ValueError,TypeError,KeyError,IndexError)) as cm:fn()
                self.assertEqual(mock.call_count,0)
            rejected.append({'label':label,'reason':str(cm.exception),'native_adds_before_rejection':0})
        for label,mut in [
            ('last_record_forged',lambda e:self.forge(e,-1)),('residual_word_forged',lambda e:e['records'][0].__setitem__('residual_uint64',e['records'][0]['residual_uint64']+1)),
            ('high_word_bool',lambda e:e['records'][0].__setitem__('high_uint32',True)),('decoded_word_bool',lambda e:e['records'][0].__setitem__('decoded_uint64',True)),
            ('low_word_nonfinite',lambda e:e['records'][0].__setitem__('low_uint32',0x7f800000)),('low_word_subnormal',lambda e:e['records'][0].__setitem__('low_uint32',1)),
            ('negative_decoded_word',lambda e:e['records'][0].__setitem__('decoded_uint64',-1)),('decoded_wrong_sign',lambda e:e['records'][0].__setitem__('decoded_uint64',e['records'][0]['decoded_uint64']^(1<<63))),
            ('charge_bool',lambda e:e['records'][0].__setitem__('encoding_error_abs',[True,2**55])),('rational_noncanonical',lambda e:e['records'][0].__setitem__('encoding_error_abs',[2,2**56])),
            ('charge_mismatch',lambda e:e['records'][0].__setitem__('encoding_error_abs',[0,1])),('path_bool',lambda e:e['records'][0]['path'].__setitem__(-1,False)),
            ('path_duplicate',lambda e:e['records'][1].__setitem__('path',e['records'][0]['path'])),('missing_record',lambda e:e['records'].pop()),
            ('source_index_bool',lambda e:e.__setitem__('source_index',False)),('byte_count_bool',lambda e:e.__setitem__('transport_bytes',True)),
            ('transport_SHA',lambda e:e.__setitem__('transport_le_sha256','0'*64)),('transport_bytes',lambda e:e.__setitem__('transport_le_base64','AAAA')),
            ('snapshot_digest',lambda e:e.__setitem__('original_snapshot_digest','0'*64))]:
            e=self.encoder();mut(e);reject(label,lambda e=e:core.decode_guarded(snap,0,e))
        with patch.object(core,'load_retained',return_value=self.retained):
            for label,ns,m in [('model',['thin_resolved'],'bad'),('empty',[],core.MODEL),('duplicate',['thin_resolved']*2,core.MODEL),('unknown',['unknown'],core.MODEL)]:
                reject(label,lambda ns=ns,m=m:core.audit_guard_CPU(ns,model=m))
            with patch.object(core.prior.prior,'runtime_probe',return_value={'PASS':False}),patch.object(core,'admit',side_effect=AssertionError('runtime guard before admission')):
                reject('runtime_FAIL',lambda:core.audit_guard_CPU(['thin_resolved'],model=core.MODEL))
        old=copy.deepcopy(self.old);old['cases']['thin_resolved']['context']['input_packet_sha256']='0'*64
        with patch.object(core,'load_retained',return_value=(self.packets,old,self.pins,self.controls)):
            reject('stale_INPUT',lambda:core.audit_guard_CPU(['thin_resolved'],model=core.MODEL))
        read=Path.read_bytes;target=core.io.ROOT/core.PREVIOUS
        with patch.object(Path,'read_bytes',lambda p:read(p)+b' ' if p==target else read(p)):
            reject('predecessor_SHA',core.load_retained)
    def test_d_signed_zero_rounding_controls(self):
        DATA['scalar_admission_controls']=[{'record':c,'validation':core.validate_scalar(c,c['original_uint64'])} for c in self.controls]
        self.assertEqual(self.controls[0]['original_uint64'],1<<63)
        self.assertEqual(self.controls[0]['decoded_uint64'],0)
        rejected=[]
        for label,q,w,width,sign in [('tie_odd',F(1)+F(1,2**24),0x3f800001,32,0),('zero_wrong_sign',F(0),1<<63,64,0),('zero_above_midpoint',F(1,2**149),0,32,0)]:
            with self.assertRaises(ValueError) as cm:core.check_RN(q,w,width,sign)
            rejected.append({'label':label,'reason':str(cm.exception)})
        core.check_RN(F(1)+F(1,2**24),0x3f800000,32,0)
        DATA['midpoint_controls']={'rejects':rejected,'even_tie_accepted':True,'odd_tie_rejected':True}
if __name__=='__main__':
    r=unittest.TextTestRunner(verbosity=2,stream=sys.stderr).run(unittest.defaultTestLoader.loadTestsFromTestCase(GuardTests))
    print(json.dumps({'PASS':r.wasSuccessful(),'tests':r.testsRun,'data':DATA},sort_keys=True,separators=(',',':'),allow_nan=False))
    raise SystemExit(0 if r.wasSuccessful() else 1)

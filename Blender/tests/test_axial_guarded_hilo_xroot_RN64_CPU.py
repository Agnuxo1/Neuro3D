"""New retained transport consumer test; old encoder/audits forbidden."""
import copy,json,sys,unittest
from pathlib import Path
from fractions import Fraction as F
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'benchmarks/capacity_audit'))
import axial_guarded_hilo_xroot_RN64_CPU_v1 as core
DATA={}
class HiloXrootTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.retained=core.load_retained();cls.packets,cls.old,cls.chain,cls.pins=cls.retained
    def test_a_new_consumer(self):
        before=core.digest(self.retained)
        with patch.object(core,'load_retained',return_value=self.retained),patch.object(core.guard.prior,'encode_geometry',side_effect=AssertionError('retained encoder not replayed')),patch.object(core.prior,'audit_Xroot_CPU',side_effect=AssertionError('old Xroot audit forbidden')),patch.object(core.prior.retained.prior,'execute_prefix',side_effect=AssertionError('old chain forbidden')):
            a=core.audit_hilo_Xroot_CPU(self.old['case_order'],model=core.MODEL)
        self.assertEqual(core.digest(self.retained),before);DATA['audit']=a
        self.assertEqual((a['new_point_sources_executed'],a['retained_sources_not_executed'],a['new_guard_decode_adds'],a['new_fixed_and_decoded_rational_root_records']),(2,17,76,32))
        self.assertEqual(a['new_Xroot_RN64_operation_counts'],{'subtract':18,'add':6,'negate':8})
        self.assertEqual(a['inherited_pins_verified'],353)
        for name,c in a['cases'].items():
            for r in c['sources']:
                self.assertEqual(r['status'],'STOP')
                for key in core.FALSE:self.assertIs(r[key],False)
                if r[core.FLAG]:
                    res=r['result'];comp=res['composition']
                    self.assertTrue(comp['length_wavelength_only_phase_charge_fits_cap'])
                    self.assertTrue(comp['quarter_point_interval_certified'])
                    self.assertEqual(F(*comp['phase_length_wavelength_only_bound_rad']),sum((F(*v) for v in comp['phase_length_wavelength_charges_rad'].values()),F(0)))
                    self.assertEqual(res['guarded_decode']['decoded_snapshot_digest'],core.digest(res['decoded_snapshot']))
                    self.assertEqual(res['retained_geometry_encoder'],self.chain['cases'][name]['sources'][0]['result']['geometry_encoder'])
        thin=a['cases']['thin_resolved']['sources'][0]['result']
        self.assertEqual(thin['new_decoded_Xroot_result']['fixed_ORIGINAL_reference']['hits'][0]['segment_BU'],[1,2**30])
    def test_b_all_transport_preflight(self):
        chain=copy.deepcopy(self.chain)
        enc=chain['cases']['thin_resolved']['sources'][0]['result']['geometry_encoder']
        rec=enc['records'][-1];rec['decoded_uint64']=core.source.word(1.0)
        decoded=core.guard.bits(rec['decoded_uint64'],64);orig=core.guard.bits(rec['original_uint64'],64);sm=F(*rec['represented_exact_sum'])
        rec['decode_RN64_delta']=core.pair(decoded-sm);rec['decoded_coordinate_error_abs']=core.pair(abs(decoded-orig))
        with patch.object(core,'load_retained',return_value=(self.packets,self.old,chain,self.pins)),patch.object(core.guard,'native_add',side_effect=AssertionError('ALL records before first CPU add')) as decode,patch.object(core.prior,'native_sub',side_effect=AssertionError('no root before guard')) as root,patch.object(core.original,'trace_original',side_effect=AssertionError('no reference before guard')) as trace:
            with self.assertRaises(ValueError) as cm:core.audit_hilo_Xroot_CPU(['nonexact_geometry_phase_PASS','thin_resolved'],model=core.MODEL)
            self.assertEqual((decode.call_count,root.call_count,trace.call_count),(0,0,0))
        DATA['forgery_rejection']={'encoder':enc,'reason':str(cm.exception),'decode_adds':0,'Xroot_subs':0,'rational_reference_records':0,'prior_case_also_not_executed':True}
    def test_c_native_decode_FAIL(self):
        called=[];orig=core.guard.native_add
        def wrong(h,l):
            v=orig(h,l);w=core.source.word(v);bad=w+1
            called.append({'input_uint32':[h,l],'correct_uint64':w,'forged_uint64':bad})
            return core.source.value(bad,64)
        with patch.object(core,'load_retained',return_value=self.retained),patch.object(core.guard,'native_add',side_effect=wrong),patch.object(core.prior,'native_sub',side_effect=AssertionError('decode FAIL before root')) as root,patch.object(core.original,'trace_original',side_effect=AssertionError('decode FAIL before reference')) as trace:
            with self.assertRaises(ValueError) as cm:core.audit_hilo_Xroot_CPU(['thin_resolved'],model=core.MODEL)
            self.assertEqual((root.call_count,trace.call_count),(0,0))
        self.assertEqual(len(called),1)
        DATA['runtime_decode_FAIL']={'reason':str(cm.exception),'attempts':called,'new_decode_adds_attempted':1,'new_Xroot_ops':0,'reference_records':0}
    def test_d_admission_and_cap_FAIL(self):
        rejects=[]
        def reject(label,fn):
            with self.assertRaises((ValueError,TypeError,KeyError)) as cm:fn()
            rejects.append({'label':label,'reason':str(cm.exception)})
        with patch.object(core,'load_retained',return_value=self.retained):
            for label,names,m in [('model',['thin_resolved'],'bad'),('empty',[],core.MODEL),('duplicate',['thin_resolved']*2,core.MODEL),('unknown',['absent'],core.MODEL)]:
                reject(label,lambda ns=names,m=m:core.audit_hilo_Xroot_CPU(ns,model=m))
        old=copy.deepcopy(self.old);old['cases']['thin_resolved']['context']['input_packet_sha256']='0'*64
        with patch.object(core,'load_retained',return_value=(self.packets,old,self.chain,self.pins)),patch.object(core.guard,'native_add',side_effect=AssertionError('stale context before CPU')) as decode:
            reject('stale_context',lambda:core.audit_hilo_Xroot_CPU(['thin_resolved'],model=core.MODEL));self.assertEqual(decode.call_count,0)
        read=Path.read_bytes;target=core.io.ROOT/core.PREVIOUS
        with patch.object(Path,'read_bytes',lambda p:read(p)+b' ' if p==target else read(p)):
            reject('predecessor_SHA',core.load_retained)
        res=DATA['audit']['cases']['thin_resolved']['sources'][0]['result'];fixed=res['fixed_ORIGINAL_reference']
        for label,change in [('negative_rounding',lambda r:r['length_rounding_charges_BU'].__setitem__('selected_Xroot_rounding_BU',[-1,1])),('bool_rounding',lambda r:r['length_rounding_charges_BU'].__setitem__('selected_Xroot_rounding_BU',[True,1])),('missing_charge',lambda r:r['length_rounding_charges_BU'].pop('effective_add_rounding_BU')),('inconsistent_total',lambda r:r.__setitem__('length_to_fixed_ORIGINAL_bound_BU',[0,1])),('quarter_mismatch',lambda r:r['fixed_ORIGINAL_reference'].__setitem__('quarter_index',99))]:
            r=copy.deepcopy(res['new_decoded_Xroot_result']);change(r)
            reject(label,lambda r=r:core.compose(fixed,r,1,[1,10**12]))
        reject('bool_sign',lambda:core.compose(fixed,res['new_decoded_Xroot_result'],True,[1,10**12]))
        reject('cap_inflation',lambda:core.compose(fixed,res['new_decoded_Xroot_result'],1,[1,1]))
        # Conservative larger valid rounding bound is a HOST-only synthetic control.
        r=copy.deepcopy(res['new_decoded_Xroot_result']);r['length_rounding_charges_BU']['selected_Xroot_rounding_BU']=[1,100]
        r['length_to_fixed_ORIGINAL_bound_BU']=core.pair(sum((F(*v) for v in r['length_rounding_charges_BU'].values()),F(0)))
        c=core.compose(fixed,r,1,[1,10**12])
        self.assertFalse(c['length_wavelength_only_phase_charge_fits_cap']);self.assertFalse(c['quarter_point_interval_certified'])
        DATA['conservative_cap_FAIL']={'root_result_majorant':r,'composition':c,'native_operations':0,'scope':'HOST larger majorant only; no caps relaxed/no node replay'}
        DATA['admission_rejections']=rejects
if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2,stream=sys.stderr).run(unittest.defaultTestLoader.loadTestsFromTestCase(HiloXrootTests))
    print(json.dumps({'PASS':result.wasSuccessful(),'tests':result.testsRun,'data':DATA},sort_keys=True,separators=(',',':'),allow_nan=False))
    raise SystemExit(0 if result.wasSuccessful() else 1)

"""New integration tests; guard precedes traversal, fixed scene/input, no old audits."""
import copy,json,sys,unittest
from pathlib import Path
from unittest.mock import patch
from fractions import Fraction as F
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'benchmarks/capacity_audit'))
import axial_guarded_scene_source_CPU_v1 as core
DATA={}
class ChainTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.retained=core.load_retained();cls.packets,cls.old,cls.src,cls.pins=cls.retained
    def test_a_new_chain(self):
        before=core.digest(self.retained)
        with patch.object(core,'load_retained',return_value=self.retained),patch.object(core.guard,'audit_guard_CPU',side_effect=AssertionError('old guard audit forbidden')),patch.object(core.geo,'audit_geometry_CPU',side_effect=AssertionError('old geometry audit forbidden')),patch.object(core.source_stage,'audit_ORIGINAL_source_CPU',side_effect=AssertionError('old source audit forbidden')):
            a=core.audit_chain_CPU(self.old['case_order'],model=core.MODEL)
        DATA['audit']=a;self.assertEqual(core.digest(self.retained),before)
        self.assertEqual((a['fresh_guarded_prefix_sources_executed'],a['retained_sources_not_executed'],a['inherited_pins_verified']),(2,17,343))
        self.assertEqual((a['new_geometry_RN32_casts'],a['new_geometry_RN64_subtractions'],a['new_geometry_encoder_decode_adds'],a['new_geometry_guard_native_decode_adds']),(152,76,76,76))
        self.assertEqual((a['new_exact_fixed_and_decoded_root_records'],a['new_Horner_RN64_nodes'],a['new_source_decode_product_nodes']),(32,52,16))
        for c in a['cases'].values():
            for r in c['sources']:
                self.assertEqual(r['status'],'STOP')
                for k in core.FALSE:self.assertFalse(r[k])
                if r[core.FLAG]:
                    res=r['result'];self.assertTrue(res['unit_composition']['phase_charge_fits_unchanged_cap'])
                    self.assertEqual(F(*res['point_bare_source_to_fixed_ORIGINAL_bound_L1']),sum(F(*v) for v in res['detailed_source_charges_L1'].values()))
                    self.assertFalse(res['old_numerical_capsule_used_as_argument_unit_source_input'])
        self.assertEqual(a['cases']['thin_resolved']['sources'][0]['result']['decoded_trace']['hits'][0]['segment_BU'],[1,2**30])
        self.assertFalse(a['cases']['two_sources']['sources'][1][core.FLAG])
    def test_b_forgery_blocks_traversal(self):
        enc_fn=core.geo.encode_geometry;captured=[]
        def forge(s,i):
            e=enc_fn(s,i);r=e['records'][0];r['decoded_uint64']+=1
            val=core.guard.bits(r['decoded_uint64'],64);q=core.guard.bits(r['original_uint64'],64);sm=F(*r['represented_exact_sum'])
            r['decode_RN64_delta']=core.pair(val-sm);r['decoded_coordinate_error_abs']=core.pair(abs(val-q));captured.append(e);return e
        snap,_=core.original.snapshot_from_packet(self.packets['thin_resolved'],self.old['cases']['thin_resolved']['context'])
        with patch.object(core.geo,'encode_geometry',side_effect=forge),patch.object(core.guard,'native_add',side_effect=AssertionError('guard must block all native decode')),patch.object(core.original,'trace_original',side_effect=AssertionError('traversal must not execute')) as trace,patch.object(core.unit_stage,'execute_unit',side_effect=AssertionError('unit must not execute')) as unit,patch.object(core.source_stage,'encode_source',side_effect=AssertionError('source must not execute')) as source:
            with self.assertRaises(ValueError) as cm:core.execute_prefix(snap,0,self.src['coefficient_profile'],[1,10**12])
            self.assertEqual((trace.call_count,unit.call_count,source.call_count),(0,0,0))
        DATA['forgery_control']={'geometry_encoder':captured[0],'reason':str(cm.exception),'new_encoder_scalars_before_rejection':38,
            'guard_native_adds':0,'fixed_and_decoded_root_records':0,'Horner_nodes':0,'source_encoder_product_nodes':0}
    def test_c_rejections(self):
        rejects=[];DATA['rejections']=rejects
        def reject(label,fn):
            with self.assertRaises((ValueError,TypeError,KeyError,IndexError)) as cm:fn()
            rejects.append({'label':label,'reason':str(cm.exception)})
        with patch.object(core,'load_retained',return_value=self.retained):
            for label,ns,m in [('model',['thin_resolved'],'bad'),('empty',[],core.MODEL),('duplicate',['thin_resolved']*2,core.MODEL),('unknown',['unknown'],core.MODEL)]:
                reject(label,lambda ns=ns,m=m:core.audit_chain_CPU(ns,model=m))
            with patch.object(core.source_stage,'runtime_probe',return_value={'PASS':False}),patch.object(core.geo,'encode_geometry',side_effect=AssertionError('runtime before encoder')):
                reject('runtime_FAIL',lambda:core.audit_chain_CPU(['thin_resolved'],model=core.MODEL))
        old=copy.deepcopy(self.old);old['cases']['thin_resolved']['context']['input_packet_sha256']='0'*64
        with patch.object(core,'load_retained',return_value=(self.packets,old,self.src,self.pins)):
            reject('stale_INPUT',lambda:core.audit_chain_CPU(['thin_resolved'],model=core.MODEL))
        src=copy.deepcopy(self.src);src['coefficient_profile']['cos'][0]['exact_rational']=[2,1]
        with patch.object(core,'load_retained',return_value=(self.packets,self.old,src,self.pins)),patch.object(core.geo,'encode_geometry',side_effect=AssertionError('coefficients before encoder')):
            reject('profile_mismatch',lambda:core.audit_chain_CPU(['thin_resolved'],model=core.MODEL))
        read=Path.read_bytes;target=core.io.ROOT/core.PREVIOUS
        with patch.object(Path,'read_bytes',lambda p:read(p)+b' ' if p==target else read(p)):
            reject('predecessor_SHA',core.load_retained)
        res=DATA['audit']['cases']['thin_resolved']['sources'][0]['result']
        for label,mut in [('geometry_charge_bool',lambda g,a,u:g.__setitem__('geometry_reference_wavelength_phase_bound_rad',[True,1])),('negative_geometry',lambda g,a,u:g.__setitem__('geometry_reference_wavelength_phase_bound_rad',[-1,1])),('argument_charge_mismatch',lambda g,a,u:a.__setitem__('phase_error_bound_rad',[0,1])),('unit_argument_mismatch',lambda g,a,u:u.__setitem__('argument_uint64',u['argument_uint64']+1)),('unit_phase_identity',lambda g,a,u:u.__setitem__('point_polynomial_phase_bound_rad',[0,1]))]:
            g,a,u=[copy.deepcopy(res[k]) for k in ('geometry_composition','decoded_argument','unit')];mut(g,a,u)
            reject(label,lambda g=g,a=a,u=u:core.compose(g,a,u,[1,10**12]))
        reject('cap_inflation',lambda:core.compose(res['geometry_composition'],res['decoded_argument'],res['unit'],[1,1]))
        reject('cap_bool',lambda:core.compose(res['geometry_composition'],res['decoded_argument'],res['unit'],[True,10**12]))
    def test_d_cap_FAIL_preserved(self):
        res=DATA['audit']['cases']['thin_resolved']['sources'][0]['result'];u=copy.deepcopy(res['unit'])
        B=F(1,100);u['point_polynomial_L1_to_ideal_represented_angle_bound']=core.pair(B);u['point_polynomial_phase_bound_rad']=core.pair(B/(1-B))
        comp=core.compose(res['geometry_composition'],res['decoded_argument'],u,[1,10**12])
        self.assertFalse(comp['phase_charge_fits_unchanged_cap']);self.assertFalse(comp['source_amplitude_budget_admitted'])
        DATA['conservative_cap_FAIL_control']={'B':core.pair(B),'composition':comp,'scope':'deliberately larger valid majorant; no node replay/cap change/promotion'}
if __name__=='__main__':
    r=unittest.TextTestRunner(verbosity=2,stream=sys.stderr).run(unittest.defaultTestLoader.loadTestsFromTestCase(ChainTests))
    print(json.dumps({'PASS':r.wasSuccessful(),'tests':r.testsRun,'data':DATA},sort_keys=True,separators=(',',':'),allow_nan=False))
    raise SystemExit(0 if r.wasSuccessful() else 1)

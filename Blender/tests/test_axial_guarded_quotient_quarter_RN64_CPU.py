"""Focused new quotient/residual CPU tests. No old native stages or suites."""
import copy,json,sys,unittest
from pathlib import Path
from fractions import Fraction as F
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'benchmarks/capacity_audit'))
import axial_guarded_quotient_quarter_RN64_CPU_v1 as core
DATA={}
class QuotientTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.retained=core.load_retained();cls.packets,cls.old,cls.pins=cls.retained
    def reject(self,label,fn,rows):
        with self.assertRaises((ValueError,TypeError,KeyError)) as cm:fn()
        rows.append({'label':label,'reason':str(cm.exception)})
    def test_a_new_operations(self):
        before=core.digest(self.retained)
        with patch.object(core,'load_retained',return_value=self.retained),patch.object(core.prior,'audit_hilo_Xroot_CPU',side_effect=AssertionError('old audit forbidden')),patch.object(core.guard,'decode_guarded',side_effect=AssertionError('old decode forbidden')),patch.object(core.prior.prior,'execute',side_effect=AssertionError('old roots forbidden')):
            a=core.audit_quotient_CPU(self.old['case_order'],model=core.MODEL)
        self.assertEqual(core.digest(self.retained),before);DATA['audit']=a
        self.assertEqual((a['new_point_sources_executed'],a['retained_sources_not_executed'],a['inherited_pins_verified']),(2,17,358))
        self.assertEqual((a['new_RN64_divisions'],a['new_exact_quarter_RN64_casts'],a['new_RN64_subtractions']),(2,2,2))
        self.assertEqual(a['old_audits_suites_reexecuted'],0)
        self.assertEqual(a['new_encoder_guard_decode_Xroot_reference_Horner_source_material_reduction_power_readout'],0)
        for c in a['cases'].values():
            for r in c['sources']:
                self.assertEqual(r['status'],'STOP')
                for key in core.FALSE:self.assertIs(r[key],False)
                if r[core.FLAG]:
                    v=r['result'];self.assertTrue(v['partial_phase_charge_fits_cap'])
                    self.assertGreater(F(*v['quarter_margin_with_quotient_error_cycles']),0)
                    self.assertEqual(v['unchanged_phase_cap_rad'],[1,10**12])
                    self.assertEqual(len(v['cycle_charges_to_fixed_ORIGINAL']),5)
    def test_b_preflight_all_cases(self):
        rows=[]
        old=copy.deepcopy(self.old);old['cases']['thin_resolved']['context']['input_packet_sha256']='0'*64
        with patch.object(core,'load_retained',return_value=(self.packets,old,self.pins)),patch.object(core,'native_divide',side_effect=AssertionError('all cases before CPU')) as native:
            self.reject('second_case_stale_context',lambda:core.audit_quotient_CPU(['nonexact_geometry_phase_PASS','thin_resolved'],model=core.MODEL),rows)
            self.assertEqual(native.call_count,0)
        old=copy.deepcopy(self.old);old['cases']['thin_resolved']['sources'][0]['result']['decoded_snapshot']['lambda_BU']=2.0
        with patch.object(core,'load_retained',return_value=(self.packets,old,self.pins)),patch.object(core,'native_divide',side_effect=AssertionError('decoded lambda before CPU')) as native:
            self.reject('decoded_wavelength_changed',lambda:core.audit_quotient_CPU(['nonexact_geometry_phase_PASS','thin_resolved'],model=core.MODEL),rows)
            self.assertEqual(native.call_count,0)
        read=Path.read_bytes;target=core.io.ROOT/core.PREVIOUS
        with patch.object(Path,'read_bytes',lambda p:read(p)+b' ' if p==target else read(p)):
            self.reject('predecessor_SHA',core.load_retained,rows)
        DATA['whole_request_preflight_rejections']={'rejections':rows,'new_CPU_operations':0,'prior_case_also_not_executed':True}
    def test_c_ambiguous_and_runtime_STOP(self):
        base=copy.deepcopy(DATA['audit']['cases']['thin_resolved']['sources'][0]['admission'])
        controls=[]
        large=copy.deepcopy(base);large['upstream_cycle_charges'][core.CHARGES[0]]=[1,8]
        large['upstream_cycles_bound']=core.pair(sum((F(*v) for v in large['upstream_cycle_charges'].values()),F(0)))
        boundary=copy.deepcopy(base);boundary.update(length_uint64=core.source.word(.125),wavelength_uint64=core.source.word(1.0),
            exact_retained_length_over_decoded_wave=[1,8],fixed_ORIGINAL_cycles=[1,8],fixed_quarter_index=1,
            upstream_cycle_charges={n:[0,1] for n in core.CHARGES},upstream_cycles_bound=[0,1])
        for label,a in [('larger_majorant_no_cap_change',large),('exact_quarter_boundary',boundary)]:
            rows=[]
            with patch.object(core,'native_quarter',side_effect=AssertionError('ambiguous before cast')) as cast,patch.object(core,'native_subtract',side_effect=AssertionError('ambiguous before residual')) as sub:
                self.reject(label,lambda a=a:core.execute(a),rows);self.assertEqual((cast.call_count,sub.call_count),(0,0))
            controls.append({'label':label,'admission':a,'reason':rows[0]['reason'],'division_attempts':1,'quarter_casts':0,'residual_subtractions':0})
        for label,stage in [('wrong_division_RN','native_divide'),('wrong_quarter_cast_RN','native_quarter'),('wrong_residual_RN','native_subtract')]:
            fn=getattr(core,stage);attempts=[];rows=[]
            def wrong(*args,fn=fn):
                good=fn(*args);w=core.source.word(good);bad=w+1
                attempts.append({'correct_uint64':w,'forged_uint64':bad})
                return core.source.value(bad,64)
            with patch.object(core,stage,side_effect=wrong):
                self.reject(label,lambda:core.execute(base),rows)
            self.assertEqual(len(attempts),1)
            controls.append({'label':label,'admission':base,'reason':rows[0]['reason'],'attempts':attempts})
        DATA['STOP_controls']=controls
    def test_d_typed_admission(self):
        rejects=[]
        with patch.object(core,'load_retained',return_value=self.retained):
            for label,names,model in [('model',['thin_resolved'],'bad'),('empty',[],core.MODEL),('duplicate',['thin_resolved']*2,core.MODEL),('unknown',['absent'],core.MODEL)]:
                self.reject(label,lambda n=names,m=model:core.audit_quotient_CPU(n,model=m),rejects)
        base=DATA['audit']['cases']['thin_resolved']['sources'][0]['admission']
        changes=[('cap_inflated',lambda a:a.__setitem__('unchanged_phase_cap_rad',[1,1])),
            ('cap_bool',lambda a:a.__setitem__('unchanged_phase_cap_rad',[True,10**12])),
            ('length_bool',lambda a:a.__setitem__('length_uint64',True)),
            ('zero_denominator',lambda a:a.__setitem__('wavelength_uint64',0)),
            ('fixed_index_bool',lambda a:a.__setitem__('fixed_quarter_index',True)),
            ('fixed_index_wrong',lambda a:a.__setitem__('fixed_quarter_index',999)),
            ('total_wrong',lambda a:a.__setitem__('upstream_cycles_bound',[0,1])),
            ('charge_negative',lambda a:a['upstream_cycle_charges'].__setitem__(core.CHARGES[0],[-1,1])),
            ('charge_missing',lambda a:a['upstream_cycle_charges'].pop(core.CHARGES[0])),
            ('quotient_input_wrong',lambda a:a.__setitem__('exact_retained_length_over_decoded_wave',[1,1]))]
        with patch.object(core,'native_divide',side_effect=AssertionError('typed admission before CPU')) as native:
            for label,change in changes:
                a=copy.deepcopy(base);change(a);self.reject(label,lambda a=a:core.execute(a),rejects)
            self.assertEqual(native.call_count,0)
        DATA['typed_admission_rejections']={'rejections':rejects,'new_CPU_operations':0}
if __name__=='__main__':
    r=unittest.TextTestRunner(verbosity=2,stream=sys.stderr).run(unittest.defaultTestLoader.loadTestsFromTestCase(QuotientTests))
    print(json.dumps({'PASS':r.wasSuccessful(),'tests':r.testsRun,'data':DATA},sort_keys=True,separators=(',',':'),allow_nan=False))
    raise SystemExit(0 if r.wasSuccessful() else 1)

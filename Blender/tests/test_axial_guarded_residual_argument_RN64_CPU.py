"""New scene-bound CPU argument tests; retained native stages forbidden."""
import copy,json,sys,unittest
from pathlib import Path
from fractions import Fraction as F
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'benchmarks/capacity_audit'))
import axial_guarded_residual_argument_RN64_CPU_v1 as core
DATA={}
class ArgumentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.retained=core.load_retained();cls.packets,cls.old,cls.roots,cls.pins=cls.retained
    def reject(self,label,fn,rows):
        with self.assertRaises((ValueError,TypeError,KeyError)) as cm:fn()
        rows.append({'label':label,'reason':str(cm.exception)})
    def test_a_new_multiply(self):
        before=core.digest(self.retained)
        with patch.object(core,'load_retained',return_value=self.retained),patch.object(core.prior,'execute',side_effect=AssertionError('retained quotient forbidden')),patch.object(core.prior,'audit_quotient_CPU',side_effect=AssertionError('old audit forbidden')),patch.object(core.guard,'decode_guarded',side_effect=AssertionError('retained decode forbidden')),patch.object(core.original,'trace_original',side_effect=AssertionError('old trace forbidden')):
            a=core.audit_argument_CPU(self.old['case_order'],model=core.MODEL)
        self.assertEqual(core.digest(self.retained),before);DATA['audit']=a
        self.assertEqual((a['new_point_sources_executed'],a['retained_sources_not_executed'],a['inherited_pins_verified'],a['new_RN64_multiplies']),(2,17,363,2))
        self.assertEqual(a['old_native_stages_suites_reexecuted'],0)
        for c in a['cases'].values():
            for row in c['sources']:
                self.assertEqual(row['status'],'STOP')
                for key in core.FALSE:self.assertIs(row[key],False)
                if row[core.FLAG]:
                    r=row['result'];self.assertEqual(len(r['phase_charges_rad']),7)
                    self.assertTrue(r['point_argument_phase_charge_fits_cap']);self.assertEqual(r['unchanged_phase_cap_rad'],[1,10**12])
    def test_b_all_case_preflight(self):
        rows=[]
        for label,mutate in [('second_case_context',lambda r:r['cases']['thin_resolved']['context'].__setitem__('input_packet_sha256','0'*64)),
          ('source_gauge',lambda r:r['cases']['thin_resolved']['sources'][0].__setitem__('phase_reference_id','foreign-source')),
          ('charge_laundering',lambda r:r['cases']['thin_resolved']['sources'][0]['result']['cycle_charges_to_fixed_ORIGINAL'].__setitem__('Xroot_length_rounding_cycles',[0,1])),
          ('forged_residual_word',lambda r:r['cases']['thin_resolved']['sources'][0]['result'].__setitem__('residual_uint64',r['cases']['thin_resolved']['sources'][0]['result']['residual_uint64']+1)),
          ('broad_promotion',lambda r:r['cases']['thin_resolved']['sources'][0].__setitem__('accepted_full_field_pipeline',True))]:
            old=copy.deepcopy(self.old);mutate(old)
            with patch.object(core,'load_retained',return_value=(self.packets,old,self.roots,self.pins)),patch.object(core,'native_multiply',side_effect=AssertionError('ALL request before multiply')) as native:
                self.reject(label,lambda:core.audit_argument_CPU(['nonexact_geometry_phase_PASS','thin_resolved'],model=core.MODEL),rows)
                self.assertEqual(native.call_count,0)
        read=Path.read_bytes;target=core.io.ROOT/core.PREVIOUS
        with patch.object(Path,'read_bytes',lambda p:read(p)+b' ' if p==target else read(p)):
            self.reject('predecessor_SHA',core.load_retained,rows)
        DATA['preflight_rejections']={'rejections':rows,'new_CPU_multiplies':0,'prior_case_also_not_executed':True}
    def test_c_native_FAIL_and_controls(self):
        base=copy.deepcopy(DATA['audit']['cases']['thin_resolved']['sources'][0]['admission'])
        fn=core.native_multiply;attempts=[];rows=[]
        def wrong(*args):
            v=fn(*args);w=core.source.word(v);attempts.append({'correct_uint64':w,'forged_uint64':w+1})
            return core.source.value(w+1,64)
        with patch.object(core,'native_multiply',side_effect=wrong):
            self.reject('wrong_multiply_RN',lambda:core.execute(base),rows)
        self.assertEqual(len(attempts),1)
        DATA['runtime_FAIL']={'admission':base,'reason':rows[0]['reason'],'attempts':attempts,'new_CPU_multiplies_attempted':1}
        controls=[]
        for label,w in [('positive_zero',0),('negative_zero',1<<63),('negative_residual',core.source.word(-.05))]:
            a=copy.deepcopy(base);R=core.guard.bits(w,64)
            a.update(residual_uint64=w,fixed_ORIGINAL_residual_cycles=core.pair(R),
              upstream_cycle_charges={n:[0,1] for n in core.CYCLE_CHARGES},upstream_cycles_bound=[0,1])
            v=core.execute(a);self.assertTrue(v['point_argument_phase_charge_fits_cap'])
            if R==0:self.assertEqual(v['argument_uint64'],w)
            controls.append({'label':label,'admission':a,'result':v,'scope':'synthetic scalar CPU control, not scene promotion'})
        large=copy.deepcopy(base);large['upstream_cycle_charges'][core.CYCLE_CHARGES[0]]=[1,100]
        large['upstream_cycles_bound']=core.pair(sum((F(*v) for v in large['upstream_cycle_charges'].values()),F(0)))
        v=core.execute(large);self.assertFalse(v['point_argument_phase_charge_fits_cap']);self.assertEqual(v['unchanged_phase_cap_rad'],[1,10**12])
        controls.append({'label':'larger_majorant_cap_FAIL','admission':large,'result':v,'scope':'synthetic majorant, unchanged cap'})
        DATA['scalar_controls']=controls
    def test_d_typed_guards(self):
        rows=[]
        with patch.object(core,'load_retained',return_value=self.retained):
            for label,ns,m in [('model',['thin_resolved'],'bad'),('empty',[],core.MODEL),('duplicate',['thin_resolved']*2,core.MODEL),('unknown',['absent'],core.MODEL)]:
                self.reject(label,lambda ns=ns,m=m:core.audit_argument_CPU(ns,model=m),rows)
        base=DATA['audit']['cases']['thin_resolved']['sources'][0]['admission']
        changes=[('constant_word_wrong',lambda a:a.__setitem__('TWO_PI_uint64',core.TWO_PI+1)),
          ('constant_word_bool',lambda a:a.__setitem__('TWO_PI_uint64',True)),
          ('cap_inflated',lambda a:a.__setitem__('unchanged_phase_cap_rad',[1,1])),
          ('cap_bool',lambda a:a.__setitem__('unchanged_phase_cap_rad',[True,10**12])),
          ('residual_bool',lambda a:a.__setitem__('residual_uint64',True)),
          ('residual_subnormal',lambda a:a.__setitem__('residual_uint64',1)),
          ('residual_boundary',lambda a:a.__setitem__('residual_uint64',core.source.word(.125))),
          ('ORIGINAL_boundary',lambda a:a.__setitem__('fixed_ORIGINAL_residual_cycles',[1,8])),
          ('charge_missing',lambda a:a['upstream_cycle_charges'].pop(core.CYCLE_CHARGES[0])),
          ('charge_negative',lambda a:a['upstream_cycle_charges'].__setitem__(core.CYCLE_CHARGES[0],[-1,1])),
          ('total_wrong',lambda a:a.__setitem__('upstream_cycles_bound',[0,1])),
          ('reference_mismatch',lambda a:a.__setitem__('fixed_ORIGINAL_residual_cycles',[1,9]))]
        with patch.object(core,'native_multiply',side_effect=AssertionError('typed preflight before CPU')) as native:
            for label,change in changes:
                a=copy.deepcopy(base);change(a);self.reject(label,lambda a=a:core.execute(a),rows)
            self.assertEqual(native.call_count,0)
        DATA['typed_rejections']={'rejections':rows,'new_CPU_multiplies':0}
if __name__=='__main__':
    r=unittest.TextTestRunner(verbosity=2,stream=sys.stderr).run(unittest.defaultTestLoader.loadTestsFromTestCase(ArgumentTests))
    print(json.dumps({'PASS':r.wasSuccessful(),'tests':r.testsRun,'data':DATA},sort_keys=True,separators=(',',':'),allow_nan=False))
    raise SystemExit(0 if r.wasSuccessful() else 1)

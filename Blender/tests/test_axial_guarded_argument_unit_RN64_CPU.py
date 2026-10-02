"""New guarded-argument CPU unit tests; prior native execution forbidden."""
import copy,json,sys,unittest
from pathlib import Path
from fractions import Fraction as F
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'benchmarks/capacity_audit'))
import axial_guarded_argument_unit_RN64_CPU_v1 as core
DATA={}
class UnitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.retained=core.load_retained();cls.packets,cls.old,cls.quot,cls.roots,cls.profile,cls.pins=cls.retained
    def reject(self,label,fn,rows):
        with self.assertRaises((ValueError,TypeError,KeyError)) as cm:fn()
        rows.append({'label':label,'reason':str(cm.exception)})
    def test_a_new_Horner(self):
        before=core.digest(self.retained)
        with patch.object(core,'load_retained',return_value=self.retained),patch.object(core.prior,'execute',side_effect=AssertionError('old argument forbidden')),patch.object(core.prior.prior,'execute',side_effect=AssertionError('old quotient forbidden')),patch.object(core.guard,'decode_guarded',side_effect=AssertionError('old decode forbidden')),patch.object(core.original,'trace_original',side_effect=AssertionError('old trace forbidden')):
            a=core.audit_unit_CPU(self.old['case_order'],model=core.MODEL)
        self.assertEqual(core.digest(self.retained),before);DATA['audit']=a
        self.assertEqual((a['new_point_sources_executed'],a['retained_sources_not_executed'],a['inherited_pins_verified'],a['new_RN64_horner_nodes']),(2,17,368,52))
        self.assertEqual(a['old_native_stages_suites_reexecuted'],0)
        for c in a['cases'].values():
            for row in c['sources']:
                self.assertEqual(row['status'],'STOP')
                for k in core.FALSE:self.assertIs(row[k],False)
                if row[core.FLAG]:
                    v=row['result'];self.assertTrue(v['point_unit_phase_charge_fits_cap']);self.assertEqual(len(v['nodes']),26)
                    self.assertEqual(len(v['unit_L1_charges_to_FIXED_ORIGINAL']),11)
                    self.assertEqual(len(v['phase_charges_to_FIXED_ORIGINAL_rad']),11)
                    self.assertFalse(v['zero_canonicalization_performed'])
    def test_b_ALL_preflight(self):
        rows=[]
        for label,mutate in [('second_context',lambda r:r['cases']['thin_resolved']['context'].__setitem__('input_packet_sha256','0'*64)),
          ('foreign_gauge',lambda r:r['cases']['thin_resolved']['sources'][0].__setitem__('phase_reference_id','foreign')),
          ('argument_word',lambda r:r['cases']['thin_resolved']['sources'][0]['result'].__setitem__('argument_uint64',r['cases']['thin_resolved']['sources'][0]['result']['argument_uint64']+1)),
          ('argument_charge',lambda r:r['cases']['thin_resolved']['sources'][0]['result']['phase_charges_rad'].__setitem__('constant_2pi_rad',[0,1])),
          ('promotion',lambda r:r['cases']['thin_resolved']['sources'][0].__setitem__('accepted_full_field_pipeline',True))]:
            old=copy.deepcopy(self.old);mutate(old)
            with patch.object(core,'load_retained',return_value=(self.packets,old,self.quot,self.roots,self.profile,self.pins)),patch.object(core,'native_multiply',side_effect=AssertionError('ALL before first Horner')) as native:
                self.reject(label,lambda:core.audit_unit_CPU(['nonexact_geometry_phase_PASS','thin_resolved'],model=core.MODEL),rows);self.assertEqual(native.call_count,0)
        p=copy.deepcopy(self.profile);p['cos'][6]['uint64']+=1
        with patch.object(core,'load_retained',return_value=(self.packets,self.old,self.quot,self.roots,p,self.pins)),patch.object(core,'native_multiply',side_effect=AssertionError('coefficients before CPU')) as native:
            self.reject('coefficient_RN',lambda:core.audit_unit_CPU(['thin_resolved'],model=core.MODEL),rows);self.assertEqual(native.call_count,0)
        read=Path.read_bytes;target=core.io.ROOT/core.PREVIOUS
        with patch.object(Path,'read_bytes',lambda p:read(p)+b' ' if p==target else read(p)):
            self.reject('predecessor_SHA',core.load_retained,rows)
        DATA['preflight_rejections']={'rejections':rows,'new_CPU_nodes':0,'prior_case_also_not_executed':True}
    def test_c_native_FAIL_and_controls(self):
        base=copy.deepcopy(DATA['audit']['cases']['thin_resolved']['sources'][0]['admission']);fails=[]
        for label,stage in [('wrong_square_RN','native_multiply'),('wrong_first_add_RN','native_add')]:
            fn=getattr(core,stage);attempts=[];rows=[]
            def wrong(*args,fn=fn):
                good=fn(*args);w=core.source.word(good);attempts.append({'correct_uint64':w,'forged_uint64':w+1});return core.source.value(w+1,64)
            other='native_add' if stage=='native_multiply' else 'native_multiply'
            with patch.object(core,stage,side_effect=wrong) as bad,patch.object(core,other,wraps=getattr(core,other)) as okay:
                self.reject(label,lambda:core.execute(base,self.profile),rows);self.assertEqual(bad.call_count,1)
                self.assertEqual(okay.call_count,0 if stage=='native_multiply' else 2)
            fails.append({'label':label,'admission':base,'attempts':attempts,'reason':rows[0]['reason'],
                'CPU_nodes_attempted':1 if stage=='native_multiply' else 3})
        DATA['runtime_FAILs']=fails
        controls=[]
        for sign in (0,1):
            for k in range(4):
                a=copy.deepcopy(base);a.update(argument_uint64=sign<<63,quadrant_mod4=k,
                    upstream_phase_charges_rad={n:[0,1] for n in core.PHASE_NAMES},upstream_phase_bound_rad=[0,1])
                v=core.execute(a,self.profile);self.assertEqual(v['point_polynomial_L1_bound'],[0,1])
                self.assertEqual(v['unpermuted_unit_uint64'],[core.source.word(1.0),sign<<63]);self.assertTrue(v['point_unit_phase_charge_fits_cap'])
                controls.append({'label':'signed_zero','admission':a,'result':v,'scope':'scalar control, no scene promotion'})
        for label,x in [('negative_argument',-.5),('Taylor_cap_FAIL',.99)]:
            a=copy.deepcopy(base);a.update(argument_uint64=core.source.word(x),quadrant_mod4=0,
                upstream_phase_charges_rad={n:[0,1] for n in core.PHASE_NAMES},upstream_phase_bound_rad=[0,1])
            v=core.execute(a,self.profile);self.assertIs(v['point_unit_phase_charge_fits_cap'],label!='Taylor_cap_FAIL')
            controls.append({'label':label,'admission':a,'result':v,'scope':'scalar control, unchanged coefficients/cap'})
        DATA['scalar_controls']=controls
    def test_d_typed_guard(self):
        rows=[]
        with patch.object(core,'load_retained',return_value=self.retained):
            for label,ns,m in [('model',['thin_resolved'],'bad'),('empty',[],core.MODEL),('duplicate',['thin_resolved']*2,core.MODEL),('unknown',['absent'],core.MODEL)]:
                self.reject(label,lambda ns=ns,m=m:core.audit_unit_CPU(ns,model=m),rows)
        base=DATA['audit']['cases']['thin_resolved']['sources'][0]['admission']
        changes=[('cap_inflated',lambda a:a.__setitem__('unchanged_phase_cap_rad',[1,1])),
          ('cap_bool',lambda a:a.__setitem__('unchanged_phase_cap_rad',[True,10**12])),
          ('angle_bool',lambda a:a.__setitem__('argument_uint64',True)),
          ('angle_subnormal',lambda a:a.__setitem__('argument_uint64',1)),
          ('angle_domain',lambda a:a.__setitem__('argument_uint64',core.source.word(1.0))),
          ('quadrant_bool',lambda a:a.__setitem__('quadrant_mod4',True)),
          ('quadrant_bad',lambda a:a.__setitem__('quadrant_mod4',4)),
          ('profile_digest',lambda a:a.__setitem__('coefficient_profile_sha256','0'*64)),
          ('charge_missing',lambda a:a['upstream_phase_charges_rad'].pop(core.PHASE_NAMES[0])),
          ('charge_negative',lambda a:a['upstream_phase_charges_rad'].__setitem__(core.PHASE_NAMES[0],[-1,1])),
          ('total_bad',lambda a:a.__setitem__('upstream_phase_bound_rad',[0,1]))]
        with patch.object(core,'native_multiply',side_effect=AssertionError('typed admission before CPU')) as native:
            for label,change in changes:
                a=copy.deepcopy(base);change(a);self.reject(label,lambda a=a:core.execute(a,self.profile),rows)
            self.assertEqual(native.call_count,0)
        DATA['typed_rejections']={'rejections':rows,'new_CPU_nodes':0}
if __name__=='__main__':
    r=unittest.TextTestRunner(verbosity=2,stream=sys.stderr).run(unittest.defaultTestLoader.loadTestsFromTestCase(UnitTests))
    print(json.dumps({'PASS':r.wasSuccessful(),'tests':r.testsRun,'data':DATA},sort_keys=True,separators=(',',':'),allow_nan=False))
    raise SystemExit(0 if r.wasSuccessful() else 1)

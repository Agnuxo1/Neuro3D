"""New stage tests only; retained scene producers forbidden."""
import copy,json,sys,unittest
from pathlib import Path
from unittest.mock import patch
from fractions import Fraction as F
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'benchmarks/capacity_audit'))
import axial_ideal_reflection_stage_CPU_v1 as core
DATA={}
class ReflectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.retained=core.load_retained();cls.packets,cls.old,cls.pins=cls.retained
    def test_a_stage(self):
        before=core.digest(self.retained)
        with patch.object(core,'load_retained',return_value=self.retained),patch.object(core.prior,'audit_chain_CPU',side_effect=AssertionError('no prior audit')),patch.object(core.prior,'execute_prefix',side_effect=AssertionError('no prefix replay')),patch.object(core.prior.geo,'encode_geometry',side_effect=AssertionError('no encoder')):
            a=core.audit_reflection_CPU(self.old['case_order'],model=core.MODEL)
        DATA['audit']=a;self.assertEqual(core.digest(self.retained),before)
        self.assertEqual((a['new_ideal_reflected_sources'],a['retained_sources_not_executed'],a['inherited_pins_verified']),(2,17,348))
        self.assertEqual(a['new_main_CPU_unary_negations'],4)
        for n,c in a['cases'].items():
            for i,r in enumerate(c['sources']):
                self.assertEqual(r['status'],'STOP')
                for k in core.FALSE:self.assertFalse(r[k])
                if r[core.FLAG]:
                    p=r['result'];old=self.old['cases'][n]['sources'][i]['result']
                    self.assertEqual(p['reflected_uint64'],[w^core.SIGN for w in p['input_uint64']])
                    self.assertEqual(p['charges_L1'],old['detailed_source_charges_L1'])
                    self.assertEqual(p['point_reflected_source_to_fixed_ORIGINAL_bound_L1'],old['point_bare_source_to_fixed_ORIGINAL_bound_L1'])
                    self.assertFalse(p['allocation_gate']['allocation_INPUT_valid'])
                    self.assertFalse(p['amplitude_budget_accepted'])
        self.assertFalse(a['cases']['two_sources']['sources'][1][core.FLAG])
    def test_b_zero_and_atomicity(self):
        controls=[]
        for w in (0,core.SIGN,0x3ff0000000000000,0xbff0000000000000):
            out=core.native_negate(w);self.assertEqual(out,w^core.SIGN);controls.append({'input_uint64':w,'output_uint64':out})
        DATA['unary_controls']=controls
        bad=copy.deepcopy(self.old);bad['cases']['thin_resolved']['sources'][0]['terminal_reference_id']='foreign'
        with patch.object(core,'load_retained',return_value=(self.packets,bad,self.pins)),patch.object(core,'native_negate',side_effect=AssertionError('no stage/probe before all admission')) as neg:
            with self.assertRaises(ValueError) as cm:core.audit_reflection_CPU(['nonexact_geometry_phase_PASS','thin_resolved'],model=core.MODEL)
            self.assertEqual(neg.call_count,0)
        DATA['atomic_rejection']={'reason':str(cm.exception),'new_CPU_unary_negations':0,'partial_outputs_returned':False}
    def test_c_rejections(self):
        rejects=[];DATA['rejections']=rejects
        def reject(label,fn):
            with self.assertRaises((ValueError,TypeError,KeyError,IndexError)) as cm:fn()
            rejects.append({'label':label,'reason':str(cm.exception)})
        with patch.object(core,'load_retained',return_value=self.retained):
            for label,ns,m in [('model',['thin_resolved'],'old'),('empty',[],core.MODEL),('duplicate',['thin_resolved']*2,core.MODEL),('unknown',['unknown'],core.MODEL)]:
                reject(label,lambda ns=ns,m=m:core.audit_reflection_CPU(ns,model=m))
            with patch.object(core,'runtime_probe',return_value={'PASS':False}),patch.object(core,'execute',side_effect=AssertionError('no reflection after FAIL')):
                reject('runtime_FAIL',lambda:core.audit_reflection_CPU(['thin_resolved'],model=core.MODEL))
        p=self.packets['thin_resolved'];ctx=self.old['cases']['thin_resolved']['context'];row=self.old['cases']['thin_resolved']['sources'][0]
        for label,mut in [('context_SHA',lambda c,r:c.__setitem__('input_packet_sha256','0'*64)),('source_id',lambda c,r:r.__setitem__('source_id','other')),('source_gauge',lambda c,r:r.__setitem__('phase_reference_id','other')),('eligibility_bool',lambda c,r:r.__setitem__(core.prior.FLAG,1)),('owner_bool',lambda c,r:r['result']['fixed_ORIGINAL_trace']['hits'][0].__setitem__('owner',False)),('owner_wrong',lambda c,r:r['result']['fixed_ORIGINAL_trace']['hits'][0].__setitem__('owner',1)),('primitive_mismatch',lambda c,r:r['result']['decoded_trace']['hits'][0].__setitem__('primitive_id',0)),('word_bool',lambda c,r:r['result']['bare_source_prefix']['product_uint64'].__setitem__(0,True)),('word_subnormal',lambda c,r:r['result']['bare_source_prefix']['product_uint64'].__setitem__(0,1)),('charge_bool',lambda c,r:r['result']['detailed_source_charges_L1'].__setitem__('source_Horner_L1',[True,1])),('charge_negative',lambda c,r:r['result']['detailed_source_charges_L1'].__setitem__('source_Horner_L1',[-1,1])),('missing_charge',lambda c,r:r['result']['detailed_source_charges_L1'].pop('source_encoding_L1')),('charge_sum',lambda c,r:r['result'].__setitem__('point_bare_source_to_fixed_ORIGINAL_bound_L1',[0,1]))]:
            c,r=copy.deepcopy(ctx),copy.deepcopy(row);mut(c,r)
            reject(label,lambda c=c,r=r:core.admit(p,c,0,r))
        reject('index_bool',lambda:core.admit(p,ctx,True,row))
        snap,meta=core.prior.original.snapshot_from_packet(p,ctx)
        for label,value in [('phase_nonzero',1e-300),('phase_subnormal',5e-324),('phase_bool',False),('phase_nan',float('nan'))]:
            s=copy.deepcopy(snap);s['objects']['M']['phase_rad']=value
            reject(label,lambda s=s:core.profile(s,meta,'s',row['result']))
        s=copy.deepcopy(snap);s['objects']['M']['phase_rad']=-0.0
        prof=core.profile(s,meta,'s',row['result']);self.assertEqual(prof['mirror_phase_ORIGINAL_uint64'],core.SIGN)
        DATA['negative_zero_profile']=prof
        read=Path.read_bytes;target=core.io.ROOT/core.PREVIOUS
        with patch.object(Path,'read_bytes',lambda p:read(p)+b' ' if p==target else read(p)):
            reject('predecessor_SHA',core.load_retained)
    def test_d_no_missing_as_zero(self):
        p=self.packets['thin_resolved'];ctx=self.old['cases']['thin_resolved']['context'];row=self.old['cases']['thin_resolved']['sources'][0]
        snap,meta=core.prior.original.snapshot_from_packet(p,ctx);meta['source_amplitude_allocation']=None
        with patch.object(core.prior.original,'snapshot_from_packet',return_value=(snap,meta)):
            with self.assertRaises(ValueError) as cm:core.admit(p,ctx,0,row)
        DATA['unsupported_allocation_extension']={'reason':str(cm.exception),'source_budget_admitted':False}
if __name__=='__main__':
    r=unittest.TextTestRunner(verbosity=2,stream=sys.stderr).run(unittest.defaultTestLoader.loadTestsFromTestCase(ReflectionTests))
    print(json.dumps({'PASS':r.wasSuccessful(),'tests':r.testsRun,'data':DATA},sort_keys=True,separators=(',',':'),allow_nan=False))
    raise SystemExit(0 if r.wasSuccessful() else 1)

"""New point-Xroot tests; no frozen suites or hi-lo/Horner/source producer replay."""
import copy,json,sys,unittest
from pathlib import Path
from fractions import Fraction as F
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'benchmarks/capacity_audit'))
import axial_xroot_selector_RN64_CPU_v1 as core
DATA={}
class XrootTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.retained=core.load_retained();cls.packets,cls.old,cls.pins=cls.retained
    def test_a_point_audit(self):
        before=core.digest(self.retained)
        with patch.object(core,'load_retained',return_value=self.retained),patch.object(core.retained.prior,'execute_prefix',side_effect=AssertionError('old prefix forbidden')),patch.object(core.guard.prior,'encode_geometry',side_effect=AssertionError('hi-lo replay forbidden')):
            a=core.audit_Xroot_CPU(self.old['case_order'],model=core.MODEL)
        self.assertEqual(core.digest(self.retained),before);DATA['audit']=a
        self.assertEqual((a['new_point_sources_executed'],a['retained_sources_not_executed']),(2,17))
        self.assertEqual(a['new_RN64_operation_counts'],{'subtract':18,'add':6,'negate':8})
        self.assertEqual(a['new_rational_reference_root_records'],16)
        for case in a['cases'].values():
            for r in case['sources']:
                self.assertEqual(r['status'],'STOP')
                for key in core.FALSE:self.assertIs(r[key],False)
                if r[core.FLAG]:
                    result=r['result'];self.assertTrue(result['length_only_phase_charge_fits_cap'])
                    self.assertEqual(result['previous_owner_exact_zero_exclusions'],2)
                    self.assertEqual(F(*result['length_to_fixed_ORIGINAL_bound_BU']),sum((F(*q) for q in result['length_rounding_charges_BU'].values()),F(0)))
        thin=a['cases']['thin_resolved']['sources'][0]['result']
        self.assertEqual(thin['fixed_ORIGINAL_reference']['hits'][0]['segment_BU'],[1,2**30])
        self.assertEqual(core.guard.bits(thin['selected_root_uint64'][0],64),F(1,2**30))
        self.assertFalse(a['cases']['two_sources']['sources'][1][core.FLAG])
    def test_b_scalar_runtime_and_rounding(self):
        controls={}
        for label,args in [('halfway_even',(1.0,2.0**-54,1)),('thin',(0.10000000093132258,0.1,1)),('reflected',(-0.125,0.1,-1)),('positive_zero',(0.0,0.0,1)),('negative_zero',(-0.0,0.0,1)),('reflected_zero',(0.0,0.0,-1))]:
            controls[label]=core.root(*args)
        self.assertEqual(controls['halfway_even']['root_uint64'],core.source.word(1.0))
        self.assertNotEqual(controls['halfway_even']['nodes'][0]['signed_rounding_delta_BU'],[0,1])
        self.assertEqual(controls['negative_zero']['root_uint64'],1<<63)
        self.assertEqual(controls['reflected_zero']['root_uint64'],1<<63)
        DATA['scalar_controls']=controls
        with patch.object(core,'native_sub',lambda a,b:core.source.value(core.source.word(a-b)+1,64)):
            with self.assertRaises(ValueError) as cm:core.root(1.0,0.25,1)
        DATA['wrong_runtime_rejection']={'reason':str(cm.exception),'input':[1.0,0.25,1]}
    def test_c_selector_guards(self):
        main=DATA['audit']['cases']['thin_resolved']['sources'][0]['result']
        rows=copy.deepcopy(main['steps'][0]);controls=[]
        def reject(label,rs,expected=0):
            with self.assertRaises(ValueError) as cm:core.select(rs,expected)
            controls.append({'label':label,'records':rs,'expected_owner':expected,'reason':str(cm.exception)})
        selected=next(r for r in rows if r['classification']=='strict_interior' and r['owner']==0)
        duplicate=copy.deepcopy(selected);duplicate['primitive_id']=999
        reject('nearest_interval_overlap',rows+[duplicate])
        zero=copy.deepcopy(rows);target=next(r for r in zero if r['classification']=='strict_interior' and r['owner']==0)
        target['root']['root_interval_BU']=[[0,1],[1,1]]
        reject('interval_touches_zero',zero)
        reversed_rows=copy.deepcopy(rows);target=next(r for r in reversed_rows if r['classification']=='strict_interior' and r['owner']==0)
        target['root']['root_interval_BU']=[[2,1],[1,1]]
        reject('reversed_interval',reversed_rows)
        reject('wrong_owner',rows,1)
        unknown=copy.deepcopy(rows);unknown[0]['classification']='boundary_FAIL'
        reject('boundary_projection',unknown)
        DATA['selector_controls']=controls
        snap,_=core.original.snapshot_from_packet(self.packets['thin_resolved'],self.old['cases']['thin_resolved']['context'])
        snap['sources'][0]['position_BU'][0]=snap['objects']['M']['vertices_world_BU'][0][0]
        with patch.object(core,'native_sub',side_effect=AssertionError('contact before CPU root')) as native:
            with self.assertRaises(ValueError) as cm:core.execute(snap,0,[1,10**12])
            self.assertEqual(native.call_count,0)
        DATA['initial_contact_rejection']={'snapshot':snap,'reason':str(cm.exception),'new_native_operations':0}
    def test_d_admission_and_no_promotion(self):
        rejected=[]
        def reject(label,fn):
            with self.assertRaises((ValueError,TypeError,KeyError)) as cm:fn()
            rejected.append({'label':label,'reason':str(cm.exception)})
        with patch.object(core,'load_retained',return_value=self.retained):
            for label,names,m in [('model',['thin_resolved'],'bad'),('empty',[],core.MODEL),('duplicate',['thin_resolved']*2,core.MODEL),('unknown',['absent'],core.MODEL)]:
                reject(label,lambda ns=names,m=m:core.audit_Xroot_CPU(ns,model=m))
        old=copy.deepcopy(self.old);old['cases']['thin_resolved']['context']['input_packet_sha256']='0'*64
        with patch.object(core,'load_retained',return_value=(self.packets,old,self.pins)),patch.object(core,'native_sub',side_effect=AssertionError('all contexts before roots')) as native:
            reject('stale_second_context',lambda:core.audit_Xroot_CPU(['nonexact_geometry_phase_PASS','thin_resolved'],model=core.MODEL));self.assertEqual(native.call_count,0)
        snap,_=core.original.snapshot_from_packet(self.packets['thin_resolved'],self.old['cases']['thin_resolved']['context'])
        for label,cap in [('cap_inflation',[1,1]),('bool_cap',[True,10**12])]:
            reject(label,lambda cap=cap:core.execute(snap,0,cap))
        reject('bool_sign',lambda:core.root(1.0,0.0,True))
        reject('subnormal_input',lambda:core.root(2.0**-1074,0.0,1))
        reject('overflow',lambda:core.root(2.0**1023,-2.0**1023,1))
        read=Path.read_bytes;target=core.io.ROOT/core.PREVIOUS
        with patch.object(Path,'read_bytes',lambda p:read(p)+b' ' if p==target else read(p)):
            reject('predecessor_SHA',core.load_retained)
        DATA['admission_rejections']=rejected
        DATA['scope']={'new_Horner_source_material_reduction_power_readout':0,'new_hi_lo_encoder_guard':0,'old_audits_suites':0,
            'selector_controls_synthetic_NOT_fixture_changes':True,'all_REAL_field_cases_STOP':True}
if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2,stream=sys.stderr).run(unittest.defaultTestLoader.loadTestsFromTestCase(XrootTests))
    print(json.dumps({'PASS':result.wasSuccessful(),'tests':result.testsRun,'data':DATA},sort_keys=True,separators=(',',':'),allow_nan=False))
    raise SystemExit(0 if result.wasSuccessful() else 1)

"""Own bounded fresh ORIGINAL CPU unit tests; no retained numeric replay."""
import copy,json,sys,unittest
from pathlib import Path
from unittest.mock import patch
from fractions import Fraction as F
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'benchmarks/capacity_audit'))
import axial_ORIGINAL_unit_CPU_v1 as core
DATA={}
class OriginalUnitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.retained=core.load_retained()
        cls.packets,cls.old,cls.profile,cls.pins=cls.retained
    def test_a_fresh_ORIGINAL_unit(self):
        before=core.digest(self.retained)
        with patch.object(core,'load_retained',return_value=self.retained),patch.object(core.original.prior,'execute_horner',side_effect=AssertionError('no retained Horner')),patch.object(core.source,'execute_graph',side_effect=AssertionError('no SOURCE graph')):
            a=core.audit_ORIGINAL_unit_CPU(self.old['case_order'],model=core.MODEL)
        DATA['audit']=a
        self.assertEqual(core.digest(self.retained),before)
        self.assertEqual((a['fresh_ORIGINAL_unit_sources_executed'],a['retained_sources_not_executed'],a['new_CPU_Horner_RN_nodes_executed']),(2,17,52))
        self.assertEqual(a['inherited_pins_verified'],323)
        found=[]
        for n,c in a['cases'].items():
            for r in c['sources']:
                self.assertEqual(r['status'],'STOP')
                for key in core.FALSE:self.assertIs(r[key],False)
                if r[core.FLAG]:
                    found.append(n)
                    self.assertTrue(r['composition']['phase_charge_fits_unchanged_cap'])
                    self.assertFalse(r['unit']['retained_angle_or_result_substitution'])
                    self.assertEqual(len(r['unit']['nodes']),26)
                    self.assertEqual(r['unit']['argument_uint64'],r['argument']['argument_uint64'])
                    for term in r['unit']['terms'].values():
                        self.assertLessEqual(F(*term['observed_Taylor_error_L1']),sum(F(*term[k]) for k in ('coefficient_charge_L1','square_charge_L1','RN_node_charge_L1')))
        self.assertEqual(set(found),{'nonexact_geometry_phase_PASS','thin_resolved'})
        thin=a['cases']['thin_resolved']['sources'][0]
        self.assertEqual(thin['trace']['hits'][0]['segment_BU'],[1,2**30])
        self.assertFalse(a['cases']['two_sources']['sources'][1][core.FLAG])
    def test_b_quadrant_bit_permutations(self):
        # Four primitive controls, not additional scenes or uniform-domain evidence.
        controls=[core.execute_unit(0x3fd0000000000000,k,self.profile) for k in range(4)]
        DATA['quadrant_controls']=controls
        a,b=controls[0]['unpermuted_unit_uint64'];sign=1<<63
        self.assertEqual([r['unit_uint64'] for r in controls],[[a,b],[b^sign,a],[a^sign,b^sign],[b,a^sign]])
        self.assertEqual(len({core.digest(r['nodes']) for r in controls}),1)
    def test_c_rejections(self):
        rejected=[];DATA['rejections']=rejected
        def reject(label,fn):
            with self.assertRaises((ValueError,TypeError,KeyError,IndexError)) as cm:fn()
            rejected.append({'label':label,'reason':str(cm.exception)})
        for label,w,k in [('bool_angle',True,0),('nonfinite_angle',0x7ff0000000000000,0),('subnormal_angle',1,0),('zero_angle',0,0),('angle_bound',0x4000000000000000,0),('bool_quadrant',0x3fd0000000000000,True),('negative_quadrant',0x3fd0000000000000,-1),('large_quadrant',0x3fd0000000000000,4)]:
            reject(label,lambda w=w,k=k:core.execute_unit(w,k,self.profile))
        for label,mut in [('missing_term',lambda p:p.pop('sin')),('short_coefs',lambda p:p['cos'].pop()),('coefficient_word',lambda p:p['cos'][0].__setitem__('uint64',p['cos'][0]['uint64']+1)),('coefficient_exact',lambda p:p['sin'][0].__setitem__('exact_rational',[2,1])),('coefficient_error',lambda p:p['cos'][0].__setitem__('error_rational',[1,1]))]:
            p=copy.deepcopy(self.profile);mut(p)
            reject(label,lambda p=p:core.execute_unit(0x3fd0000000000000,0,p))
        row=DATA['audit']['cases']['thin_resolved']['sources'][0]
        reject('changed_phase_cap',lambda:core.compose_charges(row['argument'],row['unit'],[1,10**11]))
        arg=copy.deepcopy(row['argument']);arg['phase_error_bound_rad']=[-1,1]
        reject('negative_phase_charge',lambda:core.compose_charges(arg,row['unit'],[1,10**12]))
        arg=copy.deepcopy(row['argument']);arg['phase_error_bound_rad']=[1,1]
        reject('charge_sum_mismatch',lambda:core.compose_charges(arg,row['unit'],[1,10**12]))
        unit=copy.deepcopy(row['unit']);unit['point_polynomial_phase_bound_rad']=[0,1]
        reject('phase_radius_mismatch',lambda:core.compose_charges(row['argument'],unit,[1,10**12]))
        with patch.object(core,'load_retained',return_value=self.retained):
            for label,n,m in [('wrong_model',['thin_resolved'],'bad'),('empty',[],core.MODEL),('duplicate',['thin_resolved']*2,core.MODEL),('unknown',['unknown'],core.MODEL)]:
                reject(label,lambda n=n,m=m:core.audit_ORIGINAL_unit_CPU(n,model=m))
            with patch.object(core.source,'runtime_probe',return_value={'PASS':False}),patch.object(core.original,'trace_original',side_effect=AssertionError('guard before scene')):
                reject('runtime_guard_FAIL',lambda:core.audit_ORIGINAL_unit_CPU(['thin_resolved'],model=core.MODEL))
        old=copy.deepcopy(self.old);old['cases']['thin_resolved']['context']['input_packet_sha256']='0'*64
        with patch.object(core,'load_retained',return_value=(self.packets,old,self.profile,self.pins)):
            reject('stale_INPUT_context',lambda:core.audit_ORIGINAL_unit_CPU(['thin_resolved'],model=core.MODEL))
        old=copy.deepcopy(self.old);old['cases']['thin_resolved']['sources'][0]['argument']['argument_uint64']+=1
        with patch.object(core,'load_retained',return_value=(self.packets,old,self.profile,self.pins)):
            reject('retained_argument_tamper_after_fresh_trace',lambda:core.audit_ORIGINAL_unit_CPU(['thin_resolved'],model=core.MODEL))
        read=Path.read_bytes;target=core.io.ROOT/core.PREVIOUS
        with patch.object(Path,'read_bytes',lambda p:read(p)+b' ' if p==target else read(p)):
            reject('predecessor_SHA',core.load_retained)
    def test_d_cap_exceedance_not_rescued(self):
        # The ledger must preserve a false fit, not loosen the cap or normalize.
        row=DATA['audit']['cases']['thin_resolved']['sources'][0];arg=copy.deepcopy(row['argument'])
        arg['phase_error_bound_rad']=[1,1000];arg['phase_error_charges_rad']={'synthetic_error_rad':[1,1000]}
        result=core.compose_charges(arg,row['unit'],[1,10**12])
        self.assertFalse(result['phase_charge_fits_unchanged_cap'])
        DATA['synthetic_cap_FAIL_control']=result
if __name__=='__main__':
    r=unittest.TextTestRunner(verbosity=2,stream=sys.stderr).run(unittest.defaultTestLoader.loadTestsFromTestCase(OriginalUnitTests))
    print(json.dumps({'PASS':r.wasSuccessful(),'tests':r.testsRun,'data':DATA},sort_keys=True,separators=(',',':'),allow_nan=False))
    raise SystemExit(0 if r.wasSuccessful() else 1)

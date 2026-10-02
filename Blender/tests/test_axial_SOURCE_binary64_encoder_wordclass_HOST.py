"""Own exact predicate tests and new dyadic controls; no old counterexample/producer replay."""
import copy,json,sys,unittest
from fractions import Fraction as F
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'benchmarks/capacity_audit'))
import axial_SOURCE_binary64_encoder_wordclass_HOST_v1 as c
import axial_geometry_decode_guard_CPU_v1 as guard
import axial_SOURCE_box_guard_counterexample_HOST_v1 as negative
DATA={}
class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.loaded=c.load_retained()
    def assess(self,i):return c.component_wordclasses_HOST(i,model=c.MODEL,grid=c.GRID,arithmetic_model=c.ARITH)
    def audit(self,v,x=None):
        with patch.object(c,'load_retained',return_value=self.loaded if x is None else x):
            return c.audit_wordclasses_HOST(v,model=c.MODEL,grid=c.GRID,arithmetic_model=c.ARITH)
    def reject(self,label,fn,rows):
        try:fn()
        except (ValueError,KeyError,TypeError,IndexError) as e:rows.append({'label':label,'reason':str(e)})
        else:self.fail('expected rejection '+label)
    def test_a_missing(self):
        with patch.object(c,'component_wordclasses_HOST',side_effect=AssertionError('no predicate without domain')):
            a=self.audit('real_missing');b=self.audit('explicit_None_missing')
        self.assertEqual(a['cases'],b['cases']);self.assertEqual(len(a['cases']),17)
        self.assertEqual(sum(len(v['context']['source_order']) for v in a['cases'].values()),19)
        self.assertTrue(all(v['sources'] is None for v in a['cases'].values()))
        DATA['real_missing']=a;DATA['explicit_None_missing']=b
    def test_b_retained_domains(self):
        with patch.object(negative,'counterexample_HOST',side_effect=AssertionError('no old witness replay')),patch.object(c.prior,'audit_consumer_HOST',side_effect=AssertionError('no old consumer')),patch.object(c.prior.phase.prior.producer,'encode_source',side_effect=AssertionError('no native SOURCE')):
            a=self.audit('synthetic_valid')
        self.assertEqual(a['component_predicate_assessments'],8)
        for name in ('nonexact_geometry_phase_PASS','thin_resolved'):
            s=a['cases'][name]['sources'][0]
            self.assertIs(s['retained_whole_box_guard_admission_disproved'],True)
            self.assertFalse(s[c.FLAG]);self.assertTrue(s['components'][0][c.FLAG]);self.assertFalse(s['components'][1][c.FLAG])
        self.assertEqual(a['group_admissions'],0);self.assertFalse(a['actual_scene_domain_grid_authenticated'])
        DATA['synthetic_valid']=a
    def test_c_threshold_controls(self):
        p=c.pow2;pair=c.pair
        intervals={'zero':[[0,1],[0,1]],'positive_min':[pair(p(-74)),pair(p(-73))],
            'negative_min':[pair(-p(-73)),pair(-p(-74))],'upper_margin':[pair(p(126)),pair(p(127))],
            'below_sufficient':[pair(p(-75)),pair(p(-75))],'cross_zero':[pair(-p(-70)),pair(p(-70))],
            'upper_outside':[pair(p(127)),pair(p(128))]}
        controls={k:self.assess(v) for k,v in intervals.items()}
        self.assertEqual([controls[k][c.FLAG] for k in intervals],[True,True,True,True,False,False,False])
        self.assertEqual(controls['positive_min']['proof']['nonzero_exact_residual_abs_lower_bound'],pair(p(-126)))
        for out in controls.values():
            self.assertIsNone(out['frozen_guard_verdict']);self.assertFalse(out['frozen_guard_admission_for_entire_box_proved'])
            self.assertFalse(out['actual_scene_domain_grid_authenticated']);self.assertFalse(out['all_real_continuum_wordclasses_proved'])
        DATA['control_intervals']=intervals;DATA['controls']=controls
    def test_d_new_dyadic_RN_controls(self):
        records=[]
        for e in (-74,-20,0,40):
            for sign in (0,1):
                for offset in (0,1):
                    xw=(sign<<63)|((1023+e)<<52)|offset;hw=(sign<<31)|((127+e)<<23)
                    rw=0 if offset==0 else (sign<<63)|((1023+e-52)<<52)
                    lw=0 if offset==0 else (sign<<31)|((127+e-52)<<23)
                    x=guard.bits(xw,64);h=guard.check_RN(x,hw,32,sign);r=x-h
                    self.assertEqual(guard.check_RN(r,rw,64,0),r)
                    l=guard.check_RN(r,lw,32,0 if offset==0 else sign)
                    self.assertEqual(guard.check_RN(h+l,xw,64,0),x)
                    proof=self.assess([c.pair(x),c.pair(x)]);self.assertTrue(proof[c.FLAG])
                    records.append({'binade':e,'sign':sign,'offset_binary64_ULP':offset,
                        'original_uint64':xw,'high_uint32':hw,'residual_uint64':rw,'low_uint32':lw,
                        'decoded_uint64':xw,'x':c.pair(x),'high':c.pair(h),'residual':c.pair(r),'low':c.pair(l),
                        'control_scope':'NEW exact dyadic HOST RN checks only; not exhaustive/domain/device proof'})
        self.assertEqual(len(records),16);DATA['new_dyadic_RN_controls']=records
    def test_e_types_INPUT_and_atomic(self):
        rows=[];i=[[1,1],[2,1]]
        for label,fn in [
            ('missing_grid',lambda:c.component_wordclasses_HOST(i,model=c.MODEL,grid=None,arithmetic_model=c.ARITH)),
            ('continuum_alias',lambda:c.component_wordclasses_HOST(i,model=c.MODEL,grid='all real',arithmetic_model=c.ARITH)),
            ('FTZ',lambda:c.component_wordclasses_HOST(i,model=c.MODEL,grid=c.GRID,arithmetic_model='FTZ')),
            ('model',lambda:c.component_wordclasses_HOST(i,model='foreign',grid=c.GRID,arithmetic_model=c.ARITH)),
            ('bool_endpoint',lambda:self.assess([[True,1],[2,1]])),('float',lambda:self.assess([[1.0,1],[2,1]])),
            ('noncanonical',lambda:self.assess([[2,2],[2,1]])),('order',lambda:self.assess([[2,1],[1,1]])),
            ('oversized',lambda:self.assess([[1,1<<4097],[2,1]])),('missing',lambda:self.assess(None))]:
            self.reject(label,fn,rows)
        DATA['type_rejections']=rows
        rows=[]
        for label,mut in [
            ('late_domain_context',lambda x:x[1]['synthetic_domain_INPUT_plans']['two_sources'].__setitem__('context_sha256','0'*64)),
            ('late_retained_sourceSHA',lambda x:x[2]['synthetic_valid']['cases']['two_sources']['sources'][-1].__setitem__('domain_source_sha256','0'*64)),
            ('late_baseline_domain',lambda x:x[1]['synthetic_validated_domains']['two_sources'].__setitem__('scope','foreign')),
            ('late_retained_guard_bool_alias',lambda x:x[2]['synthetic_valid']['cases']['two_sources']['sources'][-1].__setitem__('whole_box_guard_admission_disproved',1)),
            ('late_retained_INPUT_falseflag',lambda x:x[2]['synthetic_valid']['cases']['two_sources']['sources'][-1].__setitem__(c.FALSE[0],True))]:
            x=copy.deepcopy(self.loaded);mut(x)
            with patch.object(c,'component_wordclasses_HOST',side_effect=AssertionError('ALL INPUT before predicates')) as spy:
                self.reject(label,lambda:self.audit('synthetic_valid',x),rows);self.assertEqual(spy.call_count,0)
        with patch.object(c,'PARENT_SHA','0'*64):self.reject('parent_SHA',c.load_retained,rows)
        DATA['INPUT_rejections']=rows
if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
    print(json.dumps({'tests':result.testsRun,'PASS':result.wasSuccessful(),'data':DATA},sort_keys=True))
    raise SystemExit(not result.wasSuccessful())

"""Exact HOST UNIT-link tests, no native producer or previous suite."""
import copy,json,sys,unittest
from fractions import Fraction as F
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'benchmarks/capacity_audit'))
import axial_SOURCE_uniform_UNIT_ORIGINAL_link_HOST_v1 as c
DATA={}
class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.loaded=c.load_retained()
    def audit(self,v,loaded=None):
        with patch.object(c,'load_retained',return_value=self.loaded if loaded is None else loaded):
            return c.audit_link_HOST(v,model=c.MODEL,arithmetic_model=c.ARITH)
    def link(self,box,charges):return c.link_bound_HOST(box,charges,model=c.MODEL,arithmetic_model=c.ARITH)
    def reject(self,label,fn,rows):
        try:fn()
        except (ValueError,KeyError,TypeError,IndexError) as e:rows.append({'label':label,'reason':str(e)})
        else:self.fail('expected reject '+label)
    def test_a_missing(self):
        with patch.object(c,'link_bound_HOST',side_effect=AssertionError('no new numeric link')),patch.object(c.producer,'validate_retained_unit',side_effect=AssertionError('no point inspection')):
            a=self.audit('real_missing');b=self.audit('explicit_None_missing')
        x=copy.deepcopy(a);y=copy.deepcopy(b);x.pop('variant');y.pop('variant');self.assertEqual(x,y)
        self.assertEqual(len(a['cases']),17);self.assertTrue(all(v['sources'] is None for v in a['cases'].values()))
        self.assertEqual(sum(len(v['context']['source_order']) for v in a['cases'].values()),19)
        DATA['real_missing']=a;DATA['explicit_None_missing']=b
    def test_b_anchored_no_replay(self):
        with patch.object(c.producer,'execute',side_effect=AssertionError('native SOURCE')),patch.object(c.producer.prior,'execute',side_effect=AssertionError('native UNIT')),patch.object(c.prior,'product_bound_HOST',side_effect=AssertionError('old constructor')):
            a=self.audit('synthetic_domains')
        self.assertEqual((a['analytical_UNIT_links'],a['blocked_guard_boxes_preserved']),(2,2))
        for case in a['cases'].values():
            for row in case['sources']:
                self.assertEqual(len(row['bare_charges_L1']),14);self.assertTrue(row['link'][c.FLAG]);self.assertTrue(row['whole_box_guard_admission_disproved'])
                self.assertIsNone(row['uniform_executed_SOURCE_error_L1']);self.assertIsNone(row['phase_bound_rad'])
        DATA['synthetic_domains']=a
    def test_c_algebra_controls(self):
        charges=dict.fromkeys(c.producer.UNIT_NAMES,[0,1]);charges['coefficient_L1']=[1,100]
        boxes={'zero':[[[0,1],[0,1]],[[0,1],[0,1]]],
          'sign_crossing':[[[-2,1],[3,1]],[[-5,1],[4,1]]],
          'negative':[[[-4,1],[-2,1]],[[-3,1],[-1,1]]],
          'positive':[[[2,1],[4,1]],[[1,1],[3,1]]]}
        results={n:self.link(b,charges) for n,b in boxes.items()}
        self.assertEqual(results['sign_crossing']['ORIGINAL_SOURCE_box_norm_L1_bound'],[8,1])
        self.assertEqual(results['zero']['uniform_A_times_UNIT_error_to_A_times_ideal_UNIT_L1'],[0,1])
        samples=[]
        for name,box in boxes.items():
            (lo,hi),(lj,hj)=c.domain.box_values(box);eps=F(1,100)
            for a,b in ((lo,lj),(hi,hj),((lo+hi)/2,(lj+hj)/2)):
                # Delta UNIT arbitrary within retained norm bound, not a native UNIT.
                dr,di=F(3,1000),F(-7,1000)
                obs=abs(a*dr-b*di)+abs(a*di+b*dr)
                bound=F(*results[name]['uniform_A_times_UNIT_error_to_A_times_ideal_UNIT_L1'])
                self.assertLessEqual(obs,(abs(a)+abs(b))*eps);self.assertLessEqual(obs,bound)
                samples.append({'box':name,'A_reim':[c.pair(a),c.pair(b)],'delta_UNIT_reim':[c.pair(dr),c.pair(di)],'observed_L1':c.pair(obs)})
        DATA['algebra_controls']=results;DATA['algebra_examples_not_continuum_proof']=samples
    def test_d_types_dependencies(self):
        rows=[];q=dict.fromkeys(c.producer.UNIT_NAMES,[0,1]);box=[[[0,1],[1,1]],[[0,1],[1,1]]]
        bad=copy.deepcopy(q);bad['coefficient_L1']=[True,1]
        neg=copy.deepcopy(q);neg['square_L1']=[-1,10]
        huge=copy.deepcopy(q);huge['Taylor_L1']=[1,1]
        graph=c.io.read(c.GRAPH,self.loaded[8][c.GRAPH]).decode()
        for name,fn in [
          ('model',lambda:c.link_bound_HOST(box,q,model='foreign',arithmetic_model=c.ARITH)),
          ('arithmetic',lambda:c.link_bound_HOST(box,q,model=c.MODEL,arithmetic_model='FTZ')),
          ('bool_charge',lambda:self.link(box,bad)),('negative_charge',lambda:self.link(box,neg)),
          ('large_UNIT',lambda:self.link(box,huge)),('missing_charge',lambda:self.link(box,{})),
          ('reversed_box',lambda:self.link([[[1,1],[0,1]],[[0,1],[1,1]]],q)),
          ('SOURCE_dependent_UNIT',lambda:c.dependency_contract(graph.replace("aw=admission['argument_uint64']","aw=admission['field_reim']")))]:
            self.reject(name,fn,rows)
        DATA['typed_dependency_rejections']=rows
    def test_e_ALL_INPUT_before_link(self):
        rows=[]
        for name,mut in [
          ('late_context',lambda x:x[1]['synthetic_domain_INPUT_plans']['thin_resolved'].__setitem__('context_sha256','0'*64)),
          ('late_gauge',lambda x:x[6]['cases']['thin_resolved']['sources'][0].__setitem__('phase_reference_id','foreign')),
          ('late_product_digest',lambda x:x[5]['synthetic_domains']['cases']['thin_resolved']['sources'][0].__setitem__('retained_bare_SOURCE_row_sha256','0'*64)),
          ('late_bool_guard',lambda x:x[5]['synthetic_domains']['cases']['thin_resolved']['sources'][0].__setitem__('whole_box_guard_admission_disproved',1)),
          ('late_UNIT_charge',lambda x:x[6]['cases']['thin_resolved']['sources'][0]['result']['unit_L1_charges_to_FIXED_ORIGINAL'].__setitem__('Taylor_L1',[0,1]))]:
            x=copy.deepcopy(self.loaded);mut(x)
            with patch.object(c,'link_bound_HOST',side_effect=AssertionError('ALL INPUT first')) as spy:
                self.reject(name,lambda:self.audit('synthetic_domains',x),rows);self.assertEqual(spy.call_count,0)
        with patch.object(c,'PARENT_SHA','0'*64),patch.object(c,'link_bound_HOST',side_effect=AssertionError('SHA first')) as spy:
            self.reject('parent_SHA',c.load_retained,rows);self.assertEqual(spy.call_count,0)
        DATA['INPUT_SHA_rejections']=rows
if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
    print(json.dumps({'tests':result.testsRun,'PASS':result.wasSuccessful(),'data':DATA},sort_keys=True))
    raise SystemExit(not result.wasSuccessful())

"""CPU1/60s own conditional reflection/phase tests; no native execution."""
import copy,json,sys,unittest
from fractions import Fraction as F
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'benchmarks/capacity_audit'))
import axial_SOURCE_uniform_ideal_reflection_phase_HOST_v1 as c
DATA={}
class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.loaded=c.load_retained()
    def audit(self,v,loaded=None):
        with patch.object(c,'load_retained',return_value=self.loaded if loaded is None else loaded):
            return c.audit_reflected_phase_HOST(v,model=c.MODEL,material_model=c.MATERIAL_MODEL)
    def prove(self,box,q):return c.reflected_phase_HOST(box,q,model=c.MODEL,material_model=c.MATERIAL_MODEL)
    def reject(self,label,fn,rows):
        try:fn()
        except (ValueError,KeyError,TypeError,IndexError) as e:rows.append({'label':label,'reason':str(e)})
        else:self.fail('expected reject '+label)
    def test_a_missing(self):
        with patch.object(c,'reflected_phase_HOST',side_effect=AssertionError('no phase on missing domain')):
            a=self.audit('real_missing');b=self.audit('explicit_None_missing')
        x=copy.deepcopy(a);y=copy.deepcopy(b);x.pop('variant');y.pop('variant');self.assertEqual(x,y)
        self.assertEqual(len(a['cases']),17);self.assertEqual(sum(len(v['context']['source_order']) for v in a['cases'].values()),19)
        self.assertTrue(all(v['sources'] is None for v in a['cases'].values()))
        DATA['real_missing']=a;DATA['explicit_None_missing']=b
    def test_b_anchored_no_replay(self):
        with patch.object(c.prior,'link_bound_HOST',side_effect=AssertionError('old constructor')),patch.object(c.prior.producer,'execute',side_effect=AssertionError('native SOURCE')):
            a=self.audit('synthetic_domains')
        self.assertEqual(a['conditional_reflected_phase_bounds'],2)
        for v in a['cases'].values():
            for row in v['sources']:
                p=row['proof'];self.assertTrue(p[c.FLAG]);self.assertTrue(row['whole_box_guard_admission_disproved'])
                self.assertEqual(len(p['fifteen_conditional_reflected_charges_L1']),15)
                self.assertIsNone(p['executed_material_charge_L1']);self.assertIsNone(p['uniform_executed_SOURCE_error_L1'])
                self.assertIsNone(p['phase_INPUT_quota_fits']);self.assertFalse(p['material_executed'])
        DATA['synthetic_domains']=a
    def test_c_disk_boundaries_isometry(self):
        box=[[[2,1],[3,1]],[[-1,1],[1,1]]];origin=[[[-1,1],[1,1]],[[-1,1],[1,1]]]
        def q(e):
            d=dict.fromkeys(c.CHARGES,[0,1]);d[c.CHARGES[0]]=c.pair(e);return d
        controls={'missing':self.prove(box,None),'zero':self.prove(box,q(F(0))),
            'strict':self.prove(box,q(F(1,2))),'equal':self.prove(box,q(F(2))),
            'above':self.prove(box,q(F(3))),'origin':self.prove(origin,q(F(0)))}
        self.assertEqual(controls['strict']['conditional_principal_phase_bound_rad'],[1,3])
        self.assertEqual(controls['zero']['conditional_principal_phase_bound_rad'],[0,1])
        for n in ('missing','equal','above','origin'):
            self.assertFalse(controls[n][c.FLAG]);self.assertIsNone(controls[n]['conditional_principal_phase_bound_rad'])
        self.assertIsNone(controls['missing']['fifteen_conditional_reflected_charges_L1'])
        examples=[]
        for z,w in [((F(2),F(0)),(F(3),F(1))),((F(-1),F(1)),(F(2),F(-3))),((F(0),F(0)),(F(0),F(0)))]:
            pre=sum((abs(x-y) for x,y in zip(z,w)),F(0));post=sum((abs(-x-(-y)) for x,y in zip(z,w)),F(0))
            self.assertEqual(pre,post);examples.append({'z':list(map(c.pair,z)),'w':list(map(c.pair,w)),'error_before':c.pair(pre),'error_after':c.pair(post)})
        DATA['boundary_controls']=controls;DATA['isometry_examples_not_execution']=examples
    def test_d_types(self):
        box=[[[1,1],[2,1]],[[0,1],[1,1]]];q=dict.fromkeys(c.CHARGES,[0,1]);b=copy.deepcopy(q);b[c.CHARGES[0]]=[True,1]
        n=copy.deepcopy(q);n[c.CHARGES[0]]=[-1,10];rows=[]
        for name,fn in [
          ('model',lambda:c.reflected_phase_HOST(box,q,model='foreign',material_model=c.MATERIAL_MODEL)),
          ('physical_material',lambda:c.reflected_phase_HOST(box,q,model=c.MODEL,material_model='Fresnel')),
          ('bool_charge',lambda:self.prove(box,b)),('negative_charge',lambda:self.prove(box,n)),
          ('missing_charge',lambda:self.prove(box,{})),('reversed_box',lambda:self.prove([[[2,1],[1,1]],[[0,1],[1,1]]],q)),
          ('None_endpoint',lambda:self.prove([[None,[1,1]],[[0,1],[1,1]]],q))]:
            self.reject(name,fn,rows)
        DATA['typed_rejections']=rows
    def test_e_ALL_INPUT_before_phase(self):
        rows=[]
        def mat(x):return x[3]['cases']['thin_resolved']['sources'][0]
        def cert(x):return x[2]['synthetic_domains']['cases']['thin_resolved']['sources'][0]
        for name,mut in [
          ('late_context',lambda x:x[1]['synthetic_domain_INPUT_plans']['thin_resolved'].__setitem__('context_sha256','0'*64)),
          ('late_material_phase',lambda x:mat(x)['material_profile'].__setitem__('mirror_phase_ORIGINAL_uint64',1023<<52)),
          ('late_coefficient_bool',lambda x:mat(x)['material_profile'].__setitem__('ideal_coefficient_exact_reim',[[-1,True],[0,1]])),
          ('late_material_gauge',lambda x:mat(x).__setitem__('terminal_reference_id','foreign')),
          ('late_source_binding',lambda x:mat(x).__setitem__('retained_source_row_sha256','0'*64)),
          ('late_bare_total',lambda x:cert(x).__setitem__('uniform_bare_RN_model_bound_to_A_times_ideal_UNIT_L1',[0,1]))]:
            x=copy.deepcopy(self.loaded);mut(x)
            with patch.object(c,'reflected_phase_HOST',side_effect=AssertionError('ALL INPUT before phase')) as spy:
                self.reject(name,lambda:self.audit('synthetic_domains',x),rows);self.assertEqual(spy.call_count,0)
        with patch.object(c,'PARENT_SHA','0'*64),patch.object(c,'reflected_phase_HOST',side_effect=AssertionError('SHA first')) as spy:
            self.reject('parent_SHA',c.load_retained,rows);self.assertEqual(spy.call_count,0)
        DATA['INPUT_SHA_rejections']=rows
if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
    print(json.dumps({'tests':result.testsRun,'PASS':result.wasSuccessful(),'data':DATA},sort_keys=True))
    raise SystemExit(not result.wasSuccessful())

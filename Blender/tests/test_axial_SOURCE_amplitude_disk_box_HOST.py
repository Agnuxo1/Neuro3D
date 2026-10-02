"""Conditional interval controls are hypotheses, not execution or scene enclosure."""
import copy,json,struct,sys,unittest
from fractions import Fraction as F
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'benchmarks/capacity_audit'))
import axial_SOURCE_amplitude_disk_box_HOST_v1 as core
DATA={}
class BoxTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.loaded=core.load_retained();packets,stage,_=cls.loaded
        cls.real=stage['real_missing']['case_order'];cls.names=['nonexact_geometry_phase_PASS','thin_resolved'];cls.plans={}
        for name in cls.names:
            ctx=stage['synthetic_partial']['cases'][name]['context'];snap,_=core.original.snapshot_from_packet(packets[name],ctx)
            rows=[]
            for i,a in enumerate(ctx['assignments']):
                center=[F.from_float(x) for x in snap['sources'][i]['field_reim']]
                box=[[core.pair(x-F(1,1000000)),core.pair(x+F(1,1000000))] for x in center]
                rows.append({k:a[k] for k in ('source_id','source_phase_reference_id','terminal_reference_id','common_terminal_reference_id')})
                rows[-1]['box_reim']=box
            cls.plans[name]={'model':core.MODEL,'units':core.UNITS,'context_sha256':core.digest(ctx),'scope':core.SCOPE,'sources':rows}
        DATA['synthetic_domain_INPUT_plans']=copy.deepcopy(cls.plans)
    def audit(self,names,plans):
        with patch.object(core,'load_retained',return_value=self.loaded):
            return core.audit_scene_domains_HOST(names,plans,model=core.MODEL)
    def reject(self,label,fn,rows):
        try:fn()
        except (ValueError,KeyError,TypeError,IndexError) as e:rows.append({'label':label,'reason':str(e)})
        else:self.fail('expected reject '+label)
    def test_a_missing(self):
        a=self.audit(self.real,{})
        b=self.audit(self.real,{n:None for n in self.real})
        self.assertEqual(a,b);self.assertEqual((len(a['cases']),a['domain_INPUT_valid_cases']),(17,0))
        self.assertEqual(sum(len(c['context']['source_order']) for c in a['cases'].values()),19)
        DATA['real_missing']=a
    def test_b_scene_domains_missing_uniform(self):
        with patch.object(core.prior,'inspect_certificate',side_effect=AssertionError('no point error substitution')),patch.object(core.prior.phase.prior.prior,'execute',side_effect=AssertionError('no native execution')):
            a=self.audit(self.names,self.plans)
        self.assertEqual(a['domain_INPUT_valid_cases'],2);self.assertFalse(a['uniform_SOURCE_enclosure_proved'])
        for c in a['cases'].values():
            self.assertIsNone(c['uniform_executed_SOURCE_error_L1']);self.assertEqual(c['status'],'STOP')
            for row in c['domain_INPUT']['sources']:
                lemma=row['conditional_geometry']
                self.assertFalse(lemma[core.FLAG]);self.assertIsNone(lemma['conditional_phase_bound_rad'])
                self.assertFalse(row['domain_authentication']);self.assertFalse(row['uniform_SOURCE_enclosure_proved'])
        DATA['synthetic_scene_domains']=a
    def test_c_conditional_controls(self):
        controls={}
        eps=[1,10000000000000000]
        for name,p in self.plans.items():
            box=p['sources'][0]['box_reim']
            out=core.conditional_disk_box_HOST(box,eps,model=core.MODEL)
            self.assertTrue(out[core.FLAG]);self.assertFalse(out['uniform_SOURCE_enclosure_proved'])
            self.assertIsNone(out['uniform_executed_SOURCE_error_L1'])
            controls[name]=out
        controls['negative_components']=core.conditional_disk_box_HOST([[[-2,1],[-1,1]],[[-3,1],[-2,1]]],[1,10],model=core.MODEL)
        controls['axis_zero_component']=core.conditional_disk_box_HOST([[[1,1],[2,1]],[[-1,1],[1,1]]],[0,1],model=core.MODEL)
        self.assertEqual(controls['negative_components']['amplitude_lower_bound'],[2,1])
        self.assertEqual(controls['axis_zero_component']['conditional_phase_bound_rad'],[0,1])
        DATA['conditional_controls']=controls
    def test_d_zero_and_typing(self):
        rows=[]
        bad=[
            ('origin_inside',[[[-1,1],[1,1]],[[-1,1],[1,1]]],[1,100]),
            ('origin_boundary',[[[0,1],[1,1]],[[0,1],[1,1]]],[0,1]),
            ('epsilon_equal_m',[[[1,1],[2,1]],[[0,1],[0,1]]],[1,1]),
            ('epsilon_above_m',[[[1,1],[2,1]],[[0,1],[0,1]]],[2,1]),
            ('reversed',[[[2,1],[1,1]],[[0,1],[0,1]]],[0,1]),
            ('bool_endpoint',[[[True,1],[2,1]],[[0,1],[0,1]]],[0,1]),
            ('noncanonical',[[[2,2],[2,1]],[[0,1],[0,1]]],[0,1]),
            ('float_endpoint',[[[1.0,1],[2,1]],[[0,1],[0,1]]],[0,1]),
            ('negative_epsilon',[[[1,1],[2,1]],[[0,1],[0,1]]],[-1,1]),
            ('bool_epsilon',[[[1,1],[2,1]],[[0,1],[0,1]]],[False,1]),
            ('oversize',[[[1<<4097,1],[1<<4098,1]],[[0,1],[0,1]]],[0,1])]
        for label,box,eps in bad:self.reject(label,lambda:core.conditional_disk_box_HOST(box,eps,model=core.MODEL),rows)
        missing=core.conditional_disk_box_HOST([[[-1,1],[1,1]],[[-1,1],[1,1]]],None,model=core.MODEL)
        self.assertIsNone(missing['conditional_phase_bound_rad']);self.assertFalse(missing[core.FLAG])
        DATA['lemma_rejections']=rows;DATA['origin_box_missing_error']=missing
    def test_e_domain_binding(self):
        rows=[]
        def src(p):return p['thin_resolved']['sources'][0]
        mutations=[
            ('context',lambda p:p['thin_resolved'].__setitem__('context_sha256','0'*64)),
            ('units',lambda p:p['thin_resolved'].__setitem__('units','power')),
            ('scope',lambda p:p['thin_resolved'].__setitem__('scope','geometry_and_wavelength')),
            ('source',lambda p:src(p).__setitem__('source_id','foreign')),
            ('source_gauge',lambda p:src(p).__setitem__('source_phase_reference_id','foreign')),
            ('terminal',lambda p:src(p).__setitem__('terminal_reference_id','foreign')),
            ('omission',lambda p:p['thin_resolved']['sources'].clear()),
            ('anchor_outside',lambda p:src(p).__setitem__('box_reim',[[[7,1],[8,1]],[[7,1],[8,1]]])),
            ('point_error_as_uniform',lambda p:p['thin_resolved'].__setitem__('uniform_error_sup_L1',[0,1]))]
        for label,mut in mutations:
            plans=copy.deepcopy(self.plans);mut(plans)
            self.reject(label,lambda:self.audit(self.names,plans),rows)
        with patch.object(core,'PARENT_SHA','0'*64):self.reject('parent_SHA',core.load_retained,rows)
        DATA['domain_rejections']=rows
if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(BoxTests))
    print(json.dumps({'tests':result.testsRun,'PASS':result.wasSuccessful(),'data':DATA},sort_keys=True))
    raise SystemExit(not result.wasSuccessful())

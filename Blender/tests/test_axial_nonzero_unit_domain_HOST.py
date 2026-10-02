"""Bounded own tests for conditional nonzero unit/ORIGINAL composition."""
import copy,json,sys,unittest
from pathlib import Path
from unittest.mock import patch
from fractions import Fraction as F
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'benchmarks/capacity_audit'))
import axial_nonzero_unit_domain_HOST_v1 as core
DATA={}
class NonzeroDomainTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packets,cls.domain,cls.rect,cls.uniform,cls.pins=core.load_retained()
        cls.n='thin_resolved';cls.ctx=cls.domain['cases'][cls.n]['context']
        cls.d=cls.domain['cases'][cls.n]['sources'][0];cls.r=cls.rect['cases'][cls.n]['sources'][0]
        cls.u=cls.uniform['cases'][cls.n]['sources'][0];cls.profile=cls.uniform['coefficient_profile']
        cls.cap=[1,10**12]
    def test_scene_domain_composition(self):
        a=core.audit_nonzero_unit_domain_HOST(self.domain['case_order'],model=core.MODEL);DATA['audit']=a
        self.assertEqual((a['restricted_nonzero_source_unit_bounds_proved'],a['retained_unit_STOPs'],a['zero_domains_outside_scope']),(2,14,3))
        self.assertEqual(a['inherited_pins_verified'],298)
        found=[]
        for n,c in a['cases'].items():
            for s in c['sources']:
                self.assertEqual(s['status'],'STOP')
                for k in core.FALSE:self.assertIs(s[k],False)
                if s[core.FLAG]:
                    found.append(n);p=s['proof']
                    B=F(*map(int,p['polynomial_unit_L1_bound_decimal']))
                    delta=core.number(p['composed_parameter_argument_phase_bound_rad'])
                    self.assertEqual(F(*map(int,p['uniform_unit_L1_to_fixed_ORIGINAL_bound_decimal'])),B+2*delta)
                    phase=F(*map(int,p['uniform_phase_to_fixed_ORIGINAL_bound_decimal']))
                    self.assertEqual(phase,B/(1-B)+delta);self.assertLessEqual(phase,F(1,10**12))
                    self.assertEqual(len(p['normal_node_labels']),26)
                    self.assertFalse(p['uniform_unit_error_to_ORIGINAL_proved'])
        self.assertEqual(set(found),{'thin_resolved','nonexact_geometry_phase_PASS'})
        other=a['cases']['two_sources']['sources'][1]
        self.assertFalse(other[core.FLAG]);self.assertNotIn('proof',other)
    def test_pure_analytical_bounds(self):
        B,t,trace,normal=core.analytic_horner(self.u['interval_theorem']['declared_angle_interval'],self.profile)
        self.assertGreater(B,0);self.assertEqual(len(trace),26);self.assertEqual(len(normal),26)
        DATA['analytical_summary']={'interval':self.u['interval_theorem']['declared_angle_interval'],
          'bound_decimal':[str(B.numerator),str(B.denominator)],'terms_sha256':core.digest(t),'trace_sha256':core.digest(trace)}
    def test_rejections(self):
        rejected=[];DATA['rejections']=rejected
        def reject(label,fn):
            with self.assertRaises((ValueError,TypeError,KeyError,IndexError)) as cm:fn()
            rejected.append({'label':label,'reason':str(cm.exception)})
        for label,mut in [
            ('domain_absent',lambda d,r,u,p,c:d.__setitem__('restricted_coordinate_box_to_parameter_rectangle_proved',False)),
            ('rectangle_SHA',lambda d,r,u,p,c:d.__setitem__('retained_argument_rectangle_source_sha256','0'*64)),
            ('uniform_SHA',lambda d,r,u,p,c:r.__setitem__('retained_uniform_unit_source_sha256','0'*64)),
            ('source',lambda d,r,u,p,c:d.__setitem__('source_id','other')),
            ('assignment_gauge',lambda d,r,u,p,c:c['assignments'][0].__setitem__('terminal_reference_id','other')),
            ('source_gauge',lambda d,r,u,p,c:c['assignments'][0].__setitem__('source_phase_reference_id','other')),
            ('ORIGINAL_absent',lambda d,r,u,p,c:d['restricted_domain_proof'].__setitem__('ORIGINAL_inside_coordinate_box',False)),
            ('clearance',lambda d,r,u,p,c:d['restricted_domain_proof']['uniform_affine_selector_proof'].__setitem__('mirror_first_uniform_clearance',False)),
            ('departure',lambda d,r,u,p,c:d['restricted_domain_proof']['uniform_affine_selector_proof'].__setitem__('strict_positive_first_and_reflected_second',False)),
            ('length',lambda d,r,u,p,c:r['parameter_branch'].__setitem__('length_interval',[[0,1],[0,1]])),
            ('wavelength',lambda d,r,u,p,c:r['parameter_branch'].__setitem__('wavelength_interval',[[1,1],[1,1]])),
            ('quarter_branch',lambda d,r,u,p,c:r['parameter_branch'].__setitem__('quarter_branch_over_rectangle_proved',False)),
            ('quarter_index',lambda d,r,u,p,c:r['parameter_branch'].__setitem__('quarter_turn_endpoint_integers',[0,0])),
            ('image_absent',lambda d,r,u,p,c:r['argument_image'].__setitem__('argument_image_over_declared_rectangle_enclosed',False)),
            ('RN_graph_absent',lambda d,r,u,p,c:r['argument_image'].__setitem__('old_argument_RN_graph_defined_over_declared_rectangle',False)),
            ('no_coverage',lambda d,r,u,p,c:r.__setitem__('retained_uniform_unit_interval_covers_argument_image',False)),
            ('argument_zero',lambda d,r,u,p,c:r['argument_image'].__setitem__('argument_interval',[[0,1],[0,1]])),
            ('coefficient_word',lambda d,r,u,p,c:p['cos'][2].__setitem__('uint64',0x3ff0000000000000)),
            ('coefficient_error',lambda d,r,u,p,c:p['sin'][2].__setitem__('error_rational',[0,1])),
            ('FMA',lambda d,r,u,p,c:u['interval_theorem'].__setitem__('arithmetic_hypothesis','FMA')),
            ('native_admission',lambda d,r,u,p,c:u['interval_theorem'].__setitem__('inherited_runner_accepts_entire_interval',True)),
            ('trace_hash',lambda d,r,u,p,c:u['interval_theorem'].__setitem__('node_intervals_sha256','0'*64)),
            ('bound_hidden',lambda d,r,u,p,c:u['interval_theorem'].__setitem__('unit_L1_error_to_ideal_at_represented_angle_uniform_bound',[0,1])),
            ('phase_hidden',lambda d,r,u,p,c:u['interval_theorem'].__setitem__('additional_phase_uniform_bound_rad',[0,1])),
            ('cap_enlarged',lambda d,r,u,p,c:d.__setitem__('unchanged_original_phase_cap_rad',[1,1])),
            ('old_NONfit',lambda d,r,u,p,c:d.__setitem__('retained_unit_polynomial_charge_fits',False)),
            ('composed_charge',lambda d,r,u,p,c:r['argument_image'].__setitem__('uniform_composed_parameter_phase_to_fixed_ORIGINAL_rad',[0,1])),
            ('negative_argument_charge',lambda d,r,u,p,c:r['argument_image'].__setitem__('uniform_argument_error_bound_rad',[-1,1]))]:
            d,r,u,p,c=copy.deepcopy((self.d,self.r,self.u,self.profile,self.ctx));mut(d,r,u,p,c)
            # Rebind the controlled mutation's diamond hashes so later numeric/gauge guards are exercised.
            if label not in ('rectangle_SHA','uniform_SHA'):
                r['retained_uniform_unit_source_sha256']=core.digest(u);d['retained_argument_rectangle_source_sha256']=core.digest(r)
            reject(label,lambda d=d,r=r,u=u,p=p,c=c:core.compose_domain(c,d,r,u,p,self.cap))
        for label,interval in [('zero',[[0,1],[0,1]]),('cross_zero',[[-1,10],[1,10]]),
                               ('outside_Horner',[[1,1],[2,1]]),('reverse',[[1,2],[1,4]])]:
            reject(label,lambda interval=interval:core.analytic_horner(interval,self.profile))
        for label,n,m in [('model',['thin_resolved'],'wrong'),('empty',[],core.MODEL),
                          ('duplicate',['thin_resolved','thin_resolved'],core.MODEL),('unknown',['unknown'],core.MODEL)]:
            reject(label,lambda n=n,m=m:core.audit_nonzero_unit_domain_HOST(n,model=m))
        read=Path.read_bytes;target=core.io.ROOT/core.PREVIOUS
        with patch.object(Path,'read_bytes',lambda p:read(p)+b' ' if p==target else read(p)):
            reject('predecessor_SHA',core.load_retained)
    def test_fixed_profile_and_input_not_mutated(self):
        before=core.digest((self.d,self.r,self.u,self.profile,self.ctx))
        core.compose_domain(self.ctx,self.d,self.r,self.u,self.profile,self.cap)
        self.assertEqual(before,core.digest((self.d,self.r,self.u,self.profile,self.ctx)))
if __name__=='__main__':
    r=unittest.TextTestRunner(verbosity=2,stream=sys.stderr).run(unittest.defaultTestLoader.loadTestsFromTestCase(NonzeroDomainTests))
    print(json.dumps({'PASS':r.wasSuccessful(),'tests':r.testsRun,'data':DATA},sort_keys=True,separators=(',',':'),allow_nan=False))
    raise SystemExit(0 if r.wasSuccessful() else 1)

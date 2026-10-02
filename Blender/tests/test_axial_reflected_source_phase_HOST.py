"""SOURCE phase proof is point/gauge bound, not a uniform or group promotion."""
import copy,json,math,struct,sys,unittest
from fractions import Fraction as F
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'benchmarks/capacity_audit'))
import axial_reflected_source_phase_HOST_v1 as core
DATA={}
def word(x):return struct.unpack('<Q',struct.pack('<d',x))[0]
class SourcePhaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.loaded=core.load_retained();cls.names=list(cls.loaded[0][0][0])
    def reject(self,label,fn,rows):
        try:fn()
        except (ValueError,KeyError,TypeError,IndexError) as e:rows.append({'label':label,'reason':str(e)})
        else:self.fail('expected STOP '+label)
    def test_a_retained(self):
        before=core.digest(self.loaded)
        with patch.object(core,'load_retained',return_value=self.loaded),patch.object(core.prior.prior,'execute',side_effect=AssertionError('no native reflection replay')),patch.object(core.prior,'audit_reflected_budget_HOST',side_effect=AssertionError('no previous budget reexecution')):
            a=core.audit_source_phase_HOST(self.names,model=core.MODEL)
        self.assertEqual(core.digest(self.loaded),before)
        self.assertEqual((a['point_source_phase_certificates'],a['retained_sources_STOP']),(2,17))
        for c in a['cases'].values():
            self.assertEqual(c['status'],'STOP');self.assertTrue(all(c[n] is False for n in core.FALSE))
            for row in c['sources']:
                self.assertTrue(all(row[n] is False for n in core.FALSE))
                if row[core.FLAG]:
                    p=row['proof'];self.assertIsNone(p['phase_INPUT_quota_fits'])
                    self.assertGreater(core.guard.rational(p['positive_radial_projection_lower_bound']),0)
                    self.assertEqual(core.guard.rational(p['point_principal_phase_distance_bound_rad']),
                        core.guard.rational(p['point_reflected_error_L1'])/core.guard.rational(p['positive_radial_projection_lower_bound']))
                else:self.assertIsNone(row['proof'])
        DATA['audit']=a
    def test_b_disk(self):
        accepted=[];rejected=[]
        for label,words,out,e in [
            ('signed_zero_component',[word(-0.),word(1.)],[word(0.),word(-1.)],[0,1]),
            ('near_zero_positive_margin',[word(2.**-100),word(0.)],[word(2.**-100),word(0.)],[1,2**101]),
            ('opposite_components',[word(1.),word(-1.)],[word(-1.),word(1.)],[1,10]),
            ('near_boundary',[word(1.),word(0.)],[word(1.),word(0.)],[999,1000])]:
            accepted.append({'label':label,'proof':core.disk_phase_bound_HOST(words,out,e)})
        for label,words,out,e in [
            ('zero_ORIGINAL',[0,1<<63],[word(1.),0],[0,1]),
            ('disk_touches_zero',[word(1.),0],[word(1.),0],[1,1]),
            ('disk_contains_zero',[word(1.),0],[word(1.),0],[2,1]),
            ('negative_error',[word(1.),0],[word(1.),0],[-1,1]),
            ('bool_error',[word(1.),0],[word(1.),0],[False,1]),
            ('zero_output',[word(1.),0],[0,1<<63],[0,1]),
            ('bool_word',[True,0],[word(1.),0],[0,1]),
            ('subnormal_ORIGINAL',[1,0],[word(1.),0],[0,1]),
            ('nonfinite_OUTPUT',[word(1.),0],[word(float('inf')),0],[0,1]),
            ('wrong_dimension',[word(1.)],[word(1.),0],[0,1])]:
            self.reject(label,lambda words=words,out=out,e=e:core.disk_phase_bound_HOST(words,out,e),rejected)
        DATA['disk_controls']={'accepted':accepted,'rejected':rejected}
    def test_c_atomic(self):
        rows=[]
        def c(r):return r[0][1]['cases']['thin_resolved']
        mutations=[
            ('reflection_word',lambda r:c(r)['sources'][0]['result']['reflected_uint64'].__setitem__(0,0)),
            ('phase_gauge',lambda r:c(r)['sources'][0]['result'].__setitem__('phase_reference_id','foreign')),
            ('material_zero_launder',lambda r:c(r)['sources'][0]['result']['fifteen_source_material_charges_L1'].__setitem__('ideal_material_L1',[1,1])),
            ('source_omission',lambda r:c(r)['sources'].clear()),
            ('eligibility_bool_as_int',lambda r:c(r)['sources'][0].__setitem__(core.prior.prior.FLAG,1)),
            ('bare_ORIGINAL_word',lambda r:r[0][0][1]['cases']['thin_resolved']['sources'][0]['result']['source_encoder']['ORIGINAL_source_uint64'].__setitem__(0,0))]
        for label,f in mutations:
            r=copy.deepcopy(self.loaded);f(r)
            with patch.object(core,'load_retained',return_value=r):
                self.reject(label,lambda:core.audit_source_phase_HOST(['nonexact_geometry_phase_PASS','thin_resolved'],model=core.MODEL),rows)
        for label,ns,m in [('unknown',['foreign'],core.MODEL),('duplicate',['thin_resolved']*2,core.MODEL),('empty',[],core.MODEL),('model',['thin_resolved'],'foreign')]:
            with patch.object(core,'load_retained',return_value=self.loaded):
                self.reject(label,lambda ns=ns,m=m:core.audit_source_phase_HOST(ns,model=m),rows)
        with patch.object(core,'PARENT_SHA','0'*64):self.reject('parent_SHA',core.load_retained,rows)
        DATA['atomic_identity_rejections']=rows
    def test_d_independent_angle_examples(self):
        # Synthetic diagnostic only, not a proof of actual scene output/transcendental reference.
        rows=[]
        for a in [(1.,0.),(-1.,0.),(0.,1.),(1.,-1.)]:
            for delta in [(0.,2.**-20),(2.**-20,0.),(-2.**-20,-2.**-20)]:
                z=(a[0]+delta[0],a[1]+delta[1]);eps=F.from_float(abs(delta[0]))+F.from_float(abs(delta[1]))
                p=core.disk_phase_bound_HOST(list(map(word,a)),list(map(word,z)),[eps.numerator,eps.denominator])
                bound=core.guard.rational(p['point_principal_phase_distance_bound_rad'])
                angle=abs(math.atan2(z[1]*a[0]-z[0]*a[1],z[0]*a[0]+z[1]*a[1]))
                self.assertLessEqual(angle,float(bound))
                rows.append({'ORIGINAL':a,'delta':delta,'angle_diagnostic':angle,'bound_rad':float(bound)})
        DATA['synthetic_angle_diagnostics']=rows
if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(SourcePhaseTests))
    print(json.dumps({'tests':result.testsRun,'PASS':result.wasSuccessful(),'data':DATA},sort_keys=True))
    raise SystemExit(not result.wasSuccessful())

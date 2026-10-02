"""Uniform polynomial interval regression suite; no old producer or RN replay."""
import hashlib,json,sys,unittest
from pathlib import Path
from unittest.mock import patch
from fractions import Fraction as F
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'benchmarks/capacity_audit'))
import axial_uniform_unit_HOST_v1 as core
import axial_amplitude_allocation_HOST_v1 as allocation
DATA={}
class UnitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packets,cls.units,cls.pins=core.load_retained()
        cls.profile=core.coefficient_profile(cls.units)
        cls.before={n:allocation.digest(p) for n,p in cls.packets.items()}
        DATA['audit']=core.audit_uniform_unit_HOST(list(cls.packets),model=core.MODEL)
        DATA['primitives']=[core.uniform_unit_interval_HOST(v,model=core.MODEL) for v in
                            ([[0,1],[0,1]],[[-1,1],[1,1]],[[1,8],[1,4]],[[-1,2],[1,2]],
                             [[-1,1],[-1,2]],[[1,2],[1,1]])]
        DATA['rejections']=[];DATA['retained_point_checks']=[]
    def test_whole_declared_intervals_not_original_scene(self):
        a=DATA['audit'];self.assertEqual(a['inherited_pins_verified'],253)
        self.assertEqual(a['uniform_intervals_computed'],5);self.assertEqual(a['retained_unit_STOPs'],14)
        self.assertEqual(len(a['cases']),17)
        for c in a['cases'].values():
            for s in c['sources']:
                self.assertEqual(s['status'],'STOP')
                for k in core.FALSE:self.assertIs(s[k],False)
                if s['theorem_computed']:
                    t=s['interval_theorem'];self.assertEqual(t['bounded_RN_nodes'],26)
                    self.assertTrue(t['uniform_theorem_for_declared_angle_interval_proved'])
                    self.assertIsNone(s['composed_ORIGINAL_uniform_error'])
        self.assertEqual(self.before,{n:allocation.digest(p) for n,p in self.packets.items()})
    def test_preserved_stop_sources_gauges_and_caps(self):
        for n,c in DATA['audit']['cases'].items():
            old=self.units[n]
            self.assertEqual([s['source_id'] for s in c['sources']],old['source_order'])
            for s,o in zip(c['sources'],old['sources']):
                self.assertEqual(s['retained_unit_source_sha256'],allocation.digest(o))
                if not s['theorem_computed']:self.assertEqual(s['reason'],o['reason'])
                else:
                    self.assertEqual(s['unchanged_original_phase_cap_rad'],o['unchanged_original_phase_cap_rad'])
                    charge=F(*s['interval_theorem']['additional_phase_uniform_bound_rad'])
                    self.assertEqual(s['polynomial_charge_alone_fits_unchanged_phase_cap'],
                                     charge<=F(*s['unchanged_original_phase_cap_rad']))
        self.assertEqual(DATA['audit']['cases']['two_sources']['sources'][1]['status'],'STOP')
        self.assertFalse(DATA['audit']['cases']['two_sources']['sources'][1]['theorem_computed'])
    def test_retained_nodes_and_outputs_inside_uniform_enclosures(self):
        for n,c in DATA['audit']['cases'].items():
            for s,old in zip(c['sources'],self.units[n]['sources']):
                if not s['theorem_computed']:continue
                t=s['interval_theorem']
                for k,corner in enumerate(old['encoded_corner_units_HOST']):
                    rot=corner['rotation_RN64']
                    for op,bound in zip(rot['operations'],t['node_intervals']):
                        self.assertEqual(op['label'],bound['label'])
                        self.assertLessEqual(abs(F(*op['rounding_delta_rational'])),F(*bound['rounding_charge_abs']))
                        y=core.decode(op['output_uint64']);lo,hi=map(lambda v:F(*v),bound['output_interval'])
                        self.assertLessEqual(lo,y);self.assertLessEqual(y,hi)
                    for name,term in rot['terms'].items():
                        self.assertLessEqual(F(*term['actual_polynomial_error_rational']),
                                             F(*t['terms'][name]['polynomial_error_uniform_bound']))
                    DATA['retained_point_checks'].append({'case':n,'source_id':s['source_id'],'corner_index':k,
                        'corner_sha256':allocation.digest(corner),'nodes_checked':26,'old_RN_reexecuted':0})
        self.assertEqual(len(DATA['retained_point_checks']),20)
    def test_synthetic_domain_and_separate_charge_recurrences(self):
        self.assertEqual(len(DATA['primitives']),6)
        for t in DATA['primitives']:
            self.assertEqual(t['bounded_RN_nodes'],26)
            self.assertEqual(t['coefficient_profile_sha256'],allocation.digest(self.profile))
            for k in core.FALSE:self.assertIs(t[k],False)
            for term in t['terms'].values():
                self.assertEqual(set(term['error_charges']),{'coefficients','square','RN_nodes'})
                self.assertEqual(sum(F(*v) for v in term['error_charges'].values()),
                                 F(*term['polynomial_error_uniform_bound']))
        total=F(*DATA['primitives'][1]['additional_phase_uniform_bound_rad'])
        self.assertGreater(total,F(1,10**12)) # entire [-1,1] charge not silently relaxed to PASS
        self.assertEqual(DATA['primitives'][0]['terms']['cos']['Taylor_uniform_remainder'],[0,1])
    def test_reject_domain_and_injections(self):
        def reject(label,fn,exc=ValueError):
            with self.assertRaises(exc) as caught:fn()
            DATA['rejections'].append({'label':label,'reason':str(caught.exception)})
        for label,v in [('bool',[[True,1],[1,1]]),('unreduced',[[0,2],[1,1]]),
                        ('NaN',[[float('nan'),1],[1,1]]),('unordered',[[1,1],[0,1]]),
                        ('outside',[[0,1],[2,1]]),('large_endpoint',[[0,1],[1,2**257]]),
                        ('negative_denominator',[[0,-1],[1,1]]),('shape',[[0,1]])]:
            reject(label,lambda v=v:core.uniform_unit_interval_HOST(v,model=core.MODEL))
        reject('wrong_model',lambda:core.uniform_unit_interval_HOST([[0,1],[1,1]],model='other'))
        for n in ([],['positive','positive'],['unknown'],[True]):
            reject('names_'+str(n),lambda n=n:core.audit_uniform_unit_HOST(n,model=core.MODEL))
        for key,value in [('interval',[[0,1],[1,1]]),('profile',{}),('cap',[1,1]),
                          ('scene_argument_enclosed',True),('certificate',{})]:
            reject('caller_'+key,lambda key=key,value=value:core.audit_uniform_unit_HOST(
                ['positive'],model=core.MODEL,**{key:value}),TypeError)
    def test_corrupt_retained_input_no_silent_fallback(self):
        target=core.io.ROOT/core.PREVIOUS;original=Path.read_bytes;raw=original(target);bad=raw+b' '
        with patch.object(Path,'read_bytes',lambda p:bad if p==target else original(p)):
            with self.assertRaises(ValueError) as caught:core.audit_uniform_unit_HOST(['positive'],model=core.MODEL)
        DATA['rejections'].append({'label':'changed_receipt','reason':str(caught.exception),
                                   'changed_sha256':hashlib.sha256(bad).hexdigest()})
if __name__=='__main__':
    r=unittest.TextTestRunner(verbosity=2,stream=sys.stderr).run(unittest.defaultTestLoader.loadTestsFromTestCase(UnitTests))
    def compact(value):
        if type(value) is dict:
            return {('node_intervals_sha256' if k=='node_intervals' else k):
                    (allocation.digest(v) if k=='node_intervals' else compact(v)) for k,v in value.items()}
        if type(value) is list:
            if len(value)==2 and all(type(x) is int for x in value) and max(abs(x).bit_length() for x in value)>256:
                return {'exact_rational_sha256':allocation.digest(value),
                        'numerator_bits':abs(value[0]).bit_length(),'denominator_bits':value[1].bit_length()}
            return [compact(v) for v in value]
        return value
    print(json.dumps({'PASS':r.wasSuccessful(),'tests':r.testsRun,'data':compact(DATA)},sort_keys=True,separators=(',',':'),allow_nan=False))
    raise SystemExit(0 if r.wasSuccessful() else 1)

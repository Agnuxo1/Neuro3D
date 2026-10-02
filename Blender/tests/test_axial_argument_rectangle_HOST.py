"""Parameter rectangle branch/enclosure regression tests, no prior RN producer replay."""
import hashlib,json,sys,unittest
from fractions import Fraction as F
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'benchmarks/capacity_audit'))
import axial_argument_rectangle_HOST_v1 as core
import axial_amplitude_allocation_HOST_v1 as allocation
DATA={}
class RectangleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packets,cls.units,cls.arguments,cls.quarters,cls.uniform,cls.pins=core.load_retained()
        cls.before={n:allocation.digest(p) for n,p in cls.packets.items()}
        DATA['audit']=core.audit_argument_rectangle_HOST(list(cls.packets),model=core.MODEL)
        specs=[([[1,1],[2,1]],[[32,1],[64,1]],[1,1],[32,1]),
               ([[-2,1],[-1,1]],[[32,1],[64,1]],[-1,1],[32,1]),
               ([[7,1],[9,1]],[[16,1],[16,1]],[8,1],[16,1]),
               ([[1,1],[3,1]],[[16,1],[16,1]],[1,1],[16,1]),
               ([[1,1],[1,1]],[[8,1],[8,1]],[1,1],[8,1]),
               ([[-3,1],[-3,1]],[[1,1],[1,1]],[-3,1],[1,1]),
               ([[1,1],[1,1]],[[1,1],[1,1]],[0,1],[1,1]),
               ([[1,1],[2,1]],[[1,1],[1,1]],[1,1],[1,1])]
        DATA['primitives']=[core.rectangle_branches(l,w,o,v,model=core.MODEL) for l,w,o,v in specs]
        DATA['RN_cells']=[];DATA['rejections']=[]
    def test_declared_parameter_images_for_five_sources(self):
        a=DATA['audit'];self.assertEqual(a['inherited_pins_verified'],258)
        self.assertEqual(a['declared_rectangle_images_proved'],5);self.assertEqual(a['retained_unit_STOPs'],14)
        self.assertEqual(len(a['cases']),17)
        for c in a['cases'].values():
            for s in c['sources']:
                self.assertEqual(s['status'],'STOP')
                for k in core.FALSE:self.assertIs(s[k],False)
                if s['rectangle_evaluated']:
                    self.assertTrue(s['argument_image_over_declared_rectangle_enclosed'])
                    self.assertTrue(s['parameter_branch']['quarter_branch_over_rectangle_proved'])
                    self.assertTrue(s['retained_uniform_unit_interval_covers_argument_image'])
                    self.assertTrue(s['argument_image']['old_argument_RN_graph_defined_over_declared_rectangle'])
        self.assertEqual(self.before,{n:allocation.digest(p) for n,p in self.packets.items()})
    def test_prior_stop_and_polynomial_nonfitting_flags_preserved(self):
        nonfit=[]
        for n,c in DATA['audit']['cases'].items():
            old=self.uniform['cases'][n]
            for s,o in zip(c['sources'],old['sources']):
                self.assertEqual(s['retained_uniform_unit_source_sha256'],allocation.digest(o))
                self.assertEqual(s['retained_unit_polynomial_charge_fits'],o.get('polynomial_charge_alone_fits_unchanged_phase_cap'))
                if not s['rectangle_evaluated']:self.assertEqual(s['reason'],o['reason'])
                else:
                    cap=F(*s['unchanged_original_phase_cap_rad'])
                    error=F(*s['argument_image']['uniform_composed_parameter_phase_to_fixed_ORIGINAL_rad'])
                    self.assertEqual(s['uniform_parameter_phase_alone_fits_unchanged_cap'],error<=cap)
                    if s['retained_unit_polynomial_charge_fits'] is False:nonfit.append(n)
        self.assertEqual(sorted(nonfit),['negative','positive','two_sources'])
        self.assertFalse(DATA['audit']['cases']['two_sources']['sources'][1]['rectangle_evaluated'])
    def test_branch_crossings_exact_ties_negative_reference(self):
        p=DATA['primitives']
        self.assertTrue(p[0]['quarter_branch_over_rectangle_proved'])
        self.assertEqual(p[0]['quotient_interval'],[[1,64],[1,16]])
        self.assertEqual(p[1]['quotient_interval'],[[-1,16],[-1,64]])
        self.assertFalse(p[2]['centered_branch_over_rectangle_proved'])
        self.assertTrue(p[3]['centered_branch_over_rectangle_proved']);self.assertFalse(p[3]['quarter_branch_over_rectangle_proved'])
        self.assertTrue(p[4]['quarter_branch_over_rectangle_proved'])
        self.assertEqual(p[4]['quarter_residual_interval'],[[-1,8],[-1,8]]) # exact eighth tie, no snapping
        self.assertEqual(p[5]['ORIGINAL_centered_turn'],-3)
        self.assertEqual(p[5]['quarter_residual_interval'],[[0,1],[0,1]])
        self.assertFalse(p[6]['centered_branch_over_rectangle_proved'])
        self.assertFalse(p[7]['centered_branch_over_rectangle_proved'])
    def test_exact_endpoint_cells_even_odd_and_zero(self):
        one=0x3ff0000000000000;half=F(1,2**53)
        specs=[(F(1),one),(F(1)+half,one),(F(1)+F(3,2**53),one+2),
               (F(-1),one|(1<<63)),(F(0),0),(-F(1,2**1076),1<<63)]
        for x,w in specs:
            c=core.rn_cell_contains(x,w);DATA['RN_cells'].append(c)
            self.assertTrue(c['rounding_cell_membership_proved']);self.assertEqual(c['new_RN_executed'],0)
        with self.assertRaises(ValueError):core.rn_cell_contains(F(1)+half,one+1)
        with self.assertRaises(ValueError):core.rn_cell_contains(F(1)+F(1,2**51),one)
    def test_malformed_and_injected_scene_evidence(self):
        def reject(label,fn,exc=ValueError):
            with self.assertRaises(exc) as caught:fn()
            DATA['rejections'].append({'label':label,'reason':str(caught.exception)})
        for label,w in [('bool',[False]+[0]*15),('negative',[-1]+[0]*15),('oversize',[2**32]+[0]*15),('short',[0]*15)]:
            reject(label,lambda w=w:core.signed512(w))
        valid=[[0,1],[1,1]]
        for label,l,w in [('wavezero',valid,[[0,1],[1,1]]),('wavenegative',valid,[[-1,1],[1,1]]),
                          ('lengthunordered',[[1,1],[0,1]],[[1,1],[1,1]]),
                          ('waveunordered',valid,[[2,1],[1,1]]),('unreduced',[[0,2],[1,1]],[[1,1],[1,1]]),
                          ('NaN',[[float('nan'),1],[1,1]],[[1,1],[1,1]]),
                          ('bits',[[0,1],[2**513,1]],[[1,1],[1,1]])]:
            reject(label,lambda l=l,w=w:core.rectangle_branches(l,w,[0,1],[1,1],model=core.MODEL))
        reject('model',lambda:core.rectangle_branches(valid,[[1,1],[1,1]],[0,1],[1,1],model='other'))
        for names in ([],['positive','positive'],['unknown'],[True]):
            reject('names_'+str(names),lambda names=names:core.audit_argument_rectangle_HOST(names,model=core.MODEL))
        for key,v in [('rectangle',{}),('cap',[1,1]),('endpoint_words',[0]),('scene_argument_enclosed',True)]:
            reject('caller_'+key,lambda key=key,v=v:core.audit_argument_rectangle_HOST(['positive'],model=core.MODEL,**{key:v}),TypeError)
        reject('RN_word',lambda:core.rn_cell_contains(F(1),0x7ff0000000000000))
        reject('RN_tie_odd',lambda:core.rn_cell_contains(F(1)+F(1,2**53),0x3ff0000000000001))
    def test_changed_predecessor_receipt(self):
        target=core.io.ROOT/core.PREVIOUS;original=Path.read_bytes;raw=original(target);bad=raw+b' '
        with patch.object(Path,'read_bytes',lambda p:bad if p==target else original(p)):
            with self.assertRaises(ValueError) as caught:core.audit_argument_rectangle_HOST(['positive'],model=core.MODEL)
        DATA['rejections'].append({'label':'changed_receipt','reason':str(caught.exception),'changed_sha256':hashlib.sha256(bad).hexdigest()})
if __name__=='__main__':
    r=unittest.TextTestRunner(verbosity=2,stream=sys.stderr).run(unittest.defaultTestLoader.loadTestsFromTestCase(RectangleTests))
    print(json.dumps({'PASS':r.wasSuccessful(),'tests':r.testsRun,'data':DATA},sort_keys=True,separators=(',',':'),allow_nan=False))
    raise SystemExit(0 if r.wasSuccessful() else 1)

"""Quarter HOST tests only, fresh own scene dependencies; no old suites/writers."""
import base64
from copy import deepcopy
from fractions import Fraction as F
import hashlib,json
from pathlib import Path
import sys,unittest,zlib
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'benchmarks/capacity_audit'))
import axial_quarter_argument_HOST_v1 as core
ROOT=Path(__file__).resolve().parents[2]
PREVIOUS='coordinacion/respuestas/AXIAL-NATIVE-ARGUMENT-HOST-001-CODEX.json'
SHA='fbf0fae9b15300df84debfc4fd9a1f7da05d7c4d2221562d4366d9f0fc330bb4'
def digest(v):return hashlib.sha256(v).hexdigest()
def canon(v):return core.prev.quotient.phase.canon(v)
def payload(r):
    t=r['test_run'];b=zlib.decompress(base64.b64decode(t.get('stdout_zlib_base64') or ''.join(t['stdout_zlib_base64_chunks']),validate=True))
    assert t['rc']==0 and len(b)==t['stdout_bytes'] and digest(b)==t['stdout_sha256']
    return json.loads(b)
def pins_from(r):
    if 'code_doc_sha256' in r:return dict(r['code_doc_sha256'])
    dep=r['inherited_pin_source'];b=(ROOT/dep['path']).read_bytes();assert digest(b)==dep['sha256']
    pins=pins_from(json.loads(b));pins[dep['path']]=dep['sha256'];pins.update(r['own_code_doc_sha256']);return pins
def words(n):
    assert -(1<<511)<=n<(1<<511)
    return [(n>>(32*i))&0xffffffff for i in range(16)]
def check(v):
    r=F(*v['original_residual_cycles_rational']);t=F(*v['quarter_residual_HOST_rational']);k=v['quarter_turns_HOST']
    assert k==(4*r+F(1,2)).__floor__() and t==r-F(k,4) and -F(1,8)<=t<F(1,8)
    assert k%4==v['quadrant_mod4'] and v['exact_selector_error_cycles']==[0,1]
    cast=core.prev.component64(v['HOST_cast_uint64']);p=core.prev.component64(v['TWO_PI_uint64'])
    arg=core.prev.component64(v['HOST_argument_uint64'])
    assert F(*v['HOST_cast_rational'])==cast and F(*v['HOST_argument_rational'])==arg and abs(arg)<=1
    charges={key:F(*q) for key,q in v['quarter_argument_charges_rad'].items()}
    assert charges=={'HOST_quarter_RN64_cast':abs(p)*abs(cast-t),
        'constant_2pi':abs(t)*F(*v['TWO_PI_error_bound_rad']),'modeled_RN64_multiply':abs(arg-cast*p)}
    bound=sum(charges.values(),F(0));assert v['quarter_argument_error_bound_rad']==[bound.numerator,bound.denominator]
    assert max(abs(arg-2*pi*t) for pi in (core.prev.PI_LOWER,core.prev.PI_UPPER))<=bound

class QuarterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b=(ROOT/PREVIOUS).read_bytes();assert digest(b)==SHA;r=json.loads(b)
        cls.pins=pins_from(r);cls.pins[PREVIOUS]=SHA
        for p,h in cls.pins.items():assert digest((ROOT/p).read_bytes())==h,p
        cls.old=payload(r);cls.packets=payload(json.loads((ROOT/'coordinacion/respuestas/AXIAL-NATIVE-INGRESS-001-CODEX.json').read_bytes()))['packets']
        controls=payload(json.loads((ROOT/'coordinacion/respuestas/AXIAL-NATIVE-PRESENCE-STOPS-001-CODEX.json').read_bytes()))['synthetic_controls']
        cls.before={n:canon(p) for n,p in cls.packets.items()};cls.cases={}
        for n,p in cls.packets.items():
            h=digest(canon(p));o=core.prev.quotient.phase.original_cap_overlay_HOST_only(n,p,h)
            cls.cases[n]=core.audit_scene_quarter_HOST(n,p,h,o,digest(canon(o)),model=core.MODEL)
        for n,c in controls.items():
            cls.cases[n]=core.audit_scene_quarter_HOST(c['case_name'],c['parent'],digest(canon(c['parent'])),c['overlay'],digest(canon(c['overlay'])),model=core.MODEL)
        cls.primitives=[core.quarter_argument_HOST(v['numerator_words'],v['denominator_words'],model=core.MODEL) for v in cls.old['primitives']]
        pairs=[(-1,2),(0,1),(1,(1<<511)-1)]
        pairs += [(n*(1<<51)+delta,1<<54) for n in (-3,-1,1,3) for delta in (-1,0,1)]
        pairs += [(s*((1<<53)+o),1<<55) for s in (-1,1) for o in (1,3)]
        pairs += [(((1<<511)-1)//8+1,(1<<511)-1)]
        cls.controls=[core.quarter_argument_HOST(words(n),words(d),model=core.MODEL) for n,d in pairs]
    def test_upstream_proofs_scene_bindings_and_INPUT_immutable(self):
        for n,c in self.cases.items():
            old=self.old['cases'][n]
            for key in ('input_packet_sha256','overlay_sha256','scene_binding_sha256','word_ABI_sha256','source_order'):
                self.assertEqual(c[key],old[key])
            for row,p in zip(c['sources'],old['sources']):self.assertEqual(row['upstream_argument_proof'],core.projection(p))
        for n,p in self.packets.items():self.assertEqual(canon(p),self.before[n])
    def test_original_separate_corners_caps_and_same_quarter_gate(self):
        for c in self.cases.values():
            for row in c['sources']:
                p=row['upstream_argument_proof']
                self.assertEqual(row['quarter_HOST_evaluated'],p['accepted_argument_bound_CPU_only'])
                if not row['quarter_HOST_evaluated']:continue
                original=row['ideal_ORIGINAL_quarter_argument'];values=row['encoded_corner_quarter_arguments']
                check(original)
                for v in values:check(v)
                same=all(v['quarter_turns_HOST']==original['quarter_turns_HOST'] for v in values)
                self.assertEqual(row['same_exact_quarter_branch'],same)
                extra=max(F(*v['quarter_argument_error_bound_rad']) for v in values)
                total=F(*p['upstream_phase_error_bound_rad'])+extra;budget=F(*p['unchanged_original_phase_cap_rad'])
                self.assertEqual(row['composed_quarter_error_bound_rad'],core.pair(total))
                self.assertEqual(row['unchanged_original_phase_cap_rad'],p['unchanged_original_phase_cap_rad'])
                self.assertEqual(row['accepted_quarter_argument_bound_CPU_only'],same and total<=budget)
                self.assertTrue(row['ORIGINAL_is_NOT_encoded_nominal'])
    def test_declared_radius_quarter_crossing_STOP_even_if_budget_fits(self):
        row=self.cases['declared_radius_PASS']['sources'][0]
        self.assertTrue(row['upstream_argument_proof']['accepted_argument_bound_CPU_only'])
        self.assertFalse(row['same_exact_quarter_branch']);self.assertFalse(row['accepted_quarter_argument_bound_CPU_only'])
        self.assertEqual(row['reason'],core.CROSS)
        self.assertLessEqual(F(*row['composed_quarter_error_bound_rad']),F(*row['unchanged_original_phase_cap_rad']))
        self.assertEqual([row['ideal_ORIGINAL_quarter_argument']['quarter_turns_HOST']]+[v['quarter_turns_HOST'] for v in row['encoded_corner_quarter_arguments']],[0,-1,-1,1,1])
    def test_no_revive_13_upstream_STOP_including_other_zero_cap(self):
        stops=[r for c in self.cases.values() for r in c['sources'] if not r['quarter_HOST_evaluated']]
        self.assertEqual(len(stops),13)
        for row in stops:
            self.assertEqual(row['reason'],row['upstream_argument_proof']['reason'])
            self.assertFalse(row['accepted_quarter_argument_bound_CPU_only']);self.assertNotIn('encoded_corner_quarter_arguments',row)
        for n in ('two_sources','missing_cap_two_sources'):
            row=next(v for v in self.cases[n]['sources'] if v['source_id']=='other')
            self.assertEqual(row['reason'],'HOST argument charges exceed unchanged original phase cap')
    def test_130_primitives_exact_selector_RN64_bound(self):
        for v in self.primitives:check(v)
    def test_twenty_boundary_tie_extreme_controls_arbitrary_HOST_width(self):
        self.assertEqual(len(self.controls),20)
        for v in self.controls:check(v)
        for v in self.controls:
            if F(*v['original_residual_cycles_rational']) in (F(-3,8),F(-1,8),F(1,8),F(3,8)):
                self.assertEqual(v['quarter_residual_HOST_rational'],[-1,8])
        self.assertGreater(self.controls[-1]['quarter_residual_HOST_rational'][1].bit_length(),512)
    def test_invalid_words_denominator_domain_explicit_model(self):
        bad=[([],words(1)),([True]+[0]*15,words(1)),([1<<32]+[0]*15,words(1)),(words(1),words(0)),
             (words(1),words(-1)),(words(1),words(2)),(words(-2),words(3))]
        for n,d in bad:
            with self.assertRaises(ValueError):core.quarter_argument_HOST(n,d,model=core.MODEL)
        with self.assertRaises(ValueError):core.quarter_argument_HOST(words(0),words(1),model='other')
        with self.assertRaises(TypeError):core.quarter_argument_HOST(words(0),words(1))
    def test_HOST_only_no_unit_native_fields_GPU_or_fullpipeline(self):
        for c in self.cases.values():
            self.assertIs(c['HOST_only'],True)
            for key in ('native_quarter_implemented','ALU_executed','Bpy_executed','quarter_unit_permutation_executed',
                        'phase_unit_evaluated','field_values_computed','GPU_executed','GPU_job_admission','execution_authenticated','accepted_full_field_pipeline'):
                self.assertIs(c[key],False)
            self.assertEqual(c['accepted_quarter_argument_bound_CPU_only'],all(v['accepted_quarter_argument_bound_CPU_only'] for v in c['sources']))

calls=[];rejects=[]
if __name__=='__main__':
    original=core.quarter_argument_HOST
    def capture(*args,**kwargs):
        try:v=original(*args,**kwargs)
        except (ValueError,TypeError) as e:
            rejects.append({'inputs':deepcopy(list(args)),'kwargs':deepcopy(kwargs),'type':type(e).__name__,'reason':str(e)});raise
        calls.append(deepcopy(v));return v
    core.quarter_argument_HOST=capture
    run=unittest.TextTestRunner(stream=sys.stderr,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(QuarterTests))
    print(json.dumps({'PASS':run.wasSuccessful(),'tests':run.testsRun,'pins':getattr(QuarterTests,'pins',{}),
        'cases':getattr(QuarterTests,'cases',{}),'primitives':getattr(QuarterTests,'primitives',[]),
        'controls':getattr(QuarterTests,'controls',[]),'calls':calls,'expected_rejections':rejects,'GPU_executed':False},
        sort_keys=True,separators=(',',':'),allow_nan=False))
    raise SystemExit(0 if run.wasSuccessful() else 1)

"""New HOST bridge only; own pure round64 helper, no old suite/producer execution."""
import base64
from copy import deepcopy
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import sys
import unittest
import zlib
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'benchmarks/capacity_audit'))
import axial_native_argument_HOST_v1 as core
ROOT=Path(__file__).resolve().parents[2]
PREVIOUS='coordinacion/respuestas/AXIAL-NATIVE-QUOTIENT-001-CODEX.json'
SHA='c79ee5920e9cc9962bc8464139fb94e3c577fdb635e70c9f281e3acc416802a8'
def digest(v):return hashlib.sha256(v).hexdigest()
def canon(v):return core.quotient.phase.canon(v)
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
    residual=F(*v['residual_cycles_rational']);rep=core.component64(v['HOST_residual_uint64'])
    p=core.component64(v['TWO_PI_uint64']);arg=core.component64(v['HOST_argument_uint64'])
    assert F(*v['HOST_residual_rational'])==rep and F(*v['HOST_argument_rational'])==arg
    assert F(*v['multiply_rounding_delta_rational'])==arg-rep*p
    charges={k:F(*q) for k,q in v['new_argument_charges_rad'].items()}
    assert charges['HOST_residual_RN64_cast']==abs(p)*abs(rep-residual)
    assert charges['constant_2pi']==abs(residual)*F(*v['TWO_PI_error_bound_rational'])
    assert charges['modeled_RN64_multiply']==abs(arg-rep*p)
    assert sum(charges.values(),F(0))==F(*v['new_argument_error_bound_rad'])
    target=sorted((2*core.PI_LOWER*residual,2*core.PI_UPPER*residual))
    assert max(abs(arg-x) for x in target)<=sum(charges.values(),F(0))
class ArgumentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b=(ROOT/PREVIOUS).read_bytes();assert digest(b)==SHA;r=json.loads(b)
        cls.pins=pins_from(r);cls.pins[PREVIOUS]=SHA
        for p,h in cls.pins.items():assert digest((ROOT/p).read_bytes())==h,p
        cls.retained=payload(r);presence=json.loads((ROOT/'coordinacion/respuestas/AXIAL-NATIVE-PRESENCE-STOPS-001-CODEX.json').read_bytes())
        cls.controls=payload(presence)['synthetic_controls']
        cls.packets=payload(json.loads((ROOT/'coordinacion/respuestas/AXIAL-NATIVE-INGRESS-001-CODEX.json').read_bytes()))['packets']
        cls.before={n:canon(p) for n,p in cls.packets.items()};cls.cases={}
        for n,p in cls.packets.items():
            h=digest(canon(p));o=core.quotient.phase.original_cap_overlay_HOST_only(n,p,h)
            cls.cases[n]=core.audit_scene_argument_HOST(n,p,h,o,digest(canon(o)),model=core.MODEL)
        for label,c in cls.controls.items():
            cls.cases[label]=core.audit_scene_argument_HOST(c['case_name'],c['parent'],digest(canon(c['parent'])),
                              c['overlay'],digest(canon(c['overlay'])),model=core.MODEL)
        cls.primitives=[core.argument_HOST(v['centered_numerator_words'],v['centered_denominator_words'],model=core.MODEL)
                        for v in cls.retained['primitives']]
    def test_fresh_own_upstream_exact_and_INPUT_frozen_unchanged(self):
        for n,c in self.cases.items():self.assertEqual(c['upstream'],self.retained['cases'][n])
        for n,p in self.packets.items():self.assertEqual(canon(p),self.before[n])
    def test_rational_charges_and_ORIGINAL_reference_not_nominal(self):
        for c in self.cases.values():
            for old,row,proof in zip(c['upstream']['sources'],c['sources'],c['upstream']['upstream']['sources']):
                self.assertEqual(row['argument_HOST_evaluated'],old['accepted_centered_branch_CPU_only'])
                if row['argument_HOST_evaluated']:
                    check(row['ideal_original_argument_HOST'])
                    for v in row['encoded_enclosure_arguments_HOST']:check(v)
                    self.assertTrue(row['original_is_NOT_encoded_nominal'])
                    original=old['original_ideal_cycles'];ori=F(core.integer_HOST(original['length_words']),core.integer_HOST(original['wavelength_words']))
                    expected=8*max(abs(F(core.integer_HOST(v['length_words']),core.integer_HOST(v['wavelength_words']))-ori) for v in old['encoded_enclosure_corner_cycles'])
                    self.assertEqual(row['upstream_phase_error_bound_rad'],core.pair(expected))
                    cap=proof['original_phase_cap'];budget=F(core.integer_HOST(cap['numerator_words']),core.integer_HOST(cap['denominator_words']))
                    self.assertEqual(row['unchanged_original_phase_cap_rad'],core.pair(budget))
                    total=expected+max(F(*v['new_argument_error_bound_rad']) for v in row['encoded_enclosure_arguments_HOST'])
                    self.assertEqual(row['composed_argument_error_bound_rad'],core.pair(total))
                    self.assertEqual(row['accepted_argument_bound_CPU_only'],total<=budget)
    def test_all_130_signed_boundary_random_residuals(self):
        for v in self.primitives:check(v)
    def test_RN64_ties_to_even_zero_half_and_small_normal(self):
        pairs=[(0,1),(-1,2),(1,(1<<511)-1)]
        pairs += [(s*((1<<53)+offset),1<<55) for s in (-1,1) for offset in (1,3)]
        self.__class__.tie_controls=[]
        for n,d in pairs:
            v=core.argument_HOST(words(n),words(d),model=core.MODEL);check(v)
            self.__class__.tie_controls.append(v)
        self.assertEqual(self.__class__.tie_controls[0]['HOST_argument_uint64'],0)
        for v in self.__class__.tie_controls[3:]:self.assertEqual(v['HOST_residual_uint64']&1,0)
    def test_no_revive_upstream_STOP_or_missing_cap(self):
        for c in self.cases.values():
            for old,row in zip(c['upstream']['sources'],c['sources']):
                if not old['accepted_centered_branch_CPU_only']:
                    self.assertFalse(row['argument_HOST_evaluated']);self.assertFalse(row['accepted_argument_bound_CPU_only'])
                    self.assertEqual(row['reason'],old['reason'])
                    self.assertNotIn('encoded_enclosure_arguments_HOST',row)
        rows={v['source_id']:v for v in self.cases['missing_cap_two_sources']['sources']}
        self.assertFalse(rows['s']['argument_HOST_evaluated']);self.assertTrue(rows['other']['argument_HOST_evaluated'])
    def test_new_charge_FAIL_preserved_not_caps_relaxed(self):
        charged=[r for c in self.cases.values() for r in c['sources'] if r['argument_HOST_evaluated']]
        self.assertTrue(any(not r['accepted_argument_bound_CPU_only'] for r in charged))
        for r in charged:
            if not r['accepted_argument_bound_CPU_only']:
                self.assertEqual(r['reason'],'HOST argument charges exceed unchanged original phase cap')
    def test_invalid_words_denominator_domain_opt_in_fail_closed(self):
        bad=[([],words(1)),([True]+[0]*15,words(1)),([1<<32]+[0]*15,words(1)),(words(1),words(0)),
             (words(1),words(-1)),(words(1),words(2)),(words(-2),words(3))]
        for n,d in bad:
            with self.assertRaises(ValueError):core.argument_HOST(n,d,model=core.MODEL)
        with self.assertRaises(ValueError):core.argument_HOST(words(0),words(1),model='other')
        with self.assertRaises(TypeError):core.argument_HOST(words(0),words(1))
    def test_HOST_only_no_unit_fields_native_GPU_Bpy_AUTH_fullpipeline(self):
        for c in self.cases.values():
            self.assertIs(c['HOST_only'],True)
            for k in ('native_argument_implemented','ALU_executed','Bpy_executed','phase_unit_evaluated',
                      'field_values_computed','accepted_full_field_pipeline','GPU_executed','GPU_job_admission','execution_authenticated'):self.assertIs(c[k],False)
            self.assertEqual(c['accepted_argument_bound_CPU_only'],all(v['accepted_argument_bound_CPU_only'] for v in c['sources']))
calls=[];rejections=[]
if __name__=='__main__':
    original=core.argument_HOST
    def capture(*args,**kwargs):
        try:v=original(*args,**kwargs)
        except (TypeError,ValueError) as error:
            rejections.append({'inputs':deepcopy(list(args)),'kwargs':deepcopy(kwargs),'type':type(error).__name__,'reason':str(error)});raise
        calls.append(deepcopy(v));return v
    core.argument_HOST=capture
    r=unittest.TextTestRunner(stream=sys.stderr,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ArgumentTests))
    print(json.dumps({'PASS':r.wasSuccessful(),'tests':r.testsRun,'pins':getattr(ArgumentTests,'pins',{}),
        'cases':getattr(ArgumentTests,'cases',{}),'primitives':getattr(ArgumentTests,'primitives',[]),
        'tie_controls':getattr(ArgumentTests,'tie_controls',[]),'calls':calls,'expected_rejections':rejections,
        'GPU_executed':False},sort_keys=True,separators=(',',':'),allow_nan=False))
    raise SystemExit(0 if r.wasSuccessful() else 1)

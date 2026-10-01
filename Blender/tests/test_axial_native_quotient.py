"""New quotient CPU step; retained INPUTs read only, old suites/producers never run."""
import ast
import base64
from copy import deepcopy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import random
import sys
import unittest
import zlib
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'benchmarks/capacity_audit'))
import axial_native_quotient_v1 as core
ROOT=Path(__file__).resolve().parents[2]
PREVIOUS='coordinacion/respuestas/AXIAL-NATIVE-PRESENCE-STOPS-001-CODEX.json'
SHA='50bb8f64361b645394596a3982a8a811f9f2aaac3dcde9c7561661dadcd96e06'
MIN=-(1<<511);MAX=(1<<511)-1
def digest(b):return hashlib.sha256(b).hexdigest()
def canon(x):return core.phase.canon(x)
def payload(r):
    t=r['test_run'];raw=zlib.decompress(base64.b64decode(t.get('stdout_zlib_base64') or ''.join(t['stdout_zlib_base64_chunks']),validate=True))
    assert t['rc']==0 and len(raw)==t['stdout_bytes'] and digest(raw)==t['stdout_sha256']
    return json.loads(raw)
def words(n):
    assert MIN<=n<=MAX
    return [(n>>(32*i))&0xffffffff for i in range(16)]
def integer(w):
    v=sum(x<<(32*i) for i,x in enumerate(w))
    return v-(1<<512) if w[15]&0x80000000 else v
def check(v):
    n,d=integer(v['length_words']),integer(v['wavelength_words'])
    q,r=divmod(n,d);ct=(2*n+d)//(2*d);cn=n-ct*d
    assert integer(v['floor_turn_words'])==q and integer(v['euclidean_remainder_words'])==r
    assert integer(v['centered_turn_words'])==ct and integer(v['centered_numerator_words'])==cn
    assert v['centered_denominator_words']==v['wavelength_words']
    assert Fraction(-1,2)<=Fraction(cn,d)<Fraction(1,2)
    assert v['half_tie_negative']==(2*r==d)
    assert v['new_rounding_phase_error']==[0,1] and v['costs_CPU_word_operations']['bit_rounds']==512
class QuotientTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b=(ROOT/PREVIOUS).read_bytes();assert digest(b)==SHA;r=json.loads(b)
        dep=r['inherited_pin_source'];b=(ROOT/dep['path']).read_bytes();assert digest(b)==dep['sha256']
        old=json.loads(b);cls.pins=dict(old['code_doc_sha256']);cls.pins[dep['path']]=dep['sha256']
        cls.pins.update(r['own_code_doc_sha256']);cls.pins[PREVIOUS]=SHA
        for p,h in cls.pins.items():assert digest((ROOT/p).read_bytes())==h,p
        cls.retained=payload(old)['cases'];cls.presence=payload(r)['synthetic_controls']
        cls.packets=payload(json.loads((ROOT/'coordinacion/respuestas/AXIAL-NATIVE-INGRESS-001-CODEX.json').read_bytes()))['packets']
        cls.cases={};cls.inputs_before={n:canon(p) for n,p in cls.packets.items()}
        for name,p in cls.packets.items():
            h=digest(canon(p));o=core.phase.original_cap_overlay_HOST_only(name,p,h)
            cls.cases[name]=core.audit_scene_cycles(name,p,h,o,digest(canon(o)),model=core.MODEL)
        for label,c in cls.presence.items():
            cls.cases[label]=core.audit_scene_cycles(c['case_name'],c['parent'],digest(canon(c['parent'])),
                              c['overlay'],digest(canon(c['overlay'])),model=core.MODEL)
        cls.primitives=[];rng=random.Random(20261001)
        pairs=[(n,d) for n in (MIN,MIN+1,-(1<<510),-7,-1,0,1,7,1<<510,MAX-1,MAX)
               for d in (1,2,3,17,1<<510,MAX)]
        pairs += [(rng.randrange(MIN,MAX+1),rng.randrange(1,MAX+1)) for _ in range(64)]
        for n,d in pairs:cls.primitives.append(core.reduce_cycles(words(n),words(d),model=core.MODEL))
    def test_all_signed_and_random_primitives_against_independent_integers(self):
        for v in self.primitives:check(v)
    def test_exact_half_tie_and_signed_zero(self):
        for n in (-3,-1,1,3):
            v=core.reduce_cycles(words(n),words(2),model=core.MODEL);check(v)
            self.assertEqual(integer(v['centered_numerator_words']),-1)
            self.assertTrue(v['half_tie_negative'])
        for d in (1,MAX):
            v=core.reduce_cycles(words(0),words(d),model=core.MODEL);check(v)
            self.assertEqual(v['centered_numerator_words'],words(0))
    def test_new_scene_step_preserves_all_upstream_results_and_frozen_INPUTs(self):
        for n,out in self.cases.items():
            prior=self.retained[n] if n in self.retained else self.presence[n]['result']
            self.assertEqual(out['upstream'],prior)
            self.assertEqual(out['source_order'],[r['source_id'] for r in out['sources']])
        for n,p in self.packets.items():self.assertEqual(canon(p),self.inputs_before[n])
    def test_scene_rational_identity_AND_preserved_stops_per_source(self):
        for out in self.cases.values():
            for prior,row in zip(out['upstream']['sources'],out['sources']):
                self.assertEqual(row['cycle_reduction_evaluated_CPU_only'],prior['accepted_reference_phase_bound_CPU_only'])
                if row['cycle_reduction_evaluated_CPU_only']:
                    vals=[row['original_ideal_cycles']]+row['encoded_enclosure_corner_cycles']
                    self.assertEqual(len(vals),5)
                    for v in vals:check(v)
                    original=row['original_ideal_cycles']
                    self.assertEqual(original['length_words'],prior['original_effective_reference_length_words'])
                    self.assertEqual(original['wavelength_words'],prior['original_lambda_words'])
                    pairs=[(e,w) for e in prior['reference']['effective_reference_length_interval_words']
                                  for w in prior['reference']['wavelength_interval_words']]
                    self.assertEqual([(v['length_words'],v['wavelength_words']) for v in vals[1:]],pairs)
                    same=all(v['centered_turn_words']==original['centered_turn_words'] for v in vals[1:])
                    self.assertEqual(row['accepted_centered_branch_CPU_only'],same)
                else:
                    self.assertFalse(row['accepted_centered_branch_CPU_only'])
                    self.assertNotIn('original_ideal_cycles',row);self.assertNotIn('encoded_enclosure_corner_cycles',row)
                    self.assertEqual(row['reason'],prior['reason'])
    def test_signed_INT_MIN_and_near_half_exact_not_float(self):
        for n,d in ((MIN,1),(MIN,MAX),(MAX,MAX),(MAX-1,MAX),(MAX//2,MAX),(MAX//2+1,MAX)):
            v=core.reduce_cycles(words(n),words(d),model=core.MODEL);check(v)
        lo=core.reduce_cycles(words(MAX//2),words(MAX),model=core.MODEL)
        hi=core.reduce_cycles(words(MAX//2+1),words(MAX),model=core.MODEL)
        self.assertNotEqual(lo['centered_turn_words'],hi['centered_turn_words'])
    def test_half_branch_crossing_rejected_without_epsilon(self):
        original=core.reduce_cycles(words(3),words(6),model=core.MODEL)
        corners=[core.reduce_cycles(words(n),words(6),model=core.MODEL) for n in (2,2,4,4)]
        self.assertFalse(core.centered_branch_matches(original,corners))
        same=[core.reduce_cycles(words(n),words(6),model=core.MODEL) for n in (3,3,4,4)]
        self.assertTrue(core.centered_branch_matches(original,same))
        with self.assertRaises(ValueError):core.centered_branch_matches(original,[])
        self.selector_control={'original':original,'crossing_corners':corners,'same_corners':same}
        QuotientTests.selector_control=self.selector_control
    def test_fail_closed_invalid_inputs_and_explicit_opt_in(self):
        for n,d in ((words(1),words(0)),(words(1),words(-1)),(words(1),words(MIN)),
                    ([],words(1)),([True]+[0]*15,words(1)),([1<<32]+[0]*15,words(1))):
            with self.assertRaises(ValueError):core.reduce_cycles(n,d,model=core.MODEL)
        with self.assertRaises(ValueError):core.reduce_cycles(words(1),words(1),model='other')
        with self.assertRaises(TypeError):core.reduce_cycles(words(1),words(1))
    def test_no_float_Fraction_big_integer_division_in_new_implementation(self):
        tree=ast.parse((ROOT/'Blender/benchmarks/capacity_audit/axial_native_quotient_v1.py').read_text(encoding='utf-8'))
        for node in ast.walk(tree):
            if isinstance(node,ast.Constant):self.assertNotIsInstance(node.value,float)
            if isinstance(node,ast.Call) and isinstance(node.func,ast.Name):
                self.assertNotIn(node.func.id,('float','Fraction','sum','divmod'))
            if isinstance(node,ast.BinOp) and isinstance(node.op,(ast.Div,ast.FloorDiv)):
                self.assertTrue(isinstance(node.left,ast.Name) and node.left.id=='bit')
                self.assertEqual(node.right.value,32)
    def test_NO_unit_field_native_GPU_auth_or_aggregate_promotion(self):
        for out in self.cases.values():
            for k in ('phase_unit_evaluated','field_values_computed','accepted_full_field_pipeline',
                      'GLSL_compiled','GPU_executed','GPU_job_admission','execution_authenticated'):self.assertIs(out[k],False)
            self.assertEqual(out['accepted_centered_branch_CPU_only'],all(r['accepted_centered_branch_CPU_only'] for r in out['sources']))
        rows={r['source_id']:r for r in self.cases['missing_cap_two_sources']['sources']}
        self.assertFalse(rows['s']['cycle_reduction_evaluated_CPU_only'])
        self.assertTrue(rows['other']['cycle_reduction_evaluated_CPU_only'])
reduction_calls=[];expected_rejections=[]
if __name__=='__main__':
    reduce_original=core.reduce_cycles
    def traced_reduce(*args,**kwargs):
        try:value=reduce_original(*args,**kwargs)
        except (ValueError,TypeError) as error:
            expected_rejections.append({'inputs':deepcopy(list(args)),'kwargs':deepcopy(kwargs),
                                        'type':type(error).__name__,'reason':str(error)})
            raise
        reduction_calls.append(deepcopy(value));return value
    core.reduce_cycles=traced_reduce
    result=unittest.TextTestRunner(stream=sys.stderr,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(QuotientTests))
    print(json.dumps({'PASS':result.wasSuccessful(),'tests':result.testsRun,'pins':getattr(QuotientTests,'pins',{}),
                      'cases':getattr(QuotientTests,'cases',{}),'primitives':getattr(QuotientTests,'primitives',[]),
                      'selector_control':getattr(QuotientTests,'selector_control',{}),
                      'reduction_calls':reduction_calls,'expected_rejections':expected_rejections,
                      'GPU_executed':False},sort_keys=True,separators=(',',':'),allow_nan=False))
    raise SystemExit(0 if result.wasSuccessful() else 1)

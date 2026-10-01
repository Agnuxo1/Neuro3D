"""Quarter HOST tests only, fresh own scene dependencies; no old suites/writers."""
import base64
from copy import deepcopy
from fractions import Fraction as F
import hashlib,json
from pathlib import Path
import sys,unittest,zlib
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'benchmarks/capacity_audit'))
import axial_quarter_unit_HOST_v1 as core
ROOT=Path(__file__).resolve().parents[2]
PREVIOUS='coordinacion/respuestas/AXIAL-QUARTER-ARGUMENT-HOST-001-CODEX.json'
SHA='65c4355249b6d867761466e0bb37e592fb416bed2ea58f8b72c5d221ded2f439'
def digest(v):return hashlib.sha256(v).hexdigest()
def canon(v):return core.quarter.prev.quotient.phase.canon(v)
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
    rot=v['rotation_RN64'];p=core.polynomial
    for node in rot['operations']:
        a,b=map(lambda x:F(*x),node['inputs_rational']);exact=a*b if node['op']=='mul' else a+b
        observed=p.component64(node['output_uint64'])
        assert F(*node['rounding_delta_rational'])==observed-exact
    assert len(rot['operations'])==26 and len(rot['coefficients']['cos'])==len(rot['coefficients']['sin'])==7
    error=sum(F(*t['polynomial_error_upper_rational'])+F(*t['Taylor_remainder_upper_rational']) for t in rot['terms'].values())
    assert v['polynomial_Taylor_error_L1_bound']==core.pair(error) and v['additional_unit_phase_bound_rad']==core.pair(error/(1-error))
    assert v['unit_rational']==[core.pair(p.component64(w)) for w in v['unit_uint64']]
    arg=v['quarter_argument']
    assert v['unit_uint64']==p.permute64(v['unpermuted_unit_uint64'],arg['quarter_turns_HOST'])
    assert abs(sum(abs(F(*x)) for x in v['unit_rational'])-sum(abs(p.component64(w)) for w in v['unpermuted_unit_uint64']))==0
class UnitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b=(ROOT/PREVIOUS).read_bytes();assert digest(b)==SHA;r=json.loads(b)
        cls.pins=pins_from(r);cls.pins[PREVIOUS]=SHA
        for p,h in cls.pins.items():assert digest((ROOT/p).read_bytes())==h,p
        cls.old=payload(r);cls.packets=payload(json.loads((ROOT/'coordinacion/respuestas/AXIAL-NATIVE-INGRESS-001-CODEX.json').read_bytes()))['packets']
        controls=payload(json.loads((ROOT/'coordinacion/respuestas/AXIAL-NATIVE-PRESENCE-STOPS-001-CODEX.json').read_bytes()))['synthetic_controls']
        cls.before={n:canon(p) for n,p in cls.packets.items()};cls.cases={}
        for n,p in cls.packets.items():
            h=digest(canon(p));o=core.quarter.prev.quotient.phase.original_cap_overlay_HOST_only(n,p,h)
            cls.cases[n]=core.audit_scene_unit_HOST(n,p,h,o,digest(canon(o)),model=core.MODEL)
        for n,c in controls.items():
            cls.cases[n]=core.audit_scene_unit_HOST(c['case_name'],c['parent'],digest(canon(c['parent'])),c['overlay'],digest(canon(c['overlay'])),model=core.MODEL)
        pairs=[(-1,2),(0,1),(1,4),(-1,4),(1,8),(-1,8),(3,8),(-3,8)]
        cls.controls=[core.unit_HOST(words(n),words(d),model=core.MODEL) for n,d in pairs]
    def test_fresh_upstream_scene_bindings_gauges_and_INPUT_immutable(self):
        for n,c in self.cases.items():
            old=self.old['cases'][n]
            for key in ('input_packet_sha256','overlay_sha256','scene_binding_sha256','word_ABI_sha256','source_order'):self.assertEqual(c[key],old[key])
            for row,prior in zip(c['sources'],old['sources']):self.assertEqual(row['upstream_quarter_proof'],prior)
        for n,p in self.packets.items():self.assertEqual(canon(p),self.before[n])
    def test_all_unit_nodes_and_charges_and_exact_permutation(self):
        for c in self.cases.values():
            for row in c['sources']:
                if row['unit_HOST_evaluated']:
                    for v in [row['ideal_ORIGINAL_unit_HOST']]+row['encoded_corner_units_HOST']:check(v)
        for v in self.controls:check(v)
    def test_ORIGINAL_reference_phase_cap_composition_no_L1_budget_substitute(self):
        for c in self.cases.values():
            for row in c['sources']:
                p=row['upstream_quarter_proof']
                self.assertEqual(row['unit_HOST_evaluated'],p['accepted_quarter_argument_bound_CPU_only'])
                if not row['unit_HOST_evaluated']:continue
                phase=F(*p['composed_quarter_error_bound_rad']);corners=row['encoded_corner_units_HOST']
                extra=max(F(*v['additional_unit_phase_bound_rad']) for v in corners)
                l1=max(F(*v['polynomial_Taylor_error_L1_bound']) for v in corners)
                self.assertEqual(row['composed_unit_phase_bound_rad'],core.pair(phase+extra))
                self.assertEqual(row['composed_unit_error_L1_to_ORIGINAL_bound'],core.pair(2*phase+l1))
                self.assertEqual(row['unchanged_original_phase_cap_rad'],p['unchanged_original_phase_cap_rad'])
                self.assertEqual(row['accepted_unit_phase_bound_CPU_only'],phase+extra<=F(*p['unchanged_original_phase_cap_rad']))
                self.assertIs(row['amplitude_budget_accepted'],False);self.assertTrue(row['ORIGINAL_is_NOT_encoded_nominal'])
    def test_no_revive_14_previous_STOP_or_crossing_or_other_cap0(self):
        rows=[r for c in self.cases.values() for r in c['sources']]
        stops=[r for r in rows if not r['unit_HOST_evaluated']];self.assertEqual(len(stops),14)
        self.assertEqual(sum(r['accepted_unit_phase_bound_CPU_only'] for r in rows),5)
        for r in stops:
            self.assertFalse(r['accepted_unit_phase_bound_CPU_only']);self.assertEqual(r['reason'],r['upstream_quarter_proof']['reason'])
            self.assertNotIn('encoded_corner_units_HOST',r)
        r=self.cases['declared_radius_PASS']['sources'][0];self.assertEqual(r['reason'],core.quarter.CROSS)
    def test_exact_quadrants_and_signed_zeros_no_normalization(self):
        self.assertEqual([v['unit_rational'] for v in self.controls[:4]],[[[-1,1],[0,1]],[[1,1],[0,1]],[[0,1],[1,1]],[[0,1],[-1,1]]])
        for v in self.controls[:4]:self.assertEqual(v['polynomial_Taylor_error_L1_bound'],[0,1])
    def test_angular_guard_E_half_or_negative_stops(self):
        self.__class__.error_controls=[]
        for error in (F(0),F(1,8),F(499,1000),F(1,2),F(3,4),F(-1,1000)):
            try:
                b=core.angle_bound_from_L1(error);self.assertEqual(b,error/(1-error))
                self.error_controls.append({'E':core.pair(error),'bound_rad':core.pair(b),'accepted':True})
            except ValueError as e:
                self.assertFalse(0<=error<F(1,2));self.error_controls.append({'E':core.pair(error),'accepted':False,'reason':str(e)})
    def test_invalid_words_domain_denominator_model_fail_closed(self):
        bad=[([],words(1)),([True]+[0]*15,words(1)),([1<<32]+[0]*15,words(1)),(words(1),words(0)),(words(1),words(-1)),(words(1),words(2)),(words(-2),words(3))]
        for n,d in bad:
            with self.assertRaises(ValueError):core.unit_HOST(n,d,model=core.MODEL)
        with self.assertRaises(ValueError):core.unit_HOST(words(0),words(1),model='other')
        with self.assertRaises(TypeError):core.unit_HOST(words(0),words(1))
    def test_HOST_only_no_fields_source_amplitude_native_GPU_fullpipeline(self):
        for c in self.cases.values():
            self.assertIs(c['HOST_only'],True)
            for key in ('native_unit_implemented','ALU_executed','Bpy_executed','GPU_executed','GPU_job_admission','execution_authenticated','source_product_evaluated','field_values_computed','amplitude_budget_accepted','accepted_full_field_pipeline'):self.assertIs(c[key],False)
            self.assertEqual(c['accepted_unit_phase_bound_CPU_only'],all(v['accepted_unit_phase_bound_CPU_only'] for v in c['sources']))
calls=[];rejects=[]
if __name__=='__main__':
    original=core.unit_HOST
    def capture(*args,**kwargs):
        try:v=original(*args,**kwargs)
        except (ValueError,TypeError) as e:
            rejects.append({'inputs':deepcopy(list(args)),'kwargs':deepcopy(kwargs),'type':type(e).__name__,'reason':str(e)});raise
        calls.append(deepcopy(v));return v
    core.unit_HOST=capture
    run=unittest.TextTestRunner(stream=sys.stderr,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(UnitTests))
    print(json.dumps({'PASS':run.wasSuccessful(),'tests':run.testsRun,'pins':getattr(UnitTests,'pins',{}),'cases':getattr(UnitTests,'cases',{}),'controls':getattr(UnitTests,'controls',[]),'error_controls':getattr(UnitTests,'error_controls',[]),'calls':calls,'expected_rejections':rejects,'GPU_executed':False},sort_keys=True,separators=(',',':'),allow_nan=False))
    raise SystemExit(0 if run.wasSuccessful() else 1)

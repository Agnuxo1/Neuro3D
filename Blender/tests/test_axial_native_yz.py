"""Own YZ component tests; never run old scene producers."""
import base64
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
import unittest
import zlib
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'benchmarks/capacity_audit'))
import axial_native_yz_v1 as core
ROOT=Path(__file__).resolve().parents[2]
PREVIOUS='coordinacion/respuestas/AXIAL-NATIVE-SIGNED512-001-CODEX.json'
PREVIOUS_SHA='8c609597e36cb9df1324c9e396a47560984ee9bfd93c15e0c32fbf4689f0e5f1'
L=2**511
def words(n):
    if type(n) is not int or not -L<=n<L:raise ValueError('oracle range')
    return [(n%(2**512)>>(32*i))&0xffffffff for i in range(16)]
def integer(w):
    u=sum(v<<(32*i) for i,v in enumerate(w));return u-2**512 if u>=L else u
def point(y,z):return [words(y),words(z)]
def payload(report):
    t=report['test_run'];raw=zlib.decompress(base64.b64decode(t['stdout_zlib_base64']))
    assert t['rc']==0 and len(raw)==t['stdout_bytes'] and hashlib.sha256(raw).hexdigest()==t['stdout_sha256']
    return json.loads(raw)
def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
class YZTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        raw=(ROOT/PREVIOUS).read_bytes();assert hashlib.sha256(raw).hexdigest()==PREVIOUS_SHA
        prev=json.loads(raw);cls.pins=dict(prev['code_doc_sha256']);cls.pins[PREVIOUS]=PREVIOUS_SHA
        for p,h in cls.pins.items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h
        cls.packets=payload(json.loads((ROOT/'coordinacion/respuestas/AXIAL-NATIVE-INGRESS-001-CODEX.json').read_bytes()))['packets']
        cls.old=payload(json.loads((ROOT/'coordinacion/respuestas/AXIAL-GEOMETRY-WORDS-001-CODEX.json').read_bytes()))['cases']
        cls.cases={n:core.coverage(n,p,hashlib.sha256(canon(p)).hexdigest()) for n,p in cls.packets.items()}
    def test_simple_triangle_strict_edge_vertex_outside_and_winding(self):
        a,b,c=point(0,0),point(8,0),point(0,8)
        for p,expected in ((point(1,2),'strict_interior'),(point(0,2),'boundary_FAIL'),
                (point(0,0),'boundary_FAIL'),(point(4,4),'boundary_FAIL'),
                (point(9,1),'miss'),(point(-1,0),'miss')):
            self.assertEqual(core.classify_triangle(a,b,c,p)['classification'],expected)
            self.assertEqual(core.classify_triangle(a,c,b,p)['classification'],expected)
    def test_signed_translation_orientation_exact_words(self):
        offset=2**149
        a,b,c,p=[point(offset+y,-offset+z) for y,z in ((0,0),(8,0),(0,8),(1,2))]
        r=core.classify_triangle(a,b,c,p)
        self.assertEqual(list(map(integer,r['det_u_v_w_words'])),[64,8,16,40])
        self.assertEqual(r['classification'],'strict_interior')
    def test_degenerate_and_intermediate_overflow_fail_closed(self):
        r=core.classify_triangle(point(0,0),point(1,1),point(2,2),point(0,0))
        self.assertEqual(r,{'classification':'degenerate_FAIL','det_u_v_w_words':None})
        with self.assertRaises(ValueError):
            core.classify_triangle(point(0,0),point(2**300,0),point(0,2**300),point(1,1))
        with self.assertRaises(ValueError):
            core.classify_triangle(point(-L,0),point(L-1,0),point(0,1),point(0,0))
    def test_invalid_shapes_alias_and_checked_coordinates(self):
        with self.assertRaises(ValueError):core.classify_triangle([],point(1,0),point(0,1),point(0,0))
        bad=point(0,0);bad[0][0]=True
        with self.assertRaises(ValueError):core.classify_triangle(bad,point(1,0),point(0,1),point(0,0))
        a,b,c,p=point(0,0),point(8,0),point(0,8),point(1,2)
        r=core.classify_triangle(a,b,c,p);a[0][0]=999
        self.assertEqual(list(map(integer,r['det_u_v_w_words'])),[64,8,16,40])
    def test_retained_available_geometry_coverage_without_old_producer(self):
        compared=0
        for name,case in self.cases.items():
            old={r['source_id']:r for r in self.old[name]['sources']}
            self.assertFalse(case['accepted_complete_geometry']);self.assertFalse(case['GPU_executed'])
            for row in case['sources']:
                prior=old[row['source_id']]
                if prior['accepted_geometry_words_CPU_only']:
                    self.assertTrue(row['accepted_YZ_projection_component_CPU_only'])
                    self.assertEqual(row['projected_misses'],prior['projected_misses'])
                    inside=row['strict_interior_primitive_owner']
                    for segment in prior['segments']:
                        self.assertIn([segment['primitive_id'],segment['owner']],inside)
                    compared+=1
        self.assertEqual(compared,9)
    def test_boundary_kept_FAIL_and_contact_projection_not_geometry(self):
        row=self.cases['boundary_FAIL']['sources'][0]
        self.assertFalse(row['accepted_YZ_projection_component_CPU_only'])
        self.assertTrue(row['projection_failures'])
        self.assertFalse(row['accepted_complete_geometry'])
        for name in ('source_contact_FAIL','thin_collapsed_FAIL','declared_contact_FAIL','otherowner_contact_FAIL'):
            row=self.cases[name]['sources'][0]
            self.assertFalse(row['accepted_complete_geometry'])
            self.assertFalse(self.old[name]['accepted_geometry_words_CPU_only'])
    def test_input_packet_pins_wrong_case_and_no_output_ingress(self):
        p=deepcopy(self.packets['positive'])
        p['manifest']['case_name']='negative'
        with self.assertRaises(ValueError):core.coverage('negative',p,hashlib.sha256(canon(self.packets['positive'])).hexdigest())
        with self.assertRaises(ValueError):core.coverage('negative',self.packets['positive'],hashlib.sha256(canon(self.packets['positive'])).hexdigest())
        self.assertNotIn('operations',self.packets['positive']['buffers_base64'])
    def test_profile_scope_and_declared_X_radii_not_YZ_inflation(self):
        for c in self.cases.values():
            self.assertEqual(c['profile'],'retained-exact-YZ-axial-X-only')
            for flag in ('YZ_uncertainty_implemented','event_selection_implemented','phase_evaluated','GLSL_compiled','GPU_job_admission'):
                self.assertFalse(c[flag])
        rows=lambda name:self.cases[name]['sources'][0]['triangles']
        self.assertEqual(rows('positive'),rows('declared_radius_PASS'))

if __name__=='__main__':
    trace=[]
    def instrument(name):
        original=getattr(core.limb,name)
        def call(*args):
            row={'op':name,'inputs':deepcopy(list(args)),'input_container_types':[type(a).__name__ for a in args]}
            try:out=original(*args)
            except ValueError as e:
                row.update(rejected=True,reason=str(e));trace.append(row);raise
            row.update(rejected=False,output=deepcopy(out));trace.append(row);return out
        setattr(core.limb,name,call)
    for name in ('add','sub','mul','compare','decode32_scaled'):instrument(name)
    result=unittest.TextTestRunner(stream=sys.stderr,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(YZTests))
    print(json.dumps({'PASS':result.wasSuccessful(),'tests':result.testsRun,'model':core.MODEL,
        'pins':getattr(YZTests,'pins',{}),'cases':getattr(YZTests,'cases',{}),
        'all_own_limb_calls_including_controls':trace,'GLSL_compiled':False,'GPU_executed':False,
        'accepted_complete_geometry':False},sort_keys=True,separators=(',',':'),allow_nan=False))
    raise SystemExit(0 if result.wasSuccessful() else 1)

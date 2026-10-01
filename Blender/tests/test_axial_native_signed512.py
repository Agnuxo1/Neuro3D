"""Own limb core/input X tests; no frozen geometry producer is executed."""
import base64
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import struct
import sys
import unittest
import zlib

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'benchmarks/capacity_audit'))
import axial_native_signed512_v1 as core

ROOT=Path(__file__).resolve().parents[2]
PREVIOUS='coordinacion/respuestas/AXIAL-NATIVE-SOURCE-ENCODER-001-CODEX.json'
PREVIOUS_SHA='a116d831b7ddd48b1f00046c3c705e16e378a87ef01410ba9ba25b2211386474'
LIMIT=2**511
def words(n):
    if type(n) is not int or not -LIMIT<=n<LIMIT:raise ValueError('test signed512 range')
    u=n%(2**512);return [(u>>(32*i))&0xffffffff for i in range(16)]
def integer(w):
    u=sum(v<<(32*i) for i,v in enumerate(w));return u-2**512 if w[15]&2**31 else u
def payload(r):
    t=r['test_run'];raw=zlib.decompress(base64.b64decode(t['stdout_zlib_base64']))
    assert t['rc']==0 and len(raw)==t['stdout_bytes'] and hashlib.sha256(raw).hexdigest()==t['stdout_sha256']
    return json.loads(raw)
def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()


class LimbTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        raw=(ROOT/PREVIOUS).read_bytes();assert hashlib.sha256(raw).hexdigest()==PREVIOUS_SHA
        previous=json.loads(raw);cls.pins=dict(previous['code_doc_sha256']);cls.pins[PREVIOUS]=PREVIOUS_SHA
        for p,h in cls.pins.items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h
        cls.packets=payload(json.loads((ROOT/'coordinacion/respuestas/AXIAL-NATIVE-INGRESS-001-CODEX.json').read_bytes()))['packets']
        cls.geo=payload(json.loads((ROOT/'coordinacion/respuestas/AXIAL-GEOMETRY-WORDS-001-CODEX.json').read_bytes()))['cases']
        cls.cases={n:core.x_enclosures(n,p,hashlib.sha256(canon(p)).hexdigest()) for n,p in cls.packets.items()}

    def test_carry_borrow_sign_and_multiply_controls(self):
        pairs=[(0,0),(1,-1),(-1,-1),(2**32-1,1),(2**160-1,2**96+1),
               (-2**150,2**149),(2**300,2**199),(-2**511,1),(-2**511,0),
               (2**511-1,0),(-2**510,-2),(-2**511,-1),(2**511-1,1),(2**300,2**250)]
        for a,b in pairs:
            aw,bw=words(a),words(b)
            self.assertEqual(core.compare(aw,bw),(a>b)-(a<b))
            for function,expected in ((core.add,a+b),(core.sub,a-b),(core.mul,a*b)):
                if -LIMIT<=expected<LIMIT:self.assertEqual(integer(function(aw,bw)),expected)
                else:
                    with self.assertRaises(ValueError):function(aw,bw)

    def test_shifted_products_wide_carry_and_negative_minimum(self):
        for i in (0,31,32,127,148,255,510):
            a=2**i-1;b=2**(510-i)+1
            product=a*b
            if product<LIMIT:self.assertEqual(integer(core.mul(words(a),words(b))),product)
            else:
                with self.assertRaises(ValueError):core.mul(words(a),words(b))
        self.assertEqual(core.sub(words(-LIMIT),words(-LIMIT)),words(0))
        with self.assertRaises(ValueError):core.negate(words(-LIMIT))

    def test_decode32_normal_zero_all_shift_boundaries(self):
        for exponent in (1,2,32,33,64,127,128,149,150,254):
            for sign in (0,2**31):
                word=sign|(exponent<<23)|0x123456
                expected=(0x923456<<(exponent-1))*(-1 if sign else 1)
                self.assertEqual(integer(core.decode32_scaled(word)),expected)
        self.assertEqual(core.decode32_scaled(2**31),words(0))
        self.assertEqual(core.decode_hilo([0x3f800000,0xbf800000]),words(0))
        for word in (1,0x80000001,0x7f800000,0x7fc00000,True,-1,2**32):
            with self.assertRaises(ValueError):core.decode32_scaled(word)

    def test_strict_word_shapes_alias_and_overflow(self):
        for bad in ([],[0]*15,[True]+[0]*15,[2**32]+[0]*15,tuple([0]*16)):
            with self.assertRaises(ValueError):core.add(bad,words(0))
        a=words(3);r=core.add(a,words(0));a[0]=7
        self.assertEqual(integer(r),3)
        with self.assertRaises(ValueError):core.add(words(LIMIT-1),words(1))
        with self.assertRaises(ValueError):core.sub(words(-LIMIT),words(1))

    def test_X_results_from_words_and_retained_geometry_intervals_only(self):
        compared=0
        for name,c in self.cases.items():
            self.assertFalse(c['accepted_complete_geometry'])
            self.assertFalse(c['phase_evaluated'])
            self.assertFalse(c['GPU_job_admission'])
            old={s['source_id']:s for s in self.geo[name]['sources']}
            for row in c['sources']:
                prior=old[row['source_id']]
                self.assertFalse(row['accepted_complete_geometry'])
                if prior['accepted_geometry_words_CPU_only']:
                    self.assertEqual([integer(w) for w in row['geometric_length_words']],prior['length_interval_scaled'])
                    for key,index in (('first_X_distance_words',0),('second_X_distance_words',1)):
                        self.assertEqual([integer(w) for w in row[key]],prior['segments'][index]['segment_interval_scaled'])
                    compared+=1
        # Frozen geometry has exactly eight available cases, nine source rows.
        self.assertEqual(compared,9)

    def test_boundary_positive_X_does_not_promote_geometry_FAIL(self):
        boundary=self.cases['boundary_FAIL']
        self.assertTrue(boundary['sources'][0]['X_distances_strictly_positive_CPU_only'])
        self.assertFalse(self.geo['boundary_FAIL']['accepted_geometry_words_CPU_only'])
        self.assertFalse(boundary['accepted_complete_geometry'])
        for name in ('source_contact_FAIL','thin_collapsed_FAIL','declared_contact_FAIL','otherowner_contact_FAIL'):
            row=self.cases[name]['sources'][0]
            self.assertFalse(row['initial_plane_clearance_and_competition_CPU_only'])
            self.assertFalse(row['conservative_X_plane_profile_pass_CPU_only'])
        for name in ('source_contact_FAIL','declared_contact_FAIL'):
            row=self.cases[name]['sources'][0]
            self.assertTrue(row['X_distances_strictly_positive_CPU_only'])
            lo,hi=map(integer,row['initial_other_owner_X_distance_words'])
            self.assertLessEqual(lo,0);self.assertGreaterEqual(hi,0)
        self.assertEqual(self.cases['positive']['scene_binding_sha256'],
                         self.cases['declared_radius_PASS']['scene_binding_sha256'])
        self.assertNotEqual(self.cases['positive']['word_ABI_sha256'],
                            self.cases['declared_radius_PASS']['word_ABI_sha256'])
        self.assertNotEqual(self.cases['positive']['planes'][0]['radius'],
                            self.cases['declared_radius_PASS']['planes'][0]['radius'])

    def test_packet_tamper_rehash_cannot_replace_pinned_input(self):
        old=self.packets['positive'];p=deepcopy(old)
        raw=bytearray(base64.b64decode(p['buffers_base64']['sources']));raw[0]^=1
        p['buffers_base64']['sources']=base64.b64encode(raw).decode()
        p['manifest']['buffers']['sources']['sha256']=hashlib.sha256(raw).hexdigest()
        with self.assertRaises(ValueError):core.x_enclosures('positive',p,hashlib.sha256(canon(old)).hexdigest())
        with self.assertRaises(ValueError):core.x_enclosures('negative',old,hashlib.sha256(canon(old)).hexdigest())

    def test_initial_plane_strict_clearance_contacts_and_competitors(self):
        for first,other,expected in (([1,2],[-2,-1],True),([1,2],[3,4],True),
              ([1,2],[-1,0],False),([1,2],[0,0],False),([1,2],[-1,1],False),
              ([1,2],[2,3],False),([1,3],[2,4],False),([1,2],[1,1],False),
              ([0,1],[3,4],False),([-2,-1],[3,4],False)):
            self.assertEqual(core.initial_plane_clearance(list(map(words,first)),list(map(words,other))),expected)
        with self.assertRaises(ValueError):core.initial_plane_clearance(list(map(words,[2,1])),list(map(words,[3,4])))

    def test_shader_is_only_header_not_compiled_backend_evidence(self):
        raw=(ROOT/'Blender/benchmarks/capacity_audit/axial_native_signed512_v1.glsl').read_text()
        self.assertIn('umulExtended(ua.w[i],ub.w[j],hi,lo)',raw)
        self.assertIn('shift%32u',raw);self.assertIn('offset!=0u',raw)
        self.assertNotIn('float(',raw);self.assertNotIn('uint64_t',raw)
        self.assertNotIn('void main',raw)
        self.assertEqual(raw.count('{'),raw.count('}'))
        for c in self.cases.values():self.assertFalse(c['GLSL_compiled'])


if __name__=='__main__':
    trace=[]
    def instrument(name):
        original=getattr(core,name)
        def call(*args):
            row={'op':name,'inputs':deepcopy(list(args)),
                 'input_container_types':[type(arg).__name__ for arg in args]}
            try:out=original(*args)
            except ValueError as e:
                row.update(rejected=True,reason=str(e));trace.append(row);raise
            row.update(rejected=False,output=deepcopy(out));trace.append(row);return out
        setattr(core,name,call)
    for name in ('add','sub','mul','compare','decode32_scaled'):instrument(name)
    result=unittest.TextTestRunner(stream=sys.stderr,verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(LimbTests))
    print(json.dumps({'PASS':result.wasSuccessful(),'tests':result.testsRun,'model':core.MODEL,
        'pins':getattr(LimbTests,'pins',{}),'cases':getattr(LimbTests,'cases',{}) if result.wasSuccessful() else {},
        'all_own_limb_calls_including_controls':trace,
        'GLSL_compiled':False,'GPU_executed':False,'accepted_complete_geometry':False},
        sort_keys=True,separators=(',',':'),allow_nan=False))
    raise SystemExit(0 if result.wasSuccessful() else 1)

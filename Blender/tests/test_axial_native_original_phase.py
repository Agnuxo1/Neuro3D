"""New own opt-in tests; frozen inputs/answers read only, never run old producers."""
import base64
from copy import deepcopy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import struct
import sys
import unittest
import zlib
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'benchmarks/capacity_audit'))
import axial_native_original_phase_v1 as core
ROOT=Path(__file__).resolve().parents[2]
PREVIOUS='coordinacion/respuestas/AXIAL-NATIVE-REFERENCE-001-CODEX.json'
SHA='7ecf0339e4b7dc0a3383ef8c48d32cc45dab24c9435f8a0e8bfac071c9ae3890'
LIMIT=2**511
def canon(x):return core.canon(x)
def digest(x):return hashlib.sha256(x).hexdigest()
def words(n):return [(n%2**512>>(32*i))&0xffffffff for i in range(16)]
def integer(w):
    u=sum(x<<(32*i) for i,x in enumerate(w));return u-2**512 if u>=LIMIT else u
def payload(r):
    t=r['test_run'];raw=zlib.decompress(base64.b64decode(t.get('stdout_zlib_base64') or ''.join(t['stdout_zlib_base64_chunks']),validate=True))
    assert t['rc']==0 and len(raw)==t['stdout_bytes'] and digest(raw)==t['stdout_sha256']
    return json.loads(raw)
def decode64_oracle(pair,container='list'):
    if container!='list' or len(pair)!=2 or any(type(x) is not int or not 0<=x<2**32 for x in pair):raise ValueError('type')
    lo,hi=pair;e=(hi>>20)&2047;m=((hi&0xfffff)<<32)|lo
    if e==2047 or (e==0 and m):raise ValueError('finite normal/zero')
    if e==0:return 0
    q=Fraction(2**52+m)*Fraction(2)**(e-926)
    if hi>>31:q=-q
    if q.denominator!=1 or not -LIMIT<=q<LIMIT:raise ValueError('grid/range')
    return q.numerator
def changed_buffer(o,key,mutation):
    o=deepcopy(o);raw=bytearray(base64.b64decode(o['buffers_base64'][key]));mutation(raw);raw=bytes(raw)
    o['buffers_base64'][key]=base64.b64encode(raw).decode()
    o['buffer_receipts'][key]={'bytes':len(raw),'sha256':digest(raw)};return o
def word(raw,offset,v):raw[offset:offset+4]=struct.pack('<I',v)

class OriginalPhaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        raw=(ROOT/PREVIOUS).read_bytes();assert digest(raw)==SHA
        r=json.loads(raw);cls.pins=dict(r['code_doc_sha256']);cls.pins[PREVIOUS]=SHA
        for p,h in cls.pins.items():assert digest((ROOT/p).read_bytes())==h
        cls.packets=payload(json.loads((ROOT/'coordinacion/respuestas/AXIAL-NATIVE-INGRESS-001-CODEX.json').read_bytes()))['packets']
        cls.old=payload(json.loads((ROOT/'coordinacion/respuestas/AXIAL-TERMINAL-REFERENCE-001-CODEX.json').read_bytes()))['audit']['cases']
        cls.before={n:canon(p) for n,p in cls.packets.items()}
        cls.overlays={n:core.original_cap_overlay_HOST_only(n,p,digest(canon(p))) for n,p in cls.packets.items()}
        cls.cases={n:core.audit_scene_original_phase(n,p,digest(canon(p)),cls.overlays[n],digest(canon(cls.overlays[n]))) for n,p in cls.packets.items()}
        cls.decoder_controls=[];cls.corner_controls=[];cls.reader_controls=[];cls.encoder_controls=[]
    def test_fresh_scene_original_bound_matches_frozen_independent_reference(self):
        passes=fails=stops=corners=0
        for n,c in self.cases.items():
            old={r['source_id']:r for r in self.old[n]['paths']}
            p=self.packets[n];o=json.loads(base64.b64decode(p['buffers_base64']['original_scene_json']))
            meta=json.loads(base64.b64decode(p['buffers_base64']['input_metadata_json']))
            for row in c['sources']:
                prior=old[row['source_id']]
                self.assertEqual(row['phase_bound_predicate_evaluated_CPU_only'],prior['reference_evaluated'])
                ref=row['reference']
                self.assertEqual(ref['original_phase_budget_rad'],meta['original_path_phase_caps'][row['source_id']])
                if not row['phase_bound_predicate_evaluated_CPU_only']:
                    stops+=1;self.assertFalse(row['accepted_reference_phase_bound_CPU_only'])
                    self.assertEqual(row['reason'],ref['reason']);continue
                for key in ('source_phase_reference_id','terminal_reference_id'):self.assertEqual(ref[key],prior[key])
                source=next(s for s in o['sources'] if s['id']==row['source_id'])
                original=ref['geometry']['direction_sign']*(2*Fraction(o['objects']['M']['vertices_world_BU'][0][0])-Fraction(source['position_BU'][0])-Fraction(o['objects']['D']['mode_origin_BU'][0]))
                self.assertEqual(Fraction(integer(row['original_effective_reference_length_words']),2**149),original)
                self.assertEqual(original,Fraction(*prior['original_effective_reference_length_BU']))
                self.assertEqual(Fraction(integer(row['original_lambda_words']),2**149),Fraction(o['lambda_BU']))
                cap=meta['original_path_phase_caps'][row['source_id']]
                self.assertEqual([integer(row['original_phase_cap'][k]) for k in ('numerator_words','denominator_words')],cap)
                charges=[]
                for e in ref['effective_reference_length_interval_words']:
                    for w in ref['wavelength_interval_words']:
                        charges.append(8*abs(Fraction(integer(e),integer(w))-original/Fraction(o['lambda_BU'])))
                self.assertEqual(max(charges),Fraction(*prior['phase_error_upper_rad']))
                expected=max(charges)<=Fraction(*cap)
                self.assertEqual(row['accepted_reference_phase_bound_CPU_only'],expected)
                self.assertEqual(expected,prior['accepted_terminal_reference_CPU_only'])
                for q,result in zip(charges,row['corners']):
                    self.assertEqual(result['bound_predicate_PASS'],q<=Fraction(*cap))
                    self.assertEqual(Fraction(integer(result['cycle_difference_numerator_words']),integer(result['cycle_difference_denominator_words'])),q/8)
                    corners+=1
                passes+=expected;fails+=not expected
        self.assertEqual((passes,fails,stops,corners),(7,2,5,36))
    def test_HOST_overlay_exact_bits_absence_and_unchanged_parent(self):
        available=absent=size=axes=0
        for n,p in self.packets.items():
            self.assertEqual(canon(p),self.before[n])
            o=self.overlays[n];b={k:base64.b64decode(v) for k,v in o['buffers_base64'].items()}
            self.assertEqual(set(b),{'original64_axes','original_rational_caps'})
            size+=sum(map(len,b.values()));axes+=len(b['original64_axes'])//8
            available+=o['cap_records_available'];absent+=o['cap_records_absent']
            self.assertEqual(o['HOST_reference_availability_preserved'],self.cases[n]['HOST_reference_available'])
            self.assertEqual(o['new_HOST_RN32_encodings'],0);self.assertEqual(o['new_HOST_RN64_subtractions'],0)
        self.assertEqual((available,absent,size,axes),(9,5,2376,66))
    def test_original64_domains_exact_grid_and_signed_minimum(self):
        controls=[]
        for e in (1,873,874,894,895,925,926,927,957,958,1384,1385,1386,2047):
            for sign in (0,1):
                for m in (0,1,0x80000000,0x8000000000000,0xfffffffffffff):
                    controls.append([m&0xffffffff,(sign<<31)|(e<<20)|(m>>32)])
        controls.extend(([0,0],[0,0x80000000],[1,0],[0,1],(0,0),[True,0],[-1,0],[2**32,0],[],[0]))
        for pair in controls:
            r={'inputs':list(pair),'container_type':type(pair).__name__}
            try:value=decode64_oracle(pair,type(pair).__name__)
            except ValueError:
                with self.assertRaises(ValueError) as ctx:core.decode64_scaled(pair)
                r.update(rejected=True,reason=str(ctx.exception))
            else:
                out=core.decode64_scaled(pair);self.assertEqual(integer(out),value);r.update(rejected=False,result=out)
            self.decoder_controls.append(r)
        self.assertEqual(len(self.decoder_controls),150)
        self.assertEqual(integer(core.decode64_scaled([0,(1<<31)|(1385<<20)])),-LIMIT)
    def test_corner_domains_caps_and_intermediate_overflow(self):
        for values in ((8,4,2,1,0,1),(9,4,2,1,2,1),(9,4,2,1,1,1),(-9,4,-2,1,2,1),
                       (9,4,2,1,1,10**12),(9,0,2,1,2,1),(9,4,2,0,2,1),(9,4,2,1,-1,1),(9,4,2,1,2,0),
                       (2**400,2**400,2**400,2**400,0,1),(-LIMIT,1,0,1,0,1)):
            r={'inputs_TEST_ONLY':list(values)}
            try:out=core.phase_corner_predicate(*map(words,values))
            except ValueError as e:
                r.update(rejected=True,reason=str(e))
                self.assertTrue(min(values[1],values[3],values[5])<=0 or values[4]<0 or max(map(abs,values))>=2**400)
            else:
                expected=8*abs(Fraction(values[0],values[1])-Fraction(values[2],values[3]))<=Fraction(values[4],values[5])
                self.assertEqual(out['bound_predicate_PASS'],expected);r.update(rejected=False,result=out)
            self.corner_controls.append(r)
        self.assertEqual(len(self.corner_controls),11)
    def test_reader_rehashed_malformed_input_rejected(self):
        bad=[]
        for n,label,key,mutation in (
            ('positive','present cap absent','original_rational_caps',lambda b:word(b,0,0)),
            ('boundary_FAIL','missing cap zero','original_rational_caps',lambda b:(word(b,0,1),word(b,68,1))),
            ('boundary_FAIL','absent reserved nonzero','original_rational_caps',lambda b:word(b,4,1)),
            ('positive','invalid flag','original_rational_caps',lambda b:word(b,0,2)),
            ('positive','relaxed cap','original_rational_caps',lambda b:word(b,4,1)),
            ('positive','wrong Rbits','original64_axes',lambda b:word(b,20,0)),
            ('positive','wrong stride','original64_axes',lambda b:b.extend(bytes(8)))):
            bad.append((n,label,changed_buffer(self.overlays[n],key,mutation)))
        for label,change in (
            ('foreign output',lambda o:(o['buffers_base64'].update(Lref=''),o['buffer_receipts'].update(Lref={'bytes':0,'sha256':digest(b'')}))),
            ('native promotion',lambda o:o.update(GPU_executed=True)),
            ('Boolean cap count',lambda o:o.update(cap_records_available=True)),
            ('wrong parent',lambda o:o.update(parent_input_packet_sha256='0'*64)),
            ('wrong ABI',lambda o:o.update(parent_word_ABI_sha256='0'*64))):
            o=deepcopy(self.overlays['positive']);change(o);bad.append(('positive',label,o))
        o=deepcopy(self.overlays['two_sources']);o['source_order'].reverse();bad.append(('two_sources','source order',o))
        for n,label,o in bad:
            p=self.packets[n]
            with self.assertRaises(ValueError) as ctx:core.read_original_cap_overlay_HOST_only(n,o,digest(canon(o)),p,digest(canon(p)))
            self.reader_controls.append({'case':n,'label':label,'overlay_input':o,'rejected':True,'reason':str(ctx.exception)})
        self.assertEqual(len(self.reader_controls),13)
    def test_encoder_rational_and_receipt_rejections(self):
        p=self.packets['positive']
        for cap in ([True,1],[-1,1],[0,0],[0,-1],[0,True],[2**511,1],[0,2**511]):
            bad=deepcopy(p);meta=json.loads(base64.b64decode(bad['buffers_base64']['input_metadata_json']))
            meta['original_path_phase_caps']['s']=cap;raw=canon(meta)
            bad['buffers_base64']['input_metadata_json']=base64.b64encode(raw).decode()
            bad['manifest']['buffers']['input_metadata_json']={'bytes':len(raw),'sha256':digest(raw)}
            with self.assertRaises(ValueError) as ctx:core.original_cap_overlay_HOST_only('positive',bad,digest(canon(bad)))
            self.encoder_controls.append({'cap':cap,'rejected':True,'reason':str(ctx.exception)})
        with self.assertRaises(ValueError):core.original_cap_overlay_HOST_only('negative',p,digest(canon(p)))
        with self.assertRaises(ValueError):core.original_cap_overlay_HOST_only('positive',p,'0'*64)
    def test_phase_FAILs_stops_and_no_fullpipeline_native_claim(self):
        for n in ('lambda_transport_FAIL','nonexact_geometry_phase_FAIL'):
            self.assertTrue(self.cases[n]['phase_bound_predicate_evaluated_CPU_only'])
            self.assertFalse(self.cases[n]['accepted_reference_phase_bound_CPU_only'])
        for c in self.cases.values():
            for key in ('phase_unit_evaluated','accepted_full_field_pipeline','accepted_complete_geometry','GLSL_compiled','GPU_executed','GPU_job_admission','execution_authenticated'):
                self.assertIs(c[key],False)
            for row in c['sources']:
                self.assertIs(row['phase_unit_evaluated'],False);self.assertIs(row['accepted_full_field_pipeline'],False)
                if not row['phase_bound_predicate_evaluated_CPU_only']:self.assertNotIn('corners',row)
    def test_caller_receipts_and_no_output_input_alias(self):
        p=self.packets['positive'];o=self.overlays['positive'];h=digest(canon(p))
        with self.assertRaises(ValueError):core.audit_scene_original_phase('negative',p,h,o,digest(canon(o)))
        with self.assertRaises(ValueError):core.audit_scene_original_phase('positive',p,h,o,'0'*64)
        before=canon(o)
        read=core.read_original_cap_overlay_HOST_only('positive',o,digest(canon(o)),p,h)
        read['sources'][0]['original_phase_cap']['numerator_words'][0]=9
        self.assertEqual(canon(o),before)
        w=[0,0x3ff00000];out=core.decode64_scaled(w);out[0]=99
        self.assertEqual(integer(core.decode64_scaled(w)),2**149);self.assertEqual(w,[0,0x3ff00000])

if __name__=='__main__':
    trace=[];decoded=[]
    def instrument(name):
        original=getattr(core.limb,name)
        def call(*args):
            r={'op':name,'inputs':deepcopy(list(args)),'input_container_types':[type(a).__name__ for a in args]}
            try:out=original(*args)
            except ValueError as e:r.update(rejected=True,reason=str(e));trace.append(r);raise
            r.update(rejected=False,output=deepcopy(out));trace.append(r);return out
        setattr(core.limb,name,call)
    for name in ('add','sub','mul','compare','decode32_scaled'):instrument(name)
    original_decode=core.decode64_scaled
    def decode(pair):
        r={'inputs':deepcopy(list(pair)),'container_type':type(pair).__name__}
        try:out=original_decode(pair)
        except ValueError as e:r.update(rejected=True,reason=str(e));decoded.append(r);raise
        r.update(rejected=False,result=deepcopy(out));decoded.append(r);return out
    core.decode64_scaled=decode
    result=unittest.TextTestRunner(stream=sys.stderr,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(OriginalPhaseTests))
    C=OriginalPhaseTests
    print(json.dumps({'PASS':result.wasSuccessful(),'tests':result.testsRun,'pins':getattr(C,'pins',{}),
      'cases':getattr(C,'cases',{}),'overlays':getattr(C,'overlays',{}),
      'decoder_controls':getattr(C,'decoder_controls',[]),'corner_controls':getattr(C,'corner_controls',[]),
      'reader_controls':getattr(C,'reader_controls',[]),'encoder_controls':getattr(C,'encoder_controls',[]),
      'all_own_limb_calls_including_controls':trace,'all_original64_calls_including_controls':decoded,
      'GPU_executed':False},sort_keys=True,separators=(',',':'),allow_nan=False))
    raise SystemExit(0 if result.wasSuccessful() else 1)

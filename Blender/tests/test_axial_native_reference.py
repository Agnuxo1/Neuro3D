"""Only new reference-enclosure tests. Frozen producer outputs are read, not run."""
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
import axial_native_reference_v1 as core
ROOT=Path(__file__).resolve().parents[2]
PREVIOUS='coordinacion/respuestas/AXIAL-NATIVE-EVENTS-001-CODEX.json'
SHA='6a64d0d286bf2dfbbe1669b25c022bcfba5f39163bfce80b2ebd0aa70ec390af'
L=2**511

def words(n):return [(n%(2**512)>>(32*i))&0xffffffff for i in range(16)]
def integer(w):
    n=sum(x<<(32*i) for i,x in enumerate(w));return n-2**512 if n>=L else n
def interval(v):return list(map(words,v))
def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def payload(r):
    t=r['test_run'];data=t.get('stdout_zlib_base64') or ''.join(t['stdout_zlib_base64_chunks'])
    raw=zlib.decompress(base64.b64decode(data,validate=True))
    assert t['rc']==0 and len(raw)==t['stdout_bytes'] and hashlib.sha256(raw).hexdigest()==t['stdout_sha256']
    return json.loads(raw)
def scaled(v):
    n=Fraction(*v)*2**149;assert n.denominator==1;return n.numerator
def control(m,s,d,r,sign=1):
    inputs={'M':list(m),'S':list(s),'D':list(d),'R':list(r),'sign':sign}
    try:result=core.combine_intervals(*map(interval,(m,s,d,r)),sign)
    except ValueError as e:return {'inputs':inputs,'rejected':True,'reason':str(e)}
    return {'inputs':inputs,'rejected':False,'result':result}
def replace_buffer(packet,key,value):
    p=deepcopy(packet);p['buffers_base64'][key]=base64.b64encode(value).decode()
    p['manifest']['buffers'][key]={'bytes':len(value),'sha256':hashlib.sha256(value).hexdigest()}
    return p

class ReferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        raw=(ROOT/PREVIOUS).read_bytes();assert hashlib.sha256(raw).hexdigest()==SHA
        report=json.loads(raw);cls.pins=dict(report['code_doc_sha256']);cls.pins[PREVIOUS]=SHA
        for p,h in cls.pins.items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h
        cls.packets=payload(json.loads((ROOT/'coordinacion/respuestas/AXIAL-NATIVE-INGRESS-001-CODEX.json').read_bytes()))['packets']
        cls.old=payload(json.loads((ROOT/'coordinacion/respuestas/AXIAL-TERMINAL-REFERENCE-001-CODEX.json').read_bytes()))['audit']['cases']
        cls.cases={n:core.audit_reference(n,p,hashlib.sha256(canon(p)).hexdigest()) for n,p in cls.packets.items()}
        cls.controls=[]
        cls.missing_control=None
    def test_retained_reference_intervals_and_cancelled_terminal(self):
        matches=0
        keys=['geometric_length_interval','reference_correction_interval','effective_reference_length_interval']
        for name,c in self.cases.items():
            prior={r['source_id']:r for r in self.old[name]['paths']}
            for row in c['sources']:
                old=prior[row['source_id']]
                self.assertEqual(row['reference_bounds_evaluated_CPU_only'],old['reference_evaluated'])
                if not row['reference_bounds_evaluated_CPU_only']:continue
                for k in keys:self.assertEqual(list(map(integer,row[k+'_words'])),list(map(scaled,old[k+'_BU'])))
                self.assertEqual(list(map(integer,row['independent_sum_NOT_used_words'])),list(map(scaled,old['independent_sum_NOT_used_BU'])))
                self.assertEqual(list(map(integer,row['wavelength_interval_words'])),list(map(scaled,old['enclosure_inputs']['lambda'])))
                self.assertEqual(list(map(integer,row['reference_X_interval_words'])),list(map(scaled,old['enclosure_inputs']['reference'])))
                for k in ('source_phase_reference_id','terminal_reference_id','correlated_variable_cancelled'):self.assertEqual(row[k],old[k])
                matches+=1
        self.assertEqual(matches,9)
    def test_original_mode_caps_absence_and_geometry_failure_preserved(self):
        present=absent=0
        for name,c in self.cases.items():
            raw=base64.b64decode(self.packets[name]['buffers_base64']['reference']);w=list(struct.unpack('<'+'I'*(len(raw)//4),raw))
            meta=json.loads(base64.b64decode(self.packets[name]['buffers_base64']['input_metadata_json']))
            self.assertEqual(c['original_mode_point_binary64_words'],w[1:7])
            self.assertEqual(c['original_mode_direction_binary64_words'],w[7:13])
            present+=c['HOST_reference_available'];absent+=not c['HOST_reference_available']
            for row in c['sources']:
                self.assertEqual(row['original_phase_budget_rad'],meta['original_path_phase_caps'][row['source_id']])
                if not row['geometry']['accepted_axial_two_event_geometry_CPU_only']:
                    self.assertFalse(row['reference_bounds_evaluated_CPU_only'])
                    self.assertEqual(row['reason'],row['geometry']['reason'])
                    self.assertNotIn('effective_reference_length_interval_words',row)
        self.assertEqual((present,absent),(8,5))
        # Distinct synthetic input: absent HOST ABI even with valid geometry.
        p=deepcopy(self.packets['positive']);meta=json.loads(base64.b64decode(p['buffers_base64']['input_metadata_json']))
        meta['reference']['HOST_reference_ABI']=None
        p=replace_buffer(p,'input_metadata_json',canon(meta))
        rw=list(struct.unpack('<31I',base64.b64decode(p['buffers_base64']['reference'])))
        p=replace_buffer(p,'reference',struct.pack('<13I',0,*rw[1:13]))
        p['manifest']['layout']['reference']={'HOST_encoding_available':False,'words':13}
        result=core.audit_reference('positive',p,hashlib.sha256(canon(p)).hexdigest())
        type(self).missing_control={'packet':p,'result':result,'scope':'synthetic caller packet; not frozen or authenticated native evidence'}
        self.assertFalse(result['HOST_reference_available'])
        for row in result['sources']:
            self.assertTrue(row['geometry']['accepted_axial_two_event_geometry_CPU_only'])
            self.assertFalse(row['reference_bounds_evaluated_CPU_only'])
            self.assertIn('HOST reference absent',row['reason'])
            self.assertNotIn('effective_reference_length_interval_words',row)
    def test_synthetic_reference_NOT_silently_detector_or_positive_length(self):
        for reference,expected in [((-6,-6),26),((20,20),0),((30,30),-10)]:
            c=control((10,10),(0,0),(-4,-4),reference);self.controls.append(c)
            self.assertFalse(c['rejected']);r=c['result']
            self.assertEqual(list(map(integer,r['geometric_length_interval_words'])),[24,24])
            self.assertEqual(list(map(integer,r['effective_reference_length_interval_words'])),[expected,expected])
    def test_interval_correlation_both_signs(self):
        for sign in (1,-1):
            c=control((10,11),(0,1),(-5,-3),(-7,-6),sign);self.controls.append(c)
            r=c['result']
            expected={'geometric_length_interval_words':[22,27],'reference_correction_interval_words':[1,4],
                      'effective_reference_length_interval_words':[25,29],'independent_sum_NOT_used_words':[23,31]}
            for k,values in expected.items():self.assertEqual(list(map(integer,r[k])),values if sign==1 else [-values[1],-values[0]])
    def test_bad_domains_overflow_and_typed_words_fail_closed(self):
        for args in [((L-1,L-1),(0,0),(-4,-4),(-6,-6),1),
                     ((10,9),(0,0),(-4,-4),(-6,-6),1),
                     ((10,10),(0,0),(-4,-4),(-6,-6),True)]:
            c=control(*args);self.controls.append(c);self.assertTrue(c['rejected'])
        with self.assertRaises(ValueError):core.enclosure([0,0],words(-1))
        with self.assertRaises(ValueError):core.combine_intervals(tuple(interval((1,1))),interval((0,0)),interval((-1,-1)),interval((-2,-2)),1)
    def test_mode_frame_and_wavelength_rehashed_invalid_inputs(self):
        p=self.packets['positive'];meta=json.loads(base64.b64decode(p['buffers_base64']['input_metadata_json']))
        meta['reference']['frame']='detector-rebased'
        bad=replace_buffer(p,'input_metadata_json',canon(meta))
        with self.assertRaises(ValueError):core.audit_reference('positive',bad,hashlib.sha256(canon(bad)).hexdigest())
        rw=list(struct.unpack('<31I',base64.b64decode(p['buffers_base64']['reference'])));rw[7]=1
        bad=replace_buffer(p,'reference',struct.pack('<31I',*rw))
        with self.assertRaises(ValueError):core.audit_reference('positive',bad,hashlib.sha256(canon(bad)).hexdigest())
        ww=list(struct.unpack('<18I',base64.b64decode(p['buffers_base64']['wavelength'])));ww[0]=0;ww[1]=0
        bad=replace_buffer(p,'wavelength',struct.pack('<18I',*ww))
        with self.assertRaises(ValueError):core.audit_reference('positive',bad,hashlib.sha256(canon(bad)).hexdigest())
    def test_existing_phase_FAILs_and_fullpipeline_not_promoted(self):
        for c in self.cases.values():
            for k in ('accepted_terminal_reference_CPU_only','phase_evaluated','accepted_complete_geometry','accepted_full_field_pipeline','GLSL_compiled','GPU_executed','GPU_job_admission'):self.assertFalse(c[k])
            self.assertEqual(c['new_HOST_RN32_encodings'],0);self.assertEqual(c['new_HOST_RN64_subtractions'],0)
            for r in c['sources']:
                self.assertFalse(r['accepted_terminal_reference_CPU_only']);self.assertFalse(r['phase_evaluated'])
        for name in ('lambda_transport_FAIL','nonexact_geometry_phase_FAIL'):
            self.assertTrue(self.cases[name]['reference_bounds_evaluated_CPU_only'])
            self.assertTrue(all(not r['accepted_terminal_reference_CPU_only'] for r in self.old[name]['paths']))
    def test_receipt_case_mismatch_and_result_alias(self):
        p=deepcopy(self.packets['positive']);h=hashlib.sha256(canon(p)).hexdigest()
        with self.assertRaises(ValueError):core.audit_reference('negative',p,h)
        p['manifest']['case_name']='negative'
        with self.assertRaises(ValueError):core.audit_reference('positive',p,h)
        m=interval((10,10));result=core.combine_intervals(m,interval((0,0)),interval((-4,-4)),interval((-6,-6)),1)
        m[0][0]=99;self.assertEqual(integer(result['effective_reference_length_interval_words'][0]),26)

if __name__=='__main__':
    trace=[]
    def instrument(name):
        original=getattr(core.limb,name)
        def call(*args):
            r={'op':name,'inputs':deepcopy(list(args)),'input_container_types':[type(a).__name__ for a in args]}
            try:out=original(*args)
            except ValueError as e:r.update(rejected=True,reason=str(e));trace.append(r);raise
            r.update(rejected=False,output=deepcopy(out));trace.append(r);return out
        setattr(core.limb,name,call)
    for name in ('add','sub','mul','compare','decode32_scaled'):instrument(name)
    result=unittest.TextTestRunner(stream=sys.stderr,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ReferenceTests))
    print(json.dumps({'PASS':result.wasSuccessful(),'tests':result.testsRun,'model':core.MODEL,
        'pins':getattr(ReferenceTests,'pins',{}),'cases':getattr(ReferenceTests,'cases',{}),
        'synthetic_controls':getattr(ReferenceTests,'controls',[]),
        'synthetic_missing_HOST_reference_control':getattr(ReferenceTests,'missing_control',None),
        'all_own_limb_calls_including_controls':trace,'GPU_executed':False},sort_keys=True,separators=(',',':'),allow_nan=False))
    raise SystemExit(0 if result.wasSuccessful() else 1)

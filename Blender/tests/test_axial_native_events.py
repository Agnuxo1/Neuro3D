"""New event-selector tests only; retained old producer outputs are read, not executed."""
import base64
from copy import deepcopy
import hashlib
import inspect
import json
from pathlib import Path
import sys
import unittest
import zlib
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'benchmarks/capacity_audit'))
import axial_native_events_v1 as core
ROOT=Path(__file__).resolve().parents[2]
PREVIOUS='coordinacion/respuestas/AXIAL-NATIVE-YZ-001-CODEX.json'
SHA='2cbc2eb4d291de3876434f06daaa9da7aa189874c8a083913cee8796fe08331f'
L=2**511
def words(n):
    if type(n) is not int or not -L<=n<L:raise ValueError('oracle range')
    return [(n%(2**512)>>(32*i))&0xffffffff for i in range(16)]
def integer(w):
    u=sum(x<<(32*i) for i,x in enumerate(w));return u-2**512 if u>=L else u
def plane(lo,hi=None):return {'lo':words(lo),'hi':words(lo if hi is None else hi)}
def payload(report):
    t=report['test_run'];raw=zlib.decompress(base64.b64decode(t['stdout_zlib_base64']))
    assert t['rc']==0 and len(raw)==t['stdout_bytes'] and hashlib.sha256(raw).hexdigest()==t['stdout_sha256']
    return json.loads(raw)
def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def control(m,d,*,s=(0,0),sign=1,interior=None):
    members=[[0,0],[1,1]] if interior is None else interior
    result=core._source_trace('control',members,{0:plane(*m),1:plane(*d)},
                             list(map(words,s)),sign,'synthetic-control-NOT-native')
    result['synthetic_control_inputs']={'M':list(m),'D':list(d),'source':list(s),
                                      'sign':sign,'interior':deepcopy(members)}
    return result
class EventTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        raw=(ROOT/PREVIOUS).read_bytes();assert hashlib.sha256(raw).hexdigest()==SHA
        previous=json.loads(raw);cls.pins=dict(previous['code_doc_sha256']);cls.pins[PREVIOUS]=SHA
        for p,h in cls.pins.items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h
        cls.packets=payload(json.loads((ROOT/'coordinacion/respuestas/AXIAL-NATIVE-INGRESS-001-CODEX.json').read_bytes()))['packets']
        cls.old=payload(json.loads((ROOT/'coordinacion/respuestas/AXIAL-GEOMETRY-WORDS-001-CODEX.json').read_bytes()))['cases']
        cls.cases={n:core.trace_scene(n,p,hashlib.sha256(canon(p)).hexdigest()) for n,p in cls.packets.items()}
        cls.controls=[]
    def test_retained_geometry_flags_primitives_roots_clearance_and_lengths(self):
        matched=failed=0
        for name,case in self.cases.items():
            prior=self.old[name]
            self.assertEqual(case['accepted_axial_two_event_geometry_CPU_only'],prior['accepted_geometry_words_CPU_only'])
            old={r['source_id']:r for r in prior['sources']}
            for row in case['sources']:
                prev=old[row['source_id']]
                self.assertEqual(row['accepted_axial_two_event_geometry_CPU_only'],prev['accepted_geometry_words_CPU_only'])
                if not row['accepted_axial_two_event_geometry_CPU_only']:
                    self.assertEqual(row['reason'],prev['reason']);failed+=1;continue
                self.assertEqual(list(map(integer,row['length_interval_words'])),prev['length_interval_scaled'])
                self.assertEqual(row['projected_misses'],prev['projected_misses'])
                for now,oldseg in zip(row['segments'],prev['segments']):
                    for key in ('primitive_id','owner','same_owner_departures_skipped','behind'):self.assertEqual(now[key],oldseg[key])
                    self.assertEqual(list(map(integer,now['segment_interval_words'])),oldseg['segment_interval_scaled'])
                    clearance=now['competitor_clearance_words']
                    self.assertEqual(integer(clearance) if clearance is not None else None,oldseg['competitor_clearance_scaled'])
                matched+=1
        self.assertEqual((matched,failed),(9,5))
    def test_same_owner_departure_generated_from_accepted_shared_plane(self):
        for case in self.cases.values():
            for row in case['sources']:
                if not row['accepted_axial_two_event_geometry_CPU_only']:continue
                certificate=row['departure_certificate'];first,second=row['segments']
                self.assertEqual(certificate['source_id'],row['source_id'])
                self.assertEqual(certificate['input_packet_sha256'],case['input_packet_sha256'])
                self.assertEqual(certificate['owner'],first['owner'])
                self.assertEqual(certificate['primitive_id'],first['primitive_id'])
                self.assertIn(first['primitive_id'],second['same_owner_departures_skipped'])
                self.assertEqual(first['same_owner_departures_skipped'],[])
                self.assertNotIn(second['primitive_id'],second['same_owner_departures_skipped'])
    def test_public_API_cannot_request_previous_owner(self):
        self.assertEqual(list(inspect.signature(core.trace_scene).parameters),['name','packet','expected_packet_sha256'])
        p=self.packets['positive']
        with self.assertRaises(TypeError):core.trace_scene('positive',p,hashlib.sha256(canon(p)).hexdigest(),previous_owner=0)
        self.assertNotIn('previous_owner',inspect.signature(core._source_trace).parameters)
    def test_synthetic_controls_contacts_order_overlap_ties_and_no_roots(self):
        cases=[((10,),(-4,),(0,0),1,None,True,None),
               ((-10,),(4,),(0,0),-1,None,True,None),
               ((10,),(-4,),(10,10),1,None,False,'source zero contact'),
               ((10,),(0,),(0,0),1,None,False,'source zero contact'),
               ((10,),(4,),(0,0),1,None,False,'first event must be mirror'),
               ((9,11),(10,12),(0,0),1,None,False,'competitor intervals overlap/touch'),
               ((10,),(10,),(0,0),1,None,False,'competitor intervals overlap/touch'),
               ((10,),(-4,),(0,0),1,[],False,'no strictly positive root'),
               ((10,),(-4,),(0,0),1,[[0,0]],False,'no strictly positive root'),
               ((10,),(-4,),(0,0),1,[[0,0],[2,0],[1,1]],False,'competitor intervals overlap/touch')]
        for m,d,s,sign,interior,accepted,reason in cases:
            row=control(m,d,s=s,sign=sign,interior=interior);self.controls.append(row)
            self.assertEqual(row['accepted_axial_two_event_geometry_CPU_only'],accepted)
            if reason:self.assertEqual(row['reason'],reason)
            if accepted:self.assertEqual(list(map(integer,row['length_interval_words'])),[24,24])
    def test_interval_correlation_NOT_independent_sum_of_segments(self):
        row=control((2,3),(-4,-3),s=(0,1));self.controls.append(row)
        self.assertTrue(row['accepted_axial_two_event_geometry_CPU_only'])
        self.assertEqual(list(map(integer,row['length_interval_words'])),[6,10])
        self.assertEqual([list(map(integer,s['segment_interval_words'])) for s in row['segments']],[[1,3],[5,7]])
    def test_overflow_bad_domains_and_receipt_alias_fail_closed(self):
        row=control((L-1,),(-4,),s=(-2,-2));self.controls.append(row)
        self.assertFalse(row['accepted_axial_two_event_geometry_CPU_only']);self.assertIn('overflow',row['reason'])
        row=control((10,),(-4,),sign=True);self.controls.append(row)
        self.assertFalse(row['accepted_axial_two_event_geometry_CPU_only'])
        row=control((10,),(-4,),interior=[[True,0]]);self.controls.append(row)
        self.assertFalse(row['accepted_axial_two_event_geometry_CPU_only'])
        planes={0:plane(10),1:plane(-4)}
        row=core._source_trace('c',[[0,0],[1,1]],planes,[words(0),words(0)],1,'control')
        planes[0]['lo'][0]=99
        self.assertEqual(integer(row['departure_certificate']['shared_plane_interval_words'][0]),10)
    def test_existing_FAILs_phase_caps_and_profile_not_promoted(self):
        for name in ('boundary_FAIL','source_contact_FAIL','thin_collapsed_FAIL','declared_contact_FAIL','otherowner_contact_FAIL'):
            self.assertFalse(self.cases[name]['accepted_axial_two_event_geometry_CPU_only'])
        self.assertTrue(self.cases['thin_resolved']['accepted_axial_two_event_geometry_CPU_only'])
        for c in self.cases.values():
            for key in ('accepted_complete_geometry','accepted_full_field_pipeline','phase_evaluated','GLSL_compiled','GPU_executed','GPU_job_admission'):self.assertFalse(c[key])
            self.assertTrue(c['reference_length_not_geometric_length'])
        for name in ('lambda_transport_FAIL','nonexact_geometry_phase_FAIL'):
            self.assertTrue(self.cases[name]['accepted_axial_two_event_geometry_CPU_only'])
            self.assertFalse(self.old[name]['accepted_phase_budget_CPU_only'])
    def test_packet_wrong_case_tamper_and_output_not_supplied(self):
        p=deepcopy(self.packets['positive']);p['manifest']['case_name']='negative'
        with self.assertRaises(ValueError):core.trace_scene('negative',p,hashlib.sha256(canon(self.packets['positive'])).hexdigest())
        with self.assertRaises(ValueError):core.trace_scene('negative',self.packets['positive'],hashlib.sha256(canon(self.packets['positive'])).hexdigest())
        self.assertNotIn('segments',p['buffers_base64'])
if __name__=='__main__':
    trace=[]
    def instrument(name):
        original=getattr(core.limb,name)
        def call(*args):
            row={'op':name,'inputs':deepcopy(list(args)),'input_container_types':[type(a).__name__ for a in args]}
            try:out=original(*args)
            except ValueError as e:row.update(rejected=True,reason=str(e));trace.append(row);raise
            row.update(rejected=False,output=deepcopy(out));trace.append(row);return out
        setattr(core.limb,name,call)
    for name in ('add','sub','mul','compare','decode32_scaled'):instrument(name)
    result=unittest.TextTestRunner(stream=sys.stderr,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(EventTests))
    print(json.dumps({'PASS':result.wasSuccessful(),'tests':result.testsRun,'model':core.MODEL,
        'pins':getattr(EventTests,'pins',{}),'cases':getattr(EventTests,'cases',{}),'synthetic_controls':getattr(EventTests,'controls',[]),
        'all_own_limb_calls_including_controls':trace,'GPU_executed':False,'accepted_complete_geometry':False},
        sort_keys=True,separators=(',',':'),allow_nan=False))
    raise SystemExit(0 if result.wasSuccessful() else 1)

"""Presence STOP controls only. Immutable own core/frozen producers are never changed/run."""
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
import axial_native_original_phase_v1 as core
ROOT=Path(__file__).resolve().parents[2]
PREVIOUS='coordinacion/respuestas/AXIAL-NATIVE-ORIGINAL-PHASE-001-CODEX.json'
SHA='64ce050f2c79748cac922601a4898888b769676fca3a99e75b475c7e20e70b74'
def canon(x):return core.canon(x)
def digest(x):return hashlib.sha256(x).hexdigest()
def payload(r):
    t=r['test_run'];raw=zlib.decompress(base64.b64decode(t.get('stdout_zlib_base64') or ''.join(t['stdout_zlib_base64_chunks']),validate=True))
    assert t['rc']==0 and len(raw)==t['stdout_bytes'] and digest(raw)==t['stdout_sha256']
    return json.loads(raw)
def replace_buffer(p,key,raw):
    p['buffers_base64'][key]=base64.b64encode(raw).decode()
    p['manifest']['buffers'][key]={'bytes':len(raw),'sha256':digest(raw)}
def synthetic(parent,missing_cap,missing_ref):
    p=deepcopy(parent);meta=json.loads(base64.b64decode(p['buffers_base64']['input_metadata_json']))
    if missing_cap:meta['original_path_phase_caps']['s']=None
    if missing_ref:
        meta['reference']['HOST_reference_ABI']=None
        w=list(struct.unpack('<31I',base64.b64decode(p['buffers_base64']['reference'])))
        replace_buffer(p,'reference',struct.pack('<13I',0,*w[1:13]))
        p['manifest']['layout']['reference']={'HOST_encoding_available':False,'words':13}
    replace_buffer(p,'input_metadata_json',canon(meta))
    return p
class PresenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        raw=(ROOT/PREVIOUS).read_bytes();assert digest(raw)==SHA
        r=json.loads(raw);cls.pins=dict(r['code_doc_sha256']);cls.pins[PREVIOUS]=SHA
        for p,h in cls.pins.items():assert digest((ROOT/p).read_bytes())==h,p
        cls.frozen=payload(r)['cases']
        cls.originals=payload(json.loads((ROOT/'coordinacion/respuestas/AXIAL-NATIVE-INGRESS-001-CODEX.json').read_bytes()))['packets']
        cls.prior_bytes={n:canon(p) for n,p in cls.originals.items()}
        cls.controls={}
        for label,name,cap,ref in (
            ('missing_cap_one','positive',True,False),
            ('missing_cap_two_sources','two_sources',True,False),
            ('missing_HOST_reference','positive',False,True),
            ('missing_both','positive',True,True)):
            p=synthetic(cls.originals[name],cap,ref);before=canon(p);h=digest(before)
            o=core.original_cap_overlay_HOST_only(name,p,h)
            result=core.audit_scene_original_phase(name,p,h,o,digest(canon(o)))
            assert before==canon(p),'no input mutation'
            cls.controls[label]={'case_name':name,'missing_cap_s':cap,'missing_HOST_reference':ref,
                                 'scope':'synthetic caller INPUT only; not frozen, authenticated, native, physical or GPU evidence',
                                 'parent':p,'overlay':o,'result':result}
    def test_missing_cap_NOT_numerical_zero_despite_valid_reference(self):
        c=self.controls['missing_cap_one'];row=c['result']['sources'][0]
        self.assertTrue(row['reference']['geometry']['accepted_axial_two_event_geometry_CPU_only'])
        self.assertTrue(row['reference']['reference_bounds_evaluated_CPU_only'])
        self.assertFalse(row['phase_bound_predicate_evaluated_CPU_only'])
        self.assertFalse(row['accepted_reference_phase_bound_CPU_only'])
        self.assertEqual(row['reason'],'original phase cap absent; no numerical zero default')
        self.assertIsNone(c['result']['HOST_original_inputs']['sources'][0]['original_phase_cap'])
        self.assertNotIn('corners',row);self.assertNotIn('original_effective_reference_length_words',row)
        # RETAINED baseline read only: explicit numerical cap0 passes, absence must not borrow it.
        old=self.frozen['positive']['sources'][0]
        self.assertEqual(old['reference']['original_phase_budget_rad'],[0,1])
        self.assertTrue(old['accepted_reference_phase_bound_CPU_only'])
    def test_missing_cap_does_not_silently_cancel_or_replace_other_source(self):
        c=self.controls['missing_cap_two_sources'];rows={r['source_id']:r for r in c['result']['sources']}
        self.assertFalse(rows['s']['phase_bound_predicate_evaluated_CPU_only'])
        self.assertTrue(rows['other']['phase_bound_predicate_evaluated_CPU_only'])
        self.assertTrue(rows['other']['accepted_reference_phase_bound_CPU_only'])
        self.assertEqual(rows['other']['reference']['original_phase_budget_rad'],[0,1])
        self.assertEqual(rows['other']['corners'],self.frozen['two_sources']['sources'][1]['corners'])
        self.assertFalse(c['result']['accepted_reference_phase_bound_CPU_only'])
        self.assertNotEqual(rows['s']['reference']['source_phase_reference_id'],rows['other']['reference']['source_phase_reference_id'])
    def test_missing_HOST_reference_not_revived_by_overlay_original_R(self):
        for label in ('missing_HOST_reference','missing_both'):
            c=self.controls[label];out=c['result'];row=out['sources'][0]
            self.assertFalse(out['HOST_reference_available'])
            self.assertTrue(row['reference']['geometry']['accepted_axial_two_event_geometry_CPU_only'])
            self.assertFalse(row['reference']['reference_bounds_evaluated_CPU_only'])
            self.assertFalse(row['phase_bound_predicate_evaluated_CPU_only'])
            self.assertFalse(row['accepted_reference_phase_bound_CPU_only'])
            self.assertEqual(row['reason'],'HOST reference absent; no new encoder or default reference')
            self.assertNotIn('corners',row);self.assertNotIn('effective_reference_length_interval_words',row['reference'])
            self.assertEqual(out['HOST_original_inputs']['original_R_X_words'],
                             self.frozen['positive']['HOST_original_inputs']['original_R_X_words'])
            self.assertFalse(c['overlay']['HOST_reference_availability_preserved'])
            self.assertEqual(c['overlay']['new_HOST_RN32_encodings'],0)
    def test_only_declared_synthetic_deltas_and_frozen_inputs_unchanged(self):
        for n,p in self.originals.items():self.assertEqual(canon(p),self.prior_bytes[n])
        for c in self.controls.values():
            p=c['parent'];prior=self.originals[c['case_name']]
            for k,v in p['buffers_base64'].items():
                if k not in ('input_metadata_json','reference'):self.assertEqual(v,prior['buffers_base64'][k])
            self.assertEqual(p['manifest']['layout']['sources'],prior['manifest']['layout']['sources'])
            meta=json.loads(base64.b64decode(p['buffers_base64']['input_metadata_json']))
            old=json.loads(base64.b64decode(prior['buffers_base64']['input_metadata_json']))
            expected=deepcopy(old)
            if c['missing_cap_s']:expected['original_path_phase_caps']['s']=None
            if c['missing_HOST_reference']:expected['reference']['HOST_reference_ABI']=None
            self.assertEqual(meta,expected)
            if not c['missing_HOST_reference']:self.assertEqual(p['buffers_base64']['reference'],prior['buffers_base64']['reference'])
    def test_NO_fullpipeline_native_execution_or_job_admission(self):
        for c in self.controls.values():
            out=c['result']
            for key in ('phase_unit_evaluated','accepted_full_field_pipeline','accepted_complete_geometry',
                        'GLSL_compiled','GPU_executed','GPU_job_admission','execution_authenticated'):self.assertIs(out[key],False)
            for row in out['sources']:
                self.assertIs(row['phase_unit_evaluated'],False);self.assertIs(row['accepted_full_field_pipeline'],False)
        self.assertEqual(len(corner_calls),4)
        self.assertEqual(sum(len(c['result']['sources']) for c in self.controls.values()),5)

corner_calls=[]
if __name__=='__main__':
    original=core.phase_corner_predicate
    def corner(*args):
        result=original(*args)
        corner_calls.append({'inputs':deepcopy(list(args)),'result':deepcopy(result)})
        return result
    core.phase_corner_predicate=corner
    r=unittest.TextTestRunner(stream=sys.stderr,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(PresenceTests))
    print(json.dumps({'PASS':r.wasSuccessful(),'tests':r.testsRun,'pins':getattr(PresenceTests,'pins',{}),
      'synthetic_controls':getattr(PresenceTests,'controls',{}),'corner_calls':corner_calls,
      'fresh_own_dependency_recomputation':'4 changed synthetic inputs only, no old suites or unchanged sweep',
      'GPU_executed':False},sort_keys=True,separators=(',',':'),allow_nan=False))
    raise SystemExit(0 if r.wasSuccessful() else 1)

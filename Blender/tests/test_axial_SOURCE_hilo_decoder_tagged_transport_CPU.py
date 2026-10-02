"""New transport tests only; no old suite or encoder is executed."""
import importlib.util
import json
import sys
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('own_tagged_transport',ROOT/'Blender/benchmarks/capacity_audit/axial_SOURCE_hilo_decoder_tagged_transport_CPU_v1.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
DATA={}
class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Verify immutable disk evidence ONCE for this bounded unit-test process.
        # Only the test loader is patched; production load_retained stays fail-closed.
        cls.sealed_fixture=m.load_retained()
        cls.fixture_loader=patch.object(m,'load_retained',return_value=cls.sealed_fixture)
        cls.fixture_loader.start()
    @classmethod
    def tearDownClass(cls):
        cls.fixture_loader.stop()
    def test_1_explicit_program_and_frame_roundtrip(self):
        req=m.make_synthetic_request();out=m.audit_transport_CPU(req,model=m.MODEL);old,_,_=m.load_retained()
        self.assertEqual((out['payload_bytes'],out['header_bytes'],out['wire_bytes']),(64,416,480))
        self.assertEqual((out['native_RN64_adds'],out['zero_selections']),(4,4))
        for row,prior in zip(out['sources'],old['audit']['sources']):
            self.assertEqual(row['decoded_SOURCE_uint64'],[s['decoded_uint64'] for s in prior['scalars']])
            self.assertEqual(row['payload_sha256'],prior['hilo_le_sha256'])
        self.assertTrue(all(v is False for v in out['proof_scope'].values()))
        self.assertFalse(out['frozen_GRID_program_changed'])
        DATA.update(request=req,audit=out)
    def test_2_missing_and_optin(self):
        with patch.object(m.decoder,'decode_scalar') as mock:
            missing=m.audit_transport_CPU(None,model=m.MODEL)
            self.assertEqual(mock.call_count,0)
        self.assertEqual((missing['missing_cases'],missing['missing_sources']),(17,19));DATA['missing']=missing
        rejected=[]
        for model in (True,None,m.decoder.MODEL,'legacy raw decoder'):
            with self.assertRaises(ValueError):m.audit_transport_CPU(None,model=model)
            rejected.append(str(model))
        DATA['model_rejections']=rejected
    def test_3_all_late_frames_before_any_decode(self):
        req=m.make_synthetic_request();stops=[]
        def reject(label,edit):
            q=deepcopy(req);edit(q)
            with patch.object(m.decoder,'decode_scalar') as mock:
                with self.assertRaises(ValueError):m.audit_transport_CPU(q,model=m.MODEL)
                self.assertEqual(mock.call_count,0)
            stops.append(label)
        def wire(q,edit):
            f=q['frames'][-1];b=bytearray(m.canonical_base64(f['frame_base64']));edit(b)
            f['frame_base64']=m.base64.b64encode(b).decode()
        for name,index in (('magic',0),('implementation',8),('context',40),('SOURCE ledger',72),('payload',104)):
            reject('late '+name,lambda q,i=index:wire(q,lambda b:b.__setitem__(i,b[i]^1)))
        reject('late truncate',lambda q:wire(q,lambda b:b.pop()))
        reject('late extra byte',lambda q:wire(q,lambda b:b.append(0)))
        reject('legacy raw16',lambda q:wire(q,lambda b:b.__delitem__(slice(0,104))))
        reject('noncanonical base64',lambda q:q['frames'][-1].update(frame_base64=q['frames'][-1]['frame_base64']+'\n'))
        reject('base64 bool',lambda q:q['frames'][-1].update(frame_base64=True))
        reject('late source alias',lambda q:q['frames'][-1].update(source_id='alias'))
        reject('late record extra',lambda q:q['frames'][-1].update(admitted=True))
        reject('frame reorder',lambda q:q['frames'].reverse())
        reject('omitted frame',lambda q:q['frames'].pop())
        reject('wrong selector model',lambda q:q['program_INPUT']['decoder_selection'].update(model='legacy-RN-add'))
        reject('wrong selector code SHA',lambda q:q['program_INPUT']['decoder_selection'].update(implementation_sha256='0'*64))
        reject('wrong selector receipt',lambda q:q['program_INPUT']['decoder_selection'].update(parent_receipt_sha256='0'*64))
        reject('wrong selector layout',lambda q:q['program_INPUT']['decoder_selection'].update(payload_layout='highimag-first'))
        reject('selector absent',lambda q:q['program_INPUT'].pop('decoder_selection'))
        reject('PROGRAM INPUT bool digest',lambda q:q['program_INPUT'].update(decoder_INPUT_sha256=True))
        reject('last scene ORIGINAL',lambda q:q['decoder_INPUT']['SOURCE_limb_records'][-1]['scalars'][-1].update(original_uint64=1<<63))
        reject('extra request authority',lambda q:q.update(admitted=True))
        DATA['atomic_rejections']=stops
    def test_4_signed_zero_transport_not_legacy_autodetect(self):
        old,_,_=m.load_retained();nz=old['retained_negative_zero']['old']
        self.assertFalse(nz['ORIGINAL_zero_sign_preserved'])
        raw=bytes.fromhex(nz['hilo_le_hex'])+bytes(8);ctx='1'*64;source='2'*64
        frame=m.frame_SOURCE(raw,ctx,source);words=m.inspect_FRAME(frame,ctx,source)
        with patch.object(m.decoder,'native_add64',side_effect=AssertionError('zero transport must not sum')):
            decoded=[m.decoder.decode_scalar(*words[i:i+2]) for i in (0,2)]
        self.assertEqual(decoded[0]['decoded_uint64'],1<<63)
        self.assertEqual(frame[104:],raw)
        with self.assertRaises(ValueError):m.inspect_FRAME(raw,ctx,source)
        with self.assertRaises(ValueError):m.inspect_FRAME(frame,source,ctx)
        DATA['isolated_zero_frame']={'frame_base64':m.base64.b64encode(frame).decode(),'context_sha256':ctx,
                                     'source_row_sha256':source,'payload_sha256':m.sha(raw),'decoded_scalars':decoded,
                                     'old_scalar_sha256':m.digest(nz),'fixture':'isolated transport CONTROL; NOT scene INPUT',
                                     'old_failure_preserved':True,'scene_authenticated':False}
        bad=[]
        for payload,context,row in ((bytes(15),ctx,source),(bytes(17),ctx,source),
                                     ((1).to_bytes(4,'little')+bytes(12),ctx,source),
                                     (raw,True,source),(raw,'A'*64,source),(raw,ctx,'0'*63)):
            with self.assertRaises(ValueError):m.frame_SOURCE(payload,context,row)
            bad.append('length/selected-word/SHA reject')
        DATA['frame_construction_rejections']=bad
if __name__=='__main__':
    result=unittest.TextTestRunner(stream=sys.stderr,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
    print(json.dumps({'tests_run':result.testsRun,'errors':len(result.errors),'failures':len(result.failures),'data':DATA},sort_keys=True,allow_nan=False))
    sys.exit(not result.wasSuccessful())

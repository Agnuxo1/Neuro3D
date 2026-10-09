"""Read-only artifact/source audit. Never import or execute Claude backends."""
import base64
import hashlib
import json
from pathlib import Path
import unittest
import zlib

ROOT = Path(__file__).resolve().parents[2]
BASE = Path('D:/PROJECTS/.cognition/neuro3d/p0_scene_gpu')
RESPONSE = ROOT/'coordinacion/respuestas/P0-3-SCENE-STATES-CUDA-CLAUDE.json'
BACKEND = Path('D:/PROJECTS/.cognition/neuro3d/nebulatrace/gpu_states_v2.py')
RESPONSE_SHA = 'b31215b524528b0acb3a6d40614733c0137e751208cd2a59fdc4d98c8f171ac3'
BACKEND_SHA = '506b13c9c6bb442d16d9be07b8508a79b01ded9dd4c87c261ac1af83849b426e'
LITERAL = ROOT/'coordinacion/respuestas/PRECISION-OBLIQUE-COMMON-DETECTOR-LENGTH-CPU-001-CODEX.json'
LITERAL_SHA = '139cb34a315f476fa026bb346086a3a59d7c22241932ca3f4c291a501f4ca47e'
RECORDS = []


def pinned(path, expected):
    b = path.read_bytes()
    if len(b)>1048576 or hashlib.sha256(b).hexdigest()!=expected:
        raise ValueError('pinned read-only artifact mismatch: '+str(path))
    return b


class ExistingBackendTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.response = json.loads(pinned(RESPONSE, RESPONSE_SHA))
        cls.blobs = {name:pinned(BASE/name,sha)
                     for name,sha in cls.response['artifact_sha256'].items()}
        cls.result = json.loads(cls.blobs['p03_cuda_result.json'])
        cls.manifest = json.loads(cls.blobs['p03_manifest.json'])
        cls.backend = pinned(BACKEND, BACKEND_SHA).decode()
        cls.harness = cls.blobs['p03_harness_v4.py'].decode()

    def test_existing_content_chain(self):
        result, manifest = self.result, self.manifest
        self.assertEqual(result['code_sha256'][BACKEND.as_posix()], BACKEND_SHA)
        self.assertEqual(result['device'], 'cuda')
        self.assertEqual(result['errors'], [])
        verdict = json.loads(self.blobs['p03_cuda_checker_verdict.json'])
        self.assertEqual(verdict['result_sha256'],hashlib.sha256(self.blobs['p03_cuda_result.json']).hexdigest())
        self.assertEqual(verdict['manifest_sha256'],hashlib.sha256(self.blobs['p03_manifest.json']).hexdigest())
        self.assertEqual(verdict['verdict'],'PASS')
        self.assertEqual(verdict['failures'],[])
        self.assertEqual(verdict['warnings'],[])
        self.assertEqual(manifest['scene_count'],104)
        self.assertEqual(len(result['scene_results']),104)
        for i,(scene,row) in enumerate(zip(manifest['scenes'],result['scene_results'],strict=True)):
            self.assertEqual(row['index'],i)
            self.assertEqual(row['scene_sha256'],hashlib.sha256(json.dumps(scene,sort_keys=True).encode()).hexdigest())
            self.assertTrue(row['measured'])
        envelope = json.loads(self.blobs['p03_cuda_envelope.json'])
        self.assertEqual(envelope['status'],'OK')
        self.assertEqual(envelope['exit'],0)
        self.assertTrue(envelope['child_terminated_verified'])
        self.assertEqual(envelope['policy']['ram_free_after_budget_min_gib'],1.5)
        RECORDS.append(dict(kind='EXISTING_ARCHIVE_CONTENT_CHAIN',
            artifact_pins=len(self.blobs),scene_bindings=104,
            historical_device_label=result['device'],historical_checker_verdict=verdict['verdict'],
            historical_deadline_utc=envelope['deadline_utc'],current_job_admission=False,
            historical_override_NOT_current_authority=True,execution_authentication=False))

    def test_source_stage_placement(self):
        anchors = {
            'HOST_SOURCE_DIRECTION_NORMALIZATION': 'srcd[s, j] = d / np.linalg.norm(d)',
            'HOST_TRIANGLE_EDGE_SUBTRACTION': 'E1.append(V[f[1]] - V[f[0]])',
            'HOST_WAVENUMBER_THEN_DEVICE_UPLOAD': 'self.k = torch.as_tensor([2 * math.pi / l for l in lams]',
            'DEVICE_NEAREST_PARAMETER_PLUS_BIAS': 'best + BIAS, oj[:, 0], nj, lost, other.any(1)',
            'DEVICE_SEGMENT_PHASE': 'ph = torch.polar(torch.ones_like(t), kk_scene[sc] * t)',
            'DEVICE_TERMINAL_PHASE': 'kk_scene[sc[ti]] * (t[ti] + off)',
            'DEVICE_SOURCE_CHANNELS': '"U": U.reshape(S, P, NS)',
        }
        for stage,anchor in anchors.items():
            self.assertEqual(self.backend.count(anchor),1)
            RECORDS.append(dict(kind='SOURCE_STAGE',stage=stage,
                backend_sha256=BACKEND_SHA,line=self.backend[:self.backend.index(anchor)].count('\n')+1,
                anchor=anchor,compiled_graph_verified=False))
        for anchor in ('import gpu_states_v2 as gs','U = r[\'U\'].cpu().numpy()',
                       'f = complex(U[i, pi] @ amp)'):
            self.assertIn(anchor,self.harness)
        RECORDS.append(dict(kind='HOST_SOURCE_FIELD_COMPOSITION_AFTER_U_READBACK',
            source='p03_harness_v4.py',native_full_field_multiply=False))

    def test_no_original_oblique_query_binding(self):
        lit = json.loads(pinned(LITERAL,LITERAL_SHA))
        cap = lit['test_run']
        raw = zlib.decompress(base64.b64decode(cap['stdout_zlib_base64']))
        self.assertEqual(hashlib.sha256(raw).hexdigest(),cap['stdout_sha256'])
        inputs = json.loads(raw)['data']['inputs']
        declared = {row['scene_sha256'] for row in self.result['scene_results']}
        for case in ('oblique','direction_scaled','shared_ref1000','tiny_gap_2m60'):
            item = inputs[case]
            sha = item['request']['original_scene_sha256']
            self.assertNotIn(sha,declared)
            self.assertNotEqual(item['scene']['schema'],self.manifest['scenes'][0]['schema'])
            RECORDS.append(dict(kind='NO_EXACT_DECLARED_OBLIQUE_BINDING',case=case,
                literal_scene_sha256=sha,exact_scene_digest_match=False,
                query_binding=False,semantic_geometry_equivalence='NOT_CHECKED_NOT_IMPLIED'))


if __name__=='__main__':
    result = unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromTestCase(ExistingBackendTests))
    print(json.dumps(dict(status='PASS' if result.wasSuccessful() else 'FAIL',tests=result.testsRun,
        records=RECORDS,new_GPU_execution=False,foreign_code_executed=False,
        native_original_SOURCE_precision_certified=False,native_oblique_phase_bound_rad=None,
        current_job_admission=False,promotion='STOP_NO_MATCHING_QUERY_OR_NATIVE_POINTWISE_BUDGET',
        scope='READ_ONLY_EXISTING_ARCHIVE_AND_SOURCE_NOT_REEXECUTION')))
    raise SystemExit(0 if result.wasSuccessful() else 1)

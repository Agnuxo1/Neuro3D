from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import unittest
from exp005_history_job_plan import BASELINE, BASELINE_SHA
from exp005_history_artifact_data import validate_data, canonical
REPO_ROOT = Path(__file__).resolve().parents[2]
NEURO3D_COGNITION = Path(os.environ.get("NEURO3D_COGNITION_DIR", REPO_ROOT / ".cognition"))


def audit():
    assert hashlib.sha256(BASELINE.read_bytes()).hexdigest()==BASELINE_SHA
    report=deepcopy(json.loads(BASELINE.read_text())['control']['result'])
    deadline=datetime(2026,9,30,15,0,tzinfo=timezone.utc)
    report['job_deadline_utc']=deadline.isoformat()
    folder=NEURO3D_COGNITION / 'neuro3d/CPU_DOUBLES_NOT_BLEND'
    blobs={c['case']+'.blend':('CPU DOUBLE NOT BLEND '+c['case']).encode() for c in report['cases']}
    for case in report['cases']:
        case['blend_path']=str(folder/(case['case']+'.blend'))
        case['blend_sha256']=hashlib.sha256(blobs[case['case']+'.blend']).hexdigest()
    def read(path):return blobs[path.name]
    before=canonical(report);control=validate_data(report,folder,deadline,read_blob=read)
    assert before==canonical(report)
    negatives={}
    def trial(name,mutate,reader=read):
        candidate=deepcopy(report);mutate(candidate)
        try:validate_data(candidate,folder,deadline,read_blob=reader)
        except ValueError as error:negatives[name]=str(error)
        else:raise AssertionError('invalid artifact data accepted: '+name)
    trial('missing_case',lambda r:r['cases'].pop())
    trial('reordered_cases',lambda r:r['cases'].reverse())
    trial('duplicate_case',lambda r:r['cases'].__setitem__(1,deepcopy(r['cases'][0])))
    trial('wrong_scope',lambda r:r.update(scope='GPU inference certified'))
    trial('deadline_mismatch',lambda r:r.update(job_deadline_utc='2026-09-30T06:00:00+00:00'))
    trial('foreign_path',lambda r:r['cases'][0].update(blend_path=str(folder.parent/'base.blend')))
    trial('wrong_file_hash',lambda r:r['cases'][0].update(blend_sha256='0'*64))
    trial('changed_readback',lambda r:r['cases'][0]['after']['objects']['MA'].update(phase_rad=.25))
    trial('reordered_before_objects',lambda r:r['cases'][0]['before'].update(
        objects=dict(reversed(list(r['cases'][0]['before']['objects'].items())))))
    trial('missing_terminal_record',lambda r:r['cases'][0]['result']['generated_history']['records'].pop())
    trial('fake_field_error',lambda r:r['cases'][0]['result']['export_checks'].update(analytic_field_error=.01))
    def change_field(r):
        value=r['cases'][0]['result']['export_checks']['cpu_reference']['ports']['Dx']['groups']['g']['field_reim']
        value[0]+=.1
    trial('changed_complex_field',change_field)
    trial('fake_native_provenance',lambda r:r['cases'][0]['result'].update(native_backend_received_paths=True))
    trial('nan_report',lambda r:r['cases'][0]['result']['export_checks'].update(analytic_field_error=float('nan')))
    reads=[0]
    def changing(path):
        reads[0]+=1
        return read(path) if reads[0]<=3 else b'changed during audit'
    trial('changed_bytes_during_audit',lambda r:None,changing)
    return {'scope':'CPU snapshot and byte doubles only; no file/Bpy/GPU execution',
            'control':control,'negatives':negatives,'inputs_immutable':before==canonical(report)}


class ArtifactDataCPU(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.report=audit()

    def test_fresh_after_traversal_matches_three_cases_without_provenance_claim(self):
        result=self.report['control']
        self.assertTrue(result['artifact_data_consistent'])
        self.assertEqual([case['records'] for case in result['cases']],[13,13,13])
        self.assertFalse(result['bpy_execution_certified'])
        self.assertFalse(result['operational_gate_passed'])
        self.assertFalse(result['blend_format_checked'])
        self.assertTrue(self.report['inputs_immutable'])

    def test_corrupt_or_incomplete_artifacts_rejected(self):
        self.assertEqual(len(self.report['negatives']),15)
        self.assertIn('fresh scene traversal',self.report['negatives']['missing_terminal_record'])
        self.assertIn('changed during audit',self.report['negatives']['changed_bytes_during_audit'])


if __name__=='__main__':unittest.main()

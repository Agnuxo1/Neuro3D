from datetime import datetime, timedelta, timezone
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import exp005_history_job_plan as plan
REPO_ROOT = Path(__file__).resolve().parents[2]
NEURO3D_COGNITION = Path(os.environ.get("NEURO3D_COGNITION_DIR", REPO_ROOT / ".cognition"))


def audit():
    """Use actual frozen code pins, but synthetic executable/telemetry/clock."""
    now = datetime(2026, 9, 30, 14, 30, tzinfo=timezone.utc)
    sample = {'ram_available_bytes': 9*plan.GIB, 'device_used_bytes': plan.GIB, 'temperature_c': 40}
    negatives = {}
    (NEURO3D_COGNITION / 'neuro3d').mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='cpu-job-plan-', dir=NEURO3D_COGNITION / 'neuro3d') as temp:
        folder = Path(temp)
        # No executable is written or run: mock its existence/hash explicitly.
        exe = folder/'blender.exe'; evidence = folder/'private_evidence'
        original_sha = plan.sha
        def hashes(path):
            return '0'*64 if path == exe else original_sha(path)
        with patch.object(Path, 'is_file', return_value=True), patch.object(plan, 'sha', hashes):
            def call(**changes):
                args = dict(blender=exe, evidence=evidence, allowed_parent=folder,
                            deadline=now+timedelta(seconds=120), sample=sample, now=now)
                args.update(changes)
                return plan.prepare(**args)
            control = call()
            trials = [('historic_deadline', {'deadline': datetime(2026,9,30,6,tzinfo=timezone.utc)}),
                      ('too_short', {'deadline': now+timedelta(seconds=114)}),
                      ('too_long', {'deadline': now+timedelta(seconds=121)}),
                      ('naive', {'deadline': now.replace(tzinfo=None)}),
                      ('relative_path', {'evidence': Path('relative')}),
                      ('outside_parent', {'evidence': folder.parent/'foreign'})]
            for name, values in [('low_ram', {'ram_available_bytes': 6*plan.GIB}),
                                 ('high_vram', {'device_used_bytes': 17*plan.GIB}),
                                 ('hot', {'temperature_c': 81}),
                                 ('missing', {}), ('nan', {'temperature_c': float('nan')})]:
                modified = {} if name == 'missing' else dict(sample, **values)
                trials.append((name, {'sample': modified}))
            for name, changes in trials:
                try:call(**changes)
                except ValueError as error:negatives[name] = str(error)
                else:raise AssertionError('accepted negative '+name)
            with patch.object(plan, 'sha', return_value='f'*64):
                try:call()
                except ValueError as error:negatives['changed_baseline'] = str(error)
                else:raise AssertionError('changed baseline accepted')
            def altered_runner(path):
                return 'f'*64 if path == plan.RUNNER else hashes(path)
            with patch.object(plan, 'sha', altered_runner):
                try:call()
                except ValueError as error:negatives['changed_runner'] = str(error)
                else:raise AssertionError('changed runner accepted')
            # Existing output directory, but no blend/report/executable creation.
            evidence.mkdir()
            try:call()
            except ValueError as error:negatives['existing_folder'] = str(error)
            else:raise AssertionError('existing folder accepted')
        assert not (evidence/'export.json').exists()
    return {'scope': 'CPU plan only; actual dependency hashes, synthetic executable/resources/deadline',
            'control': control, 'negatives': negatives, 'launched': False}


class HistoryJobPlanCPU(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.report = audit()

    def test_manifest_is_not_launch_authority(self):
        manifest = self.report['control']
        self.assertFalse(manifest['admitted_for_launch'])
        self.assertEqual(len(manifest['code_sha256']), 18)
        self.assertEqual(manifest['child_timeout_s'], 110)
        self.assertEqual(manifest['close_margin_s'], 10)
        index = manifest['command'].index('--job-deadline-utc')
        self.assertEqual(manifest['command'][index+1], manifest['job_deadline_utc'])
        self.assertIn('--python-exit-code', manifest['command'])
        self.assertIn('CPU tracing/fields', manifest['scope'])

    def test_bounds_and_stale_inputs_rejected(self):
        self.assertEqual(len(self.report['negatives']), 14)
        self.assertIn('changed baseline report', self.report['negatives']['changed_baseline'])
        self.assertIn('changed or foreign dependency', self.report['negatives']['changed_runner'])
        self.assertFalse(self.report['launched'])


if __name__ == '__main__':unittest.main()

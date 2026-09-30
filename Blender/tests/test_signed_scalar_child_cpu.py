"""Synthetic ancestry/argv binding and fake preferences only; no GPU/Blender."""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace as NS
import unittest
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'Blender/tests'))
import exp005_signed_scalar_child as E


class ChildTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=ROOT/'Blender/tests')
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.exe = self.base/'not-executed.exe'; self.exe.write_bytes(b'CPU fixture only')
        self.rpath, self.bpath = self.base/'recipe.json', self.base/'binding.json'
        argv = E.command(self.exe, self.rpath, self.bpath)
        now = datetime.now(timezone.utc)
        self.recipe = E.B.recipe(argv, self.base/'capture', self.base/'supervisor',
            deadline=now+timedelta(seconds=90), now=now, queue_name='CPU-child-binding', timeout=60)
        E.C.write_once(self.rpath, self.recipe)
        self.binding = {'version': 'signed-scalar-child-v1', 'recipe_sha256': E.C.sha(self.rpath),
            'entrypoint_sha256': E.C.sha(E.SELF), 'executable_sha256': E.C.sha(self.exe),
            'guard_pid': 200, 'guard_birth': 2000., 'queue_pid': 100, 'queue_birth': 1000.}
        self.holder = {'name': 'CPU-child-binding', 'pid': 100, 'ctime': 1000.,
                       'child_pid': 200, 'child_ctime': 2000.}
        self.current = {'pid': 300, 'ppid': 200, 'birth': 3000., 'argv': argv}
        self.parent = {'pid': 200, 'ppid': 100, 'birth': 2000.}
        self.queue = {'pid': 100, 'ppid': 99, 'birth': 1000.}
        self.environ = {'GPUQ_NAME': 'CPU-child-binding', 'GPUQ_HOLDER': '1'}

    def check(self):
        return E.validate_binding(self.recipe, self.binding, recipe_path=self.rpath,
            binding_path=self.bpath, holder=self.holder, current=self.current,
            parent=self.parent, queue=self.queue, environ=self.environ)

    def test_correct_grandchild_is_not_mistaken_for_gpuq_direct_child(self):
        result = self.check()
        self.assertEqual((result['child_pid'], result['guard_pid'], result['queue_pid']), (300, 200, 100))
        self.assertFalse(result['runtime_execution_authenticated'])
        self.assertFalse(result['native_promotion_allowed'])

    def test_parent_or_queue_PID_reuse_rejects(self):
        for process in (self.parent, self.queue):
            birth = process['birth']; process['birth'] += 1
            with self.assertRaises(ValueError): self.check()
            process['birth'] = birth

    def test_direct_holder_blender_or_unrelated_parent_rejects(self):
        self.holder.update(child_pid=300, child_ctime=3000.)
        with self.assertRaises(ValueError): self.check()
        self.holder.update(child_pid=200, child_ctime=2000.)
        self.current['ppid'] = 201
        with self.assertRaises(ValueError): self.check()

    def test_missing_environment_or_changed_holder_name_rejects(self):
        self.environ.pop('GPUQ_HOLDER')
        with self.assertRaises(ValueError): self.check()
        self.environ['GPUQ_HOLDER'] = '1'; self.holder['name'] = 'other-owner'
        with self.assertRaises(ValueError): self.check()

    def test_boolean_PID_and_nonfinite_birth_reject(self):
        self.binding['guard_pid'] = True
        with self.assertRaises(ValueError): self.check()
        self.binding['guard_pid'] = 200; self.binding['queue_birth'] = float('nan')
        with self.assertRaises(ValueError): self.check()

    def test_factory_startup_or_actual_argv_mismatch_rejects(self):
        self.current['argv'] = [a for a in self.current['argv'] if a != '--factory-startup']
        with self.assertRaises(ValueError): self.check()

    def test_recipe_entrypoint_and_executable_tamper_rejects(self):
        for key in ('recipe_sha256', 'entrypoint_sha256', 'executable_sha256'):
            original = self.binding[key]; self.binding[key] = '0'*64
            with self.assertRaises(ValueError): self.check()
            self.binding[key] = original
        self.exe.write_bytes(b'changed own disposable fixture')
        with self.assertRaises(ValueError): self.check()

    def test_unknown_binding_field_and_outside_input_path_reject(self):
        self.binding['promote'] = True
        with self.assertRaises(ValueError): self.check()
        self.binding.pop('promote')
        with self.assertRaises(ValueError):
            E.validate_binding(self.recipe, self.binding, recipe_path=ROOT.parent/'recipe.json',
                binding_path=self.bpath, holder=self.holder, current=self.current,
                parent=self.parent, queue=self.queue, environ=self.environ)

    def test_expired_child_deadline_rejects_before_native_work(self):
        with self.assertRaises(ValueError):
            E.C.fresh_deadline(datetime.now(timezone.utc)-timedelta(seconds=1))

    def test_private_preferences_disable_save_before_mutations(self):
        events = []
        class Preferences:
            view = NS(use_save_prompt=True)
            filepaths = NS(use_auto_save_temporary_files=True)
            def __setattr__(self, name, value):
                events.append((name, value)); object.__setattr__(self, name, value)
        p = Preferences(); E.private_preferences(NS(context=NS(preferences=p)))
        self.assertEqual(events[0], ('use_preferences_save', False))
        self.assertFalse(p.view.use_save_prompt); self.assertFalse(p.filepaths.use_auto_save_temporary_files)

    def test_clean_exit_is_scheduled_not_hard_exit_and_import_is_non_native(self):
        timer = Mock(); fake = NS(app=NS(timers=NS(register=timer)))
        E.schedule_clean_exit(fake)
        self.assertEqual(timer.call_args.kwargs, {'first_interval': .1})
        self.assertNotIn('bpy', sys.modules); self.assertNotIn('gpu', sys.modules)


if __name__ == '__main__': unittest.main()

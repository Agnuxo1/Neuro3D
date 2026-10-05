"""Blender regression controls: escaped interference, saved ref and portable assets.
Run with blender -b -t 1 --python-exit-code 1 --python this_file.
No rendering, training or GPU kernels.
"""
import importlib.util
import json
import math
from pathlib import Path
import shutil
import tempfile
import bpy
import numpy as np

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('iris_demo', HERE / 'neuro3d_iris_demo.py')
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)
results = {}

# Empty optical scene: coincident outgoing fields must interfere before power.
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
sc = bpy.context.scene
sc['sources'] = json.dumps([{'id':'a','p':[0,0,0],'d':[1,0,0]}, {'id':'b','p':[0,0,0],'d':[1,0,0]}])
demo.trace({'a':1, 'b':1}); assert abs(demo.TRACE_INFO['escape'] - 4) < 1e-12
demo.trace({'a':1, 'b':-1}); assert demo.TRACE_INFO['escape'] < 1e-12
sc['sources'] = json.dumps([{'id':'a','p':[0,0,0],'d':[1,0,0]}, {'id':'b','p':[0,0,0],'d':[0,1,0]}])
demo.trace({'a':1, 'b':1}); assert abs(demo.TRACE_INFO['escape'] - 2) < 1e-12
results['coherent_escape_controls'] = 'PASS'

state = demo.load_state(); x, y, _ = demo.load_iris()
demo.build_scene(np.array(state['theta']).reshape(demo.K,demo.K), state['ref'])
before = demo.classify(x[71])[2]
demo.embed_assets()
code = bpy.data.texts.new('neuro3d_iris_demo.py'); code.from_string((HERE / 'neuro3d_iris_demo.py').read_text(encoding='utf-8'))
with tempfile.TemporaryDirectory(prefix='.neuro3d-test-', dir=HERE) as tmp:
    saved = Path(tmp)/'original'/'scene.blend'; saved.parent.mkdir()
    bpy.ops.wm.save_as_mainfile(filepath=str(saved))
    moved = Path(tmp)/'elsewhere'/'scene.blend'; moved.parent.mkdir(); shutil.copy2(saved,moved)
    bpy.ops.wm.open_mainfile(filepath=str(moved))
    original_here = demo.HERE; demo.HERE = str(moved.parent)
    assert demo.load_raw()[0].shape == (150,4)
    assert demo.load_state()['theta'] == state['theta']
    after = demo.classify(x[71])[2]
    assert max(abs(before[k]-after[k]) for k in before) < 1e-8
    # Mutating the persisted ref must change actual classifier fields.
    bpy.context.scene['ref'] *= 1.5
    changed = demo.classify(x[71])[2]
    assert max(abs(after[k]-changed[k]) for k in after) > 1e-3
    bpy.context.scene['ref'] = state['ref']
    demo.build_scene(np.array(demo.load_state()['theta']).reshape(demo.K,demo.K), demo.load_state()['ref'])
    assert demo.classify(x[71])[0] == int(y[71])
    bpy.data.texts.remove(bpy.data.texts['neuro3d.asset.iris.csv'])
    try: demo.load_raw()
    except RuntimeError: pass
    else: raise AssertionError('Missing embedded data silently fell back')
    demo.HERE = original_here
results['portable_saved_rebuilt_scene'] = 'PASS'
results['scene_reference_intervention'] = 'PASS'
results['missing_embedded_asset_fails'] = 'PASS'

# Interactive rebuild must preserve the user's scene even with conflicting collection names.
bpy.ops.wm.read_factory_settings(use_empty=True)
prior_scene = bpy.context.scene
prior_collection = bpy.data.collections.new('Optics')
prior_scene.collection.children.link(prior_collection)
sentinel = bpy.data.objects.new('unsaved-user-object', None)
prior_collection.objects.link(sentinel)
prior_count = len(bpy.data.objects)
demo.build_scene(np.array(state['theta']).reshape(demo.K,demo.K), state['ref'], reset=False)
assert bpy.context.scene != prior_scene and prior_scene.use_fake_user
assert sentinel in prior_collection.objects[:] and sentinel.name in bpy.data.objects
assert len(prior_collection.objects) == 1
assert len(demo.scene_collection('Optics').objects) > 1
assert len(bpy.data.objects) > prior_count
demo.classify(x[71])
results['interactive_rebuild_preserves_user_scene'] = 'PASS'

# Training bootstrap and post-training bundle refresh: cheap deterministic trainer fixture.
saved_train, saved_build, saved_classify = demo.train, demo.build_scene, demo.classify
try:
    with tempfile.TemporaryDirectory(prefix='.neuro3d-train-test-', dir=HERE) as tmp:
        demo.HERE = tmp
        shutil.copy2(HERE / 'iris.csv', Path(tmp) / 'iris.csv')
        bpy.ops.wm.read_factory_settings(use_empty=True)
        x0, y0, scale = demo.load_iris()  # weights deliberately absent
        raw, _ = demo.load_raw(); train_idx, _ = demo.split()
        assert np.array_equal(scale[0], raw[train_idx].min(0))
        assert np.array_equal(scale[1], raw[train_idx].max(0))
        p = np.zeros(18); p[16] = 0.75
        demo.train = lambda *args, **kwargs: p.copy()
        built = []
        demo.build_scene = lambda theta, ref: built.append((theta.copy(), ref))
        demo.main(['--train'])
        assert demo.load_state()['ref'] == 0.75 and built[-1][1] == 0.75
        demo.embed_assets()
        p[16] = 1.25; p[0] = 0.4
        demo.main(['--train'])
        assert demo.load_state()['ref'] == 1.25 and built[-1][1] == 1.25
        assert demo.load_state()['theta'][0] == 0.4
        # A stale successful report must be replaced when a new trace yields NaN.
        report_path = Path(tmp) / 'scene_verification.json'
        report_path.write_text('{"verification_passed":true}')
        demo.classify = lambda row: (0, np.array([float('nan'), 0, 0]), {}, [], 0)
        try: demo.main(['--verify'])
        except RuntimeError as exc: assert 'Non-finite' in str(exc)
        else: raise AssertionError('Non-finite trace passed')
        failed = json.loads(report_path.read_text())
        assert failed['verification_passed'] is False
        assert 'Non-finite' in failed['verification_failures'][0]
finally:
    demo.HERE = str(HERE)
    demo.train, demo.build_scene, demo.classify = saved_train, saved_build, saved_classify
results['train_bootstrap_and_bundle_refresh'] = 'PASS (trainer fixture, no optimization run)'
results['failed_trace_overwrites_stale_report'] = 'PASS'
print('IRIS_REVIEW_CONTROLS', json.dumps(results), flush=True)

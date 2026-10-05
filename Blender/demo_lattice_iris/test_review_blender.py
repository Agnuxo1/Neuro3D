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
print('IRIS_REVIEW_CONTROLS', json.dumps(results), flush=True)

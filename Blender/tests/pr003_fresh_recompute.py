"""Read-only bounded PR#3 audit: embedded code, TRAIN scaler, fresh inference.

Two fixed holdout flowers plus optical/visual intervention on an in-memory copy.
No retraining, render, saving or edits to Claude's worktree. Run through gpuq.
Parity with Claude's training model is not an independent physical-wave oracle.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import bpy
import numpy as np

HERE = Path('D:/PROJECTS/.cognition/neuro3d/wt-demo/Blender/demo_lattice_iris')


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--evidence',required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    folder = Path(args.evidence).resolve(); folder.mkdir(parents=True,exist_ok=True)
    blend = HERE/'renders/neuro3d_iris_lattice.blend'
    sha = hashlib.sha256(blend.read_bytes()).hexdigest()
    bpy.ops.wm.open_mainfile(filepath=str(blend))
    source = bpy.data.texts['neuro3d_iris_demo.py'].as_string()
    assert source == (HERE/'neuro3d_iris_demo.py').read_text(encoding='utf-8')
    ns = {'__name__':'pr003_review'}
    exec(compile(source,'embedded_pr003','exec'),ns)
    assert Path(ns['HERE'])==HERE
    st = json.loads((HERE/'trained_lattice.json').read_text())
    raw,y = ns['load_raw'](); tr,te = ns['split']()
    assert not set(tr)&set(te)
    assert list(tr)==st['train_idx'] and list(te)==st['test_idx']
    assert np.array_equal(raw[tr].min(0),st['scaler_lo'])
    assert np.array_equal(raw[tr].max(0),st['scaler_hi'])
    x,_,_ = ns['load_iris']()
    ins,outs = ns['modes']()
    U = ns['model_U'](np.array(st['theta']).reshape(4,4)*ns['LAM']/(4*np.pi))
    selected = [int(te[0]),13]  # 13 is a held-out feature below the TRAIN minimum
    assert set(selected)<=set(te)
    def evaluate(n):
        flags = {c.name:c.exclude for c in bpy.context.view_layer.layer_collection.children}
        pred,P,det,_,casts = ns['classify'](x[n])
        assert flags=={c.name:c.exclude for c in bpy.context.view_layer.layer_collection.children}
        fields = np.array([det.get(name,0j) for name in outs])
        expected = U@ns['encode'](x[n][None],st['ref'])[0]
        escape = ns['TRACE_INFO']['escape']
        error = float(np.max(np.abs(fields-expected)))
        balance = float(abs(np.sum(np.abs(fields)**2)-1))
        return fields,{'index':n,'prediction':int(pred),'truth':int(y[n]),
                       'max_complex_error':error,'power_balance_error':balance,
                       'escape_path_power':escape,'raycasts':casts}
    records = []; first = None
    for n in selected:
        fields,record = evaluate(n); records.append(record)
        assert record['max_complex_error']<=2e-3 and record['power_balance_error']<=1e-3
        assert record['escape_path_power']==0
        if first is None: first = fields
    sc = bpy.context.scene
    sc.objects['c12.r1'].color = (.9,.1,.2,1)
    sham,_ = evaluate(selected[0]); sham_error = float(np.max(np.abs(sham-first)))
    assert sham_error<=2e-3
    for name in ('c12.r1','c12.r2'): sc.objects[name].location.x += .003125
    changed,record = evaluate(selected[0]); optical_change = float(np.max(np.abs(changed-first)))
    # The unchanged training matrix SHOULD disagree after actual geometry changes.
    assert optical_change>1e-4 and record['escape_path_power']==0
    ns['register']()
    assert bpy.types.Panel.bl_rna_get_subclass_py('NEURO3D_PT_panel') is not None
    assert hashlib.sha256(blend.read_bytes()).hexdigest()==sha
    result = {'passed':True,'blender_version':bpy.app.version_string,
              'blend_sha256':sha,'embedded_script_matches_file':True,'train_only_scaler':True,
              'panel_registration':True,'samples':records,'sham_complex_error':sham_error,
              'mirror_move_BU':.003125,'geometry_complex_change':optical_change,
              'scope':'fresh recompute hybrid raycast/Python; not full holdout rerun or GPU speed benchmark'}
    (folder/'pr003_fresh_recompute.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print('PR003_FRESH_RECOMPUTE_PASS',flush=True)


if __name__=='__main__': main()

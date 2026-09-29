"""Independent CPU-only checks of saved X/W/Y. Never launches Blender/CUDA.

Historical evidence is diagnostic, not a retrospectively pre-registered gate.
File hashes bind CURRENT files, not prove what a past render actually consumed.
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

MAX_ELEMENTS = 4_194_304


def load_array(path):
    path = Path(path)
    if path.stat().st_size > 32 * 2**20:
        raise ValueError('artifact exceeds CPU audit budget')
    data = path.read_bytes()
    arr = np.load(path, allow_pickle=False)
    if arr.dtype.kind not in 'fiu' or arr.size > MAX_ELEMENTS:
        raise ValueError('numeric bounded array required')
    return arr, {'path':str(path.resolve()), 'sha256':hashlib.sha256(data).hexdigest(),
                 'shape':list(arr.shape), 'dtype':str(arr.dtype)}


def compare_batch(x, weights, observed):
    x, weights, observed = (np.asarray(a, dtype=np.float64) for a in (x,weights,observed))
    if any(a.ndim != 2 or not a.size or a.size > MAX_ELEMENTS for a in (x,weights,observed)):
        raise ValueError('bounded nonempty 2D arrays required')
    if x.shape[1] != weights.shape[0] or observed.shape != (x.shape[0],weights.shape[1]):
        raise ValueError('batch/input/output dimensions mismatch')
    if not all(np.isfinite(a).all() for a in (x,weights,observed)):
        raise ValueError('nonfinite artifact')
    reference = x @ weights
    error = observed-reference
    norm = float(np.linalg.norm(reference))
    row_norm = np.linalg.norm(reference,axis=1)
    row_error = np.linalg.norm(error,axis=1)
    nonzero = row_norm > 0
    return {'B':x.shape[0], 'N':weights.shape[0], 'M':weights.shape[1],
            'relative_l2':float(np.linalg.norm(error)/norm) if norm else None,
            'max_abs_error':float(np.max(np.abs(error))),
            'max_row_relative_l2':float(np.max(row_error[nonzero]/row_norm[nonzero])) if nonzero.any() else None,
            'zero_reference_rows':int((~nonzero).sum()),
            'zero_reference_rows_exact':bool(np.all(row_error[~nonzero] == 0)),
            'reference_norm':norm}, reference


def compare_iris(observed, reference, labels, model_predictions, train_idx, test_idx):
    observed,reference = (np.asarray(a,dtype=np.float64) for a in (observed,reference))
    labels,model_predictions = np.asarray(labels),np.asarray(model_predictions)
    if observed.shape != reference.shape or observed.ndim != 2 or observed.shape[1] != 16:
        raise ValueError('Iris requires eight real and eight imaginary outputs')
    b = observed.shape[0]
    if labels.shape != (b,) or model_predictions.shape != (b,):
        raise ValueError('label/prediction shape mismatch')
    if any(a.dtype.kind not in 'iu' or not np.isin(a,[0,1,2]).all() for a in (labels,model_predictions)):
        raise ValueError('integer Iris classes required')
    if not all(np.isfinite(a).all() for a in (observed,reference)):
        raise ValueError('nonfinite field')
    tr,te = np.asarray(train_idx),np.asarray(test_idx)
    if any(a.ndim != 1 or not a.size or a.dtype.kind not in 'iu' for a in (tr,te)):
        raise ValueError('integer split indices required')
    combined = np.concatenate([tr,te])
    if combined.size != b or not np.array_equal(np.sort(combined),np.arange(b)):
        raise ValueError('split must partition all samples without overlap')
    def classify(y):
        return (y[:,:8]**2+y[:,8:]**2)[:,:3].argmax(axis=1)
    pred,ref_pred = classify(observed),classify(reference)
    return {'test_samples':len(te),'test_correct':int((pred[te]==labels[te]).sum()),
            'test_accuracy':float((pred[te]==labels[te]).mean()),
            'agreement_with_current_matvec_reference':float((pred==ref_pred).mean()),
            'agreement_with_saved_model_predictions':float((pred==model_predictions).mean()),
            'scope':'CPU detection from saved linear readback; not all-GPU neural inference'}


def run(root,trained_path):
    root = Path(root); cases = [('iris',root/'iris_X.npy',root/'iris_W.npy')]
    cases += [(f'rand_N{n}_B{b}',root/'tmp'/f'X{n}_{b}.npy',root/'tmp'/f'W{n}.npy')
              for n,bs in ((64,(1,64,1024)),(256,(1,64)),(1024,(1,4))) for b in bs]
    report = {'scope':'post-restart diagnostic of current saved arrays; no runtime or RT certification',
              'current_input_identity_is_not_historical_provenance':True,
              'full_gpu_verified':False,'coherent_rt_verified':False,'cases':[]}
    for tag,xpath,wpath in cases:
        item = {'tag':tag}
        try:
            x,xid = load_array(xpath); w,wid = load_array(wpath)
            y,yid = load_array(root/'tmp'/f'{tag}.npy')
            metrics,reference = compare_batch(x,w,y)
            item.update(metrics=metrics,artifacts=[xid,wid,yid])
            if tag == 'iris':
                labels,lid = load_array(root/'iris_y.npy')
                pred,pid = load_array(root/'iris_pred_model.npy')
                trained_path = Path(trained_path); raw = trained_path.read_bytes()
                trained = json.loads(raw)
                item['iris'] = compare_iris(y,reference,labels,pred,trained['train_idx'],trained['test_idx'])
                item['artifacts'] += [lid,pid,{'path':str(trained_path.resolve()),'sha256':hashlib.sha256(raw).hexdigest()}]
            item['status'] = 'diagnostic_complete'
        except (OSError,ValueError,KeyError) as exc:
            item.update(status='incomplete_or_invalid',error=str(exc))
        report['cases'].append(item)
    return report


def main():
    p=argparse.ArgumentParser(); p.add_argument('--root',required=True)
    p.add_argument('--trained',required=True); p.add_argument('--output',required=True); args=p.parse_args()
    result=run(args.root,args.trained)
    Path(args.output).write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    print(json.dumps([{'tag':r['tag'],'status':r['status'],'metrics':r.get('metrics'),'iris':r.get('iris'),'error':r.get('error')}
                      for r in result['cases']],allow_nan=False))


if __name__=='__main__': main()

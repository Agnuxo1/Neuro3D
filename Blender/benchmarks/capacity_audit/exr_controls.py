"""Independent pixel/causality audit of a SMALL signed-intensity render.

CPU OpenCV decodes retained EXR, independent of producer bpy pixel reader.
OpenCV returns top-left BGRA; geometry/pixel grid is bottom-left RGBA.
No Blender, CUDA or producer imports. This cannot certify hardware RT execution.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path

import numpy as np
from batch_readback import compare_batch,load_array

MAX_PIXELS=1_048_576


def decode_exr(path):
    os.environ['OPENCV_IO_ENABLE_OPENEXR']='1'
    import cv2
    cv2.setNumThreads(1)
    path=Path(path)
    if path.stat().st_size>32*2**20: raise ValueError('EXR exceeds bounded audit size')
    image=cv2.imread(str(path),cv2.IMREAD_UNCHANGED)
    if image is None or image.ndim!=3 or image.shape[2]<3 or image.dtype!=np.float32:
        raise ValueError('float32 multichannel EXR required')
    if image.shape[0]*image.shape[1]>MAX_PIXELS or not np.isfinite(image).all():
        raise ValueError('nonfinite or oversized EXR')
    rgba=np.empty_like(image)
    rgba[...,:3]=image[::-1,:,2::-1]
    if image.shape[2]>3: rgba[...,3:]=image[::-1,:,3:]
    return rgba,{'path':str(path.resolve()),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                 'shape':list(rgba.shape),'decoder':'OpenCV CPU, flipped BGRA to bottom-left RGBA'}


def inspect_pixels(image,x,w,tiles):
    image=np.asarray(image); x=np.asarray(x,dtype=np.float64); w=np.asarray(w,dtype=np.float64)
    if x.ndim!=2 or w.ndim!=2 or x.shape[1]!=w.shape[0]: raise ValueError('input shapes')
    b,n=x.shape; m=w.shape[1]
    if len(tiles)!=2 or any(isinstance(t,bool) or not isinstance(t,int) or t<=0 for t in tiles):
        raise ValueError('tile grid')
    tx,ty=tiles
    if tx*ty<b or image.shape[:2]!=(ty*2*n,tx*m) or image.shape[2]<3:
        raise ValueError('image/grid shape mismatch')
    if image.shape[0]*image.shape[1]>MAX_PIXELS or not all(np.isfinite(a).all() for a in (image,x,w)):
        raise ValueError('bounded finite pixels required')
    if np.max(np.abs(w))>1: raise ValueError('transmittance outside signed unit interval')
    wr=np.concatenate((w,-w),axis=0)
    rows=np.concatenate((np.maximum(x,0),np.maximum(-x,0)),axis=1)
    y=np.empty((b,m),dtype=np.float64); worst=0.
    used=np.zeros(image.shape[:2],dtype=bool)
    for t in range(b):
        ox,oy=(t%tx)*m,(t//tx)*2*n
        block=image[oy:oy+2*n,ox:ox+m]
        expected_r=rows[t,:,None]*np.maximum(wr,0)
        expected_g=rows[t,:,None]*np.maximum(-wr,0)
        worst=max(worst,float(np.max(np.abs(block[...,0]-expected_r))),
                  float(np.max(np.abs(block[...,1]-expected_g))))
        y[t]=np.sum(block[...,0].astype(np.float64)-block[...,1].astype(np.float64),axis=0)
        used[oy:oy+2*n,ox:ox+m]=True
    unused=float(np.max(np.abs(image[~used,:3]))) if (~used).any() else 0.
    metrics,_=compare_batch(x,w,y)
    return y,{'pixel_product_max_abs_error':worst,'unused_pixels_max_rgb':unused,'sum':metrics}


def audit(root):
    root=Path(root); x,xid=load_array(root/'cX.npy'); w,wid=load_array(root/'cW.npy')
    if x.shape[1]<=3 or w.shape[1]<=5: raise ValueError('control fixture too small')
    metadata_path=root/'controls.json'; metadata=json.loads(metadata_path.read_text())
    wp=w.copy(); wp[2,5]=np.clip(float(w[2,5])+.5,-1,1)
    xp=x.copy(); xp[0,3]+=.7
    cases=(('base','controls.exr',x,w),('sham','controls_sham.exr',x,w),
           ('weight','controls_weight.exr',x,wp),('input','controls_input.exr',xp,wp))
    outputs={}; raw_pixels={}; metrics={}; identities=[xid,wid]
    for tag,name,xi,wi in cases:
        image,identity=decode_exr(root/name); identities.append(identity)
        y,metric=inspect_pixels(image,xi,wi,metadata['tiles'])
        outputs[tag]=y; raw_pixels[tag]=image; metrics[tag]=metric
    base,sham,weight,inp=(outputs[k] for k in ('base','sham','weight','input'))
    saved,saved_id=load_array(root/'controls.npy'); identities.append(saved_id)
    return {'scope':'post-run independent CPU EXR/cell-product/causality diagnostic, not pre-registered confirmation',
            'full_gpu_inference_verified':False,'coherent_rt_verified':False,
            'raw_pixel_products_reviewed':True,'cases':metrics,'artifacts':identities,
            'causality':{'sham_max_abs_difference':float(np.max(np.abs(sham-base))),
              'sham_raw_pixel_max_abs_difference':float(np.max(np.abs(raw_pixels['sham']-raw_pixels['base']))),
              'weight_other_columns_max_change':float(np.max(np.abs(np.delete(weight-base,5,axis=1)))),
              'weight_column_max_change':float(np.max(np.abs((weight-base)[:,5]))),
              'input_other_samples_max_change':float(np.max(np.abs((inp-weight)[1:]))),
              'input_sample0_max_change':float(np.max(np.abs((inp-weight)[0]))),
              'producer_saved_output_vs_independent_raw_sum_max':float(np.max(np.abs(saved-base)))},
            'limitations':['Current input hashes are not producer input provenance',
              'Scene persistence/reopen and geometric path intervention not tested',
              'Row reduction/detection still CPU; these are signed intensities, not coherent waves',
              'Hardware RT execution and resource guard telemetry not independently established']}


def main():
    p=argparse.ArgumentParser(); p.add_argument('--root',required=True); p.add_argument('--output',required=True)
    a=p.parse_args(); result=audit(a.root)
    Path(a.output).write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    print(json.dumps({'cases':result['cases'],'causality':result['causality']},allow_nan=False))


if __name__=='__main__': main()

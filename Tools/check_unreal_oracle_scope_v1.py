"""A concrete CPU counterexample to claiming existing Unreal oracle parity.

The shader-side result below is algebra for a single specified edge, not a GPU
run. It isolates normalization: raw color (2,0,0) has norm2; SafeNormalizeColor
emits (1,0,0), whereas the current CPU step accumulates (2,0,0).
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True);args=parser.parse_args()
    source=ROOT/'Plugins/SantoGrialPhotonic/Tests/photonic_reference.py'
    shader=ROOT/'Plugins/SantoGrialPhotonic/Shaders/SantoGrialPhotonic.usf'
    before=hashlib.sha256(source.read_bytes()).hexdigest()
    spec=importlib.util.spec_from_file_location('neuro3d_legacy_unreal_oracle',source)
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
    neurons=[module.Neuron(1.,0.,0.,1.,1.,(2.,0.,0.)),module.Neuron(0.,0.,0.,0.,1.,(1.,0.,0.))]
    actual=module.step(neurons,[module.Edge(0,1,1.,0.)],.125,0.,.25)
    # At dt=1/8, lerp intensity factor=1; unit phase/weight/attenuation.
    shader_field=(1.,0.,0.);shader_power=sum(v*v for v in shader_field);shader_intensity=shader_power**.5
    if actual[1].intensity!=2. or shader_intensity!=1.:raise ValueError('counterexample does not reproduce')
    if hashlib.sha256(source.read_bytes()).hexdigest()!=before:raise ValueError('source changed')
    result={'schema':'neuro3d.unreal.oracle_scope_counterexample.v1','status':'COUNTEREXAMPLE_REPRODUCED',
            'legacy_CPU_output_intensity':actual[1].intensity,'algebraic_shader_expected_output_intensity':shader_intensity,
            'input':{'source_intensity':1.,'source_activation':1.,'source_color':[2.,0.,0.],
                     'phase':0.,'frequency':0.,'weight':1.,'delay':0.,'dt':.125,'attenuation':0.,'threshold':.25},
            'GPU_execution':False,'Unreal_compilation':False,'runtime_parity_verified':False,
            'finding':'Existing CPU oracle and HLSL implement different color normalization; they cannot certify all-field parity without alignment or a versioned reference.',
            'source_sha256':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in (Path(__file__),source,shader)}}
    with args.out.open('xb') as stream:stream.write((json.dumps(result,indent=2,allow_nan=False)+'\n').encode())
    print(json.dumps({k:result[k] for k in ('status','legacy_CPU_output_intensity','algebraic_shader_expected_output_intensity','GPU_execution')}))


if __name__=='__main__':main()

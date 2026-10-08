"""NEW bounded synthetic chain for subsequent GPU contract; CPU only today.

Three/four connected MZI, dyadic quads and scene-owned optical properties.
No edits to frozen conf1/v0/v4/escape0119. No hidden transfer matrix input.
"""
import argparse
import cmath
import copy
import hashlib
import itertools
import json
from pathlib import Path
from exp005_escape_fixture import escape_fixture


def chain_fixture(cells=4,*,treatment='base'):
    if isinstance(cells,bool) or not isinstance(cells,int) or not 2<=cells<=4:
        raise ValueError('bounded chain requires two to four cells')
    if treatment not in ('base','phase','sham','shift','T','lambda'):
        raise ValueError('unknown chain treatment')
    original=escape_fixture(); objects={}
    for i in range(cells):
        delta=(4*i,2*i,0)
        for name,source in original['objects'].items():
            if not name.startswith('a.'): continue
            obj=copy.deepcopy(source)
            obj['vertices_world_BU']=[tuple(x+d for x,d in zip(v,delta)) for v in obj['vertices_world_BU']]
            if obj['kind'] in ('det','escape'):
                obj['mode_origin_BU']=tuple(x+d for x,d in zip(obj['mode_origin_BU'],delta))
            if name=='a.r1': obj['phase_rad']=.2+.17*i
            if obj['kind']=='bs': obj['power_transmittance']=.5
            objects[f'c{i}.{name[2:]}']=obj
    terminal=copy.deepcopy(original['objects']['b.escape']); delta=(4*(cells-2),2*(cells-2),0)
    terminal['vertices_world_BU']=[tuple(x+d for x,d in zip(v,delta)) for v in terminal['vertices_world_BU']]
    terminal['mode_origin_BU']=tuple(x+d for x,d in zip(terminal['mode_origin_BU'],delta))
    objects[f'c{cells-1}.escape']=terminal
    sources=[{'id':'row','position_BU':[-1,0,0],'direction':[1,0,0],'field_reim':[1,0]}]
    sources.extend({'id':f'col{i}','position_BU':[4*i,2*i-1,0],'direction':[0,1,0],'field_reim':[0,0]} for i in range(cells))
    scene={'schema':'exp005-readback-v2','lambda_BU':.126 if treatment=='lambda' else .125,
           'objects':objects,'sources':sources,'undeclared_meshes':[]}
    target=f'c{cells-1}'
    if treatment=='phase': objects[target+'.r1']['phase_rad']+=.1
    if treatment=='T': objects[target+'.bs2']['power_transmittance']=.2
    if treatment=='shift':
        for name in ('r1','r2'):
            obj=objects[target+'.'+name]
            obj['vertices_world_BU']=[(x+.03125,y,z) for x,y,z in obj['vertices_world_BU']]
    # Sham: no optical edit. Runtime will change visual object color only.
    return scene


def inputs(count):
    if not 3<=count<=5: raise ValueError('bounded chain input count required')
    for i in range(count):
        amplitudes=[0j]*count; amplitudes[i]=1+0j
        yield f'basis{i}',amplitudes
    for i,j in itertools.combinations(range(count),2):
        for second in (1+0j,1j):
            amplitudes=[0j]*count; amplitudes[i]=1+0j; amplitudes[j]=second
            yield f'pair{i}{j}_{second.imag:g}',amplitudes


def set_fields(scene,amplitudes):
    if len(amplitudes)!=len(scene['sources']): raise ValueError('complete source amplitudes required')
    for source,value in zip(scene['sources'],amplitudes): source['field_reim']=[value.real,value.imag]


def analytic_fields(cells,amplitudes,*,phase_shift=0.):
    """Independent ideal cell composition ONLY at lambda=.125/T=.5/base geometry.

All lengths are integer multiples of lambda in this fixture. This is a CPU
oracle, never an inference payload. Does not call the geometric ray tracer.
"""
    if not 2<=cells<=4 or len(amplitudes)!=cells+1: raise ValueError('bounded complete analytic inputs')
    result={}; row=amplitudes[0]
    for i in range(cells):
        col=amplitudes[i+1]; phase=.2+.17*i+(phase_shift if i==cells-1 else 0.)
        e=cmath.exp(1j*phase)
        xx=-.5j*(1+e); xy=.5*(e-1); yx=.5*(1-e); yy=-.5j*(1+e)
        result[f'c{i}.Y']=yx*row+yy*col
        row=xx*row+xy*col
    result[f'c{cells-1}.escape']=row
    return result


def summarize(scene,trace):
    """Actual CPU-oracle counts, not estimates of GPU memory/maximum capacity."""
    ports={p:0 for p in trace['fields']}; source_counts={s['id']:0 for s in scene['sources']}
    for path in trace['paths']: ports[path['terminal']]+=1; source_counts[path['source_id']]+=1
    return {'triangles':sum(len(o['faces']) for o in scene['objects'].values()),
            'sources':len(scene['sources']),'ports':len(ports),'rays':trace['rays'],
            'terminal_paths':len(trace['paths']),'paths_by_port':ports,'paths_by_source':source_counts,
            'depth':max((len(p['hits']) for p in trace['paths']),default=0)}


def cpu_report():
    from exp005_triangle_oracle import trace_scene
    report={'scope':'synthetic CPU chain/reference only, no Blender or GPU execution','cells':{}}
    for cells in (3,4):
        scene=chain_fixture(cells); rows=[]
        for label,amps in inputs(cells+1):
            set_fields(scene,amps); traced=trace_scene(scene); reference=analytic_fields(cells,amps)
            rows.append({'probe':label,'field_error':max(abs(traced['fields'][p]-reference[p]) for p in reference),
                         'balance_error':abs(traced['input_power']-traced['output_power']),
                         'fields':{p:[f.real,f.imag] for p,f in traced['fields'].items()},'counts':summarize(scene,traced)})
        set_fields(scene,[1+0j]*(cells+1)); all_sources=trace_scene(scene); baseline=trace_scene(chain_fixture(cells))
        effects={}
        for case in ('phase','shift','T','lambda'):
            treatment=trace_scene(chain_fixture(cells,treatment=case))
            effects[case]=max(abs(treatment['powers'][p]-baseline['powers'][p]) for p in baseline['powers'])
        if (max(r['field_error'] for r in rows)>1e-11 or max(r['balance_error'] for r in rows)>1e-11 or
                min(effects.values())<=1e-3): raise ValueError('synthetic chain CPU gate failed')
        report['cells'][str(cells)]={'snapshot':chain_fixture(cells),'probes':rows,
             'all_source_counts':summarize(scene,all_sources),'causal_power_effects':effects}
    return report


def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--report',type=Path,required=True)
    args=parser.parse_args()
    if args.report.exists(): raise ValueError('fresh CPU report required')
    report=cpu_report(); dependencies=[Path(__file__),Path(__file__).with_name('exp005_cascade_fixture.py'),
                                      Path(__file__).with_name('exp005_escape_fixture.py'),Path(__file__).with_name('exp005_triangle_oracle.py')]
    report['code_sha256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in dependencies}
    args.report.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    print('SYNTHETIC_CHAIN_CPU_PASS')


if __name__=='__main__': main()

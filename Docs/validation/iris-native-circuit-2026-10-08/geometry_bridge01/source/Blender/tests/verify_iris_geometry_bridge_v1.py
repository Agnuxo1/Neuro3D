"""Exact planned triangle geometry -> coherent DAG -> frozen canonical GPU model.

This verifies the rational canonical blueprint, not a float32 Blender capture
or GPU triangle traversal. Exhaust all unique optical states, never threshold
paths. Quotient states share point/direction/previous plane and future operator.
"""
import argparse
from collections import deque
from fractions import Fraction as F
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from Blender.benchmarks.capacity_audit import robust_multipath_v1 as geom
from Blender.tests.audit_iris_native_circuit_v1 import transfer,mp


def surface(center,normal,kind):
    # Exact rational planar quad with two triangles. Same canonical local
    # optical planes; center on a certified interior seam. No Blender rounding.
    tangent=(normal[1],-normal[0],0);radius=F(1,8)
    vertices=[tuple(center[k]+radius*(s*tangent[k]+(t if k==2 else 0)) for k in range(3))
              for s,t in ((-1,-1),(1,-1),(1,1),(-1,1))]
    record={'kind':kind,'vertices_world_BU':vertices,'faces':[(0,1,2),(0,2,3)]}
    if kind=='mirror':record['phase_rad']=F(0)
    if kind=='bs':record['power_transmittance']=F(1,2)
    if kind=='det':record.update(mode_origin_BU=center,mode_direction=normal)
    return record


def blueprint(state):
    wavelength=F(.1);X=[F(0)];Y=[F(0)]
    for i in range(1,4):
        X.append(X[-1]+4+F(.0137)*i+F(.0031)*i*i)
        Y.append(Y[-1]+4+F(.0211)*i+F(.0017)*i*i)
    # The mathematical ideal pi and its represented displacement are distinct;
    # this bridge explicitly uses the original CPU binary64 pi in displacement.
    displacements=[F(theta)*wavelength/(4*F(math.pi)) for theta in state['theta']]
    objects={};sources=[]
    cells=[('bs1',(0,0),(1,-1,0),'bs'),('r1',(2,0),(1,-1,0),'mirror'),
           ('r2',(2,F(1,2)),(1,1,0),'mirror'),('f1',(1,F(1,2)),(1,1,0),'mirror'),
           ('m2',(0,2),(1,-1,0),'mirror'),('bs2',(1,2),(1,-1,0),'bs')]
    for i in range(4):
        for j in range(4):
            ox,oy=X[i]+j,Y[j]+2*i;d=displacements[4*i+j]
            for name,(lx,ly),normal,kind in cells:
                center=(ox+lx+(d if name in ('r1','r2') else 0),oy+ly,F(0))
                objects['c%d%d.%s'%(i,j,name)]=surface(center,normal,kind)
    for j in range(4):
        row_start=(F(j)-1,Y[j],F(0));row_end=(X[3]+j+2,Y[j]+8,F(0))
        sources.append({'id':'r'+str(j),'position_BU':row_start,'direction':(1,0,0),'field_reim':[1,0]})
        objects['R'+str(j)]=surface(row_end,(1,0,0),'det')
    for i in range(4):
        col_start=(X[i],F(2*i)-1,F(0));col_end=(X[i]+4,Y[3]+2*i+3,F(0))
        sources.append({'id':'c'+str(i),'position_BU':col_start,'direction':(0,1,0),'field_reim':[1,0]})
        objects['C'+str(i)]=surface(col_end,(0,1,0),'det')
    return {'schema':'exp005-readback-v2','lambda_BU':wavelength,'objects':objects,'sources':sources,'undeclared_meshes':[]}


def graph(scene):
    wavelength,objects,triangles=geom.geometry(scene);nodes={};pending=deque();roots=[]
    def admit(origin,direction,previous):
        key=(origin,direction,None if previous is None else previous['object_id'])
        if key not in nodes:nodes[key]={'id':len(nodes),'origin':origin,'direction':direction,'previous':previous,'edges':[]};pending.append(key)
        return nodes[key]['id']
    for source in scene['sources']:roots.append(admit(geom.vector(source['position_BU']),geom.vector(source['direction']),None))
    hits=set();checks=0
    while pending:
        node=nodes[pending.popleft()];selection=geom.select(node['origin'],node['direction'],triangles,node['previous']);checks+=1
        if selection['status']!='SELECT':raise ValueError('blueprint unresolved: '+selection['status'])
        selected=selection['selected'];name=selected['object_id'];obj=objects[name];point=selection['point'];parameter=selection['t'];hits.add(name)
        node.update(segment=parameter,hit=name,point=point,coincident_primitives=[t['primitive_id'] for t in selection['candidates']])
        if geom.dot(node['direction'],node['direction'])!=1:raise ValueError('unit cardinal direction required')
        if obj['kind']=='det':
            if node['direction']!=obj['axis'] or point!=obj['reference']:raise ValueError('terminal reference/mode mismatch')
            node['terminal']=name;continue
        reflection=geom.reflected(node['direction'],selected['normal'])
        if obj['kind']=='mirror':branches=[(reflection,F(1),2)]
        else:branches=[(node['direction'],obj['tau'],0),(reflection,1-obj['tau'],1)]
        for direction,power,turn in branches:
            node['edges'].append({'target':admit(point,direction,selected),'coefficient_power':power,'quarter_turns':turn})
        if len(nodes)>1024:raise ValueError('blueprint state budget')
    if hits!=set(objects):raise ValueError('not all learned cells/terminals covered')
    byid=sorted(nodes.values(),key=lambda n:n['id']);degree=[0]*len(byid)
    for node in byid:
        for edge in node['edges']:degree[edge['target']]+=1
    queue=deque(i for i,d in enumerate(degree) if d==0);order=[]
    while queue:
        index=queue.popleft();order.append(index)
        for edge in byid[index]['edges']:
            degree[edge['target']]-=1
            if degree[edge['target']]==0:queue.append(edge['target'])
    if len(order)!=len(byid):raise ValueError('cyclic blueprint cannot use finite coherent DAG quotient')
    fields=[[mp.mpc(0) for _ in roots] for _ in byid];U=mp.matrix(8,8);ports=['R'+str(i) for i in range(4)]+['C'+str(i) for i in range(4)]
    for p,index in enumerate(roots):fields[index][p]=1
    for index in order:
        node=byid[index];phase=mp.exp(2*mp.j*mp.pi*(mp.mpf(node['segment'].numerator)/node['segment'].denominator)/(mp.mpf(wavelength.numerator)/wavelength.denominator))
        incoming=[v*phase for v in fields[index]]
        if 'terminal' in node:
            for p,value in enumerate(incoming):U[ports.index(node['terminal']),p]+=value
        for edge in node['edges']:
            power=edge['coefficient_power'];coefficient=mp.sqrt(mp.mpf(power.numerator)/power.denominator)*(mp.j**edge['quarter_turns'])
            fields[edge['target']]=[a+coefficient*b for a,b in zip(fields[edge['target']],incoming)]
    return U,{'objects':len(objects),'triangles':len(triangles),'all_optical_objects_hit':len(hits),'all_cells':16,
              'unique_geometric_states':len(byid),'exact_first_hit_queries':checks,'DAG_verified':True,'ports':ports,
              'nodes':byid,'topological_order':order,'root_node_ids':roots}


def encode(value):
    if isinstance(value,F):return {'numerator':value.numerator,'denominator':value.denominator}
    if isinstance(value,dict):return {k:encode(v) for k,v in value.items() if k!='previous'}
    if isinstance(value,(list,tuple)):return [encode(v) for v in value]
    return value


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True);args=parser.parse_args()
    saved=ROOT/'Blender/demo_lattice_iris/trained_lattice.json';state=json.loads(saved.read_bytes());results=[]
    for case in ('baseline','phase'):
        current=dict(state);current['theta']=list(state['theta'])
        if case=='phase':current['theta'][0]+=.1
        scene=blueprint(current);observed,proof=graph(scene)
        expected,_=transfer(current['theta'],[.1,1.,4.,.0137,.0031,.0211,.0017])
        error=max(abs((observed-expected)[i,j]) for i in range(8) for j in range(8))
        if error>mp.mpf('1e-11'):raise ValueError('complete geometry/circuit bridge mismatch')
        results.append({'case_id':case,'max_complex_transfer_error':str(error),'geometry':encode(scene),'graph_proof':encode(proof)})
    result={'schema':'neuro3d.iris_lattice.geometry_bridge.v1','status':'PASS','cases':results,
            'scope':'canonical rational planned geometry, exact first-hit graph and coherent linear quotient; CPU proof/90dps numerical bridge',
            'actual_Blender_float32_capture_certified':False,'GPU_triangle_traversal_certified':False,
            'physical_optics_certified':False,'reference_dps':90,
            'source_sha256':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in
                             (Path(__file__),saved,Path(geom.__file__),ROOT/'Blender/tests/audit_iris_native_circuit_v1.py')}}
    with args.out.open('xb') as stream:stream.write((json.dumps(result,indent=2,allow_nan=False)+'\n').encode())
    print(json.dumps({'status':'PASS','cases':[{k:r[k] for k in ('case_id','max_complex_transfer_error')} for r in results]}))


if __name__=='__main__':main()

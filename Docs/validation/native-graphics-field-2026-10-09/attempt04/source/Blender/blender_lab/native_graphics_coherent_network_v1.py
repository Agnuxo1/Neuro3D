"""Hybrid complete graph: actual GPU geometry/phase/branches, CPU field merging."""
import cmath,math,time
from Blender.blender_lab.coherent_state_graph_v1 import segment_coefficient
from Blender.blender_lab.scene_capture_v1 import need


def transport_batch(graph,backend,inputs,*,distance_tolerance_BU):
    need(graph['status']=='COMPLETE' and not graph['unresolved'],'Complete exactly admitted geometry required')
    ids={r['source_id'] for r in graph['roots']}
    need(0<len(inputs)<=152 and all(set(x)==ids for x in inputs),'Bounded explicit common-coherent inputs required')
    n=len(graph['nodes']);samples=len(inputs);incoming=[[[] for _ in inputs] for _ in range(n)];outputs=[{p:[] for p in graph['ports']} for _ in inputs]
    degree=[0]*n
    for node in graph['nodes']:
        for e in node['edges']:degree[e['target']]+=1
    for root in graph['roots']:
        for j,row in enumerate(inputs):incoming[root['node']][j].append(complex(*row[root['source_id']]))
    ready=[i for i,d in enumerate(degree) if d==0];done=[];batches=[];maximum=0.;start=time.perf_counter()
    while ready:
        frontier=ready;ready=[];queries=[];fields=[];mapping=[]
        for i in frontier:
            node=graph['nodes'][i];previous=node['previous_plane']
            for j in range(samples):
                values=incoming[i][j];z=complex(math.fsum(v.real for v in values),math.fsum(v.imag for v in values))
                queries.append({'origin':node['origin'],'direction':node['direction'],'previous_name':previous[0] if previous else None});fields.append(z);mapping.append((i,j))
        need(len(queries)<=4096,'Bounded native graphics coherent frontier required')
        result=backend.query(queries,fields);need(len(result['rows'])==len(mapping),'Complete native field readback required')
        batches.append({'node_ids':frontier,'query_count':len(queries),'incoming_reim':[[z.real,z.imag] for z in fields],'readback':result})
        for (i,j),incoming_field,row in zip(mapping,fields,result['rows']):
            node=graph['nodes'][i]
            need(row['object']==node['hit_object'] and row['primitive_id'] in node['coincident_primitives'],'Actual selected transport surface must match independently exact admitted geometry')
            distance=float(node['segment_parameter'])*math.sqrt(sum(float(v)**2 for v in node['direction']))
            need(abs(distance-row['distance_BU'])<=distance_tolerance_BU,'Actual geometric transport candidate budget required')
            propagated=complex(*row['propagated_reim']);first=complex(*row['first_reim']);second=complex(*row['second_reim'])
            reference=incoming_field*segment_coefficient(node['segment_parameter'],node['direction'],graph['wavelength'])
            maximum=max(maximum,abs(propagated-reference))
            if 'terminal' in node:
                outputs[j][node['terminal']].append(first)
                maximum=max(maximum,abs(first-reference*segment_coefficient(node['reference_parameter'],node['direction'],graph['wavelength'])))
            for edge in node['edges']:
                value=second if edge['event']=='r' else first
                coefficient=math.sqrt(float(edge['power']))*(1j**edge['quarter_turns'])*cmath.exp(1j*float(edge['phase_rad']))
                maximum=max(maximum,abs(value-reference*coefficient));incoming[edge['target']][j].append(value)
        for i in frontier:
            done.append(i)
            for e in graph['nodes'][i]['edges']:
                degree[e['target']]-=1
                if degree[e['target']]==0:ready.append(e['target'])
    need(len(done)==n,'Every complete optical state must execute native transport')
    fields=[{p:complex(math.fsum(v.real for v in a),math.fsum(v.imag for v in a)) for p,a in row.items()} for row in outputs]
    return {'fields_reim':[{p:[z.real,z.imag] for p,z in row.items()} for row in fields],
            'powers':[{p:abs(z)**2 for p,z in row.items()} for row in fields],
            'transport_local_max_difference':maximum,'seconds':time.perf_counter()-start,
            'states':n,'samples':samples,'actual_geometric_ray_queries':n*samples,
            'batches':batches,'gpu_geometry_phase_branches':True,'cpu_compensated_coherent_merging':True,
            'precomputed_transfer_matrix_used':False,'physical_optics_certified':False,'native_rounding_certified':False}

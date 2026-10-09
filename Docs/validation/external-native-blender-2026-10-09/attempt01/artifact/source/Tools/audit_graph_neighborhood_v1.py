"""Independent exact square-perimeter witness for local planar surface unions.

Convex triangles contain the center. Coverage of every square-perimeter point
therefore covers every radial segment and the entire square. An exact positive
radius bounded by all inactive inequalities gives completeness of the local
test. No producer intersection/angle-sorter/union kernel is imported.
"""
from fractions import Fraction as F
from Tools.audit_coherent_state_graph_v1 import audit_graph_result,planar_objects
from Tools.audit_captured_pilot_result_v1 import decode,need,vec


def square_neighborhood(vertices_list,point,normal):
    drop=next(i for i,v in enumerate(normal) if v)
    keep=[i for i in range(3) if i!=drop]
    center=tuple(F(point[i]) for i in keep)
    constraints=[]
    radius=F(1)
    for vertices in vertices_list:
        projected=[tuple(F(v[i]) for i in keep) for v in vertices]
        signed=(projected[1][0]-projected[0][0])*(projected[2][1]-projected[0][1])-(projected[1][1]-projected[0][1])*(projected[2][0]-projected[0][0])
        need(signed!=0,'nondegenerate injective plane projection required')
        winding=1 if signed>0 else -1
        rows=[]
        for i,a in enumerate(projected):
            b=projected[(i+1)%3]
            dx,dy=b[0]-a[0],b[1]-a[1]
            u,v=-winding*dy,winding*dx
            slack=u*(center[0]-a[0])+v*(center[1]-a[1])
            need(slack>=0,'nearest triangle must contain center')
            if slack>0:
                radius=min(radius,slack/(2*(abs(u)+abs(v))))
            rows.append((u,v,slack))
        constraints.append(rows)
    need(constraints and radius>0,'positive rational neighborhood required')
    corners=[(-radius,-radius),(radius,-radius),(radius,radius),(-radius,radius)]
    coverage=[]
    for i,start in enumerate(corners):
        end=corners[(i+1)%4];direction=(end[0]-start[0],end[1]-start[1])
        intervals=[]
        for rows in constraints:
            lower,upper=F(0),F(1)
            for u,v,slack in rows:
                offset=slack+u*start[0]+v*start[1]
                slope=u*direction[0]+v*direction[1]
                if slope==0:
                    if offset<0:
                        lower,upper=F(1),F(0);break
                elif slope>0:
                    lower=max(lower,-offset/slope)
                else:
                    upper=min(upper,-offset/slope)
            if lower<=upper:
                intervals.append((lower,upper))
        covered=F(0)
        for lower,upper in sorted(intervals):
            if lower>covered:
                return None
            covered=max(covered,upper)
        if covered<1:
            return None
        coverage.append(len(intervals))
    return {'projected_radius':[radius.numerator,radius.denominator],
            'projection_keeps':keep,'perimeter_closed_interval_counts':coverage,
            'all_four_edges_covered':True}


def audit_graph_neighborhood(scene_wire,result_wire):
    audit=audit_graph_result(scene_wire,result_wire)
    need(audit['primary_metric']==1,'complete independently audited graph required')
    scene,result=decode(scene_wire),decode(result_wire)
    objects={row[0]:row for row in planar_objects(scene)}
    witnesses=[]
    for node in result['graph']['nodes']:
        obj=objects[node['hit_object']]
        vertices=[vertices for primitive,vertices,normal in obj[3] if primitive in node['coincident_primitives']]
        witness=square_neighborhood(vertices,vec(node['point']),obj[2][1])
        need(witness is not None,'nearest triangle union has no independently proved interior neighborhood')
        witnesses.append(dict(witness,node_id=node['id'],object_id=node['hit_object']))
    return dict(audit,boundary_neighborhood_independently_verified=True,
                neighborhood_witnesses=witnesses,
                neighborhood_method='EXACT_PROJECTED_SQUARE_PERIMETER_CONVEX_RADIAL_COVERAGE',
                scope='Represented planar geometry only; no intended geometry or physical error bound')

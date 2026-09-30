"""Exact CPU tree-completeness gate layered on history V2, not native code.

No amplitudes, terminal-mode acceptance or phase computation. No GPU paths
supplied to a backend. Both splitter events are required even at T=0 or T=1;
zero-field pruning/fusion needs a different, explicit contract.
"""
from history_lineage_cpu_v2 import validate_history,scene_binding,triangles,nearest,vec


def validate_complete_tree(snapshot,records):
    prefix=validate_history(snapshot,records)
    _,packed=scene_binding(snapshot); geometry=triangles(packed)
    children={r['id']:[] for r in records}
    for r in records:
        if r['parent_id'] is not None:children[r['parent_id']].append(r)
    checks=[];terminals=[]
    roles={'mirror':{'mirror'},'bs':{'t','r'},'det':{'detect'},'escape':{'escape'}}
    for r in records:
        successors=children[r['id']]
        if r['event'] in ('detect','escape'):
            if successors:raise ValueError('terminal has children')
            terminals.append(r['id']);continue
        t,pid,owner,_=nearest(vec(r['origin_BU']),vec(r['direction']),geometry,r['primitive_id'])
        name=packed.geometry.object_ids[owner];required=roles[snapshot['objects'][name]['kind']]
        observed={c['event'] for c in successors}
        if observed!=required or len(successors)!=len(required):
            raise ValueError('incomplete tree at record %s: required %s, observed %s' %
                             (r['id'],sorted(required),sorted(observed)))
        if any(c['primitive_id']!=pid for c in successors):raise ValueError('nearest sibling mismatch')
        checks.append({'parent_id':r['id'],'next_primitive_id':pid,'events':sorted(required),
                       't_parameter_exact':[t.numerator,t.denominator]})
    if not terminals:raise ValueError('complete bounded tree requires a terminal')
    return {'schema':'exp005-history-completeness-CPU-v1','scene_binding_sha256':prefix['scene_binding_sha256'],
            'scope':'complete finite exact represented CPU geometric event tree, NOT optical/native completeness',
            'source_ids':[s['id'] for s in snapshot['sources']],'record_count':len(records),
            'terminal_ids':terminals,'branch_checks':checks,'geometric_tree_complete':True,
            'fields_computed':False,'terminal_modes_validated':False,'native_exemption_allowed':False}

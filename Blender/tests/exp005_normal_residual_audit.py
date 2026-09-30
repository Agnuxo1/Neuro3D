"""Exact represented-plane residual replay; diagnostic, NOT native exemption.

Reads one retained peer case and a legitimate parallel-surface control.
No peer writers/imports, no new search and no change to frozen tolerances.
"""
import argparse
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
from exp005_near_origin_audit import vector, sub, dot, cross
from exp005_interval_audit import exact_parameters

ROOT = Path(__file__).parents[2]
PEER_SHA = 'dc67eb8b1625981a701199abed3a3027c0f705312ab3a159a776231f50b0cd94'
PEER_PATH = Path('D:/PROJECTS/.cognition/neuro3d/precision005_claude/e_origin.json')


def plane_offset(triangle, saved_origin, outgoing):
    if len(triangle) != 3: raise ValueError('three-vertex plane required')
    a,b,c = map(vector, triangle)
    point, direction = vector(saved_origin), vector(outgoing)
    n = cross(sub(b,a), sub(c,a))
    if n == (0,0,0): raise ValueError('nondegenerate plane required')
    residual = dot(n, sub(point,a)); denom = dot(n, direction)
    if denom == 0: raise ValueError('parallel direction: no finite plane offset')
    t = -residual/denom
    return {'normal_rational':[pair(v) for v in n], 'residual_rational':pair(residual),
        'direction_projection_rational':pair(denom), 'signed_plane_t_rational':pair(t),
        'signed_plane_t_BU_display':float(t),
        'unit_normal_residual_BU_display':float(residual)/math.sqrt(float(dot(n,n))),
        'scope':'exact represented plane equation only; does not validate triangle hit/history'}


def pair(q): return [q.numerator, q.denominator]


def audit():
    raw = PEER_PATH.read_bytes()
    if hashlib.sha256(raw).hexdigest() != PEER_SHA: raise ValueError('retained annex changed')
    peer = json.loads(raw); a,b = peer['A_local_case'], peer['B_overlap_control']
    tri = [a['vertices'][i] for i in a['triangles'][a['hit_tri']]]
    result = plane_offset(tri,a['point'],a['reflected'])
    rational_hit = exact_parameters(a['point'],a['reflected'],tri)
    if rational_hit is None or result['signed_plane_t_rational'] != pair(rational_hit['t']):
        raise ValueError('plane/Moller identity inconsistent')
    if rational_hit['u'] < 0 or rational_hit['v'] < 0 or rational_hit['u_plus_v'] > 1:
        raise ValueError('retained represented self-hit outside triangle')
    gap = b['legit_surface_z_BU']
    vertices = [[-1.,-1.,gap],[3.,-1.,gap],[3.,1.,gap],[-1.,1.,gap]]
    inside = []
    for pid, face in enumerate(((0,1,2),(0,2,3))):
        tri_q = [vertices[i] for i in face]
        value = exact_parameters(b['hit_point'],b['reflected'],tri_q)
        if value is not None and value['t'] > 0 and value['u'] >= 0 and value['v'] >= 0 and value['u_plus_v'] <= 1:
            inside.append((pid,tri_q,value))
    if not inside:
        raise ValueError('forward inside legitimate surface required')
    pid, qtri, exact_ctrl = min(inside,key=lambda row:row[2]['t'])
    ctrl = plane_offset(qtri,b['hit_point'],b['reflected'])
    ctrl['selected_primitive_id'] = pid
    ctrl['strict_inside_primitive_ids'] = [row[0] for row in inside]
    if ctrl['signed_plane_t_rational'] != pair(exact_ctrl['t']):
        raise ValueError('legitimate plane/triangle parameter mismatch')
    r_t = result['signed_plane_t_BU_display']; peer_t = a['spurious_t_BU']
    return {'scope':'CPU exact residual replay, not native error-bound or repair',
        'input_sha256':{str(PEER_PATH):PEER_SHA}, 'self_hit':result,
        'self_hit_exact_barycentrics':{k:pair(v) for k,v in rational_hit.items()},
        'peer_float_t_BU':peer_t, 'exact_vs_peer_float_t_delta_BU':abs(r_t-peer_t),
        'peer_predicted_t_BU':a['predicted_t_from_residual'],
        'predicted_t_display_delta_BU':abs(r_t-a['predicted_t_from_residual']),
        'unit_normal_residual_display_delta_BU':abs(result['unit_normal_residual_BU_display']-a['normal_residual_exact_BU']),
        'legitimate_parallel_surface':ctrl,
        'band_0_332_would_omit_legitimate_surface':exact_ctrl['t'] < Fraction(.332),
        'native_promotion_allowed':False,
        'limitations':['No validation of selected previous triangle or authenticated optical history',
            'Represented saved point/direction, not a priori GPU error enclosure',
            'Native point export currently insufficient for this exact diagnostic',
            'No snapping, whole-object/plane veto or successful-network certification',
            'One retained self-hit and one synthetic control, no rates or full field comparison']}


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--output',type=Path,required=True)
    args = parser.parse_args(); result = audit()
    files = [Path(__file__),Path(__file__).with_name('test_exp005_normal_residual.py')]
    files += [Path(__file__).with_name(n) for n in ('exp005_near_origin_audit.py','exp005_interval_audit.py')]
    files += [ROOT/'Blender/shaders'/n for n in ('exp005_shared_frontier.glsl','exp005_nearest_v2.glsl')]
    result['code_sha256'] = {str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    with args.output.open('x',encoding='utf-8') as f:
        f.write(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'self_t_BU':result['self_hit']['signed_plane_t_BU_display'],
        'legitimate_t_BU':result['legitimate_parallel_surface']['signed_plane_t_BU_display'],
        'sha256':hashlib.sha256(args.output.read_bytes()).hexdigest()}))


if __name__ == '__main__': main()

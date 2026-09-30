"""NEW synthetic two-cell/three-input fixture, not a Blender runtime result.

The X port of cell a feeds cell b through free space. This is a connected
cascade, not two unrelated copies or a learned matrix hidden in the scene.
Scalar phases and terminal reference planes remain explicit scene properties.
"""
import cmath
import math


def _surface(center, normal, kind):
    norm = math.hypot(*normal)
    n = tuple(v/norm for v in normal)
    tangent = (n[1], -n[0], 0.0)
    vertices = [center]
    for i in range(12):
        angle = 2*math.pi*i/12
        vertices.append(tuple(center[j]+.2*(tangent[j]*math.sin(angle)+
                                (1 if j==2 else 0)*math.cos(angle)) for j in range(3)))
    result = {'kind':kind,'vertices_world_BU':vertices,
              'faces':[(0,i+1,(i+1)%12+1) for i in range(12)]}
    if kind=='mirror': result['phase_rad']=0.0
    if kind=='det': result.update(mode_origin_BU=center,mode_direction=normal)
    return result


def cascade_fixture(phase_a=.2, phase_b=.37, wavelength=.1):
    layout = [('bs1',(0,0,0),(1,-1,0),'bs'),
              ('r1',(2,0,0),(1,-1,0),'mirror'),
              ('r2',(2,.5,0),(1,1,0),'mirror'),
              ('f1',(1,.5,0),(1,1,0),'mirror'),
              ('m2',(0,2,0),(1,-1,0),'mirror'),
              ('bs2',(1,2,0),(1,-1,0),'bs'),
              ('X',(2,2,0),(1,0,0),'det'),
              ('Y',(1,3,0),(0,1,0),'det')]
    objects = {}
    for prefix, offset, phase in [('a',(0,0,0),phase_a),('b',(4,2,0),phase_b)]:
        for name, position, normal, kind in layout:
            if prefix=='a' and name=='X': continue  # open connector, no detector
            center = tuple(v+d for v,d in zip(position,offset))
            record = _surface(center,normal,kind)
            if name=='r1': record['phase_rad']=phase
            objects[f'{prefix}.{name}']=record
    return {'schema':'exp005-readback-v1','lambda_BU':wavelength,'objects':objects,
            'undeclared_meshes':[], 'sources':[
                {'id':'a.row','position_BU':(-1,0,0),'direction':(1,0,0),'field_reim':[1,0]},
                {'id':'a.col','position_BU':(0,-1,0),'direction':(0,1,0),'field_reim':[0,0]},
                {'id':'b.col','position_BU':(4,1,0),'direction':(0,1,0),'field_reim':[0,0]}]}


def closed_form_columns(phase_a=.2, phase_b=.37):
    """Independent ideal MZ composition at lambda=.1 BU, integer connector lengths.

    Columns: a.row, a.col, b.col. Ports: a.Y, b.X, b.Y.
    No triangle tracing, path enumeration, consumer or matrix library called.
    """
    def cell(phase):
        e = cmath.exp(1j*phase)
        return (-.5j*(1+e), .5*(e-1), .5*(1-e), -.5j*(1+e))
    axx,axy,ayx,ayy = cell(phase_a)
    bxx,bxy,byx,byy = cell(phase_b)
    return [(ayx,bxx*axx,byx*axx),
            (ayy,bxx*axy,byx*axy), (0j,bxy,byy)]

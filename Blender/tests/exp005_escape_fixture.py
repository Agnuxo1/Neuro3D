"""New explicit coherent escape boundary; no lost-ray approximation."""
from exp005_cascade_fixture import cascade_fixture

CASES=('base','phase','sham','boundary_shift','reference_shift','lambda')
ESCAPE='b.escape'
SHIFT_BU=.03125


def escape_fixture(case='base'):
    if case not in CASES:
        raise ValueError('unknown escape treatment')
    scene=cascade_fixture(phase_b=.77 if case=='phase' else .37,
                          wavelength=.126 if case=='lambda' else .125,surface='binary_quad')
    boundary=scene['objects'].pop('b.X')
    boundary['kind']='escape'
    if case in ('boundary_shift','reference_shift'):
        boundary['vertices_world_BU']=[(x+SHIFT_BU,y,z) for x,y,z in boundary['vertices_world_BU']]
    if case=='reference_shift':
        x,y,z=boundary['mode_origin_BU']; boundary['mode_origin_BU']=(x+SHIFT_BU,y,z)
    scene['objects'][ESCAPE]=boundary
    return scene

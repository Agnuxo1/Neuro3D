"""New schema-v2 fixtures, preserves all frozen schema-v1 scene files."""
from exp005_escape_fixture import escape_fixture

CASES=('T0','T02','T05','T08','T1','sham','phase')


def splitter_fixture(case='T05'):
    if case not in CASES: raise ValueError('unknown splitter treatment')
    scene=escape_fixture('phase' if case=='phase' else 'base')
    scene['schema']='exp005-readback-v2'
    for record in scene['objects'].values():
        if record['kind']=='bs': record['power_transmittance']=.5
    tau={'T0':0.,'T02':.2,'T05':.5,'T08':.8,'T1':1.,'sham':.5,'phase':.2}[case]
    scene['objects']['b.bs2']['power_transmittance']=tau
    return scene

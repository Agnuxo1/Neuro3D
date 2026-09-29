"""Bounded scalar modal diagnostics; not proof of geometrical orthogonality.

Reconstructs a transfer operator from independent full-scene traces, then traces
every 1+1 / 1+i pair again. Basis intensities alone cannot expose every phase bug.
Registered source/terminal IDs must still be justified as distinct optical modes
by the geometry gate. Diagnostics NEVER promote EXP-005 by themselves.
"""
import copy
import math

from exp005_triangle_oracle import trace_scene


def modal_audit(snapshot, *, tracer=trace_scene, max_rays=4096):
    sources = snapshot['sources']
    if not 1<=len(sources)<=8:
        raise ValueError('bounded audit supports one to eight registered inputs')
    ids = [s['id'] for s in sources]
    if len(set(ids))!=len(ids): raise ValueError('unique source IDs required')
    ports = [n for n,o in snapshot['objects'].items() if o['kind'] in ('det','escape')]
    if not ports: raise ValueError('declared output channels required')

    def probe(amplitudes):
        scene = copy.deepcopy(snapshot)
        for source,amp in zip(scene['sources'],amplitudes):
            source['field_reim'] = [amp.real,amp.imag]
        result = tracer(scene,max_rays=max_rays,max_depth=64)
        if set(result['fields'])!=set(ports):
            raise ValueError('full detected AND escape field set required')
        fields = [complex(result['fields'][n]) for n in ports]
        if any(not math.isfinite(f.real) or not math.isfinite(f.imag) for f in fields):
            raise ValueError('nonfinite traced field')
        return fields

    columns = []
    for i in range(len(sources)):
        amps = [0j]*len(sources); amps[i] = 1+0j
        columns.append(probe(amps))
    gram_error = max(abs(sum(a.conjugate()*b for a,b in zip(columns[i],columns[j]))
                         -(1 if i==j else 0)) for i in range(len(sources))
                         for j in range(len(sources)))
    cases = []
    for i in range(len(sources)):
        for j in range(i+1,len(sources)):
            for phase in (1+0j,1j):
                amps = [0j]*len(sources); amps[i]=1+0j; amps[j]=phase
                measured = probe(amps)
                expected = [a+phase*b for a,b in zip(columns[i],columns[j])]
                cases.append({'sources':[ids[i],ids[j]],'relative_phase':phase,
                    'complex_linearity_error':max(abs(a-b) for a,b in zip(measured,expected)),
                    'conditional_power_error':abs(sum(abs(f)**2 for f in measured)-2)})
    return {'input_ids':ids,'ports':ports,'columns':columns,
            'gram_identity_error':gram_error,'pair_cases':cases,
            'traces':len(columns)+len(cases),
            'worst_pair_complex_error':max((c['complex_linearity_error'] for c in cases),default=0.),
            'worst_pair_conditional_power_error':max((c['conditional_power_error'] for c in cases),default=0.),
            'geometry_gate_passed':False,
            'scope':'conditional scalar diagnostics; source/port orthogonality not proven'}

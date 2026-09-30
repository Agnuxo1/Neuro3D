"""Scene-bound ideal CPU fields over complete reconstructed histories.

One ideal plane-wave mode per terminal; coherence grouping is mandatory.
No spatial overlap, Fresnel, native transport, RT or libm error certificate.
Lengths are reconstructed, not supplied by a backend or fitted matrix.
"""
import cmath
from fractions import Fraction as F
import hashlib
import json
import math
from history_lengths_cpu_v1 import reconstruct_lengths
from history_lineage_cpu_v2 import scene_binding,triangles


def pair(z):
    if not math.isfinite(z.real) or not math.isfinite(z.imag):
        raise ValueError('finite complex field required')
    return [z.real,z.imag]


def ideal_fields(snapshot,records,*,coherence_groups):
    lengths=reconstruct_lengths(snapshot,records)
    binding,packed=scene_binding(snapshot);geom=triangles(packed)
    sources={s['id']:s for s in snapshot['sources']}
    if not isinstance(coherence_groups,dict) or set(coherence_groups)!=set(sources):
        raise ValueError('explicit coherence group for every declared source required')
    if any(not isinstance(g,str) or not g for g in coherence_groups.values()):
        raise ValueError('nonempty coherence group IDs required')
    config={'schema':'exp005-history-fields-CPU-v1','scene_binding_sha256':binding,
            'coherence_groups':coherence_groups,'terminal_model':'one ideal plane-wave mode per terminal'}
    config_sha=hashlib.sha256(json.dumps(config,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    wavelength=F(snapshot['lambda_BU']);amplitudes={};ledger=[]
    terminal_lengths={row['id']:row for row in lengths['terminals']}
    grouped={port:{g:[] for g in sorted(set(coherence_groups.values()))} for port in packed.ports}
    for record in records:
        rid=record['id'];event=record['event'];sid=record['source_id']
        if record['parent_id'] is None:
            z=complex(*sources[sid]['field_reim'])
        else:
            z=amplitudes[record['parent_id']]
            owner=geom[record['primitive_id']][0];name=packed.geometry.object_ids[owner]
            obj=snapshot['objects'][name]
            if event=='mirror':z*=-cmath.exp(1j*obj['phase_rad'])
            if event in ('t','r'):
                tau=packed.optics[owner*12+1]
                z*=math.sqrt(tau) if event=='t' else 1j*math.sqrt(1-tau)
        pair(z);amplitudes[rid]=z
        if event not in ('detect','escape'):continue
        info=terminal_lengths[rid];effective=info['effective_length']
        lo=F(*effective['rational_lower']);hi=F(*effective['rational_upper'])
        # Exact rational modulo before float conversion; sqrt enclosure midpoint
        # remains an approximation when path lengths are irrational.
        turns=(lo+hi)/(2*wavelength)
        reduced=turns-((turns+F(1,2))//1)
        field=z*cmath.exp(1j*math.tau*float(reduced));pair(field)
        group=coherence_groups[sid];port=info['port'];grouped[port][group].append(field)
        ledger.append({'id':rid,'source_id':sid,'coherence_group':group,'port':port,
                       'amplitude_before_propagation':pair(z),'effective_length':effective,
                       'reduced_turns_midpoint':[reduced.numerator,reduced.denominator],
                       'ideal_length_phase_span_turns':[(hi-lo).numerator*wavelength.denominator,
                                                       (hi-lo).denominator*wavelength.numerator],
                       'field_reim':pair(field)})
    outputs={}
    for port,groups in grouped.items():
        sums={}
        for group,values in groups.items():
            total=complex(math.fsum(z.real for z in values),math.fsum(z.imag for z in values))
            sums[group]={'field_reim':pair(total),'intensity':abs(total)**2,'path_count':len(values)}
            if not math.isfinite(sums[group]['intensity']):raise ValueError('finite intensity required')
        intensity=math.fsum(g['intensity'] for g in sums.values())
        if not math.isfinite(intensity):raise ValueError('finite total intensity required')
        outputs[port]={'groups':sums,'intensity':intensity}
    return {**config,'configuration_sha256':config_sha,'ledger':ledger,'ports':outputs,
            'scope':'ideal digital CPU reference with explicit coherence; NOT native/physical validation',
            'fields_computed_on':'CPU Python standard-library complex arithmetic',
            'native_precision_certified':False,'phase_error_certified':False,
            'spatial_overlap_validated':False,'native_exemption_allowed':False}

"""Restricted input-word reference enclosures. CPU only; no phase or gate promotion."""
import base64
from copy import deepcopy
import json
import struct
import axial_native_events_v1 as events
import axial_native_signed512_v1 as limb

MODEL='axial-fixed-original-reference-enclosures-16limb-CPU-v1'
REFERENCE_MODEL='axial-fixed-original-terminal-plane-reference-CPU-v1'
FRAME='fixed original world point; ideal unit-X plane-wave mode'

def _words(raw):
    limb.require(len(raw)%4==0,'whole uint32 words')
    return list(struct.unpack('<'+'I'*(len(raw)//4),raw))

def enclosure(pair,radius):
    center=limb.decode_hilo(pair);limb.valid(radius)
    limb.require(not limb.negative(radius),'nonnegative radius')
    return [limb.sub(center,radius),limb.add(center,radius)]

def combine_intervals(m,s,d,r,sign):
    """Scaled BU*2^149, signed reference allowed. SAME D cancels exactly."""
    limb.require(type(sign) is int and sign in (-1,1),'signed unit X sign')
    for interval in (m,s,d,r):
        limb.require(type(interval) is list and len(interval)==2,'two endpoints')
        limb.valid(interval[0]);limb.valid(interval[1])
        limb.require(limb.compare(*interval)<=0,'ordered interval')
    two=[2]+[0]*15
    def length(endpoint):
        low=limb.sub(limb.sub(limb.mul(two,m[0]),s[1]),endpoint[1])
        high=limb.sub(limb.sub(limb.mul(two,m[1]),s[0]),endpoint[0])
        return [low,high] if sign>0 else [limb.negate(high),limb.negate(low)]
    geom=length(d);reference=length(r)
    correction=[limb.sub(d[0],r[1]),limb.sub(d[1],r[0])]
    if sign<0:correction=[limb.negate(correction[1]),limb.negate(correction[0])]
    independent=[limb.add(geom[0],correction[0]),limb.add(geom[1],correction[1])]
    return {'geometric_length_interval_words':geom,'reference_correction_interval_words':correction,
            'effective_reference_length_interval_words':reference,'independent_sum_NOT_used_words':independent,
            'correlated_variable_cancelled':'same terminal X variable D, not independent interval sum'}

def audit_reference(name,packet,expected_packet_sha256):
    """Exact-YZ +/-X profile, frozen HOST reference consumed; no new encoding."""
    geometry=events.trace_scene(name,packet,expected_packet_sha256)
    buffers={k:base64.b64decode(v,validate=True) for k,v in packet['buffers_base64'].items()}
    meta=json.loads(buffers['input_metadata_json']);refmeta=meta['reference']
    limb.require(refmeta['model']==REFERENCE_MODEL and refmeta['frame']==FRAME,'fixed original reference frame')
    rw=_words(buffers['reference']);ww=_words(buffers['wavelength'])
    limb.require(len(rw) in (13,31) and type(rw[0]) is int and rw[0] in (0,1),'reference layout')
    available=rw[0]==1
    limb.require(len(rw)==(31 if available else 13),'reference flag stride')
    limb.require(packet['manifest']['layout']['reference']=={'HOST_encoding_available':available,'words':len(rw)},'reference manifest')
    limb.require((refmeta['HOST_reference_ABI'] is not None)==available,'HOST reference availability')
    limb.require(rw[7]==0 and rw[8] in (0x3ff00000,0xbff00000) and
                 all(rw[j]==0 and rw[j+1] in (0,0x80000000) for j in (9,11)),'original64 axial unit mode bits')
    mode_sign=-1 if rw[8]==0xbff00000 else 1
    limb.require(refmeta['direction']==[[mode_sign,1],[0,1],[0,1]],'original mode metadata direction')
    limb.require(len(ww)==18,'wavelength stride')
    wavelength=enclosure(ww[:2],ww[2:18])
    limb.require(limb.compare(wavelength[0],limb.ZERO)>0,'positive wavelength enclosure')
    reference=None
    if available:
        limb.require(refmeta['HOST_reference_ABI']['uint32_hilo']==rw[13:15],'reference HOST input words')
        reference=enclosure(rw[13:15],rw[15:31])
    # Reconstruct D from input triangles, not from retained output answers.
    tw=_words(buffers['triangles']);detector=None
    for start in range(0,len(tw),35):
        t=tw[start:start+35]
        if t[0]==1:
            interval=enclosure(t[1:3],t[19:35])
            limb.require(detector is None or detector==interval,'same terminal plane')
            detector=interval
    limb.require(detector is not None,'terminal owner required')
    sw=_words(buffers['sources']);rows=[];binding=geometry['scene_binding_sha256']
    for i,g in enumerate(geometry['sources']):
        sid=g['source_id']
        row={'source_id':sid,'geometry':deepcopy(g),'reference_bounds_evaluated_CPU_only':False,
             'accepted_terminal_reference_CPU_only':False,'phase_evaluated':False,
             'original_phase_budget_rad':deepcopy(meta['original_path_phase_caps'][sid]),
             'source_phase_reference_id':'original-source-zero:'+binding+':'+sid,
             'terminal_reference_id':'fixed-original-plane-mode:'+binding+':D'}
        if not g['accepted_axial_two_event_geometry_CPU_only']:
            row['reason']=g['reason']
        elif not available:
            row['reason']='HOST reference absent; no new encoder or default reference'
        else:
            try:
                sign=g['direction_sign']
                limb.require(mode_sign==-sign,'mode must follow reflected axial ray')
                cert=g['departure_certificate']
                limb.require(cert['owner']==0 and cert['source_id']==sid and cert['input_packet_sha256']==expected_packet_sha256,'derived mirror receipt')
                source=sw[32*i:32*(i+1)]
                intervals=combine_intervals(cert['shared_plane_interval_words'],enclosure(source[:2],source[12:28]),detector,reference,sign)
                limb.require(intervals['geometric_length_interval_words']==g['length_interval_words'],'same geometric length')
                row.update(intervals,reference_bounds_evaluated_CPU_only=True,
                           wavelength_interval_words=deepcopy(wavelength),reference_X_interval_words=deepcopy(reference))
            except ValueError as error:row['reason']=str(error)
        rows.append(row)
    return {'model':MODEL,'case_name':name,'input_packet_sha256':expected_packet_sha256,
            'scene_binding_sha256':binding,'word_ABI_sha256':geometry['word_ABI_sha256'],
            'source_order':list(geometry['source_order']),'sources':rows,
            'reference_frame':FRAME,'original_mode_point_binary64_words':rw[1:7],
            'original_mode_direction_binary64_words':rw[7:13],'HOST_reference_available':available,
            'new_HOST_RN32_encodings':0,'new_HOST_RN64_subtractions':0,
            'reference_bounds_evaluated_CPU_only':all(r['reference_bounds_evaluated_CPU_only'] for r in rows),
            'accepted_terminal_reference_CPU_only':False,'phase_evaluated':False,
            'accepted_complete_geometry':False,'accepted_full_field_pipeline':False,
            'GLSL_compiled':False,'GPU_executed':False,'GPU_job_admission':False}

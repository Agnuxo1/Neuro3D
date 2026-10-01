"""Opt-in original64 input overlay and restricted scene reference phase-bound CPU gate.
HOST serialization is explicit, not native evidence. No trig/field/GPU admission.
"""
import base64
from copy import deepcopy
import hashlib
import json
import struct
import axial_native_signed512_v1 as limb
import axial_native_reference_v1 as reference

def canon(x):
    return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()

MASK=0xffffffff
def require(ok,reason):
    if not ok:raise ValueError(reason)
def decode64_scaled(pair):
    """CPU word implementation only. ORIGINAL64 -> exact signed512 BU*2^149; no rounding."""
    require(type(pair) is list and len(pair)==2 and
            all(type(w) is int and 0<=w<=MASK for w in pair),'two original64 uint32 words')
    low,high=pair;exponent=(high>>20)&2047
    require(exponent!=2047,'finite original64')
    if exponent==0:
        require(low==0 and (high&0xfffff)==0,'subnormal original64 off fixed grid; no FTZ')
        return [0]*16
    require(exponent<=1385,'signed512 original64 magnitude overflow')
    parts=[low,(high&0xfffff)|0x100000]
    shift=exponent-926
    if shift<0:
        cut=-shift
        require(cut<=52,'original64 off BU*2^-149 grid')
        if cut>=32:
            require(parts[0]==0 and (parts[1]&((1<<(cut-32))-1))==0,'original64 off BU*2^-149 grid')
            parts=[parts[1]>>(cut-32),0]
        else:
            require((parts[0]&((1<<cut)-1))==0,'original64 off BU*2^-149 grid')
            parts=[((parts[0]>>cut)|(parts[1]<<(32-cut)))&MASK,parts[1]>>cut]
        shift=0
    out=[0]*16;slot,offset=divmod(shift,32)
    for i,chunk in enumerate(parts):
        if not chunk:continue
        require(slot+i<16,'signed512 original64 magnitude overflow')
        out[slot+i]|=(chunk<<offset)&MASK
        if offset:
            carry=chunk>>(32-offset)
            if carry:
                require(slot+i+1<16,'signed512 original64 magnitude overflow')
                out[slot+i+1]|=carry
    negative=bool(high&0x80000000)
    require(out[15]<0x80000000 or
            (negative and out[15]==0x80000000 and not any(out[:15])),
            'signed512 original64 sign overflow')
    if negative:
        carry=1
        for i,w in enumerate(out):
            total=(w^MASK)+carry;out[i]=total&MASK;carry=total>>32
    return out

def phase_corner_predicate(encoded_L,encoded_lambda,original_L,original_lambda,budget_numerator,budget_denominator):
    """Opt-in CPU predicate for 8*cycle-error<=p/q; no phase field or backend."""
    for value in (encoded_L,encoded_lambda,original_L,original_lambda,budget_numerator,budget_denominator):
        limb.valid(value)
    limb.require(limb.compare(encoded_lambda,limb.ZERO)>0 and
                 limb.compare(original_lambda,limb.ZERO)>0,'positive wavelength')
    limb.require(limb.compare(budget_numerator,limb.ZERO)>=0 and
                 limb.compare(budget_denominator,limb.ZERO)>0,'nonnegative rational cap with positive denominator')
    difference=limb.sub(limb.mul(encoded_L,original_lambda),limb.mul(original_L,encoded_lambda))
    magnitude=limb.negate(difference) if limb.negative(difference) else difference
    denominator=limb.mul(encoded_lambda,original_lambda)
    left=limb.mul([8]+[0]*15,limb.mul(magnitude,budget_denominator))
    right=limb.mul(budget_numerator,denominator)
    return {'bound_predicate_PASS':limb.compare(left,right)<=0,
            'cycle_difference_numerator_words':magnitude,'cycle_difference_denominator_words':denominator,
            'cross_left_words':left,'cross_right_words':right}

def original_cap_overlay_HOST_only(name,parent,expected_parent_sha256):
    """Opt-in input-only HOST overlay; unchanged parent, no native/GPU claim."""
    def need(ok,reason):
        if not ok:raise ValueError(reason)
    need(hashlib.sha256(canon(parent)).hexdigest()==expected_parent_sha256,'parent receipt')
    need(parent['manifest']['case_name']==name,'case identity')
    buffers={k:base64.b64decode(v,validate=True) for k,v in parent['buffers_base64'].items()}
    for k,v in buffers.items():
        need(parent['manifest']['buffers'][k]=={'bytes':len(v),'sha256':hashlib.sha256(v).hexdigest()},'parent buffer receipt')
    metadata=json.loads(buffers['input_metadata_json']);original=json.loads(buffers['original_scene_json'])
    need(metadata['original_snapshot_sha256']==hashlib.sha256(buffers['original_scene_json']).hexdigest(),'original snapshot binding')
    need(metadata['source_order']==[s['id'] for s in original['sources']],'original source order')
    need(1<=len(original['sources'])<=64,'bounded sources')
    def pair(v):
        need(type(v) is float,'original64 JSON float type')
        packed=struct.pack('<d',v);w=list(struct.unpack('<II',packed))
        decode64_scaled(w) # exact grid/range validation, NO stored length/gate result
        return packed
    for key in ('M','D'):
        xs=[pair(v[0]) for v in original['objects'][key]['vertices_world_BU']]
        need(bool(xs) and all(x==xs[0] for x in xs),'shared original X plane')
    values=[original['objects']['M']['vertices_world_BU'][0][0],
            original['objects']['D']['vertices_world_BU'][0][0],
            original['objects']['D']['mode_origin_BU'][0],original['lambda_BU']]
    values += [s['position_BU'][0] for s in original['sources']]
    axes=b''.join(pair(v) for v in values)
    def unsigned_integer_words(n):
        need(type(n) is int and 0<=n<2**511,'nonnegative bounded rational integer')
        return b''.join(struct.pack('<I',(n>>(32*i))&0xffffffff) for i in range(16))
    records=[];available=absent=0
    for sid in metadata['source_order']:
        cap=metadata['original_path_phase_caps'][sid]
        if cap is None:
            records.append(struct.pack('<I',0)+bytes(128));absent+=1
        else:
            need(type(cap) is list and len(cap)==2 and type(cap[1]) is int and cap[1]>0,'positive rational cap denominator')
            records.append(struct.pack('<I',1)+unsigned_integer_words(cap[0])+unsigned_integer_words(cap[1]));available+=1
    caps=b''.join(records)
    return {'schema':'axial-original64-rational-cap-HOST-input-overlay-v1',
            'scope':'HOST input transport only; not native evidence, inference, phase, backend or GPU admission',
            'case_name':name,'parent_input_packet_sha256':expected_parent_sha256,
            'parent_word_ABI_sha256':metadata['word_ABI_sha256'],
            'original_snapshot_sha256':metadata['original_snapshot_sha256'],
            'scene_binding_sha256':metadata['scene_binding_sha256'],
            'source_order':list(metadata['source_order']),
            'axes_layout':'ORIGINAL64 little-endian M.X,D.X,R.X,lambda then ordered source X',
            'cap_layout':'per-source flag uint32; numerator16+denominator16 uint32; flag0 reserved zeros NOT cap0',
            'buffers_base64':{'original64_axes':base64.b64encode(axes).decode(),'original_rational_caps':base64.b64encode(caps).decode()},
            'buffer_receipts':{k:{'bytes':len(v),'sha256':hashlib.sha256(v).hexdigest()} for k,v in (('original64_axes',axes),('original_rational_caps',caps))},
            'HOST_reference_availability_preserved':metadata['reference']['HOST_reference_ABI'] is not None,
            'cap_records_available':available,'cap_records_absent':absent,
            'new_HOST_RN32_encodings':0,'new_HOST_RN64_subtractions':0,
            'phase_evaluated':False,'accepted_full_field_pipeline':False,'GPU_executed':False,'GPU_job_admission':False}

def read_original_cap_overlay_HOST_only(name,overlay,expected_overlay_sha256,parent,expected_parent_sha256):
    """Opt-in HOST semantic validation/readback, NOT native execution evidence."""
    def need(ok,reason):
        if not ok:raise ValueError(reason)
    need(hashlib.sha256(canon(parent)).hexdigest()==expected_parent_sha256,'parent receipt')
    need(hashlib.sha256(canon(overlay)).hexdigest()==expected_overlay_sha256,'overlay receipt')
    need(parent['manifest']['case_name']==overlay['case_name']==name,'case identity')
    need(overlay['schema']=='axial-original64-rational-cap-HOST-input-overlay-v1','overlay schema')
    need(overlay['parent_input_packet_sha256']==expected_parent_sha256,'same parent binding')
    pb={k:base64.b64decode(v,validate=True) for k,v in parent['buffers_base64'].items()}
    for key,value in pb.items():
        need(parent['manifest']['buffers'][key]=={'bytes':len(value),'sha256':hashlib.sha256(value).hexdigest()},'parent buffer receipt')
    meta=json.loads(pb['input_metadata_json']);original=json.loads(pb['original_scene_json'])
    need(meta['original_snapshot_sha256']==hashlib.sha256(pb['original_scene_json']).hexdigest(),'original snapshot receipt')
    need(meta['source_order']==[s['id'] for s in original['sources']],'original source order')
    for key in ('original_snapshot_sha256','scene_binding_sha256'):
        need(overlay[key]==meta[key],'original scene binding')
    need(overlay['parent_word_ABI_sha256']==meta['word_ABI_sha256'],'parent word ABI')
    need(type(overlay['source_order']) is list and overlay['source_order']==meta['source_order'],'source order')
    n=len(meta['source_order']);need(1<=n<=64,'bounded source count')
    need(overlay['axes_layout']=='ORIGINAL64 little-endian M.X,D.X,R.X,lambda then ordered source X','axes layout')
    need(overlay['cap_layout']=='per-source flag uint32; numerator16+denominator16 uint32; flag0 reserved zeros NOT cap0','cap layout')
    need(set(overlay['buffers_base64'])==set(overlay['buffer_receipts'])=={'original64_axes','original_rational_caps'},'input-only buffer roles')
    buffers={k:base64.b64decode(v,validate=True) for k,v in overlay['buffers_base64'].items()}
    for key,value in buffers.items():
        need(overlay['buffer_receipts'][key]=={'bytes':len(value),'sha256':hashlib.sha256(value).hexdigest()},'overlay buffer receipt')
    axes=buffers['original64_axes'];caps=buffers['original_rational_caps']
    need(len(axes)==8*(4+n) and len(caps)==132*n,'overlay strides')
    vals=[original['objects']['M']['vertices_world_BU'][0][0],original['objects']['D']['vertices_world_BU'][0][0],
          original['objects']['D']['mode_origin_BU'][0],original['lambda_BU']]+[s['position_BU'][0] for s in original['sources']]
    # Explicit HOST validation serializations; not free native comparisons.
    for i,value in enumerate(vals):
        need(type(value) is float and axes[8*i:8*(i+1)]==struct.pack('<d',value),'exact original64 bytes')
    pairs=[list(struct.unpack('<II',axes[8*i:8*(i+1)])) for i in range(4+n)]
    decoded=[decode64_scaled(p) for p in pairs]
    rows=[];available=absent=0
    for i,sid in enumerate(meta['source_order']):
        w=list(struct.unpack('<33I',caps[132*i:132*(i+1)]));flag=w[0];prior=meta['original_path_phase_caps'][sid]
        need(flag in (0,1),'cap presence flag')
        if flag==0:
            need(prior is None and not any(w[1:]),'absent cap reserved zeros; NOT cap0')
            cap=None;absent+=1
        else:
            need(type(prior) is list and len(prior)==2 and all(type(q) is int for q in prior) and prior[0]>=0 and prior[1]>0,'declared rational cap')
            num=sum(v<<(32*j) for j,v in enumerate(w[1:17]));den=sum(v<<(32*j) for j,v in enumerate(w[17:33]))
            need(num<2**511 and 0<den<2**511 and [num,den]==prior,'exact original rational cap')
            cap={'numerator_words':w[1:17],'denominator_words':w[17:33]};available+=1
        rows.append({'source_id':sid,'original_source_X_words':decoded[4+i],'original_phase_cap':cap})
    for key,value in (('cap_records_available',available),('cap_records_absent',absent)):
        need(type(overlay[key]) is int and overlay[key]==value,'cap counts')
    need(type(overlay['HOST_reference_availability_preserved']) is bool and
         overlay['HOST_reference_availability_preserved']==(meta['reference']['HOST_reference_ABI'] is not None),'same HOST reference availability')
    for key in ('phase_evaluated','accepted_full_field_pipeline','GPU_executed','GPU_job_admission'):need(overlay[key] is False,'no promotion flags')
    for key in ('new_HOST_RN32_encodings','new_HOST_RN64_subtractions'):need(type(overlay[key]) is int and overlay[key]==0,'no hi-lo encoder claim')
    return {'case_name':name,'overlay_sha256':expected_overlay_sha256,'parent_input_packet_sha256':expected_parent_sha256,
            'original_M_X_words':decoded[0],'original_D_X_words':decoded[1],
            'original_R_X_words':decoded[2],'original_lambda_words':decoded[3],'sources':rows,
            'HOST_reference_available':overlay['HOST_reference_availability_preserved'],
            'phase_evaluated':False,'accepted_full_field_pipeline':False,'GPU_executed':False,'GPU_job_admission':False}


def audit_scene_original_phase(name,parent,parent_sha256,overlay,overlay_sha256):
    """Fresh own scene events/reference; never substitutes retained answer lookup."""
    original=read_original_cap_overlay_HOST_only(name,overlay,overlay_sha256,parent,parent_sha256)
    ref=reference.audit_reference(name,parent,parent_sha256)
    require(ref['source_order']==[s['source_id'] for s in original['sources']],'same source identities')
    rows=[]
    for before,src in zip(ref['sources'],original['sources']):
        row={'source_id':src['source_id'],'reference':deepcopy(before),
             'phase_bound_predicate_evaluated_CPU_only':False,
             'accepted_reference_phase_bound_CPU_only':False,
             'phase_unit_evaluated':False,'accepted_full_field_pipeline':False}
        if not before['reference_bounds_evaluated_CPU_only']:
            row['reason']=before['reason']
        elif src['original_phase_cap'] is None:
            row['reason']='original phase cap absent; no numerical zero default'
        else:
            try:
                # ORIGINAL reference, not terminal D. Signed effective length allowed.
                length=limb.sub(limb.sub(limb.mul([2]+[0]*15,original['original_M_X_words']),
                                        src['original_source_X_words']),original['original_R_X_words'])
                sign=before['geometry']['direction_sign']
                if sign<0:length=limb.negate(length)
                cap=src['original_phase_cap'];corners=[]
                for e in before['effective_reference_length_interval_words']:
                    for wavelength in before['wavelength_interval_words']:
                        corners.append(phase_corner_predicate(e,wavelength,length,original['original_lambda_words'],
                                       cap['numerator_words'],cap['denominator_words']))
                row.update(original_effective_reference_length_words=length,
                           original_lambda_words=deepcopy(original['original_lambda_words']),
                           original_phase_cap=deepcopy(cap),corners=corners,
                           phase_bound_predicate_evaluated_CPU_only=True,
                           accepted_reference_phase_bound_CPU_only=all(c['bound_predicate_PASS'] for c in corners))
                if not row['accepted_reference_phase_bound_CPU_only']:
                    row['reason']='conservative reference phase error bound exceeds unchanged original cap'
            except ValueError as error:
                row['reason']=str(error)
        rows.append(row)
    return {'model':'axial-original64-scene-reference-phase-bound-16limb-CPU-v1',
            'case_name':name,'input_packet_sha256':parent_sha256,'overlay_sha256':overlay_sha256,
            'scene_binding_sha256':ref['scene_binding_sha256'],'word_ABI_sha256':ref['word_ABI_sha256'],
            'source_order':list(ref['source_order']),'HOST_original_inputs':original,'sources':rows,
            'reference_frame':ref['reference_frame'],'conservative_two_pi_upper_integer':8,
            'HOST_reference_available':ref['HOST_reference_available'],
            'phase_bound_predicate_evaluated_CPU_only':all(r['phase_bound_predicate_evaluated_CPU_only'] for r in rows),
            'accepted_reference_phase_bound_CPU_only':all(r['accepted_reference_phase_bound_CPU_only'] for r in rows),
            'fresh_dependency_recomputation':'own EVENTS/YZ/X/reference reused as fresh computation; redundant work charged, no old suites',
            'phase_unit_evaluated':False,'accepted_full_field_pipeline':False,'accepted_complete_geometry':False,
            'GLSL_compiled':False,'GPU_executed':False,'GPU_job_admission':False,'execution_authenticated':False}

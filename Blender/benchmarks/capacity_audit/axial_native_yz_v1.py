"""Opt-in strict YZ projection CPU component from pinned exact-YZ input words.

No float/Fraction/big-signed arithmetic in this component. Not general 3D,
YZ uncertainty propagation, event selection, phase or GPU geometry.
"""
import base64
import hashlib
import json
import struct
import axial_native_signed512_v1 as limb

MODEL='axial-YZ-strict-signed512-CPU-component-v1'

def cross(ay,az,by,bz):
    return limb.sub(limb.mul(ay,bz),limb.mul(az,by))

def classify_triangle(a,b,c,p):
    """a,b,c,p are YZ pairs of signed512 words; strict boundary, no snap."""
    for point in (a,b,c,p):
        limb.require(type(point) is list and len(point)==2,'YZ pair')
        for coordinate in point:limb.valid(coordinate)
    by,bz=limb.sub(b[0],a[0]),limb.sub(b[1],a[1])
    cy,cz=limb.sub(c[0],a[0]),limb.sub(c[1],a[1])
    py,pz=limb.sub(p[0],a[0]),limb.sub(p[1],a[1])
    det=cross(by,bz,cy,cz)
    if limb.compare(det,limb.ZERO)==0:
        return {'classification':'degenerate_FAIL','det_u_v_w_words':None}
    u,v=cross(py,pz,cy,cz),cross(by,bz,py,pz)
    if limb.negative(det):det,u,v=limb.negate(det),limb.negate(u),limb.negate(v)
    w=limb.sub(limb.sub(det,u),v)
    signs=[limb.compare(value,limb.ZERO) for value in (u,v,w)]
    kind='miss' if min(signs)<0 else ('boundary_FAIL' if min(signs)==0 else 'strict_interior')
    return {'classification':kind,'det_u_v_w_words':[det,u,v,w]}

def coverage(name,packet,expected_packet_sha256):
    """Caller pins the original exact-YZ profile; SHA is not authentication."""
    canonical=json.dumps(packet,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
    limb.require(hashlib.sha256(canonical).hexdigest()==expected_packet_sha256,'pinned input packet SHA')
    manifest=packet['manifest'];limb.require(manifest['case_name']==name,'case identity')
    buffers={k:base64.b64decode(v,validate=True) for k,v in packet['buffers_base64'].items()}
    for key,raw in buffers.items():
        limb.require(manifest['buffers'][key]=={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()},'input receipt')
    meta=json.loads(buffers['input_metadata_json']);ids=meta['source_order']
    limb.require(meta['object_ids']==['M','D'] and meta['kinds']==['mirror','det'],'M-D owner profile')
    limb.require(type(ids) is list and 1<=len(ids)<=3 and len(set(ids))==len(ids)
                 and all(type(s) is str and s for s in ids),'bounded ordered unique source IDs')
    def words(raw):
        limb.require(len(raw)%4==0,'uint32 byte alignment')
        return list(struct.unpack('<'+'I'*(len(raw)//4),raw))
    tw,sw=words(buffers['triangles']),words(buffers['sources'])
    limb.require(len(tw)%35==0 and 1<=len(tw)//35<=64,'bounded triangle stride')
    limb.require(len(sw)==32*len(ids),'source stride')
    triangles=[]
    for pid,start in enumerate(range(0,len(tw),35)):
        row=tw[start:start+35];owner=row[0]
        limb.require(owner in (0,1),'owner slot')
        # X radius is not a YZ uncertainty: exact-YZ ABI profile only.
        yz=[[limb.decode_hilo(row[j+2:j+4]),limb.decode_hilo(row[j+4:j+6])] for j in (1,7,13)]
        triangles.append((pid,owner,yz))
    rows=[];unit=limb.decode32_scaled(0x3f800000)
    for i,sid in enumerate(ids):
        row=sw[32*i:32*(i+1)]
        direction=[limb.decode_hilo(row[j:j+2]) for j in (6,8,10)]
        limb.require(direction[0] in (unit,limb.negate(unit)) and direction[1:]==[limb.ZERO,limb.ZERO],'signed unit axial X')
        p=[limb.decode_hilo(row[j:j+2]) for j in (2,4)]
        records=[];interior=[];misses=[];failures=[]
        for pid,owner,yz in triangles:
            result=classify_triangle(*yz,p)
            records.append({'primitive_id':pid,'owner':owner,**result})
            if result['classification']=='strict_interior':interior.append([pid,owner])
            elif result['classification']=='miss':misses.append(pid)
            else:failures.append({'primitive_id':pid,'reason':result['classification']})
        rows.append({'source_id':sid,'triangles':records,'strict_interior_primitive_owner':interior,
                     'projected_misses':misses,'projection_failures':failures,
                     'accepted_YZ_projection_component_CPU_only':not failures,
                     'accepted_complete_geometry':False,'event_selection_implemented':False})
    return {'model':MODEL,'case_name':name,'input_packet_sha256':expected_packet_sha256,
            'scene_binding_sha256':meta['scene_binding_sha256'],'word_ABI_sha256':meta['word_ABI_sha256'],
            'source_order':ids,'sources':rows,'profile':'retained-exact-YZ-axial-X-only',
            'YZ_uncertainty_implemented':False,'event_selection_implemented':False,
            'accepted_complete_geometry':False,'accepted_full_field_pipeline':False,
            'phase_evaluated':False,'GLSL_compiled':False,'GPU_executed':False,'GPU_job_admission':False}

"""Scene-word length to RN32 quotient and checked selector: opt-in CPU only."""
import base64
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import zlib
from axial_geometry_words_cpu_v1 import checked as checked512,word512
from axial_selector_int256_cpu_v1 import decode32_scaled,checked as checked256,pack,host_radius,select_words,MODEL as SELECTOR
from axial_phase_quotient_cpu_v1 import quotient_words,MODEL as QUOTIENT
from axial_hilo_terminal_cpu_v1 import encode_hilo
from axial_relative_gate_cpu_v1 import ratio

ROOT=Path(__file__).resolve().parents[3]
REPORT='coordinacion/respuestas/AXIAL-GEOMETRY-WORDS-001-CODEX.json'
SHA='dfdb03a27f7aaa58dd05d750ea1980de789281ed798b75fd2c5209d12712a5fa'
MODEL='scene-geometry-words-to-5rn32-selector256-CPU-v1'
S=1<<149

def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()

def load_retained():
    raw=(ROOT/REPORT).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SHA:raise ValueError('scene geometry report SHA mismatch')
    r=json.loads(raw)
    if r['id']!='AXIAL-GEOMETRY-WORDS-001' or r['test_run']['rc']!=0:raise ValueError('retained scene geometry identity/status mismatch')
    for n,h in r['code_doc_sha256'].items():
        if hashlib.sha256((ROOT/n).read_bytes()).hexdigest()!=h:raise ValueError('changed frozen input '+n)
    run=r['test_run'];raw=zlib.decompress(base64.b64decode(run['stdout_zlib_base64'],validate=True))
    if len(raw)!=run['stdout_bytes'] or hashlib.sha256(raw).hexdigest()!=run['stdout_sha256']:raise ValueError('geometry raw payload SHA mismatch')
    return dict(r['code_doc_sha256'],**{REPORT:SHA}),json.loads(raw)['cases']

def bridge_case(c,*,case_sha256,bridge_model):
    if bridge_model!=MODEL:raise ValueError('explicit new scene geometry bridge CPU model required')
    if digest(c)!=case_sha256:raise ValueError('retained geometry case digest mismatch')
    b=c['word_ABI'];scene=c['scene_snapshot'];ids=b['source_order']
    if digest(b)!=c['word_ABI_sha256']:raise ValueError('geometry ABI binding mismatch')
    binding={'snapshot':scene,'object_order':b['object_ids'],'source_order':ids}
    if digest(binding)!=b['original_scene_binding_sha256']:raise ValueError('original scene binding mismatch')
    if ids!=[s['source_id'] for s in b['sources']] or ids!=[s['id'] for s in scene['sources']] or ids!=[r['source_id'] for r in c['sources']] or len(set(ids))!=len(ids):raise ValueError('complete ordered unique source coverage required')
    out={'geometry_case_sha256':case_sha256,'word_ABI_sha256':c['word_ABI_sha256'],
         'original_scene_binding_sha256':b['original_scene_binding_sha256'],
         'previous_geometry_accepted':c['accepted_geometry_words_CPU_only'],
         'previous_phase_accepted':c['accepted_phase_budget_CPU_only'],
         'accepted_bridge_phase_CPU_only':False,'paths':[],'quotient_RN32_operations':0,
         'HOST_length_encoding_RN32_operations':0,'new_length_integer_operations':0,'selector_integer_operations':0,
         'retained_geometry_nodes_NOT_executed':c['integer_operations'],'geometry_or_producer_rerun':False}
    def decode(words):return checked512(sum(map(decode32_scaled,words)))
    planes={}
    for t in b['triangles']:
        p=(decode(t['vertices_uint32_hilo'][0][0]),t['X_radius_scaled'])
        if t['owner'] in planes and planes[t['owner']]!=p:raise ValueError('shared plane mismatch')
        planes[t['owner']]=p
    wavelength_center=decode(b['wavelength_uint32_hilo']);wr=b['wavelength_radius_scaled']
    highword=b['wavelength_uint32_hilo'][0];w=F(decode32_scaled(highword),S);wc=F(wavelength_center,S)
    if w<=0 or wavelength_center-wr<=0:raise ValueError('positive high32 and full wavelength enclosure required')
    for src,original,g in zip(b['sources'],scene['sources'],c['sources']):
        row={'source_id':g['source_id'],'previous_geometry_accepted':g['accepted_geometry_words_CPU_only'],
             'previous_phase_accepted':g['accepted_phase_budget_CPU_only'],'arithmetic_evaluated':False,
             'accepted_bridge_phase_CPU_only':False}
        out['paths'].append(row)
        if not g['accepted_geometry_words_CPU_only']:
            row['reason']='retained geometry rejection; no quotient/selector';continue
        reference='original-source-zero:'+b['original_scene_binding_sha256']+':'+g['source_id']
        if g['phase_reference_id']!=reference:raise ValueError('original source gauge mismatch')
        sign=g['direction_sign'];mi=g['mirror_owner'];di=g['terminal_owner']
        origin=decode(src['origin_uint32_hilo'][0]);mc,mr=planes[mi];dc,dr=planes[di];sr=src['X_radius_scaled']
        trace=[]
        def op(a,b,kind,label):
            v=checked512(a*b if kind=='mul' else a-b)
            trace.append({'label':label,'op':kind,'inputs_signed512_words':[word512(a),word512(b)],'output_signed512_words':word512(v)})
            return v
        center=op(op(op(2,mc,'mul','length.center.2M'),origin,'sub','length.center.minusS'),dc,'sub','length.center.minusD')
        if sign not in (-1,1):raise ValueError('signed axial direction required')
        if sign<0:center=op(0,center,'sub','length.center.negate')
        center256=pack(checked256(center)) # exact range check; no truncation/cast credit
        lo=sign*(2*(mc-mr)-(origin+sr)-(dc+dr))
        hi=sign*(2*(mc+mr)-(origin-sr)-(dc-dr))
        if sign<0:lo,hi=hi,lo
        if [lo,hi]!=g['length_interval_scaled'] or not 0<lo<=center<=hi:raise ValueError('correlated scene length enclosure mismatch')
        length=F(center,S);words,represented,cast=encode_hilo(length)
        h=F(decode32_scaled(words[0]),S);l=F(decode32_scaled(words[1]),S)
        if h+l!=represented:raise ValueError('exact length limb sum mismatch')
        encode_nodes=[{'input_rational':ratio(length),'output_uint32':words[0],'rounding_delta_rational':ratio(h-length)},
                      {'input_rational':ratio(length-h),'output_uint32':words[1],'rounding_delta_rational':ratio(l-(length-h))}]
        m=quotient_words(words,highword,phase_model=QUOTIENT)
        observed=F(*m['modeled_quotient_rational']);rn=F(*m['quotient_error_upper_rational'])
        encode=cast/w
        lambda_drop=abs(length/w-length/wc)
        numeric=encode+rn+lambda_drop
        cycleslo=F(lo,wavelength_center+wr);cycleshi=F(hi,wavelength_center-wr)
        sel_lo=min(cycleslo,observed-numeric);sel_hi=max(cycleshi,observed+numeric)
        radius=host_radius(sel_lo,sel_hi,observed)
        selector=select_words(m['quotient_limb_uint32'],radius['radius_signed256_words'],selector_model=SELECTOR)
        original_length=F(*g['original_length_BU_rational']);original_cycles=original_length/F(scene['lambda_BU'])
        geometry=8*max(abs(cycleslo-original_cycles),abs(cycleshi-original_cycles))
        if geometry!=F(*g['phase_error_bound_rad']):raise ValueError('original geometry/lambda phase charge mismatch')
        budget=F(*g['phase_budget_rad']);total=geometry+8*numeric
        if abs(observed-original_cycles)*8>total:raise ValueError('original-source phase bound violated')
        accepted=g['accepted_phase_budget_CPU_only'] and selector['accepted_CPU_integer_selector_only'] and total<=budget
        row.update(arithmetic_evaluated=True,phase_reference_id=reference,original_length_BU_rational=ratio(original_length),
                   original_cycles_rational=ratio(original_cycles),center_length_scaled_signed256_words=center256,
                   length_center_BU_rational=ratio(length),length_integer_operations=trace,
                   HOST_length_encoding_nodes=encode_nodes,length_encoding_error_BU_rational=ratio(cast),
                   wavelength_uint32_hilo=b['wavelength_uint32_hilo'],full_wavelength_center_BU_rational=ratio(wc),
                   quotient_uses_high32_explicit=True,quotient_wavelength_BU_rational=ratio(w),
                   measurement=m,geometry_phase_bound_rad=ratio(geometry),
                   length_encoding_charge_cycles=ratio(encode),quotient_RN_charge_cycles=ratio(rn),
                   discarded_lambda_low_charge_cycles=ratio(lambda_drop),new_numeric_phase_bound_rad=ratio(8*numeric),
                   composed_phase_bound_rad=ratio(total),phase_budget_rad=ratio(budget),
                   selector_requested_enclosure_cycles=[ratio(sel_lo),ratio(sel_hi)],HOST_selector_radius=radius,
                   selector=selector,accepted_bridge_phase_CPU_only=accepted)
        out['quotient_RN32_operations']+=5;out['HOST_length_encoding_RN32_operations']+=2
        out['new_length_integer_operations']+=len(trace);out['selector_integer_operations']+=selector['integer_operations']
    out['accepted_bridge_phase_CPU_only']=all(p['accepted_bridge_phase_CPU_only'] for p in out['paths'])
    return out

def audit_retained_bridge(*,case_names,bridge_model):
    if bridge_model!=MODEL:raise ValueError('explicit new scene geometry bridge CPU model required')
    if not isinstance(case_names,list) or not case_names or any(type(n) is not str for n in case_names) or len(set(case_names))!=len(case_names):raise ValueError('explicit unique nonempty case selection required')
    pins,cases=load_retained()
    if any(n not in cases for n in case_names):raise ValueError('unknown retained geometry case')
    result={n:bridge_case(cases[n],case_sha256=digest(cases[n]),bridge_model=MODEL) for n in case_names}
    return {'bridge_model':MODEL,'cases':result,'pins_verified':pins,'retained_report_sha256':SHA,
            'GPU_executed':False,'ALU_executed':False,'native_geometry_implemented':False,
            'native_selector_implemented':False,'execution_authenticated':False,'accepted_full_field_pipeline':False,
            'field_values_computed':False,'native_promotion_allowed':False,'geometry_or_producer_rerun':False,
            'scope':'CPU synthetic RN32 plus checked512/256; HOST exact length encode/outward radius/lambda-low charges. No shader geometry, GPU/RT/physical optics or full costs.'}

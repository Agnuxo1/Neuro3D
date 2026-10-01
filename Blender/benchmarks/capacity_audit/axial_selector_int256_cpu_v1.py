"""Bounded integer word-ABI phase selector CPU model, not native or GPU."""
import base64
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import zlib

ROOT=Path(__file__).resolve().parents[3]
REPORT='coordinacion/respuestas/AXIAL-REDUCTION-DETECTOR-RN64-001-CODEX.json'
SHA='0ee74281cfb6bd775da4c1d72b58ecc712e534976850eafe673d450e805b503d'
MODEL='axial-selector-signed256-words32-CPU-v1'
S=1<<149
MIN=-(1<<255)
MAX=(1<<255)-1


def checked(n):
    if type(n) is not int or not MIN<=n<=MAX:raise ValueError('signed256 overflow/type; no wraparound')
    return n


def pack(n):
    checked(n);n=n if n>=0 else n+(1<<256)
    return [(n>>(32*i))&0xffffffff for i in range(8)]


def unpack(words):
    if not isinstance(words,list) or len(words)!=8 or any(type(w) is not int or not 0<=w<1<<32 for w in words):
        raise ValueError('eight exact uint32 little-endian words required')
    n=sum(w<<(32*i) for i,w in enumerate(words))
    return n-(1<<256) if words[-1]>>31 else n


def decode32_scaled(word):
    if type(word) is not int or not 0<=word<1<<32:raise ValueError('exact uint32 required')
    e=(word>>23)&255;m=word&0x7fffff
    if e==255 or (e==0 and m):raise ValueError('normal-or-zero only; no FTZ')
    if e==0:return 0
    n=((1<<23)|m)<<(e-1)
    return checked(-n if word>>31 else n)


def select_words(words,radius_words,*,selector_model):
    """No Fraction/rational floor in this selector; signed256 checked ops."""
    if selector_model!=MODEL:raise ValueError('explicit bounded integer CPU selector required')
    if not isinstance(words,list) or len(words)!=2:raise ValueError('two quotient words required')
    a,b=map(decode32_scaled,words);radius=unpack(radius_words)
    if radius<0:raise ValueError('nonnegative signed256 radius required')
    trace=[]
    def op(a,b,kind,label):
        if kind=='add':v=a+b
        elif kind=='sub':v=a-b
        elif kind=='shr':v=a>>b
        elif kind=='shl':v=a<<b
        else:raise ValueError('unsupported checked integer op')
        checked(v);trace.append({'label':label,'op':kind,'inputs_signed256_words':[pack(a),pack(b)],'output_signed256_words':pack(v)})
        return v
    x=op(a,b,'add','decode.sum');lo=op(x,radius,'sub','enclosure.lo');hi=op(x,radius,'add','enclosure.hi')
    base={'selector_model':MODEL,'quotient_uint32':words,'radius_signed256_words':radius_words,
          'accepted_CPU_integer_selector_only':False,'native_selector_implemented':False,
          'GPU_executed':False,'ALU_executed':False,'accepted_full_field_pipeline':False,
          'observed_cycles_signed256_words':pack(x),'enclosure_signed256_words':[pack(lo),pack(hi)]}
    ns=[op(op(v,1<<148,'add',tag+'.turn.offset'),149,'shr',tag+'.turn.shift') for tag,v in [('lo',lo),('observed',x),('hi',hi)]]
    if len(set(ns))!=1:return {**base,'reason':'centered-turn branch uncertain; no epsilon/fallback','operations':trace,'integer_operations':len(trace)}
    n=ns[0];center=op(n,149,'shl','turn.center')
    rs=[op(v,center,'sub',tag+'.centered') for tag,v in [('lo',lo),('observed',x),('hi',hi)]]
    ks=[op(op(v,1<<146,'add',tag+'.quarter.offset'),147,'shr',tag+'.quarter.shift') for tag,v in zip(['lo','observed','hi'],rs)]
    if len(set(ks))!=1:return {**base,'reason':'quarter branch uncertain; no epsilon/fallback','operations':trace,'integer_operations':len(trace)}
    k=ks[0];quarter=op(k,147,'shl','quarter.center');residual=op(rs[1],quarter,'sub','residual')
    if not -2<=k<=2 or abs(residual)>1<<146:raise ValueError('quarter/residual invariant violated')
    return {**base,'accepted_CPU_integer_selector_only':True,'integer_turn':n,'quarter_index':k,
            'quarter_mod4':k%4,'residual_cycles_signed256_words':pack(residual),'residual_scale_exponent':-149,
            'operations':trace,'integer_operations':len(trace)}


def host_radius(lo,hi,observed):
    """Explicit outward HOST adapter, NOT shader/geometry or selector math."""
    lo,hi,observed=map(F,(lo,hi,observed))
    if not lo<=observed<=hi:raise ValueError('observed enclosed by retained cycles required')
    exact=max(observed-lo,hi-observed);q=exact*S;r=(q.numerator+q.denominator-1)//q.denominator
    checked(r)
    def ratio(v):return [v.numerator,v.denominator]
    return {'radius_signed256_words':pack(r),'exact_radius_cycles_rational':ratio(exact),
            'outward_inflation_cycles_rational':ratio(F(r,S)-exact),
            'origin':'HOST outward ceil radius from retained enclosure, not native geometry ABI'}


def payload(r):
    run=r['run'];raw=zlib.decompress(base64.b64decode(run['stdout_zlib_base64'],validate=True))
    if len(raw)!=run['stdout_bytes'] or hashlib.sha256(raw).hexdigest()!=run['stdout_sha256']:raise ValueError('retained payload SHA mismatch')
    return json.loads(raw)


def load_retained():
    raw=(ROOT/REPORT).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SHA:raise ValueError('retained reduction report SHA mismatch')
    r=json.loads(raw)
    if r['id']!='AXIAL-REDUCTION-DETECTOR-RN64-001-CODEX' or r['run']['rc']!=0:raise ValueError('retained identity/status mismatch')
    for n,h in r['code_doc_sha256'].items():
        if hashlib.sha256((ROOT/n).read_bytes()).hexdigest()!=h:raise ValueError('changed frozen input '+n)
    cases={}
    for key,f in [('quotient','AXIAL-PHASE-QUOTIENT-001'),('unit','AXIAL-UNIT-ROTATION-001')]:
        cases[key]=payload(json.loads((ROOT/('coordinacion/respuestas/'+f+'-CODEX.json')).read_bytes()))['audit']['cases']
    return r,cases['quotient'],cases['unit']


def audit_retained_selectors(*,case_names,selector_model):
    if selector_model!=MODEL:raise ValueError('explicit bounded integer CPU selector required')
    if not isinstance(case_names,list) or not case_names or any(type(n) is not str for n in case_names) or len(set(case_names))!=len(case_names):raise ValueError('explicit unique retained case selection required')
    r,cases,units=load_retained()
    if any(n not in cases for n in case_names):raise ValueError('unknown retained case')
    out={}
    for n in case_names:
        c=cases[n];u=units[n];ids=[p['source_id'] for p in c['paths']]
        if ids!=[p['source_id'] for p in u['paths']] or len(ids)!=len(set(ids)):raise ValueError('ordered unique path coverage required')
        for key in ('original_scene_binding_sha256','decoded_scene_binding_sha256'):
            if c[key]!=u[key]:raise ValueError('retained scene binding mismatch')
        rows=[]
        for p,up in zip(c['paths'],u['paths']):
            row={'source_id':p['source_id'],'phase_reference_id':p['phase_reference_id'],
                 'previous_phase_argument_accepted':p['accepted_phase_argument_CPU_only'],
                 'previous_unit_accepted':up['accepted_propagation_unit_CPU_only'],'integer_selector_evaluated':False}
            rows.append(row)
            if not p['accepted_phase_argument_CPU_only']:continue
            if p['phase_reference_id']!=up['phase_reference_id'] or p['phase_reference_id']!='original-source-zero:'+c['original_scene_binding_sha256']+':'+p['source_id']:raise ValueError('original source gauge required')
            old=p['selector'];turn=old['CPU_integer_turn'];center=F(*old['centered_observed_cycles_rational']);observed=center+turn
            lo,hi=[F(*v)+turn for v in old['centered_enclosure_cycles_rational']]
            radius=host_radius(lo,hi,observed);s=select_words(p['measurement']['quotient_limb_uint32'],radius['radius_signed256_words'],selector_model=MODEL)
            if F(unpack(s['observed_cycles_signed256_words']),S)!=observed:raise ValueError('word sum != retained observed argument')
            if s['accepted_CPU_integer_selector_only']:
                if s['integer_turn']!=turn or s['quarter_index']!=up['quarter_CPU_index'] or F(unpack(s['residual_cycles_signed256_words']),S)!=F(*up['quarter_residual_cycles_rational']):raise ValueError('retained branch/residual mismatch')
            row.update(integer_selector_evaluated=True,host_radius=radius,selector=s)
        out[n]={'original_scene_binding_sha256':c['original_scene_binding_sha256'],'decoded_scene_binding_sha256':c['decoded_scene_binding_sha256'],
                'previous_full_case_accepted':c['previous_full_case_accepted'],'previous_phase_argument_accepted':c['accepted_phase_argument_CPU_only'],
                'accepted_integer_selector_CPU_only':bool(rows) and all(row.get('selector',{}).get('accepted_CPU_integer_selector_only',False) for row in rows),
                'accepted_full_field_pipeline':False,'paths':rows}
    return {'selector_model':MODEL,'cases':out,'pins_verified':r['code_doc_sha256'],'retained_report_sha256':SHA,
            'GPU_executed':False,'ALU_executed':False,'native_selector_implemented':False,'accepted_full_field_pipeline':False,
            'geometry_ABI_implemented':False,'scene_or_producer_rerun':False,
            'cost_scope':'checked signed256 CPU integer operations and word decode only; HOST outward adapter separate; no native/hardware/full costs'}

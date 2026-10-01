"""Opt-in RN32 intensity CPU simulator over SHA-pinned scene outputs only."""
import base64
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import zlib

from axial_hilo_ops_cpu_v1 import component
from axial_hilo_terminal_cpu_v1 import round32_exact
from axial_relative_gate_cpu_v1 import ratio, bound, _relative

ROOT=Path(__file__).resolve().parents[3]
REPORT='coordinacion/respuestas/AXIAL-QUARTER-SOURCE-OPS-001-CODEX.json'
SHA='c3a54d51c47f901d4c0520216499c027a24c9579742e9b28a57073c72053d2a0'
MODEL='hilo-square-13op-rn32-v1'


class DetectorOperations:
    def __init__(self):self.trace=[]

    def rn(self,a,b,op,label):
        exact=a*b if op=='mul' else a+b
        word,value=round32_exact(exact)
        delta=value-exact
        self.trace.append({'label':label,'op':op,'inputs_rational':[ratio(a),ratio(b)],
            'output_uint32':word,'rounding_delta_rational':ratio(delta)})
        return value,delta

    def square(self,h,l,label):
        s,ds=self.rn(h,h,'mul',label+'.s')
        t,dt=self.rn(h,l,'mul',label+'.t')
        u,du=self.rn(l,l,'mul',label+'.u')
        v,dv=self.rn(t,t,'add',label+'.v')
        w,dw=self.rn(s,v,'add',label+'.w')
        z,dz=self.rn(w,u,'add',label+'.z')
        delta=ds+2*dt+du+dv+dw+dz
        if z-(h+l)**2!=delta:raise ValueError('square operation graph identity mismatch')
        b=abs(ds)+2*abs(dt)+abs(du)+abs(dv)+abs(dw)+abs(dz)
        return z,delta,b


def measure_group_words(words,*,detector_model):
    """Synthetic primitive; scene-level API accepts only retained named cases."""
    if detector_model!=MODEL:raise ValueError('explicit hilo-square-13op-rn32-v1 required')
    if not isinstance(words,list) or len(words)!=4:raise ValueError('four expansion uint32 words required')
    hr,lr,hi,li=map(component,words);o=DetectorOperations()
    re,dr,br=o.square(hr,lr,'real');im,di,bi=o.square(hi,li,'imag')
    q,dq=o.rn(re,im,'add','group.power')
    if q<0:raise ValueError('negative detector output outside nonnegative power contract; no clipping')
    reference=(hr+lr)**2+(hi+li)**2;b=br+bi+abs(dq)
    if q-reference!=dr+di+dq or abs(q-reference)>b:
        raise ValueError('detector group graph error bound mismatch')
    return {'output_power_uint32':o.trace[-1]['output_uint32'],'observed_power_rational':ratio(q),
        'input_modeled_power_rational':ratio(reference),'component_graph_deltas_rational':[ratio(dr),ratio(di)],
        'error_upper_rational':ratio(b),'actual_detector_error_rational':ratio(abs(q-reference)),
        'operations':o.trace,'RN32_operations':13,'GPU_executed':False,'ALU_executed':False}


def load_retained():
    raw=(ROOT/REPORT).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SHA:raise ValueError('retained report SHA mismatch')
    r=json.loads(raw)
    if r['id']!='AXIAL-QUARTER-SOURCE-OPS-001-CODEX' or r['run']['rc']!=0:
        raise ValueError('retained identity/status mismatch')
    for name,h in r['code_doc_sha256'].items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=h:raise ValueError('changed frozen input '+name)
    run=r['run'];stdout=zlib.decompress(base64.b64decode(run['stdout_zlib_base64'],validate=True))
    if len(stdout)!=run['stdout_bytes'] or hashlib.sha256(stdout).hexdigest()!=run['stdout_sha256']:
        raise ValueError('retained exact JSON payload integrity mismatch')
    return r,json.loads(stdout)


def _case(c):
    result={'accepted_detector_CPU_only':False,'previous_case_accepted':c['accepted_original_ideal_scene_CPU_only'],
        'new_field_values_computed':False,'scene_or_reduction_rerun':False,'GPU_executed':False,
        'ALU_executed':False,'native_promotion_allowed':False,'execution_authenticated':False,
        'no_jev_aval':True,'ports':{},'RN32_operations':0}
    if not c['field_values_computed']:
        return {**result,'reason':'prior scene/profile rejection; no detector execution'}
    for k in ('original_scene_binding_sha256','decoded_scene_binding_sha256'):result[k]=c[k]
    reference='ideal-scene-source-gauge:'+c['original_scene_binding_sha256']
    rows=c['rows'];valid=True
    expected_ids=[r['source_id'] for r in c['transport']['contributions']]
    if [r['source_id'] for r in rows]!=expected_ids or len(set(expected_ids))!=len(expected_ids):
        raise ValueError('complete unique ordered source coverage required')
    represented=c['reduction']['ports']
    if {(r['port'],r['coherence_group']) for r in rows}!={(p,g) for p,v in represented.items() for g in v['groups']}:
        raise ValueError('complete retained port/group coverage required')
    for port,p in represented.items():
        groups={};o=DetectorOperations();acc=F(0);sum_measure_bound=F(0);sum_exact=F(0);acc_bound=F(0)
        for group,g in p['groups'].items():
            ids=[r['source_id'] for r in rows if r['port']==port and r['coherence_group']==group]
            if ids!=g['source_ids'] or g['phase_reference_id']!=reference:
                raise ValueError('retained ordered group/reference mismatch')
            w=g['output_hilo_uint32'];vs=list(map(component,w))
            if [ratio(vs[0]+vs[1]),ratio(vs[2]+vs[3])]!=g['modeled_field_rational']:
                raise ValueError('retained field words/decoding mismatch')
            measured=measure_group_words(w,detector_model=MODEL)
            acc,delta=o.rn(acc,F(*measured['observed_power_rational']),'add','port.'+group)
            acc_bound+=abs(delta);sum_measure_bound+=bound(measured['error_upper_rational'])
            sum_exact+=F(*measured['input_modeled_power_rational'])
            groups[group]={'source_ids':ids,'phase_reference_id':reference,'measurement':measured}
            result['RN32_operations']+=13
        if acc<0:raise ValueError('negative port power; no clipping')
        propagation=bound(p['power_error_upper_rational']);detector=sum_measure_bound+acc_bound
        if abs(acc-sum_exact)>detector:raise ValueError('detector port composed graph bound mismatch')
        total=propagation+detector
        limit=bound(c['transport']['intensity_absolute_budget'])
        relative_limit=bound(p['relative_intensity']['relative_budget_rational'])
        gate=_relative(acc,total,relative_limit);ok=total<=limit and gate['relative_budget_satisfied']
        valid=valid and ok;result['RN32_operations']+=len(o.trace)
        result['ports'][port]={'groups':groups,'port_accumulator_operations':o.trace,
            'output_power_uint32':o.trace[-1]['output_uint32'],'observed_power_rational':ratio(acc),
            'retained_input_modeled_power_rational':ratio(sum_exact),
            'propagation_power_error_upper_rational':ratio(propagation),
            'detector_error_upper_rational':ratio(detector),'actual_detector_error_rational':ratio(abs(acc-sum_exact)),
            'composed_original_power_error_upper_rational':ratio(total),
            'intensity_absolute_budget_rational':ratio(limit),'intensity_absolute_pass':total<=limit,
            'relative_original_power':gate}
    result['new_detector_gates_pass']=valid
    result['accepted_detector_CPU_only']=c['accepted_original_ideal_scene_CPU_only'] and valid
    return result


def audit_retained_detector(*,case_names,detector_model):
    if detector_model!=MODEL:raise ValueError('explicit hilo-square-13op-rn32-v1 required')
    if not isinstance(case_names,list) or not case_names or any(type(n) is not str for n in case_names) \
            or len(set(case_names))!=len(case_names):
        raise ValueError('explicit nonempty unique retained case selection required')
    r,obs=load_retained();cases=obs['cases']
    if any(n not in cases for n in case_names):raise ValueError('unknown retained case')
    results={n:_case(cases[n]) for n in case_names}
    return {'schema':'exp005-axial-detector-ops-CPU-v1','detector_model':MODEL,'cases':results,
        'retained_report_sha256':SHA,'pins_verified':r['code_doc_sha256'],
        'RN32_operations':sum(c['RN32_operations'] for c in results.values()),
        'new_field_values_computed':False,'scene_or_reduction_rerun':False,'GPU_executed':False,
        'ALU_executed':False,'native_promotion_allowed':False,'execution_authenticated':False,'no_jev_aval':True,
        'cost_scope':'13 modeled RN32 per group plus port additions; excludes all upstream, IO, memory, energy, physical detector'}

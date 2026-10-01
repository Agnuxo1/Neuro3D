"""Opt-in operation-by-operation RN32 CPU simulation, NOT executed GPU/ALU.

Only SHA-pinned scene terminals; no producer replay or arbitrary scene fields.
Rational arithmetic supplies the emulator/oracle, not a native residual path.
"""
from fractions import Fraction as F
import hashlib
import json
import math
from pathlib import Path

from axial_hilo_terminal_cpu_v1 import round32_exact, word_value
from axial_relative_gate_cpu_v1 import ratio, bound, _relative

ROOT=Path(__file__).resolve().parents[3]
REPORT='coordinacion/respuestas/AXIAL-HILO-TERMINAL-001-CODEX.json'
SHA='7f82df1358ca2264ada8a39e884615b56845a4265768e20556860fcdbc37200e'
MODEL='five-twosum-32op-v1'


def component(word):
    if type(word) is not int or not 0<=word<2**32:
        raise ValueError('exact uint32 required')
    v=word_value(word)
    if not math.isfinite(v) or (v!=0 and abs(v)<2.**-126):
        raise ValueError('finite normal-or-zero inputs required')
    return F(v)


class Operations:
    def __init__(self):self.trace=[]

    def rn(self,a,b,op,label):
        exact=a+b if op=='add' else a-b
        word,value=round32_exact(exact)
        self.trace.append({'label':label,'op':op,'input_rational':[ratio(a),ratio(b)],
            'output_uint32':word,'rounding_delta_rational':ratio(value-exact)})
        return value

    def two_sum(self,a,b,label):
        s=self.rn(a,b,'add',label+'.s')
        bb=self.rn(s,a,'sub',label+'.bb')
        aa=self.rn(s,bb,'sub',label+'.aa')
        da=self.rn(a,aa,'sub',label+'.da')
        db=self.rn(b,bb,'sub',label+'.db')
        e=self.rn(da,db,'add',label+'.e')
        return s,e,s+e-a-b


def add_hilo_words(a,b,*,operation_model):
    """Bounded synthetic CPU primitive. Each result originates at one RN32 node."""
    if operation_model!=MODEL:raise ValueError('explicit five-twosum-32op-v1 required')
    if not isinstance(a,list) or not isinstance(b,list) or len(a)!=2 or len(b)!=2:
        raise ValueError('two limbs per input required')
    ah,al=map(component,a);bh,bl=map(component,b)
    o=Operations();deltas=[]
    s,e,d=o.two_sum(ah,bh,'high');deltas.append(d)
    t,f,d=o.two_sum(al,bl,'low');deltas.append(d)
    u,g,d=o.two_sum(e,t,'cross');deltas.append(d)
    v,h,d=o.two_sum(s,u,'merge');deltas.append(d)
    w=o.rn(g,f,'add','tail.w');deltas.append(w-g-f)
    z=o.rn(h,w,'add','tail.z');deltas.append(z-h-w)
    hi,lo,d=o.two_sum(v,z,'final');deltas.append(d)
    exact=ah+al+bh+bl;actual=hi+lo-exact
    if actual!=sum(deltas,F(0)) or len(o.trace)!=32:
        raise ValueError('operation graph identity/count mismatch')
    # Words of final.s and final.e, not exact residual re-encoding.
    words=[o.trace[-6]['output_uint32'],o.trace[-1]['output_uint32']]
    return {'output_hilo_uint32':words,'decoded_rational':ratio(hi+lo),
        'local_signed_deltas_rational':[ratio(d) for d in deltas],
        'error_upper_rational':ratio(sum(map(abs,deltas),F(0))),
        'actual_error_rational':ratio(abs(actual)),'operations':o.trace,'RN32_operations':32,
        'ALU_executed':False,'GPU_executed':False}


def load_retained():
    raw=(ROOT/REPORT).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SHA:raise ValueError('retained SHA mismatch')
    r=json.loads(raw)
    if r['id']!='AXIAL-HILO-TERMINAL-001-CODEX' or r['run']['rc']!=0:
        raise ValueError('retained identity/status mismatch')
    for name,h in r['code_doc_sha256'].items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=h:
            raise ValueError('changed frozen input: '+name)
    return r


def _case(c):
    out={'accepted_operation_model_CPU_only':False,'previous_case_accepted':c['accepted_original_ideal_scene_CPU_only'],
        'field_values_regenerated':False,'ALU_executed':False,'GPU_executed':False,
        'native_promotion_allowed':False,'execution_authenticated':False,'no_jev_aval':True,
        'ports':{},'RN32_operations':0}
    if not c['field_values_computed']:
        return {**out,'reason':'prior topology/mode rejection; no reduction executed'}
    out.update({k:c[k] for k in ('original_scene_binding_sha256','decoded_scene_binding_sha256')})
    rows=c['rows'];ids=[row['source_id'] for row in rows]
    expected=[row['source_id'] for row in c['transport']['contributions']]
    if not 1<=len(rows)<=16 or ids!=expected or len(set(ids))!=len(ids):
        raise ValueError('complete ordered unique scene coverage required')
    reference='ideal-scene-source-gauge:'+c['original_scene_binding_sha256']
    groups={}
    for row in rows:
        if row['phase_reference_id']!=reference:raise ValueError('original scene reference mismatch')
        words=row['field_hilo_uint32']
        if not isinstance(words,list) or len(words)!=4:raise ValueError('four terminal words required')
        values=list(map(component,words));decoded=[values[0]+values[1],values[2]+values[3]]
        if [ratio(v) for v in decoded]!=row['decoded_field_rational']:
            raise ValueError('retained words/decode mismatch')
        key=(row['port'],row['coherence_group'])
        g=groups.setdefault(key,{'words':[0,0,0,0],'bound':F(0),'reduction_bound':F(0),
            'exact_sum':[F(0),F(0)],'steps':[],'source_ids':[]})
        steps=[add_hilo_words(g['words'][i:i+2],words[i:i+2],operation_model=MODEL) for i in (0,2)]
        g['words']=[w for step in steps for w in step['output_hilo_uint32']]
        g['bound']+=bound(row['combined_error_L1_upper_rational'])
        g['reduction_bound']+=sum((bound(s['error_upper_rational']) for s in steps),F(0))
        g['exact_sum']=[a+b for a,b in zip(g['exact_sum'],decoded)]
        g['source_ids'].append(row['source_id']);g['steps'].append({'source_id':row['source_id'],'components':steps})
        out['RN32_operations']+=64
    if set(groups)!={(p,k) for p,v in c['ports'].items() for k in v['groups']}:
        raise ValueError('retained port/group coverage mismatch')
    fb=bound(c['field_budget_rational']);pb=bound(c['intensity_budget_rational'])
    fr=bound(c['field_relative_budget_rational']);pr=bound(c['intensity_relative_budget_rational'])
    valid=True
    for (port,group),g in groups.items():
        if g['source_ids']!=c['ports'][port]['groups'][group]['source_ids']:
            raise ValueError('retained ordered group coverage mismatch')
        vals=list(map(component,g['words']));y=[vals[0]+vals[1],vals[2]+vals[3]]
        actual=sum((abs(a-b) for a,b in zip(y,g['exact_sum'])),F(0))
        if actual>g['reduction_bound']:raise ValueError('graph reduction bound violated')
        b=g['bound']+g['reduction_bound'];n=sum(map(abs,y),F(0));q=sum((v*v for v in y),F(0))
        pe=2*n*b+b*b;rel=_relative(n,b,fr)
        p=out['ports'].setdefault(port,{'groups':{},'q':F(0),'pe':F(0)})
        p['q']+=q;p['pe']+=pe
        p['groups'][group]={'source_ids':g['source_ids'],'phase_reference_id':reference,
            'output_hilo_uint32':g['words'],'modeled_field_rational':[ratio(v) for v in y],
            'steps':g['steps'],'path_error_upper_rational':ratio(g['bound']),
            'reduction_error_upper_rational':ratio(g['reduction_bound']),
            'actual_reduction_error_rational':ratio(actual),'field_error_upper_rational':ratio(b),
            'power_error_upper_rational':ratio(pe),'field_absolute_pass':b<=fb,'relative_field':rel}
        valid=valid and b<=fb and rel['relative_budget_satisfied']
    for p in out['ports'].values():
        q=p.pop('q');pe=p.pop('pe');rel=_relative(q,pe,pr)
        p.update({'modeled_incoherent_power_rational':ratio(q),'power_error_upper_rational':ratio(pe),
            'intensity_absolute_pass':pe<=pb,'relative_intensity':rel})
        valid=valid and pe<=pb and rel['relative_budget_satisfied']
    out['new_model_gates_pass']=valid
    out['accepted_operation_model_CPU_only']=c['accepted_original_ideal_scene_CPU_only'] and valid
    return out


def audit_retained_hilo_operations(*,case_names,operation_model):
    if operation_model!=MODEL:raise ValueError('explicit five-twosum-32op-v1 required')
    if not isinstance(case_names,list) or not case_names or any(type(n) is not str for n in case_names) \
            or len(set(case_names))!=len(case_names):
        raise ValueError('explicit nonempty unique retained case selection required')
    r=load_retained();cases=r['run']['observations']['cases']
    if any(n not in cases for n in case_names):raise ValueError('unknown retained case')
    results={n:_case(cases[n]) for n in case_names}
    return {'schema':'exp005-axial-hilo-ops-CPU-v1','operation_model':MODEL,
        'retained_report_sha256':SHA,'pins_verified':r['code_doc_sha256'],'cases':results,
        'RN32_operations':sum(c['RN32_operations'] for c in results.values()),
        'ALU_executed':False,'GPU_executed':False,'native_promotion_allowed':False,
        'execution_authenticated':False,'no_jev_aval':True,'old_producer_or_suites_rerun':False,
        'cost_scope':'64 modeled RN32 nodes per complex source; excludes producer, geometry, IO, detector, energy'}

"""Compose new terminal bounds using changed reduction input or pinned graph."""
from copy import deepcopy
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
from axial_reduction_detector_rn64_cpu_v1 import Nodes,detector_words,payload,frozen_defaults,limits,MODEL as FROZEN_MODEL
from axial_unit_rn64_cpu_v1 import component64
from axial_relative_gate_cpu_v1 import ratio,bound,_relative

ROOT=Path(__file__).resolve().parents[3]
REPORT='coordinacion/respuestas/AXIAL-SOURCE-ARGUMENT-RN64-001-CODEX.json'
SHA='a70cc95da56063c96eeb853b95409903212f728efa472421fbb04465dc8b40e6'
RED_REPORT='coordinacion/respuestas/AXIAL-REDUCTION-DETECTOR-RN64-001-CODEX.json'
RED_SHA='0ee74281cfb6bd775da4c1d72b58ecc712e534976850eafe673d450e805b503d'
OLD_PRODUCT='coordinacion/respuestas/AXIAL-SOURCE-PRODUCT-RN64-001-CODEX.json'
OLD_PRODUCT_SHA='6be20bac7ddf52a4c8d167b92db2c576c03a81c45428d5fa7b95ac4577d1d9a8'
SOURCE_REPORT='coordinacion/respuestas/AXIAL-QUARTER-SOURCE-OPS-001-CODEX.json'
SOURCE_SHA='c3a54d51c47f901d4c0520216499c027a24c9579742e9b28a57073c72053d2a0'
RED_CODE='Blender/benchmarks/capacity_audit/axial_reduction_detector_rn64_cpu_v1.py'
MODEL='new-argument-coherent-detector-RN64-cached-graph-CPU-v1'


def pinned(name,sha):
    raw=(ROOT/name).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=sha:raise ValueError('retained report SHA mismatch '+name)
    r=json.loads(raw)
    if r['run']['rc']!=0:raise ValueError('retained status not successful')
    return r


def load_retained():
    r=pinned(REPORT,SHA)
    if r['id']!='AXIAL-SOURCE-ARGUMENT-RN64-001-CODEX':raise ValueError('new product identity mismatch')
    for n,h in r['code_doc_sha256'].items():
        if hashlib.sha256((ROOT/n).read_bytes()).hexdigest()!=h:raise ValueError('changed frozen input '+n)
    red=pinned(RED_REPORT,RED_SHA);old=pinned(OLD_PRODUCT,OLD_PRODUCT_SHA);src=pinned(SOURCE_REPORT,SOURCE_SHA)
    if red['detector_model']!=FROZEN_MODEL or red['code_doc_sha256'][RED_CODE]!=r['code_doc_sha256'][RED_CODE]:
        raise ValueError('cached reducer model/code mismatch')
    return r,payload(r)['audit']['cases'],payload(src)['cases'],payload(old)['audit']['cases'],payload(red)['audit']['cases'],frozen_defaults()


class CachedNodes:
    """Read exact SHA-pinned nodes, not RN execution; validate graph inputs."""
    def __init__(self,trace):self.saved=trace;self.trace=[]
    def rn(self,a,b,op,label):
        n=self.saved[len(self.trace)]
        if n['label']!=label or n['op']!=op or n['inputs_rational']!=[ratio(a),ratio(b)]:
            raise ValueError('cached graph inputs/order mismatch')
        v=component64(n['output_uint64']);exact=a+b if op=='add' else a*b
        d=F(*n['rounding_delta_rational'])
        if v-exact!=d:raise ValueError('cached node delta mismatch')
        self.trace.append(deepcopy(n))
        return v,d,n['output_uint64']


def signature(c):
    return [{'source_id':p['source_id'],'port':p['port'],'coherence_group':p['coherence_group'],
             'phase_reference_id':p['phase_reference_id'],'terminal_uint64':p['measurement']['output_uint64']}
            for p in c['paths']]


def _case(c,source,lim,oldproduct,oldred,code_sha):
    for key in ('original_scene_binding_sha256','decoded_scene_binding_sha256','previous_full_case_accepted'):
        if c[key]!=oldproduct[key] or c[key]!=oldred[key]:raise ValueError('cached case identity/binding mismatch')
    evaluated=c['accepted_source_product_absolute_CPU_only']
    reuse=evaluated and oldred['scene_field_reduced'] and signature(c)==signature(oldproduct)
    out=_compose(c,source,lim,oldred if reuse else None)
    n=out['RN64_operations']
    if reuse and n!=oldred['RN64_operations']:raise ValueError('cached graph count mismatch')
    out.update(reduction_cache_reused=bool(reuse),new_RN64_operations=0 if reuse else n,
               cached_RN64_operations=n if reuse else 0,
               cache_signature={'model':FROZEN_MODEL,'reducer_code_sha256':code_sha,
                                'ordered_terminals':signature(c),'report_sha256':RED_SHA if reuse else None})
    return out


def _compose(c,source,lim,cached):
    out={'previous_full_case_accepted':c['previous_full_case_accepted'],
         'previous_path_product_accepted':c['accepted_source_product_absolute_CPU_only'],
         'accepted_reduction_detector_CPU_only':False,'accepted_full_field_pipeline':False,
         'GPU_executed':False,'ALU_executed':False,'native_promotion_allowed':False,'execution_authenticated':False,
         'old_scene_unit_product_or_suites_rerun':False,'scene_field_reduced':False,'detector_evaluated':False,
         'original_scene_binding_sha256':c['original_scene_binding_sha256'],
         'decoded_scene_binding_sha256':c['decoded_scene_binding_sha256'],'RN64_operations':0,'ports':{}}
    for k in ('original_scene_binding_sha256','decoded_scene_binding_sha256'):
        if c[k]!=source['transport'][k]:raise ValueError('retained scene binding mismatch')
    if not c['accepted_source_product_absolute_CPU_only']:return {**out,'reason':'retained source-product reject; no reduction/detector'}
    rows=c['paths'];ids=[p['source_id'] for p in rows]
    expected=[p['source_id'] for p in source['transport']['contributions']]
    if not 1<=len(ids)<=16 or len(set(ids))!=len(ids) or ids!=expected:raise ValueError('complete ordered unique source coverage required')
    if lim is None:raise ValueError('explicit provenance-linked budgets required')
    fb,pb,fr,pr=[bound(lim[k]) for k in ('field','power','relative_field','relative_power')]
    if ratio(fb)!=c['field_absolute_L1_budget_rational']:raise ValueError('unchanged field cap required')
    reference='ideal-scene-source-gauge:'+c['original_scene_binding_sha256'];groups={}
    for row,con in zip(rows,source['transport']['contributions']):
        if row['phase_reference_id']!=reference or row['port']!=con['port'] or row['coherence_group']!=con['coherence_group']:
            raise ValueError('common gauge/port/coherence mismatch')
        if not row['accepted_source_product_absolute_CPU_only']:raise ValueError('complete path acceptance required')
        words=row['measurement']['output_uint64'];z=list(map(component64,words))
        if [ratio(v) for v in z]!=row['measurement']['observed_path_field_rational']:raise ValueError('retained terminal word/decode mismatch')
        key=(row['port'],row['coherence_group'])
        g=groups.setdefault(key,{'words':[0,0],'exact':[F(0),F(0)],'path_bound':F(0),'red_bound':F(0),'source_ids':[],'steps':[]})
        if cached is None:o=Nodes()
        else:
            cg=cached['ports'][key[0]]['groups'][key[1]]
            step=cg['steps'][len(g['steps'])]
            if step['source_id']!=row['source_id']:raise ValueError('cached ordered source mismatch')
            o=CachedNodes(step['operations'])
        values=list(map(component64,g['words']));new=[];deltas=[]
        for i in range(2):
            v,d,w=o.rn(values[i],z[i],'add','reduce.'+str(i));new.append(w);deltas.append(d)
        g['words']=new;g['exact']=[a+b for a,b in zip(g['exact'],z)]
        g['path_bound']+=bound(row['composed_path_field_error_L1_upper_rational'])
        g['red_bound']+=sum(map(abs,deltas),F(0));g['source_ids'].append(row['source_id'])
        g['steps'].append({'source_id':row['source_id'],'operations':o.trace});out['RN64_operations']+=2
    valid=True
    for (port,group),g in groups.items():
        y=list(map(component64,g['words']));actual=sum((abs(a-b) for a,b in zip(y,g['exact'])),F(0))
        if actual>g['red_bound']:raise ValueError('reduction error bound violated')
        e=g['path_bound']+g['red_bound'];n=sum(map(abs,y),F(0))
        relative=_relative(n,e,fr);transport_power=2*n*e+e*e
        if cached is None:det=detector_words(g['words'],detector_model=FROZEN_MODEL)
        else:
            cg=cached['ports'][port]['groups'][group]
            if cg['output_uint64']!=g['words']:raise ValueError('cached detector input words mismatch')
            det=deepcopy(cg['detector'])
        dp=bound(det['detector_error_upper_rational'])
        q=F(*det['observed_power_rational']);power_bound=transport_power+dp
        p=out['ports'].setdefault(port,{'groups':{},'power':F(0),'bound':F(0),'add_bound':F(0),'add_steps':[]})
        o=Nodes() if cached is None else CachedNodes([cached['ports'][port]['add_steps'][len(p['add_steps'])]])
        new,delta,w=o.rn(p['power'],q,'add','port.incoherent_sum')
        p['power']=new;p['bound']+=power_bound;p['add_bound']+=abs(delta);p['word']=w;p['add_steps']+=o.trace
        p['groups'][group]={'source_ids':g['source_ids'],'phase_reference_id':reference,
            'output_uint64':g['words'],'observed_field_rational':[ratio(v) for v in y],'steps':g['steps'],
            'path_error_upper_rational':ratio(g['path_bound']),'reduction_error_upper_rational':ratio(g['red_bound']),
            'actual_reduction_error_rational':ratio(actual),'composed_field_error_upper_rational':ratio(e),
            'field_absolute_pass':e<=fb,'relative_field':relative,'detector':det,
            'transport_power_error_upper_rational':ratio(transport_power),'group_power_error_upper_rational':ratio(power_bound)}
        valid=valid and e<=fb and relative['relative_budget_satisfied'];out['RN64_operations']+=4
    for p in out['ports'].values():
        q=p.pop('power');e=p.pop('bound')+p['add_bound'];relative=_relative(q,e,pr)
        p.update(observed_power_uint64=p.pop('word'),observed_incoherent_power_rational=ratio(q),
                 port_sum_error_upper_rational=ratio(p.pop('add_bound')),composed_power_error_upper_rational=ratio(e),
                 power_absolute_pass=e<=pb,relative_power=relative)
        valid=valid and e<=pb and relative['relative_budget_satisfied']
    out.update(scene_field_reduced=True,detector_evaluated=True,accepted_reduction_detector_CPU_only=valid,budgets=lim)
    return out



def audit_retained_new_argument_reduction(*,case_names,detector_model):
    if detector_model!=MODEL:raise ValueError('explicit new-argument CPU reduction contract required')
    if not isinstance(case_names,list) or not case_names or any(type(n) is not str for n in case_names) or len(set(case_names))!=len(case_names):
        raise ValueError('explicit unique retained selection required')
    r,cases,sources,oldproducts,oldred,defaults=load_retained()
    if any(n not in cases for n in case_names):raise ValueError('unknown retained case')
    result={n:_case(cases[n],sources[n],limits(n,sources[n],defaults) if cases[n]['accepted_source_product_absolute_CPU_only'] else None,
                    oldproducts[n],oldred[n],r['code_doc_sha256'][RED_CODE]) for n in case_names}
    return {'detector_model':MODEL,'cases':result,'pins_verified':r['code_doc_sha256'],'retained_report_sha256':SHA,
            'RN64_operations':sum(c['RN64_operations'] for c in result.values()),
            'new_RN64_operations':sum(c['new_RN64_operations'] for c in result.values()),
            'cached_RN64_operations':sum(c['cached_RN64_operations'] for c in result.values()),
            'GPU_executed':False,'ALU_executed':False,'native_promotion_allowed':False,'accepted_full_field_pipeline':False,
            'cost_scope':'new modeled RN64 nodes only for changed ordered terminals; same-input graph evidence not executed; bounds recomposed; upstream/IO/RAM/energy/guard/fullcost excluded'}

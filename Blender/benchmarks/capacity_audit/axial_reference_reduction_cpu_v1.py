"""Referenced original-scene terminal reduction; opt-in CPU hypothesis only."""
from copy import deepcopy
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
from axial_reference_argument_cpu_v1 import require, digest, pair, rat, nonnegative, payload
from axial_unit_rn64_cpu_v1 import component64
from axial_relative_gate_cpu_v1 import _relative
from axial_reduction_detector_rn64_cpu_v1 import Nodes, detector_words, MODEL as NUMERIC
ROOT=Path(__file__).resolve().parents[3]
MODEL='fixed-original-reference-terminal-group-reduction-detector-cache-CPU-v1'
SOURCE='scene-fixed-original-reference-source-mirror-product-RN64-cache-CPU-v1'
REPORT='coordinacion/respuestas/AXIAL-REFERENCE-SOURCE-001-CODEX.json'
SHA='58507912b97b88589ce292d22ab88d801578c2d1c69e4abd398ad959afd28d7d'
CACHE_REPORT='coordinacion/respuestas/AXIAL-GEOMETRY-REDUCTION-001-CODEX.json'
CACHE_SHA='61220e4c1460d1b867064745d1ac7fbde53faf7d9b160d7e5d2c15dd6fba9f10'
OLD_SOURCE='coordinacion/respuestas/AXIAL-GEOMETRY-SOURCE-001-CODEX.json'
CODE='Blender/benchmarks/capacity_audit/axial_reduction_detector_rn64_cpu_v1.py'
DECLARATION='explicit CPU grouping hypothesis; not scene/native/physical coherence authentication'
LIMITS=('field_L1','power','relative_field','relative_power')
AUDIT_LIMITS={'field_L1':[1,1000000000000],'power':[1,1000000000000],
              'relative_field':[1,1000000],'relative_power':[1,1000000]}

class ReductionCache:
    def __init__(self,pins,old,sources):
        self.code=pins[CODE];self.bank={'reduce2':{},'detector3':{},'power_add1':{}}
        cases=list(old['audit']['cases'].items())
        cases += [('two_sources',old['separate_group_control']),('positive',old['zero_cap_control'])]
        for name,c in cases:
            if not c['scene_field_reduced']:continue
            terminals={p['source_id']:p['measurement']['output_uint64'] for p in sources[name]['paths'] if 'measurement' in p}
            require(all(sig['model']==NUMERIC and sig['code_sha256']==self.code for sig in c['cache_signatures']),'pure reduction origin model/code')
            for port,p in c['ports'].items():
                for group,g in p['groups'].items():
                    acc=[0,0]
                    require(g['source_ids']==[s['source_id'] for s in g['steps']],'origin group coverage')
                    for step in g['steps']:
                        words=terminals[step['source_id']];ops=step['operations']
                        require(len(ops)==2,'two reduction nodes')
                        self.add('reduce2',acc+words,{'operations':ops})
                        acc=[n['output_uint64'] for n in ops]
                    require(acc==g['output_uint64'],'origin sum words')
                    self.add('detector3',acc,g['detector'])
                acc=0
                for step in p['add_steps']:
                    det=p['groups'][step['coherence_group']]['detector']
                    self.add('power_add1',[acc,det['output_uint64']],{'operations':step['operations']})
                    acc=step['operations'][0]['output_uint64']

    def key(self,kind,words):
        return {'kind':kind,'ordered_input_uint64':words,'model':NUMERIC,
                'code_sha256':self.code,'origin_report_sha256':CACHE_SHA}
    def add(self,kind,words,out):
        k=self.key(kind,words);h=digest(k);item={'key':k,'output':deepcopy(out),'output_sha256':digest(out)}
        require(h not in self.bank[kind] or self.bank[kind][h]['output_sha256']==item['output_sha256'],'conflicting reduction cache')
        self.bank[kind][h]=item
    def find(self,kind,words):
        k=self.key(kind,words);item=self.bank[kind].get(digest(k))
        if item is None:return None,{'cache_hit':False,'key':k}
        require(item['key']==k and digest(item['output'])==item['output_sha256'],'corrupt pure reduction cache')
        return deepcopy(item['output']),{'cache_hit':True,'key':k,'output_sha256':item['output_sha256'],
            'not_reused':['binding/IDs/group/gauges','bounds/caps/gates','execution admission/authentication','hardware costs']}

def load_retained():
    b=(ROOT/REPORT).read_bytes();require(hashlib.sha256(b).hexdigest()==SHA,'referenced source report SHA')
    r=json.loads(b)
    require(r['id']=='AXIAL-REFERENCE-SOURCE-001' and r['model']==SOURCE and
        r['test_run']['rc']==r['independent_validation']['rc']==0,'source identity/model/verification')
    pins=dict(r['code_doc_sha256'],**{REPORT:SHA})
    require(pins[CACHE_REPORT]==CACHE_SHA,'pure reduction origin pin')
    for n,h in pins.items():require(hashlib.sha256((ROOT/n).read_bytes()).hexdigest()==h,'changed frozen input '+n)
    old=payload(json.loads((ROOT/CACHE_REPORT).read_bytes()))
    src=payload(json.loads((ROOT/OLD_SOURCE).read_bytes()))['audit']['cases']
    return pins,payload(r)['audit'],ReductionCache(pins,old,src)

def contract_for(c,groups,limits):
    require(type(groups) is dict and set(groups)==set(c['source_order']),'explicit full grouping')
    binding=c['scene_binding_sha256'];terminal='fixed-original-plane-mode:'+binding+':D'
    return {'scene_binding_sha256':binding,'grouping_provenance':DECLARATION,'limits':deepcopy(limits),
        'assignments':[{'source_id':sid,'port':'D','coherence_group':groups[sid],
            'source_phase_reference_id':'original-source-zero:'+binding+':'+sid,
            'terminal_reference_id':terminal,'common_terminal_reference_id':terminal,
            'rebase_cycles':[0,1]} for sid in c['source_order']]}

def arithmetic(kind,words,cache):
    m,info=cache.find(kind,words)
    if m is None:
        if kind=='detector3':m=detector_words(words,detector_model=NUMERIC)
        else:
            o=Nodes()
            if kind=='reduce2':
                for j in range(2):o.rn(component64(words[j]),component64(words[j+2]),'add','reduce.'+str(j))
            else:o.rn(component64(words[0]),component64(words[1]),'add','port.incoherent_sum')
            m={'operations':o.trace}
    ops=m['operations'];length={'reduce2':2,'detector3':3,'power_add1':1}[kind]
    require(len(ops)==length,'matching node count')
    if kind=='reduce2':
        require([rat(v) for n in ops for v in n['inputs_rational']]==
            [component64(words[0]),component64(words[2]),component64(words[1]),component64(words[3])],'reduce input identity')
    if kind=='power_add1':require(list(map(rat,ops[0]['inputs_rational']))==list(map(component64,words)),'power input identity')
    return m,info,length

def compose(c,contract,cache,*,model,expected_source_sha256):
    require(model==MODEL and c['model']==SOURCE and digest(c)==expected_source_sha256,'explicit model/source digest')
    binding=c['scene_binding_sha256'];ids=c['source_order']
    require(type(contract) is dict and contract['scene_binding_sha256']==binding and contract['grouping_provenance']==DECLARATION,'binding-linked CPU hypothesis')
    rows=contract['assignments'];require(type(rows) is list and ids and len(set(ids))==len(ids)
        and [r['source_id'] for r in rows]==ids==[p['source_id'] for p in c['paths']],'complete ordered source assignments')
    require(type(contract['limits']) is dict and set(contract['limits'])==set(LIMITS),'explicit full caps no defaults')
    limits={k:nonnegative(contract['limits'][k]) for k in LIMITS}
    terminal='fixed-original-plane-mode:'+binding+':D'
    for row in rows:
        name=row['coherence_group'];require(type(name) is str and 0<len(name)<=64 and row['port']=='D','bounded group/port')
        require(row['source_phase_reference_id']=='original-source-zero:'+binding+':'+row['source_id']
            and row['terminal_reference_id']==row['common_terminal_reference_id']==terminal
            and rat(row['rebase_cycles'])==0,'explicit same fixed terminal gauge; no implicit source-gauge rebase')
    require(type(c['accepted_source_absolute_CPU_only']) is bool,'strict source gate')
    out={'model':MODEL,'scene_binding_sha256':binding,'word_ABI_sha256':c['word_ABI_sha256'],
        'source_case_sha256':expected_source_sha256,'source_order':ids,'contract':deepcopy(contract),
        'previous_source_accepted':c['accepted_source_absolute_CPU_only'],'accepted_reduction_detector_CPU_only':False,
        'scene_field_reduced':False,'detector_evaluated':False,'coherence_authenticated':False,
        'execution_authenticated':False,'accepted_full_field_pipeline':False,'ports':{},
        'new_RN64_operations':0,'cached_RN64_operations_NOT_executed':0,'cache_signatures':[]}
    if 'retained_closure_gates_UNCHANGED' in c:out['retained_closure_gates_UNCHANGED']=deepcopy(c['retained_closure_gates_UNCHANGED'])
    if not c['accepted_source_absolute_CPU_only']:
        out['reason']='retained source/unit/phase/geometry rejection; no downstream arithmetic'
        return out
    def calc(kind,words):
        m,info,n=arithmetic(kind,words,cache);out['cache_signatures'].append(info)
        out['cached_RN64_operations_NOT_executed' if info['cache_hit'] else 'new_RN64_operations']+=n
        return m,info
    groups={}
    for p,row in zip(c['paths'],rows):
        require(p['product_available'] is p['accepted_source_absolute_CPU_only'] is True,'complete accepted terminal products')
        require(p['port']==row['port'] and p['terminal_reference_id']==terminal
            and p['source_phase_reference_id']==row['source_phase_reference_id'],'terminal source/port/gauges')
        words=p['measurement']['output_uint64'];require(list(map(component64,words))==list(map(rat,p['measurement']['observed_path_field_rational'])),'terminal word decode identity')
        g=groups.setdefault(row['coherence_group'],{'words':[0,0],'source_ids':[],'steps':[],'path_bound':F(0),'round_bound':F(0)})
        m,info=calc('reduce2',g['words']+words);ops=m['operations']
        g['words']=[n['output_uint64'] for n in ops];g['source_ids'].append(p['source_id'])
        g['steps'].append({'source_id':p['source_id'],'operations':ops,'cache':info})
        g['path_bound']+=nonnegative(p['composed_path_field_error_L1'])
        g['round_bound']+=sum((abs(rat(n['rounding_delta_rational'])) for n in ops),F(0))
    port={'groups':{},'add_steps':[]};power=F(0);powerword=0;pb=F(0);valid=True
    for name,g in groups.items():
        y=list(map(component64,g['words']));e=g['path_bound']+g['round_bound'];norm=sum(map(abs,y),F(0))
        rel=_relative(norm,e,limits['relative_field']);det,di=calc('detector3',g['words'])
        require(component64(det['output_uint64'])==rat(det['observed_power_rational']),'detector word decode identity')
        transport=2*norm*e+e*e;gb=transport+nonnegative(det['detector_error_upper_rational'])
        add,ai=calc('power_add1',[powerword,det['output_uint64']]);node=add['operations'][0]
        powerword=node['output_uint64'];power=component64(powerword);pb+=gb+abs(rat(node['rounding_delta_rational']))
        port['add_steps'].append({'coherence_group':name,'operations':add['operations'],'cache':ai})
        port['groups'][name]={'source_ids':g['source_ids'],'common_terminal_reference_id':terminal,
            'output_uint64':g['words'],'observed_field_rational':[pair(v) for v in y],'steps':g['steps'],
            'path_error_L1':pair(g['path_bound']),'reduction_error_L1':pair(g['round_bound']),
            'composed_field_error_L1':pair(e),'field_absolute_pass':e<=limits['field_L1'],'relative_field':rel,
            'detector':det,'detector_cache':di,'transport_power_error':pair(transport),'group_power_error':pair(gb)}
        valid=valid and e<=limits['field_L1'] and rel['relative_budget_satisfied']
    rel=_relative(power,pb,limits['relative_power'])
    port.update(observed_power_uint64=powerword,observed_power_rational=pair(power),
        composed_power_error=pair(pb),power_absolute_pass=pb<=limits['power'],relative_power=rel)
    out.update(ports={'D':port},scene_field_reduced=True,detector_evaluated=True,
        accepted_reduction_detector_CPU_only=valid and port['power_absolute_pass'] and rel['relative_budget_satisfied'])
    return out

def audit(*,model,case_contracts):
    require(model==MODEL,'explicit referenced reduction model')
    pins,sources,cache=load_retained()
    require(type(case_contracts) is dict and set(case_contracts)==set(sources['cases']),'complete explicit case contracts')
    cases={n:compose(c,case_contracts[n],cache,model=model,expected_source_sha256=digest(c)) for n,c in sources['cases'].items()}
    controls={}
    for n,c in sources['controls'].items():
        contract=contract_for(c,{sid:'g' for sid in c['source_order']},AUDIT_LIMITS)
        controls[n]=compose(c,contract,cache,model=model,expected_source_sha256=digest(c))
    c=sources['cases']['two_sources'];contract=contract_for(c,{sid:sid for sid in c['source_order']},AUDIT_LIMITS)
    separated=compose(c,contract,cache,model=model,expected_source_sha256=digest(c))
    c=sources['cases']['positive'];limits=deepcopy(AUDIT_LIMITS);limits['field_L1']=[0,1]
    strict=compose(c,contract_for(c,{'s':'g'},limits),cache,model=model,expected_source_sha256=digest(c))
    return {'model':MODEL,'pins':pins,'cases':cases,'controls':controls,'separate_group_control':separated,
        'zero_field_cap_control':strict,'counts':{'cases':len(cases),'sources':sum(len(c['source_order']) for c in cases.values()),
            'reduced_cases':sum(c['scene_field_reduced'] for c in cases.values()),
            'accepted_cases_CPU_only':sum(c['accepted_reduction_detector_CPU_only'] for c in cases.values())},
        'new_RN64_operations':sum(c['new_RN64_operations'] for c in cases.values()),
        'cached_RN64_operations_NOT_executed':sum(c['cached_RN64_operations_NOT_executed'] for c in cases.values()),
        'control_costs_separate':{n:{k:c[k] for k in ('new_RN64_operations','cached_RN64_operations_NOT_executed')} for n,c in dict(controls,split_group=separated,zero_field_cap=strict).items()},
        'GPU_executed':False,'ALU_executed':False,'Bpy_executed':False,'execution_authenticated':False,
        'coherence_authenticated':False,'native_promotion_allowed':False,'accepted_full_field_pipeline':False,
        'old_upstream_producer_rerun':False,'cost_scope':'pure word RN64 nodes only; cache NOT executed; no IO/RAM/build/guard/energy/upstream/fullcost/equalwork evidence'}

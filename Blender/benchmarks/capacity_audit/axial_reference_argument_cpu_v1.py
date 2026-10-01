"""Opt-in referenced selector -> charged RN64 argument; partial CPU only."""
import base64
from copy import deepcopy
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import zlib
from axial_argument_pi_rn64_cpu_v1 import argument_words, MODEL as ARGUMENT, TWO_PI
from axial_unit_rn64_cpu_v1 import component64
from axial_selector_int256_cpu_v1 import unpack, decode32_scaled, MODEL as SELECTOR
from scene_field_producer_cpu_v1 import PI_LOWER, PI_UPPER

ROOT = Path(__file__).resolve().parents[3]
MODEL = 'scene-fixed-original-reference-argument-RN64-cache-CPU-v1'
BRIDGE = 'scene-fixed-original-reference-to-5rn32-selector256-CPU-v1'
REPORT = 'coordinacion/respuestas/AXIAL-REFERENCE-QUOTIENT-001-CODEX.json'
SHA = '392cc61542deb189d54762f40e1ffc8da5bfdf08d5a9b34e4b2115e95449c273'
CACHE_REPORT = 'coordinacion/respuestas/AXIAL-GEOMETRY-UNIT-001-CODEX.json'
CACHE_SHA = '525e7dc3fe7ffb2971390a0cc4034dafe07fd585d64f040223ac8b4ede5ef1cb'
CODE = 'Blender/benchmarks/capacity_audit/axial_argument_pi_rn64_cpu_v1.py'
S = 1 << 149


def require(c, why):
    if not c:
        raise ValueError(why)


def digest(v):
    return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


def pair(v):
    v=F(v)
    return [v.numerator,v.denominator]


def rat(v):
    require(type(v) is list and len(v)==2 and all(type(n) is int for n in v) and v[1]>0,'explicit rational pair')
    return F(*v)


def nonnegative(v):
    q=rat(v)
    require(q>=0,'nonnegative bound/budget')
    return q


def payload(r):
    run=r['test_run']
    raw=zlib.decompress(base64.b64decode(run['stdout_zlib_base64'],validate=True))
    require(run['rc']==0 and len(raw)==run['stdout_bytes'] and hashlib.sha256(raw).hexdigest()==run['stdout_sha256'],'retained payload status/SHA')
    return json.loads(raw)


class ArgumentCache:
    """Pure graph by exact words/model/code/origin, never scene acceptance."""
    def __init__(self,pins,old):
        self.codes={n:pins[n] for n in (CODE,
            'Blender/benchmarks/capacity_audit/axial_unit_rn64_cpu_v1.py',
            'Blender/benchmarks/capacity_audit/axial_selector_int256_cpu_v1.py',
            'Blender/benchmarks/capacity_audit/scene_field_producer_cpu_v1.py')}
        self.bank={}
        for c in old.values():
            for p in c['paths']:
                if 'argument_measurement' not in p:
                    continue
                m=p['argument_measurement'];sig=p['argument_cache_signature']
                require(sig['model']==ARGUMENT and sig['code_sha256']==pins[CODE],'argument origin model/code')
                key=self.key(m['residual_signed256_words']);k=digest(key)
                item={'key':key,'output':deepcopy(m),'output_sha256':digest(m)}
                require(k not in self.bank or self.bank[k]['output_sha256']==item['output_sha256'],'conflicting pure argument cache')
                self.bank[k]=item

    def key(self,words):
        unpack(words)
        return {'residual_words':words,'model':ARGUMENT,'code_sha256':self.codes,'origin_report_sha256':CACHE_SHA}

    def find(self,words):
        key=self.key(words);item=self.bank.get(digest(key))
        if item is None:
            return None,{'cache_hit':False,'key':key}
        require(item['key']==key and item['output_sha256']==digest(item['output']),'corrupt pure argument cache')
        return deepcopy(item['output']),{'cache_hit':True,'key':key,'output_sha256':item['output_sha256'],
            'not_reused':['scene binding/gauge','phase bound/budget/admission','execution authentication','cost comparison']}


def load_retained():
    data=(ROOT/REPORT).read_bytes()
    require(hashlib.sha256(data).hexdigest()==SHA,'reference quotient report SHA')
    r=json.loads(data)
    require(r['id']=='AXIAL-REFERENCE-QUOTIENT-001' and r['model']==BRIDGE
        and r['test_run']['rc']==r['independent_validation']['rc']==0,'retained identity/model/verification')
    pins=dict(r['code_doc_sha256'],**{REPORT:SHA})
    require(pins[CACHE_REPORT]==CACHE_SHA,'argument cache origin pin')
    for name,sha in pins.items():
        require(hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==sha,'changed frozen input '+name)
    old=json.loads((ROOT/CACHE_REPORT).read_bytes())
    data=payload(r)
    return pins,data,ArgumentCache(pins,payload(old)['audit']['cases'])


def integrate(c,cache,*,model,expected_case_sha256):
    require(model==MODEL,'explicit referenced CPU argument model required')
    require(digest(c)==expected_case_sha256 and c['model']==BRIDGE,'bound referenced case digest/model')
    ids=c['source_order'];binding=c['scene_binding_sha256']
    require(type(ids) is list and ids and all(type(v) is str for v in ids)
        and len(set(ids))==len(ids) and ids==[p['source_id'] for p in c['paths']],'ordered complete source coverage')
    costs={'new_bit_conversion':0,'cached_bit_conversion_NOT_executed':0,
           'new_RN64_multiply':0,'cached_RN64_multiply_NOT_executed':0}
    out={'model':MODEL,'reference_quotient_case_sha256':expected_case_sha256,
         'scene_binding_sha256':binding,'word_ABI_sha256':c['word_ABI_sha256'],
         'source_order':ids,'paths':[],'costs':costs,
         'accepted_argument_CPU_only':False,'accepted_full_field_pipeline':False,
         'fields_computed':False,'unit_computed':False,'execution_authenticated':False}
    for p in c['paths']:
        for k in ('arithmetic_evaluated','accepted_reference_quotient_CPU_only',
                  'previous_geometry_accepted','previous_phase_accepted','previous_reference_accepted'):
            require(type(p[k]) is bool,'strict retained gates')
        row={'source_id':p['source_id'],'previous_reference_quotient_accepted':p['accepted_reference_quotient_CPU_only'],
             'argument_available':False,'accepted_argument_CPU_only':False}
        out['paths'].append(row)
        if not p['accepted_reference_quotient_CPU_only']:
            row['reason']='retained upstream rejection; no argument conversion/multiply'
            continue
        require(all(p[k] for k in ('arithmetic_evaluated','previous_geometry_accepted','previous_phase_accepted','previous_reference_accepted')),'full reference provenance gates')
        source='original-source-zero:'+binding+':'+p['source_id']
        terminal='fixed-original-plane-mode:'+binding+':D'
        require(p['source_phase_reference_id']==source and p['terminal_reference_id']==terminal,'original source/terminal gauge')
        s=p['selector']
        require(s['selector_model']==SELECTOR and s['accepted_CPU_integer_selector_only'] is True
            and s['residual_scale_exponent']==-149,'referenced selector certificate')
        words=s['residual_cycles_signed256_words'];residual=F(unpack(words),S)
        turn=s['integer_turn'];quarter=s['quarter_index']
        require(type(turn) is int and type(quarter) is int and -2<=quarter<=2 and abs(residual)<=F(1,8),'turn/quarter/residual domain')
        observed=rat(p['measurement']['modeled_quotient_rational'])
        require(observed==sum(F(decode32_scaled(w),S) for w in s['quotient_uint32'])
            and observed==F(unpack(s['observed_cycles_signed256_words']),S)
            and residual==observed-turn-F(quarter,4),'selector residual words identity')
        lo,hi=[F(unpack(w),S) for w in s['enclosure_signed256_words']]
        require(lo<=observed<=hi and all((x+F(1,2))//1==turn and
            (x-turn+F(1,8))//F(1,4)==quarter for x in (lo,hi)),'same branch full enclosure')
        physical=rat(p['original_reference_cycles']);up=nonnegative(p['composed_phase_bound_rad']);cap=nonnegative(p['phase_budget_rad'])
        require(8*abs(observed-physical)<=up and up<=cap,'original referenced phase/cap')
        m,info=cache.find(words);hit=info['cache_hit']
        if m is None:
            m=argument_words(words,argument_model=ARGUMENT)
        costs['cached_bit_conversion_NOT_executed' if hit else 'new_bit_conversion']+=1
        costs['cached_RN64_multiply_NOT_executed' if hit else 'new_RN64_multiply']+=1
        require(m['residual_signed256_words']==words and m['TWO_PI_uint64']==TWO_PI
            and m['RN64_operations']==1 and len(m['operations'])==1,'exact argument input/constant')
        represented=component64(m['conversion']['output_uint64'])
        piword=component64(TWO_PI);value=component64(m['argument_uint64'])
        delta=value-represented*piword
        require(pair(delta)==m['operations'][0]['rounding_delta_rational']
            and pair(value)==m['observed_argument_rad_rational'],'argument node output/delta')
        charges={'residual_conversion':abs(piword)*abs(represented-residual),
                 'constant_2pi':abs(residual)*max(abs(piword-2*PI_LOWER),abs(piword-2*PI_UPPER)),
                 'multiply_RN64':abs(delta)}
        extra=sum(charges.values(),F(0));total=up+extra
        require(2*PI_UPPER<8 and pair(extra)==m['angle_error_upper_rad_rational'],'argument numerical charge')
        row.update(argument_available=True,argument_evaluated=not hit,argument_cache=info,
            source_phase_reference_id=source,terminal_reference_id=terminal,
            integer_turn=turn,quarter_index=quarter,residual_cycles=pair(residual),
            original_reference_cycles=pair(physical),original_reduced_reference_cycles=pair(physical-turn-F(quarter,4)),
            measurement=m,new_argument_error_charges_rad={k:pair(v) for k,v in charges.items()},
            new_argument_error_bound_rad=pair(extra),upstream_reference_phase_bound_rad=pair(up),
            composed_argument_phase_bound_rad=pair(total),phase_budget_rad=pair(cap),
            accepted_argument_CPU_only=total<=cap)
    out['accepted_argument_CPU_only']=all(p['accepted_argument_CPU_only'] for p in out['paths'])
    if 'retained_closure_gates_UNCHANGED' in c:
        out['retained_closure_gates_UNCHANGED']=deepcopy(c['retained_closure_gates_UNCHANGED'])
    return out


def audit(*,model):
    require(model==MODEL,'explicit referenced CPU argument model required')
    pins,data,cache=load_retained()
    cases={n:integrate(c,cache,model=model,expected_case_sha256=digest(c)) for n,c in data['audit']['cases'].items()}
    controls={n:integrate(c,cache,model=model,expected_case_sha256=digest(c)) for n,c in data['controls'].items()}
    def costs(items):
        return {k:sum(c['costs'][k] for c in items.values()) for k in next(iter(items.values()))['costs']}
    return {'model':MODEL,'pins':pins,'cases':cases,'controls':controls,
        'costs':costs(cases),'control_costs_separate':costs(controls),
        'counts':{'cases':len(cases),'sources':sum(len(c['paths']) for c in cases.values()),
                  'arguments':sum(p['argument_available'] for c in cases.values() for p in c['paths']),
                  'accepted_cases_CPU_only':sum(c['accepted_argument_CPU_only'] for c in cases.values())},
        'GPU_executed':False,'ALU_executed':False,'Bpy_executed':False,
        'execution_authenticated':False,'physical_coherence_verified':False,
        'native_promotion_allowed':False,'accepted_full_field_pipeline':False,
        'unit_computed':False,'fields_computed':False,'old_upstream_producer_rerun':False,
        'scope':'referenced residual to RN64 argument; new original-mode charges, pure graph reuse only; no unit/source/group/fields/full costs',
        'pending':['unit from THIS referenced argument with new budgets/gauges','native authentication and equal-work full costs']}

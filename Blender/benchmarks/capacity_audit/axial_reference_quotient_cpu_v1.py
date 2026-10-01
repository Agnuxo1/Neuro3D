"""Opt-in scene reference length -> RN32 quotient/selector, CPU only.

Retained arithmetic cached by exact inputs/model/code/report SHA, not by
source identity or acceptance. New reference/gauge/enclosures/costs explicit.
"""
import base64
from copy import deepcopy
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import zlib
from axial_selector_int256_cpu_v1 import (decode32_scaled, host_radius, select_words,
                                          pack, MODEL as SELECTOR)
from axial_phase_quotient_cpu_v1 import quotient_words, MODEL as QUOTIENT
from axial_hilo_terminal_cpu_v1 import encode_hilo

ROOT = Path(__file__).resolve().parents[3]
MODEL = 'scene-fixed-original-reference-to-5rn32-selector256-CPU-v1'
REFERENCE_MODEL = 'axial-fixed-original-terminal-plane-reference-CPU-v1'
FRAME = 'fixed original world point; ideal unit-X plane-wave mode'
TREE_MODEL = 'axial-shared-X-finite-event-tree-certificate-CPU-v1'
PREVIOUS = 'coordinacion/respuestas/AXIAL-TREE-COMPLETENESS-001-CODEX.json'
PREVIOUS_SHA = 'd895ef448dee2a4bb8657da1b6bd3f36635b91f4b8137ae29d194664c6db7d9e'
QREPORT = 'coordinacion/respuestas/AXIAL-GEOMETRY-QUOTIENT-001-CODEX.json'
QSHA = 'a16fd247a6aca8dd71796f0ee84bddb5efb7a7c439df7b644066e57c2772ab8b'
GREPORT = 'coordinacion/respuestas/AXIAL-GEOMETRY-WORDS-001-CODEX.json'
RREPORT = 'coordinacion/respuestas/AXIAL-TERMINAL-REFERENCE-001-CODEX.json'
S = 1 << 149


def require(c, reason):
    if not c:
        raise ValueError(reason)


def digest(v):
    return hashlib.sha256(json.dumps(v, sort_keys=True, separators=(',', ':'),
                                    allow_nan=False).encode()).hexdigest()


def pair(v):
    v = F(v)
    return [v.numerator, v.denominator]


def rat(v):
    require(type(v) is list and len(v) == 2 and all(type(x) is int for x in v)
            and v[1] > 0, 'explicit rational pair')
    return F(*v)


def decode(words):
    require(type(words) is list and len(words) == 2, 'two explicit normal-or-zero words')
    return sum(map(decode32_scaled, words))


def signed512(n):
    require(type(n) is int and -(1 << 511) <= n < 1 << 511, 'signed512 type/range no wrap')
    u = n % (1 << 512)
    return [(u >> (32*i)) & 0xffffffff for i in range(16)]


def integer_radius(n):
    require(type(n) is int and 0 <= n < 1 << 511, 'nonnegative integer radius')
    return n


def read_payload(p):
    r = json.loads((ROOT/p).read_bytes())
    run = r['test_run']
    raw = zlib.decompress(base64.b64decode(run['stdout_zlib_base64'], validate=True))
    require(len(raw) == run['stdout_bytes'] and hashlib.sha256(raw).hexdigest() == run['stdout_sha256'],
            'retained payload digest mismatch')
    return json.loads(raw)


class ArithmeticCache:
    """Only pure mathematical graph identity; never cached runtime/admission."""
    def __init__(self, pins, cases):
        self.code = {n: pins[n] for n in (
            'Blender/benchmarks/capacity_audit/axial_hilo_terminal_cpu_v1.py',
            'Blender/benchmarks/capacity_audit/axial_hilo_ops_cpu_v1.py',
            'Blender/benchmarks/capacity_audit/axial_phase_quotient_cpu_v1.py',
            'Blender/benchmarks/capacity_audit/axial_selector_int256_cpu_v1.py')}
        self.tables = {k: {} for k in ('encoding','quotient','selector')}
        for c in cases.values():
            for p in c['paths']:
                if not p['arithmetic_evaluated']:
                    continue
                m = p['measurement']
                e = {'nodes': p['HOST_length_encoding_nodes'],
                     'length_uint32_hilo': m['length_limb_uint32'],
                     'encoding_error_BU': p['length_encoding_error_BU_rational']}
                self.add('encoding', p['length_center_BU_rational'], e)
                self.add('quotient', [m['length_limb_uint32'],m['wavelength_uint32']], m)
                s = p['selector']
                self.add('selector', [s['quotient_uint32'],s['radius_signed256_words']], s)

    def key(self, kind, inputs):
        return {'kind':kind, 'inputs':inputs, 'model':{'encoding':'HOST-exact-RN32-hilo',
                'quotient':QUOTIENT,'selector':SELECTOR}[kind],
                'code_sha256':self.code, 'origin_report_sha256':QSHA}

    def add(self, kind, inputs, output):
        key = self.key(kind, inputs); k = digest(key)
        old = self.tables[kind].get(k)
        if old:
            require(old['output_sha256'] == digest(output), 'contradictory retained graph cache')
        self.tables[kind][k] = {'key':key, 'output':deepcopy(output), 'output_sha256':digest(output)}

    def find(self, kind, inputs):
        key = self.key(kind, inputs)
        item = self.tables[kind].get(digest(key))
        if item is None:
            return None, {'cache_hit':False, 'key':key}
        require(item['key'] == key and item['output_sha256'] == digest(item['output']),
                'corrupt mathematical graph cache')
        return deepcopy(item['output']), {'cache_hit':True,'key':key,'output_sha256':item['output_sha256'],
                                        'not_reused':['gauge','scene acceptance','geometry/reference bound','cost comparison']}


def load_retained():
    data = (ROOT/PREVIOUS).read_bytes()
    require(hashlib.sha256(data).hexdigest() == PREVIOUS_SHA, 'tree report SHA mismatch')
    r = json.loads(data)
    require(r['test_run']['rc'] == r['independent_validation']['rc'] == 0, 'tree verification status')
    pins = dict(r['code_doc_sha256'], **{PREVIOUS:PREVIOUS_SHA})
    for p,h in pins.items():
        require(hashlib.sha256((ROOT/p).read_bytes()).hexdigest() == h, 'changed frozen input '+p)
    require(pins[QREPORT] == QSHA, 'arithmetic cache report binding')
    q = read_payload(QREPORT)['audit']['cases']
    return pins, read_payload(GREPORT)['cases'], read_payload(RREPORT)['audit']['cases'], read_payload(PREVIOUS)['cases'], ArithmeticCache(pins,q)


def integrate(g, reference, tree, cache, *, model):
    require(model == MODEL, 'explicit CPU reference quotient model required')
    abi = g['word_ABI']; scene = g['scene_snapshot']; ids = abi['source_order']
    binding = digest({'snapshot':scene,'object_order':abi['object_ids'],'source_order':ids})
    require(binding == abi['original_scene_binding_sha256'] and digest(abi) == g['word_ABI_sha256'],
            'scene ABI binding mismatch')
    require(ids == [s['id'] for s in scene['sources']] == [s['source_id'] for s in g['sources']]
            == [s['source_id'] for s in abi['sources']] == [p['source_id'] for p in reference['paths']]
            == reference['source_ids'] == tree['source_order'] and len(set(ids)) == len(ids) and ids,
            'ordered full source/reference/tree coverage')
    require(reference['scene_binding_sha256'] == binding and reference['geometry_case_sha256'] == digest(g)
            and reference['reference_model'] == REFERENCE_MODEL and reference['reference_frame'] == FRAME,
            'matching fixed-original reference certificate')
    require(abi['object_ids'] == ['M','D'] and abi['kinds'] == ['mirror','det'],
            'restricted axial profile required')
    for p in g['sources']:
        require(type(p['accepted_geometry_words_CPU_only']) is bool
                and type(p['accepted_phase_budget_CPU_only']) is bool, 'strict retained geometry/phase gates')
    certified = tree['geometric_tree_complete_restricted_CPU_only']
    require(type(certified) is bool and certified == g['accepted_geometry_words_CPU_only'],
            'geometry/tree acceptance mismatch')
    if certified:
        cert = tree['certificate']
        require(tree['model'] == cert['model'] == TREE_MODEL and digest(cert) == tree['certificate_sha256']
                and cert['geometry_case_sha256'] == digest(g) and cert['word_ABI_sha256'] == g['word_ABI_sha256']
                and cert['scene_binding_sha256'] == binding and cert['source_order'] == ids,
                'matching tree certificate binding required')
    costs = dict(length_integer_new=0, HOST_length_RN32_new=0, HOST_length_RN32_cached_NOT_executed=0,
                 quotient_RN32_new=0, quotient_RN32_cached_NOT_executed=0,
                 selector_integer_new=0, selector_integer_cached_NOT_executed=0)
    out = {'model':MODEL,'scene_binding_sha256':binding,'word_ABI_sha256':g['word_ABI_sha256'],
           'reference_case_sha256':digest(reference),'tree_case_sha256':digest(tree),'source_order':ids,
           'paths':[],'costs':costs,'accepted_reference_quotient_CPU_only':False,
           'accepted_full_field_pipeline':False,'field_values_computed':False,
           'execution_authenticated':False,'native_promotion_allowed':False}
    for index,(original,src,geom,r) in enumerate(zip(scene['sources'],abi['sources'],g['sources'],reference['paths'])):
        row={'source_id':original['id'],'arithmetic_evaluated':False,
             'previous_geometry_accepted':geom['accepted_geometry_words_CPU_only'],
             'previous_phase_accepted':geom['accepted_phase_budget_CPU_only'],
             'previous_reference_accepted':r['accepted_terminal_reference_CPU_only'],
             'accepted_reference_quotient_CPU_only':False}
        out['paths'].append(row)
        require(type(r['accepted_terminal_reference_CPU_only']) is bool
                and r['previous_geometry_accepted'] is geom['accepted_geometry_words_CPU_only']
                and r['previous_phase_accepted'] is geom['accepted_phase_budget_CPU_only'],
                'reference upstream gate identity required')
        if not certified or not geom['accepted_geometry_words_CPU_only'] or not geom['accepted_phase_budget_CPU_only'] or not r['accepted_terminal_reference_CPU_only']:
            row['reason']='retained geometry/tree/phase/reference rejection; no new quotient/selector'
            continue
        require(r['reference_evaluated'] is True, 'evaluated reference required')
        sigma=geom['direction_sign']
        require(type(sigma) is int and sigma in (-1,1), 'signed axial context required')
        require(original['direction'] == [sigma,0,0]
                and [F(decode(w),S) for w in src['direction_uint32_hilo']] == [sigma,0,0]
                and scene['objects']['D']['mode_direction'] == [-sigma,0,0],
                'unchanged original forward unit-X reference')
        source_gauge='original-source-zero:'+binding+':'+original['id']
        terminal='fixed-original-plane-mode:'+binding+':D'
        require(geom['phase_reference_id'] == r['source_phase_reference_id'] == source_gauge
                and r['terminal_reference_id'] == terminal and r['port'] == 'D', 'original source/terminal gauge')
        planes={}
        for t in abi['triangles']:
            c=decode(t['vertices_uint32_hilo'][0][0]);rad=integer_radius(t['X_radius_scaled'])
            require(all(decode(v[0]) == c for v in t['vertices_uint32_hilo']), 'shared owner plane')
            if t['owner'] in planes:require(planes[t['owner']] == (c,rad), 'shared owner variable')
            planes[t['owner']]=(c,rad)
        mc,mr=planes[0];dc,dr=planes[1];sc=decode(src['origin_uint32_hilo'][0]);sr=integer_radius(src['X_radius_scaled'])
        rb=reference['reference_ABI'];rc=decode(rb['uint32_hilo']);rr=rat(rb['outward_radius_BU'])
        mode_original=F(scene['objects']['D']['mode_origin_BU'][0])
        require(rat(rb['original_BU']) == mode_original and rat(rb['center_BU']) == F(rc,S)
                and rat(rb['encoding_error_BU']) == abs(F(rc,S)-mode_original), 'original mode-X encoding required')
        require(rr*S == ((abs(F(rc,S)-mode_original)*S).__ceil__()), 'outward mode radius required')
        trace=[]
        def op(a,b,kind,label):
            value=a*b if kind=='mul' else a-b
            trace.append({'label':label,'op':kind,'inputs_signed512_words':[signed512(a),signed512(b)],
                          'output_signed512_words':signed512(value)})
            return value
        center=op(op(op(2,mc,'mul','reference.center.2M'),sc,'sub','reference.center.minusS'),rc,'sub','reference.center.minusR')
        if sigma<0:center=op(0,center,'sub','reference.center.negate')
        pack(center) # exact signed512 -> signed256 checked range, no truncation
        length=F(center,S)
        low,high=sorted((sigma*(2*F(mc-mr,S)-F(sc+sr,S)-(F(rc,S)+rr)),
                         sigma*(2*F(mc+mr,S)-F(sc-sr,S)-(F(rc,S)-rr))))
        require([pair(low),pair(high)] == r['effective_reference_length_interval_BU']
                and low<=length<=high, 'correlated referenced-length enclosure')
        # D deliberately absent ONLY in reference length; tree still covers D contact.
        original_m={F(v[0]) for v in scene['objects']['M']['vertices_world_BU']}
        require(len(original_m)==1, 'one original mirror plane')
        original_effective=sigma*(2*original_m.pop()-F(original['position_BU'][0])-mode_original)
        require(pair(original_effective)==r['original_effective_reference_length_BU'], 'original reference length')
        if low<=0:
            row['reason']='positive referenced length required by this quotient profile; no extension'
            continue
        wl=decode(abi['wavelength_uint32_hilo']);wr=integer_radius(abi['wavelength_radius_scaled'])
        whigh=abi['wavelength_uint32_hilo'][0];w=F(decode32_scaled(whigh),S);wc=F(wl,S)
        require(w>0 and wl-wr>0, 'positive high32/full wavelength')
        exact_original=original_effective/F(scene['lambda_BU'])
        cycles=[x/F(v,S) for x in (low,high) for v in (wl-wr,wl+wr)]
        ref_bound=8*max(abs(v-exact_original) for v in cycles)
        cap=rat(geom['phase_budget_rad'])
        require(pair(cap)==r['phase_budget_rad'] and pair(ref_bound)==r['phase_error_upper_rad'],
                'original reference phase/cap, not old geometric bound')
        encoded,enc_info=cache.find('encoding',pair(length))
        if encoded is None:
            words,represented,err=encode_hilo(length)
            h,l=[F(decode32_scaled(word),S) for word in words]
            encoded={'nodes':[{'input_rational':pair(length),'output_uint32':words[0],'rounding_delta_rational':pair(h-length)},
                              {'input_rational':pair(length-h),'output_uint32':words[1],'rounding_delta_rational':pair(l-(length-h))}],
                     'length_uint32_hilo':words,'encoding_error_BU':pair(err)}
            costs['HOST_length_RN32_new']+=2
        else:costs['HOST_length_RN32_cached_NOT_executed']+=2
        words=encoded['length_uint32_hilo'];represented=F(decode(words),S);cast=abs(represented-length)
        require(pair(cast)==encoded['encoding_error_BU'], 'encoded reference length error')
        measured,q_info=cache.find('quotient',[words,whigh])
        if measured is None:
            measured=quotient_words(words,whigh,phase_model=QUOTIENT);costs['quotient_RN32_new']+=5
        else:costs['quotient_RN32_cached_NOT_executed']+=5
        observed=rat(measured['modeled_quotient_rational']);rn=rat(measured['quotient_error_upper_rational'])
        require(measured['length_limb_uint32']==words and measured['wavelength_uint32']==whigh, 'matching quotient inputs')
        cast_charge=cast/w;lambda_drop=abs(length/w-length/wc);numeric=cast_charge+rn+lambda_drop
        selector_low=min(min(cycles),observed-numeric);selector_high=max(max(cycles),observed+numeric)
        radius=host_radius(selector_low,selector_high,observed)
        selector,s_info=cache.find('selector',[measured['quotient_limb_uint32'],radius['radius_signed256_words']])
        if selector is None:
            selector=select_words(measured['quotient_limb_uint32'],radius['radius_signed256_words'],selector_model=SELECTOR)
            costs['selector_integer_new']+=selector['integer_operations']
        else:costs['selector_integer_cached_NOT_executed']+=selector['integer_operations']
        total=ref_bound+8*numeric
        require(8*abs(observed-exact_original)<=total, 'original referenced phase not enclosed')
        row.update(arithmetic_evaluated=True,source_phase_reference_id=source_gauge,terminal_reference_id=terminal,
                   center_length_scaled_signed256_words=pack(center),length_center_BU=pair(length),
                   reference_length_integer_operations=trace,HOST_length_encoding=encoded,
                   encoding_cache=enc_info,measurement=measured,quotient_cache=q_info,selector_cache=s_info,
                   reference_inputs={'M':[pair(F(mc-mr,S)),pair(F(mc+mr,S))],
                                     'S':[pair(F(sc-sr,S)),pair(F(sc+sr,S))],
                                     'R':[pair(F(rc,S)-rr),pair(F(rc,S)+rr)],
                                     'D_ONLY_GEOMETRY':[pair(F(dc-dr,S)),pair(F(dc+dr,S))],
                                     'lambda':[pair(F(wl-wr,S)),pair(F(wl+wr,S))]},
                   original_effective_length_BU=pair(original_effective),original_reference_cycles=pair(exact_original),
                   effective_reference_length_interval_BU=[pair(low),pair(high)],
                   reference_phase_bound_rad=pair(ref_bound),length_encoding_charge_cycles=pair(cast_charge),
                   quotient_RN_charge_cycles=pair(rn),discarded_lambda_low_charge_cycles=pair(lambda_drop),
                   new_numeric_phase_bound_rad=pair(8*numeric),composed_phase_bound_rad=pair(total),
                   phase_budget_rad=pair(cap),HOST_selector_radius=radius,
                   selector_requested_enclosure_cycles=[pair(selector_low),pair(selector_high)],selector=selector,
                   accepted_reference_quotient_CPU_only=selector['accepted_CPU_integer_selector_only'] and total<=cap)
        costs['length_integer_new']+=len(trace)
    out['accepted_reference_quotient_CPU_only']=all(p['accepted_reference_quotient_CPU_only'] for p in out['paths'])
    return out


def audit(*, model):
    require(model==MODEL, 'explicit CPU model required')
    pins,geometry,refs,trees,cache=load_retained()
    require(set(geometry)==set(refs)==set(trees), 'complete cases required')
    cases={n:integrate(g,refs[n],trees[n],cache,model=model) for n,g in geometry.items()}
    for n,c in cases.items():c['retained_closure_gates_UNCHANGED']=trees[n]['retained_closure_gates_UNCHANGED']
    return {'model':MODEL,'pins':pins,'cases':cases,
            'counts':{'cases':len(cases),'sources':sum(len(c['paths']) for c in cases.values()),
                      'evaluated_paths':sum(p['arithmetic_evaluated'] for c in cases.values() for p in c['paths']),
                      'accepted_cases_CPU_only':sum(c['accepted_reference_quotient_CPU_only'] for c in cases.values())},
            'costs':{k:sum(c['costs'][k] for c in cases.values()) for k in next(iter(cases.values()))['costs']},
            'geometry_or_old_producer_rerun':False,'GPU_executed':False,'ALU_executed':False,'Bpy_executed':False,
            'execution_authenticated':False,'physical_coherence_verified':False,'native_promotion_allowed':False,
            'accepted_full_field_pipeline':False,'fields_computed':False,
            'scope':'new referenced-length graph and phase/selector enclosures; pure arithmetic cache only; no unit/source/field/group reinference',
            'pending':['feed THIS referenced residual into argument/unit/source/reduction with new bounds',
                       'native scene-bound operation/guard authentication and equivalent-work full costs']}

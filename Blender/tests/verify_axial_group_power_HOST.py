"""Independent receipt/budget oracle, stdlib only, no production imports or numeric replay."""
import base64,hashlib,json,math,sys,zlib
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
REPORT='coordinacion/respuestas/AXIAL-GROUP-POWER-HOST-001-CODEX.json'
PREVIOUS='coordinacion/respuestas/AXIAL-AMPLITUDE-ALLOCATION-CONTRACT-001-CODEX.json'
PREVIOUS_SHA='f8432ef9d18b27eb1b64d61a87320ecb2a380b4a68b85438f6cde6b590b970f4'
PRODUCT='coordinacion/respuestas/AXIAL-SOURCE-PRODUCT-HOST-001-CODEX.json'
PRODUCT_SHA='04390dac11ab3d7b2a785542bc9b7c94a0f447686b777def0cdeb0a3dceca1b3'
MODEL='axial-retained-bare-source-product-budget-HOST-v1'
AMODEL='axial-static-amplitude-L1-allocation-HOST-v1'
UNITS='ORIGINAL-source-field-amplitude-L1'
FLAG='accepted_retained_bare_source_product_budget_CPU_only'
FALSE=('amplitude_budget_accepted','remaining_stages_error_proved','reflection_coefficient_applied',
       'field_values_computed','field_sum_computed','detector_evaluated','native_kernel_implemented',
       'GPU_executed','GPU_job_admission','execution_authenticated','coherence_authenticated','accepted_full_field_pipeline')
def canon(v):
    return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def sha(v):
    return hashlib.sha256(v).hexdigest()
def digest(v):
    return sha(canon(v))
def read(p,h):
    b=(ROOT/p).read_bytes();assert sha(b)==h,p;return json.loads(b)
def payload(r):
    t=r['test_run'];assert t['rc']==0
    b=zlib.decompress(base64.b64decode(t.get('stdout_zlib_base64') or ''.join(t['stdout_zlib_base64_chunks']),validate=True))
    assert len(b)==t['stdout_bytes'] and sha(b)==t['stdout_sha256']
    return json.loads(b)
def pins_from(r):
    if 'code_doc_sha256' in r:
        return dict(r['code_doc_sha256'])
    d=r['inherited_pin_source'];p=pins_from(read(d['path'],d['sha256']))
    p[d['path']]=d['sha256'];p.update(r['own_code_doc_sha256']);return p
def rat(v):
    assert type(v) is list and len(v)==2 and all(type(n) is int for n in v)
    assert v[0]>=0 and v[1]>0 and math.gcd(*v)==1
    return F(*v)
def pair(v):
    return [v.numerator,v.denominator]
def context(packet):
    roles={'triangles','sources','wavelength','reference','original_scene_json','input_metadata_json'}
    assert set(packet['buffers_base64'])==set(packet['manifest']['buffers'])==roles
    b={k:base64.b64decode(v,validate=True) for k,v in packet['buffers_base64'].items()}
    for k,v in b.items():
        assert packet['manifest']['buffers'][k]=={'bytes':len(v),'sha256':sha(v)}
    m=json.loads(b['input_metadata_json']);snap=json.loads(b['original_scene_json']);g=m['explicit_group_contract']
    assert m['original_snapshot_sha256']==sha(b['original_scene_json'])
    assert m['source_order']==[s['id'] for s in snap['sources']]
    assert m['case_name']==packet['manifest']['case_name']
    assert g['scene_binding_sha256']==m['scene_binding_sha256']
    assert [a['source_id'] for a in g['assignments']]==m['source_order']
    groups=[]
    for a in g['assignments']:
        assert a['source_phase_reference_id']=='original-source-zero:'+m['scene_binding_sha256']+':'+a['source_id']
        key=[a['port'],a['coherence_group']]
        if key not in groups:
            groups.append(key)
    cap=rat(g['limits']['field_L1'])
    return {'model':AMODEL,'units':UNITS,'case_name':m['case_name'],'input_packet_sha256':digest(packet),
            'scene_binding_sha256':m['scene_binding_sha256'],'word_ABI_sha256':m['word_ABI_sha256'],
            'original_snapshot_sha256':m['original_snapshot_sha256'],'original_group_contract_sha256':digest(g),
            'source_order':m['source_order'],'assignments':g['assignments'],'groups':groups,
            'unchanged_field_L1_cap':pair(cap),'unchanged_limits':g['limits'],
            'grouping_provenance':g['grouping_provenance'],'execution_authenticated':False,'coherence_authenticated':False}

PREV='coordinacion/respuestas/AXIAL-GROUP-REDUCTION-HOST-001-CODEX.json'
PREV_SHA='44e1af7a17f3fdb9577d274dc001212f9cefe7ea17af7548c9ba5f7f113a942d'
PMODEL='axial-retained-group-power-3RN64-HOST-v1'
PUNITS='ORIGINAL-group-power-absolute'
PFLAG='accepted_retained_corner_group_power_CPU_only'
FFLAG='accepted_retained_corner_group_reduction_CPU_only'
PFALSE=('accepted_full_field_pipeline','detector_evaluated','remaining_stages_error_proved',
        'execution_authenticated','coherence_authenticated','native_kernel_implemented','GPU_executed','GPU_job_admission')
VARIANT='explicit_synthetic_INPUT_controls'
SIGN=1<<63
def decode(w):
    assert type(w) is int and 0<=w<2**64
    e=(w>>52)&2047;assert e<2047
    n=w&((1<<52)-1)
    if e:n+=1<<52
    return (-1 if w>>63 else 1)*F(n)*F(2)**(e-1075 if e else -1074)

def round_even_ratio(v):
    q,r=divmod(v.numerator,v.denominator)
    return q+(2*r>v.denominator or (2*r==v.denominator and q%2==1))

def round_word(v,left,right):
    # Independent integer-only RN-even; no float/struct conversion or production import.
    if not v:return SIGN if left==right==SIGN else 0
    negative=v<0;x=abs(v)
    e=x.numerator.bit_length()-x.denominator.bit_length()
    if x<F(2)**e:e-=1
    if e < -1022:
        n=round_even_ratio(x/F(2)**-1074)
        w=n # zero/subnormal or smallest normal, including rounded tiny zero.
    else:
        n=round_even_ratio(x/F(2)**(e-52))
        if n==2**53:n//=2;e+=1
        assert e<=1023,'integer oracle overflow'
        w=((e+1023)<<52)+(n-2**52)
    return w|(SIGN if negative else 0)


def number(row):
    words=row['input_uint64'];assert type(words) is list and len(words)==2
    real,imag=[decode(v) for v in words];bound=rat(row['input_field_L1_error_bound'])
    trace=[];square_words=[]
    for w in words:
        exact=decode(w)**2;out=round_word(exact,0,0)
        square_words.append(out)
        trace.append({'op':'mul','left_uint64':w,'right_uint64':w,'output_uint64':out,
                      'exact_rational':pair(exact),'rounding_error_abs':pair(abs(decode(out)-exact))})
    a,b=square_words;exact=decode(a)+decode(b);out=round_word(exact,0,0)
    trace.append({'op':'add','left_uint64':a,'right_uint64':b,'output_uint64':out,
                  'exact_rational':pair(exact),'rounding_error_abs':pair(abs(decode(out)-exact))})
    assert row['trace']==trace and row['RN64_operations']==3
    represented=real*real+imag*imag;observed=decode(out);rn=sum((rat(t['rounding_error_abs']) for t in trace),F(0))
    magnitude=max(abs(real),abs(imag));prop=2*magnitude*bound+bound*bound
    error=prop+rn;lower=max(F(0),magnitude-bound)**2
    assert row['observed_power_uint64']==out and rat(row['observed_power_rational'])==observed
    assert rat(row['represented_input_power_exact'])==represented
    assert rat(row['actual_error_abs_to_represented_power'])==abs(observed-represented)<=rn
    assert rat(row['field_to_power_error_abs_bound'])==prop
    assert rat(row['power_RN64_error_abs_bound'])==rn
    assert rat(row['combined_error_abs_to_ORIGINAL_power_bound'])==error
    assert rat(row['ORIGINAL_power_lower_bound'])==lower
    assert row['relative_power_error_bound']==(pair(error/lower) if lower else None)
    assert row['scope']=='HOST arithmetic primitive only, not scene evidence'
    assert row['relative_scope']=='ORIGINAL denominator lower bound; absent when ORIGINAL may be zero, no epsilon'
    # Independent exact diamond-extreme perturbations for the stated L1 field bound.
    for dr,di in ((bound,F(0)),(-bound,F(0)),(F(0),bound),(F(0),-bound)):
        original=(real+dr)**2+(imag+di)**2
        assert abs(original-represented)<=prop
        assert original>=lower
        assert abs(observed-original)<=error
        if lower:assert abs(observed-original)/original<=error/lower
    return prop,rn,error,lower

def plan_check(ctx,field,p):
    if p is None:return False
    assert type(p) is dict and set(p)=={'model','units','context_sha256','retained_variant',
                                      'field_allocation_INPUT_sha256','field_reduction_stage_INPUT_sha256','groups'}
    assert p['model']==PMODEL and p['units']==PUNITS and p['retained_variant']==VARIANT
    assert p['context_sha256']==digest(ctx)
    a=field['allocation_result'];s=field['stage_result']
    assert a['allocation_INPUT_valid'] is s['stage_INPUT_valid'] is True
    assert p['field_allocation_INPUT_sha256']==a['allocation_sha256']
    assert p['field_reduction_stage_INPUT_sha256']==s['stage_plan_sha256']
    assert type(p['groups']) is list
    assert [[g['port'],g['coherence_group']] for g in p['groups']]==ctx['groups']
    for g in p['groups']:
        assert type(g) is dict and set(g)=={'port','coherence_group','field_to_power_cap_abs','power_RN64_cap_abs',
                                           'other_power_stages_reserved_abs','relative_power_cap'}
        assert sum((rat(g[k]) for k in ('field_to_power_cap_abs','power_RN64_cap_abs','other_power_stages_reserved_abs')),F(0))<=rat(ctx['unchanged_limits']['power'])
        assert rat(g['relative_power_cap'])<=rat(ctx['unchanged_limits']['relative_power'])
    return True

def main():
    report=json.loads((ROOT/REPORT).read_bytes())
    assert report['base_commit']=='44a5a8e8af2b1b619b145d2f759e10ac52826a60'
    assert report['inherited_pin_source']=={'path':PREV,'sha256':PREV_SHA}
    pins=pins_from(report)
    assert len(pins)==237
    for p,h in pins.items():assert sha((ROOT/p).read_bytes())==h,p
    previous=payload(read(PREV,PREV_SHA))['data']
    fields=previous[VARIANT]['cases']
    ingress='coordinacion/respuestas/AXIAL-NATIVE-INGRESS-001-CODEX.json'
    presence='coordinacion/respuestas/AXIAL-NATIVE-PRESENCE-STOPS-001-CODEX.json'
    packets=payload(read(ingress,pins[ingress]))['packets']
    controls=payload(read(presence,pins[presence]))['synthetic_controls']
    packets.update({n:c['parent'] for n,c in controls.items()})
    raw=payload(report);assert raw['PASS'] is True and raw['tests']==6
    d=raw['data'];assert len(d['rejections'])==31 and len(d['primitives'])==7
    counts={'cases':17,'groups_partial_PASS':0,'groups_STOP':0,'preserved_source_STOPs':0,
            'scene_power_corners':0,'scene_power_RN64_operations':0,'diagnostic_power_corners':0,'diagnostic_power_RN64_operations':0}
    for label in ('missing','explicit_synthetic_INPUT_controls','zero_absolute','zero_relative'):
        audit=d[label];assert audit['model']==PMODEL and audit['units']==PUNITS and audit['retained_variant']==VARIANT
        assert audit['inherited_pins_verified']==233
        assert audit['field_L1_reserve_used_as_power_budget'] is False
        for flag in PFALSE:assert audit[flag] is False
        for key in ('new_field_products','new_field_reductions','new_trigonometry','new_ray_traces'):assert audit[key]==0
        total=0
        if label in ('missing','explicit_synthetic_INPUT_controls'):assert set(audit['cases'])==set(packets)
        for n,c in audit['cases'].items():
            old=fields[n];ctx=context(packets[n])
            assert c['context']==ctx==old['context'] and c['retained_variant']==VARIANT
            assert c['retained_source_rows_sha256']==[digest(s) for s in old['sources']]
            assert c['retained_source_STOP_FAILs']==[{'source_id':s['source_id'],'status':s['status'],'reason':s['reason']}
                                                   for s in old['sources'] if s['status'] in ('STOP','FAIL')]
            if label=='explicit_synthetic_INPUT_controls':counts['preserved_source_STOPs']+=len(c['retained_source_STOP_FAILs'])
            if label=='missing':p=None
            elif label=='explicit_synthetic_INPUT_controls':p=d['power_INPUT_plans'][n]
            else:p=d[label+'_INPUT']
            valid=plan_check(ctx,old,p)
            assert c['power_plan_result']['power_INPUT_valid'] is valid
            if valid:
                result=c['power_plan_result']
                assert result['power_plan_sha256']==digest(p) and result['groups']==p['groups']
                assert result['units']==PUNITS and result['unchanged_power_cap_abs']==ctx['unchanged_limits']['power']
                assert result['unchanged_relative_power_cap']==ctx['unchanged_limits']['relative_power']
                assert result['other_power_stages_error_proved'] is result['field_L1_reserve_used_as_power_budget'] is False
            assert [[g['port'],g['coherence_group']] for g in c['groups']]==ctx['groups']
            for index,(g,oldg) in enumerate(zip(c['groups'],old['groups'])):
                assert g['source_order']==oldg['source_order'] and g['retained_group_row_sha256']==digest(oldg)
                for flag in PFALSE:assert g[flag] is False
                if oldg[FFLAG] is not True:
                    assert g['status']=='STOP' and g['reason']==oldg['reason'] and g['retained_field_status']==oldg['status']
                    assert g['reason_provenance']=='unchanged_retained_field_group_STOP'
                    assert g['power_evaluated_HOST'] is g[PFLAG] is False and 'power_corners' not in g
                    if 'blocked_source_ids' in oldg:assert g['blocked_source_ids']==oldg['blocked_source_ids']
                elif not valid:
                    assert g['status']=='STOP' and g['reason_provenance']=='missing_power_INPUT'
                    assert g['power_evaluated_HOST'] is g[PFLAG] is False and 'power_corners' not in g
                else:
                    assert g['power_evaluated_HOST'] is True
                    assert len(g['power_corners'])==len(oldg['corner_sums'])
                    prop=F(0);rn=F(0);error=F(0);rel=F(0);zero=False
                    for row,corner in zip(g['power_corners'],oldg['corner_sums']):
                        assert row['retained_field_corner_sha256']==digest(corner)
                        assert row['input_uint64']==corner['sum_uint64'] and row['corner_indices']==corner['corner_indices']
                        assert row['input_field_L1_error_bound']==oldg['error_L1_to_ORIGINAL_group_corner_sum_bound']
                        a,b,e,lower=number(row)
                        prop=max(prop,a);rn=max(rn,b);error=max(error,e)
                        if lower:rel=max(rel,e/lower)
                        else:zero=True
                        total+=1
                    assert g['field_to_power_error_abs_bound']==pair(prop) and g['power_RN64_error_abs_bound']==pair(rn)
                    assert g['combined_error_abs_to_ORIGINAL_power_bound']==pair(error)
                    assert g['relative_power_error_bound']==(None if zero else pair(rel))
                    caps=p['groups'][index]
                    absolute=prop<=rat(caps['field_to_power_cap_abs']) and rn<=rat(caps['power_RN64_cap_abs']) and error<=rat(ctx['unchanged_limits']['power'])
                    relative=not zero and rel<=rat(caps['relative_power_cap']) and rel<=rat(ctx['unchanged_limits']['relative_power'])
                    assert g['absolute_power_gate'] is absolute and g['relative_power_gate'] is relative
                    assert g[PFLAG] is (absolute and relative)
                    assert g['status']==('STOP' if zero else ('PASS_PARTIAL' if absolute and relative else 'FAIL'))
                    assert g['unchanged_original_limits']==ctx['unchanged_limits']
                if label=='explicit_synthetic_INPUT_controls':counts['groups_partial_PASS' if g[PFLAG] else 'groups_STOP']+=1
            assert c[PFLAG] is all(g[PFLAG] for g in c['groups'])
            for flag in PFALSE:assert c[flag] is False
        assert audit['power_corner_evaluations']==total and audit['new_RN64_power_operations']==3*total
        if label=='explicit_synthetic_INPUT_controls':
            counts['scene_power_corners']=total;counts['scene_power_RN64_operations']=3*total
        elif label.startswith('zero_'):
            counts['diagnostic_power_corners']+=total;counts['diagnostic_power_RN64_operations']+=3*total
            g=audit['cases']['positive']['groups'][0];assert g['status']=='FAIL' and g[PFLAG] is False
            if label=='zero_relative':assert g['absolute_power_gate'] is True and g['relative_power_gate'] is False
            else:assert g['absolute_power_gate'] is False
        else:assert total==0
    for row in d['primitives']:number(row)
    assert d['primitives'][1]['observed_power_uint64']==0 and d['primitives'][1]['relative_power_error_bound'] is None
    assert d['primitives'][5]['relative_power_error_bound'] is None
    n='positive';ctx=context(packets[n])
    for rejected in d['rejections']:
        if rejected['kind']=='plan':
            p=json.loads(canon(d['power_INPUT_plans'][n]));obj=p
            for k in rejected['path'][:-1]:obj=obj[k]
            obj[rejected['path'][-1]]=rejected['value']
            try:plan_check(ctx,fields[n],p)
            except (AssertionError,KeyError,TypeError,ValueError,ZeroDivisionError):pass
            else:raise AssertionError('independent oracle accepted invalid plan '+rejected['label'])
        elif rejected['kind']=='primitive':
            w=rejected['words'];bound=rejected['bound']
            try:
                assert type(w) is list and len(w)==2;rat(bound)
                values=[decode(v) for v in w]
                outputs=[round_word(v*v,0,0) for v in values]
                round_word(sum((decode(v) for v in outputs),F(0)),0,0)
            except (AssertionError,KeyError,TypeError,ValueError,ZeroDivisionError):pass
            else:raise AssertionError('independent oracle accepted invalid primitive '+rejected['label'])
        else:assert rejected['label'] in {'duplicate','missing plan map','unknown case','unknown variant','missing opt-in model','variant/upstream mismatch'}
    assert counts=={'cases':17,'groups_partial_PASS':4,'groups_STOP':13,'preserved_source_STOPs':14,
                    'scene_power_corners':16,'scene_power_RN64_operations':48,'diagnostic_power_corners':8,'diagnostic_power_RN64_operations':24}
    assert report['failures_preserved']==[]
    return {'PASS':True,'pins_verified':len(pins),**counts,'primitive_controls':7,'primitive_RN64_operations':21,
            'all_new_power_RN64_operations':93,'diamond_extreme_ORIGINAL_checks':124,
            'expected_rejections':31,'production_imports':0,'field_computation_replays':0}
if __name__=='__main__':print(json.dumps(main(),sort_keys=True))

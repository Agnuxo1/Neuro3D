"""Independent receipt/budget oracle, stdlib only, no production imports or numeric replay."""
import base64,hashlib,json,math,sys,zlib
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
REPORT='coordinacion/respuestas/AXIAL-GROUP-REDUCTION-HOST-001-CODEX.json'
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

RREPORT='coordinacion/respuestas/AXIAL-GROUP-REDUCTION-HOST-001-CODEX.json'
TREE_REPORT='coordinacion/respuestas/AXIAL-TREE-LINEAGE-HOST-001-CODEX.json'
TREE_REPORT_SHA='e9ad9731436da1f75724354e8e6fb4fae9ed043d936a01a0752dc936abce7ae6'
MIRROR_REPORT='coordinacion/respuestas/AXIAL-MIRROR-ZERO-HOST-001-CODEX.json'
MIRROR_REPORT_SHA='5f5b8ce30a02a7b1a558d26ffbe5fd211d9fc9d78f9554456d93512f91d21586'
RMODEL='axial-retained-corner-group-reduction-RN64-HOST-v1'
RFLAG='accepted_retained_corner_group_reduction_CPU_only'
RFALSE=('accepted_full_field_pipeline','amplitude_budget_accepted','remaining_stages_error_proved',
        'detector_evaluated','execution_authenticated','coherence_authenticated','native_kernel_implemented',
        'GPU_executed','GPU_job_admission')
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

def numeric(row):
    words=row['source_uint64'];assert 1<=len(words)<=64
    for w in words:
        assert type(w) is list and len(w)==2
        for v in w:decode(v)
    current=list(words[0]);ops=[];error=F(0)
    for index,w in enumerate(words[1:],1):
        for component in range(2):
            a=current[component];b=w[component];exact=decode(a)+decode(b)
            out=round_word(exact,a,b);eps=abs(decode(out)-exact);error+=eps
            ops.append({'left_uint64':a,'right_uint64':b,'output_uint64':out,
                        'exact_sum':pair(exact),'rounding_error':pair(eps),
                        'source_index':index,'component':component})
            current[component]=out
    exact=[sum((decode(w[c]) for w in words),F(0)) for c in range(2)]
    actual=sum((abs(decode(current[c])-exact[c]) for c in range(2)),F(0))
    assert row['trace']==ops and row['RN64_additions']==len(ops)
    assert row['sum_uint64']==current and row['sum_rational']==[pair(decode(w)) for w in current]
    assert row['exact_represented_sources_sum']==[pair(x) for x in exact]
    assert rat(row['actual_error_L1_to_represented_sum'])==actual<=error
    assert rat(row['rounding_error_L1_bound'])==error
    assert row['scope']=='primitive only, not scene evidence'
    return error,len(ops)

def sources_plan(ctx,p):
    if p is None:return None
    assert set(p)=={'model','units','context_sha256','sources','groups'}
    assert p['model']==AMODEL and p['units']==UNITS and p['context_sha256']==digest(ctx)
    assert [s['source_id'] for s in p['sources']]==ctx['source_order']
    assert all(set(s)=={'source_id','cap_L1'} for s in p['sources'])
    caps={s['source_id']:rat(s['cap_L1']) for s in p['sources']}
    assert [[g['port'],g['coherence_group']] for g in p['groups']]==ctx['groups']
    assert all(set(g)=={'port','coherence_group','remaining_stages_reserved_L1'} for g in p['groups'])
    for g in p['groups']:
        members=[v['source_id'] for v in ctx['assignments'] if v['port']==g['port'] and v['coherence_group']==g['coherence_group']]
        assert sum((caps[s] for s in members),F(0))+rat(g['remaining_stages_reserved_L1'])<=rat(ctx['unchanged_field_L1_cap'])
    return caps

def stages_plan(ctx,source,p):
    if p is None:return False
    assert set(p)=={'model','units','context_sha256','source_allocation_sha256','groups'}
    assert source is not None
    assert p['model']==RMODEL and p['units']==UNITS and p['context_sha256']==digest(ctx)
    assert p['source_allocation_sha256']==digest(source)
    assert [[g['port'],g['coherence_group']] for g in p['groups']]==ctx['groups']
    assert all(set(g)=={'port','coherence_group','reduction_cap_L1','other_stages_reserved_L1'} for g in p['groups'])
    for g,old in zip(p['groups'],source['groups']):
        assert rat(g['reduction_cap_L1'])+rat(g['other_stages_reserved_L1'])<=rat(old['remaining_stages_reserved_L1'])
    return True

def main():
    report=json.loads((ROOT/RREPORT).read_bytes())
    assert report['base_commit']=='04a5285c1b416b5ac700af7a0b9b630f9e6e7fd3'
    assert report['inherited_pin_source']=={'path':TREE_REPORT,'sha256':TREE_REPORT_SHA}
    pins=pins_from(report)
    for p,h in pins.items():assert sha((ROOT/p).read_bytes())==h,p
    assert len(pins)==232 and pins[MIRROR_REPORT]==MIRROR_REPORT_SHA
    tree=payload(read(TREE_REPORT,TREE_REPORT_SHA))['data']['audit']['cases']
    mirror=payload(read(MIRROR_REPORT,MIRROR_REPORT_SHA))['data']['missing']['cases']
    bare=payload(read(PRODUCT,PRODUCT_SHA))['cases']
    ingress='coordinacion/respuestas/AXIAL-NATIVE-INGRESS-001-CODEX.json'
    presence='coordinacion/respuestas/AXIAL-NATIVE-PRESENCE-STOPS-001-CODEX.json'
    packets=payload(read(ingress,pins[ingress]))['packets']
    controls=payload(read(presence,pins[presence]))['synthetic_controls']
    packets.update({n:r['parent'] for n,r in controls.items()})
    raw=payload(report);assert raw['PASS'] is True and raw['tests']==6
    d=raw['data'];assert set(packets)==set(bare)==set(mirror)==set(tree)
    assert len(d['rejections'])==24 and len(d['primitives'])==7
    totals={'groups_partial_PASS':0,'groups_STOP':0,'source_numeric_STOPs':0,'corner_sums':0,'scene_RN64_additions':0}
    for label in ('missing','explicit_synthetic_INPUT_controls','missing_stage','zero_source'):
        audit=d[label];assert audit['model']==RMODEL and audit['units']==UNITS
        assert audit['inherited_pins_verified']==228
        for flag in RFALSE:assert audit[flag] is False
        for k in ('new_products','new_trigonometry','new_ray_traces','old_numeric_suites_executed'):assert audit[k]==0
        count=0;ops=0
        for name,c in audit['cases'].items():
            ctx=context(packets[name]);assert c['context']==ctx==mirror[name]['context']
            t=tree[name];assert t['input_packet_sha256']==ctx['input_packet_sha256']
            if 'context' in t:assert t['context']==ctx
            else:assert t['tree_lineage_matches_restricted_CPU_only'] is False
            assert c['retained_tree_row_sha256']==digest(t)
            if label=='missing':sp=None;st=None
            elif label=='missing_stage':sp=d['source_INPUT_plans'][name];st=None
            elif label=='zero_source':sp=d['zero_source_INPUT']['source'];st=d['zero_source_INPUT']['stage']
            else:sp=d['source_INPUT_plans'][name];st=d['stage_INPUT_plans'][name]
            caps=sources_plan(ctx,sp);stage_valid=stages_plan(ctx,sp,st)
            assert c['allocation_result']['allocation_INPUT_valid'] is (caps is not None)
            assert c['stage_result']['stage_INPUT_valid'] is stage_valid
            for flag in RFALSE:assert c[flag] is False
            assert [s['source_id'] for s in c['sources']]==ctx['source_order']
            for row,b,r,a in zip(c['sources'],bare[name]['sources'],mirror[name]['sources'],ctx['assignments']):
                assert r['retained_product_row_sha256']==digest(b) and row['reflected_row_sha256']==digest(r)
                assert r['phase_reference_id']==a['source_phase_reference_id']
                assert r['terminal_reference_id']==a['terminal_reference_id']
                if not b['source_product_evaluated']:
                    assert row['status']=='STOP' and row['reason']==r['reason']==b['reason']
                    assert row['source_budget_evaluated'] is row['source_budget_fits'] is False
                    if label=='missing':totals['source_numeric_STOPs']+=1
                elif caps is None:
                    assert row['status']=='STOP' and row['source_budget_evaluated'] is False
                else:
                    bound=rat(r['reflected_source_error_L1_to_ORIGINAL_bound']);cap=caps[row['source_id']]
                    assert rat(row['source_error_L1'])==bound and rat(row['source_cap_L1'])==cap
                    assert row['source_budget_evaluated'] is True and row['source_budget_fits'] is (bound<=cap)
                    assert row['status']==('PASS_PARTIAL' if bound<=cap else 'FAIL')
            assert [[g['port'],g['coherence_group']] for g in c['groups']]==ctx['groups']
            for index,g in enumerate(c['groups']):
                assignments=[a for a in ctx['assignments'] if [a['port'],a['coherence_group']]==ctx['groups'][index]]
                ids=[a['source_id'] for a in assignments];assert g['source_order']==ids
                members=[s for s in c['sources'] if s['source_id'] in ids]
                blocked=[s['source_id'] for s in members if not s['source_budget_fits']]
                if blocked:
                    assert g['status']=='STOP' and g['blocked_source_ids']==blocked
                    assert g['retained_corner_sum_computed'] is g[RFLAG] is False and 'corner_sums' not in g
                elif not stage_valid:
                    assert g['status']=='STOP' and 'missing explicit reduction-stage' in g['reason']
                    assert g['retained_corner_sum_computed'] is g[RFLAG] is False
                else:
                    assert t['tree_lineage_matches_restricted_CPU_only'] is True
                    assert all(a['terminal_reference_id']==a['common_terminal_reference_id']==assignments[0]['common_terminal_reference_id']
                               and a['rebase_cycles']==[0,1] for a in assignments)
                    assert g['certificate_sha256']==t['certificate_sha256']
                    from itertools import product
                    selections=list(product(range(4),repeat=len(ids)))
                    assert [r['corner_indices'] for r in g['corner_sums']]==[list(v) for v in selections]
                    max_rn=F(0)
                    for r,sel in zip(g['corner_sums'],selections):
                        words=[mirror[name]['sources'][ctx['source_order'].index(s)]['reflected_corner_products_HOST'][i]['reflected_uint64']
                               for s,i in zip(ids,sel)]
                        assert r['source_uint64']==words
                        err,cnt=numeric(r);max_rn=max(max_rn,err);ops+=cnt;count+=1
                    total=sum((rat(s['source_error_L1']) for s in members),F(0))
                    assert rat(g['source_errors_L1_sum'])==total and rat(g['reduction_RN64_error_L1_bound'])==max_rn
                    plan=st['groups'][index]
                    assert g['reduction_cap_L1']==plan['reduction_cap_L1']
                    assert g['other_stages_reserved_L1']==plan['other_stages_reserved_L1']
                    assert rat(g['error_L1_to_ORIGINAL_group_corner_sum_bound'])==total+max_rn
                    assert g['unchanged_group_field_L1_cap']==ctx['unchanged_field_L1_cap']
                    accepted=max_rn<=rat(plan['reduction_cap_L1']) and total+max_rn<=rat(ctx['unchanged_field_L1_cap'])
                    assert g[RFLAG] is accepted and g['retained_corner_sum_computed'] is True
                    assert g['status']==('PASS_PARTIAL' if accepted else 'FAIL')
                for flag in RFALSE:assert g[flag] is False
                if label=='explicit_synthetic_INPUT_controls':
                    totals['groups_partial_PASS' if g[RFLAG] else 'groups_STOP']+=1
            assert c[RFLAG] is all(g[RFLAG] for g in c['groups'])
        assert audit['retained_corner_sums']==count and audit['new_RN64_additions']==ops
        if label=='explicit_synthetic_INPUT_controls':
            totals['corner_sums']=count;totals['scene_RN64_additions']=ops
    primitive_ops=sum(numeric(r)[1] for r in d['primitives'])
    assert primitive_ops==14
    n='positive';ctx=context(packets[n])
    for r in d['rejections']:
        if r['kind']=='stage':
            st=json.loads(canon(d['stage_INPUT_plans'][n]));obj=st
            for key in r['path'][:-1]:obj=obj[key]
            obj[r['path'][-1]]=r['value']
            try:stages_plan(ctx,d['source_INPUT_plans'][n],st)
            except (AssertionError,KeyError,TypeError,ValueError,ZeroDivisionError):pass
            else:raise AssertionError('oracle accepted rejected stage '+r['label'])
        elif r['kind']=='primitive':
            w=r['words']
            try:
                assert type(w) is list and 1<=len(w)<=64 and all(type(v) is list and len(v)==2 for v in w)
                for v in w:
                    for a in v:decode(a)
                for a,b in zip(w[0],w[1] if len(w)>1 else [0,0]):round_word(decode(a)+decode(b),a,b)
            except (AssertionError,ValueError,TypeError,IndexError):pass
            else:raise AssertionError('oracle accepted invalid primitive '+r['label'])
        else:assert r['label'] in {'duplicate cases','missing stage map','unknown case','model opt-in missing','stage without source allocation'}
    assert totals=={'groups_partial_PASS':4,'groups_STOP':13,'source_numeric_STOPs':14,'corner_sums':16,'scene_RN64_additions':0}
    failed=report['failures_preserved']
    assert any(v['kind']=='new_suite_schema_ERROR' and v['run']['rc']==1 for v in failed)
    return {'PASS':True,'pins_verified':len(pins),**totals,'primitive_controls':7,'primitive_RN64_additions':primitive_ops,
            'expected_rejections':24,'production_imports':0,'new_geometry_product_trig_replays':0}
if __name__=='__main__':print(json.dumps(main(),sort_keys=True))

"""Independent coverage and integer-RNE oracle; stdlib, no production imports."""
import base64,hashlib,json,math,sys,zlib
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
REPORT='coordinacion/respuestas/AXIAL-STAGE-CLOSURE-HOST-001-CODEX.json'
AMODEL='axial-static-amplitude-L1-allocation-HOST-v1'
UNITS='ORIGINAL-source-field-amplitude-L1'
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


PREV='coordinacion/respuestas/AXIAL-GROUP-RELATIVE-HOST-001-CODEX.json'
PREV_SHA='997acd5255a9b3b0b115316f4c28cfeefc2b4459fff621edacb7dc42c39c7959'
FIELD='coordinacion/respuestas/AXIAL-GROUP-REDUCTION-HOST-001-CODEX.json'
POWER='coordinacion/respuestas/AXIAL-GROUP-POWER-HOST-001-CODEX.json'
TREE='coordinacion/respuestas/AXIAL-TREE-LINEAGE-HOST-001-CODEX.json'
MODEL='axial-retained-stage-domain-closure-HOST-v1'
PARTIAL='accepted_retained_corner_field_power_limits_CPU_only'
TFLAG='tree_lineage_matches_restricted_CPU_only'
STAGES=['restricted_geometry_lineage','source_error_entire_domain','group_RN_error_entire_domain',
        'power_error_entire_domain','ORIGINAL_reference_lower_entire_domain',
        'remaining_field_stage_error','remaining_power_stage_error']
VARIANTS=['missing','explicit_synthetic_INPUT_controls','zero_absolute','zero_relative']
FALSE=['stage_closure_proved','remaining_stages_error_proved','accepted_full_field_pipeline','detector_evaluated',
       'execution_authenticated','coherence_authenticated','native_kernel_implemented','GPU_executed','GPU_job_admission']
def false_flags(v):
    for k in FALSE:assert v[k] is False
def reservation(v,reserve,units):
    if reserve is not None:rat(reserve)
    assert v=={'reserved':reserve,'units':units,'proved':False,
               'reason':'reservation is INPUT accounting, not error evidence; absent or zero cannot close stage'}
def rn(v):
    x,y=decode(v['left_uint64']),decode(v['right_uint64'])
    assert v['op'] in ('add','mul')
    exact=x+y if v['op']=='add' else x*y
    out=round_word(exact,0,0)
    assert v['output_uint64']==out and v['exact_rational']==pair(exact)
    assert v['RN_error_abs']==pair(abs(decode(out)-exact))
def main():
    report=json.loads((ROOT/REPORT).read_bytes())
    assert report['task_id']=='AXIAL-STAGE-CLOSURE-HOST-001' and report['model']==MODEL
    assert report['inherited_pin_source']=={'path':PREV,'sha256':PREV_SHA}
    pins=pins_from(report);assert len(pins)==247 and pins[PREV]==PREV_SHA
    for p,h in pins.items():assert sha((ROOT/p).read_bytes())==h,p
    run=payload(report);assert run['PASS'] is True and run['tests']==6;d=run['data']
    r=payload(read(PREV,PREV_SHA))['data']
    f=payload(read(FIELD,pins[FIELD]))['data'];p=payload(read(POWER,pins[POWER]))['data']
    trees=payload(read(TREE,pins[TREE]))['data']['audit']['cases']
    packets=payload(read('coordinacion/respuestas/AXIAL-NATIVE-INGRESS-001-CODEX.json',
                         pins['coordinacion/respuestas/AXIAL-NATIVE-INGRESS-001-CODEX.json']))['packets']
    controls=payload(read('coordinacion/respuestas/AXIAL-NATIVE-PRESENCE-STOPS-001-CODEX.json',
                          pins['coordinacion/respuestas/AXIAL-NATIVE-PRESENCE-STOPS-001-CODEX.json']))['synthetic_controls']
    packets.update({n:c['parent'] for n,c in controls.items()});assert len(packets)==17
    totals=0;geometry_total=0
    for variant in VARIANTS:
        a=d[variant];expected=list(packets) if variant in VARIANTS[:2] else ['positive']
        assert a['model']==MODEL and a['retained_variant']==variant and a['case_order']==expected
        assert set(a['cases'])==set(expected) and a['required_stage_ids']==STAGES
        assert a['inherited_pins_verified']==243
        assert a['new_scene_RN_nodes']==a['new_scene_geometry_phase_field_power_computations']==0
        false_flags(a);count=0;geometry=0;partial=0;source_stops=0
        for n in expected:
            old=r[variant]['cases'][n];power=p[variant]['cases'][n];field=f[power['retained_variant']]['cases'][n]
            tree=trees[n];c=a['cases'][n];ctx=context(packets[n])
            assert c['context']==ctx==old['context']==power['context']==field['context']
            assert tree['input_packet_sha256']==ctx['input_packet_sha256']
            assert c['retained_case_sha256']==digest(old) and c['retained_variant']==variant
            assert c['retained_source_STOP_FAILs']==old['retained_source_STOP_FAILs']
            source_stops+=len(c['retained_source_STOP_FAILs'])
            false_flags(c)
            assert [[g['port'],g['coherence_group']] for g in c['groups']]==ctx['groups']
            assert len(c['groups'])==len(old['groups'])==len(power['groups'])==len(field['groups'])
            for index,(g,rg,pg,fg) in enumerate(zip(c['groups'],old['groups'],power['groups'],field['groups'])):
                assert g['source_order']==rg['source_order']==pg['source_order']==fg['source_order']
                assert g['retained_relative_group_sha256']==digest(rg)
                assert g['retained_corner_limits_pass'] is rg[PARTIAL]
                assert (g['retained_group_status'],g['retained_group_reason'])==(rg['status'],rg['reason'])
                false_flags(g)
                geo=tree[TFLAG]
                assert type(geo) is bool
                if geo:
                    assert tree['context']==ctx
                    assert [s['source_id'] for s in tree['sources']]==ctx['source_order']
                    assert all(s[TFLAG] is True for s in tree['sources'])
                evidence=[
                  {'report_path':TREE,'report_sha256':pins[TREE],'row_sha256':digest(tree)},
                  {'report_path':FIELD,'report_sha256':pins[FIELD],
                   'source_rows_sha256':[digest(s) for s in field['sources'] if s['source_id'] in g['source_order']]},
                  {'report_path':FIELD,'report_sha256':pins[FIELD],'row_sha256':digest(fg)},
                  {'report_path':POWER,'report_sha256':pins[POWER],'row_sha256':digest(pg)},
                  {'report_path':PREV,'report_sha256':PREV_SHA,'row_sha256':digest(rg)},
                  {'report_path':FIELD,'report_sha256':pins[FIELD],'row_sha256':digest(field['stage_result'])},
                  {'report_path':POWER,'report_sha256':pins[POWER],'row_sha256':digest(power['power_plan_result'])}]
                assert [v['stage_id'] for v in g['stage_obligations']]==STAGES
                for i,(v,stage,ref) in enumerate(zip(g['stage_obligations'],STAGES,evidence)):
                    proved=geo if i==0 else False
                    assert v['evidence']==ref and v['proved_for_required_domain'] is proved
                    assert v['required_domain']==('restricted axial tree only' if i==0 else 'entire claimed field/reference domain, not corners')
                    assert v['status']==('RETAINED_RESTRICTED_GEOMETRY' if proved else 'MISSING_REQUIRED_DOMAIN_EVIDENCE')
                    if i==5:
                        sr=field['stage_result'];reserved=sr['groups'][index]['other_stages_reserved_L1'] if sr['stage_INPUT_valid'] else None
                        if sr['stage_INPUT_valid']:assert sr['other_stages_error_proved'] is False
                        reservation(v['reservation'],reserved,'field_L1')
                    if i==6:
                        pr=power['power_plan_result'];reserved=pr['groups'][index]['other_power_stages_reserved_abs'] if pr['power_INPUT_valid'] else None
                        if pr['power_INPUT_valid']:assert pr['other_power_stages_error_proved'] is False
                        reservation(v['reservation'],reserved,'power_abs')
                    count+=1;geometry+=int(proved)
                assert g['missing_stage_ids']==[s for i,s in enumerate(STAGES) if not (i==0 and geo)]
                if rg[PARTIAL]:
                    partial+=1;assert g['status']=='STOP'
                    assert g['reason']=='corner limits fit but entire-domain and remaining-stage proofs are missing'
                    assert g['reason_provenance']=='new_stage_domain_coverage_requirement'
                else:
                    assert (g['status'],g['reason'])==(rg['status'],rg['reason'])
                    assert g['reason_provenance']=='unchanged_retained_STOP_FAIL'
            if n=='two_sources':assert c['retained_source_STOP_FAILs']==old['retained_source_STOP_FAILs']
        assert a['obligations_checked']==count and a['restricted_geometry_obligations_available']==geometry
        assert a['missing_obligations']==count-geometry;totals+=count;geometry_total+=geometry
        if variant==VARIANTS[1]:assert (count,geometry,partial,source_stops)==(119,8,4,14)
        if variant in VARIANTS[2:]:assert a['cases']['positive']['groups'][0]['status']=='FAIL'
    assert (totals,geometry_total)==(252,18)
    ce=d['counterexamples'];assert ce['synthetic_RN_nodes']==8
    nodes=[]
    for key,ncorners in [('square',2),('sum',4)]:
        witness=ce[key];assert witness['label']=='SYNTHETIC_NOT_SCENE'
        assert len(witness['corners'])==ncorners and witness['corner_RN_bound']==[0,1]
        nodes.extend(witness['corners']);nodes.append(witness['interior'])
        for v in witness['corners']:assert v['RN_error_abs']==[0,1]
        assert rat(witness['interior']['RN_error_abs'])>0
        for v in witness['corners']+[witness['interior']]:
            assert 1<=decode(v['left_uint64'])<=2 and 1<=decode(v['right_uint64'])<=2
    for v in nodes:rn(v)
    assert ce['sum']['interior']['RN_error_abs']==[1,2**52]
    assert ce['square']['interior']['RN_error_abs']==[1,2**104]
    witness=ce['reference'];assert witness['label']=='SYNTHETIC_NOT_SCENE'
    assert witness['real_interval']==[[-1,1],[1,1]] and witness['corner_error_bound']==[0,1]
    assert witness['observed_corner_L1']==witness['corner_ORIGINAL_lower']==[[1,1],[1,1]]
    assert witness['interior_original_field']==witness['entire_domain_original_lower']==[0,1]
    assert len(d['reservations'])==6
    for v,(reserve,units) in zip(d['reservations'],[(b,u) for u in ('field_L1','power_abs') for b in (None,[0,1],[1,10**12])]):
        reservation(v,reserve,units)
    assert len(d['rejections'])==19
    for v in d['rejections']:
        assert v['reason']
        if v['kind']=='reservation':
            try:
                assert v['model']==MODEL and v['units'] in ('field_L1','power_abs')
                rat(v['reserve'])
            except (AssertionError,TypeError,ValueError,ZeroDivisionError):pass
            else:raise AssertionError('invalid reservation accepted')
        elif v['kind']=='selection':
            try:
                names=v['names'];variant=v['variant']
                assert v['model']==MODEL and variant in VARIANTS and type(names) is list and 1<=len(names)<=64
                assert all(type(n) is str and n for n in names) and len(set(names))==len(names)
                assert set(names)<=set(r[variant]['cases'])
            except (AssertionError,TypeError,KeyError):pass
            else:raise AssertionError('invalid selection accepted')
        elif v['kind']=='changed_report':
            raw=(ROOT/PREV).read_bytes()
            bad=raw+b' ' if v['label']=='append_byte' else raw.replace(b'"accepted_full_field_pipeline": false',b'"accepted_full_field_pipeline": true',1)
            assert v['original_sha256']==PREV_SHA and v['changed_sha256']==sha(bad)!=PREV_SHA
        else:assert v['kind']=='caller_claim' and v['key'] in ('stage_closure_proved','reserved','stage_ids','proofs')
    assert report['failures_preserved']==[]
    return {'PASS':True,'pins_verified':247,'cases':17,'partial_corner_groups_preserved':4,
            'full_domain_closures':0,'main_obligations':119,'main_geometry_available':8,'main_missing':111,
            'all_variant_obligations':252,'all_variant_geometry_available':18,'source_STOPs_preserved':14,
            'synthetic_counterexamples':3,'synthetic_RN_nodes':8,'expected_rejections':19,
            'production_imports':0,'old_numeric_replays':0,'GPU_job_admission':False}
if __name__=='__main__':print(json.dumps(main(),sort_keys=True))

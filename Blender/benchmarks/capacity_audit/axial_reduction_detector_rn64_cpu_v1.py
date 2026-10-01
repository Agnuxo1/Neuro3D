"""Retained new RN64 paths -> coherent sums -> incoherent detector; CPU only."""
import ast
import base64
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import zlib

from axial_unit_rn64_cpu_v1 import component64,round64
from axial_relative_gate_cpu_v1 import ratio,bound,_relative

ROOT=Path(__file__).resolve().parents[3]
REPORT='coordinacion/respuestas/AXIAL-SOURCE-PRODUCT-RN64-001-CODEX.json'
SHA='6be20bac7ddf52a4c8d167b92db2c576c03a81c45428d5fa7b95ac4577d1d9a8'
MODEL='retained-path-coherent-detector-RN64-CPU-v1'


class Nodes:
    def __init__(self):self.trace=[]
    def rn(self,a,b,op,label):
        exact=a+b if op=='add' else a*b;w,v=round64(exact);d=v-exact
        self.trace.append({'label':label,'op':op,'inputs_rational':[ratio(a),ratio(b)],
                          'output_uint64':w,'rounding_delta_rational':ratio(d)})
        return v,d,w


def detector_words(words,*,detector_model):
    if detector_model!=MODEL:raise ValueError('explicit synthetic RN64 reduction-detector required')
    if not isinstance(words,list) or len(words)!=2:raise ValueError('two complex uint64 words required')
    re,im=map(component64,words);o=Nodes()
    rr,dr,_=o.rn(re,re,'mul','detector.real_square')
    ii,di,_=o.rn(im,im,'mul','detector.imag_square')
    q,ds,w=o.rn(rr,ii,'add','detector.combine')
    b=abs(dr)+abs(di)+abs(ds);actual=q-re*re-im*im
    if actual!=dr+di+ds:raise ValueError('detector graph identity violated')
    return {'output_uint64':w,'observed_power_rational':ratio(q),
            'detector_error_upper_rational':ratio(b),'actual_detector_error_rational':ratio(abs(actual)),
            'operations':o.trace,'RN64_operations':3}


def payload(report):
    run=report['run'];raw=zlib.decompress(base64.b64decode(run['stdout_zlib_base64'],validate=True))
    if len(raw)!=run['stdout_bytes'] or hashlib.sha256(raw).hexdigest()!=run['stdout_sha256']:
        raise ValueError('retained exact payload SHA mismatch')
    return json.loads(raw)


def frozen_defaults():
    """Read only four Fraction literal defaults; never execute frozen test."""
    tree=ast.parse((ROOT/'Blender/tests/test_axial_quarter_source_ops_cpu.py').read_text(encoding='utf-8'))
    run=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='run')
    opts=next(n.value for n in run.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='opts' for t in n.targets))
    wanted={'field_budget','intensity_budget','field_relative_budget','intensity_relative_budget'};out={}
    def integer(n):
        if isinstance(n,ast.Constant) and type(n.value) is int:return n.value
        if isinstance(n,ast.BinOp) and isinstance(n.op,ast.Pow) and isinstance(n.left,ast.Constant) and isinstance(n.right,ast.Constant) and n.left.value==10 and n.right.value==6:return 10**6
        raise ValueError('unsupported pinned budget literal')
    for key,v in zip(opts.keys,opts.values):
        if not isinstance(key,ast.Constant) or key.value not in wanted:continue
        if not isinstance(v,ast.Call) or not isinstance(v.func,ast.Name) or v.func.id!='F' or len(v.args)!=2 or v.keywords:
            raise ValueError('pinned Fraction default required')
        out[key.value]=F(integer(v.args[0]),integer(v.args[1]))
    if set(out)!=wanted or any(v<0 for v in out.values()):raise ValueError('complete nonnegative frozen limits required')
    return out


def limits(name,source,defaults):
    trans=source['transport'];fb=bound(trans['field_absolute_L1_budget']);pb=bound(trans['intensity_absolute_budget'])
    if 'reduction' in source:
        ports=source['reduction']['ports'];frs={bound(g['relative_field']['relative_budget_rational']) for p in ports.values() for g in p['groups'].values()}
        prs={bound(p['relative_intensity']['relative_budget_rational']) for p in ports.values()}
        if len(frs)!=1 or len(prs)!=1:raise ValueError('unambiguous retained relative limits required')
        fr=frs.pop();pr=prs.pop();origin='retained reducer per-group/per-port budgets, not PASS flags'
    else:
        if name not in ['nonquarter_FAIL','near_quarter_FAIL']:raise ValueError('missing retained limit provenance')
        if fb!=defaults['field_budget'] or pb!=defaults['intensity_budget']:raise ValueError('frozen default absolute budget mismatch')
        fr=defaults['field_relative_budget'];pr=defaults['intensity_relative_budget'];origin='SHA-pinned quarter run(s) defaults parsed AST; those cases had no limit override'
    return {'field':ratio(fb),'power':ratio(pb),'relative_field':ratio(fr),'relative_power':ratio(pr),'origin':origin}


def load_retained():
    raw=(ROOT/REPORT).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SHA:raise ValueError('retained product report SHA mismatch')
    r=json.loads(raw)
    if r['id']!='AXIAL-SOURCE-PRODUCT-RN64-001-CODEX' or r['run']['rc']!=0:raise ValueError('retained identity/status mismatch')
    for n,h in r['code_doc_sha256'].items():
        if hashlib.sha256((ROOT/n).read_bytes()).hexdigest()!=h:raise ValueError('changed frozen input '+n)
    src=json.loads((ROOT/'coordinacion/respuestas/AXIAL-QUARTER-SOURCE-OPS-001-CODEX.json').read_bytes())
    return r,payload(r)['audit']['cases'],payload(src)['cases'],frozen_defaults()


def _case(c,source,lim):
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
        o=Nodes();values=list(map(component64,g['words']));new=[];deltas=[]
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
        det=detector_words(g['words'],detector_model=MODEL);dp=bound(det['detector_error_upper_rational'])
        q=F(*det['observed_power_rational']);power_bound=transport_power+dp
        p=out['ports'].setdefault(port,{'groups':{},'power':F(0),'bound':F(0),'add_bound':F(0),'add_steps':[]})
        o=Nodes();new,delta,w=o.rn(p['power'],q,'add','port.incoherent_sum')
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


def audit_retained_reduction_detector(*,case_names,detector_model):
    if detector_model!=MODEL:raise ValueError('explicit synthetic RN64 reduction-detector required')
    if not isinstance(case_names,list) or not case_names or any(type(n) is not str for n in case_names) or len(set(case_names))!=len(case_names):
        raise ValueError('explicit unique nonempty retained selection required')
    r,cases,sources,defaults=load_retained()
    if any(n not in cases for n in case_names):raise ValueError('unknown retained case')
    result={n:_case(cases[n],sources[n],limits(n,sources[n],defaults) if cases[n]['accepted_source_product_absolute_CPU_only'] else None) for n in case_names}
    return {'schema':'exp005-coherent-detector-synthetic-RN64-CPU-v1','detector_model':MODEL,'cases':result,
        'RN64_operations':sum(c['RN64_operations'] for c in result.values()),'pins_verified':r['code_doc_sha256'],
        'retained_report_sha256':SHA,'GPU_executed':False,'ALU_executed':False,
        'native_promotion_allowed':False,'accepted_full_field_pipeline':False,
        'cost_scope':'2 modeled RN64/source +3 detector/group +1 incoherent-add/group; excludes retained geometry/unit/sourceproduct/IO/memory/energy/guard; no equalwork/fullcost/speed claim'}

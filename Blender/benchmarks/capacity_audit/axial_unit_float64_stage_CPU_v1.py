"""Opt-in actual CPU Horner26 stage over retained scene-bound angle fixtures."""
from copy import deepcopy
from fractions import Fraction as F
import math
import axial_source_float64_stage_CPU_v1 as source
io=source.io
allocation=source.allocation
require=source.require
digest=source.digest
MODEL='axial-pinned-Horner26-stage-CPU-float64-noFMA-v1'
PREVIOUS='coordinacion/respuestas/AXIAL-SOURCE-FLOAT64-STAGE-CPU-001-CODEX.json'
PREVIOUS_SHA='3075e1141e201cc773e88ab985b5f4da0f35da8f8ff86721dffd78db859c83b1'
UNIT_DOMAIN='coordinacion/respuestas/AXIAL-NONZERO-UNIT-DOMAIN-HOST-001-CODEX.json'
UNIFORM='coordinacion/respuestas/AXIAL-UNIFORM-UNIT-HOST-001-CODEX.json'
QUARTER='coordinacion/respuestas/AXIAL-QUARTER-UNIT-HOST-001-CODEX.json'
FALSE=source.FALSE
FLAG='CPU_float64_Horner26_fixture_executed'
UNIT_FLAG='restricted_nonzero_unit_error_to_ORIGINAL_bound_proved'
LABELS=['square']+[name+'.'+op+str(j) for name in ('cos','sin') for j in range(5,-1,-1) for op in ('mul','add')]+['sin.final']

def load_retained():
    receipt=allocation.parse(io.read(PREVIOUS,PREVIOUS_SHA))
    require(receipt['task_id']=='AXIAL-SOURCE-FLOAT64-STAGE-CPU-001','CPU SOURCE predecessor identity')
    pins=io.pins_from(receipt);pins[PREVIOUS]=PREVIOUS_SHA
    for path,h in pins.items():io.read(path,h)
    def payload(path):return io.payload(allocation.parse(io.read(path,pins[path])))
    old=payload(UNIT_DOMAIN)['data']['audit'];uniform=payload(UNIFORM)['data']['audit']
    units=payload(QUARTER)['cases'];previous=io.payload(receipt)['data']['audit']
    packets=payload(io.INGRESS)['packets']
    packets.update({n:v['parent'] for n,v in payload(io.PRESENCE)['synthetic_controls'].items()})
    require(set(packets)==set(old['cases'])==set(uniform['cases'])==set(units)==set(previous['cases']),'complete retained cases')
    return packets,old,uniform,units,previous,pins

def bind_fixture(packet,ctx,index,certificate,uniformrow,unitrow,profile):
    require(ctx==allocation.context_from_packet(packet,digest(packet),model=allocation.MODEL),'fresh complete INPUT context')
    require(type(index) is int and 0<=index<len(ctx['source_order']),'ordered source index')
    sid=ctx['source_order'][index];assignment=ctx['assignments'][index]
    require(certificate[UNIT_FLAG] is True and certificate['source_id']==uniformrow['source_id']==unitrow['source_id']==sid,'same eligible SOURCE')
    proof=certificate['proof']
    require(proof[UNIT_FLAG] is True and all(proof[k] is False for k in FALSE),'conditional certificate only; no promotion')
    require(proof['ORIGINAL_assignment_sha256']==digest(assignment),'ORIGINAL assignment/gauge')
    require(proof['retained_uniform_unit_row_sha256']==digest(uniformrow),'same uniform unit row')
    require(uniformrow['retained_unit_source_sha256']==digest(unitrow),'same retained quarter unit row')
    require(proof['coefficient_profile_sha256']==digest(profile),'same fixed coefficient profile')
    require(unitrow['phase_reference_id']==assignment['source_phase_reference_id']
            and unitrow['terminal_reference_id']==assignment['terminal_reference_id'],'same source/terminal gauge')
    require(unitrow['unchanged_original_phase_cap_rad']==proof['unchanged_original_phase_cap_rad'],'unchanged cap')
    require(unitrow['unit_HOST_evaluated'] is True,'retained modeled polynomial available')
    corners=unitrow['encoded_corner_units_HOST']
    require(len(corners)==4 and [digest(c) for c in corners]==uniformrow['retained_angle_corner_sha256'],'all four pinned witnesses')
    lo,hi=map(lambda v:F(*v),uniformrow['interval_theorem']['declared_angle_interval'])
    for corner in corners:
        rotation=corner['rotation_RN64'];arg=corner['quarter_argument']
        require(rotation['coefficients']==profile and rotation['RN64_operations']==26,'same coefficient words/Horner26')
        x=source.value(rotation['angle_uint64'],64)
        require(rotation['angle_uint64']==arg['HOST_argument_uint64'] and lo<=F.from_float(x)<=hi and abs(x)<=1,'same represented angle and polynomial interval')
        require(type(arg['quadrant_mod4']) is int and 0<=arg['quadrant_mod4']<4,'fixed quarter index')
        require([n['label'] for n in rotation['operations']]==LABELS,'same node labels')
    return corners

def execute_horner(corner):
    """Partial stage primitive; retained angle/coefficient inputs are NOT fresh scene inference."""
    rotation=corner['rotation_RN64'];refs=rotation['operations'];profile=rotation['coefficients']
    require(type(refs) is list and len(refs)==26 and [n['label'] for n in refs]==LABELS,'Horner26 reference graph')
    expected_ops=['mul']+[op for name in ('cos','sin') for j in range(5,-1,-1) for op in ('mul','add')]+['mul']
    require([n['op'] for n in refs]==expected_ops,'no FMA graph')
    require(set(profile)=={'cos','sin'} and all(len(profile[n])==7 for n in profile),'fixed seven coefficients per term')
    x=source.value(rotation['angle_uint64'],64);require(abs(x)<=1,'represented angle inside [-1,1]')
    coeff={n:[source.value(c['uint64'],64) for c in profile[n]] for n in ('cos','sin')}
    k=corner['quarter_argument']['quadrant_mod4']
    require(type(k) is int and 0<=k<4,'fixed quarter')
    nodes=[]
    def op(a,b,kind,label):
        ref=refs[len(nodes)]
        require(ref['inputs_rational']==[source.prev.unit.pair(F.from_float(a)),source.prev.unit.pair(F.from_float(b))],'same exact operands: '+label)
        v=a*b if kind=='mul' else a+b
        require(math.isfinite(v),'nonfinite result fail closed')
        actual=source.word(v);expected=ref['output_uint64']
        require(type(expected) is int and 0<=expected<2**64,'strict reference uint64')
        delta=F.from_float(v)-(F.from_float(a)*F.from_float(b) if kind=='mul' else F.from_float(a)+F.from_float(b))
        nodes.append({'label':label,'op':kind,'input_uint64':[source.word(a),source.word(b)],
          'output_uint64':actual,'reference_output_uint64':expected,'word_match':actual==expected,
          'observed_delta_rational':source.prev.unit.pair(delta)})
        return v
    z=op(x,x,'mul','square');out=[]
    for name in ('cos','sin'):
        h=coeff[name][6]
        for j in range(5,-1,-1):
            p=op(h,z,'mul',name+'.mul'+str(j));h=op(p,coeff[name][j],'add',name+'.add'+str(j))
        if name=='sin':h=op(h,x,'mul','sin.final')
        out.append(source.word(h))
    a,b=out;sign=1<<63
    unit=[a,b] if k==0 else ([b^sign,a] if k==1 else ([a^sign,b^sign] if k==2 else [b,a^sign]))
    bad=[n['label'] for n in nodes if not n['word_match']]
    final=unit==corner['unit_uint64']
    return {'nodes':nodes,'angle_uint64':rotation['angle_uint64'],'quarter_index':k,
      'unpermuted_unit_uint64':out,'unit_uint64':unit,'node_word_mismatches':bad,
      'exact_retained_node_bits_match':not bad,'retained_final_unit_bits_match':final,
      'status':'POINT_BITS_MATCH' if not bad and final else 'FAIL_RETAINED_NODE_BITS',
      'new_CPU_float64_RN_nodes_executed':26,'quarter_bit_permutation_executed':True,
      'zero_canonicalization_performed':False,'old_numeric_producers_reexecuted':0}

def audit_unit_float64_stage_CPU(case_names,*,model):
    require(model==MODEL,'explicit partial CPU Horner stage, not scene inference')
    require(type(case_names) is list and 1<=len(case_names)<=64 and all(type(n) is str and n for n in case_names)
            and len(set(case_names))==len(case_names),'bounded unique case names')
    packets,old,uniform,units,previous,pins=load_retained()
    require(set(case_names)<=set(packets),'known cases')
    probe=source.runtime_probe();require(probe['PASS'] is True,'CPU runtime probe failed; no Horner execution')
    cases={};executed=stopped=matched=failed=nodes=0
    for name in case_names:
        ctx=allocation.context_from_packet(packets[name],digest(packets[name]),model=allocation.MODEL)
        require(ctx==old['cases'][name]['context']==uniform['cases'][name]['context']==previous['cases'][name]['context'],'same fresh complete INPUT')
        quarter=units[name]
        for key in ('case_name','input_packet_sha256','scene_binding_sha256','word_ABI_sha256','source_order'):require(quarter[key]==ctx[key],'quarter INPUT '+key)
        cs=old['cases'][name]['sources'];us=uniform['cases'][name]['sources'];qs=quarter['sources']
        require([s['source_id'] for s in cs]==[s['source_id'] for s in us]==[s['source_id'] for s in qs]==ctx['source_order'],'complete ordered source coverage')
        rows=[]
        for i,(certificate,uniformrow,unitrow) in enumerate(zip(cs,us,qs)):
            row={'source_id':certificate['source_id'],'retained_unit_certificate_sha256':digest(certificate),
                 FLAG:False,'status':'STOP',**dict.fromkeys(FALSE,False)}
            if not certificate[UNIT_FLAG]:
                stopped+=1;row.update(reason=certificate['reason'],reason_provenance=certificate['reason_provenance'])
            else:
                corners=bind_fixture(packets[name],ctx,i,certificate,uniformrow,unitrow,uniform['coefficient_profile'])
                points=[]
                for j,corner in enumerate(corners):
                    point=execute_horner(corner);point.update(witness_index=j,retained_unit_corner_sha256=digest(corner))
                    points.append(point);nodes+=26
                    good=point['status']=='POINT_BITS_MATCH';matched+=int(good);failed+=int(not good)
                executed+=1;row.update(points=points,**{FLAG:True},reason='partial represented-angle CPU Horner only; scene/selector/argument production and backend-domain/material/allocations absent')
            rows.append(row)
        cases[name]={'context':ctx,'sources':rows,**dict.fromkeys(FALSE,False)}
    return {'model':MODEL,'case_order':deepcopy(case_names),'cases':cases,'runtime_probe':probe,
       'inherited_pins_verified':len(pins),'executed_source_fixture_sets':executed,'retained_sources_not_executed':stopped,
       'new_CPU_float64_RN_nodes_executed':nodes,'point_graphs_bits_MATCH':matched,'point_graphs_bits_FAIL':failed,
       'new_scene_selector_argument_encoder_executions':0,'old_numeric_producers_reexecuted':0,
       'previous_SOURCE_eight_bit_FAILs_preserved':True,'backend_domain_admitted':False,
       'cost_scope':'26 CPU nodes per fixture plus 6 probes; quarter bit permutations separately; pins/context/coeff loads/setup/scene/selector/argument/remaining costs UNMEASURED not zero',
       **dict.fromkeys(FALSE,False)}

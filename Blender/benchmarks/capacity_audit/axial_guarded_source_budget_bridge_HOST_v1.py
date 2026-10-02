"""HOST-only bridge from retained guarded-source fourteen charges to frozen INPUT quotas."""
import base64,hashlib,struct
from copy import deepcopy
from fractions import Fraction as F
import axial_guarded_source_product_RN64_CPU_v1 as prior
import axial_stage_allocation_HOST_v1 as quotas
guard=prior.guard
source=prior.source
original=prior.original
io=prior.io
allocation=prior.allocation
require=prior.require
digest=prior.digest
pair=prior.pair
FALSE=prior.FALSE
UNIT_NAMES=prior.UNIT_NAMES
MODEL='axial-retained-guarded-source-fourteen-to-six-stage-L1-HOST-v1'
PREVIOUS='coordinacion/respuestas/AXIAL-GUARDED-SOURCE-PRODUCT-RN64-CPU-001-CODEX.json'
PREVIOUS_SHA='046d9781461e573c137ec46fd07bcb7528172747b0c0f8769a88b1d5b6a51e3e'
PLAN_REPORT='coordinacion/respuestas/AXIAL-STAGE-ALLOCATION-HOST-001-CODEX.json'
PLAN_SHA='686e7c67ba7f2115de70443f38e13a5c306a70416193a91817fee3595a9eb7a8'
MAPPING={
 'source_encoding_L1':('source_encoding_L1',),
 'source_decode_RN64_L1':('source_decode_RN64_L1',),
 'source_Horner_L1':tuple('source_unit_'+n for n in ('coefficient_L1','square_L1','RN_nodes_L1','Taylor_L1')),
 'source_decoded_argument_L1':tuple('source_unit_'+n for n in ('quotient_RN64_L1','quarter_subtraction_RN64_L1','constant_2pi_L1','argument_multiply_RN64_L1')),
 'source_geometry_reference_wavelength_L1':tuple('source_unit_'+n for n in ('geometry_representation_L1','Xroot_length_rounding_L1','wavelength_representation_L1')),
 'source_product_RN64_L1':('source_product_RN64_L1',)}
UNEXECUTED='ideal_material_L1'

def load_retained():
    r=allocation.parse(io.read(PREVIOUS,PREVIOUS_SHA));require(r['task_id']=='AXIAL-GUARDED-SOURCE-PRODUCT-RN64-CPU-001','predecessor identity')
    pins=io.pins_from(r);pins[PREVIOUS]=PREVIOUS_SHA
    plan_receipt=allocation.parse(io.read(PLAN_REPORT,PLAN_SHA))
    require(plan_receipt['task_id']=='AXIAL-STAGE-ALLOCATION-HOST-001','frozen quota receipt identity')
    plan_pins=io.pins_from(plan_receipt);plan_pins[PLAN_REPORT]=PLAN_SHA
    for p,h in plan_pins.items():
        require(p not in pins or pins[p]==h,'consistent frozen branch pin collision')
        pins[p]=h
    for p,h in pins.items():io.read(p,h)
    old=io.payload(r)['data']['audit'];plans=io.payload(allocation.parse(io.read(PLAN_REPORT,PLAN_SHA)))['data']
    packets,unit,arg,quot,roots,profile,_=prior.load_retained()
    require(set(packets)==set(old['cases']),'complete retained cases')
    return packets,old,unit,arg,quot,roots,profile,pins,plans

def verify_encoder(words,retained):
    require(type(retained['new_RN32_casts']) is int and type(retained['new_RN64_subtractions']) is int and retained['zero_canonicalization_performed'] is False,'typed encoder metadata')
    require(type(retained['records']) is list and len(retained['records'])==2,'two retained component proofs')
    require(type(words) is list and len(words)==2,'two ORIGINAL source words')
    originals=[guard.bits(w,64) for w in words] # ALL input words before first cast
    limbs=[];records=[];sums=[];enc=F(0)
    for i,(w,x) in enumerate(zip(words,originals)):
        record=retained['records'][i]
        hw=record['high_uint32'];h=guard.check_RN(x,hw,32,w>>63)
        rw=record['residual_uint64']
        exact=x-h;zs=int(x==h==0 and w>>63==1 and hw>>31==0)
        res=guard.check_RN(exact,rw,64,zs)
        lw=record['low_uint32'];low=guard.check_RN(res,lw,32,rw>>63)
        represented=h+low;e=abs(represented-x);enc+=e;sums.append(represented);limbs.extend([hw,lw])
        records.append({'original_uint64':w,'high_uint32':hw,'residual_uint64':rw,'low_uint32':lw,
          'exact_residual':pair(exact),'signed_residual_RN64_delta':pair(res-exact),
          'signed_low_RN32_delta':pair(low-res),'represented_sum':pair(represented),'encoding_error_L1':pair(e)})
    raw=struct.pack('<IIII',*limbs)
    expected={'ORIGINAL_source_uint64':deepcopy(words),'limb_uint32':limbs,'records':records,
      'hilo_le_base64':base64.b64encode(raw).decode(),'hilo_le_sha256':hashlib.sha256(raw).hexdigest(),
      'exact_limb_sums':list(map(pair,sums)),'source_encoding_error_L1':pair(enc),
      'new_RN32_casts':4,'new_RN64_subtractions':2,'zero_canonicalization_performed':False}
    require(retained==expected,'retained encoder complete ledger')
    return expected

def verify_source_result(admission,retained):
    require(type(retained['new_decode_product_RN64_nodes']) is int and retained['new_decode_product_RN64_nodes']==8,'typed retained source graph count')
    for k in ('source_amplitude_budget_admitted','source_phase_bound_proved','material_applied','zero_canonicalization_performed'):require(retained[k] is False,'unchanged false source scope')
    words=admission['ORIGINAL_source_uint64'];require(type(words) is list and len(words)==2,'two source components')
    sq=[guard.bits(w,64) for w in words]
    uw=admission['unit_uint64'];require(type(uw) is list and len(uw)==2,'two retained unit words');u=[guard.bits(w,64) for w in uw]
    charges={n:guard.rational(v) for n,v in admission['unit_L1_charges'].items()};U=sum(charges.values(),F(0))
    require(set(charges)==set(UNIT_NAMES) and all(v>=0 for v in charges.values()) and U==guard.rational(admission['unit_L1_bound']) and U<1,'eleven nonnegative retained unit charges')
    encoder=verify_encoder(words,retained['source_encoder']);limbs=encoder['limb_uint32'];nodes=[];given=retained['nodes'];require(type(given) is list and len(given)==8,'eight retained SOURCE nodes')
    def node(a,b,op,label):
        aq,bq=guard.bits(a,64),guard.bits(b,64);exact=aq*bq if op=='mul' else aq+bq
        zs=(a>>63)^(b>>63) if op=='mul' else int(aq==bq==0 and a>>63==b>>63==1)
        record=given[len(nodes)];w=record['output_uint64'];q=guard.check_RN(exact,w,64,zs)
        require(record=={'label':label,'op':op,'input_uint64':[a,b],'output_uint64':w,'exact_operation':pair(exact),'signed_RN64_delta':pair(q-exact)},'retained source node edges/ledger')
        nodes.append({'label':label,'op':op,'input_uint64':[a,b],'output_uint64':w,'exact_operation':pair(exact),'signed_RN64_delta':pair(q-exact)})
        return w
    lw=[source.word(source.value(w,32)) for w in limbs] # exact widening, not rounding nodes
    a=node(lw[0],lw[1],'add','decode0');b=node(lw[2],lw[3],'add','decode1')
    ac=node(a,uw[0],'mul','ac');bd=node(b,uw[1],'mul','bd')
    ad=node(a,uw[1],'mul','ad');bc=node(b,uw[0],'mul','bc')
    re=node(ac,bd^(1<<63),'add','real');im=node(ad,bc,'add','imag')
    E=guard.rational(encoder['source_encoding_error_L1']);D=sum((abs(guard.rational(n['signed_RN64_delta'])) for n in nodes[:2]),F(0))
    N=sum((abs(guard.rational(n['signed_RN64_delta'])) for n in nodes[2:]),F(0))
    L=sum(map(abs,u),F(0));S=sum(map(abs,sq),F(0))
    detailed={'source_encoding_L1':E*L,'source_decode_RN64_L1':D*L,**{'source_unit_'+n:S*v for n,v in charges.items()},'source_product_RN64_L1':N}
    B=sum(detailed.values(),F(0));require(B==(E+D)*L+S*U+N and len(detailed)==14,'fourteen source charges')
    ref=[sq[0]*u[0]-sq[1]*u[1],sq[0]*u[1]+sq[1]*u[0]]
    obs=abs(guard.bits(re,64)-ref[0])+abs(guard.bits(im,64)-ref[1])
    require(obs<=(E+D)*L+N,'source product toward ORIGINAL times represented retained unit')
    expected={'source_encoder':encoder,'nodes':nodes,'unit_uint64':deepcopy(uw),'decoded_source_uint64':[a,b],
      'product_uint64':[re,im],'ORIGINAL_source_norm_L1':pair(S),'represented_unit_norm_L1':pair(L),
      'observed_error_to_ORIGINAL_times_represented_unit_L1':pair(obs),'detailed_source_charges_L1':{n:pair(v) for n,v in detailed.items()},
      'point_bare_source_bound_to_FIXED_ORIGINAL_L1':pair(B),'new_decode_product_RN64_nodes':8,
      'source_amplitude_budget_admitted':False,'source_phase_bound_proved':False,
      'material_applied':False,'zero_canonicalization_performed':False,
      'scope':'bare source point only; no source allocation/material/group/power/readout/full field/native GPU/RT/physical optics'}
    require(retained==expected,'retained source complete charges/result')
    return deepcopy(expected)


def admit_source(packet,ctx,index,row,unitrow,argrow,qr,rr,profile):
    snap,meta=original.snapshot_from_packet(packet,ctx);sid=ctx['source_order'][index]
    require(row['source_id']==unitrow['source_id']==sid and row[prior.FLAG] is unitrow[prior.prior.FLAG] is True,'same eligible source')
    for r in (row,unitrow):
        require(r['status']=='STOP' and all(r[n] is False for n in FALSE),'no broad promotion')
        require(r['phase_reference_id']==ctx['assignments'][index]['source_phase_reference_id'] and r['terminal_reference_id']==ctx['assignments'][index]['terminal_reference_id'],'same source gauges')
    a=prior.prior.admit(snap,index,argrow,qr,rr['result'],meta['original_path_phase_caps'][sid],profile)
    require(a==unitrow['admission'] and unitrow['retained_row_sha256']==digest(argrow),'same retained unit provenance')
    u=prior.validate_retained_unit(a,profile,unitrow['result']);require(u['point_unit_phase_charge_fits_cap'] is True,'same unit phase cap')
    fields=snap['sources'][index]['field_reim']
    for x in fields:original.number(x)
    words=[source.word(x) for x in fields]
    raw=base64.b64decode(packet['buffers_base64']['sources'],validate=True)
    require(packet['manifest']['layout']['sources']['stride_words']==32 and len(raw)==128*len(ctx['source_order']) and raw[128*index+112:128*index+128]==struct.pack('<QQ',*words),'same ORIGINAL source ABI')
    expected={'source_id':sid,'ORIGINAL_source_uint64':words,'unit_uint64':u['unit_uint64'],
      'unit_L1_charges':u['unit_L1_charges_to_FIXED_ORIGINAL'],'unit_L1_bound':u['point_unit_L1_bound_to_FIXED_ORIGINAL'],
      'retained_unit_row_sha256':digest(unitrow),'phase_reference_id':unitrow['phase_reference_id'],'terminal_reference_id':unitrow['terminal_reference_id']}
    require(row['retained_row_sha256']==digest(unitrow) and row['admission']==expected,'source admission binding')
    result=verify_source_result(expected,row['result'])
    return {'source_id':sid,'retained_source_row_sha256':digest(row),'charges_L1':result['detailed_source_charges_L1'],
      'partial_bare_source_bound_L1':result['point_bare_source_bound_to_FIXED_ORIGINAL_L1']}

def map_charges(evidence):
    detailed={k:guard.rational(v) for k,v in evidence['charges_L1'].items()}
    names=[k for v in MAPPING.values() for k in v]
    require(len(names)==len(set(names))==14 and set(names)==set(detailed) and all(v>=0 for v in detailed.values()),'each of fourteen charges mapped ONCE')
    totals={stage:sum((detailed[n] for n in names),F(0)) for stage,names in MAPPING.items()}
    B=sum(totals.values(),F(0));require(B==sum(detailed.values(),F(0))==guard.rational(evidence['partial_bare_source_bound_L1']),'six-stage exact charge conservation')
    return {k:pair(v) for k,v in totals.items()}

def compare_source(evidence,plan):
    require(evidence['source_id']==plan['source_id'],'same source plan');mapped=map_charges(evidence)
    comparisons={n:{'charge_L1':v,'quota_L1':deepcopy(plan['stages_L1'][n]),'fits':guard.rational(v)<=allocation.rational(plan['stages_L1'][n])} for n,v in mapped.items()}
    total=guard.rational(evidence['partial_bare_source_bound_L1']);totalfits=total<=allocation.rational(plan['cap_L1'])
    return {'source_id':evidence['source_id'],'retained_source_row_sha256':evidence['retained_source_row_sha256'],
      'fourteen_charges_L1':deepcopy(evidence['charges_L1']),'six_stage_charges_L1':mapped,'stage_comparisons':comparisons,
      'partial_bare_source_bound_L1':pair(total),'source_cap_L1':deepcopy(plan['cap_L1']),'partial_total_fits_source_cap':totalfits,
      'partial_six_stage_comparison_fits':totalfits and all(t['fits'] for t in comparisons.values()),
      'unexecuted_stages':{UNEXECUTED:{'charge_L1':None,'quota_L1':deepcopy(plan['stages_L1'][UNEXECUTED]),'executed':False,'fits':None}},
      'reason':'six-stage point comparison ONLY; material error unknown/not zero, no source phase/field acceptance',**dict.fromkeys(FALSE,False)}

def audit_budget_bridge_HOST(case_names,plans_by_case,*,model):
    require(model==MODEL,'explicit HOST budget bridge')
    require(type(case_names) is list and 1<=len(case_names)<=64 and all(type(n) is str and n for n in case_names) and len(set(case_names))==len(case_names),'bounded unique case list')
    require(type(plans_by_case) is dict and set(plans_by_case)<=set(case_names),'selected static INPUT plans only')
    packets,old,unit,arg,quot,roots,profile,pins,controls=load_retained();require(set(case_names)<=set(packets),'known cases')
    admitted={}
    # ALL INPUT plans validated BEFORE ANY numerical charges are inspected.
    for name in case_names:
        ctx,plan=quotas.validate_plan(packets[name],digest(packets[name]),plans_by_case.get(name),model=quotas.MODEL)
        require(ctx==old['cases'][name]['context']==unit['cases'][name]['context']==arg['cases'][name]['context']==quot['cases'][name]['context']==roots['cases'][name]['context'],'same complete INPUT context')
        for c in (old['cases'][name],unit['cases'][name]):
            require([r['source_id'] for r in c['sources']]==ctx['source_order'] and all(c[n] is False for n in FALSE),'source order/nonpromotion')
        admitted[name]=(ctx,plan)
    evidences={}
    # Admit ALL requested available point proofs before ANY quota comparisons.
    for name,(ctx,plan) in admitted.items():
        ev={}
        if plan['allocation_INPUT_valid']:
            for i,row in enumerate(old['cases'][name]['sources']):
                require(type(row[prior.FLAG]) is bool,'typed eligibility')
                require(row['status']=='STOP' and all(row[n] is False for n in FALSE),'source nonpromotion')
                if row[prior.FLAG]:ev[i]=admit_source(packets[name],ctx,i,row,unit['cases'][name]['sources'][i],arg['cases'][name]['sources'][i],quot['cases'][name]['sources'][i],roots['cases'][name]['sources'][i],profile)
        evidences[name]=ev
    cases={};valid=missing=compared=fits=0
    for name,(ctx,plan) in admitted.items():
        rows=[];valid+=int(plan['allocation_INPUT_valid']);missing+=int(not plan['allocation_INPUT_valid'])
        for i,row in enumerate(old['cases'][name]['sources']):
            if i in evidences[name]:
                v=compare_source(evidences[name][i],plan['sources'][i]);compared+=1;fits+=int(v['partial_six_stage_comparison_fits'])
            else:
                reason=plan['reason'] if not plan['allocation_INPUT_valid'] else row['reason']
                v={'source_id':row['source_id'],'partial_six_stage_comparison_fits':False,'stage_comparisons':None,
                  'unexecuted_stages':None,'reason':reason,'retained_source_row_sha256':digest(row),**dict.fromkeys(FALSE,False)}
            rows.append(v)
        cases[name]={'context':ctx,'allocation_INPUT':plan,'sources':rows,'status':'STOP',**dict.fromkeys(FALSE,False)}
    return {'model':MODEL,'case_order':deepcopy(case_names),'cases':cases,'charge_mapping':deepcopy(MAPPING),
      'inherited_pins_verified':len(pins),'explicit_INPUT_plans_valid':valid,'missing_INPUT_plans_STOP':missing,
      'partial_source_comparisons':compared,'partial_six_stage_comparisons_fit':fits,'new_native_numeric_operations':0,
      'old_native_stages_suites_reexecuted':0,'material_charge_invented_as_zero':False,'allocation_policy_adopted':False,
      'cost_scope':'HOST pure retained proof and quota comparison only; IO/pins/setup/upstream/remaining costs UNMEASURED never zero',**dict.fromkeys(FALSE,False)}

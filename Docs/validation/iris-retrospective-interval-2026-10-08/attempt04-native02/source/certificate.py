"""Retrospective rational error bounds for archived canonical Iris readbacks.

No Blender, GPU, producer, mpmath or numerical-auditor import. This bounds the
observed output error for the exact represented algebraic model, not triangle
traversal, physical optics, a new trial, or a universal compiler guarantee.
"""
import argparse
import csv
from fractions import Fraction as F
import hashlib
import io
import json
import math
from pathlib import Path
import shutil
import struct
import sys
import time
import uuid

ROOT=Path(__file__).resolve().parents[1]
MATH=ROOT/'Blender/benchmarks/capacity_audit/rational_interval_v1.py'
sys.path.insert(0,str(MATH.parent))
import rational_interval_v1 as interval_math
from rational_interval_v1 import Interval as I, error_upper, pi_interval, sincos, upward_float

def need(ok,message):
    if not ok: raise ValueError(message)

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def read(path):
    raw=Path(path).read_bytes()
    need(len(raw)<=16*2**20,'bounded JSON')
    def pairs(values):
        out={}
        for k,v in values:
            need(k not in out,'duplicate JSON key')
            out[k]=v
        return out
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _:(_ for _ in ()).throw(ValueError('nonfinite JSON')))

def exponent(value,terms=128):
    """Bound exp at an exact rational point by positive Taylor plus tail.

    For x>=0, tail from t_(N+1) is <=t_(N+1)/(1-x/(N+2)).
    Negative values use reciprocal monotonicity. No float exp is used.
    """
    x=F(value)
    need(abs(x)<=32,'bounded exponent domain')
    if x<0:
        return I(1)/exponent(-x,terms)
    total=F(1);term=F(1)
    for n in range(1,terms+1):
        term=term*x/n
        total+=term
    first=term*x/(terms+1)
    ratio=x/(terms+2)
    need(ratio<1,'convergent geometric tail')
    return I.rounded(total,total+first/(1-ratio))

def zero(): return I(0),I(0)
def add(a,b): return a[0]+b[0],a[1]+b[1]
def neg(a): return -a[0],-a[1]
def scale(a,b): return a[0]*b,a[1]*b
def mul(a,b): return a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0]
def conjugate(a): return a[0],-a[1]
def ph(value):
    s,c=sincos(value)
    return c,s

def transfer(theta,geometry):
    wavelength,gap,spacing,xa,xb,ya,yb=map(F,geometry)
    k=2*pi_interval()/wavelength
    X=[F(0)];Y=[F(0)]
    for i in range(1,4):
        X.append(X[-1]+spacing+xa*i+xb*i*i)
        Y.append(Y[-1]+spacing+ya*i+yb*i*i)
    ax=[[zero()for _ in range(8)]for _ in range(16)]
    ay=[[zero()for _ in range(8)]for _ in range(16)]
    U=[[zero()for _ in range(8)]for _ in range(8)]
    gap_phase=ph(k*gap)
    for j in range(4):ax[j][j]=gap_phase
    for i in range(4):ay[4*i][4+i]=gap_phase
    for i in range(4):
        for j in range(4):
            cell=4*i+j
            e1=ph(k*5+F(theta[cell]));e2=ph(k*3)
            summed=add(e1,e2)
            diagonal=(summed[1]/2,-summed[0]/2)
            upper=scale(add(e1,neg(e2)),F(1,2))
            horizontal=[add(mul(diagonal,a),mul(upper,b))for a,b in zip(ax[cell],ay[cell])]
            vertical=[add(mul(neg(upper),a),mul(diagonal,b))for a,b in zip(ax[cell],ay[cell])]
            if i<3:
                link=ph(k*(X[i+1]-X[i]-1))
                ax[cell+4]=[mul(v,link)for v in horizontal]
            else:U[j]=[mul(v,gap_phase)for v in horizontal]
            if j<3:
                link=ph(k*(Y[j+1]-Y[j]-2))
                ay[cell+1]=[mul(v,link)for v in vertical]
            else:U[4+i]=[mul(v,gap_phase)for v in vertical]
    # Necessary invariant check; inclusion alone is not the full model proof.
    for i in range(8):
        for j in range(8):
            value=zero()
            for p in range(8):value=add(value,mul(conjugate(U[p][i]),U[p][j]))
            need(value[0].contains(int(i==j)) and value[1].contains(0),'unitarity invariant inclusion')
    return U

def pair_wire(z):return {'real':z[0].wire(),'imag':z[1].wire()}
def complex_error(observed,reference):return error_upper(observed[0],reference[0])+error_upper(observed[1],reference[1])

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--archive',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--interval-bits',type=int,choices=[128,256,384],default=256)
    args=parser.parse_args()
    # Private checker process only; original module source and historical jobs
    # remain unchanged. Outward dyadic arithmetic is valid at each resolution.
    interval_math.BITS=args.interval_bits
    interval_math.GRID=1<<args.interval_bits
    interval_math.pi_interval.cache_clear()
    archive=args.archive.resolve();output=args.output.resolve()
    need(archive.is_relative_to(ROOT) and archive.is_dir(),'archive inside checkout')
    need(output.is_relative_to(ROOT),'output inside checkout')
    output.mkdir(parents=True,exist_ok=False)
    source_dir=output/'source';source_dir.mkdir()
    shutil.copyfile(__file__,source_dir/'certificate.py')
    shutil.copyfile(MATH,source_dir/'rational_interval_v1.py')
    sources={str(Path(__file__).relative_to(ROOT)):sha(__file__),str(MATH.relative_to(ROOT)):sha(MATH)}
    started=time.perf_counter()
    worker_path=archive/'worker.json';guard_path=archive/'guard.json'
    worker=read(worker_path);guard=read(guard_path)
    need(worker['status']=='PASS' and worker['native_gpu_executed'] is True,'existing native execution receipt')
    need(guard['status']=='PASS' and guard['worker_exit_code']==0 and guard['cleanup_confirmed'] is True and
         guard['worker_report_sha256']==sha(worker_path),'existing guard/readback binding')
    need(worker['job_id']==guard['job_id'] and str(uuid.UUID(worker['job_id']))==worker['job_id'],'bound existing job')
    need(worker['backend']=='OPENGL' and 'NVIDIA' in worker['vendor'] and 'RTX 3090' in worker['renderer'] and
         worker['background'] is False,'archived hardware/domain')
    candidates=list((archive/'source/Docs/validation/iris-native-circuit-2026-10-08').glob('inputs*/input_manifest.json'))
    manifest_path=next((p for p in candidates if sha(p)==worker['input_manifest_sha256']),None)
    need(manifest_path is not None,'archived manifest preimage')
    manifest=read(manifest_path);assets=manifest['assets']
    state_path=archive/'source'/assets['trained_path'];csv_path=archive/'source'/assets['dataset_path']
    need(sha(state_path)==assets['trained_sha256'] and sha(csv_path)==assets['dataset_sha256'],'archived raw assets')
    state=read(state_path)
    csv_rows=list(csv.reader(io.StringIO(csv_path.read_text(encoding='utf-8'))))[1:]
    need(len(csv_rows)==150,'complete frozen source dataset')
    features=[[float(x)for x in row[:4]]for row in csv_rows]
    expected_cases=['baseline','phase','sham']
    need([c['case_id']for c in manifest['cases']]==expected_cases and
         [c['case_id']for c in worker['gpu_readback_records']]==expected_cases,'complete fixed cases')
    results=[];maximum={'amplitude':F(0),'field_l1':F(0),'power':F(0),'logit':F(0),'power_from_field':F(0),'norm':F(0),'normalized_power_balance':F(0)}
    native_hasher=hashlib.sha256();decisions=0;records=[]
    for case,record in zip(manifest['cases'],worker['gpu_readback_records']):
        packet_path=archive/'source'/case['packet_path']
        need(packet_path.is_relative_to(archive/'source') and sha(packet_path)==case['packet_sha256'],'pinned archived packet')
        packet=read(packet_path);wire=bytes.fromhex(packet['wire_hex'])
        need(len(wire)==5200 and hashlib.sha256(wire).hexdigest()==packet['wire_sha256'],'raw wire')
        header=struct.unpack('<32I',wire[:128])
        need(header[:11]==(0x4e33434c,1,32,1300,150,32,1232,1264,1280,1282,1284) and
             header[11]==0 and header[12:16]==(3,8,16,4) and not any(header[16:]) and wire[-8:]==bytes(8),'wire layout')
        def data(offset,count):return list(struct.unpack('<%dd'%count,wire[offset*4:(offset+2*count)*4]))
        raw_features=data(32,600);theta=data(1232,16);scaler=data(1264,8);ref=data(1280,1)[0];log_gain=data(1282,1)[0];geometry=data(1284,7)
        declared_theta=list(state['theta'])
        if case['case_id']=='phase':declared_theta[0]+=.1
        need(raw_features==[v for row in features for v in row] and theta==declared_theta and
             scaler==state['scaler_lo']+state['scaler_hi'] and ref==state['ref'] and log_gain==state['logt'] and
             geometry==[.1,1.,4.,.0137,.0031,.0211,.0017],'source-to-wire semantics')
        nonce=int.from_bytes(hashlib.sha256((worker['job_id']+'/'+case['case_id']).encode()).digest()[:4],'little')&0x7fffffff
        need(record['nonce']==nonce and nonce>0,'archived fresh nonce binding')
        echo=bytes.fromhex(record['input_echo_hex']);raw=bytes.fromhex(record['result_hex'])
        need(echo==wire+bytes((-len(wire))%256) and len(raw)==150*128*4,'full historical echo/result')
        native_hasher.update(echo);native_hasher.update(raw)
        U=transfer(theta,geometry);gain=exponent(F(log_gain))
        case_max={k:F(0)for k in maximum};certified=0;row_records=[]
        for row in range(150):
            base=row*512
            words=struct.unpack('<128I',raw[base:base+512])
            need(words[:6]==(0x49334e52,1,row,1,nonce,nonce^0xffffffff) and 0<=words[6]<3 and
                 words[7:12]==(16,8,3,150,1) and not any(words[90:]),'typed complete row')
            def native(offset):
                value=struct.unpack('<d',raw[base+offset*4:base+(offset+2)*4])[0]
                need(math.isfinite(value),'finite archived output')
                return F(value)
            x=[(F(raw_features[4*row+j])-F(scaler[j]))/(F(scaler[4+j])-F(scaler[j]))for j in range(4)]
            norm2=sum((v*v for v in x),F(ref)*F(ref));norm=I(norm2).sqrt()
            source=[I(x[0])/norm,I(x[1])/norm,I(0),I(0),I(x[2])/norm,I(x[3])/norm,I(F(ref))/norm,I(0)]
            fields=[];intensities=[];field_bounds=[];power_bounds=[];power_chain=[];amplitude_bounds=[]
            for mode in range(8):
                value=zero()
                for p in range(8):value=add(value,scale(U[mode][p],source[p]))
                fields.append(value)
                intensity=value[0].square()+value[1].square();intensities.append(intensity)
                observed=(native(16+4*mode),native(18+4*mode))
                bound=complex_error(observed,value);field_bounds.append(bound)
                native_power=native(48+2*mode)
                power_bounds.append(error_upper(native_power,intensity))
                squared=observed[0]**2+observed[1]**2
                absolute_upper=I(squared).sqrt().hi
                chain=abs(native_power-squared)+2*absolute_upper*bound+bound*bound
                power_chain.append(chain)
                amplitude_bounds.append(error_upper(native(70+2*mode),source[mode]))
            logits=[gain*p for p in intensities[:3]]
            logit_bounds=[error_upper(native(64+2*i),logits[i])for i in range(3)]
            prediction=words[6]
            decision_ok=logits[prediction].lo>max(logits[j].hi for j in range(3)if j!=prediction)
            certified+=int(decision_ok)
            # The exact canonical circuit is lossless and the exact source is
            # normalized. This is field norm balance, not joules of GPU energy.
            normalized_balance=max(abs(native(86)-1),abs(native(88)-1),
                                   abs(sum((native(48+2*m)for m in range(8)),F(0))-1))
            local={'amplitude':max(amplitude_bounds),'field_l1':max(field_bounds),'power':max(power_bounds),
                   'logit':max(logit_bounds),'power_from_field':max(power_chain),
                   'normalized_power_balance':normalized_balance,
                   'norm':max(error_upper(native(12),I(norm2)),error_upper(native(14),norm))}
            for k,v in local.items():case_max[k]=max(case_max[k],v)
            row_records.append({'row':row,'fields_reference':[pair_wire(v)for v in fields],
                                'field_l1_error_upper':[str(v)for v in field_bounds],
                                'powers_reference':[v.wire()for v in intensities],
                                'power_error_upper':[str(v)for v in power_bounds],
                                'field_to_native_power_error_upper':[str(v)for v in power_chain],
                                'logits_reference':[v.wire()for v in logits],
                                'logit_error_upper':[str(v)for v in logit_bounds],
                                'native_prediction':prediction,'decision_certified':decision_ok})
        for k,v in case_max.items():maximum[k]=max(maximum[k],v)
        decisions+=certified
        result={'case_id':case['case_id'],'certified_decisions':certified,'rows':row_records,
                'maximum_upper_rational':{k:str(v)for k,v in case_max.items()},
                'maximum_upper_display':{k:upward_float(v)for k,v in case_max.items()}}
        results.append(result)
        print(json.dumps({'case':case['case_id'],'certified_decisions':certified,
                          'maximum_upper_display':result['maximum_upper_display']}),flush=True)
        records.append({'case_id':case['case_id'],'packet_sha256':sha(packet_path)})
    # Same utility thresholds as the historical circuit protocol, not tuned now.
    limits={'amplitude':F(1,10**12),'field_l1':F(1,10**11),'power':F(1,10**11),'logit':F(1,10**9)}
    useful=all(maximum[k]<=v for k,v in limits.items()) and decisions==450
    need(all(sha(ROOT/p)==s for p,s in sources.items()),'certificate sources unchanged')
    report={'schema':'neuro3d.archived_iris.rational_output_certificate.v1',
            'status':'CERTIFIED_WITHIN_HISTORICAL_UTILITY'if useful else 'CERTIFIED_ERROR_EXCEEDS_UTILITY_OR_DECISION_UNRESOLVED',
            'analysis':'RETROSPECTIVE_MATHEMATICAL_AUDIT_EXISTING_DATA',
            'interval_bits':args.interval_bits,'trig_Taylor_terms':32,'Machin_arctan_terms':64,
            'model':'exact_represented_canonical_algebraic_Iris_circuit',
            'new_native_execution':False,'native_triangle_traversal_certified':False,
            'captured_Blender_geometry_certified':False,'physical_accuracy_certified':False,
            'H1_confirmatory':False,'novelty_demonstrated':False,
            'native_worker_sha256':sha(worker_path),'native_guard_sha256':sha(guard_path),
            'manifest_sha256':sha(manifest_path),'native_readback_sha256':native_hasher.hexdigest(),
            'certificate_source_hashes':sources,'packets':records,
            'certified_decisions':decisions,'maximum_upper_rational':{k:str(v)for k,v in maximum.items()},
            'maximum_upper_display':{k:upward_float(v)for k,v in maximum.items()},
            'utility_limits_rational':{k:str(v)for k,v in limits.items()},'cases':results,
            'analysis_elapsed_seconds':time.perf_counter()-started,
            'timing_is_not_native_task_total_cost':True}
    path=output/'certificate.json';path.write_bytes((json.dumps(report,indent=2)+'\n').encode())
    print(json.dumps({k:report[k]for k in ['status','certified_decisions','maximum_upper_display','native_readback_sha256']}))
    return 0 if useful else 2

if __name__=='__main__':
    try:sys.exit(main())
    except Exception as error:
        print(json.dumps({'status':'ERROR','error_type':type(error).__name__,'message':str(error)}),file=sys.stderr)
        raise

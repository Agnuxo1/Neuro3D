"""Independent post-readback audit: analytic local 2x2 transfer matrices at 90dps.

No producer, Blender, GL, packet, or readback modules are imported. GPU sees
neither this high-precision U nor labels. This is a diagnostic, not a proof of
physical accuracy or a rigorous native floating-point interval certificate.
"""
import argparse
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import struct
import uuid
import mpmath as mp

ROOT=Path(__file__).resolve().parents[2]
mp.mp.dps=90


def need(condition,message):
    if not condition:raise ValueError(message)


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    data=Path(path).read_bytes();need(len(data)<=16*2**20,'bounded audit JSON')
    def pairs(items):
        out={}
        for key,value in items:need(key not in out,'duplicate JSON key');out[key]=value
        return out
    return json.loads(data,object_pairs_hook=pairs,parse_constant=lambda _:(_ for _ in ()).throw(ValueError('nonfinite JSON')))


def transfer(theta,geometry):
    # Reference uses analytic two-port coefficients, independent of the
    # producer's splitter/mirror operations. U is built only AFTER readback.
    wavelength,gap,spacing,xa,xb,ya,yb=map(mp.mpf,geometry);kw=2*mp.pi/wavelength
    X=[mp.mpf(0)];Y=[mp.mpf(0)]
    for i in range(1,4):X.append(X[-1]+spacing+xa*i+xb*i*i);Y.append(Y[-1]+spacing+ya*i+yb*i*i)
    ax=[[mp.mpc(0) for _ in range(8)] for _ in range(16)]
    ay=[[mp.mpc(0) for _ in range(8)] for _ in range(16)]
    U=mp.matrix(8,8);ph=lambda a:mp.exp(mp.j*a);g=ph(kw*gap)
    for j in range(4):ax[j][j]=g
    for i in range(4):ay[4*i][4+i]=g
    for i in range(4):
        for j in range(4):
            cell=4*i+j;e1=ph(kw*5+mp.mpf(theta[cell]));e2=ph(kw*3)
            diagonal=-mp.j*(e1+e2)/2;upper=(e1-e2)/2
            horizontal=[diagonal*a+upper*b for a,b in zip(ax[cell],ay[cell])]
            vertical=[-upper*a+diagonal*b for a,b in zip(ax[cell],ay[cell])]
            if i<3:ax[cell+4]=[v*ph(kw*(X[i+1]-X[i]-1)) for v in horizontal]
            else:
                for p,v in enumerate(horizontal):U[j,p]=g*v
            if j<3:ay[cell+1]=[v*ph(kw*(Y[j+1]-Y[j]-2)) for v in vertical]
            else:
                for p,v in enumerate(vertical):U[4+i,p]=g*v
    unitarity=max(abs((U.H*U)[i,j]-(1 if i==j else 0)) for i in range(8) for j in range(8))
    return U,unitarity


def raw_decode(raw,nonce):
    need(len(raw)==150*128*4,'full native output length');words=struct.unpack('<19200I',raw);rows=[]
    for row in range(150):
        o=row*128;w=words[o:o+128]
        need(w[:6]==(0x49334e52,1,row,1,nonce,nonce^0xffffffff) and 0<=w[6]<3 and
             w[7:12]==(16,8,3,150,1) and all(v==0 for v in w[90:]),'independent header/coverage/nonce/reserved')
        def num(p):return struct.unpack('<d',raw[(o+p)*4:(o+p+2)*4])[0]
        fields=[mp.mpc(num(16+4*p),num(18+4*p)) for p in range(8)]
        powers=[num(48+2*p) for p in range(8)];logits=[num(64+2*p) for p in range(3)]
        encoded=[num(70+2*p) for p in range(8)];misc=[num(p) for p in (12,14,86,88)]
        need(all(math.isfinite(v) for v in [*powers,*logits,*encoded,*misc]) and
             all(mp.isfinite(v.real) and mp.isfinite(v.imag) for v in fields),'all outputs finite')
        rows.append((fields,powers,logits,encoded,w[6],misc))
    return rows


def audit(worker_path,guard_path,manifest_path):
    worker=read(worker_path);guard=read(guard_path);manifest=read(manifest_path)
    need(worker['status']=='PASS' and worker['verification_passed'] is True and
         worker['schema']=='neuro3d.iris_lattice.native_report.v1','native worker PASS')
    need(guard['status']=='PASS' and guard['cleanup_confirmed'] is True and guard['worker_exit_code']==0 and
         guard['native_gpu_execution_verified'] is True and guard['worker_report_sha256']==sha(worker_path),'guard bound PASS/cleanup')
    need(worker['job_id']==guard['job_id'] and str(uuid.UUID(worker['job_id']))==worker['job_id'] and
         worker['input_manifest_sha256']==sha(manifest_path),'immutable job/manifest binding')
    need(worker['native_gpu_executed'] is True and worker['background'] is False and worker['backend']=='OPENGL' and
         'NVIDIA' in worker['vendor'] and 'RTX 3090' in worker['renderer'],'native verified hardware context')
    assets=manifest['assets'];state_path=ROOT/assets['trained_path'];csv_path=ROOT/assets['dataset_path']
    need(sha(state_path)==assets['trained_sha256'] and sha(csv_path)==assets['dataset_sha256'],'frozen assets')
    state=read(state_path);csv_rows=list(csv.reader(io.StringIO(csv_path.read_text(encoding='utf-8'))))[1:]
    need(len(csv_rows)==150 and state['scaler_fit']=='train rows only','full raw dataset and training-only scaler')
    need(len(state['train_idx'])==120 and len(state['test_idx'])==30 and
         set(state['train_idx']).isdisjoint(state['test_idx']) and set(state['train_idx']+state['test_idx'])==set(range(150)),'frozen complete partition')
    features=[[float(v) for v in r[:4]] for r in csv_rows];truth=[['setosa','versicolor','virginica'].index(r[4]) for r in csv_rows]
    for i in range(4):
        need(min(features[r][i] for r in state['train_idx'])==state['scaler_lo'][i] and
             max(features[r][i] for r in state['train_idx'])==state['scaler_hi'][i],'scaler actually matches train rows')
    need([r['case_id'] for r in worker['gpu_readback_records']]==['baseline','phase','sham'] and
         worker['gpu_dispatch_count']==worker['completed_readbacks']==3,'complete three-case coverage')
    need([r['case_id'] for r in manifest['cases']]==['baseline','phase','sham'],'fixed control ordering')
    hasher=hashlib.sha256();results=[];numeric_raws=[];source_assets={str(state_path.relative_to(ROOT)):sha(state_path),str(csv_path.relative_to(ROOT)):sha(csv_path)}
    for case,record in zip(manifest['cases'],worker['gpu_readback_records']):
        path=ROOT/case['packet_path'];need(sha(path)==case['packet_sha256'],'pinned packet SHA');p=read(path)
        wire=bytes.fromhex(p['wire_hex']);need(hashlib.sha256(wire).hexdigest()==p['wire_sha256'] and len(wire)==5200,'raw full ingress')
        h=struct.unpack('<32I',wire[:128]);need(h[:11]==(0x4e33434c,1,32,1300,150,32,1232,1264,1280,1282,1284) and h[11]==0 and
                                             h[12:16]==(3,8,16,4) and not any(h[16:]) and wire[-8:]==bytes(8),'canonical ingress header/padding')
        def doubles(offset,count):return list(struct.unpack('<%dd'%count,wire[offset*4:(offset+2*count)*4]))
        actual_features=doubles(32,600);theta=doubles(1232,16);scaler=doubles(1264,8);ref=doubles(1280,1)[0];gain=doubles(1282,1)[0];geometry=doubles(1284,7)
        expected_theta=list(state['theta'])
        if case['case_id']=='phase':expected_theta[0]+=.1
        need(actual_features==[v for r in features for v in r] and theta==expected_theta and
             scaler==state['scaler_lo']+state['scaler_hi'] and ref==state['ref'] and gain==state['logt'] and
             geometry==[.1,1.,4.,.0137,.0031,.0211,.0017],'wire contains only declared raw features/parameters')
        need(p['trained_sha256']==sha(state_path) and p['dataset_sha256']==sha(csv_path),'packet-to-assets binding')
        nonce=int.from_bytes(hashlib.sha256((worker['job_id']+'/'+case['case_id']).encode()).digest()[:4],'little')&0x7fffffff
        need(record['nonce']==nonce and nonce>0,'fresh expected case nonce')
        echo=bytes.fromhex(record['input_echo_hex']);raw=bytes.fromhex(record['result_hex'])
        need(echo==wire+bytes((-len(wire))%256),'independent raw echo')
        hasher.update(echo);hasher.update(raw);observed=raw_decode(raw,nonce);numeric_raws.append(raw)
        U,unitarity=transfer(theta,geometry);need(unitarity<mp.mpf('1e-80'),'high-precision reference is unitary')
        maxima=dict(amplitude=mp.mpf(0),field_l1=mp.mpf(0),power=mp.mpf(0),logit=mp.mpf(0),energy=mp.mpf(0),norm=mp.mpf(0))
        expected_predictions=[];per_row=[];smallest_margin=mp.inf
        for row,(fields,powers,logits,amps,pred,misc) in enumerate(observed):
            x=[(mp.mpf(features[row][i])-mp.mpf(scaler[i]))/(mp.mpf(scaler[4+i])-mp.mpf(scaler[i])) for i in range(4)]
            a=mp.matrix([x[0],x[1],0,0,x[2],x[3],mp.mpf(ref),0]);norm2=sum(v*v for v in a);norm=mp.sqrt(norm2);a=a/norm
            expected=U*a;intensity=[abs(v)**2 for v in expected];g=mp.exp(mp.mpf(gain));expected_pred=max(range(3),key=lambda i:intensity[i]);expected_predictions.append(expected_pred)
            need(pred==expected_pred,'GPU class differs at sample %d in %s'%(row,case['case_id']))
            sorted_class=sorted(intensity[:3],reverse=True);smallest_margin=min(smallest_margin,sorted_class[0]-sorted_class[1])
            error_a=max(abs(mp.mpf(amps[i])-a[i]) for i in range(8))
            error_e=max(abs(fields[i].real-expected[i].real)+abs(fields[i].imag-expected[i].imag) for i in range(8))
            error_p=max(abs(mp.mpf(powers[i])-intensity[i]) for i in range(8))
            error_l=max(abs(mp.mpf(logits[i])-g*intensity[i]) for i in range(3))
            energy=max(abs(mp.mpf(misc[2])-1),abs(mp.mpf(misc[3])-1),abs(sum(map(mp.mpf,powers))-mp.mpf(misc[3])))
            norm_error=max(abs(mp.mpf(misc[0])-norm2),abs(mp.mpf(misc[1])-norm))
            for key,error in zip(maxima,(error_a,error_e,error_p,error_l,energy,norm_error)):maxima[key]=max(maxima[key],error)
            need(error_a<=mp.mpf('1e-12') and error_e<=mp.mpf('1e-11') and error_p<=mp.mpf('1e-11') and error_l<=mp.mpf('1e-9'),'prospective numeric acceptance at sample %d in %s'%(row,case['case_id']))
            per_row.append({'sample_index':row,'GPU_prediction':pred,'reference_prediction':expected_pred,'truth':truth[row],
                            'max_field_l1_error':str(error_e),'max_power_error':str(error_p),'class_margin_reference':str(sorted_class[0]-sorted_class[1])})
        train=sum(expected_predictions[r]==truth[r] for r in state['train_idx']);test=sum(expected_predictions[r]==truth[r] for r in state['test_idx'])
        if case['case_id']=='baseline':need((train,test)==(117,29),'frozen historical baseline not reproduced')
        results.append({'case_id':case['case_id'],'all150_decisions_match':True,'samples':150,'modes':8,
                        'all_outputs_compared':True,'train_correct':train,'train_total':120,'test_correct':test,'test_total':30,
                        'max_errors':{k:str(v) for k,v in maxima.items()},'reference_unitarity_error':str(unitarity),
                        'minimum_class_margin':str(smallest_margin),'rows':per_row})
    need(hasher.hexdigest()==worker['gpu_readback_sha256']==guard['gpu_readback_sha256'],'complete raw digest')
    # Nonce fields are the only numerical-output differences allowed for sham.
    for row in range(150):
        baseline=numeric_raws[0][row*512:(row+1)*512];sham=numeric_raws[2][row*512:(row+1)*512]
        need(baseline[:16]+baseline[24:]==sham[:16]+sham[24:],'sham changes numerical bits at sample '+str(row))
    baseline=raw_decode(numeric_raws[0],worker['gpu_readback_records'][0]['nonce'])
    phase=raw_decode(numeric_raws[1],worker['gpu_readback_records'][1]['nonce'])
    causal=max(abs(b[0][i]-p[0][i]) for b,p in zip(baseline,phase) for i in range(8))
    need(causal>mp.mpf('1e-3'),'phase intervention has no specified causal effect')
    return {'schema':'neuro3d.iris_lattice.independent_audit.v1','status':'PASS','mpmath_version':mp.__version__,'reference_dps':90,
            'worker_report_sha256':sha(worker_path),'guard_report_sha256':sha(guard_path),'input_manifest_sha256':sha(manifest_path),
            'auditor_sha256':sha(__file__),'gpu_readback_sha256':hasher.hexdigest(),'frozen_assets_sha256':source_assets,
            'cases':results,'maximum_phase_control_field_change':str(causal),'sham_numeric_bits_identical':True,
            'scope':'complete canonical scalar circuit native GPU; all 150 rows/8 modes/16 cells/18 parameters; empirical numerical diagnostic',
            'new_generalization_claimed':False,'GPU_triangle_traversal_certified':False,'physical_optics_certified':False,
            'native_complete_interval_certificate':False}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--worker',type=Path,required=True);parser.add_argument('--guard',type=Path,required=True)
    parser.add_argument('--input-manifest',type=Path,required=True);parser.add_argument('--out',type=Path,required=True);args=parser.parse_args()
    try:result=audit(args.worker,args.guard,args.input_manifest)
    except Exception as error:
        result={'schema':'neuro3d.iris_lattice.independent_audit.v1','status':'FAIL','error':type(error).__name__+': '+str(error),
                'auditor_sha256':sha(__file__),'worker_report_sha256':sha(args.worker),'guard_report_sha256':sha(args.guard)}
    with args.out.open('xb') as stream:stream.write((json.dumps(result,indent=2,allow_nan=False)+'\n').encode())
    print(json.dumps({k:result.get(k) for k in ('status','error','gpu_readback_sha256','maximum_phase_control_field_change')}))
    return 0 if result['status']=='PASS' else 1


if __name__=='__main__':raise SystemExit(main())

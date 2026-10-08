"""Raw frozen Iris/scaler/local-optics ingress. No CPU inference or labels in wire."""
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import struct

ROOT=Path(__file__).resolve().parents[3]
SCHEMA='neuro3d.iris_lattice.native_job.v1'
MAGIC=0x4e33434c
RESULT_MAGIC=0x49334e52
HEADER_WORDS=32
ROW_WORDS=128
SAMPLES=150


def need(ok,message):
    if not ok: raise ValueError(message)


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def double_words(values):
    need(all(type(v) in (int,float) and not isinstance(v,bool) and math.isfinite(v) for v in values),'finite doubles')
    return list(struct.unpack('<%dI'%(len(values)*2),struct.pack('<%dd'%len(values),*values)))


def prepare(output):
    output=Path(output).resolve()
    need(output.is_relative_to(ROOT),'inputs must live inside this checkout')
    need(not output.exists(),'fresh circuit inputs required'); output.mkdir(parents=True)
    trained=ROOT/'Blender/demo_lattice_iris/trained_lattice.json'; dataset=trained.with_name('iris.csv')
    state=json.loads(trained.read_bytes()); rows=list(csv.reader(io.StringIO(dataset.read_text(encoding='utf-8'))))[1:]
    need(len(rows)==SAMPLES and all(len(row)==5 for row in rows),'complete raw Iris rows')
    raw_features=[[float(v) for v in row[:4]] for row in rows]
    need(len(state['theta'])==16 and len(state['train_idx'])==120 and len(state['test_idx'])==30,'full frozen network/split')
    need(set(state['train_idx']).isdisjoint(state['test_idx']) and set(state['train_idx']+state['test_idx'])==set(range(SAMPLES)),'disjoint full split')
    need(state['scaler_fit']=='train rows only' and all(hi>lo for lo,hi in zip(state['scaler_lo'],state['scaler_hi'])),'saved train-only scaler')
    need(0.01<=state['ref']<=10 and -32<=state['logt']<=32,'bounded reference/gain')
    base={}; cases=[]
    for name in ('baseline','phase','sham'):
        theta=list(state['theta'])
        if name=='phase': theta[0]+=.1
        words=[0]*HEADER_WORDS
        words[:5]=[MAGIC,1,HEADER_WORDS,0,SAMPLES]
        payloads=[('features',[v for row in raw_features for v in row]),('theta',theta),
                  ('scaler',[*state['scaler_lo'],*state['scaler_hi']]),('reference',[state['ref']]),
                  ('log_gain',[state['logt']]),('geometry',[.1,1.,4.,.0137,.0031,.0211,.0017])]
        layout={}
        for name_index,(key,values) in enumerate(payloads):
            words[5+name_index]=len(words); layout[key]={'word_offset':len(words),'doubles':len(values)}
            words.extend(double_words(values))
        while len(words)%4: words.append(0)
        words[3]=len(words); words[12:16]=[3,8,16,4]
        raw=struct.pack('<%dI'%len(words),*words)
        need(len(raw)<=32768 and len(raw)%16==0,'bounded std140 uvec4 wire')
        packet={'schema':'neuro3d-iris-circuit-raw-binary64-v1','wire_hex':raw.hex(),
                'wire_sha256':hashlib.sha256(raw).hexdigest(),'layout':layout,'rows':SAMPLES,
                'output_row_words':ROW_WORDS,'trained_sha256':sha(trained),'dataset_sha256':sha(dataset)}
        destination=output/(name+'.packet.json')
        destination.write_bytes((json.dumps(packet,indent=2,allow_nan=False)+'\n').encode())
        cases.append({'case_id':name,'packet_path':destination.relative_to(ROOT).as_posix(),
                      'packet_sha256':sha(destination)})
        base[name]=raw
    need(base['baseline']==base['sham'] and base['baseline']!=base['phase'],'causal controls differ only as specified')
    manifest={'schema':SCHEMA,'expected_backend':'OPENGL','expected_renderer_contains':'RTX 3090',
              'limits':{'samples':SAMPLES,'cells':16,'modes':8,'dispatches':3,'output_row_words':ROW_WORDS},
              'assets':{'trained_path':trained.relative_to(ROOT).as_posix(),'trained_sha256':sha(trained),
                        'dataset_path':dataset.relative_to(ROOT).as_posix(),'dataset_sha256':sha(dataset)},'cases':cases}
    path=output/'input_manifest.json'; path.write_bytes((json.dumps(manifest,indent=2,allow_nan=False)+'\n').encode())
    return path


def packet_path(case):
    path=Path(case['packet_path']); path=path if path.is_absolute() else ROOT/path
    path=path.resolve(); need(path.is_file() and sha(path)==case['packet_sha256'],'pinned circuit packet')
    return path


def admit(packet):
    need(type(packet) is dict and packet.get('schema')=='neuro3d-iris-circuit-raw-binary64-v1','circuit packet schema')
    need(set(packet)=={'schema','wire_hex','wire_sha256','layout','rows','output_row_words','trained_sha256','dataset_sha256'},'closed packet metadata')
    need(packet['rows']==SAMPLES and packet['output_row_words']==ROW_WORDS,'complete packet metadata')
    need(type(packet['wire_hex']) is str and len(packet['wire_hex'])<=65536,'bounded wire hex')
    raw=bytes.fromhex(packet['wire_hex']); need(hashlib.sha256(raw).hexdigest()==packet['wire_sha256'],'circuit wire hash')
    need(len(raw)<=32768 and len(raw)%16==0,'std140 wire bound')
    words=list(struct.unpack('<%dI'%(len(raw)//4),raw))
    need(words[:3]==[MAGIC,1,HEADER_WORDS] and words[3]==len(words) and words[4]==SAMPLES,'circuit wire header')
    need(words[12:16]==[3,8,16,4] and all(v==0 for v in words[11:12]+words[16:HEADER_WORDS]),'closed circuit header')
    counts=[600,16,8,1,1,7]; cursor=HEADER_WORDS; decoded=[]; layout={}
    for i,(key,count) in enumerate(zip(('features','theta','scaler','reference','log_gain','geometry'),counts)):
        need(words[5+i]==cursor,'canonical payload offsets')
        layout[key]={'word_offset':cursor,'doubles':count}
        values=struct.unpack('<%dd'%count,raw[cursor*4:(cursor+2*count)*4])
        need(all(math.isfinite(v) for v in values),'finite ingress values')
        decoded.append(values)
        cursor+=2*count
    need(0<=len(words)-cursor<4 and all(v==0 for v in words[cursor:]),'complete closed payload and zero padding')
    need(packet['layout']==layout,'canonical packet layout metadata')
    features,phases,scaler,reference,gain,geometry=decoded
    need(all(abs(v)<=20 for v in features) and all(abs(v)<=64 for v in phases),'bounded features/phases')
    need(all(scaler[i+4]>scaler[i] for i in range(4)),'positive scaler ranges')
    need(.01<=reference[0]<=10 and -32<=gain[0]<=32,'bounded normalization/gain')
    need(geometry==(.1,1.,4.,.0137,.0031,.0211,.0017),'frozen canonical geometry constants')
    return raw


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(); parser.add_argument('--out',type=Path,required=True)
    print(prepare(parser.parse_args().out))

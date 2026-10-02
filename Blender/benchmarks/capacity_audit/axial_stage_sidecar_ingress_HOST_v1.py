"""Bounded strict UTF-8 JSON sidecar ingress; INPUT only, no numerical producer."""
import hashlib,json,re
import axial_stage_allocation_HOST_v1 as prior
io=prior.io
allocation=prior.allocation
require=prior.require
digest=prior.digest
MODEL='axial-seven-stage-sidecar-UTF8-SHA-bounded-HOST-v1'
SCHEMA='axial-seven-stage-allocation-sidecar-v1'
PREVIOUS='coordinacion/respuestas/AXIAL-STAGE-ALLOCATION-HOST-001-CODEX.json'
PREVIOUS_SHA='686e7c67ba7f2115de70443f38e13a5c306a70416193a91817fee3595a9eb7a8'
FALSE=prior.FALSE
MAX_BYTES=65536
MAX_DEPTH=12
MAX_CONTAINERS=2048
MAX_INTEGER_DIGITS=96
MAX_STRING_UTF8_BYTES=256
TOKEN=re.compile(r'"(?:[^"\\]|\\.)*"|-?(?:0|[1-9][0-9]*)|true|false|null|[{}\[\],:]')
SHA=re.compile(r'[0-9a-f]{64}')
LIMITS={'max_bytes':MAX_BYTES,'max_depth':MAX_DEPTH,'max_containers':MAX_CONTAINERS,
        'max_integer_digits':MAX_INTEGER_DIGITS,'max_string_UTF8_bytes':MAX_STRING_UTF8_BYTES}
def sha(raw):return hashlib.sha256(raw).hexdigest()
def load_retained():
    r=allocation.parse(io.read(PREVIOUS,PREVIOUS_SHA))
    require(r['task_id']=='AXIAL-STAGE-ALLOCATION-HOST-001','previous task identity')
    pins=io.pins_from(r);pins[PREVIOUS]=PREVIOUS_SHA
    for p,h in pins.items():io.read(p,h)
    def data(p):return io.payload(allocation.parse(io.read(p,pins[p])))
    old=io.payload(r)['data']['real_absent'];packets=data(io.INGRESS)['packets']
    packets.update({n:v['parent'] for n,v in data(io.PRESENCE)['synthetic_controls'].items()})
    require(set(packets)==set(old['cases']),'complete retained INPUT cases')
    return packets,old,pins

def preflight(raw):
    require(type(raw) is bytes and 0<len(raw)<=MAX_BYTES,'bounded nonempty bytes INPUT')
    require(not raw.startswith(b'\xef\xbb\xbf'),'UTF-8 BOM excluded by explicit wire contract')
    text=raw.decode('utf-8',errors='strict')
    pos=0;stack=[];containers=depth=integers=strings=0
    while pos<len(text):
        if text[pos] in ' \t\r\n':pos+=1;continue
        m=TOKEN.match(text,pos);require(m is not None,'strict JSON token: floats/nonfinite/comments/invalid escape syntax excluded')
        t=m.group();pos=m.end()
        if t in ('{','['):
            stack.append(t);containers+=1;depth=max(depth,len(stack))
            require(depth<=MAX_DEPTH and containers<=MAX_CONTAINERS,'wire depth/container resource bound')
        elif t in ('}',']'):
            require(stack and stack.pop()==('{' if t=='}' else '['),'balanced matching containers')
        elif t.startswith('"'):
            # Decode only bounded string token, then bound decoded UTF-8 size.
            require(len(t)<=6*MAX_STRING_UTF8_BYTES+2,'bounded escaped string token')
            s=json.loads(t);require(len(s.encode('utf-8',errors='strict'))<=MAX_STRING_UTF8_BYTES,'decoded UTF-8 string resource bound')
            strings+=1
        elif t[0]=='-' or t[0].isdigit():
            require(len(t.lstrip('-'))<=MAX_INTEGER_DIGITS,'integer digit resource bound before global JSON parse')
            integers+=1
    require(not stack,'closed containers')
    return text,{'bytes':len(raw),'maximum_depth':depth,'containers':containers,'integer_tokens':integers,'string_tokens':strings}

def parse_unique(text):
    def unique(pairs):
        d={}
        for k,v in pairs:
            require(k not in d,'duplicate decoded JSON key, including escaped aliases')
            d[k]=v
        return d
    def integer(token):
        require(len(token.lstrip('-'))<=MAX_INTEGER_DIGITS,'bounded integer');return int(token)
    def invalid(token):raise ValueError('floats/nonfinite excluded: '+token)
    return json.loads(text,object_pairs_hook=unique,parse_int=integer,parse_float=invalid,parse_constant=invalid)

def receive(packet,raw,receipt,*,model):
    require(model==MODEL,'explicit sidecar ingress HOST model')
    require(type(receipt) is dict and set(receipt)=={'bytes','sha256'},'wire receipt whitelist')
    require(type(receipt['bytes']) is int and 0<receipt['bytes']<=MAX_BYTES,'typed bounded receipt length')
    require(type(receipt['sha256']) is str and SHA.fullmatch(receipt['sha256']) is not None,'lowercase exact SHA256')
    require(type(raw) is bytes and len(raw)==receipt['bytes'] and sha(raw)==receipt['sha256'],'exact raw byte receipt BEFORE parsing')
    text,stats=preflight(raw);env=parse_unique(text)
    require(type(env) is dict and set(env)=={'schema','input_packet_sha256','plan'},'sidecar envelope whitelist')
    require(env['schema']==SCHEMA and type(env['input_packet_sha256']) is str and
            SHA.fullmatch(env['input_packet_sha256']) is not None and env['input_packet_sha256']==digest(packet),'schema and complete INPUT packet SHA')
    require(type(env['plan']) is dict,'explicit plan object; serialized null is NOT missing sidecar')
    ctx,result=prior.validate_plan(packet,env['input_packet_sha256'],env['plan'],model=prior.MODEL)
    require(result['allocation_INPUT_valid'] is True,'complete stage INPUT accounting')
    return {'schema':SCHEMA,'raw_wire_receipt':dict(receipt),'wire_preflight':stats,'limits':dict(LIMITS),
        'context':ctx,'allocation_INPUT':result,'canonical_envelope_sha256':digest(env),
        'status':'STOP','reason':'sidecar INPUT admitted only; no numerical charge comparison or policy adoption',
        'numerical_charge_comparisons':0,'allocation_policy_adopted':False,**dict.fromkeys(FALSE,False)}

def serialize(packet,plan,*,model):
    require(model==MODEL,'explicit sidecar ingress HOST model')
    _,result=prior.validate_plan(packet,digest(packet),plan,model=prior.MODEL)
    require(result['allocation_INPUT_valid'] is True,'cannot serialize missing/invalid plan')
    env={'schema':SCHEMA,'input_packet_sha256':digest(packet),'plan':plan}
    raw=allocation.canon(env);preflight(raw)
    return raw,{'bytes':len(raw),'sha256':sha(raw)}

def audit_ingress_HOST(case_names,sidecars_by_case,*,model):
    require(model==MODEL,'explicit sidecar ingress HOST model')
    require(type(case_names) is list and 1<=len(case_names)<=64 and all(type(n) is str and n for n in case_names)
            and len(set(case_names))==len(case_names),'bounded unique cases')
    require(type(sidecars_by_case) is dict and set(sidecars_by_case)<=set(case_names),'selected sidecars only')
    packets,old,pins=load_retained();require(set(case_names)<=set(packets),'known cases')
    cases={};admitted=missing=0
    for n in case_names:
        entry=sidecars_by_case.get(n)
        if entry is None:
            ctx,result=prior.validate_plan(packets[n],digest(packets[n]),None,model=prior.MODEL);missing+=1
            out={'context':ctx,'allocation_INPUT':result,'status':'STOP','reason':'absent wire sidecar; no default plan/zero',
                'numerical_charge_comparisons':0,'allocation_policy_adopted':False,**dict.fromkeys(FALSE,False)}
        else:
            require(type(entry) is dict and set(entry)=={'raw','receipt'},'sidecar entry whitelist')
            out=receive(packets[n],entry['raw'],entry['receipt'],model=model);admitted+=1
        require(out['context']==old['cases'][n]['context'],'same retained complete INPUT context')
        cases[n]=out
    # No result is returned if any entry rejects: atomic API result, no external writer.
    return {'model':MODEL,'case_order':list(case_names),'cases':cases,'limits':dict(LIMITS),'inherited_pins_verified':len(pins),
        'sidecar_INPUT_admitted':admitted,'missing_sidecars_STOP':missing,'numerical_charge_comparisons':0,
        'new_numeric_producers_executed':0,'old_suites_producers_reexecuted':0,'allocation_policy_adopted':False,
        'cost_scope':'bounded HOST byte parsing/SHA/INPUT accounting only; IO/pins/setup/rational/upstream/remaining UNMEASURED, not full costs or benchmark',
        **dict.fromkeys(FALSE,False)}

"""Independent evidence audit. No imports of production or native computation."""
import base64,hashlib,json,zlib
from fractions import Fraction as F
from pathlib import Path
R=Path(__file__).resolve().parents[2]
P=R/'coordinacion/respuestas/AXIAL-TAGGED-SOURCE-UNIT-MATERIAL-LINK-HOST-001-CODEX.json'
def h(b):return hashlib.sha256(b).hexdigest()
def dig(v):return h(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
def data(r):
 t=r['test_run'];s=t.get('stdout_zlib_base64') or ''.join(t['stdout_zlib_base64_chunks']);b=zlib.decompress(base64.b64decode(s,validate=True))
 assert len(b)==t['stdout_bytes'] and h(b)==t['stdout_sha256'];return json.loads(b)['data']
def val(w):
 assert type(w) is int and 0<=w<1<<64;e=w>>52&2047;m=w&((1<<52)-1);assert e<2047 and (e or m==0)
 return (-1 if w>>63 else 1)*F(m+(1<<52) if e else m)*F(2)**((e or 1)-1075)
r=json.loads(P.read_bytes());pins=r['code_doc_sha256'];assert len(pins)==537
for p,s in pins.items():assert h((R/p).read_bytes())==s,p
d=data(r);req=d['request'];out=d['audit'];assert out['links']==2 and len(out['sources'])==4 and out['group_admissions']==0
assert len(out['proof_scope'])==38 and all(v is False for v in out['proof_scope'].values())
parent=data(json.loads((R/'coordinacion/respuestas/AXIAL-TAGGED-SOURCE-ORIGINAL-POINT-BOUND-HOST-001-CODEX.json').read_bytes()))
assert dig(req['A_POINT_INPUT'])==dig(parent['request']) and dig(req['A_POINT_OUTPUT'])==dig(parent['audit'])
for key,path in [('bare_OUTPUT','AXIAL-GUARDED-SOURCE-PRODUCT-RN64-CPU-001-CODEX.json'),('material_OUTPUT','AXIAL-CURRENT-SOURCE-IDEAL-REFLECTION-CPU-001-CODEX.json')]:
 assert dig(req[key])==dig(data(json.loads((R/'coordinacion/respuestas'/path).read_bytes()))['audit'])
src=req['A_POINT_INPUT']['transport_INPUT']['decoder_INPUT']['SOURCE_limb_records'];tr=req['A_POINT_INPUT']['transport_OUTPUT']['sources']
for i,row in enumerate(out['sources']):
 a=req['A_POINT_OUTPUT']['sources'][i];name,sid=src[i]['case_name'],src[i]['source_id']
 assert (row['case_name'],row['source_id'])==(name,sid)==(a['case_name'],a['source_id'])
 assert row['A_point_row_sha256']==dig(a) and row['reference']=='fixed ORIGINAL A * exact exp(i ORIGINAL path phase) * ideal minus one'
 bc=req['bare_OUTPUT']['cases'][name];mc=req['material_OUTPUT']['cases'][name];ctx=bc['context'];assert dig(ctx)==dig(mc['context'])==src[i]['context_sha256']
 j=ctx['source_order'].index(sid);b=bc['sources'][j];m=mc['sources'][j];l=row['ledger']
 assert row['phase_bound_rad'] is None and row['phase_quota_fits'] is None and row['new_product_or_material_executed'] is False
 if l is None:assert b.get('result') is None and m.get('result') is None and row['retained_operand_link_proved'] is False;continue
 v=b['result'];mv=m['result'];ad=b['admission'];p=a['proof']
 assert p['decoded_uint64']==v['decoded_source_uint64'] and p['ORIGINAL_uint64']==ad['ORIGINAL_source_uint64']
 assert ad['unit_uint64']==v['unit_uint64'] and l['bare_row_sha256']==dig(b) and l['material_row_sha256']==dig(m)
 S=sum(map(lambda w:abs(val(w)),p['ORIGINAL_uint64']),F(0));L=sum(map(lambda w:abs(val(w)),v['unit_uint64']),F(0))
 E=sum((F(*s['encoding_error_abs']) for s in src[i]['scalars']),F(0));D=sum((F(*s['decode_error_abs']) for s in tr[i]['decoded_scalars']),F(0))
 assert E+D==F(*p['point_error_L1_bound']);u=ad['unit_L1_charges'];assert len(u)==11 and sum((F(*q) for q in u.values()),F(0))==F(*ad['unit_L1_bound'])
 expected={'source_encoding_L1':E*L,'source_decode_RN64_L1':D*L,**{'source_unit_'+k:S*F(*q) for k,q in u.items()},'source_product_RN64_L1':F(*v['detailed_source_charges_L1']['source_product_RN64_L1']),'ideal_material_L1':F(0)}
 assert len(expected)==15 and expected=={k:F(*q) for k,q in l['charges'].items()}=={k:F(*q) for k,q in mv['fifteen_source_material_charges_L1'].items()}
 assert sum(expected.values(),F(0))==F(*l['total'])==F(*mv['point_reflected_source_bound_to_FIXED_ORIGINAL_L1'])
 assert mv['input_uint64']==v['product_uint64'] and l['retained_reflected_uint64']==mv['reflected_uint64']
 assert all(z==w^(1<<63) for w,z in zip(mv['input_uint64'],mv['reflected_uint64']))
 assert l['context_sha256']==dig(ctx) and mv['material_profile']['ideal_coefficient_exact_reim']==[[-1,1],[0,1]]
 assign=ctx['assignments'][j]
 assert ad['phase_reference_id']==mv['phase_reference_id']==assign['source_phase_reference_id']
 assert ad['terminal_reference_id']==mv['terminal_reference_id']==assign['terminal_reference_id']
assert len(d['rejections'])==12 and all(x['rejected'] is True and x['emissions']==0 for x in d['rejections'])
assert d['typed_rejections']==12 and d['missing']['missing_sources']==19
print(json.dumps({'PASS':True,'pins':len(pins),'links':2,'missing_downstream':2,'new_native_operations':0,'phase_quota_fits':None}))

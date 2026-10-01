"""Scene word ABI and checked integer axial geometry; CPU model, not native."""
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import struct
from history_lineage_cpu_v2 import scene_binding
from exp005_blender_gpu import split_double
from axial_selector_int256_cpu_v1 import decode32_scaled
from axial_relative_gate_cpu_v1 import ratio
from axial_root_margin_cpu_v1 import exact_nonnegative

ROOT=Path(__file__).resolve().parents[3]
PREVIOUS='coordinacion/respuestas/AXIAL-REDUCTION-ARGUMENT-RN64-001-CODEX.json'
SHA='b355de12848533fb13c02b171f7459c1c8ad2689ae2f65e11f3e81cf793dfe24'
MODEL='scene-hilo32-axial-geometry-signed512-CPU-v1'
S=1<<149
MIN=-(1<<511);MAX=(1<<511)-1


def checked(n):
    if type(n) is not int or not MIN<=n<=MAX:raise ValueError('signed512 overflow/type; no wrap')
    return n


def word512(n):
    checked(n);u=n if n>=0 else n+(1<<512)
    return [(u>>(32*i))&0xffffffff for i in range(16)]


def pins():
    raw=(ROOT/PREVIOUS).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SHA:raise ValueError('previous report SHA mismatch')
    r=json.loads(raw)
    for n,h in r['code_doc_sha256'].items():
        if hashlib.sha256((ROOT/n).read_bytes()).hexdigest()!=h:raise ValueError('changed frozen input '+n)
    return dict(r['code_doc_sha256'],**{PREVIOUS:SHA})


def pair(value):
    hi,lo=split_double(value)
    words=[struct.unpack('<I',struct.pack('<f',v))[0] for v in (hi,lo)]
    center=checked(sum(map(decode32_scaled,words)))
    error=abs(F(value)-F(center,S));q=error*S
    radius=checked((q.numerator+q.denominator-1)//q.denominator)
    return words,center,radius


def encode_scene(snapshot,extra_radius_BU):
    """HOST only: scene pack/order + outward encoding enclosures, no hits."""
    binding,p=scene_binding(snapshot);extra=exact_nonnegative(extra_radius_BU);q=extra*S
    extra_scaled=checked((q.numerator+q.denominator-1)//q.denominator)
    triangles=[];original_planes={}
    for start in range(0,len(p.geometry.triangles),12):
        row=p.geometry.triangles[start:start+12];owner=int(row[3])
        if row[3]!=owner:raise ValueError('packed owner index required')
        points=[row[i:i+3] for i in (0,4,8)]
        if len({F(v[0]) for v in points})!=1:raise ValueError('original X-normal triangles required')
        x=F(points[0][0])
        if owner in original_planes and original_planes[owner]!=x:raise ValueError('one original plane per owner required')
        original_planes[owner]=x;encoded=[];radius=0
        for xyz in points:
            v=[]
            for i,value in enumerate(xyz):
                words,center,r=pair(value)
                if i and F(center,S)!=F(value):raise ValueError('unchanged exact YZ required')
                if not i:radius=max(radius,r)
                v.append(words)
            encoded.append(v)
        triangles.append({'owner':owner,'vertices_uint32_hilo':encoded,'X_radius_scaled':checked(radius+extra_scaled)})
    sources=[]
    for i,sid in enumerate(p.source_ids):
        row=p.sources[8*i:8*i+8];v=[];radius=0
        for j,value in enumerate(row[:3]):
            words,center,r=pair(value)
            if j and F(center,S)!=F(value):raise ValueError('unchanged exact source YZ required')
            if not j:radius=r
            v.append(words)
        direction=[]
        for value in row[4:7]:
            words,center,_=pair(value)
            if F(center,S)!=F(value):raise ValueError('unchanged source direction required')
            direction.append(words)
        sources.append({'source_id':sid,'origin_uint32_hilo':v,'direction_uint32_hilo':direction,
                        'X_radius_scaled':checked(radius+extra_scaled)})
    w,wc,wr=pair(p.wavelength_BU)
    for name,obj in snapshot['objects'].items():
        if obj['kind']=='mirror' and F(obj['phase_rad'])!=0:raise ValueError('mirror original phase zero required')
    bundle={'model':MODEL,'original_scene_binding_sha256':binding,'object_ids':list(p.geometry.object_ids),
            'kinds':[snapshot['objects'][n]['kind'] for n in p.geometry.object_ids],
            'source_order':list(p.source_ids),'sources':sources,'triangles':triangles,
            'wavelength_uint32_hilo':w,'wavelength_radius_scaled':wr,
            'extra_radius_HOST_BU_rational':ratio(extra),
            'extra_radius_HOST_outward_inflation_BU_rational':ratio(F(extra_scaled,S)-extra)}
    body=json.dumps(bundle,sort_keys=True,separators=(',',':'),allow_nan=False)
    return bundle,hashlib.sha256(body.encode()).hexdigest(),original_planes


def geometry_words(bundle,*,geometry_model):
    """Checked integer branch core. No Fraction, float, supplied hit/length."""
    if geometry_model!=MODEL or bundle['model']!=MODEL:raise ValueError('explicit geometry words CPU model required')
    ids=bundle['source_order'];owners=bundle['object_ids']
    if not 1<=len(ids)<=3 or len(set(ids))!=len(ids) or any(type(n) is not str or not n for n in ids) or ids!=[s['source_id'] for s in bundle['sources']]:
        raise ValueError('ordered unique bounded source IDs required')
    if not owners or len(set(owners))!=len(owners) or len(bundle['kinds'])!=len(owners) or not 1<=len(bundle['triangles'])<=64:
        raise ValueError('bounded owner/triangle ABI required')
    trace=[]
    def op(a,b,kind,label):
        checked(a);checked(b)
        v=checked(a+b if kind=='add' else (a-b if kind=='sub' else a*b))
        trace.append({'label':label,'op':kind,'input_words_signed512':[word512(a),word512(b)],'output_words_signed512':word512(v)})
        return v
    def decode(words):
        if not isinstance(words,list) or len(words)!=2:raise ValueError('two normal-or-zero uint32 limbs required')
        return op(decode32_scaled(words[0]),decode32_scaled(words[1]),'add','coordinate.decode')
    def cross(a,b,c,d,label):
        return op(op(a,d,'mul',label+'.m1'),op(b,c,'mul',label+'.m2'),'sub',label+'.sub')
    ts=[];planes={}
    for pid,t in enumerate(bundle['triangles']):
        owner=t['owner']
        if type(owner) is not int or not 0<=owner<len(bundle['object_ids']):raise ValueError('scene owner slot required')
        xyz=[[decode(w) for w in v] for v in t['vertices_uint32_hilo']]
        if len(xyz)!=3 or len({v[0] for v in xyz})!=1:raise ValueError('one decoded X plane required')
        radius=checked(t['X_radius_scaled'])
        if radius<0:raise ValueError('nonnegative geometry radius required')
        plane=(xyz[0][0],op(xyz[0][0],radius,'sub','plane.lo'),op(xyz[0][0],radius,'add','plane.hi'))
        if owner in planes and planes[owner]!=plane:raise ValueError('one shared decoded plane per owner required')
        planes[owner]=plane;ts.append((pid,owner,xyz))
    rows=[]
    for src in bundle['sources']:
        out={'source_id':src['source_id'],'accepted_geometry_words_CPU_only':False,'segments':[]}
        try:
            origin=[decode(w) for w in src['origin_uint32_hilo']];direction=[decode(w) for w in src['direction_uint32_hilo']]
            if direction not in ([S,0,0],[-S,0,0]):raise ValueError('signed unit X ray required')
            sign=1 if direction[0]>0 else -1;interior=[];misses=[]
            for pid,owner,t in ts:
                a,b,c=t;by=op(b[1],a[1],'sub','YZ.by');bz=op(b[2],a[2],'sub','YZ.bz')
                cy=op(c[1],a[1],'sub','YZ.cy');cz=op(c[2],a[2],'sub','YZ.cz')
                py=op(origin[1],a[1],'sub','YZ.py');pz=op(origin[2],a[2],'sub','YZ.pz')
                det=cross(by,bz,cy,cz,'YZ.det');u=cross(py,pz,cy,cz,'YZ.u');v=cross(by,bz,py,pz,'YZ.v')
                if det==0:raise ValueError('nondegenerate YZ projection required')
                if det<0:det,u,v=checked(-det),checked(-u),checked(-v)
                w=op(op(det,u,'sub','YZ.w1'),v,'sub','YZ.w2')
                if min(u,v,w)<0:misses.append(pid);continue
                if min(u,v,w)==0:raise ValueError('boundary hit excluded; no snap')
                interior.append((pid,owner))
            radius=checked(src['X_radius_scaled'])
            if radius<0:raise ValueError('nonnegative source radius required')
            def select(olo,ohi,s,departure=None):
                candidates=[];skip=[];behind=[]
                for pid,owner in interior:
                    if departure is not None and owner==departure:skip.append(pid);continue
                    _,lo,hi=planes[owner]
                    low=op(lo,ohi,'sub','root.lo');high=op(hi,olo,'sub','root.hi')
                    if s<0:low,high=checked(-high),checked(-low)
                    if high<0:behind.append(pid);continue
                    if low<=0:raise ValueError('other owner zero contact' if departure is not None else 'source zero contact')
                    candidates.append((pid,owner,low,high))
                if not candidates:raise ValueError('no strictly positive root')
                chosen=min(candidates,key=lambda c:c[2]);pid,owner,lo,hi=chosen
                gaps=[]
                for pp,oo,_,_ in candidates:
                    if pp==pid:continue
                    _,cl,ch=planes[oo];_,wl,wh=planes[owner]
                    gap=op(cl,wh,'sub','root.gap') if s>0 else op(wl,ch,'sub','root.gap')
                    gaps.append(gap)
                if gaps and min(gaps)<=0:raise ValueError('competitor intervals overlap/touch')
                return {'primitive_id':pid,'owner':owner,'segment_interval_scaled':[lo,hi],
                        'competitor_clearance_scaled':min(gaps) if gaps else None,
                        'same_owner_departures_skipped':skip,'behind':behind}
            slo=op(origin[0],radius,'sub','source.lo');shi=op(origin[0],radius,'add','source.hi')
            first=select(slo,shi,sign);mo=first['owner']
            if bundle['kinds'][mo]!='mirror':raise ValueError('first event must be mirror')
            _,ml,mh=planes[mo]
            # Derive departure from the accepted SAME plane variable; not caller previous-id.
            second=select(ml,mh,-sign,mo);do=second['owner']
            if bundle['kinds'][do] not in ('det','escape'):raise ValueError('second event must be terminal')
            _,dl,dh=planes[do]
            low=op(op(op(2,ml,'mul','length.2Mlo'),shi,'sub','length.minusShi'),dh,'sub','length.minusDhi')
            high=op(op(op(2,mh,'mul','length.2Mhi'),slo,'sub','length.minusSlo'),dl,'sub','length.minusDlo')
            if sign<0:low,high=checked(-high),checked(-low)
            if low<=0:raise ValueError('nonpositive complete length')
            out.update(accepted_geometry_words_CPU_only=True,segments=[first,second],mirror_owner=mo,terminal_owner=do,
                       length_interval_scaled=[low,high],projected_misses=misses,direction_sign=sign)
        except ValueError as e:out['reason']=str(e)
        rows.append(out)
    return {'sources':rows,'integer_operations':len(trace),'operations':trace,'geometry_model':MODEL}


def audit_scene_geometry_words(snapshot,*,geometry_model,phase_budget_rad,extra_radius_BU=0):
    if geometry_model!=MODEL:raise ValueError('explicit geometry words CPU model required')
    frozen=pins();budget=exact_nonnegative(phase_budget_rad)
    bundle,wordsha,original_planes=encode_scene(snapshot,extra_radius_BU)
    result=geometry_words(bundle,geometry_model=MODEL)
    wl=sum(map(decode32_scaled,bundle['wavelength_uint32_hilo']));wr=bundle['wavelength_radius_scaled']
    if wl-wr<=0:raise ValueError('positive wavelength enclosure required')
    for row,src in zip(result['sources'],snapshot['sources']):
        row['accepted_phase_budget_CPU_only']=False
        if not row['accepted_geometry_words_CPU_only']:continue
        mo,do=row['mirror_owner'],row['terminal_owner'];sign=row['direction_sign']
        original=sign*(2*original_planes[mo]-F(src['position_BU'][0])-original_planes[do])
        lo,hi=row['length_interval_scaled'];low,high=F(lo,S),F(hi,S)
        if not low<=original<=high:raise ValueError('original length outside declared enclosure')
        cycles=original/F(snapshot['lambda_BU'])
        phase=8*max(abs(F(lo,wl+wr)-cycles),abs(F(hi,wl-wr)-cycles))
        row.update(original_length_BU_rational=ratio(original),length_interval_BU_rational=[ratio(low),ratio(high)],
                   phase_error_bound_rad=ratio(phase),phase_budget_rad=ratio(budget),
                   phase_reference_id='original-source-zero:'+bundle['original_scene_binding_sha256']+':'+src['id'],
                   accepted_phase_budget_CPU_only=phase<=budget)
    return {**result,'scene_snapshot':snapshot,'word_ABI':bundle,'word_ABI_sha256':wordsha,'pins_verified':frozen,
            'accepted_geometry_words_CPU_only':all(r['accepted_geometry_words_CPU_only'] for r in result['sources']),
            'accepted_phase_budget_CPU_only':all(r['accepted_phase_budget_CPU_only'] for r in result['sources']),
            'GPU_executed':False,'ALU_executed':False,'native_geometry_implemented':False,'execution_authenticated':False,
            'accepted_full_field_pipeline':False,'field_values_computed':False,'native_promotion_allowed':False,
            'scope':'HOST encoded original scene -> checked integer word geometry; HOST outward enclosures and original-gauge phase bound; not shader arithmetic/runtime'}

"""Scene-bound binary64 pair transport + actual native recenter; no predicate admission."""
from fractions import Fraction as F
from pathlib import Path
import struct,hashlib,copy
import oblique_finite_interval_HOST_v1 as host
import position_pair_recenter_native_CPU_v1 as native
ROOT=Path(__file__).resolve().parents[3]
MODEL="oblique-scene-pair64-recenter-CPU-v1"
POLICY="ALL15_EXACT_PAIR_WORDS_COMMON_SOURCE0_CONSTANT_KEEP_RADII"
PINS={
 "Blender/benchmarks/capacity_audit/position_pair_recenter_native_CPU_v1.py":"f7b6251f45af2c355d78dfec0d593a8f8b014f13a90a728f85871cc7bd22d0d2",
 "Blender/benchmarks/capacity_audit/oblique_pair64_difference_CPU_v1.py":"902dfb1030a41bc6594806d0cef6d00729bbc11b4eade0adb96a23b3f688774e",
 "Blender/benchmarks/capacity_audit/oblique_finite_interval_HOST_v1.py":"72db45c04ea1bb9b26e3752eb11bb860d79bf20e1bb3dd48bbfd3fb979d20b56"}
def pair(v):return [v.numerator,v.denominator]
def require(ok,why):
    if not ok:raise ValueError(why)
def recenter(scene,q):
    out=dict(backend=MODEL,status="STOP_INPUT",reason=None,frame=None,ledger=[],
        packet_bytes=0,decoded_words=0,native_RN64_operations=0,native_sign_flips=0,
        native_hi_lo_recenter_executed=False,reference_uncertainty="EXACT_CHOSEN_CONSTANT_NOT_ACTUAL_SOURCE_ERROR",
        predicate_calls=0,HOST_recenter_substitution=False,source_uncertainty_cancelled=False,
        physical_visibility_certified=False,phase_certified=False,scene_authenticated=False,
        GPU_used=False,promotion="STOP_DOWNSTREAM_PHYSICAL_GPU",full_costs="UNKNOWN_NOT_ZERO")
    try:
        for p,h in PINS.items():require(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,"pinned_dependency:"+p)
        host.keys(q,("backend","policy","snapshot_sha256","scene_query","packet_hex","packet_sha256"))
        require(q["backend"]==MODEL and q["policy"]==POLICY,"closed_backend_policy")
        require(q["snapshot_sha256"]==host.digest(scene),"snapshot_binding")
        host.validate(scene,q["scene_query"])  # schema/intervals only; no HOST classifier
        text=q["packet_hex"]
        require(type(text)is str and len(text)==480,"ALL15_pairs_240bytes")
        raw=bytes.fromhex(text)
        require(raw.hex()==text and len(raw)==240 and hashlib.sha256(raw).hexdigest()==q["packet_sha256"],"canonical_packet_identity")
        out.update(packet_bytes=240,snapshot_sha256=host.digest(scene),request_sha256=host.digest(q),
                   packet_sha256=q["packet_sha256"])
        floats=[];decoded=[]
        for i in range(30):
            word=raw[8*i:8*i+8];b=int.from_bytes(word,"little");exp=(b>>52)&2047
            require(exp!=2047 and (exp!=0 or b&((1<<63)-1)==0),"normal_zero_input_words")
            v=struct.unpack("<d",word)[0]
            floats.append(v);decoded.append(F.from_float(v));out["decoded_words"]+=1
        for i in range(15):
            n=host.POINTS[i//3];j=i%3
            require(decoded[2*i]+decoded[2*i+1]==F(*scene["points"][n]["nominal"][j]),"inexact_pair_input:"+n+":"+str(j))
        centered=copy.deepcopy(scene)
        centered["scene_id"]+="/NATIVE-PAIR64";centered["context"]+="/NATIVE-PAIR64"
        out["status"]="STOP_NATIVE"
        for i in range(15):
            n=host.POINTS[i//3];j=i%3
            aa=tuple(floats[2*i:2*i+2]);bb=tuple(floats[2*j:2*j+2])
            r=native.subtract(aa,bb)
            out["native_RN64_operations"]+=r["native_RN64_operations"]
            out["native_sign_flips"]+=2 if r["native_RN64_operations"] else 0
            out["native_hi_lo_recenter_executed"]|=r["CPU_native_executed"]
            item=dict(point=n,axis=j,input_words=[raw[16*i:16*i+8].hex(),raw[16*i+8:16*i+16].hex()],
                reference_words=[raw[16*j:16*j+8].hex(),raw[16*j+8:16*j+16].hex()],
                radius=scene["points"][n]["radius"][j],native_result=r)
            out["ledger"].append(item)
            require(r["status"]=="CONTROL_ONLY","native_graph_STOP:"+str(r["reason"]))
            # Exact HOST subtraction audits only; the output is decoded NATIVE words.
            require(r["exact_pair_difference"] is True,"inexact_native_difference_STOP")
            y=F.from_float(struct.unpack("<d",bytes.fromhex(r["hi_word_le_hex"]))[0])
            y+=F.from_float(struct.unpack("<d",bytes.fromhex(r["lo_word_le_hex"]))[0])
            require(pair(y)==r["decoded_debug_BU"],"native_output_words")
            centered["points"][n]["nominal"][j]=pair(y)
        cq=dict(q["scene_query"],snapshot_sha256=host.digest(centered),context=centered["context"])
        host.validate(centered,cq)  # same frozen domain, ALL radii unchanged
        out.update(status="CPU_NATIVE_PAIR64_RECENTER_ONLY",reason="EXACT_TRANSPORT_NOT_PREDICATE",
            frame=dict(scene=centered,scene_query=cq,snapshot_sha256=host.digest(centered),
                reference=scene["points"]["origin"]["nominal"],coordinate_representation="EXACT_DECODED_NATIVE_PAIR64",
                output_packet_hex="".join(x["native_result"]["hi_word_le_hex"]+x["native_result"]["lo_word_le_hex"] for x in out["ledger"])))
    except (ValueError,TypeError,KeyError,IndexError,OSError,OverflowError,struct.error) as ex:
        out["reason"]=str(ex)
    return out

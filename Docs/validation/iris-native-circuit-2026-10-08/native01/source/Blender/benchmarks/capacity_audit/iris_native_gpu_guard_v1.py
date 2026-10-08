"""Versioned full-circuit evidence gate; unchanged bounded first-hit supervisor.

Import is inert: overrides are installed only in this private adapter's main.
This gate checks typed coverage/freshness; the independent auditor checks math.
"""
import hashlib
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from Blender.benchmarks.capacity_audit import robust_first_hit_gpu_guard_v1 as base
from Blender.benchmarks.capacity_audit import iris_native_packet_v1 as packet
from Blender.benchmarks.capacity_audit.iris_native_readback_v1 import validate_result

_base_critical_paths=base.critical_paths


def critical_paths():
    return sorted(set(_base_critical_paths())|{Path(__file__).resolve()},key=base.key)


def worker_gate(path,plan):
    original=base.sha_file(path);result=base.read_json(path);need=base.require
    need(result.get('schema')=='neuro3d.iris_lattice.native_report.v1' and
         result.get('status')=='PASS' and result.get('verification_passed') is True,'circuit worker verification required')
    need(result.get('job_id')==plan.job_id and result.get('input_manifest_sha256')==plan.input_sha,'circuit job binding')
    need(result.get('native_gpu_executed') is True and result.get('backend')=='OPENGL','native circuit execution required')
    need(result.get('background') is False and 'NVIDIA' in result.get('vendor','') and
         'RTX 3090' in result.get('renderer',''),'circuit device/context required')
    inputs=base.read_json(plan.input_manifest)
    need(inputs.get('schema')==packet.SCHEMA and inputs.get('limits')=={
         'samples':150,'cells':16,'modes':8,'dispatches':3,'output_row_words':128},'full circuit manifest')
    cases=inputs.get('cases');records=result.get('gpu_readback_records')
    need(type(cases) is list and [c.get('case_id') for c in cases]==['baseline','phase','sham'],'circuit intervention coverage')
    need(type(records) is list and [r.get('case_id') for r in records]==['baseline','phase','sham'] and
         result.get('gpu_dispatch_count')==result.get('completed_readbacks')==len(records)==3,'complete circuit dispatch/readback coverage')
    digest=hashlib.sha256();count=0;nonces=set()
    for case,record in zip(cases,records):
        nonce=int.from_bytes(hashlib.sha256((plan.job_id+'/'+case['case_id']).encode()).digest()[:4],'little')&0x7fffffff
        need(nonce!=0 and nonce not in nonces and record.get('nonce')==nonce,'fresh nonzero case nonce')
        nonces.add(nonce);raws=[]
        for field in ('input_echo_hex','result_hex'):
            value=record.get(field)
            need(type(value) is str and value and len(value)%2==0 and re.fullmatch('[0-9a-f]+',value),'circuit readback hex')
            count+=len(value)//2;need(count<=base.MAX_READBACK,'bounded circuit readback')
            raw=bytes.fromhex(value);digest.update(raw);raws.append(raw)
        value=base.read_json(packet.packet_path(case));wire=packet.admit(value)
        expected_echo=wire+bytes((-len(wire))%256)
        need(raws[0]==expected_echo,'exact circuit input echo and zero padding')
        validate_result(raws[1],nonce)
    need(result.get('gpu_readback_sha256')==digest.hexdigest(),'circuit readback digest')
    need(base.sha_file(path)==original,'immutable worker evidence')
    return {'worker_report_sha256':original,'gpu_readback_sha256':digest.hexdigest(),
            'gpu_readback_bytes':count,'gpu_dispatch_count':3,'backend':result['backend'],
            'renderer':result['renderer'],'vendor':result['vendor'],'native_gpu_execution_verified':True,
            'evidence_gate_scope':'typed full algebraic circuit; numerical audit remains separate'}


def main():
    base.critical_paths=critical_paths;base.worker_gate=worker_gate
    return base.main()


if __name__=='__main__':raise SystemExit(main())

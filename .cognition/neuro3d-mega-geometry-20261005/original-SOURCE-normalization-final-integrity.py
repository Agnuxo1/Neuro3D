import base64,hashlib,json,subprocess,zlib
from pathlib import Path
own={"Blender/benchmarks/capacity_audit/original_SOURCE_normalization_CPU64_v1.py":{"sha256":"770864fbc962efd292649a51fb3cf94439b1685c484b8a00b4cba3adfff21c96","bytes":5196},"Blender/tests/test_original_SOURCE_normalization_CPU64_v1.py":{"sha256":"8cb463f63213d29e8dc7921667d33048907846aeb7bfd4819682c4af82d33dc2","bytes":5219},"Docs/EXP-005-ORIGINAL-SOURCE-NORMALIZATION-CPU64-001.md":{"sha256":"156b2f0cd7290b1bf0a5139aaa89f5dd20225eab376c65d088eb69c4e1c2de4c","bytes":3528},"coordinacion/respuestas/PRECISION-ORIGINAL-SOURCE-NORMALIZATION-CPU64-001-CODEX.json":{"sha256":"fc7e9fa79c594d6c87d6c8c039db9327c0cc152fe910ab8fa2a1336533c0fb20","bytes":23191}}
for p,pin in own.items():
 raw=Path(p).read_bytes()
 assert hashlib.sha256(raw).hexdigest()==pin["sha256"] and len(raw)==pin["bytes"]
 assert subprocess.check_output(["git","show","HEAD:"+p])==raw,p
assert subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()=="1c315e83a0f832212808727eda0366a1c5177045"
assert not subprocess.check_output(["git","diff","--cached","--name-only"],text=True).strip()
assert not subprocess.check_output(["git","status","--porcelain","--"]+list(own),text=True).strip()
r=json.loads(Path("coordinacion/respuestas/PRECISION-ORIGINAL-SOURCE-NORMALIZATION-CPU64-001-CODEX.json").read_bytes())
for p,pin in r["pins"].items():
 raw=Path(p).read_bytes();assert hashlib.sha256(raw).hexdigest()==pin["sha256"] and len(raw)==pin["bytes"]
for c in (r["test_run"],r["oracle_run"],r["review_initial_capture"]):
 raw=zlib.decompress(base64.b64decode(c["stdout_zlib_base64"]))
 assert hashlib.sha256(raw).hexdigest()==c["stdout_sha256"] and len(raw)==c["stdout_bytes"]
 assert c["rc"]==0 and not c["timed_out"] and c["before_deadline"]
 assert c["affinity_mask"]==1 and c["RAM_reserve_after_budget_bytes"]>=4*1024**3
 assert json.loads(raw)["status"]=="PASS"
m=json.loads(Path("coordinacion/respuestas/GPU-GUARD-OWNED-TREE-CONTAINMENT-CPU-001-CODEX.json").read_bytes())["pinned_manifest_capture"]
raw=zlib.decompress(base64.b64decode(m["stdout_zlib_base64"]))
assert hashlib.sha256(raw).hexdigest()==m["stdout_sha256"]
pins=json.loads(raw)["pins"];assert len(pins)==461
for p,h in pins.items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h,p
assert Path(".cognition/neuro3d-mega-geometry-20261005/SOURCE-normalization-initial-core.py").read_text()==r["review_initial_source"]
assert Path(".cognition/neuro3d-mega-geometry-20261005/original-SOURCE-normalization-oracle.py").read_text()==r["oracle_code"]
boards={}
for name in ("CHECKPOINT","COLA-DE-TRABAJO","THINKTANK","TABLON"):
 p=Path("coordinacion")/(name+".md");raw=p.read_bytes();lines=raw.decode().splitlines()
 assert lines[2].startswith("## 2026-10-07 11:12 UTC") and r["id"] in lines[2]
 if name=="TABLON":assert next(x for x in reversed(lines) if x.startswith("|"))=="| 2026-10-07 11:12 UTC | Codex | PRECISION-ORIGINAL-SOURCE-NORMALIZATION-CPU64-001 | P1 DONE ingreso CPU64 / native STOP | Commit1c315e83a0f832212808727eda0366a1c5177045/4own/461pins/índice vacío | ReciboSHAfc7e9fa79c594d6c87d6c8c039db9327c0cc152fe910ab8fa2a1336533c0fb20/23191bytes;3tests20records/8SOURCE/8sqrtQAfinal/8STOPsinroots/oraclePASS;delta exactoNO0, NOcotaangular/fase | Claude ACK ID+SHA artifacts EXISTENTES normalización/ingreso y s actual ligados escena/query, o faltantes. No sustituirlos porCPU64 ni recrearbackendguard/cargasrelleno; nativephaseNULL/pointwiseSTOP/GPU0/JEVLOCAL/shared4SINstage/sinpush. |"
 boards[p.as_posix()]=hashlib.sha256(raw).hexdigest()
checkpoint=json.loads(Path(".cognition/neuro3d-mega-geometry-20261005/original-SOURCE-normalization-checkpoint.json").read_bytes())
assert checkpoint["owned_pins"]==own and not checkpoint["GPU_used"] and not checkpoint["native_GPU_admission"]
print(json.dumps(dict(status="PASS",own_pins=4,input_pins=6,frozen_pins=461,raw_HEAD_equal_disk=True,index_empty=True,
 initial_and_final_captures_preserved=True,boards=boards,GPU_used=False)))

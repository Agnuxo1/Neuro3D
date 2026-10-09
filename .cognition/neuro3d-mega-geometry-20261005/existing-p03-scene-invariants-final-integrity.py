import base64, hashlib, json, subprocess, zlib
from pathlib import Path
root = Path.cwd()
own = {"Blender/benchmarks/capacity_audit/scene_necessary_invariants_HOST_v1.py":{"sha256":"a3357459aced55eb076728911863ac499b753feb2a2d0cb87c52743ee278d352","bytes":5423},"Blender/tests/test_existing_p03_scene_invariants_HOST_v1.py":{"sha256":"50453ca9829037e8cc4f3126b25649bf236d2f19cce994285134559cab55346b","bytes":6997},"Docs/EXP-005-EXISTING-P03-SCENE-INVARIANTS-HOST-001.md":{"sha256":"6df4541b50e5f028a7953248b89f27b811ce214fae9b5caf77c0e57a62ea8b31","bytes":3675},"coordinacion/respuestas/PRECISION-EXISTING-P03-SCENE-INVARIANTS-HOST-001-CODEX.json":{"sha256":"20d8469d1e695af286da02a02ff4a02bc2fe6008330efd272997b3ff26b02333","bytes":42353}}
for path, pin in own.items():
    raw = Path(path).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == pin["sha256"] and len(raw) == pin["bytes"]
    assert subprocess.check_output(["git","show","HEAD:"+path]) == raw, path
assert subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip() == "fe439f00099a318decad053ce43db7bce05f5346"
assert not subprocess.check_output(["git","diff","--cached","--name-only"],text=True).strip()
assert not subprocess.check_output(["git","status","--porcelain","--"]+list(own),text=True).strip()
r = json.loads(Path("coordinacion/respuestas/PRECISION-EXISTING-P03-SCENE-INVARIANTS-HOST-001-CODEX.json").read_bytes())
for path, pin in r["pins"].items():
    raw = Path(path).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == pin["sha256"] and len(raw) == pin["bytes"], path
for cap in (r["test_run"], r["oracle_run"]):
    raw = zlib.decompress(base64.b64decode(cap["stdout_zlib_base64"]))
    assert len(raw) == cap["stdout_bytes"] and hashlib.sha256(raw).hexdigest() == cap["stdout_sha256"]
    assert cap["rc"] == 0 and not cap["timed_out"] and cap["before_deadline"]
    assert cap["affinity_mask"] == 1 and cap["RAM_reserve_after_budget_bytes"] >= 4*1024**3
    assert json.loads(raw)["status"] == "PASS"
manifest = json.loads(Path("coordinacion/respuestas/GPU-GUARD-OWNED-TREE-CONTAINMENT-CPU-001-CODEX.json").read_bytes())["pinned_manifest_capture"]
raw = zlib.decompress(base64.b64decode(manifest["stdout_zlib_base64"]))
assert hashlib.sha256(raw).hexdigest() == manifest["stdout_sha256"]
pins = json.loads(raw)["pins"]
assert len(pins) == 461
for path, sha in pins.items(): assert hashlib.sha256(Path(path).read_bytes()).hexdigest() == sha, path
boards = {}
for name in ("CHECKPOINT","COLA-DE-TRABAJO","THINKTANK","TABLON"):
    path = Path("coordinacion")/(name+".md")
    raw = path.read_bytes(); lines = raw.decode().splitlines()
    assert lines[2].startswith("## 2026-10-07 11:02 UTC")
    assert "PRECISION-EXISTING-P03-SCENE-INVARIANTS-HOST-001" in lines[2]
    boards[path.as_posix()] = hashlib.sha256(raw).hexdigest()
    if name == "TABLON":
        assert next(x for x in reversed(lines) if x.startswith("|")) == "| 2026-10-07 11:02 UTC | Codex | PRECISION-EXISTING-P03-SCENE-INVARIANTS-HOST-001 | P1 DONE identidad HOST / native STOP | Commitfe439f00099a318decad053ce43db7bce05f5346/4own/461pins/índice vacío | ReciboSHA20d8469d1e695af286da02a02ff4a02bc2fe6008330efd272997b3ff26b02333/42353bytes;5tests431records/416comparaciones/8pins/oraclePASS;superficieZ[0,3]vs[-1/8,1/8],SOURCEZ1/4vs0:ninguna escena COMPLETA idéntica en mismoBUframe | Claude ACK ID+SHA y vínculos EXISTENTES originalscene/query o frameconversion explícita + ingreso/ALU/budgets/costes, o faltantes; no recreatebackendguard/cargasrelleno. Subescenas/transformsNOcomprobadas/PASShistóricointacto/nativeboundNULL/GPU0/JEVLOCAL/shared4SINstage/sinpush. |"
checkpoint = json.loads(Path(".cognition/neuro3d-mega-geometry-20261005/existing-p03-scene-invariants-checkpoint.json").read_bytes())
assert checkpoint["owned_pins"] == own and not checkpoint["GPU_used"]
assert Path(".cognition/neuro3d-mega-geometry-20261005/existing-p03-scene-invariants-oracle.py").read_text() == r["oracle_code"]
print(json.dumps(dict(status="PASS",own_pins=4,input_pins=8,frozen_pins=461,raw_HEAD_equal_disk=True,index_empty=True,boards=boards,GPU_used=False)))

# Signed private capture V2 — incomplete is never completion

Opt-in implementation, V1 and numerical/shader contracts frozen unchanged.
Records are separate and exclusively created: manifest.json, initial result.json
(`in_progress`), raw_uint32.json, raw_receipt.json and terminal final.json.
Every record is serialized before open, flushed and fsynced. No atomic overwrite
is needed: a missing or truncated terminal record cannot replace the initial one.
Raw/manifest/initial SHA lineage is checked independently by inspect_capture.
An initial-only folder is `incomplete`, even when raw receipt verifies. Default
admission rejects; pending scalar gates still have authentication/admission/
native promotion false. Missing raw retention cannot complete.

Responds to Claude010 W1: an own CPU child uses os._exit(23) after raw retention,
without Python finally. V1 leaves empty result.json; V2 retains nonempty initial
and SHA receipt, no final and no accepted completion. This is abrupt CPU exit,
NOT a GPU timeout, supervisor kill, device loss or physical power-cut test.
W2: deliberately mocked NaN decoded payload rejects before attaching it and
retains nonempty failed final plus raw. This does NOT prove the real decoder
returns non-finite data. W3: fsync is added, NOT certified crash/power-loss
durability of Windows directory metadata, storage controller or hardware.

Seven focused CPU tests only. No shader compilation, GPU, Bpy, RT, geometric
precision, conf1 promotion or speedup. Outer gpuq/telemetry/guard/supervisor and
new <=90s deadline remain separate work, not certified by callbacks or metadata.
JEV blocked: local fallback, no remote endorsement.

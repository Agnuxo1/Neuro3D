# Scalar own-job supervisor V1 — new deadline, no night-policy reuse

New opt-in synchronous function, no CLI/queue acquisition. Production reservation
reads gpuq holder.json and requires matching named holder, direct child PID and
birth identities plus real parent/environment. Never edits tickets, holder or other processes. GPU calls MUST
still be made only inside gpuq run, with recorded coordination and private child.
The historical guarded_job launcher/deadline stays unchanged; only its telemetry
and PID/birth checked own-child cleanup helpers are reused.

Explicit UTC deadline at most90s ahead, timeout <=70s and at least20s margin
for telemetry (5s bounded call) and frozen cleanup helper (10s bounded wait).
Scalar host reserve2GiB before launch, >=4GiB remaining; running RAM floor4GiB.
Projected device reserve0.25GiB, total <=18GiB; running actual <=18GiB; <=80C.
These fixed scalar budgets DO NOT authorize geometry scaling: >=1024B/cell plus
fixed/temporary margins needs a new estimate before geometry jobs.
Initial/final exclusive fsynced envelope, stdout/stderr private files. Telemetry
or reservation loss rejects/stops own child; monotonic timeout and absolute
deadline are both checked. Blocking telemetry/cleanup have bounded calls, not
hard realtime guarantees. Outer supervisor abrupt termination remains a limit.

Nine focused tests: synthetic telemetry/reservation, real own Python CPU child
normal exit/timeout/telemetry failure. Injected adapters are explicitly labeled
and never GPU-authenticated. No actual gpuq run, NVIDIA telemetry, GPU/Blender,
shader compilation, scalar decoder/scene geometry/RT or performance comparison.
Next: pin command/child/capture, supervisor envelope and real queue integration
before one safe scalar native pilot. JEV blocked, explicit local fallback.

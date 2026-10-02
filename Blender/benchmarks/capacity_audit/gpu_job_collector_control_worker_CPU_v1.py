"""Fixed, bounded-output synthetic CPU collector control; never live telemetry."""
import ctypes,json,sys,time
k=ctypes.windll.kernel32
k.GetCurrentProcess.restype=ctypes.c_void_p
k.SetProcessAffinityMask.argtypes=[ctypes.c_void_p,ctypes.c_size_t]
assert k.SetProcessAffinityMask(k.GetCurrentProcess(),1)
mode=sys.argv[1]
if mode=="block":time.sleep(2)
if mode=="invalid_json":print("INVALID_SYNTHETIC_CONTROL");raise SystemExit(0)
if mode=="oversized":sys.stdout.write("X"*8193);raise SystemExit(0)
if mode=="exit_error":sys.stderr.write("EXPECTED_CPU_CONTROL_EXIT");raise SystemExit(2)
if mode=="bad_packet":print(json.dumps({"origin":"GPU","snapshot":None}));raise SystemExit(0)
assert mode in ("valid","block")
job="CPU-LIFECYCLE-SYNTHETIC"
snapshot={"job_id":job,"sampled_utc_s":1790978400,"ram_available_bytes":8*2**30,
 "device_used_bytes":2**30,"device_total_bytes":24*2**30,"temperature_millic":80000,
 "elapsed_s":0,"gpuq_job_id":job,"claude_job_id":job,"process_scan_job_id":job,
 "exclusive_gpu":True,"gpuq_checked":True,"claude_checked":True,"processes_checked":True,
 "guard_fail_closed_checked":True,"post_0x9f_headroom_checked":True}
print(json.dumps({"origin":"SYNTHETIC_CONTROL_NOT_LIVE_TELEMETRY","snapshot":snapshot},sort_keys=True))

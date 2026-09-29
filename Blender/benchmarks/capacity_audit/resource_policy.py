"""CPU-only preflight arithmetic; not a substitute for a live job watchdog."""
from datetime import datetime,timezone
import math

GIB = 2**30
DEADLINE = datetime(2026,9,30,6,0,tzinfo=timezone.utc)


def preflight(*,kind,width,batch,device_used_bytes,ram_available_bytes,
              temperature_c,now_utc,job_seconds=600,depth=4,direct_gpu_weights=True):
    for name,value in (('width',width),('batch',batch),('depth',depth),('job_seconds',job_seconds)):
        if isinstance(value,bool) or not isinstance(value,int) or value<=0:
            raise ValueError(f'{name}: positive integer required')
    for value in (device_used_bytes,ram_available_bytes,temperature_c):
        if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or value<0:
            raise ValueError('finite nonnegative telemetry required')
    if now_utc.tzinfo is None: raise ValueError('timezone-aware time required')
    if kind not in ('matvec','mlp'): raise ValueError('known workload required')
    layers = depth if kind=='mlp' else 1
    params = layers*width*width+(layers*width if kind=='mlp' else 0)
    # fp32 inference only; conservative simultaneous input/output/intermediate buffers.
    weight_bytes = 4*params
    activation_bytes = 4*batch*width*(2*layers+3)
    device_estimate = weight_bytes+activation_bytes+512*2**20
    # Host-first construction may hold initialization/copy buffers; reject it before allocation.
    host_estimate = 256*2**20+(2*weight_bytes if not direct_gpu_weights else 0)
    reasons = []
    if device_used_bytes+device_estimate>18*GIB: reasons.append('projected_total_device_memory_cap')
    if ram_available_bytes-host_estimate<4*GIB: reasons.append('projected_free_host_memory_floor')
    if temperature_c>80: reasons.append('temperature_cap')
    if job_seconds>600: reasons.append('job_duration_cap')
    remaining = (DEADLINE-now_utc.astimezone(timezone.utc)).total_seconds()
    if remaining<job_seconds+60: reasons.append('absolute_deadline_with_shutdown_margin')
    return {'allowed':not reasons,'reasons':reasons,'parameters':params,
            'estimated_device_bytes':device_estimate,'estimated_host_bytes':host_estimate,
            'scope':'conservative fp32 inference preflight; actual telemetry/watchdog still mandatory'}

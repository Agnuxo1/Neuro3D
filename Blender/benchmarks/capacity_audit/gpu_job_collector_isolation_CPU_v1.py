"""Bounded fixed CPU control worker. NOT a live collector or GPU guard/launcher."""
import base64,hashlib,json,math,os,subprocess,time,zlib
from pathlib import Path
import gpu_job_resource_policy_HOST_v1 as policy
MODEL="gpu-job-collector-isolation-CPU-v1"
ORIGIN="SYNTHETIC_CONTROL_NOT_LIVE_TELEMETRY"
WORKER=Path(__file__).with_name("gpu_job_collector_control_worker_CPU_v1.py")
WORKER_SHA="08658fc20e46d63f6e7a22c612191a50f9979308eaa7b8e64b49e04ae3d3cc40"
PYTHON=Path("C:/Python313/python.exe")
PYTHON_SHA="d932e5e2f324d57f392e8fd063dcf6d0185be8a664c57c6d24e7762ed02c28ca"
PROFILES={"valid","block","invalid_json","oversized","exit_error","bad_packet"}
OUTPUT_CAP=8192
FIXED_WORKER_MAX_OUTPUT=8193
class CollectorFailure(RuntimeError):
 def __init__(self,report):
  super().__init__("CPU control collector failed: "+report["status"]);self.report=report

def sha(b):return hashlib.sha256(b).hexdigest()
def _read_worker():return WORKER.read_bytes()
def _launch(source,profile):
 env=dict(os.environ)
 for key in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS","VECLIB_MAXIMUM_THREADS"):env[key]="1"
 return subprocess.Popen([str(PYTHON),"-I","-B","-c",source.decode("utf-8"),profile],
  stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=env,
  creationflags=subprocess.CREATE_NO_WINDOW)

def collect(profile,*,timeout_s,model):
 report={"model":MODEL,"status":"INPUT_INVALID","profile":profile if type(profile) is str and profile in PROFILES else None,
  "process_started":False,"own_process_terminated":False,"cleanup_confirmed":False,
  "GPU_job_admission":False,"GPU_executed":False,"live_telemetry_collected":False,
  "foreign_processes_touched":False,"origin":ORIGIN,"threads_compute":1,"affinity_mask":1}
 if type(model) is not str or model!=MODEL or type(profile) is not str or profile not in PROFILES or \
    type(timeout_s) not in (int,float) or not math.isfinite(timeout_s) or not 0.05<=timeout_s<=1:
  raise CollectorFailure(report)
 report["timeout_s"]=timeout_s
 try:
  source=_read_worker()
  if sha(source)!=WORKER_SHA or sha(PYTHON.read_bytes())!=PYTHON_SHA:
   report["status"]="PIN_MISMATCH";raise CollectorFailure(report)
  report.update(worker_sha256=WORKER_SHA,python_sha256=PYTHON_SHA)
  start=time.monotonic();child=_launch(source,profile)
 except CollectorFailure:raise
 except (OSError,ValueError,TypeError) as exc:
  report.update(status="START_ERROR",error_type=type(exc).__name__);raise CollectorFailure(report) from None
 report.update(process_started=True,own_pid=child.pid)
 stdout=stderr=b"";interrupted=None;status=None
 try:
  stdout,stderr=child.communicate(timeout=timeout_s)
 except subprocess.TimeoutExpired:
  status="TIMEOUT"
 except BaseException as exc:
  status="COMMUNICATE_ERROR";report["error_type"]=type(exc).__name__;interrupted=exc
 finally:
  try:
   if child.poll() is None:
    child.kill();report["own_process_terminated"]=True
    stdout,stderr=child.communicate(timeout=1)
   report["cleanup_confirmed"]=child.poll() is not None
   report["returncode"]=child.returncode
  except (OSError,subprocess.SubprocessError) as exc:
   report.update(status="CLEANUP_UNCONFIRMED",error_type=type(exc).__name__)
   raise CollectorFailure(report) from None
  report["elapsed_s"]=time.monotonic()-start
 if interrupted is not None and not isinstance(interrupted,Exception):raise interrupted
 report.update(stdout_bytes=len(stdout),stdout_sha256=sha(stdout),
  stdout_zlib_base64=base64.b64encode(zlib.compress(stdout)).decode(),
  stderr_bytes=len(stderr),stderr_sha256=sha(stderr),
  stderr_zlib_base64=base64.b64encode(zlib.compress(stderr)).decode())
 if status is None and child.returncode!=0:status="CHILD_EXIT_ERROR"
 if status is None and (len(stdout)>OUTPUT_CAP or len(stderr)>OUTPUT_CAP):status="OUTPUT_CAP"
 packet=None
 if status is None:
  try:
   packet=json.loads(stdout)
   policy.closed(packet,{"origin","snapshot"})
   if packet["origin"]!=ORIGIN:raise ValueError("synthetic origin required")
   policy.closed(packet["snapshot"],policy.SNAP_KEYS)
  except (ValueError,TypeError,UnicodeError):status="PACKET_INVALID"
 report["status"]=status or "SYNTHETIC_PACKET"
 if status is not None:raise CollectorFailure(report)
 report["packet"]=packet
 return report

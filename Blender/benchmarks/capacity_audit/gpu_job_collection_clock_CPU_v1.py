"""Opt-in OS endpoint clock adapter. CPU control only; no GPU permit or general timeout."""
from copy import deepcopy
import time
import gpu_job_monitor_lifecycle_CPU_v1 as frozen
import gpu_job_resource_policy_HOST_v1 as policy
MODEL = "gpu-job-collection-clock-CPU-v1"

def stamp():
    # Sequential OS reads, not an atomic/authenticated clock pair.
    utc = policy.integer(time.time_ns() // 10**9)
    mono = policy.integer(time.monotonic_ns())
    return {"utc_s": utc, "monotonic_ns": mono}

class EndpointMonitor:
    def __init__(self, plan, *, model):
        self._state = "STOP"
        self._reasons = ["invalid_constructor_INPUT"]
        self._inner = None
        self._before = self._after = None
        self._collection_ns = None
        self._last = None
        self._collector_calls = 0
        try:
            if type(model) is not str or model != MODEL:
                raise ValueError("explicit CPU model required")
            self._last = stamp()
            self._inner = frozen.Monitor(plan, now_utc_s=self._last["utc_s"],
                monotonic_ns=self._last["monotonic_ns"], model=frozen.MODEL)
            if self._inner.view()["state"] != "STOP":
                self._state = "CONTROL_READY"
                self._reasons = []
        except Exception as exc:
            self._reasons = ["constructor_error:" + type(exc).__name__]

    def _stop(self, reason):
        self._state = "STOP"
        self._reasons = [reason]
        return self.view()

    def view(self):
        return deepcopy({"model": MODEL, "state": self._state, "reasons": self._reasons,
            "before": self._before, "after": self._after, "collection_ns": self._collection_ns,
            "collector_calls": self._collector_calls,
            "frozen_view": self._inner.view() if self._inner is not None else None,
            "GPU_job_admission": False, "GPU_executed": False,
            "live_resource_telemetry": False, "runtime_GPU_guard": False,
            "reservation_authenticated": False, "clock_pair_atomic_authenticated": False,
            "arbitrary_callback_timeout_implemented": False,
            "scope": "OS endpoint clocks around bounded collector; untrusted snapshot NOT overwritten"})

    def sample(self, read_snapshot):
        if self._state == "STOP":
            return self.view()  # Before clocks and ANY collector invocation.
        try:
            self._before = stamp()
            for old, new in ((self._last, self._before),):
                if new["monotonic_ns"] < old["monotonic_ns"]:
                    return self._stop("precollection_monotonic_rollback")
                if new["utc_s"] < old["utc_s"]:
                    return self._stop("precollection_wall_rollback")
                if new["monotonic_ns"] - old["monotonic_ns"] > frozen.MAX_MONITOR_GAP_NS:
                    return self._stop("precollection_gap")
            if not callable(read_snapshot):
                return self._stop("collector_not_callable")
        except Exception as exc:
            return self._stop("precollection_error:" + type(exc).__name__)
        try:
            self._collector_calls += 1
            snapshot = read_snapshot()
        except BaseException as exc:
            result = self._stop("collector_error:" + type(exc).__name__)
            if not isinstance(exc, Exception):
                raise
            return result
        try:
            self._after = stamp()
            self._collection_ns = self._after["monotonic_ns"] - self._before["monotonic_ns"]
            if self._collection_ns < 0:
                return self._stop("postcollection_monotonic_rollback")
            if self._after["utc_s"] < self._before["utc_s"]:
                return self._stop("postcollection_wall_rollback")
            if self._after["monotonic_ns"] - self._last["monotonic_ns"] > frozen.MAX_MONITOR_GAP_NS:
                return self._stop("postcollection_gap")
            # Frozen elapsed/deadline/freshness checks now use AFTER, never rewrite snapshot.
            out = self._inner.sample(lambda: snapshot, now_utc_s=self._after["utc_s"],
                                     monotonic_ns=self._after["monotonic_ns"])
            self._state = out["state"]
            self._reasons = list(out["reasons"])
            self._last = self._after.copy()
            return self.view()
        except BaseException as exc:
            result = self._stop("postcollection_error:" + type(exc).__name__)
            if not isinstance(exc, Exception):
                raise
            return result

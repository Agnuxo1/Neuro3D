"""Opt-in per-SOURCE per-branch CPU primitive state; NOT geometry/tracing/field evidence."""
from copy import deepcopy
import hashlib
import json
import primitive_tie_guard_v1 as tie
from primitive_return_guard_v1 import classify_return
MODEL = "precision-branch-primitive-state-CPU-v1"
MAX_DEPTH = 64  # NEW opt-in state bound; STOP, not an optical truncation permission.

def label(value):
    if type(value) is not str or not 1 <= len(value) <= 128:
        raise ValueError("explicit bounded branch/SOURCE label required")
    return value

def closed(value, keys):
    if type(value) is not dict or set(value) != set(keys):
        raise ValueError("closed INPUT schema required")

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                    allow_nan=False).encode()).hexdigest()

class Branch:
    def __init__(self, *, snapshot_sha256, manifest, source_id, branch_id, model):
        if type(model) is not str or model != MODEL:
            raise ValueError("explicit CPU-state model required")
        self._sha = tie.snapshot_id(snapshot_sha256)
        self._source = label(source_id)
        self._branch = label(branch_id)
        if type(manifest) is not list:
            raise ValueError("explicit manifest list required")
        for row in manifest:
            closed(row, ("primitive_id", "object_id"))
        tie.resolve_candidates(snapshot_sha256=self._sha, manifest=manifest,
                               candidates=[], previous=None)
        self._manifest = deepcopy(manifest)
        self._previous = None
        self._depth = 0
        self._ancestors = (self._branch,)
        self._state = "READY"
        self._reason = None
        self._pending = None
        self._last = None
        self._seal()

    def _binding(self):
        return {"snapshot": self._sha, "manifest": self._manifest, "source": self._source,
                "branch": self._branch, "previous": self._previous, "depth": self._depth,
                "ancestors": self._ancestors, "pending": self._pending}
    def _seal(self):
        self._fingerprint = digest(self._binding())
    def _intact(self):
        return digest(self._binding()) == self._fingerprint
    def _stop(self, reason):
        self._state = "STOP"
        self._reason = reason
        self._pending = None
        return self.view()
    def view(self):
        return deepcopy({"model": MODEL, "state": self._state, "reason": self._reason,
            "snapshot_sha256": self._sha, "manifest_sha256": digest(self._manifest),
            "source_id": self._source, "branch_id": self._branch, "depth": self._depth,
            "previous": self._previous, "pending": self._pending, "last_policy": self._last,
            "binding_sha256": self._fingerprint, "origin": "SYNTHETIC_DECLARED_CANDIDATES_CPU_ONLY",
            "GPU_executed": False, "native_promotion_allowed": False,
            "scene_geometry_authenticated": False, "complete_hit_coverage": False,
            "length_reference_phase_bound_certified": False, "full_field_certified": False,
            "fork_energy_or_material_certified": False})

    def query(self, *, snapshot_sha256, source_id, branch_id, candidates):
        if self._state in ("STOP", "FORKED"):
            return self.view()
        try:
            if not self._intact():
                return self._stop("state_binding_changed")
            if self._state != "READY":
                return self._stop("pending_hit_requires_departure")
            if snapshot_sha256 != self._sha or source_id != self._source or branch_id != self._branch:
                return self._stop("snapshot_SOURCE_branch_binding_mismatch")
            if type(candidates) is not list:
                raise ValueError("explicit candidates list required")
            for row in candidates:
                closed(row, ("primitive_id", "distance_BU", "normal"))
            result = tie.resolve_candidates(snapshot_sha256=self._sha, manifest=self._manifest,
                                            candidates=deepcopy(candidates), previous=self._previous)
            self._last = deepcopy(result)
            if result["action"] != "continue":
                return self._stop("tie_policy:" + result["reason"])
            prior = self._previous
            returned = classify_return(previous_primitive=prior["primitive_id"] if prior else None,
                candidate_primitive=result["selected_primitive"],
                departure_event=prior["departure_event"] if prior else None,
                distance_BU=result["minimum_distance_BU"])
            if returned["action"] != "continue":
                return self._stop("return_policy:" + returned["reason"])
            self._pending = {"primitive_id": result["selected_primitive"],
                             "distance_BU": result["minimum_distance_BU"]}
            self._state = "HIT_PENDING_DEPARTURE"
            self._seal()
            return self.view()
        except (ValueError, TypeError, KeyError, OverflowError):
            return self._stop("invalid_query_INPUT")

    def fork(self, departures):
        """Atomic state-only fork: mirror singleton OR distinct t/r pair, no field weights."""
        if self._state in ("STOP", "FORKED"):
            return []
        try:
            if not self._intact():
                self._stop("state_binding_changed"); return []
            if self._state != "HIT_PENDING_DEPARTURE":
                raise ValueError("accepted pending hit required")
            if self._depth >= MAX_DEPTH:
                self._stop("state_depth_bound_NOT_optical_truncation"); return []
            if type(departures) is not list or not 1 <= len(departures) <= 2:
                raise ValueError("explicit bounded departures required")
            ids = []
            events = []
            for row in departures:
                closed(row, ("branch_id", "departure_event"))
                bid = label(row["branch_id"])
                if bid in ids or bid in self._ancestors:
                    raise ValueError("unique NEW branch labels required")
                ids.append(bid); events.append(row["departure_event"])
            if not (events == ["mirror"] or len(events) == 2 and set(events) == {"t", "r"}):
                raise ValueError("mirror singleton or t/r pair required")
            children = []
            for bid, event in zip(ids, events):
                child = Branch(snapshot_sha256=self._sha, manifest=self._manifest,
                               source_id=self._source, branch_id=bid, model=MODEL)
                child._previous = {"snapshot_sha256": self._sha,
                    "primitive_id": self._pending["primitive_id"], "departure_event": event}
                child._depth = self._depth + 1
                child._ancestors = self._ancestors + (bid,)
                child._seal()
                children.append(child)
            self._state = "FORKED"
            self._pending = None
            self._seal()
            return children
        except (ValueError, TypeError, KeyError, OverflowError):
            self._stop("invalid_departure_INPUT")
            return []

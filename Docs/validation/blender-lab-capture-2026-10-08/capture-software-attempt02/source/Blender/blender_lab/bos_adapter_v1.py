"""Optional interface to an independently installed Blender Optics Simulator.

No GPL code or addon installer is included. Capturing reads bpy RNA directly;
requesting diagnostics explicitly invokes the external optical trace.
"""
from __future__ import annotations

import importlib

from .scene_capture_v1 import capture_scene, digest, need


UPSTREAM = {
    "repository": "https://github.com/emircbngl/blender-optics-simulator",
    "reviewed_commit": "2b488e2e99dff4f56d67f57f9674bd00f812dda1",
    "license": "GPL-3.0",
    "api_geometry_decimal_rounding": True,
    "source_copied": False,
}


def capture_bos_scene(*, network: dict | None = None) -> dict:
    import bpy

    need(hasattr(bpy.context.scene, "optics"), "Optics Simulator scene RNA not registered")
    optics = [obj for obj in bpy.context.scene.objects
              if getattr(getattr(obj, "optics", None), "is_optical", False)]
    need(bool(optics), "no registered optical elements in active scene")
    snapshot = capture_scene(network=network)
    snapshot["provenance"]["external_schema_adapter"] = dict(UPSTREAM)
    # A reviewed commit is a reference, not a claim about the installed binary.
    snapshot["provenance"]["installed_upstream_commit_verified"] = False
    return snapshot


def collect_bos_diagnostic(*, api=None) -> dict:
    """Opt-in external trace/readout; never use rounded data as a certificate."""
    if api is None:
        api = importlib.import_module("optics_api")
    result = api.get_state()
    need(isinstance(result, dict) and "error" not in result, "external optics API failed")
    need(all(key in result for key in ("coordinate_units", "elements", "sources", "detectors", "report")),
         "external optics API state schema changed")
    return {"schema": "neuro3d.blender_lab.bos_diagnostic.v1", "external_state": result,
            "external_state_sha256": digest(result), "geometry_certificate": False,
            "optical_result_independently_validated": False,
            "upstream_reference": dict(UPSTREAM)}

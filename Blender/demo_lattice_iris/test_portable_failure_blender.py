"""Check portable-verifier rejection and stale-report replacement without classifying rows."""
import argparse
import copy
import importlib.util
import json
from pathlib import Path
import sys


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("--blend", required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    verifier_path = Path(__file__).with_name("verify_portable_blender.py")
    spec = importlib.util.spec_from_file_location("portable_negative_verifier", verifier_path)
    verifier = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(verifier)
    original = json.loads(args.manifest.read_text(encoding="utf-8"))
    cases = [
        ("missing_blend_hash", "blend_sha256"),
        ("wrong_blend_hash", "Copied .blend hash mismatch"),
        ("wrong_source_hash", "Embedded asset hash mismatch"),
    ]
    results = []
    for name, reason in cases:
        changed = copy.deepcopy(original)
        if name == "missing_blend_hash":
            del changed["blend_sha256"]
        elif name == "wrong_blend_hash":
            changed["blend_sha256"] = "0" * 64
        else:
            changed["assets"]["neuro3d_iris_demo.py"]["sha256"] = "0" * 64
        manifest = args.output_dir / (name + ".manifest.json")
        report = args.output_dir / (name + ".report.json")
        manifest.write_text(json.dumps(changed), encoding="utf-8")
        report.write_text(json.dumps({"status": "PASS", "verification_passed": True,
                                      "old_report_sentinel": "must_be_replaced"}), encoding="utf-8")
        code = verifier.main(["--blend", args.blend, "--manifest", str(manifest),
                              "--report", str(report)])
        evidence = json.loads(report.read_text(encoding="utf-8"))
        assert code == 1 and evidence["status"] == "FAIL" and evidence["verification_passed"] is False
        assert evidence["classify_calls_attempted"] == evidence["classify_calls_completed"] == 0
        assert "old_report_sentinel" not in evidence
        assert any(reason in failure for failure in evidence["verification_failures"]), evidence
        results.append({"case": name, "status": "PASS_EXPECTED_REJECTION",
                        "classify_calls": 0, "stale_success_replaced": True,
                        "reason": evidence["verification_failures"]})
    summary = {"status": "PASS", "cases": results, "scene_classifications": 0}
    (args.output_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print("PORTABLE_NEGATIVE_CONTROLS", json.dumps(summary), flush=True)


if __name__ == "__main__":
    main(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])

"""Read-only repository inventory, pin checking, and closure-record validation.

Integrity checks never establish scientific correctness. Objective acceptance
must also cite an independently executed verifier and its frozen raw results.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys


def sha256(path: Path) -> str:
    """Hash a file incrementally without loading large evidence into memory."""
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024*1024), b""):
            h.update(block)
    return h.hexdigest()


def contained_file(root: Path, relative: str) -> Path:
    """Resolve a repository-relative file and reject escapes and absolute paths."""
    p = Path(relative)
    if p.is_absolute() or ".." in p.parts or not p.parts or ":" in relative:
        raise ValueError("Only repository-relative evidence paths are accepted")
    target = (root/p).resolve()
    if not target.is_relative_to(root.resolve()) or not target.is_file():
        raise ValueError("Evidence is missing or resolves outside the repository: "+relative)
    return target


def check_pins(root: Path, pins: dict[str, str]) -> list[dict]:
    """Check every source/evidence pin, reporting all mismatches without edits."""
    if not isinstance(pins, dict) or not pins:
        raise ValueError("A nonempty path-to-SHA256 dictionary is required")
    results = []
    for name, expected in sorted(pins.items()):
        try:
            if not isinstance(expected, str) or len(expected) != 64 or any(c not in "0123456789abcdef" for c in expected):
                raise ValueError("An exact lowercase SHA256 is required")
            actual = sha256(contained_file(root, name))
            results.append({"path": name, "status": "PASS" if actual == expected else "FAIL", "expected": expected, "actual": actual})
        except (ValueError, OSError) as exc:
            results.append({"path": name, "status": "BLOCKED", "reason": str(exc)})
    return results


def _git(root: Path, *arguments: str) -> str:
    """Run a bounded read-only git query with explicit arguments and no shell."""
    return subprocess.check_output(["git", "-C", str(root), *arguments], text=True, timeout=60)


def inventory(root: Path) -> dict:
    """Identify current state, missing tracked files, and import-time cwd changes."""
    root = root.resolve()
    head = _git(root, "rev-parse", "HEAD").strip()
    tracked = _git(root, "ls-files", "-z").split("\0")
    tracked = [s for s in tracked if s]
    missing, module_chdir, syntax_errors = [], [], []
    for relative in tracked:
        p = root/relative
        if not p.is_file():
            missing.append(relative)
            continue
        if p.suffix != ".py" or not relative.startswith(("Blender/", "Tools/", "Benchmarks/")):
            continue
        try:
            tree = ast.parse(p.read_text(encoding="utf-8-sig"), filename=relative)
            for statement in tree.body:
                if isinstance(statement, ast.Expr) and isinstance(statement.value, ast.Call):
                    fn = statement.value.func
                    if isinstance(fn, ast.Attribute) and fn.attr == "chdir":
                        module_chdir.append({"path": relative, "line": statement.lineno})
        except (SyntaxError, UnicodeError) as exc:
            syntax_errors.append({"path": relative, "reason": str(exc)})
    acceptance_path = root/"Docs/research/optic_neuro_blender_acceptance_v1.json"
    acceptance = json.loads(acceptance_path.read_text(encoding="utf-8")) if acceptance_path.is_file() else None
    return {"schema": "neuro3d.closure.inventory.v1", "head": head,
            "tracked_files": len(tracked), "missing_tracked_files": missing,
            "module_scope_chdir": module_chdir, "python_syntax_errors": syntax_errors,
            "working_tree": _git(root, "status", "--porcelain").splitlines(),
            "canonical_priorities": acceptance["priorities"] if acceptance else None,
            "claim_policy": acceptance.get("claim_policy") if acceptance else None,
            "scope": "Static inventory only; no experiment, GPU, or proof has been executed"}


def verify_closure(root: Path, document: dict) -> dict:
    """Check that eleven fronts have honest states and verifiable evidence pins."""
    if document.get("schema") != "neuro3d.closure.manifest.v1":
        raise ValueError("Unsupported closure schema")
    objectives = document.get("objectives", [])
    if not isinstance(objectives, list) or any(not isinstance(x, dict) or type(x.get("id")) is not int for x in objectives):
        raise ValueError("Objectives must be dictionaries with integer identifiers")
    if sorted(x.get("id") for x in objectives) != list(range(1, 12)):
        raise ValueError("Exactly the eleven joint-status fronts are required")
    failures, unresolved = [], []
    states = {"PASS", "PARTIAL", "OPEN", "BLOCKED", "NOT_APPLICABLE"}
    for objective in objectives:
        oid, state = objective["id"], objective.get("state")
        if state not in states:
            failures.append({"id": oid, "reason": "INVALID_STATE"})
            continue
        if state == "NOT_APPLICABLE":
            if not objective.get("scope_reason"):
                failures.append({"id": oid, "reason": "UNEXPLAINED_SCOPE_EXCLUSION"})
            continue
        if state != "PASS":
            unresolved.append({"id": oid, "state": state, "remaining": objective.get("remaining", [])})
            continue
        if objective.get("remaining") or not objective.get("scientific_verifier_record"):
            failures.append({"id": oid, "reason": "PASS_WITHOUT_VERIFIER_OR_WITH_REMAINING_WORK"})
            continue
        checks = check_pins(root, objective.get("pins", {}))
        failures.extend({"id": oid, **x} for x in checks if x["status"] != "PASS")
        if objective["scientific_verifier_record"] not in objective.get("pins", {}):
            failures.append({"id": oid, "reason": "UNPINNED_SCIENTIFIC_VERIFIER"})
    return {"schema": "neuro3d.closure.integrity.v1", "failures": failures, "unresolved": unresolved,
            "integrity_pass": not failures, "all_selected_fronts_pass": not failures and not unresolved,
            "scope": "Manifest integrity only; verify scientific semantics, independence, and scope separately"}


def write_report(path: Path, report: dict) -> None:
    """Create a new report atomically with respect to an existing destination."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(report, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write("\n")


def main() -> int:
    """Expose static inventory and evidence checking without modifying sources."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    sub = parser.add_subparsers(dest="action", required=True)
    inv = sub.add_parser("inventory")
    inv.add_argument("--out", type=Path, required=True)
    pins = sub.add_parser("check-pins")
    pins.add_argument("--profile", type=Path, required=True)
    closure = sub.add_parser("verify-closure")
    closure.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.action == "inventory":
            report = inventory(args.repo)
            write_report(args.out, report)
            print(json.dumps({"head": report["head"], "tracked_files": report["tracked_files"], "report": str(args.out)}))
            return 0
        if args.action == "check-pins":
            profile = json.loads(args.profile.read_text(encoding="utf-8"))
            checks = check_pins(args.repo, profile["pins"])
            print(json.dumps(checks, indent=2))
            return 0 if all(x["status"] == "PASS" for x in checks) else 2
        report = verify_closure(args.repo, json.loads(args.manifest.read_text(encoding="utf-8")))
        print(json.dumps(report, indent=2))
        return 0 if report["all_selected_fronts_pass"] else 2
    except (ValueError, OSError, KeyError, subprocess.SubprocessError) as exc:
        print(json.dumps({"status": "BLOCKED", "reason": str(exc)}), file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())

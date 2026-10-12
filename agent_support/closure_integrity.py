"""Blinding commitments, experiment-record checks, and citation identifier checks.

These tools make three failure modes detectable: looking at test labels
before the analysis is frozen, records that omit what section 18 requires,
and references that do not resolve. Detecting a problem is not proof of
scientific quality.
"""
from __future__ import annotations

import hashlib
import json
import re
import secrets
from typing import Callable, Iterable
from urllib import error as urlerror
from urllib import request as urlrequest


def new_salt() -> bytes:
    """32 secret random bytes; keep them with the owner until the reveal."""
    return secrets.token_bytes(32)


def _item_hash(salt: bytes, index: int, label) -> str:
    payload = json.dumps(label, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    return hashlib.sha256(salt+index.to_bytes(8, "big")+payload.encode("utf-8")).hexdigest()


def commit_labels(labels: Iterable, salt: bytes) -> dict:
    """Commit to ordered labels: publish root and count now, reveal salt and labels later."""
    if not isinstance(salt, (bytes, bytearray)) or len(salt) < 32:
        raise ValueError("A secret salt of at least 32 bytes is required")
    items = [_item_hash(bytes(salt), i, label) for i, label in enumerate(labels)]
    if not items:
        raise ValueError("At least one label is required")
    root = hashlib.sha256(b"".join(bytes.fromhex(h) for h in items)).hexdigest()
    return {"scheme": "neuro3d.label-commitment.v1", "count": len(items), "root": root, "item_hashes": items}


def verify_reveal(labels: Iterable, salt: bytes, root: str, count: int) -> bool:
    """True only when the revealed labels and salt reproduce the published commitment."""
    try:
        c = commit_labels(labels, salt)
    except (ValueError, TypeError):
        return False
    return c["count"] == count and secrets.compare_digest(c["root"], root)


RECORD_FIELDS = ("id", "hypothesis", "alternative", "protocol_commit", "sources", "inputs", "environment",
                 "seeds", "resource_budget", "deadline", "commands", "exit_codes", "results",
                 "independent_oracle", "decision_rule", "decision", "deviations", "limitations",
                 "published_commit", "status")
RECORD_STATES = {"OPEN", "PARTIAL", "PASS", "FAIL", "BLOCKED", "UNKNOWN", "NOT_APPLICABLE"}
_HEX40 = re.compile(r"^[0-9a-f]{40}$")
_HEX64 = re.compile(r"^[0-9a-f]{64}$")
_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}([T ]\d{2}:\d{2}(:\d{2})?([+-]\d{2}:\d{2}|Z)?)?$")


def validate_experiment_record(record: dict) -> list[str]:
    """Return every problem found against section 18; an empty list means complete."""
    if not isinstance(record, dict):
        return ["Record must be a JSON object"]
    problems = [f"Missing field: {f}" for f in RECORD_FIELDS if f not in record]
    rid = str(record.get("id", ""))
    if rid.startswith("EXP-005-"):
        problems.append("The EXP-005-* chain is closed; new work needs a new identifier")
    if record.get("status") not in RECORD_STATES:
        problems.append("Invalid status")
    for key in ("protocol_commit", "published_commit"):
        value = record.get(key)
        if value is not None and value != "PENDING" and not _HEX40.match(str(value)):
            problems.append(f"{key} must be a 40-hex commit or PENDING")
    if record.get("status") in {"PASS", "FAIL", "UNKNOWN"} and record.get("published_commit") in (None, "PENDING"):
        problems.append("A decided record must cite its published commit")
    sources = record.get("sources", [])
    if not isinstance(sources, list) or not sources:
        problems.append("sources must be a nonempty list")
    else:
        for i, s in enumerate(sources):
            if not isinstance(s, dict) or not s.get("path") or not _HEX64.match(str(s.get("sha256", ""))):
                problems.append(f"sources[{i}] needs path and lowercase sha256")
    if "deadline" in record and not _DATE.match(str(record["deadline"])):
        problems.append("deadline must be an ISO date or datetime")
    if record.get("status") == "PASS" and not (record.get("independent_oracle") and record.get("decision_rule")):
        problems.append("PASS requires an independent oracle and a prospective decision rule")
    for i, c in enumerate(record.get("jev_consultations", []) or []):
        missing = [k for k in ("question", "answer", "date", "provenance", "confidence") if not c.get(k)]
        if missing:
            problems.append(f"jev_consultations[{i}] missing {missing}")
    return problems


_DOI = re.compile(r"\b(10\.\d{4,9}/[^\s\"'<>\]\)]+)")
_ARXIV = re.compile(r"(?:arxiv\.org/(?:abs|pdf)/|arXiv:\s*)(\d{4}\.\d{4,5})(?:v\d+)?", re.IGNORECASE)


def extract_identifiers(text: str) -> dict:
    """Find DOIs and explicitly marked arXiv identifiers, deduplicated in order.

    A closing parenthesis ends a DOI so Markdown links parse cleanly; the rare
    DOIs that contain parentheses must be checked by hand.
    """
    dois, arxiv = [], []
    for m in _DOI.finditer(text):
        doi = m.group(1).rstrip(".,;:")
        if doi.lower().endswith(".pdf"):
            doi = doi[:-4]
        if doi not in dois:
            dois.append(doi)
    for m in _ARXIV.finditer(text):
        if m.group(1) not in arxiv:
            arxiv.append(m.group(1))
    return {"doi": dois, "arxiv": arxiv}


def _default_fetch(url: str, headers: dict) -> tuple[int, bytes]:
    req = urlrequest.Request(url, headers={"User-Agent": "neuro3d-citation-check/1", **headers})
    try:
        with urlrequest.urlopen(req, timeout=20) as response:
            return response.status, response.read(1 << 20)
    except urlerror.HTTPError as exc:
        return exc.code, b""


def resolve_identifiers(identifiers: dict, fetch: Callable[[str, dict], tuple[int, bytes]] | None = None) -> list[dict]:
    """Check that identifiers exist. Existence never proves the citation is apt.

    DOI: FOUND iff doi.org's handle API answers 200 with responseCode 1.
    arXiv: FOUND iff the abs page answers 200; NOT_FOUND on 404.
    Anything else is ERROR and needs a manual check.
    """
    fetch = fetch or _default_fetch
    out = []
    for doi in identifiers.get("doi", []):
        try:
            status, body = fetch("https://doi.org/api/handles/"+doi, {"Accept": "application/json"})
            code = json.loads(body.decode("utf-8")).get("responseCode") if status == 200 else None
            state = "FOUND" if code == 1 else "NOT_FOUND" if status == 404 else "ERROR"
            out.append({"kind": "doi", "id": doi, "status": state, "http": status})
        except (OSError, ValueError) as exc:
            out.append({"kind": "doi", "id": doi, "status": "ERROR", "detail": str(exc)})
    for aid in identifiers.get("arxiv", []):
        try:
            status, _ = fetch("https://arxiv.org/abs/"+aid, {})
            state = "FOUND" if status == 200 else "NOT_FOUND" if status == 404 else "ERROR"
            out.append({"kind": "arxiv", "id": aid, "status": state, "http": status})
        except OSError as exc:
            out.append({"kind": "arxiv", "id": aid, "status": "ERROR", "detail": str(exc)})
    return out

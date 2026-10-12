"""Restore checkout newline conversions only when the indexed blob matches a pin.

Never regenerate a manifest, normalize a receipt or replace a genuine edit.
Run with --write explicitly. The restoration receipt is a new artifact.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT=Path(__file__).resolve().parents[1]


def restore(manifest,write=False):
    manifest=manifest.resolve()
    if not manifest.is_relative_to(ROOT):
        raise ValueError("Repository manifest required")
    rows=[]
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if not line.strip():continue
        match=re.fullmatch(r"([0-9a-f]{64}) [ *](.+)",line)
        if not match:raise ValueError("Invalid SHA256 line")
        expected,name=match.groups();path=(manifest.parent/name).resolve()
        if not path.is_relative_to(ROOT):raise ValueError("Manifest path escapes repository")
        before=path.read_bytes();actual=hashlib.sha256(before).hexdigest()
        if actual==expected:continue
        relative=path.relative_to(ROOT).as_posix()
        blob=subprocess.check_output(["git","show",":"+relative],cwd=ROOT)
        if hashlib.sha256(blob).hexdigest()!=expected:
            raise ValueError("Indexed bytes do not match historical pin: "+relative)
        if before!=blob.replace(b"\n",b"\r\n") or b"\r\n" in blob:
            raise ValueError("Mismatch is not a pure checkout LF to CRLF conversion: "+relative)
        rows.append({"path":relative,"before_sha256":actual,"indexed_sha256":expected,"write":write})
    # Preflight every mismatch before touching any destination.
    if write:
        for row in rows:
            blob=subprocess.check_output(["git","show",":"+row["path"]],cwd=ROOT)
            (ROOT/row["path"]).write_bytes(blob)
    return {"schema":"neuro3d.checkout_restoration.v1","manifest":manifest.relative_to(ROOT).as_posix(),
            "rows":rows,"scope":"Restores exact indexed historical bytes; expected hashes unchanged"}


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--manifest",type=Path,required=True)
    p.add_argument("--write",action="store_true");p.add_argument("--out",type=Path,required=True);a=p.parse_args()
    report=restore(a.manifest,a.write)
    with a.out.open("x",encoding="utf-8",newline="\n") as stream:json.dump(report,stream,indent=2);stream.write("\n")
    print(json.dumps({"restored":len(report["rows"]),"write":a.write}))

"""Extract the guide's complete CODEFILE blocks without overwriting other work."""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path, PurePosixPath
import re
import sys


PATTERN = re.compile(r"^<!-- CODEFILE: ([^\n]+) -->\s*\n```(?:python|text|json|yaml|glsl)\n(.*?)\n```", re.DOTALL | re.MULTILINE)


def extract(text: str) -> list[tuple[str, bytes]]:
    """Validate explicit support paths and return complete LF-normalized payloads."""
    blocks, seen = [], set()
    for relative, body in PATTERN.findall(text):
        relative = relative.strip()
        path = PurePosixPath(relative)
        if path.is_absolute() or ".." in path.parts or ":" in relative or "\\" in relative or not relative.startswith("agent_support/"):
            raise ValueError("Every code target must be beneath agent_support/")
        if relative in seen:
            raise ValueError("Duplicate code target: "+relative)
        seen.add(relative)
        blocks.append((relative, (body.replace("\r\n", "\n")+"\n").encode("utf-8")))
    if not blocks:
        raise ValueError("No complete CODEFILE blocks were found")
    if len(re.findall(r"^<!-- CODEFILE:", text, re.MULTILINE)) != len(blocks):
        raise ValueError("An incomplete or unsupported CODEFILE block was found")
    return blocks


def materialize(blocks: list[tuple[str, bytes]], root: Path) -> list[dict]:
    """Preflight every destination, then create only missing support files."""
    root = root.resolve()
    prepared = []
    for relative, payload in blocks:
        destination = (root/relative).resolve()
        if not destination.is_relative_to(root):
            raise ValueError("A destination escapes the selected root")
        if destination.exists() and (not destination.is_file() or destination.read_bytes() != payload):
            raise ValueError("Different existing content will not be overwritten: "+relative)
        prepared.append((relative, destination, payload))
    output = []
    for relative, destination, payload in prepared:
        existed = destination.exists()
        if not existed:
            destination.parent.mkdir(parents=True, exist_ok=True)
            with destination.open("xb") as stream:
                stream.write(payload)
        output.append({"path": relative, "bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest(), "created": not existed})
    return output


def main() -> int:
    """Validate a guide or extract its support kit into an explicitly chosen root."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("guide", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    try:
        blocks = extract(args.guide.read_text(encoding="utf-8"))
        if args.write:
            records = materialize(blocks, args.root)
            for row in records:
                print(row["path"], row["bytes"], row["sha256"])
        else:
            print("Validated complete code blocks:", len(blocks))
        return 0
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

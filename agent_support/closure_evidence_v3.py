"""Windows UTF-8 successor; preserve the guide's exact v1 support bytes."""
import subprocess
import closure_evidence as original


def git_utf8(root, *arguments):
    return subprocess.check_output(["git", "-C", str(root), *arguments],
                                   encoding="utf-8", timeout=60)


def inventory(root):
    previous = original._git
    try:
        original._git = git_utf8
        return original.inventory(root)
    finally:
        original._git = previous


if __name__ == "__main__":
    original._git = git_utf8
    raise SystemExit(original.main())

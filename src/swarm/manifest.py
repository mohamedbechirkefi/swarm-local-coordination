# SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0
"""Run manifests (environment capture) and the protocol-freeze check.

The freeze check fails closed: a protocol counts as frozen only if
``research/protocol_freeze.json`` exists, was written by the owner, and
the SHA-256 of every listed protocol file matches the bytes on disk.
Sessions never create that file (gate G-FREEZE).
"""

from __future__ import annotations

import hashlib
import json
import platform
import resource
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from . import __version__

REPO_ROOT = Path(__file__).resolve().parents[2]
FREEZE_FILE = REPO_ROOT / "research" / "protocol_freeze.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _git(*args: str) -> str | None:
    try:
        out = subprocess.run(["git", "-C", str(REPO_ROOT), *args], capture_output=True,
                             text=True, timeout=10, check=True)
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.strip()


def git_revision() -> tuple[str, bool | None]:
    rev = _git("rev-parse", "HEAD") or "unknown"
    status = _git("status", "--porcelain")
    return rev, (None if status is None else bool(status))


def cpu_name() -> str:
    if sys.platform == "darwin":
        try:
            out = subprocess.run(["sysctl", "-n", "machdep.cpu.brand_string"], capture_output=True,
                                 text=True, timeout=5, check=True)
            return out.stdout.strip()
        except (OSError, subprocess.SubprocessError):
            pass
    return platform.processor() or platform.machine()


def peak_rss_bytes() -> int | None:
    """Peak resident set size of this process (ru_maxrss: bytes on macOS, KiB on Linux)."""
    try:
        v = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    except (OSError, ValueError):
        return None
    return int(v if sys.platform == "darwin" else v * 1024)


def environment() -> dict:
    rev, dirty = git_revision()
    return {
        "git_revision": rev,
        "git_dirty": dirty,
        "package_version": __version__,
        "python": platform.python_version(),
        "numpy": np.__version__,
        "os": f"{platform.system()} {platform.release()} ({platform.platform()})",
        "cpu": cpu_name(),
    }


def sha256_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def freeze_status(protocol_paths: list[str], freeze_file: Path = FREEZE_FILE,
                  root: Path = REPO_ROOT) -> tuple[bool, str]:
    """Return (frozen, reason). Frozen only if every path is listed with a matching hash."""
    if not freeze_file.exists():
        return False, f"no freeze record at {freeze_file.relative_to(root) if freeze_file.is_relative_to(root) else freeze_file}"
    try:
        record = json.loads(freeze_file.read_text(encoding="utf-8"))
        hashes = {e["path"]: e["sha256"] for e in record["protocols"]}
        approved = record["approved_by"]
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        return False, f"malformed freeze record ({exc})"
    if approved != "owner":
        return False, "freeze record not approved by the owner"
    for p in protocol_paths:
        if p not in hashes:
            return False, f"{p} is not listed in the freeze record"
        actual = sha256_file(root / p)
        if actual != hashes[p]:
            return False, f"{p} changed since the freeze (sha256 {actual} != {hashes[p]})"
    return True, "frozen"

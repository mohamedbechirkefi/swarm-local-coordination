# SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0
"""Run-time provenance for M3 (confirmatory and smoke runs).

  python experiments/provenance.py prelaunch DIR --config CFG
      Before a run: records the git revision and dirty flag, the SHA-256 of
      the data manifest, of the config file and its canonical hash, the
      machine, the load average and the UTC launch time in DIR/launch.json.
  python experiments/provenance.py finalize DIR [--exit-status N]
      After a run: writes DIR/provenance.csv (one row per run: run id,
      config hash, seed, revision, data manifest hash, hardware, start and
      end times, status) and DIR/raw_manifest.json (SHA-256 of every raw
      file). Every run in DIR/runs appears; none is dropped.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from swarm.config import canonical_hash  # noqa: E402
from swarm.manifest import environment, utc_now  # noqa: E402

DATA_MANIFEST = ROOT / "data" / "manifest.json"
RAW_TOP = ("experiment_config.json", "metrics.csv", "run_manifest.json", "execution.json", "launch.json")


def sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def prelaunch(out: Path, config: Path) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    exp = json.loads(config.read_text(encoding="utf-8"))
    rec = {"record_type": "swarm.launch", "launched_utc": utc_now(), **environment(),
           "config_path": str(config.relative_to(ROOT)) if config.is_absolute() else str(config),
           "config_sha256": sha256(ROOT / config if not config.is_absolute() else config),
           "config_canonical_sha256": canonical_hash(exp),
           "data_manifest_path": "data/manifest.json", "data_manifest_sha256": sha256(DATA_MANIFEST),
           "load_average": list(os.getloadavg()), "cpu_count": os.cpu_count(),
           "memory_bytes": _memsize()}
    (out / "launch.json").write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    return rec


def _memsize() -> int | None:
    try:
        return int(subprocess.run(["sysctl", "-n", "hw.memsize"], capture_output=True, text=True,
                                  timeout=5, check=True).stdout.strip())
    except (OSError, subprocess.SubprocessError, ValueError):
        return None


def finalize(out: Path, exit_status: int | None) -> tuple[int, int]:
    launch = json.loads((out / "launch.json").read_text(encoding="utf-8"))
    runs = sorted((out / "runs").glob("*.json"))
    rows = []
    for f in runs:
        r = json.loads(f.read_text(encoding="utf-8"))
        m = r["manifest"]
        rows.append({"run_id": r["run_id"], "experiment_id": r["experiment_id"], "label": r["label"],
                     "config_hash": r["config_hash"], "seed": r["config"]["seed"],
                     "git_revision": m["git_revision"], "git_dirty": m["git_dirty"],
                     "data_manifest_sha256": launch["data_manifest_sha256"],
                     "hardware": f"{m['cpu']}; {launch['cpu_count']} cores; "
                                 f"{launch['memory_bytes']} bytes RAM; {m['os']}",
                     "python": m["python"], "numpy": m["numpy"],
                     "started_utc": m["started_utc"], "finished_utc": m["finished_utc"],
                     "runtime_s": m["runtime_s"], "status": r["status"], "error": r["error"] or ""})
    with open(out / "provenance.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]) if rows else ["run_id"])
        w.writeheader()
        w.writerows(rows)
    files = {p: sha256(out / p) for p in RAW_TOP if (out / p).exists()}
    files.update({f"runs/{f.name}": sha256(f) for f in runs})
    files["provenance.csv"] = sha256(out / "provenance.csv")
    total = sum((out / p).stat().st_size for p in files)
    manifest = {"record_type": "swarm.raw_manifest", "generated_utc": utc_now(),
                "directory": str(out.relative_to(ROOT)), "process_exit_status": exit_status,
                "runs": len(rows), "failed": sum(r["status"] != "ok" for r in rows),
                "total_bytes": total, "sha256": files}
    (out / "raw_manifest.json").write_text(json.dumps(manifest, indent=1) + "\n", encoding="utf-8")
    return len(rows), manifest["failed"]


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("prelaunch")
    a.add_argument("dir")
    a.add_argument("--config", required=True)
    b = sub.add_parser("finalize")
    b.add_argument("dir")
    b.add_argument("--exit-status", type=int)
    args = p.parse_args(argv)
    out = (ROOT / args.dir) if not Path(args.dir).is_absolute() else Path(args.dir)
    if args.cmd == "prelaunch":
        rec = prelaunch(out, Path(args.config))
        print(f"launch record: revision {rec['git_revision']} dirty {rec['git_dirty']}, "
              f"data manifest {rec['data_manifest_sha256'][:12]}, load {rec['load_average']}")
    else:
        n, failed = finalize(out, args.exit_status)
        print(f"provenance: {n} runs, {failed} not ok; raw_manifest.json written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

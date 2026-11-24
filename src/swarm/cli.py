# SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0
"""Command-line interface: smoke, run, bench, report, test.

  python -m swarm.cli smoke [--config EXP.json] [--workers K]
  python -m swarm.cli run --config EXP.json [--workers K]
  python -m swarm.cli bench --config BENCH.json
  python -m swarm.cli report --results DIR [--title T] [--pdf]
  python -m swarm.cli test [pytest args...]

``run`` refuses any confirmatory configuration while the protocol is not
frozen by the owner (research/protocol_freeze.json, gate G-FREEZE).
``smoke`` accepts exploratory configurations only; without --config it runs
a tiny built-in configuration into results/exploratory/cli-smoke/.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from .bench import run_bench
from .config import ConfigError
from .manifest import REPO_ROOT
from .report import build_report
from .runner import RunRefused, load_experiment, run_experiment
from .schema import EXPERIMENT_SCHEMA_VERSION, SchemaError

BUILTIN_SMOKE = {
    "schema_version": EXPERIMENT_SCHEMA_VERSION,
    "experiment_id": "EXP-001",
    "label": "exploratory",
    "confirmatory": False,
    "description": "Built-in CLI smoke check: tiny model, all arms, two seeds. Not a result.",
    "base": {"n_agents": 40, "density": 1.0, "noise": 0.3, "radius": 1.0, "steps": 120,
             "t_disturb": 60, "window": 60, "pre_window": 20},
    "grid": {"arm": ["A0", "A1", "A2"]},
    "seeds": [1, 2],
    "output_dir": "results/exploratory/cli-smoke",
    "store_series": True,
}


def _print_run(records: list[dict], out: str) -> None:
    failed = sum(r["status"] == "failed" for r in records)
    print(f"{len(records)} runs written to {out} ({failed} failed); label {records[0]['label']}")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="swarm")
    sub = p.add_subparsers(dest="cmd", required=True)
    sp = sub.add_parser("smoke", help="exploratory smoke run")
    sp.add_argument("--config")
    sp.add_argument("--workers", type=int, default=1)
    rp = sub.add_parser("run", help="run an experiment configuration")
    rp.add_argument("--config", required=True)
    rp.add_argument("--workers", type=int, default=1)
    bp = sub.add_parser("bench", help="neighbour-search benchmark (exploratory)")
    bp.add_argument("--config", required=True)
    pp = sub.add_parser("report", help="build tables, figures and report from result files")
    pp.add_argument("--results", required=True)
    pp.add_argument("--title", default="SWARM run report")
    pp.add_argument("--pdf", action="store_true")
    pp.add_argument("--workers-assumed", type=int, default=8)
    tp = sub.add_parser("test", help="run the test suite")
    tp.add_argument("pytest_args", nargs=argparse.REMAINDER)
    a = p.parse_args(argv)

    try:
        if a.cmd == "smoke":
            exp = load_experiment(Path(a.config)) if a.config else dict(BUILTIN_SMOKE)
            if exp["label"] != "exploratory" or exp["confirmatory"]:
                raise RunRefused("smoke accepts exploratory configurations only")
            recs = run_experiment(exp, workers=a.workers)
            _print_run(recs, exp["output_dir"])
            return 0 if all(r["status"] == "ok" for r in recs) else 1
        if a.cmd == "run":
            exp = load_experiment(Path(a.config))
            recs = run_experiment(exp, workers=a.workers)
            _print_run(recs, exp["output_dir"])
            return 0 if all(r["status"] == "ok" for r in recs) else 1
        if a.cmd == "bench":
            spec = json.loads(Path(a.config).read_text(encoding="utf-8"))
            rows = run_bench(spec)
            bad = sum(r["mismatched_steps"] for r in rows)
            print(f"{len(rows)} benchmark rows written to {spec['output_dir']}; mismatched steps: {bad}")
            return 0 if bad == 0 else 1
        if a.cmd == "report":
            md = build_report(Path(a.results), a.title, pdf=a.pdf, workers_assumed=a.workers_assumed)
            print(f"report written to {md}" + (f" and {md.with_suffix('.pdf')}" if a.pdf else ""))
            return 0
        if a.cmd == "test":
            return subprocess.call([sys.executable, "-m", "pytest", "-q", *a.pytest_args], cwd=REPO_ROOT)
    except (RunRefused, ConfigError, SchemaError, FileNotFoundError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

# SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0
"""Tests of the frozen confirmatory analysis helpers (experiments/analyse_confirmatory.py)
and the provenance helper, on synthetic records and a tiny real simulation."""

import copy
import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest

from swarm.cli import BUILTIN_SMOKE
from swarm.runner import load_results, run_experiment

ROOT = Path(__file__).resolve().parents[1]


def _load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "experiments" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ac = _load("analyse_confirmatory")
prov = _load("provenance")


def _rec(arm, cell, seed, v, status="ok", **cfg):
    c = {"arm": arm, "density": cell[0], "noise": cell[1], "radius": cell[2], "seed": seed, **cfg}
    return {"run_id": f"{arm}{cell}{seed}", "status": status, "config": c,
            "metrics": {"phi_post": None if status != "ok" else v}, "error": None}


def test_pair_matches_seeds_and_skips_failed():
    cell = (1.0, 0.1, 1.0)
    recs = [_rec("A0", cell, s, 0.5) for s in (1, 2, 3)] + [_rec("A1", cell, 1, 0.7), _rec("A1", cell, 2, 0.4),
                                                           _rec("A1", cell, 3, None, status="failed")]
    d = ac.pair(ac.values(recs, "A1", "phi_post"), ac.values(recs, "A0", "phi_post"))
    assert list(d) == [cell]
    np.testing.assert_allclose(d[cell], [0.2, -0.1])


def test_pair_restricts_cells():
    a, b = (0.5, 0.1, 1.0), (1.0, 0.3, 1.0)
    t = {a: {1: 1.0}, b: {1: 1.0}}
    c = {a: {1: 0.0}, b: {1: 0.0}}
    assert list(ac.pair(t, c, cells={a})) == [a]


def test_failure_check_stop_rule():
    cell = (1.0, 0.1, 1.0)
    recs = [_rec("A0", cell, s, 0.5) for s in range(20)] + [_rec("A1", cell, s, 0.5) for s in range(19)]
    recs.append(_rec("A1", cell, 19, None, status="failed"))
    assert not ac.failure_check(recs)["stop"]  # exactly 5% is not more than 5%
    recs[-2] = _rec("A1", cell, 18, None, status="failed")
    assert ac.failure_check(recs)["stop"]


@pytest.mark.parametrize("ci,ref,expected", [
    ((-0.3, -0.1), (0.2, 0.1, 0.3), "invalidated"),
    ((0.1, 0.3), (-0.2, -0.3, -0.1), "invalidated"),
    ((-0.1, 0.2), (0.2, 0.1, 0.3), "weakened"),
    ((-0.1, 0.2), (0.02, -0.01, 0.05), "neither invalidated nor weakened"),
    ((0.1, 0.3), (0.2, 0.1, 0.3), "neither invalidated nor weakened"),
])
def test_classify(ci, ref, expected):
    b = {"estimate": sum(ci) / 2, "ci_low": ci[0], "ci_high": ci[1]}
    r = {"estimate": ref[0], "ci_low": ref[1], "ci_high": ref[2]}
    assert ac.classify(b, r) == expected


def test_check_metrics_on_real_runs_and_detects_tampering(tmp_path):
    e = copy.deepcopy(BUILTIN_SMOKE)
    e["base"].update(steps=60, t_disturb=30, window=30, pre_window=10, n_agents=30)
    run_experiment(e, root=tmp_path)
    recs = load_results(tmp_path / e["output_dir"])
    r = ac.check_metrics(recs)
    assert r["runs_checked"] == len(recs) == 6 and r["runs_with_mismatch"] == 0
    recs[0]["metrics"]["phi_post"] += 1e-6
    recs[1]["metrics"]["tau"] = -5
    r = ac.check_metrics(recs)
    assert r["runs_with_mismatch"] == 2
    assert {e for p in r["problems"] for e in p["errors"]} == {"phi_post", "tau"}


def test_write_generated_replaces_only_marked_block(tmp_path):
    p = tmp_path / "r.md"
    p.write_text("a\n<!-- BEGIN GENERATED:x -->\nold\n<!-- END GENERATED:x -->\nb\n")
    ac.write_generated(p, {"x": "new\nlines", "y": "ignored"})
    assert p.read_text() == "a\n<!-- BEGIN GENERATED:x -->\nnew\nlines\n<!-- END GENERATED:x -->\nb\n"


def test_provenance_finalize_lists_every_run(tmp_path, monkeypatch):
    e = copy.deepcopy(BUILTIN_SMOKE)
    e["base"].update(steps=40, t_disturb=20, window=20, pre_window=5, n_agents=20)
    run_experiment(e, root=tmp_path)
    out = tmp_path / e["output_dir"]
    cfg = tmp_path / "cfg.json"
    cfg.write_text(json.dumps(e))
    monkeypatch.setattr(prov, "ROOT", tmp_path)
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "manifest.json").write_text("{}")
    monkeypatch.setattr(prov, "DATA_MANIFEST", tmp_path / "data" / "manifest.json")
    prov.prelaunch(out, cfg)
    n, failed = prov.finalize(out, 0)
    assert (n, failed) == (6, 0)
    man = json.loads((out / "raw_manifest.json").read_text())
    assert sum(k.startswith("runs/") for k in man["sha256"]) == 6
    lines = (out / "provenance.csv").read_text().strip().splitlines()
    assert len(lines) == 7 and "data_manifest_sha256" in lines[0]

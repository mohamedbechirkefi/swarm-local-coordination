# SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0
"""Schema, runner gates, freeze check, analysis, integration config -> results -> report."""

import copy
import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

from swarm.analysis import decision, paired_differences, stratified_bootstrap
from swarm.cli import BUILTIN_SMOKE, main
from swarm.manifest import freeze_status
from swarm.report import build_report
from swarm.runner import RunRefused, check_allowed, expand, load_results, run_experiment
from swarm.schema import SchemaError, read_result, validate_experiment, validate_result


def _exp(**kw):
    e = copy.deepcopy(BUILTIN_SMOKE)
    e["base"].update(steps=40, t_disturb=20, window=20, pre_window=5, n_agents=20)
    e.update(kw)
    return e


def test_expand_and_run_ids():
    e = _exp(grid={"arm": ["A0", "A1"], "noise": [0.1, 0.3]}, seeds=[1, 2, 3])
    runs = expand(e)
    assert len(runs) == 12
    ids = [r for r, _ in runs]
    assert len(set(ids)) == 12 and ids[0] == "EXP-001_A0_noise0.1_s1"


def test_expand_rejects_invalid_cell():
    with pytest.raises(Exception):
        expand(_exp(grid={"arm": ["A0"], "noise": [2.0]}))


def test_integration_run_validate_report(tmp_path):
    e = _exp(output_dir="results/exploratory/t", full_matrix_runs=540)
    recs = run_experiment(e, root=tmp_path)
    assert len(recs) == 6 and all(r["status"] == "ok" for r in recs)
    out = tmp_path / "results/exploratory/t"
    loaded = load_results(out)
    assert [r["run_id"] for r in loaded] == sorted(r["run_id"] for r in recs)
    assert (out / "metrics.csv").read_text().count("\n") == 7
    manifest = json.loads((out / "run_manifest.json").read_text())
    assert len(manifest["runs"]) == 6 and manifest["runs"][0]["git_revision"]
    md = build_report(out, "test report")
    text = md.read_text()
    assert "EXPLORATORY" in text and "A1-A0" in text and "540 runs" in text
    assert (out / "report" / "fig01_phi_timeseries.png").exists()
    data = json.loads((out / "report" / "report_data.json").read_text())
    assert data["runs"] == 6 and data["failed"] == 0


def test_results_identical_across_reruns(tmp_path):
    e = _exp(output_dir="results/exploratory/a")
    r1 = run_experiment(e, root=tmp_path)
    r2 = run_experiment(dict(e, output_dir="results/exploratory/b"), root=tmp_path)
    for a, b in zip(r1, r2):
        assert a["metrics"] == b["metrics"] and a["series"] == b["series"]


def test_parallel_equals_serial(tmp_path):
    e = _exp(output_dir="results/exploratory/s")
    r1 = run_experiment(e, root=tmp_path, workers=1)
    r2 = run_experiment(dict(e, output_dir="results/exploratory/p"), root=tmp_path, workers=2)
    assert [r["metrics"] for r in r1] == [r["metrics"] for r in r2]


def test_failed_run_is_recorded_not_dropped(tmp_path, monkeypatch):
    import swarm.runner as runner

    def boom(cfg):
        raise RuntimeError("injected failure")
    monkeypatch.setattr(runner, "simulate", boom)
    recs = run_experiment(_exp(output_dir="results/exploratory/f"), root=tmp_path)
    assert all(r["status"] == "failed" and "injected" in r["error"] for r in recs)
    assert len(load_results(tmp_path / "results/exploratory/f")) == 6


def test_confirmatory_refused_while_unfrozen(tmp_path):
    e = _exp(label="confirmatory", confirmatory=True, output_dir="results/confirmatory/x")
    with pytest.raises(RunRefused, match="not frozen"):
        run_experiment(e, root=tmp_path)
    assert not (tmp_path / "results").exists()


def test_cli_run_refuses_confirmatory_on_repo(tmp_path, capsys):
    e = _exp(label="confirmatory", confirmatory=True, output_dir="results/confirmatory/x")
    p = tmp_path / "c.json"
    p.write_text(json.dumps(e))
    assert main(["run", "--config", str(p)]) == 2
    assert "not frozen" in capsys.readouterr().err


@pytest.mark.parametrize("kw", [
    dict(label="confirmatory", confirmatory=False),
    dict(label="exploratory", confirmatory=True),
    dict(output_dir="results/confirmatory/x"),
    dict(output_dir="results/x"),
    dict(output_dir="results/exploratory/../confirmatory/x"),
    dict(output_dir="/tmp/x"),
])
def test_label_and_output_rules(kw, tmp_path):
    with pytest.raises(RunRefused):
        check_allowed(_exp(**kw), root=tmp_path)


def test_freeze_check(tmp_path):
    (tmp_path / "research").mkdir()
    proto = tmp_path / "research" / "protocol.md"
    proto.write_text("protocol v1\n")
    ff = tmp_path / "research" / "protocol_freeze.json"
    assert freeze_status(["research/protocol.md"], ff, tmp_path)[0] is False
    sha = hashlib.sha256(proto.read_bytes()).hexdigest()
    ff.write_text(json.dumps({"approved_by": "owner", "protocols": [
        {"path": "research/protocol.md", "sha256": sha}]}))
    assert freeze_status(["research/protocol.md"], ff, tmp_path) == (True, "frozen")
    proto.write_text("protocol v2\n")
    assert freeze_status(["research/protocol.md"], ff, tmp_path)[0] is False
    ff.write_text(json.dumps({"approved_by": "session", "protocols": []}))
    assert freeze_status(["research/protocol.md"], ff, tmp_path)[0] is False
    ff.write_text("{not json")
    assert freeze_status(["research/protocol.md"], ff, tmp_path)[0] is False


def test_repository_protocol_is_not_frozen():
    frozen, _ = freeze_status(["research/protocol.md"])
    assert frozen is False


def test_schema_rejects_malformed(tmp_path):
    recs = run_experiment(_exp(output_dir="results/exploratory/m"), root=tmp_path)
    good = recs[0]
    validate_result(good)
    for mutate in (lambda r: r.update(schema_version="2.0.0"),
                   lambda r: r["metrics"].update(phi_post=1.5),
                   lambda r: r["config"].update(arm="A9"),
                   lambda r: r.pop("manifest"),
                   lambda r: r.update(extra=1),
                   lambda r: r.update(config_hash="abc")):
        bad = copy.deepcopy(good)
        mutate(bad)
        with pytest.raises(SchemaError):
            validate_result(bad)
    f = tmp_path / "bad.json"
    f.write_text("{")
    with pytest.raises(SchemaError):
        read_result(f)
    with pytest.raises(SchemaError):
        validate_experiment({"schema_version": "1.0.0"})


def test_report_fails_closed_on_missing_results(tmp_path):
    with pytest.raises(FileNotFoundError):
        build_report(tmp_path, "x")


def _rec(arm, seed, val, cell=0.1):
    return {"status": "ok", "config": {"arm": arm, "seed": seed, "noise": cell},
            "metrics": {"phi_post": val}}


def test_paired_differences_and_missing_pairs():
    recs = [_rec("A0", 1, 0.5), _rec("A1", 1, 0.7), _rec("A0", 2, 0.4), _rec("A1", 3, 0.9)]
    d = paired_differences(recs, "phi_post", "A1", "A0")
    (cell,) = d
    assert d[cell] == pytest.approx({1: 0.2})


def test_bootstrap_against_simple_loop():
    cells = {"a": np.array([0.1, 0.2, 0.3]), "b": np.array([-0.1, 0.0])}
    res = stratified_bootstrap(cells, n_boot=500, seed=3)
    assert res["estimate"] == pytest.approx((0.2 + -0.05) / 2)
    rng = np.random.Generator(np.random.PCG64(3))
    boots = np.zeros(500)
    for a in (cells["a"], cells["b"]):
        idx = rng.integers(0, a.size, size=(500, a.size))
        boots += a[idx].mean(axis=1)
    boots /= 2
    assert res["ci_low"] == pytest.approx(np.quantile(boots, 0.025))
    assert res["ci_low"] <= res["estimate"] <= res["ci_high"]
    const = stratified_bootstrap({"a": np.full(5, 0.3)}, n_boot=100)
    assert const["ci_low"] == pytest.approx(0.3) and const["ci_high"] == pytest.approx(0.3)
    with pytest.raises(ValueError):
        stratified_bootstrap({})


def test_decision_rule():
    assert decision(0.01, 0.2, 0.05) == "rejects H0"
    assert decision(-0.2, -0.01, 0.05) == "rejects H0"
    assert decision(-0.03, 0.04, 0.05) == "practically equivalent"
    assert decision(-0.1, 0.04, 0.05) == "inconclusive"

# SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0
"""Frozen protocol v1.0 (owner-approved 2026-11-24): amended values, freeze record,
and the runner gate accepting frozen confirmatory configs and refusing changed ones."""

import copy
import hashlib
import importlib.util
import json
import shutil
from pathlib import Path

import pytest

import swarm.runner as runner
from swarm.config import SimConfig, canonical_hash
from swarm.manifest import REPO_ROOT, config_frozen, freeze_status
from swarm.runner import RunRefused, check_allowed, load_experiment, run_experiment

FREEZE = REPO_ROOT / "research" / "protocol_freeze.json"
CONFIGS = ["experiments/EXP-002/config.json", "experiments/EXP-003/config_S1.json",
           "experiments/EXP-003/config_S2.json", "experiments/EXP-003/config_S3.json"]
PROTOCOLS = ["research/protocol.md", "research/experiments/EXP-002/protocol.md",
             "research/experiments/EXP-003/protocol.md"]
SEEDS = list(range(1001, 1021))


def _cfg(path: str) -> dict:
    return load_experiment(REPO_ROOT / path)


def test_amended_values_in_frozen_configs():
    e2 = _cfg(CONFIGS[0])
    b = e2["base"]
    # AM-1 w_c = 0.5; AM-2 t_d = 3000 (rule R-BI), W = 500; AM-3 20 seeds.
    assert (b["w_cohesion"], b["t_disturb"], b["window"], b["steps"]) == (0.5, 3000, 500, 3500)
    assert e2["seeds"] == SEEDS and e2["confirmatory"] and e2["label"] == "confirmatory"
    assert len(runner.expand(e2)) == 1080
    s1, s2, s3 = (_cfg(p) for p in CONFIGS[1:])
    assert s1["base"]["neighbourhood"] == "topological" and s1["base"]["k_topological"] == 7
    assert s2["grid"]["w_cohesion"] == [0.25, 1.0] and s2["grid"]["arm"] == ["A1"]
    assert s3["base"]["boundary"] == "reflecting"
    for e in (s1, s2, s3):
        assert e["seeds"] == SEEDS and e["base"]["t_disturb"] == 3000
        assert e["grid"]["density"] == [0.5, 2.0] and e["grid"]["noise"] == [0.1, 0.5]
        assert len(runner.expand(e)) == 160
    for e in (s1, s3):
        assert e["base"]["w_cohesion"] == 0.5


def test_freeze_record_matches_disk():
    rec = json.loads(FREEZE.read_text())
    assert rec["approved_by"] == "owner" and rec["approval_date"] == "2026-11-24"
    assert {p["path"] for p in rec["protocols"]} == set(PROTOCOLS)
    assert {c["path"] for c in rec["configs"]} == set(CONFIGS)
    for c in rec["configs"]:
        assert hashlib.sha256((REPO_ROOT / c["path"]).read_bytes()).hexdigest() == c["sha256"]
        assert canonical_hash(_cfg(c["path"])) == c["canonical_sha256"]
    for p in PROTOCOLS:
        assert freeze_status([p]) == (True, "frozen")


@pytest.mark.parametrize("path", CONFIGS)
def test_runner_accepts_frozen_configs(path):
    check_allowed(_cfg(path))  # no exception


@pytest.mark.parametrize("mutate", [
    lambda e: e.update(seeds=e["seeds"][:10]),
    lambda e: e["base"].update(w_cohesion=1.0),
    lambda e: e["base"].update(t_disturb=500, steps=1000),
    lambda e: e.update(description=e["description"] + " "),
])
def test_runner_refuses_changed_config(mutate):
    e = copy.deepcopy(_cfg(CONFIGS[0]))
    mutate(e)
    with pytest.raises(RunRefused, match="configuration not frozen"):
        check_allowed(e)


def _frozen_copy(tmp_path: Path) -> Path:
    for p in PROTOCOLS + CONFIGS + ["research/protocol_freeze.json"]:
        (tmp_path / p).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(REPO_ROOT / p, tmp_path / p)
    return tmp_path


def test_runner_refuses_changed_protocol(tmp_path):
    root = _frozen_copy(tmp_path)
    e = _cfg(CONFIGS[0])
    check_allowed(e, root=root)
    with open(root / "research/experiments/EXP-002/protocol.md", "a") as fh:
        fh.write("\nedited after freeze\n")
    with pytest.raises(RunRefused, match="protocol not frozen"):
        check_allowed(e, root=root)


def test_run_executes_frozen_config_in_copy(tmp_path, monkeypatch):
    """End to end through run_experiment on a copy, with the matrix cut to one tiny run
    after the gate (the gate sees the frozen config unchanged)."""
    root = _frozen_copy(tmp_path)
    e = _cfg(CONFIGS[0])
    tiny = SimConfig(arm="A1", n_agents=20, steps=40, t_disturb=20, window=20, pre_window=5, seed=1001)
    monkeypatch.setattr(runner, "expand", lambda exp: [("EXP-002_tiny", tiny)])
    recs = run_experiment(e, root=root)
    assert len(recs) == 1 and recs[0]["status"] == "ok" and recs[0]["label"] == "confirmatory"
    assert (root / "results/confirmatory/EXP-002/execution.json").exists()


def test_config_frozen_fails_closed(tmp_path):
    ff = tmp_path / "f.json"
    assert config_frozen("0" * 64, ff)[0] is False
    ff.write_text("{bad")
    assert config_frozen("0" * 64, ff)[0] is False
    ff.write_text(json.dumps({"configs": [{"canonical_sha256": "a" * 64}]}))
    assert config_frozen("a" * 64, ff) == (True, "frozen")
    assert config_frozen("b" * 64, ff)[0] is False


def _rule():
    spec = importlib.util.spec_from_file_location(
        "apply_burnin_rule", REPO_ROOT / "experiments/EXP-001/apply_burnin_rule.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.choose_t_d


def test_burnin_rule_r_bi():
    choose = _rule()
    c = (500, 1000, 1500, 2000, 3000, 4000)
    m = {"fast": dict(zip(c, [0.9] * 6)),
         "slow": dict(zip(c, [0.3, 0.4, 0.45, 0.6, 0.7, 0.8])),
         "never": dict(zip(c, [0.1] * 6))}
    t_d, orderable, below = choose(m)
    assert (t_d, orderable, below) == (2000, ["fast", "slow"], [])
    m["slow"][3000] = 0.49  # only the candidate itself counts, not later steps
    m["slow"][2000] = 0.6
    assert choose(m)[0] == 2000
    m["slow"][2000] = 0.49
    assert choose(m)[0] == 4000
    assert choose({"never": m["never"]})[0] == 500


def test_burnin_decision_file_gives_t_d_3000():
    d = json.loads((REPO_ROOT / "results/exploratory/EXP-001-burnin-rule-decision.json").read_text())
    assert d["t_d"] == 3000 and d["steps"] == 3500 and len(d["orderable_cells"]) == 8

# SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0
"""Simulation: determinism (V2), invariants (V3), hand-computed full step (V4),
common random numbers across arms, and a loop-reference differential run."""

import math

import numpy as np
import pytest

from reference import ref_A0, ref_A1, ref_A2
from swarm.config import ConfigError, SimConfig
from swarm.geometry import reflect, wrap_angle, wrap_positions
from swarm.simulate import initial_state, run

SMALL = dict(n_agents=30, density=1.0, radius=1.0, steps=80, t_disturb=40, window=40, pre_window=10)


@pytest.mark.parametrize("arm", ["A0", "A1", "A2"])
def test_v2_bit_identical_reruns(arm):
    cfg = SimConfig(arm=arm, seed=5, **SMALL)
    a, b = run(cfg, record_trajectory=True), run(cfg, record_trajectory=True)
    assert np.array_equal(a.trajectory["x"], b.trajectory["x"])
    assert np.array_equal(a.trajectory["theta"], b.trajectory["theta"])
    assert np.array_equal(a.phi, b.phi)
    assert a.metrics == b.metrics


def test_different_seeds_differ():
    a = run(SimConfig(seed=1, **SMALL))
    b = run(SimConfig(seed=2, **SMALL))
    assert not np.array_equal(a.phi, b.phi)


@pytest.mark.parametrize("arm", ["A0", "A1", "A2"])
@pytest.mark.parametrize("boundary", ["periodic", "reflecting"])
def test_v3_invariants(arm, boundary):
    cfg = SimConfig(arm=arm, seed=3, boundary=boundary, noise=0.5, **SMALL)
    res = run(cfg, record_trajectory=True)
    x, th = res.trajectory["x"], res.trajectory["theta"]
    L = cfg.box
    unit = np.hypot(np.cos(th), np.sin(th))
    assert np.max(np.abs(unit - 1.0)) <= 1e-12
    assert np.all(th > -math.pi) and np.all(th <= math.pi)
    assert np.all(x >= 0.0) and np.all(x <= L)
    if boundary == "periodic":
        assert np.all(x < L)
    assert x.shape == (cfg.steps + 1, cfg.n_agents, 2)  # agent count conserved
    assert np.all((res.phi >= 0) & (res.phi <= 1))
    m = res.metrics
    assert 0 < m["cohesion_post"] <= 1
    assert m["collisions_per_agent_per_100"] >= 0
    # every step moves each agent by exactly v0 when no wrap or reflection happens
    step = np.hypot(*(x[1:] - x[:-1]).transpose(2, 0, 1))
    inner = step < L / 2
    if boundary == "periodic":
        np.testing.assert_allclose(step[inner], cfg.speed, atol=1e-12)


def test_common_random_numbers_across_arms():
    states = [initial_state(SimConfig(arm=a, seed=9, **SMALL)) for a in ("A0", "A1", "A2")]
    for s in states[1:]:
        assert np.array_equal(s[0], states[0][0])
        assert np.array_equal(s[1], states[0][1])
        assert np.array_equal(s[2], states[0][2])
        assert np.array_equal(s[3], states[0][3])
    noise = [s[4].uniform(-1, 1, 30) for s in states]
    assert np.array_equal(noise[0], noise[1]) and np.array_equal(noise[0], noise[2])
    # pre-disturbance phi identical across arms at t = 0
    phis = [run(SimConfig(arm=a, seed=9, **SMALL)).phi[0] for a in ("A0", "A1", "A2")]
    assert phis[0] == phis[1] == phis[2]


def test_shock_applied_at_t_disturb():
    cfg = SimConfig(arm="A2", noise=0.0, seed=4, **SMALL)
    res = run(cfg, record_trajectory=True)
    _, _, chosen, new, _ = initial_state(cfg)
    assert chosen.size == round(0.5 * cfg.n_agents)
    np.testing.assert_array_equal(res.trajectory["theta"][cfg.t_disturb][chosen], new)
    assert res.phi[cfg.t_disturb - 1] == pytest.approx(1.0)  # A2 with no noise is fully ordered
    assert res.phi[cfg.t_disturb] < 1.0


def test_v4_hand_computed_two_agent_full_step():
    # Build a 2-agent run, eta = 0: after one step both headings are pi/4 and
    # each agent moved by v0 * (cos pi/4, sin pi/4).
    cfg = SimConfig(arm="A0", n_agents=2, density=2 / 25.0, radius=2.0, noise=0.0, steps=1,
                    t_disturb=1, window=0, pre_window=0, shock_fraction=0.0, seed=0)
    x0, th0, _, _, _ = initial_state(cfg)
    res = run(cfg, record_trajectory=True)
    d = math.dist(x0[0], x0[1])
    d = min(d, *(math.dist(x0[0], x0[1] + np.array([a, b]) * cfg.box)
                 for a in (-1, 0, 1) for b in (-1, 0, 1)))
    if d <= 2.0:
        target = math.atan2(math.sin(th0[0]) + math.sin(th0[1]), math.cos(th0[0]) + math.cos(th0[1]))
        np.testing.assert_allclose(res.trajectory["theta"][1], [target, target], atol=1e-12)
    else:
        np.testing.assert_allclose(res.trajectory["theta"][1], th0, atol=1e-12)
    th1 = res.trajectory["theta"][1]
    expect = wrap_positions(x0 + 0.05 * np.stack([np.cos(th1), np.sin(th1)], 1), cfg.box)
    np.testing.assert_allclose(res.trajectory["x"][1], expect, atol=1e-12)


@pytest.mark.parametrize("arm", ["A0", "A1", "A2"])
@pytest.mark.parametrize("boundary", ["periodic", "reflecting"])
def test_differential_full_run_against_loop_reference(arm, boundary):
    """Replays a vectorized run step by step with the loop reference rules."""
    cfg = SimConfig(arm=arm, seed=12, boundary=boundary, n_agents=25, density=1.0, radius=1.0,
                    steps=30, t_disturb=15, window=15, pre_window=5, noise=0.3)
    res = run(cfg, record_trajectory=True)
    x, th, chosen, new, noise_rng = initial_state(cfg)
    periodic = boundary == "periodic"
    L = cfg.box
    # trajectory index t holds the state at t, with the shock already applied at t_d
    for t in range(cfg.steps):
        if t == cfg.t_disturb:
            th = th.copy()
            th[chosen] = new
            np.testing.assert_allclose(res.trajectory["theta"][t], th, atol=1e-9)
            np.testing.assert_array_equal(res.trajectory["theta"][t][chosen], new)
        if arm == "A0":
            desired = ref_A0(x, th, L, cfg.radius, periodic)
        elif arm == "A1":
            desired = ref_A1(x, th, L, cfg.radius, periodic, 0.25 * cfg.radius, 1.0, 1.0)
        else:
            desired = ref_A2(th)
        th = wrap_angle(desired + noise_rng.uniform(-0.3 * math.pi, 0.3 * math.pi, cfg.n_agents))
        x = x + cfg.speed * np.stack([np.cos(th), np.sin(th)], 1)
        x, th = (wrap_positions(x, L), th) if periodic else reflect(x, th, L)
        np.testing.assert_allclose(res.trajectory["x"][t + 1], x, atol=1e-9)
        if t + 1 != cfg.t_disturb:
            np.testing.assert_allclose(np.cos(res.trajectory["theta"][t + 1]), np.cos(th), atol=1e-9)
            np.testing.assert_allclose(np.sin(res.trajectory["theta"][t + 1]), np.sin(th), atol=1e-9)


@pytest.mark.parametrize("arm", ["A0", "A1"])
def test_cell_and_brute_index_give_identical_runs(arm):
    a = run(SimConfig(arm=arm, seed=21, index="cell", **SMALL), record_trajectory=True)
    b = run(SimConfig(arm=arm, seed=21, index="brute", **SMALL), record_trajectory=True)
    assert np.array_equal(a.trajectory["x"], b.trajectory["x"])
    assert np.array_equal(a.phi, b.phi)
    assert a.metrics["dist_evals_per_step"] < b.metrics["dist_evals_per_step"]


def test_topological_variant_runs():
    res = run(SimConfig(arm="A1", neighbourhood="topological", seed=2, **SMALL))
    assert 0 <= res.metrics["phi_post"] <= 1


def test_burn_in_only_config_has_no_post_metrics():
    res = run(SimConfig(n_agents=20, steps=50, t_disturb=50, window=0, pre_window=10, seed=1))
    assert res.metrics["phi_post"] is None and res.metrics["phi_pre"] is not None


def test_extreme_parameters():
    for kw in (dict(noise=0.0), dict(noise=1.0), dict(speed=0.0), dict(shock_fraction=1.0),
               dict(shock_fraction=0.0), dict(n_agents=1, density=0.01, radius=1.0)):
        base = dict(SMALL, **kw)
        res = run(SimConfig(seed=1, **base))
        assert np.all(np.isfinite(res.phi))
    # noise 0, A2, no shock: perfectly ordered after the first update
    res = run(SimConfig(arm="A2", noise=0.0, shock_fraction=0.0, seed=1, **SMALL))
    np.testing.assert_allclose(res.phi[1:], 1.0, atol=1e-12)


@pytest.mark.parametrize("bad", [
    dict(arm="A3"), dict(n_agents=0), dict(density=0.0), dict(density=-1.0), dict(noise=1.5),
    dict(noise=float("nan")), dict(radius=0.0), dict(speed=-0.1), dict(steps=0),
    dict(t_disturb=2000), dict(window=600), dict(pre_window=600), dict(shock_fraction=2.0),
    dict(boundary="open"), dict(neighbourhood="voronoi"), dict(index="tree"), dict(seed=-1),
    dict(n_agents=10.5), dict(n_agents=True), dict(radius="1"), dict(recovery_threshold=0.0),
    dict(radius=8.0),  # >= L/2 for N=200, rho=1 (L ~ 14.1) on a torus
])
def test_invalid_configs_rejected(bad):
    with pytest.raises(ConfigError):
        SimConfig(**bad)


def test_unknown_key_rejected():
    with pytest.raises(ConfigError):
        SimConfig.from_dict({"arm": "A0", "colour": "red"})


def test_config_hash_stable_and_sensitive():
    assert SimConfig(seed=1).config_hash() == SimConfig(seed=1).config_hash()
    assert SimConfig(seed=1).config_hash() != SimConfig(seed=2).config_hash()


@pytest.mark.parametrize("boundary", ["periodic", "reflecting"])
def test_a1_reduces_to_a0_without_separation_and_cohesion(boundary):
    """Differential check: A1 with r_s = 0 and w_c = 0 is the A0 rule."""
    kw = dict(SMALL, boundary=boundary, seed=17)
    a0 = run(SimConfig(arm="A0", **kw), record_trajectory=True)
    a1 = run(SimConfig(arm="A1", sep_ratio=0.0, w_cohesion=0.0, **kw), record_trajectory=True)
    np.testing.assert_allclose(a1.trajectory["x"], a0.trajectory["x"], atol=1e-9)
    np.testing.assert_allclose(a1.phi, a0.phi, atol=1e-9)

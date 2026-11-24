# SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0
"""Rule updates: hand-computed examples (EXP-001 V4) and differential tests."""

import math

import numpy as np
import pytest

from reference import ref_A0, ref_A1, ref_A2
from swarm import rules
from swarm.neighbors import brute_force_pairs
from swarm.simulate import _directed

PI = math.pi


def _edges(x, L=100.0, r=1.0, periodic=False):
    return _directed(brute_force_pairs(np.asarray(x, float), L, r, periodic))


def test_a0_two_agents_hand_computed():
    x = [[0.0, 0.0], [0.5, 0.0]]
    recv, other, _, _ = _edges(x)
    got = rules.align_only(np.array([0.0, PI / 2]), recv, other)
    np.testing.assert_allclose(got, [PI / 4, PI / 4], atol=1e-15)


def test_a0_out_of_range_keeps_heading():
    recv, other, _, _ = _edges([[0.0, 0.0], [5.0, 0.0]])
    th = np.array([0.3, -1.2])
    np.testing.assert_allclose(rules.align_only(th, recv, other), th, atol=1e-15)


def test_a0_three_agents_hand_computed():
    recv, other, _, _ = _edges([[0.0, 0.0], [0.3, 0.0], [0.0, 0.3]])
    got = rules.align_only(np.array([0.0, PI, PI / 2]), recv, other)
    np.testing.assert_allclose(got, [PI / 2] * 3, atol=1e-12)


def test_a0_zero_sum_keeps_heading():
    recv, other, _, _ = _edges([[0.0, 0.0], [0.5, 0.0]])
    th = np.array([0.0, PI])
    np.testing.assert_allclose(rules.align_only(th, recv, other), th)


def test_a1_separation_hand_computed():
    recv, other, disp, dist = _edges([[0.0, 0.0], [0.2, 0.0]])
    got = rules.zonal(np.array([1.0, 2.0]), recv, other, disp, dist, 0.25, 1.0, 1.0)
    assert abs(abs(got[0]) - PI) < 1e-12 and abs(got[1]) < 1e-12


def test_a1_alignment_plus_cohesion_hand_computed():
    recv, other, disp, dist = _edges([[0.0, 0.0], [0.0, 0.5]])
    got = rules.zonal(np.array([0.0, 0.0]), recv, other, disp, dist, 0.25, 1.0, 1.0)
    np.testing.assert_allclose(got, [PI / 4, -PI / 4], atol=1e-12)


def test_a1_weights_change_direction():
    recv, other, disp, dist = _edges([[0.0, 0.0], [0.0, 0.5]])
    got = rules.zonal(np.array([0.0, 0.0]), recv, other, disp, dist, 0.25, 1.0, 2.0)
    assert got[0] == pytest.approx(math.atan2(2.0, 1.0))
    got0 = rules.zonal(np.array([0.0, 0.0]), recv, other, disp, dist, 0.25, 1.0, 0.0)
    np.testing.assert_allclose(got0, [0.0, 0.0], atol=1e-15)


def test_a1_separation_has_priority_over_far_neighbours():
    # agent 0: agent 1 inside r_s, agent 2 inside r but outside r_s
    recv, other, disp, dist = _edges([[0.0, 0.0], [0.1, 0.0], [0.0, 0.9]])
    got = rules.zonal(np.array([0.0, 0.0, 0.0]), recv, other, disp, dist, 0.25, 1.0, 1.0)
    assert abs(abs(got[0]) - PI) < 1e-12


def test_a1_coincident_agents_keep_heading():
    recv, other, disp, dist = _edges([[1.0, 1.0], [1.0, 1.0]])
    th = np.array([0.4, -0.7])
    np.testing.assert_allclose(rules.zonal(th, recv, other, disp, dist, 0.25, 1.0, 1.0), th)


def test_a1_isolated_agent_follows_own_heading():
    recv, other, disp, dist = _edges([[0.0, 0.0], [9.0, 9.0]])
    th = np.array([0.4, -0.7])
    np.testing.assert_allclose(rules.zonal(th, recv, other, disp, dist, 0.25, 1.0, 1.0), th, atol=1e-15)


def test_a2_hand_computed_and_zero_case():
    np.testing.assert_allclose(rules.centralized(np.array([0.0, PI / 2, PI])), [PI / 2] * 3, atol=1e-12)
    th = np.array([0.0, PI])
    np.testing.assert_allclose(rules.centralized(th), th)


@pytest.mark.parametrize("periodic", [True, False])
def test_differential_against_loop_reference(periodic):
    rng = np.random.default_rng(7)
    L, r = 6.0, 1.0
    for _ in range(25):
        n = int(rng.integers(2, 60))
        x = rng.uniform(0, L, size=(n, 2))
        th = rng.uniform(-PI, PI, size=n)
        recv, other, disp, dist = _directed(brute_force_pairs(x, L, r, periodic))
        np.testing.assert_allclose(rules.align_only(th, recv, other), ref_A0(x, th, L, r, periodic),
                                   atol=1e-12)
        np.testing.assert_allclose(
            np.cos(rules.zonal(th, recv, other, disp, dist, 0.25, 1.0, 1.0)),
            np.cos(ref_A1(x, th, L, r, periodic, 0.25, 1.0, 1.0)), atol=1e-12)
        np.testing.assert_allclose(
            np.sin(rules.zonal(th, recv, other, disp, dist, 0.25, 1.0, 1.0)),
            np.sin(ref_A1(x, th, L, r, periodic, 0.25, 1.0, 1.0)), atol=1e-12)
        np.testing.assert_allclose(rules.centralized(th), ref_A2(th), atol=1e-12)

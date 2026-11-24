# SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0
"""Spatial indexing versus brute force (EXP-001 V1), boundary conditions, ties."""

import math

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from reference import ref_pairs
from swarm.neighbors import (brute_force_pairs, cell_list_pairs, cells_per_side, metric_pairs,
                             topological_edges)


def _same(a, b):
    return np.array_equal(a.i, b.i) and np.array_equal(a.j, b.j)


def _edge_config(rng, n, L):
    x = rng.uniform(0, L, size=(n, 2))
    k = max(1, n // 5)
    # put some agents within 1e-9 u of the four edges
    x[:k, 0] = rng.choice([0.0, 1e-9, L - 1e-9, np.nextafter(L, 0)], size=k)
    x[k:2 * k, 1] = rng.choice([0.0, 1e-9, L - 1e-9, np.nextafter(L, 0)], size=min(k, n - k))
    return x


def test_v1_cell_list_equals_brute_force_1000_configs():
    """EXP-001 V1: 1,000 random configurations, exact equality of neighbour sets."""
    rng = np.random.default_rng(20261124)
    checked = 0
    for trial in range(1000):
        n = [2, 50, 200][trial % 3]
        rho = [0.5, 1.0, 2.0][(trial // 3) % 3]
        r = [0.5, 1.0][(trial // 9) % 2]
        L = math.sqrt(200 / rho)  # box of the EXP-002 grid; N varies inside it
        periodic = trial % 4 != 3
        x = _edge_config(rng, n, L)
        a = cell_list_pairs(x, L, r, periodic)
        b = brute_force_pairs(x, L, r, periodic)
        assert _same(a, b), f"trial {trial}"
        np.testing.assert_array_equal(a.dist, b.dist)
        checked += 1
    assert checked == 1000


def test_brute_force_matches_loop_reference():
    rng = np.random.default_rng(1)
    for periodic in (True, False):
        x = rng.uniform(0, 6, size=(40, 2))
        got = brute_force_pairs(x, 6.0, 1.2, periodic)
        assert list(zip(got.i.tolist(), got.j.tolist())) == ref_pairs(x, 6.0, 1.2, periodic)


@settings(max_examples=200, deadline=None)
@given(n=st.integers(1, 60), L=st.floats(2.0, 15.0), frac=st.floats(0.05, 0.45),
       seed=st.integers(0, 2**32 - 1), periodic=st.booleans())
def test_property_cell_list_equals_brute_force(n, L, frac, seed, periodic):
    r = frac * L
    x = np.random.default_rng(seed).uniform(0, L, size=(n, 2))
    x = np.where(x >= L, 0.0, x)
    assert _same(cell_list_pairs(x, L, r, periodic), brute_force_pairs(x, L, r, periodic))


def test_wraparound_pair_found_only_when_periodic():
    L, r = 10.0, 1.0
    x = np.array([[0.1, 5.0], [9.9, 5.0]])  # torus distance 0.2, Euclidean 9.8
    for idx in ("cell", "brute"):
        p = metric_pairs(x, L, r, True, idx)
        assert p.i.tolist() == [0] and p.j.tolist() == [1]
        assert p.dist[0] == pytest.approx(0.2)
        assert p.d[0, 0] == pytest.approx(-0.2)  # minimum image from agent 0 to agent 1
        assert metric_pairs(x, L, r, False, idx).i.size == 0


def test_corner_wrap_diagonal():
    L, r = 10.0, 0.5
    x = np.array([[0.05, 0.05], [9.95, 9.95]])
    for idx in ("cell", "brute"):
        p = metric_pairs(x, L, r, True, idx)
        assert p.dist[0] == pytest.approx(math.hypot(0.1, 0.1))


def test_tie_at_exact_radius_is_neighbour():
    L = 10.0
    x = np.array([[1.0, 1.0], [1.5, 1.0]])  # distance exactly 0.5
    for idx in ("cell", "brute"):
        assert metric_pairs(x, L, 0.5, True, idx).i.size == 1
        assert metric_pairs(x, L, 0.5 - 1e-12, True, idx).i.size == 0
        assert metric_pairs(x, L, 0.5 + 1e-12, True, idx).i.size == 1


def test_small_boxes_with_fewer_than_three_cells():
    rng = np.random.default_rng(3)
    for L, r in ((2.5, 1.0), (1.9, 0.9), (3.0, 1.4)):
        assert cells_per_side(L, r) < 3
        x = rng.uniform(0, L, size=(30, 2))
        for periodic in (True, False):
            assert _same(cell_list_pairs(x, L, r, periodic), brute_force_pairs(x, L, r, periodic))


def test_eval_counts():
    rng = np.random.default_rng(4)
    x = rng.uniform(0, 20, size=(200, 2))
    b = brute_force_pairs(x, 20.0, 1.0, True)
    c = cell_list_pairs(x, 20.0, 1.0, True)
    assert b.evals == 200 * 199 // 2
    assert 0 < c.evals < b.evals


def test_cell_side_never_below_radius():
    for L in np.linspace(1.0, 30.0, 200):
        for r in (0.3, 0.5, 1.0, 2.0):
            if r <= L:
                assert L / cells_per_side(L, r) >= r


def test_invalid_inputs():
    with pytest.raises(ValueError):
        brute_force_pairs(np.zeros((3, 3)), 10.0, 1.0, True)
    with pytest.raises(ValueError):
        cell_list_pairs(np.array([[np.nan, 0.0]]), 10.0, 1.0, True)
    with pytest.raises(ValueError):
        cell_list_pairs(np.zeros((2, 2)), 10.0, 0.0, True)
    with pytest.raises(ValueError):
        metric_pairs(np.zeros((2, 2)), 10.0, 1.0, True, "kdtree")


def test_single_agent_and_empty():
    for idx in ("cell", "brute"):
        p = metric_pairs(np.array([[1.0, 1.0]]), 5.0, 1.0, True, idx)
        assert p.i.size == 0


def test_topological_k_nearest():
    x = np.array([[0.0, 0.0], [1.0, 0.0], [3.0, 0.0], [0.0, 2.0]])
    recv, other, disp, evals = topological_edges(x, 100.0, 2, False)
    got = {(int(a), int(b)) for a, b in zip(recv, other)}
    assert {(0, 1), (0, 3), (1, 0), (2, 1), (3, 0)} <= got
    assert len(recv) == 8 and evals == 6
    # tie: agent 1 has 0 at distance 1 and nothing else at 1; second nearest is 3 (sqrt 5) vs 2 (2.0)
    assert (1, 2) in got
    # k larger than N-1 is capped
    recv, _, _, _ = topological_edges(x, 100.0, 10, False)
    assert len(recv) == 4 * 3

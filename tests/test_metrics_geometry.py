# SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0
"""Metrics and geometry: golden values, bounds, edge cases, invalid inputs."""

import math

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from hypothesis.extra.numpy import arrays

from swarm.geometry import displacement, reflect, wrap_angle, wrap_positions
from swarm.metrics import collision_rate, largest_component_fraction, polarization, recovery_time

PI = math.pi


def test_polarization_golden():
    assert polarization(np.zeros(5)) == pytest.approx(1.0)
    assert polarization(np.array([0.0, PI])) == pytest.approx(0.0, abs=1e-15)
    assert polarization(np.array([0.0, PI / 2])) == pytest.approx(math.sqrt(2) / 2)
    assert polarization(np.array([0.0, 2 * PI / 3, -2 * PI / 3])) == pytest.approx(0.0, abs=1e-15)
    with pytest.raises(ValueError):
        polarization(np.array([]))


@settings(max_examples=200, deadline=None)
@given(arrays(np.float64, st.integers(1, 100), elements=st.floats(-50, 50)))
def test_polarization_bounds(theta):
    assert 0.0 <= polarization(theta) <= 1.0


@settings(max_examples=200, deadline=None)
@given(arrays(np.float64, st.integers(1, 50), elements=st.floats(-1e4, 1e4)))
def test_wrap_angle_range_and_equivalence(theta):
    w = wrap_angle(theta)
    assert np.all(w > -PI) and np.all(w <= PI)
    np.testing.assert_allclose(np.cos(w), np.cos(theta), atol=1e-9)
    np.testing.assert_allclose(np.sin(w), np.sin(theta), atol=1e-9)


def test_wrap_angle_edges():
    np.testing.assert_allclose(wrap_angle(np.array([-PI, PI, 3 * PI, 0.0])), [PI, PI, PI, 0.0])


def test_wrap_positions_edge_rounding():
    L = 10.0
    y = wrap_positions(np.array([[-1e-17, 10.0], [10.0 + 1e-15, -0.5]]), L)
    assert np.all(y >= 0) and np.all(y < L)
    assert y[1, 1] == pytest.approx(9.5)


def test_displacement_minimum_image():
    d = displacement(np.array([0.5, 9.5]), np.array([9.5, 0.5]), 10.0, True)
    np.testing.assert_allclose(d, [-1.0, 1.0])
    d = displacement(np.array([0.5, 9.5]), np.array([9.5, 0.5]), 10.0, False)
    np.testing.assert_allclose(d, [9.0, -9.0])


def test_reflect_hand_computed():
    x, th = reflect(np.array([[-0.1, 5.0], [10.2, 10.3], [5.0, 5.0]]),
                    np.array([PI, PI / 4, 0.3]), 10.0)
    np.testing.assert_allclose(x, [[0.1, 5.0], [9.8, 9.7], [5.0, 5.0]])
    assert th[0] == pytest.approx(0.0, abs=1e-15)
    assert th[1] == pytest.approx(-3 * PI / 4)
    assert th[2] == 0.3


def test_components():
    assert largest_component_fraction(5, np.array([0, 1]), np.array([1, 2])) == pytest.approx(0.6)
    assert largest_component_fraction(4, np.array([], int), np.array([], int)) == pytest.approx(0.25)
    assert largest_component_fraction(4, np.array([0, 2, 1]), np.array([1, 3, 2])) == 1.0
    with pytest.raises(ValueError):
        largest_component_fraction(0, np.array([]), np.array([]))


def test_components_against_bfs():
    rng = np.random.default_rng(11)
    for _ in range(50):
        n = int(rng.integers(1, 40))
        m = int(rng.integers(0, 60))
        i = rng.integers(0, n, m)
        j = rng.integers(0, n, m)
        adj = {k: set() for k in range(n)}
        for a, b in zip(i, j):
            adj[a].add(b)
            adj[b].add(a)
        seen, best = set(), 0
        for s in range(n):
            if s in seen:
                continue
            stack, comp = [s], 0
            seen.add(s)
            while stack:
                u = stack.pop()
                comp += 1
                for v in adj[u]:
                    if v not in seen:
                        seen.add(v)
                        stack.append(v)
            best = max(best, comp)
        assert largest_component_fraction(n, i, j) == pytest.approx(best / n)


def test_recovery_time_golden():
    phi = np.array([0.9] * 10 + [0.1, 0.5, 0.85, 0.85, 0.85, 0.2, 0.85, 0.85, 0.85, 0.85])
    # target 0.9*0.9 = 0.81, hold 3: first window of 3 consecutive starts at index 12 -> tau 2
    assert recovery_time(phi, 10, 10, 0.9, 0.9, 3) == (2, False)
    assert recovery_time(phi, 10, 10, 0.9, 0.9, 5) == (None, True)
    assert recovery_time(phi, 10, 10, 0.9, 0.9, 4) == (6, False)
    assert recovery_time(phi, 10, 2, 0.9, 0.9, 3) == (None, True)


def test_collision_rate():
    assert collision_rate(50, 10, 500) == pytest.approx(1.0)
    with pytest.raises(ValueError):
        collision_rate(1, 0, 10)

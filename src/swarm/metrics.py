# SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0
"""Metrics (protocol section 4). All pure functions of recorded state."""

from __future__ import annotations

import math

import numpy as np


def polarization(theta: np.ndarray) -> float:
    """phi = |(1/N) sum_i exp(i theta_i)|, dimensionless in [0, 1]."""
    if theta.size == 0:
        raise ValueError("polarization of an empty group is undefined")
    return float(min(1.0, math.hypot(np.cos(theta).mean(), np.sin(theta).mean())))


def largest_component_fraction(n: int, i: np.ndarray, j: np.ndarray) -> float:
    """Fraction of agents in the largest connected component of the graph (i, j).

    Union-find with path halving; isolated agents are components of size 1.
    """
    if n < 1:
        raise ValueError("n must be >= 1")
    parent = list(range(n))

    def find(a: int) -> int:
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for a, b in zip(i.tolist(), j.tolist()):
        ra, rb = find(a), find(b)
        if ra != rb:
            if ra < rb:
                parent[rb] = ra
            else:
                parent[ra] = rb
    roots = [find(a) for a in range(n)]
    return max(np.bincount(roots)) / n


def recovery_time(phi: np.ndarray, t_disturb: int, window: int, phi_pre: float,
                  threshold: float, hold: int) -> tuple[int | None, bool]:
    """Recovery time tau in steps after t_d, and whether it is right-censored.

    tau is the smallest t - t_d with t >= t_d such that phi(s) >= threshold * phi_pre
    for all s in [t, t + hold), with t + hold <= t_d + W. Returns (None, True) if
    no such t exists inside the window.
    """
    target = threshold * phi_pre
    end = t_disturb + window
    seg = phi[t_disturb:end] >= target
    if seg.size < hold:
        return None, True
    run = 0
    for k, ok in enumerate(seg.tolist()):
        run = run + 1 if ok else 0
        if run >= hold:
            return k - hold + 1, False
    return None, True


def collision_rate(count: int, n: int, window: int) -> float:
    """Collisions per agent per 100 steps over the post window."""
    if n < 1 or window < 1:
        raise ValueError("n and window must be >= 1")
    return 100.0 * count / (n * window)

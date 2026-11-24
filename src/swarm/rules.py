# SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0
"""Heading-update rules (protocol section 2), before noise.

Neighbour information arrives as directed edges: ``recv`` receives from
``other``; ``disp`` is the displacement from recv to other (u) and ``dist``
its length. Every rule returns the desired heading in (-pi, pi]; where the
desired direction is the zero vector (|v| <= ZERO_TOL), the current heading
is kept (EXP-001 protocol section 8).
"""

from __future__ import annotations

import numpy as np

ZERO_TOL = 1e-12


def _unit(vx: np.ndarray, vy: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    norm = np.hypot(vx, vy)
    ok = norm > ZERO_TOL
    safe = np.where(ok, norm, 1.0)
    return np.where(ok, vx / safe, 0.0), np.where(ok, vy / safe, 0.0), ok


def _heading_or_keep(vx: np.ndarray, vy: np.ndarray, theta: np.ndarray) -> np.ndarray:
    ok = np.hypot(vx, vy) > ZERO_TOL
    return np.where(ok, np.arctan2(vy, vx), theta)


def align_only(theta: np.ndarray, recv: np.ndarray, other: np.ndarray) -> np.ndarray:
    """A0: arg of the sum of unit headings over neighbours and self (Vicsek)."""
    n = theta.size
    c, s = np.cos(theta), np.sin(theta)
    sx = c + np.bincount(recv, weights=c[other], minlength=n)
    sy = s + np.bincount(recv, weights=s[other], minlength=n)
    return _heading_or_keep(sx, sy, theta)


def zonal(theta: np.ndarray, recv: np.ndarray, other: np.ndarray, disp: np.ndarray,
          dist: np.ndarray, r_sep: float, w_align: float, w_cohesion: float) -> np.ndarray:
    """A1: separation has priority within r_sep; otherwise w_a*a + w_c*c.

    s_i = sum over neighbours with dist <= r_sep and dist > 0 of -disp/dist.
    a_i = unit sum of headings over neighbours and self.
    c_i = unit mean displacement to neighbours (direction to the local centroid).
    Coincident agents (dist == 0) trigger separation but contribute no direction.
    """
    n = theta.size
    c, s = np.cos(theta), np.sin(theta)

    sep = dist <= r_sep
    has_sep = np.bincount(recv[sep], minlength=n) > 0
    nz = sep & (dist > 0)
    inv = np.zeros_like(dist)
    inv[nz] = 1.0 / dist[nz]
    w = np.where(nz, inv, 0.0)
    sepx = -np.bincount(recv, weights=disp[:, 0] * w, minlength=n)
    sepy = -np.bincount(recv, weights=disp[:, 1] * w, minlength=n)

    ax, ay, _ = _unit(c + np.bincount(recv, weights=c[other], minlength=n),
                      s + np.bincount(recv, weights=s[other], minlength=n))
    cnt = np.bincount(recv, minlength=n)
    mx = np.bincount(recv, weights=disp[:, 0], minlength=n)
    my = np.bincount(recv, weights=disp[:, 1], minlength=n)
    safe = np.where(cnt > 0, cnt, 1)
    cx, cy, _ = _unit(mx / safe, my / safe)

    dx = np.where(has_sep, sepx, w_align * ax + w_cohesion * cx)
    dy = np.where(has_sep, sepy, w_align * ay + w_cohesion * cy)
    return _heading_or_keep(dx, dy, theta)


def centralized(theta: np.ndarray) -> np.ndarray:
    """A2: every agent takes the global mean heading of all N agents."""
    gx, gy = np.cos(theta).sum(), np.sin(theta).sum()
    if np.hypot(gx, gy) <= ZERO_TOL:
        return theta.copy()
    return np.full_like(theta, np.arctan2(gy, gx))

# SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0
"""Boundary geometry: displacements, position wrapping and wall reflection.

Positions are arrays of shape (N, 2) in u; headings are arrays of shape (N,)
in radians, kept in (-pi, pi].
"""

from __future__ import annotations

import numpy as np


def wrap_angle(theta: np.ndarray) -> np.ndarray:
    """Map angles to (-pi, pi]. Values already in range are returned unchanged
    (bit for bit), so wrapping never adds rounding drift."""
    out = np.mod(theta + np.pi, 2.0 * np.pi) - np.pi  # in [-pi, pi)
    out = np.where(out <= -np.pi, out + 2.0 * np.pi, out)
    inside = (theta > -np.pi) & (theta <= np.pi)
    return np.where(inside, theta, out)


def displacement(xi: np.ndarray, xj: np.ndarray, box: float, periodic: bool) -> np.ndarray:
    """Vector from xi to xj; minimum image on the torus when periodic."""
    d = xj - xi
    if periodic:
        d = d - box * np.round(d / box)
    return d


def wrap_positions(x: np.ndarray, box: float) -> np.ndarray:
    """Map positions into [0, box) on the torus, robust to rounding at the edge."""
    y = np.mod(x, box)
    return np.where(y >= box, y - box, y)


def reflect(x: np.ndarray, theta: np.ndarray, box: float) -> tuple[np.ndarray, np.ndarray]:
    """Reflect positions off walls at 0 and box; mirror the heading component.

    Assumes a step is shorter than the box (v0 << L), so one reflection per
    axis suffices. Positions end in [0, box].
    """
    x = x.copy()
    vx, vy = np.cos(theta), np.sin(theta)
    low = x < 0.0
    high = x > box
    x = np.where(low, -x, x)
    x = np.where(high, 2.0 * box - x, x)
    flip_x = low[:, 0] | high[:, 0]
    flip_y = low[:, 1] | high[:, 1]
    vx = np.where(flip_x, -vx, vx)
    vy = np.where(flip_y, -vy, vy)
    x = np.clip(x, 0.0, box)
    new_theta = np.where(flip_x | flip_y, np.arctan2(vy, vx), theta)
    return x, wrap_angle(new_theta)
